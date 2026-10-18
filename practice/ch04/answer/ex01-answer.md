# 練習 01 解答 — 從快樂路徑到生產級

> 依本章補充，`pymysql` 改用標準庫 `sqlite3`，可在本機直接執行與測試；換回 pymysql 時佔位符 `?` 改成 `%s` 即可。

## 任務 1：原始程式碼的缺陷清單

```python
def fetch_user(user_id):
    conn = pymysql.connect(host='localhost', db='app',
                           user='root', password='1234')
    result = conn.execute(f"SELECT * FROM users WHERE id={user_id}")
    return result.fetchone()
```

| # | 類型 | 問題 | 後果 |
| --- | ------ | ------ | ------ |
| 1 | SQL 注入 | 用 f-string 把 `user_id` 直接拼進 SQL | 傳入 `1 OR 1=1` 可撈任意資料；`1; DROP TABLE users` 可能毀表（測試 `test_legacy_version_is_injectable` 實際打穿重現） |
| 2 | 硬編碼機密 | 帳號 `root`、密碼 `1234` 寫在程式裡 | 進版控即外洩；換環境要改程式碼 |
| 3 | 權限過大 | 用 `root` 連線 | 一旦被注入，攻擊者擁有整個 DB 權限 |
| 4 | 硬編碼設定 | host / db 寫死 | 無法切換開發／測試／正式環境 |
| 5 | 連線資源洩漏 | 從未 `conn.close()`，例外時更不會關 | 高流量下連線耗盡 |
| 6 | 缺少錯誤處理 | 連線失敗、查詢錯誤都沒處理也沒 log | 出事時無線索可查 |
| 7 | 缺少輸入驗證 | `user_id` 任何型別都接受 | 垃圾輸入直接打到 DB |
| 8 | 回傳值不確定 | 回傳 tuple 或 None，呼叫端不知道欄位順序；`SELECT *` 欄位隨 schema 變動 | 加欄位就可能取錯資料、外洩密碼雜湊等敏感欄位 |
| 9 | API 誤用 | pymysql 的 `Connection` 沒有 `execute()`，要先開 cursor | 原始程式根本跑不起來 |
| 10 | 無型別標註／docstring | 呼叫端只能猜 | 可維護性差 |

## 任務 2：生產級版本

完整檔案：`src/user_repo.py`

```python
import logging
import os
import sqlite3
from typing import Any

logger = logging.getLogger(__name__)
DB_PATH_ENV = "APP_DB_PATH"


class ConfigError(RuntimeError):
    """必要的環境變數缺失。"""


def get_db_path() -> str:
    db_path = os.environ.get(DB_PATH_ENV)
    if not db_path:
        raise ConfigError(f"缺少環境變數 {DB_PATH_ENV}")
    return db_path


def fetch_user(user_id: int) -> dict[str, Any] | None:
    if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id <= 0:
        raise ValueError(f"user_id 必須是正整數，收到 {user_id!r}")

    conn = sqlite3.connect(get_db_path())
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row is None:
            logger.info("找不到使用者 id=%s", user_id)
            return None
        return dict(row)
    except sqlite3.Error:
        logger.exception("查詢使用者失敗 id=%s", user_id)
        raise
    finally:
        conn.close()
```

### 五項要求對照

| 要求 | 做法 |
| ------ | ------ |
| 1. 參數化查詢 | `WHERE id = ?` + `(user_id,)`，另加型別驗證當第二道防線 |
| 2. 環境變數 | 讀 `APP_DB_PATH`；缺少時拋 `ConfigError`，不用預設值掩蓋 |
| 3. try/finally | `finally: conn.close()`，成功、找不到、例外三條路徑都會關 |
| 4. 明確回傳型別 | `dict[str, Any] \| None`；明列欄位取代 `SELECT *` |
| 5. 錯誤 logging | `logger.exception` 記下 id 與 stack trace 後重新拋出（不吞錯），log 不含連線資訊 |

pymysql 版只需改：`pymysql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"], password=os.environ["DB_PASS"], database=os.environ["DB_NAME"], cursorclass=pymysql.cursors.DictCursor)`，再用 `with conn.cursor() as cur: cur.execute("... WHERE id = %s", (user_id,))`。（需要 MySQL 伺服器，本練習未實測。）

## 驗證結果（實際執行）

`PYTHONUTF8=1 python -m pytest -q tests/test_user_repo.py` → **21 passed**

| 測試 | 驗證什麼 |
| ------ | --------- |
| `test_found_returns_dict` / `test_not_found_returns_none` | 找到回 dict、找不到回 None |
| `test_invalid_id_rejected` ×6 | 0、-1、None、"1"、1.0、True 都拋 ValueError |
| `test_missing_env_var` | 未設 `APP_DB_PATH` 拋 ConfigError |
| `test_injection_string_rejected_and_table_intact` ×4 | 4 種攻擊字串被拒絕，users 表仍是 2 筆 |
| `test_parameterized_query_treats_payload_as_literal` ×4 | 跳過型別檢查，直接證明參數化讓攻擊字串只被當成值（查無資料、表沒被刪） |
| `test_legacy_version_is_injectable` | 對照組：原始 f-string 版被 `999 OR 1=1` 打穿，證明測試有鑑別力 |
| `test_connection_always_closed` ×2 | 成功與 DB 例外兩種路徑，連線都有關 |
| `test_db_error_is_logged_and_reraised` | DB 錯誤有寫 log 且重新拋出 |

冒煙執行 `python -m src.user_repo`：

```
id=1 → {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
INFO:__main__:找不到使用者 id=99
id=99 → None
```
