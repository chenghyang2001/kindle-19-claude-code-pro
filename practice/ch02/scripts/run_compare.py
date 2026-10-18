"""批次用 claude -p 實跑提示詞，存下輸出與量化指標，供改寫前後／有無角色比較。

用法：
    PYTHONUTF8=1 python scripts/run_compare.py            # 跑 prompts/ 底下全部
    PYTHONUTF8=1 python scripts/run_compare.py ex02       # 只跑 prompts/ex02
    PYTHONUTF8=1 python scripts/run_compare.py --dry-run  # 只展開提示詞，不呼叫 claude
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "prompts"
OUT_DIR = ROOT / "outputs"
TIMEOUT_SEC = 120  # 使用者要求每次 claude -p 上限 120 秒
MAX_WORKERS = 4  # 同時開太多 claude 進程會吃記憶體
FILE_PLACEHOLDER = re.compile(r"\{\{file:([^}]+)\}\}")


def expand_prompt(text: str) -> str:
    """把 {{file:相對路徑}} 換成檔案內容，讓兩個版本拿到完全相同的程式碼。"""
    def _replace(match: re.Match) -> str:
        path = ROOT / match.group(1).strip()
        if not path.is_file():
            raise FileNotFoundError(f"提示詞引用的檔案不存在：{path}")
        return path.read_text(encoding="utf-8").rstrip()
    return FILE_PLACEHOLDER.sub(_replace, text)


def clean_env() -> dict:
    """移除 CLAUDE 開頭的環境變數，避免巢狀 Claude Code 限制。"""
    return {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}


def measure(output: str) -> dict:
    """簡單量化指標：長度、程式碼區塊數、表格列數、是否反問使用者。"""
    asks_back = bool(re.search(r"[?？]\s*$", output.strip())) or any(
        kw in output for kw in ("請提供", "請問", "能否提供", "可以告訴我")
    )
    return {
        "chars": len(output),
        "lines": output.count("\n") + 1,
        "code_blocks": output.count("```") // 2,
        "table_rows": sum(1 for ln in output.splitlines() if ln.strip().startswith("|")),
        "asserts": output.count("assert "),
        "asks_back": asks_back,
    }


def run_one(prompt_file: Path, workdir: str) -> dict:
    """跑單一提示詞；不給工具（--tools ""），只比純文字回答品質。"""
    name = f"{prompt_file.parent.name}/{prompt_file.stem}"
    prompt = expand_prompt(prompt_file.read_text(encoding="utf-8"))
    started = time.time()
    claude_bin = shutil.which("claude")
    try:
        if claude_bin is None:
            raise FileNotFoundError("PATH 中沒有 claude")
        # 提示詞走 stdin：多行文字經 Windows cmd 參數傳遞會被截斷或跳脫錯亂
        proc = subprocess.run(
            [claude_bin, "-p", "--tools", ""], input=prompt,
            cwd=workdir, env=clean_env(), capture_output=True,
            encoding="utf-8", errors="replace", timeout=TIMEOUT_SEC,
        )
        output, status = proc.stdout, ("ok" if proc.returncode == 0 else f"exit {proc.returncode}")
        if proc.returncode != 0:
            output += f"\n[stderr]\n{proc.stderr}"
    except subprocess.TimeoutExpired:
        output, status = "", f"timeout >{TIMEOUT_SEC}s"
    except FileNotFoundError as err:
        output, status = "", f"找不到 claude 指令：{err}"
    elapsed = round(time.time() - started, 1)
    out_path = OUT_DIR / f"{prompt_file.parent.name}-{prompt_file.stem}.md"
    out_path.write_text(f"<!-- prompt: {name} | {status} | {elapsed}s -->\n\n{output}", encoding="utf-8")
    print(f"[{status}] {name} {elapsed}s -> {out_path.name}", flush=True)
    return {"name": name, "status": status, "seconds": elapsed, **measure(output)}


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    groups = args or sorted(p.name for p in PROMPT_DIR.iterdir() if p.is_dir())
    files = [f for g in groups for f in sorted((PROMPT_DIR / g).glob("*.txt"))]
    if not files:
        print(f"錯誤：{groups} 底下找不到 .txt 提示詞", file=sys.stderr)
        sys.exit(1)
    if dry_run:
        for f in files:
            print(f"=== {f.name} ===\n{expand_prompt(f.read_text(encoding='utf-8'))}\n")
        return
    OUT_DIR.mkdir(exist_ok=True)
    # 在空的暫存目錄執行，避免子 claude 讀到本專案 CLAUDE.md 而干擾比較
    with tempfile.TemporaryDirectory() as workdir, ThreadPoolExecutor(MAX_WORKERS) as pool:
        results = list(pool.map(lambda f: run_one(f, workdir), files))
    metrics_path = OUT_DIR / f"metrics-{'-'.join(groups)}.json"
    metrics_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"指標已存：{metrics_path}")
    if any(r["status"] != "ok" for r in results):
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as err:
        print(f"錯誤：{err}", file=sys.stderr)
        sys.exit(1)
