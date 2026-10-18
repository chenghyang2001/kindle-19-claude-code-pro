"""SessionStart hook：印出 git branch、最近 3 個 commit、未提交變更。

stdout 會被 Claude Code 當成 session 的額外 context。
任何 git 錯誤都只顯示提示文字，一律 exit 0。
"""

import datetime
import subprocess
import sys
from pathlib import Path

LOG_FILE = Path(__file__).with_name("session-start.log")


def git(*args: str) -> tuple[int, str]:
    """執行 git 指令，回傳 (exit code, 輸出)；git 不存在時回傳 (-1, 錯誤訊息)。"""
    try:
        proc = subprocess.run(
            ["git", *args], capture_output=True, encoding="utf-8", timeout=10
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, repr(exc)
    return proc.returncode, (proc.stdout or proc.stderr).rstrip()


def build_report() -> str:
    code, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if code != 0:
        # 尚無 commit 時 rev-parse 會失敗，改用 symbolic-ref
        code, branch = git("symbolic-ref", "--short", "HEAD")
    if code != 0:
        return "[SessionStart] 這裡不是 git repo（或 git 無法執行）"

    code, commits = git("log", "-3", "--format=- %h %s")
    if code != 0 or not commits:
        commits = "- （尚無 commit）"

    _, status = git("status", "--short")
    dirty = f"有未提交變更：\n{status}" if status else "沒有未提交變更"

    return (
        f"[SessionStart] 目前 branch：{branch}\n最近 3 個 commit：\n{commits}\n{dirty}"
    )


def main() -> None:
    report = build_report()
    print(report)
    try:
        stamp = datetime.datetime.now().isoformat(timespec="seconds")
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(f"{stamp}\n{report}\n\n")
    except OSError:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
