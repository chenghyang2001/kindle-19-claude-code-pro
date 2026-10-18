"""簡易品質閘門：掃描 .py 檔的高風險模式，命中就 exit 1。

可掛在 pre-commit hook 或 CI，讓 checklist 前幾項「不得不做」。
這是 regex 粗篩，不取代 bandit / ruff 等正式工具。
"""
import re
import sys
from pathlib import Path

RULES = [
    ("C1 SQL 字串組合", re.compile(r"""execute\(\s*f["']|execute\([^)]*["']\s*(\+|%)""")),
    ("C2 硬編碼機密", re.compile(r"""(?i)(api_key|password|secret|token)\s*=\s*["'][^"']{6,}["']""")),
    ("C3 硬編碼使用者路徑", re.compile(r"""(?i)[a-z]:[\/]+users[\/]+\w+""")),
    ("C4 裸 except", re.compile(r"^\s*except\s*:", re.M)),
    ("C5 except 後直接 pass", re.compile(r"except[^\n]*:\s*\n\s*pass\b")),
    ("C6 HTTP 呼叫沒有 timeout", re.compile(r"requests\.(get|post|put|delete)\((?![^)]*timeout)[^)]*\)", re.S)),
]


def scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{path}: 無法讀取（{exc}）"]
    findings = []
    for name, pattern in RULES:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(f"{path}:{line_no}: {name}")
    return findings


def main(argv: list[str]) -> int:
    targets = [Path(arg) for arg in argv] or [Path(".")]
    files = [f for t in targets for f in ([t] if t.is_file() else sorted(t.rglob("*.py")))]
    findings = [item for f in files for item in scan_file(f)]
    for item in findings:
        print(item)
    print(f"掃描 {len(files)} 個檔案，問題 {len(findings)} 個")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
