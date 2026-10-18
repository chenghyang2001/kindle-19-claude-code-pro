"""子任務 B：GET /api/reports/orders 與 /api/reports/orders.csv（標準庫 http.server）。"""
import json
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from order_report import db
from order_report.export_csv import rows_to_csv

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
MAX_RANGE_DAYS = 366


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def parse_params(query: str) -> tuple[str, str, str | None]:
    """驗證查詢參數；不合法時丟 ApiError(400)。"""
    qs = parse_qs(query)

    def first(key):
        return (qs.get(key) or [None])[0]

    raw_from, raw_to, status = first("from"), first("to"), first("status")
    if raw_from is None or raw_to is None:
        raise ApiError(400, "MISSING_PARAM", "from 與 to 為必填")
    try:
        d_from, d_to = date.fromisoformat(raw_from), date.fromisoformat(raw_to)
    except ValueError:
        raise ApiError(400, "INVALID_DATE", "日期格式需為 YYYY-MM-DD")
    if d_from > d_to:
        raise ApiError(400, "INVALID_RANGE", "from 不可晚於 to")
    if (d_to - d_from).days > MAX_RANGE_DAYS:
        raise ApiError(400, "RANGE_TOO_LARGE", f"區間最多 {MAX_RANGE_DAYS} 天")
    if status is not None and status not in db.VALID_STATUS:
        raise ApiError(400, "INVALID_STATUS", "status 只能是 paid/refunded/pending")
    return d_from.isoformat(), d_to.isoformat(), status


def build_report(conn, query: str) -> dict:
    d_from, d_to, status = parse_params(query)
    rows = db.daily_summary(conn, d_from, d_to, status)
    total = {
        "orders": sum(r["orders"] for r in rows),
        "revenue": round(sum(r["revenue"] for r in rows), 2),
    }
    return {"from": d_from, "to": d_to, "status": status, "rows": rows, "total": total}


def make_handler(conn):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: bytes, ctype: str, extra=None):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, payload: dict):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send(status, body, "application/json; charset=utf-8")

        def _route(self, url):
            if url.path == "/api/reports/orders":
                self._json(200, {"data": build_report(conn, url.query)})
            elif url.path == "/api/reports/orders.csv":
                report = build_report(conn, url.query)
                self._send(200, rows_to_csv(report["rows"]).encode("utf-8"),
                           "text/csv; charset=utf-8",
                           {"Content-Disposition": 'attachment; filename="order-report.csv"'})
            elif url.path in ("/", "/report.html"):
                self._send(200, (WEB_DIR / "report.html").read_bytes(), "text/html; charset=utf-8")
            else:
                raise ApiError(404, "NOT_FOUND", "找不到此路徑")

        def do_GET(self):
            try:
                self._route(urlparse(self.path))
            except ApiError as e:
                self._json(e.status, {"error": {"code": e.code, "message": e.message}})
            except Exception as e:  # 不洩漏內部細節給前端，只記在伺服器端
                print(f"內部錯誤：{e!r}", file=sys.stderr)
                self._json(500, {"error": {"code": "INTERNAL", "message": "伺服器內部錯誤"}})

        def log_message(self, format, *args):  # 關閉預設逐請求 log，保持測試輸出乾淨
            pass

    return Handler


def main(port: int = 8765):
    conn = db.connect(":memory:")
    db.seed_demo(conn)
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(conn))
    print(f"訂單報表服務：http://127.0.0.1:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8765)
