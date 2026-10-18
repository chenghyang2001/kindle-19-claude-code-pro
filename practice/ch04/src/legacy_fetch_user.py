"""原始「快樂路徑」版本（改寫成 sqlite3 以便本機重現缺陷）。

僅供測試示範 SQL 注入，請勿在正式程式使用。
"""
import sqlite3


def fetch_user(user_id):
    conn = sqlite3.connect("app.db")  # 硬編碼連線目標，且連線從未關閉
    result = conn.execute(f"SELECT * FROM users WHERE id={user_id}")  # SQL 注入
    return result.fetchone()  # 回傳 tuple 或 None，呼叫端不知道欄位順序
