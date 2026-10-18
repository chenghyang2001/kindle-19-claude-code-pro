# NOTES — K19 第 3 章練習（CLAUDE.md + Hooks）

> 快速 demo 模式完成，未經 QA／code-review 流程。全程未 push、未建 GitHub repo、未碰全域 `~/.claude/`。

## 做了什麼

| 項目 | 產出 |
| --- | --- |
| 練習 01 任務 1 | 根目錄 `CLAUDE.md`（六區塊）＋可實際執行的最小 Flask 專案 `app/`、`tests/`、`run.py`、`requirements.txt` |
| 練習 01 任務 2 | 用 3 個全新 `claude -p` session 各問一題，輸出存 `answer/logs/ex01-q1~3.txt` |
| 練習 02 任務 1 | `.claude/settings.json` PostToolUse(Write) → `.claude/hooks/format_py.py`（ruff format，失敗只記 log） |
| 練習 02 任務 2 | `.claude/settings.json` SessionStart → `.claude/hooks/session_start.py`（branch / 3 commit / 未提交變更） |
| 解答 | `answer/ex01-answer.md`、`answer/ex02-answer.md` |
| 其他 | `.gitignore`（含 hook log、當機檔）、`sandbox/hook_demo.*`（hook 整合測試留下的證據） |

## 驗證結果

- `pytest`：4 passed（正常／邊界／錯誤案例）。
- `ruff check` / `ruff format --check`：全部通過。
- CLAUDE.md 有效性：3 題全部正確引用 CLAUDE.md；發現「資料庫描述有歧義」已修正（細節見 ex01 解答）。
- PostToolUse hook：單元 5 案例 + 真實 `claude -p` session 皆通過；`.py` 被格式化、`.txt` 不動、ruff 失敗/未安裝/壞 JSON 都 exit 0 並寫 log。
- SessionStart hook：無 commit repo、非 git 目錄、多 commit repo、真實 session 4 案例皆通過；Claude 能說出 hook 提供的 branch 與變更狀態。

## 與題目要求的差異

1. **格式化工具**：題目可選 black 或 ruff format；本機沒有 black，選 ruff format。
2. **「只在 .py 觸發」的實作位置**：hook matcher 只能比對工具名稱，所以 matcher 設 `Write`，副檔名過濾放在腳本裡。
3. **測試有效性的方式**：題目說「在新的 Claude Code session 中問」，這裡用 `claude -p`（non-interactive）開三個新 session 代替互動式 session，結果效果相同。
4. **額外加的東西**：題目只要求 CLAUDE.md，為了讓「執行方式／常用指令」真的能跑，多建了最小 Flask 專案；部署平台 Render、PostgreSQL 只寫在文件裡（需外部帳號，未實際設定）。
5. **設定檔位置衝突**：原有 CLAUDE.md「本專案例外」寫設定放 `.claude/settings.local.json`，但本次指示要求 hook 寫在 `.claude/settings.json`，以本次指示為準（`settings.local.json` 也列入 .gitignore）。
6. **整合測試的環境變數**：`claude -p` 子 session 加了 `DISABLE_WRITER_QA_HOOK=1`，只作用在那一次子程序，避免全域「三 agent 鐵律」hook 擋下 Write `.py`，否則測不到 PostToolUse 格式化。未修改任何全域設定。
7. **MCP**：本章題目沒有 MCP 任務，所以沒有建立 `.mcp.json`。
8. 未執行 `/doctor`、`/statusline`、`/login`、`/logout`。

## 已知限制

- Flask 範例資料存在記憶體，`id` 用 `len()+1` 產生，只適合 demo。
- hook 只攔 `Write`；`Edit` 修改 `.py` 不會格式化（題目只要求 Write）。要涵蓋可把 matcher 改成 `Write|Edit|MultiEdit`。
- hook 依賴 PATH 上的 `python` 指令；換機器若沒有 python，hook 會失敗（Claude Code 只會顯示非阻斷錯誤）。
