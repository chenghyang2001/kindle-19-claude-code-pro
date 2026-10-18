# 練習 02 解答 — 系統化 Debug 流程

> 實作檔案：`ex02/request_logger.py`（decorator）、`ex02/app.py`（示範 API）、`ex02/test_request_logger.py`（測試）
> 實際輸出：`ex02/server-run.log`（真實啟動 Flask 伺服器、用 curl 打出來的 log）

## 任務 1：「API 回傳 500」Debug Checklist

排序原則：前面的步驟「最可能是原因」且「最快能驗證」；越往後越少見、越花時間。

| # | 步驟 | 怎麼做 | 有發現 → 下一步 |
| --- | --- | --- | --- |
| 1 | **重現**這個 500，確定觸發條件 | 用 `curl -v` 帶同樣的方法、路徑、參數、body、header 重送；比對成功與失敗的請求差在哪（哪個 id、哪個參數） | 能穩定重現 → 縮小到「哪個輸入會壞」，跳到第 3 步看 traceback；無法重現 → 偏向環境／時序問題，跳到第 6～8 步 |
| 2 | **找出**錯誤被誰吞掉了 | 搜尋 `@app.errorhandler(500)`、`errorhandler(Exception)`、`try/except Exception: return ...`；確認 `app.logger` 的 level 與 handler；確認 gunicorn／uwsgi 的 `--error-logfile`、`--capture-output` | 找到只回 `Internal Server Error` 卻沒 `logger.exception()` 的 handler → 先補上 log（或套第 2 部分的 decorator），重送請求 |
| 3 | **取得**完整 traceback | 本機：`FLASK_DEBUG=1 flask run` 重送；正式環境：套 `@log_request`、或暫時在 handler 加 `app.logger.exception(e)`；查 `journalctl -u <服務>`、容器 `docker logs` | 拿到 traceback → 從最下面的錯誤類型往上找第一個「自己的檔案」那一層，就是出事點 |
| 4 | **比對**最近的改動 | `git log --since="2 days ago" --oneline`、看最近一次部署時間是否與 500 開始的時間吻合；必要時 `git bisect` | 時間吻合 → 回滾或檢查該 commit 的 diff；不吻合 → 往資料面找 |
| 5 | **檢查**觸發請求用到的資料 | 用觸發的 id 直接查 DB／資料來源：欄位缺漏、`NULL`、格式不符、編碼異常（例如本練習的舊使用者沒有 `email`） | 資料有異常 → 程式加防禦（`.get()`、驗證、回 4xx 而非 500）並修資料 |
| 6 | **驗證**外部相依服務 | 檢查 DB、Redis、第三方 API 是否活著與延遲：`pg_isready`、`redis-cli ping`、`curl` 第三方健康檢查端點；看連線池是否用盡 | 相依服務逾時／拒絕連線 → 加 timeout、重試、斷路器；回 503 而非 500 |
| 7 | **比對**環境設定 | 比較本機與正式環境的環境變數、設定檔、套件版本（`pip freeze` diff）、Python 版本 | 缺環境變數或版本不同 → 補設定／鎖版本，啟動時加必要環境變數檢查 |
| 8 | **檢查**系統資源 | `df -h`（磁碟滿 → 寫檔／寫 log 失敗）、`free -m`、`ulimit -n`（檔案描述子用盡）、CPU／記憶體監控 | 資源耗盡 → 清空間、調整上限、找洩漏 |
| 9 | **排查**併發／時序問題 | 用 `ab` / `hey` / `locust` 壓測；檢查共享的全域變數、非執行緒安全的物件、競態條件 | 只有在併發下才壞 → 加鎖或改成每請求獨立的物件 |
| 10 | **確認**修復並防止再犯 | 為觸發條件寫回歸測試；部署後觀察錯誤率；把這次的根因記錄到事件報告 | 測試通過且錯誤率回到基準 → 結案 |

## 任務 2：加強 Logging 的 decorator

完整檔案：`ex02/request_logger.py`

```python
import functools
import logging
import random
import time

from flask import make_response, request
from werkzeug.exceptions import HTTPException

SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "authorization"}


def _mask(params):
    """遮蔽敏感欄位，避免密碼、token 落進 log。"""
    return {k: ("***" if k.lower() in SENSITIVE_KEYS else v) for k, v in params.items()}


def _request_params(view_kwargs):
    """收集 path 參數、query string、JSON body（解析失敗就略過，不影響主流程）。"""
    params = {"path": dict(view_kwargs), "query": _mask(request.args.to_dict())}
    body = request.get_json(silent=True)
    if isinstance(body, dict):
        params["json"] = _mask(body)
    return params


def make_log_request(sample_rate=1.0, slow_ms=None, logger=None, rand=random.random):
    """產生 decorator。4xx、5xx、例外一律記錄，不受抽樣影響。"""
    if not 0.0 <= sample_rate <= 1.0:
        raise ValueError(f"sample_rate 必須介於 0 和 1，收到 {sample_rate}")
    log = logger or logging.getLogger("request")

    def decorator(view):
        @functools.wraps(view)  # 保留原函式名稱，否則多個 route 會撞 endpoint 名
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            line = f"{request.method} {request.path} params={_request_params(kwargs)}"
            try:
                response = make_response(view(*args, **kwargs))
            except HTTPException as exc:
                # abort(404) 這類是預期中的錯誤，不需要 traceback
                ms = (time.perf_counter() - start) * 1000
                log.warning("%s status=%s %.1fms", line, exc.code, ms)
                raise
            except Exception:
                ms = (time.perf_counter() - start) * 1000
                log.exception("%s status=500 %.1fms 未處理的例外", line, ms)
                raise  # 交回 Flask，維持原本的 500 行為

            ms = (time.perf_counter() - start) * 1000
            status = response.status_code
            is_slow = slow_ms is not None and ms >= slow_ms
            if status >= 400:
                log.warning("%s status=%s %.1fms", line, status, ms)
            elif is_slow or rand() < sample_rate:
                level = logging.WARNING if is_slow else logging.INFO
                log.log(level, "%s status=%s %.1fms%s", line, status, ms, " SLOW" if is_slow else "")
            return response

        return wrapper

    return decorator


log_request = make_log_request()
```

