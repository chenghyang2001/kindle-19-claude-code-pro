"""生產級 fetch_user：參數化查詢、環境變數設定、finally 關連線、logging。"""
import logging
import os
import sqlite3
from typing import Any

logger = logging.getLogger(__name__)

DB_PATH_ENV = "APP_DB_PATH"


class ConfigError(RuntimeError):
    """必要的環境變數缺失。"""


def get_db_path() -> str:
    """從環境變數讀 DB 位置；缺少就明確失敗，不用預設值掩蓋。"""
    db_path = os.environ.get(DB_PATH_ENV)
    if not db_path:
        raise ConfigError(f"缺少環境變數 {DB_PATH_ENV}")
    return db_path


def fetch_user(user_id: int) -> dict[str, Any] | None:
    """依 id 查使用者。找到回傳 dict，找不到回傳 None。

    Raises:
        ValueError: user_id 不是正整數（bool 也拒絕，因為 True == 1）。
        ConfigError: 未設定 APP_DB_PATH。
        sqlite3.Error: 資料庫錯誤（已記錄 log 後重新拋出，不吞掉）。
    """
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
        # 只記 id 與例外，不把連線資訊或整段 SQL 參數外洩到 log
        logger.exception("查詢使用者失敗 id=%s", user_id)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import tempfile

    logging.basicConfig(level=logging.INFO)
    with tempfile.TemporaryDirectory() as tmp:
        demo_db = os.path.join(tmp, "demo.db")
        setup = sqlite3.connect(demo_db)
        setup.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        setup.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
        setup.commit()
        setup.close()
        os.environ[DB_PATH_ENV] = demo_db
        print("id=1 →", fetch_user(1))
        print("id=99 →", fetch_user(99))
