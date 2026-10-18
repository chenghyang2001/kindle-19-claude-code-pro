"""每日信件簡報 Pipeline：抓信 → 過濾+評分 → 摘要 → Notion → Telegram（全部本地模擬）。"""
import argparse
import sys
from pathlib import Path

from gmail_fetcher import FetchError, fetch_emails
from email_filter import filter_and_score, filter_emails
from summarizer import summarize_all
from notion_creator import create_pages
from telegram_briefer import send_briefing

OUT_DIR = Path(__file__).parent / "output"


def run(csv_path=None, out_dir=OUT_DIR, use_score=True, min_score=1):
    emails = fetch_emails(csv_path) if csv_path is not None else fetch_emails()
    filtered = filter_and_score(emails, min_score) if use_score else filter_emails(emails)
    summaries = summarize_all(filtered)
    try:
        create_pages(summaries, out_dir)
    except OSError as e:  # Notion 失敗不該擋住 Telegram 簡報
        print(f"警告：Notion 建頁失敗：{e}", file=sys.stderr)
    message, alerts = send_briefing(summaries, out_dir)
    return {"fetched": len(emails), "kept": len(filtered), "message": message, "alerts": alerts}


def main():
    parser = argparse.ArgumentParser(description="每日信件簡報（本地模擬）")
    parser.add_argument("--csv", default=None, help="信件 CSV 路徑")
    parser.add_argument("--no-score", action="store_true", help="關閉評分（等同擴充前行為）")
    parser.add_argument("--min-score", type=int, default=1)
    args = parser.parse_args()
    try:
        result = run(args.csv, OUT_DIR, not args.no_score, args.min_score)
    except FetchError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])
    for alert in result["alerts"]:
        print("\n" + alert)
    print(f"\n[統計] 抓到 {result['fetched']} 封，保留 {result['kept']} 封，"
          f"緊急 {len(result['alerts'])} 封", file=sys.stderr)


if __name__ == "__main__":
    main()
