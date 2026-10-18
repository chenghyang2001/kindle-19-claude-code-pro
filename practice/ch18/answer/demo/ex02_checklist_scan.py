"""練習 02：把個人資安清單中「可自動化」的項目做成掃描器。

用法：
    PYTHONUTF8=1 .venv/Scripts/python answer/demo/ex02_checklist_scan.py <目標資料夾> [...]
只讀取目標檔案，不做任何修改。每個項目輸出 PASS / FAIL / N/A 與命中行號。
"""
import ast
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

# (清單編號, 說明, 正規表示式) —— 命中即 FAIL
REGEX_RULES = [
    ("A1", "SQL 用字串拼接/f-string", re.compile(r"""f["'](SELECT|INSERT|UPDATE|DELETE)\b|(["'])(SELECT|INSERT|UPDATE|DELETE)\b.*?\2\s*\+""", re.I)),
    ("A3", "疑似硬編碼密鑰", re.compile(r"""^\s*\w*(SECRET|PASSWORD|API_KEY|TOKEN)\w*\s*=\s*["'][^"']{4,}["']""", re.I)),
    ("A4", "弱雜湊存密碼（md5/sha1）", re.compile(r"hashlib\.(md5|sha1)\(")),
    ("A5", "shell=True 執行指令", re.compile(r"shell\s*=\s*True")),
    ("A6", "eval/exec/pickle.loads", re.compile(r"\b(eval|exec)\(|pickle\.loads\(")),
    ("A7", "用 assert 做權限檢查", re.compile(r"^\s*assert\s+.*(role|admin|perm)", re.I)),
    ("C2", "DEBUG=True", re.compile(r"\bDEBUG\s*=\s*True")),
    ("D3", "用 random 產生安全值", re.compile(r"random\.(choice|choices|randint|random)\(.*(token|password|key|otp)", re.I)),
]


def scan_regex(files: list[Path]) -> None:
    for rule_id, desc, pattern in REGEX_RULES:
        # 測試檔的 assert 是正常用法，A7 只看正式程式碼
        scoped = [f for f in files if not (rule_id == "A7" and f.name.startswith("test_"))]
        hits = [f"{f.name}:{n}" for f in scoped for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1) if pattern.search(line)]
        status = "FAIL" if hits else "PASS"
        print(f"  [{status}] {rule_id} {desc:24} {', '.join(hits)}")


def scan_imports(files: list[Path]) -> None:
    """D1：AI 幻覺套件——import 了本機找不到的模組（可能不存在或被搶註）。"""
    local_names = {f.stem for f in files}
    missing = []
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            print(f"  [FAIL] 語法錯誤 {f.name}: {exc}")
            continue
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            for name in names:
                top = name.split(".")[0]
                if top not in local_names and importlib.util.find_spec(top) is None:
                    missing.append(f"{f.name}:{node.lineno}:{top}")
    print(f"  [{'FAIL' if missing else 'PASS'}] D1 import 的模組都真實存在   {', '.join(missing)}")


def scan_project_files(target: Path) -> None:
    lock_files = [p.name for p in target.rglob("*") if p.name in {"requirements.txt", "poetry.lock", "Pipfile.lock", "uv.lock", "package-lock.json"}]
    print(f"  [{'PASS' if lock_files else 'FAIL'}] B2 依賴版本鎖定檔           {lock_files or '找不到'}")
    has_env = any(p.name == ".env" for p in target.rglob(".env"))
    gitignore = target / ".gitignore"
    ignored = gitignore.exists() and ".env" in gitignore.read_text(encoding="utf-8")
    status = "N/A" if not has_env else ("PASS" if ignored else "FAIL")
    print(f"  [{status}] C1 .env 已列入 .gitignore")


def run_tool(label: str, cmd: list[str]) -> None:
    """B1：依賴漏洞/相容性（需要網路的 pip-audit 失敗時只標示，不中斷）。"""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        last = (proc.stdout.strip() or proc.stderr.strip()).splitlines()[-1:] or [""]
        print(f"  [{'PASS' if proc.returncode == 0 else 'FAIL'}] {label:30} {last[0][:90]}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"  [N/A ] {label:30} 無法執行：{type(exc).__name__}")


def main() -> None:
    if len(sys.argv) < 2:
        print("用法：ex02_checklist_scan.py <目標資料夾> [...]", file=sys.stderr)
        sys.exit(2)
    for arg in sys.argv[1:]:
        target = Path(arg)
        if not target.is_dir():
            print(f"錯誤：找不到資料夾 {target}", file=sys.stderr)
            sys.exit(1)
        files = sorted(p for p in target.rglob("*.py") if "__pycache__" not in p.parts)
        print(f"== {target.as_posix()}（{len(files)} 個 .py）")
        scan_regex(files)
        scan_imports(files)
        scan_project_files(target)
    print("== 目前 Python 環境的依賴")
    run_tool("B1 pip check（相依衝突）", [sys.executable, "-m", "pip", "check"])
    run_tool("B1 pip-audit（已知 CVE）", [sys.executable, "-m", "pip_audit", "--progress-spinner", "off"])


if __name__ == "__main__":
    main()
