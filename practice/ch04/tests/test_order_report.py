import sqlite3

import pytest

from src.order_report import send_order_report, summarize_orders


@pytest.fixture
def shop_db(tmp_path, monkeypatch):
    db_file = tmp_path / "shop.db"
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, customer TEXT, amount REAL)")
    conn.executemany(
        "INSERT INTO orders (customer, amount) VALUES (?, ?)",
        [("amy", 100), ("amy", 300), ("ben", 50)],
    )
    conn.commit()
    conn.close()
    monkeypatch.setenv("SHOP_DB_PATH", str(db_file))
    return db_file


def test_happy_path(shop_db):
    sent = []
    report = send_order_report("amy", sender=sent.append)
    assert report == {"customer": "amy", "count": 2, "total": 400, "avg": 200}
    assert sent == [report]


def test_no_orders_does_not_divide_by_zero(shop_db):
    assert summarize_orders(str(shop_db), "nobody")["avg"] == 0


@pytest.mark.parametrize("payload", ["' OR '1'='1", "amy' --", "x'; DROP TABLE orders; --"])
def test_sql_injection_payload_is_literal(shop_db, payload):
    assert summarize_orders(str(shop_db), payload)["count"] == 0
    conn = sqlite3.connect(shop_db)
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 3
    conn.close()


def test_sender_failure_is_raised_not_swallowed(shop_db):
    def broken_sender(_report):
        raise ConnectionError("network down")

    with pytest.raises(ConnectionError):
        send_order_report("amy", sender=broken_sender)


def test_missing_db_env(monkeypatch):
    monkeypatch.delenv("SHOP_DB_PATH", raising=False)
    with pytest.raises(RuntimeError, match="SHOP_DB_PATH"):
        send_order_report("amy", sender=lambda _r: None)