用法和題目一樣（`@app.route` 要在 `@log_request` 上面，Flask 才會註冊到包好的函式）：

```python
@app.route("/api/users/<int:user_id>")
@log_request
def get_user_email(user_id):
    ...
```

設計重點：

- **`make_response()` 統一轉成 Response**：view 可能回 dict、tuple、字串，轉過之後才能可靠地讀 `status_code`。
- **例外記完 traceback 後 `raise`**：不改變 API 原本的行為（仍是 500、仍走原本的 error handler），decorator 只負責「看見」。
- **`HTTPException`（`abort(404)` 等）分開處理**：記 WARNING、不印 traceback，避免把預期內的錯誤當成 bug 洗版。
- **敏感欄位遮蔽**：`password`、`token` 等改成 `***`。
- **`functools.wraps`**：沒有它，所有被包的 view 名稱都叫 `wrapper`，Flask 註冊第二個 route 時會報 endpoint 重複。

## 驗證結果（實際執行）

### 真實伺服器 + curl（`ex02/server-run.log` 節錄）

**沒套 decorator**（`/legacy/users/2`，被全域 error handler 吞掉）——log 只有這一行，看不出原因：

```
INFO werkzeug: 127.0.0.1 - - [18/Oct/2026 07:45:55] "GET /legacy/users/2 HTTP/1.1" 500 -
```

**套了 decorator**（`/api/users/2`，同一段邏輯）：

```
ERROR request: GET /api/users/2 params={'path': {'user_id': 2}, 'query': {}} status=500 0.0ms 未處理的例外
Traceback (most recent call last):
  File "~\...\ex02\request_logger.py", line 49, in wrapper
    response = make_response(view(*args, **kwargs))
  File "~\...\ex02\app.py", line 39, in get_user_email
    return jsonify(id=user_id, email=USERS[user_id]["email"].lower())
KeyError: 'email'
WARNING request: GET /api/users/999 params={'path': {'user_id': 999}, 'query': {}} status=404 0.1ms
INFO request: POST /api/login params={'path': {}, 'query': {}, 'json': {'user': 'bob', 'password': '***'}} status=200 0.1ms
```

traceback 直接指出：使用者 2 的資料沒有 `email` 欄位——對應 checklist 第 5 步「資料異常」。

### pytest（`ex02/test_request_logger.py`）

```
11 passed
```

涵蓋：成功請求記錄方法／路徑／參數／狀態碼／毫秒、例外記錄完整 traceback 且仍回 500、404 記 WARNING 無 traceback、密碼遮蔽、沒套 decorator 的 route 確實什麼都沒記、`functools.wraps` 保留 endpoint 名稱、抽樣丟棄／保留、抽樣時錯誤不會被丟、慢請求一律記錄、非法 `sample_rate` 拋錯。

## 延伸思考：每分鐘 10,000 次請求

每分鐘 1 萬次 ≈ 每秒 167 次，每筆 log 約 200～300 bytes，光成功請求一天就約 **1,400 萬行、3～4 GB**。會出現的問題：

1. **儲存與費用**：log 平台（CloudWatch、Datadog、ELK）多半按量計費，成本直線上升。
2. **效能**：`logging` 預設是同步寫入，寫檔／送網路會卡住處理請求的執行緒，拉高延遲；檔案 handler 還有鎖競爭。
3. **訊雜比**：99.9% 都是正常的 200，真正的錯誤被淹沒，反而更難 debug。
4. **磁碟寫滿**：沒有輪替的話會把磁碟寫滿，回頭造成更多 500（checklist 第 8 步）。
5. **個資風險**：記錄越多參數，外洩面越大。

採樣設計（已實作在 `make_log_request`）：

| 請求類型 | 處理方式 | 理由 |
| --- | --- | --- |
| 例外 / 5xx | **100% 記錄**，含 traceback | 這正是要 debug 的東西，一筆都不能漏 |
| 4xx | 100% 記錄（不含 traceback） | 量通常不大，能抓到攻擊或用戶端 bug |
| 慢請求（超過 `slow_ms`） | 100% 記錄 | 效能問題的線索 |
| 正常 2xx/3xx | 依 `sample_rate` 機率抽樣，例如 1% | 保留流量樣貌即可 |

```python
log_request = make_log_request(sample_rate=0.01, slow_ms=500)
```

進一步可以做的（本練習未實作）：

- **以 request id 決定是否採樣**（例如 `hash(request_id) % 100 == 0`），讓同一個請求跨多個服務時，要嘛全記、要嘛全不記，追蹤才不會斷。
- **非同步寫 log**：`logging.handlers.QueueHandler` + `QueueListener`，把 I/O 移出請求執行緒。
- **結構化 log（JSON）**，方便在 log 平台上聚合查詢。
- **計數用 metrics、細節才用 log**：請求數、延遲分佈、錯誤率交給 Prometheus 之類的 metrics 系統（不採樣、成本低），log 只負責個案細節。
- **動態調整**：錯誤率升高時自動把 `sample_rate` 拉高，事件結束後再降回來。
