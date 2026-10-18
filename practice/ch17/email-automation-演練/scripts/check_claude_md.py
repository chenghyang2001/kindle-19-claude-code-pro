"""CLAUDE.md 過時檢查：@匯入是否存在、文件中提到的路徑是否存在、最後更新日是否太久。

用法：python scripts/check_claude_md.py [專案根目錄]
回傳碼：0 = 全部通過，1 = 有過時項目
"""
import re
import sys
from datetime import date, datetime
from pathlib import Path

MAX_AGE_DAYS = 90  # 對應「每季審查」
IMPORT_RE = re.compile(r"@([\w./-]+\.md)")
# 反引號中看起來像專案內路徑的字串（含 / 或常見副檔名）
PATH_RE = re.compile(r"`([\w./-]+(?:/|\.py|\.txt|\.csv|\.md|\.example))`")
DATE_RE = re.compile(r"最後更新：(\d{4}-\d{2}-\d{2})")


def collect_docs(root: Path) -> tuple[list[Path], list[str]]:
    """回傳 CLAUDE.md 與其 @匯入的檔案清單，以及找不到的匯入。"""
    main = root / "CLAUDE.md"
    if not main.exists():
        return [], [f"找不到 {main}"]
    docs, problems = [main], []
    for name in IMPORT_RE.findall(main.read_text(encoding="utf-8")):
        target = root / name
        if target.exists():
            docs.append(target)
        else:
            problems.append(f"@匯入不存在：{name}")
    return docs, problems


def path_exists(root: Path, ref: str) -> bool:
    """相對路徑直接比對；裸檔名（如 `cli.py`）在專案內任一處存在即可；專案目錄名本身視為存在。"""
    if ref.rstrip("/") == root.name or (root / ref).exists():
        return True
    return "/" not in ref and any(root.rglob(ref))


def check_paths(root: Path, docs: list[Path]) -> list[str]:
    problems = []
    for doc in docs:
        for ref in PATH_RE.findall(doc.read_text(encoding="utf-8")):
            if not path_exists(root, ref):
                problems.append(f"{doc.relative_to(root)} 提到不存在的路徑：{ref}")
    return problems


def check_age(root: Path, today: date) -> list[str]:
    match = DATE_RE.search((root / "CLAUDE.md").read_text(encoding="utf-8"))
    if match is None:
        return ["CLAUDE.md 缺少「最後更新：YYYY-MM-DD」"]
    age = (today - datetime.strptime(match.group(1), "%Y-%m-%d").date()).days
    return [f"CLAUDE.md 已 {age} 天未更新（上限 {MAX_AGE_DAYS}）"] if age > MAX_AGE_DAYS else []


def run(root: Path, today: date | None = None) -> list[str]:
    docs, problems = collect_docs(root)
    if not docs:
        return problems
    return problems + check_paths(root, docs) + check_age(root, today or date.today())


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    problems = run(root)
    for p in problems:
        print(f"[STALE] {p}")
    print("CLAUDE.md 檢查通過" if not problems else f"共 {len(problems)} 個過時項目")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
