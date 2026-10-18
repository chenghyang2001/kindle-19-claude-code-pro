"""子任務 D：報表列轉 CSV（UTF-8 BOM，讓 Excel 正確顯示中文）。"""
import csv
import io

HEADER = ["日期", "訂單數", "營收"]


def rows_to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    buf.write("\ufeff")
    writer = csv.writer(buf, lineterminator="\r\n")
    writer.writerow(HEADER)
    for r in rows:
        writer.writerow([r["day"], r["orders"], f'{r["revenue"]:.2f}'])
    return buf.getvalue()


if __name__ == "__main__":
    print(rows_to_csv([{"day": "2026-10-01", "orders": 2, "revenue": 1550.0}]))
