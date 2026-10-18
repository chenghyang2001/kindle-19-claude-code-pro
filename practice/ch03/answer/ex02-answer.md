# 練習 02 解答 — 設定 Hooks

檔案位置（全部在本專案，未碰全域 `~/.claude/`）：

| 檔案 | 用途 |
| --- | --- |
| `.claude/settings.json` | 註冊 PostToolUse + SessionStart hook |
| `.claude/hooks/format_py.py` | Write `.py` 後跑 `ruff format` |
| `.claude/hooks/session_start.py` | 印 branch / 最近 3 commit / 未提交變更 |
| `.claude/hooks/*.log` | hook 執行紀錄（已 gitignore） |

## 完整 settings.json

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "PYTHONUTF8=1 python \"$CLAUDE_PROJECT_DIR/.claude/hooks/format_py.py\"",
            "timeout": 60
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "PYTHONUTF8=1 python \"$CLAUDE_PROJECT_DIR/.claude/hooks/session_start.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

設計重點：

- `matcher: "Write"` 只攔 Write 工具；是不是 `.py` 交給腳本判斷 `tool_input.file_path`（matcher 只能比對工具名稱，不能比對副檔名）。
- 格式化工具選 **ruff format**（本機已裝 ruff 0.15，沒有 black；ruff 也快很多）。
- 用 `$CLAUDE_PROJECT_DIR` 組路徑，不寫死使用者路徑；不管 Claude 的 cwd 在哪都找得到腳本。
- SessionStart matcher 用 `startup|resume|clear|compact`，四種開始方式都會補上 git 狀態。

## 任務 1：PostToolUse hook（`.claude/hooks/format_py.py`）

```python
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
```

### 測試步驟與結果

**A. 直接餵 hook JSON（單元層）**

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"C:/.../ugly.py"}}' | python .claude/hooks/format_py.py; echo $?
cat .claude/hooks/format-py.log
```

| # | 案例 | 預期 | 實測 |
| --- | --- | --- | --- |
| 1 | Write 亂排版 `.py` | 被格式化、exit 0 | ✅ `x = [1, 2, 3]` / `def f(a):`，log `OK formatted` |
| 2 | Write `.md` | 不動、不記錄 | ✅ 內容不變 |
| 3 | stdin 不是 JSON | exit 0、log 錯誤 | ✅ `ERROR stdin 不是合法 hook JSON` |
| 4 | `.py` 有語法錯誤 | exit 0、log ruff 錯誤 | ✅ `ERROR ruff exit=2 ... Failed to parse` |
| 5 | ruff 未安裝（用沒裝 ruff 的空 venv python 執行） | exit 0、log 錯誤 | ✅ `ERROR ruff exit=1 ... No module named ruff` |

**B. 真實 Claude Code session（整合層）**

```bash
UNSET=$(env | grep -o '^CLAUDE[A-Z_]*' | sed 's/^/-u /' | tr '\n' ' ')
env $UNSET DISABLE_WRITER_QA_HOOK=1 timeout 120 claude -p --permission-mode acceptEdits \
  '請用 Write 工具逐字建立 sandbox/hook_demo.py 與 sandbox/hook_demo.txt ...'
```

結果（原始輸出：`answer/logs/ex02-claude-p.txt`）：

- `sandbox/hook_demo.py` 寫入的是 `x  =  [1,2,\n 3]\ndef f( a ):  return a`，落地後變成：
  ```python
  x = [1, 2, 3]


  def f(a):
      return a
  ```
- `sandbox/hook_demo.txt` 保持原本的亂排版 → 只對 `.py` 觸發 ✅
- `format-py.log`：`OK formatted ...\sandbox\hook_demo.py: 1 file reformatted` ✅

## 任務 2：SessionStart hook（`.claude/hooks/session_start.py`）

```python
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
```

### 測試結果

| # | 案例 | 實測輸出 |
| --- | --- | --- |
| 6 | 本 repo（尚無 commit） | `目前 branch：master` / `（尚無 commit）` / 列出未追蹤檔 ✅ |
| 7 | 非 git 目錄 | `這裡不是 git repo（或 git 無法執行）`，exit 0 ✅ |
| 8 | 臨時 repo：4 個 commit + 1 個修改 | `feat/demo`、只列最新 3 個 commit、` M f1` ✅ |
| 9 | 真實 `claude -p` session | `session-start.log` 有紀錄；Claude 回答「branch 是 `master`，有未提交變更…還沒有任何 commit」→ stdout 確實進入 context ✅ |

案例 8 輸出：

```text
[SessionStart] 目前 branch：feat/demo
最近 3 個 commit：
- bd20900 commit 4
- faa6386 commit 3
- d776d3e commit 2
有未提交變更：
 M f1
?? bad.py
...
```

## 延伸思考：hook 如何「靜默失敗」

1. **永遠 exit 0**：PostToolUse 的 exit 2 會把 stderr 回饋給 Claude、其他非 0 會顯示錯誤；守門型以外的輔助 hook 都應固定 exit 0。
2. **錯誤寫 log，不寫 stdout/stderr**：失敗原因落到 `.claude/hooks/format-py.log`，事後可查，又不污染對話。
3. **把每一個外部依賴都包 try/except**：JSON 解析、`subprocess`（`OSError` = 工具不存在、`TimeoutExpired`）、甚至寫 log 本身（`OSError`）。
4. **設 timeout**：subprocess 30 秒、settings.json 的 hook `timeout` 60 秒，避免格式化工具卡住整個 session。
5. **先過濾再動作**：不是 Write、不是 `.py` 立刻 return，降低出錯面。
6. **用 `sys.executable -m ruff`** 而非依賴 PATH 上的 `ruff`，少一個環境差異；沒裝時就是案例 5 的 log。
7. 進一步：可加環境變數開關（例如 `SKIP_FORMAT_HOOK=1`）讓 hook 壞掉時一鍵關閉；或在 SessionStart 檢查 ruff 是否存在，缺少時提示一次就好。
