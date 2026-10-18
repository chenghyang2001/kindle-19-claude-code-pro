"""fixed/app.py 的 pytest：驗證功能正常 + 注入防護有效。"""
import os
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import app  # noqa: E402

os.environ.setdefault("APP_SECRET_KEY", "test-only-fake-key")  # 測試用假密鑰


@pytest.fixture()
def conn():
    c = sqlite3.connect(":memory:")
    app.init_db(c)
    yield c
    c.close()


# ---- 功能正常（happy path）----

def test_login_success(conn):
    assert app.login(conn, "alice", "alice-pw") is not None


def test_login_wrong_password(conn):
    assert app.login(conn, "alice", "wrong") is None


def test_get_user_returns_row(conn):
    assert app.get_user(conn, 1) == [(1, "alice", "admin")]


def test_password_hash_has_salt():
    # 同一密碼兩次雜湊結果不同（salt 生效）
    assert app.hash_password("x") != app.hash_password("x")


def test_calc_literal(conn):
    assert app.calc("[1, 2, 3]") == [1, 2, 3]


def test_delete_user_as_admin(conn):
    app.delete_user(conn, "admin", 2)
    assert app.get_user(conn, 2) == []


# ---- 注入防護（attack blocked）----

def test_sql_injection_in_login_blocked(conn):
    # vulnerable 版此 payload 可繞過密碼；修復版應登入失敗
    assert app.login(conn, "alice' --", "wrong") is None


def test_sql_injection_in_get_user_blocked(conn):
    # "0 OR 1=1" 無法轉成 int，應拋錯而非回傳全表
    with pytest.raises(ValueError):
        app.get_user(conn, "0 OR 1=1")


def test_command_injection_blocked():
    with pytest.raises(ValueError):
        app.ping_host("127.0.0.1 & echo INJECTED")


def test_eval_rce_blocked():
    # literal_eval 無法呼叫函式 / import
    with pytest.raises((ValueError, SyntaxError)):
        app.calc("__import__('os').getcwd()")


def test_load_session_is_json_only():
    blob = app.dump_session({"uid": 1})
    assert app.load_session(blob) == {"uid": 1}


def test_delete_user_non_admin_denied(conn):
    with pytest.raises(PermissionError):
        app.delete_user(conn, "user", 1)
    # 使用者仍在，刪除確實被擋
    assert app.get_user(conn, 1) == [(1, "alice", "admin")]


def test_issue_token_requires_env(monkeypatch, conn):
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        app.login(conn, "alice", "alice-pw")
