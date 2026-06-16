# 練習 02 解答 — 系統化 Debug 流程

## 任務 1：API 500 系統化 Debug Checklist

| # | 步驟 | 如何執行 | 有發現時 |
|---|------|---------|---------|
| 1 | **重現問題** — 找出觸發條件 | 用相同參數手動打 API（curl/Postman），確認可穩定重現 | 記錄最小觸發請求，後續驗證都用這組 |
| 2 | **看完整 server log** — 不只看 error level | `grep -A 10 "500" app.log` 或 `journalctl -u flask -n 100` | 找到 traceback → 跳到步驟 5 定位根因 |
| 3 | **加強 logging** — 讓 Flask 暴露完整 traceback | 設 `app.config["PROPAGATE_EXCEPTIONS"] = True`；開發環境加 `DEBUG = True` | 看到真正的 exception 訊息 |
| 4 | **縮小觸發範圍** — 用二分搜尋法 | 逐一移除請求參數，找到哪個參數導致 500 | 找到最小觸發條件 → 進步驟 5 |
| 5 | **讀 traceback 找根因** — 從最底層往上看 | 找 `File` 最深那行，那才是真正爆點 | 去對應位置加 print/breakpoint |
| 6 | **本地 breakpoint 除錯** — 直接看變數值 | 在懷疑的位置加 `import pdb; pdb.set_trace()` | 觀察進入點的實際變數值 |
| 7 | **查資料庫/外部服務** — 確認依賴項正常 | 直接打 DB query 或呼叫外部 API，看是否回傳非預期值 | 是依賴項問題 → 加 timeout + fallback |
| 8 | **查環境差異** — 比對 dev 和 prod 的差異 | 比較 `pip freeze`、環境變數、config 設定 | 找到差異 → 統一設定 |

---

## 任務 2：Flask Logging Decorator

```python
import logging
import time
import traceback
from functools import wraps
from flask import request

logger = logging.getLogger(__name__)

def log_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            response = f(*args, **kwargs)
            elapsed = (time.time() - start) * 1000
            logger.info(
                "%s %s | params=%s | status=%s | %.1fms",
                request.method, request.path,
                dict(request.args), response.status_code, elapsed
            )
            return response
        except Exception:
            elapsed = (time.time() - start) * 1000
            logger.error(
                "%s %s | params=%s | EXCEPTION | %.1fms\n%s",
                request.method, request.path,
                dict(request.args), elapsed, traceback.format_exc()
            )
            raise
    return wrapper
```

---

## 延伸思考：高流量採樣機制

10,000 req/min 全記錄問題：磁碟 I/O 成為瓶頸、log 量難以分析。

設計原則：
- **正常請求**：1% 採樣（`random.random() < 0.01`）
- **500 錯誤**：100% 記錄（錯誤不能漏）
- **慢請求（> 500ms）**：100% 記錄（效能異常不能漏）
- **特定使用者/IP**：可臨時開啟 100% 記錄（用於 debug 特定問題）
