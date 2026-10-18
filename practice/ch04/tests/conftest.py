import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def user_db(tmp_path, monkeypatch):
    """每個測試一份獨立 DB，避免共享狀態。"""
    db_file = tmp_path / "app.db"
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.executemany(
        "INSERT INTO users VALUES (?, ?, ?)",
        [(1, "Alice", "alice@example.com"), (2, "Bob", "bob@example.com")],
    )
    conn.commit()
    conn.close()
    monkeypatch.setenv("APP_DB_PATH", str(db_file))
    return db_file
