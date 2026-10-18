"""子任務 E：訂單報表整合測試（db / api / csv / HTTP）。"""
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from order_report import api, db
from order_report.export_csv import rows_to_csv


class TestDb(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()
        db.seed_demo(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_daily_summary_paid(self):
        rows = db.daily_summary(self.conn, "2026-10-01", "2026-10-03", "paid")
        self.assertEqual([r["day"] for r in rows], ["2026-10-01", "2026-10-02", "2026-10-03"])
        self.assertEqual(rows[0], {"day": "2026-10-01", "orders": 2, "revenue": 1550.0})

    def test_empty_range(self):
        self.assertEqual(db.daily_summary(self.conn, "2025-01-01", "2025-01-31"), [])

    def test_to_is_inclusive(self):
        rows = db.daily_summary(self.conn, "2026-10-03", "2026-10-03")
        self.assertEqual(rows[0]["orders"], 1)

    def test_bad_status_rejected(self):
        with self.assertRaises(ValueError):
            db.daily_summary(self.conn, "2026-10-01", "2026-10-03", "x' OR 1=1 --")


class TestParams(unittest.TestCase):
    def assert_api_error(self, query, code):
        with self.assertRaises(api.ApiError) as ctx:
            api.parse_params(query)
        self.assertEqual((ctx.exception.status, ctx.exception.code), (400, code))

    def test_errors(self):
        self.assert_api_error("to=2026-10-01", "MISSING_PARAM")
        self.assert_api_error("from=2026/10/01&to=2026-10-02", "INVALID_DATE")
        self.assert_api_error("from=2026-10-05&to=2026-10-01", "INVALID_RANGE")
        self.assert_api_error("from=2024-01-01&to=2026-01-01", "RANGE_TOO_LARGE")
        self.assert_api_error("from=2026-10-01&to=2026-10-02&status=done", "INVALID_STATUS")


class TestCsv(unittest.TestCase):
    def test_header_and_bom(self):
        text = rows_to_csv([{"day": "2026-10-01", "orders": 2, "revenue": 1550.0}])
        self.assertTrue(text.startswith("\ufeff日期,訂單數,營收"))
        self.assertIn("2026-10-01,2,1550.00", text)

    def test_empty_rows(self):
        self.assertEqual(rows_to_csv([]), "\ufeff日期,訂單數,營收\r\n")


class TestHttp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = db.connect()
        db.seed_demo(cls.conn)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), api.make_handler(cls.conn))
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.conn.close()

    def get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=5) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            with e:  # 關閉 HTTPError 內含的回應，避免 ResourceWarning
                return e.code, e.read().decode("utf-8")

    def test_ok(self):
        status, body = self.get("/api/reports/orders?from=2026-10-01&to=2026-10-03")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["data"]["total"], {"orders": 6, "revenue": 5448.0})

    def test_400(self):
        status, body = self.get("/api/reports/orders?from=bad&to=2026-10-03")
        self.assertEqual(status, 400)
        self.assertEqual(json.loads(body)["error"]["code"], "INVALID_DATE")

    def test_404(self):
        self.assertEqual(self.get("/nope")[0], 404)

    def test_csv_endpoint(self):
        status, body = self.get("/api/reports/orders.csv?from=2026-10-01&to=2026-10-01&status=paid")
        self.assertEqual(status, 200)
        self.assertIn("2026-10-01,2,1550.00", body)

    def test_html(self):
        status, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("訂單報表", body)


if __name__ == "__main__":
    unittest.main()
