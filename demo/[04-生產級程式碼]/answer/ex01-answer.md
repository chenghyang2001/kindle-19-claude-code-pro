# 練習 01 解答 — 從快樂路徑到生產級

## 任務 1：問題清單

| # | 問題類型 | 程式碼位置 | 說明 |
|---|---------|-----------|------|
| 1 | **SQL 注入** | `f"SELECT * FROM users WHERE id={user_id}"` | 直接把 user_id 插入 SQL，攻擊者傳入 `1 OR 1=1` 可取得全部資料 |
| 2 | **硬編碼機密** | `user='root', password='1234'` | 密碼寫死在程式碼，一旦 commit 到 git 就永久洩漏 |
| 3 | **連線資源洩漏** | `conn = pymysql.connect(...)` | 函式結束或中途拋例外時 conn 永遠不關閉，長時間運行耗盡連線池 |
| 4 | **缺少錯誤處理** | 整個函式 | 網路斷線、DB 掛掉都直接拋未捕捉例外，呼叫方無法預期 |
| 5 | **回傳值不確定** | `return result.fetchone()` | 找到回傳 tuple，找不到回傳 None，不同 driver 行為還不一樣 |

## 任務 2：生產級重寫

```python
import os
import logging
import pymysql
import pymysql.cursors

logger = logging.getLogger(__name__)

def fetch_user(user_id: int) -> dict | None:
    """查詢單一使用者。找到回傳 dict，找不到回傳 None，失敗拋 RuntimeError。"""
    conn = pymysql.connect(
        host=os.environ["DB_HOST"],
        db=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", (user_id,)
            )
            return cursor.fetchone()  # 找到 → dict，找不到 → None
    except pymysql.Error as e:
        logger.error("fetch_user 失敗：user_id=%s, error=%s", user_id, e)
        raise RuntimeError(f"資料庫查詢失敗：{e}") from e
    finally:
        conn.close()  # 無論成功失敗都關閉
```

## 修正對照

| 問題 | 原始 | 修正後 |
|------|------|--------|
| SQL 注入 | `f"...{user_id}"` | `%s` 參數化查詢 |
| 硬編碼機密 | `password='1234'` | `os.environ["DB_PASS"]` |
| 連線洩漏 | 無關閉 | `finally: conn.close()` |
| 錯誤處理 | 無 | `except pymysql.Error` + logging |
| 回傳不確定 | fetchone() → tuple/None | DictCursor → dict/None + 型別標注 |

## 核心洞察

SQL 注入是「最危險且最常見」的漏洞，修復成本極低（只需改一行），但被利用的代價是整個資料庫被讀取或刪除。`%s` 參數化查詢是不可妥協的鐵律。
