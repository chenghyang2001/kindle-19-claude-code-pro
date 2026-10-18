"""log_request decorator 測試。"""
import logging

import pytest
from flask import Flask

from app import app
from request_logger import make_log_request


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_success_logs_method_path_params_status_time(client, caplog):
    with caplog.at_level(logging.INFO, logger="request"):
        resp = client.get("/api/users?limit=1")
    assert resp.status_code == 200
    rec = caplog.records[-1]
    assert rec.levelno == logging.INFO
    msg = rec.getMessage()
    assert "GET /api/users" in msg and "'limit': '1'" in msg
    assert "status=200" in msg and "ms" in msg


def test_exception_logs_full_traceback_and_still_500(client, caplog):
    with caplog.at_level(logging.INFO, logger="request"):
        resp = client.get("/api/users/2")
    assert resp.status_code == 500
    rec = caplog.records[-1]
    assert rec.levelno == logging.ERROR
    assert "status=500" in rec.getMessage() and "'user_id': 2" in rec.getMessage()
    assert rec.exc_info is not None
    assert "KeyError: 'email'" in caplog.text
    assert "Traceback (most recent call last)" in caplog.text


def test_abort_404_logged_as_warning_without_traceback(client, caplog):
    with caplog.at_level(logging.INFO, logger="request"):
        resp = client.get("/api/users/999")
    assert resp.status_code == 404
    rec = caplog.records[-1]
    assert rec.levelno == logging.WARNING and "status=404" in rec.getMessage()
    assert rec.exc_info is None


def test_sensitive_fields_masked(client, caplog):
    with caplog.at_level(logging.INFO, logger="request"):
        client.post("/api/login", json={"user": "bob", "password": "hunter2"})
    assert "hunter2" not in caplog.text
    assert "'password': '***'" in caplog.text


def test_legacy_route_without_decorator_logs_nothing(client, caplog):
    with caplog.at_level(logging.DEBUG):
        resp = client.get("/legacy/users/2")
    assert resp.status_code == 500
    assert resp.get_json() == {"error": "Internal Server Error"}
    assert "KeyError" not in caplog.text


def test_wraps_keeps_endpoint_names():
    assert app.view_functions["get_user_email"].__name__ == "get_user_email"


def _mini_client(**kwargs):
    """建立只有 /ok 與 /boom 兩個 route 的小 app，用來測抽樣邏輯。"""
    mini = Flask("mini")
    deco = make_log_request(**kwargs)

    @mini.route("/ok")
    @deco
    def ok():
        return "ok"

    @mini.route("/boom")
    @deco
    def boom():
        raise RuntimeError("boom")

    return mini.test_client()


def test_sampling_skips_success_when_rand_above_rate(caplog):
    c = _mini_client(sample_rate=0.01, rand=lambda: 0.5)
    with caplog.at_level(logging.INFO, logger="request"):
        c.get("/ok")
    assert not [r for r in caplog.records if r.name == "request"]


def test_sampling_keeps_success_when_rand_below_rate(caplog):
    c = _mini_client(sample_rate=0.01, rand=lambda: 0.001)
    with caplog.at_level(logging.INFO, logger="request"):
        c.get("/ok")
    assert "status=200" in caplog.text


def test_sampling_never_drops_errors(caplog):
    c = _mini_client(sample_rate=0.0, rand=lambda: 0.99)
    with caplog.at_level(logging.INFO, logger="request"):
        c.get("/boom")
    assert "RuntimeError: boom" in caplog.text


def test_slow_request_always_logged(caplog):
    c = _mini_client(sample_rate=0.0, slow_ms=0, rand=lambda: 0.99)
    with caplog.at_level(logging.INFO, logger="request"):
        c.get("/ok")
    assert "SLOW" in caplog.text


def test_invalid_sample_rate():
    with pytest.raises(ValueError):
        make_log_request(sample_rate=1.5)
