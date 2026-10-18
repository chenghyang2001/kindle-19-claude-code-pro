import logging
import sqlite3

import pytest

from src import user_repo
from src.user_repo import ConfigError, fetch_user

INJECTION_PAYLOADS = [
    "1 OR 1=1",
    "1; DROP TABLE users; --",
    "' OR '1'='1",
    "1 UNION SELECT 1, sqlite_version(), 3",
]


# --- 正常案例 ---
def test_found_returns_dict(user_db):
    assert fetch_user(1) == {"id": 1, "name": "Alice", "email": "alice@example.com"}


def test_not_found_returns_none(user_db):
    assert fetch_user(999) is None


# --- 邊界 / 錯誤案例 ---
@pytest.mark.parametrize("bad", [0, -1, None, "1", 1.0, True])
def test_invalid_id_rejected(user_db, bad):
    with pytest.raises(ValueError):
        fetch_user(bad)


def test_missing_env_var(monkeypatch):
    monkeypatch.delenv("APP_DB_PATH", raising=False)
    with pytest.raises(ConfigError):
        fetch_user(1)


# --- SQL 注入 ---
@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_injection_string_rejected_and_table_intact(user_db, payload):
    with pytest.raises(ValueError):
        fetch_user(payload)
    conn = sqlite3.connect(user_db)
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 2
    conn.close()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_parameterized_query_treats_payload_as_literal(user_db, payload):
    """繞過型別檢查，直接驗證「參數化」本身：攻擊字串只被當成值比對，查不到任何列。"""
    conn = sqlite3.connect(user_db)
    rows = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (payload,)).fetchall()
    assert rows == []
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 2
    conn.close()


def test_legacy_version_is_injectable(user_db, monkeypatch):
    """對照組：原始 f-string 版本會被 '1 OR 1=1' 打穿（證明測試有鑑別力）。"""
    monkeypatch.chdir(user_db.parent)
    from src.legacy_fetch_user import fetch_user as legacy

    assert legacy("2 OR 1=1") is not None  # 傳不存在的條件也撈到資料
    assert legacy("999 OR 1=1") is not None


# --- 資源釋放與 logging ---
class SpyConn:
    def __init__(self, real, fail=False):
        self._real, self._fail, self.closed = real, fail, False
        self.row_factory = None

    def execute(self, *args):
        if self._fail:
            raise sqlite3.OperationalError("disk I/O error")
        self._real.row_factory = self.row_factory
        return self._real.execute(*args)

    def close(self):
        self.closed = True
        self._real.close()


@pytest.mark.parametrize("fail", [False, True])
def test_connection_always_closed(user_db, monkeypatch, fail):
    spy = SpyConn(sqlite3.connect(user_db), fail=fail)
    monkeypatch.setattr(user_repo.sqlite3, "connect", lambda *_a, **_k: spy)
    if fail:
        with pytest.raises(sqlite3.OperationalError):
            fetch_user(1)
    else:
        assert fetch_user(1)["name"] == "Alice"
    assert spy.closed


def test_db_error_is_logged_and_reraised(user_db, monkeypatch, caplog):
    spy = SpyConn(sqlite3.connect(user_db), fail=True)
    monkeypatch.setattr(user_repo.sqlite3, "connect", lambda *_a, **_k: spy)
    with caplog.at_level(logging.ERROR, logger="src.user_repo"):
        with pytest.raises(sqlite3.OperationalError):
            fetch_user(1)
    assert "查詢使用者失敗 id=1" in caplog.text
