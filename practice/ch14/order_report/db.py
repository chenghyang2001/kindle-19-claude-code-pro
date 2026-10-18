"""子任務 A：資料庫連線、schema 初始化與報表聚合查詢。"""
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
VALID_STATUS = {"paid", "refunded", "pending"}


def connect(db_path: str = ":memory:") -> sqlite3.Connection:
    # check_same_thread=False：測試與 demo 伺服器在背景執行緒共用同一個記憶體 DB
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn


def seed_demo(conn: sqlite3.Connection) -> None:
    """塞入示範資料（3 天、各狀態）。"""
    rows = [
        ("2026-10-01T02:00:00Z", "paid", 120000),
        ("2026-10-01T05:30:00Z", "paid", 35000),
        ("2026-10-01T09:00:00Z", "refunded", 35000),
        ("2026-10-02T03:10:00Z", "paid", 89900),
        ("2026-10-02T11:45:00Z", "pending", 15000),
        ("2026-10-03T07:20:00Z", "paid", 249900),
    ]
    conn.executemany(
        "INSERT INTO orders(created_at, status, amount_cents) VALUES (?, ?, ?)", rows
    )
    conn.commit()


def daily_summary(conn, date_from: str, date_to: str, status: str | None = None) -> list[dict]:
    """依日彙總訂單數與營收（含頭含尾），一律參數化查詢。"""
    if status is not None and status not in VALID_STATUS:
        raise ValueError(f"不支援的 status：{status}")
    sql = (
        "SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS orders, "
        "SUM(amount_cents) AS revenue_cents FROM orders "
        "WHERE created_at >= ? AND created_at < date(?, '+1 day')"
    )
    params: list = [date_from, date_to]
    if status is not None:
        sql += " AND status = ?"
        params.append(status)
    sql += " GROUP BY day ORDER BY day"
    return [
        {"day": r["day"], "orders": r["orders"], "revenue": r["revenue_cents"] / 100}
        for r in conn.execute(sql, params)
    ]


if __name__ == "__main__":
    demo_conn = connect()
    seed_demo(demo_conn)
    print(daily_summary(demo_conn, "2026-10-01", "2026-10-03", "paid"))
