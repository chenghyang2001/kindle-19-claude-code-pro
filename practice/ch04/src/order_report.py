"""修正版訂單報表：依 checklist 修掉 starter/order_report.py 的問題。

為了離線可測，報表送出改由呼叫端注入 sender；預設 sender 走 HTTPS 並帶 timeout。
"""
import json
import logging
import os
import sqlite3
import urllib.request
from typing import Any, Callable

logger = logging.getLogger(__name__)

REPORT_URL = "https://report.example.com/api"
HTTP_TIMEOUT_SECONDS = 10


def _require_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"缺少環境變數 {key}")
    return value


def summarize_orders(db_path: str, customer: str) -> dict[str, Any]:
    """彙總某客戶訂單；沒有訂單時 avg 為 0（避免除以零）。"""
    if not isinstance(customer, str) or not customer.strip():
        raise ValueError("customer 必須是非空字串")
    conn = sqlite3.connect(db_path)
    try:
        amounts = [
            row[0]
            for row in conn.execute(
                "SELECT amount FROM orders WHERE customer = ?", (customer,)
            )
        ]
    finally:
        conn.close()
    order_count = len(amounts)
    total_amount = sum(amounts)
    return {
        "customer": customer,
        "count": order_count,
        "total": total_amount,
        "avg": total_amount / order_count if order_count else 0,
    }


def post_report(report: dict[str, Any]) -> None:
    """預設 sender：API key 從環境變數讀，失敗就拋出（不靜默吞掉）。"""
    api_key = _require_env("REPORT_API_KEY")
    request = urllib.request.Request(
        REPORT_URL,
        data=json.dumps(report).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        if response.status != 200:
            raise RuntimeError(f"報表 API 回傳 {response.status}")


def send_order_report(
    customer: str, sender: Callable[[dict[str, Any]], None] = post_report
) -> dict[str, Any]:
    report = summarize_orders(_require_env("SHOP_DB_PATH"), customer)
    try:
        sender(report)
    except Exception:
        logger.exception("報表送出失敗 customer=%s", customer)
        raise
    logger.info("報表已送出 customer=%s count=%s", customer, report["count"])
    return report
