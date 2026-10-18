"""API 測試：正常 / 邊界 / 錯誤三類案例。"""

import pytest

from app import create_app
from app import routes


@pytest.fixture()
def client():
    routes._todos.clear()  # 每個測試獨立狀態
    return create_app({"TESTING": True}).test_client()


def test_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}


def test_create_todo(client):
    resp = client.post("/api/todos", json={"title": "  買牛奶 "})
    assert resp.status_code == 201
    assert resp.get_json()["data"] == {"id": 1, "title": "買牛奶"}


def test_empty_title_rejected(client):
    assert client.post("/api/todos", json={"title": "   "}).status_code == 400


def test_invalid_body_rejected(client):
    assert client.post("/api/todos", data="not json").status_code == 400
