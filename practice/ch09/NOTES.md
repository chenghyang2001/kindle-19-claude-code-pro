# NOTES — 第 9 章 MCP 練習（快速 demo 模式）

> 2026-10-18｜快速模式：主 Claude 直接寫檔，未經 QA／審查

## 做了什麼

| 檔案 | 內容 |
| --- | --- |
| `answer/ex01-answer.md` | MCP 能力地圖（依 `claude mcp list` 實際 17 個 server）＋ MCP vs REST API 比較 |
| `answer/ex02-answer.md` | Gmail → 摘要 → Notion 呼叫序列設計、實際執行 3 步、優雅失敗設計 |
| `scripts/list_issues_api.py` | 方式 B：Python urllib 呼叫 GitHub REST API，只發 GET |
| `scripts/graceful_workflow.py` | 延伸思考：模擬 token 中途過期的 checkpoint＋冪等續跑 |
| `.mcp.json` | project scope 示範：`notion-local`，token 用 `${NOTION_TOKEN}` 佔位 |

## 驗證結果

| 項目 | 結果 |
| --- | --- |
| `claude mcp list` | 17 個 server：15 ✔、Microsoft 365 與 Notion 需登入 |
| `gh api .../issues`（GET） | 回 0 筆；repo 公開、`open_issues_count: 0`、`state=all` 也是 0 |
| `mcp__github__list_issues` | `{"issues":[],"totalCount":0}`，與 REST 一致 |
| `list_issues_api.py` 4 個案例 | 正常（無 token／有 token）exit 0；格式錯、404 正確報錯 exit 1 |
| curl | HTTP 200（curl 本身 exit 23，是 Windows 下 `-o /dev/null` 寫入問題，不影響結果） |
| `mcp__gmail__search_emails` | 成功，回 3 封未讀（純文字格式） |
| `mcp__gmail__read_email` | 成功但內容只有「此信件為 HTML 格式…」佔位字 |
| `mcp__claude_ai_Gmail__get_message` | 成功，`snippet` 有真內容；`UNREAD` 標籤未被移除 |
| `graceful_workflow.py` | 3 個情境斷言全部通過 |
| `claude mcp add --scope project` | 只寫入 `.mcp.json`；確認 `~/.claude.json` 的 user mcpServers 沒有 `notion-local`、本專案 local mcpServers 為空 |

## 和題目要求的差異

1. **能力地圖來源**：題目說看 `settings.json`，實際照本章補充改用 `claude mcp list`（MCP 設定其實在 `~/.claude.json` 和 claude.ai connector，不在 settings.json）。
2. **「列出本週 open issues」**：指定的 repo 目前 0 個 issue，所以兩種方式都回空結果；比較重點放在格式、設定、錯誤處理。只做 GET，沒有建立或修改 issue。
3. **Gmail query**：題目範例 `is:unread subject:urgent` 在我的信箱沒有結果，改用 `is:unread newer_than:2d`；參數名也從 `max_results` 改成工具實際的 `maxResults`。
4. **Notion 步驟沒有實際執行**：claude.ai Notion 需要 OAuth 登入，屬於外部帳號；只寫序列範本，並用 `claude mcp add --scope project` 示範本機 Notion server 的設定（token 佔位）。Notion 工具名稱未經實際清單驗證，已在解答中標註。
5. **任務 2 實際跑了 3 步**（預檢、搜尋、讀信），超過「至少兩步」；讀信那步還多試了一個備援工具。
6. **延伸思考**除了文字設計，另寫了可執行的模擬腳本。

## 已知限制／風險

- `.mcp.json` 中的 `notion-local` 狀態為 Pending approval，下次在本資料夾開 `claude` 會被詢問是否核准；不需要可執行 `claude mcp remove notion-local -s project`。
- 檢查 `~/.claude.json` 時，執行前的備份比較腳本因路徑格式失敗，最後改用「確認 user scope 沒有 notion-local」來驗證，沒有做完整 diff。
- 能力地圖的工具清單是節錄，不是每個 server 的完整清單。
- 未 push、未建 GitHub repo。
