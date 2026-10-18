"""PostToolUse hook：Write 寫入 .py 後自動 ruff format。

設計：任何失敗（ruff 沒裝、語法錯、JSON 壞掉）都只寫 log，一律 exit 0，
讓 hook 「靜默失敗」，不中斷 Claude 的主要工作流。
"""

import datetime
import json
import subprocess
import sys
from pathlib import Path

LOG_FILE = Path(__file__).with_name("format-py.log")


def log(message: str) -> None:
    """寫 log 本身也不能讓 hook 爆掉，所以吞掉 OSError。"""
    try:
        stamp = datetime.datetime.now().isoformat(timespec="seconds")
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(f"{stamp} {message}\n")
    except OSError:
        pass


def get_target_path(raw_input: str) -> str | None:
    """從 hook stdin JSON 取出 file_path；非 Write 或非 .py 回傳 None。"""
    payload = json.loads(raw_input)
    if payload.get("tool_name") != "Write":
        return None
    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not isinstance(file_path, str) or not file_path.lower().endswith(".py"):
        return None
    return file_path


def run_formatter(file_path: str) -> None:
    """跑 ruff format；失敗只記錄。"""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "ruff", "format", file_path],
            capture_output=True,
            encoding="utf-8",
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log(f"ERROR 無法執行 ruff：{exc!r} file={file_path}")
        return
    if proc.returncode == 0:
        log(f"OK formatted {file_path}: {proc.stdout.strip()}")
    else:
        log(
            f"ERROR ruff exit={proc.returncode} file={file_path}: {proc.stderr.strip()}"
        )


def main() -> None:
    try:
        file_path = get_target_path(sys.stdin.read())
    except (json.JSONDecodeError, AttributeError) as exc:
        log(f"ERROR stdin 不是合法 hook JSON：{exc!r}")
        return
    if file_path is None:
        return  # 不是 .py：不動作也不記錄
    run_formatter(file_path)


if __name__ == "__main__":
    main()
    sys.exit(0)
