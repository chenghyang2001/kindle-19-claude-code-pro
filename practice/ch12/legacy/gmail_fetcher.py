"""模擬 Gmail 抓信：從 CSV 讀信件（真實版應改用 Gmail MCP / Gmail API，見 ex01 答案範本）。"""
import csv
from pathlib import Path

DEFAULT_CSV = Path(__file__).parent / "data" / "emails.csv"
REQUIRED_COLUMNS = {"id", "sender", "subject", "body", "received_at", "has_attachment", "labels"}


class FetchError(RuntimeError):
    """抓信失敗（檔案不存在、欄位缺漏）。"""


def fetch_emails(csv_path=DEFAULT_CSV):
    """回傳 list[dict]，每封信含 id/sender/subject/body/received_at/has_attachment/labels。"""
    try:
        with open(csv_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise FetchError(f"CSV 缺少欄位：{sorted(missing)}")
            emails = []
            for row in reader:
                row["has_attachment"] = (row["has_attachment"] or "").strip().lower() == "true"
                emails.append(row)
            return emails
    except FileNotFoundError as e:
        raise FetchError(f"找不到信件來源：{csv_path}") from e
