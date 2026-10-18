"""收件人名單讀取與驗證。"""
import csv
import re
from pathlib import Path

# 刻意用寬鬆規則：只擋明顯錯誤，真正的有效性交給 SMTP 伺服器判斷
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def load_recipients(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """讀 CSV（需含 email 欄）。回傳 (有效名單, 錯誤訊息清單)；重複 email 只留第一筆。"""
    valid: list[dict[str, str]] = []
    errors: list[str] = []
    seen: set[str] = set()
    with Path(path).open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or "email" not in reader.fieldnames:
            raise ValueError(f"CSV 缺少 email 欄位：{path}")
        for line_no, row in enumerate(reader, start=2):
            email = (row.get("email") or "").strip().lower()
            if not EMAIL_PATTERN.match(email):
                errors.append(f"第 {line_no} 行 email 格式錯誤：{email!r}")
                continue
            if email in seen:
                errors.append(f"第 {line_no} 行重複 email：{email}")
                continue
            seen.add(email)
            valid.append({**row, "email": email})
    return valid, errors
