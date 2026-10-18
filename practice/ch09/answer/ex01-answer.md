# 練習 01 解答 — MCP 工具探索

> 執行日期：2026-10-18｜環境：Windows 10 + Git Bash｜資料來源：`claude mcp list` 實際輸出（不是看 settings.json）

## 任務 1：MCP 能力地圖

### 1-1 `claude mcp list` 實際結果（2026-10-18）

```text
claude.ai Claude Docs:    https://api.anthropic.com/v1/pages/mcp   - ✔ Connected
claude.ai Microsoft 365:  https://microsoft365.mcp.claude.com/mcp  - ! Needs authentication
claude.ai Notify Server:  https://mcp.chenghyang.uk/mcp            - ✔ Connected
claude.ai Context7:       https://mcp.context7.com/mcp             - ✔ Connected
claude.ai Google Calendar:https://calendarmcp.googleapis.com/mcp/v1 - ✔ Connected
claude.ai Gmail:          https://gmailmcp.googleapis.com/mcp/v1   - ✔ Connected
claude.ai Google Drive:   https://drivemcp.googleapis.com/mcp/v1   - ✔ Connected
claude.ai Notion:         https://mcp.notion.com/mcp               - ! Needs authentication
plugin:telegram:telegram: bun run ... telegram/0.0.7 start          - ✔ Connected
github:          https://api.githubcopilot.com/mcp (HTTP)          - ✔ Connected
gmail:           npx @gongrzhe/server-gmail-autoauth-mcp           - ✔ Connected
gdrive:          npx @modelcontextprotocol/server-gdrive           - ✔ Connected
google-calendar: npx @gongrzhe/server-calendar-autoauth-mcp        - ✔ Connected
youtube:         npx -y zubeid-youtube-mcp-server                  - ✔ Connected
google-docs:     google-docs-mcp                                   - ✔ Connected
notebooklm:      npx -y notebooklm-mcp                             - ✔ Connected
nano-banana:     npx -y @ycse/nanobanana-mcp@latest                - ✔ Connected
```

共 17 個：15 個已連線，2 個需要登入（Microsoft 365、Notion）。
來源分三種：**user scope**（`~/.claude.json`，8 個 npx/HTTP）、**claude.ai connector**（雲端帳號綁定，8 個）、**plugin**（telegram）。

### 1-2 能力地圖

工具名稱取自本 session 實際載入的 tool 清單（`mcp__<server>__<tool>`）。

| MCP Server | 提供的 Tools（節錄） | 適合場景 | 限制 / 注意事項 |
| --- | --- | --- | --- |
| **github**（HTTP，Copilot 端點） | list_issues, issue_read, issue_write, search_issues, list_pull_requests, create_pull_request, get_file_contents, push_files, create_repository, delete_repository… | 查 issue/PR、code search、PR review | 權限＝token 權限，含 **delete_repository / push_files 等破壞性工具**，要靠權限設定擋；回傳的是 GraphQL 風格（`totalCount`、`pageInfo`） |
| **gmail**（gongrzhe，本機 npx） | search_emails, read_email, send_email, draft_email, modify_email, batch_delete_emails, create_filter, list_email_labels… | 搜信、批次貼標籤、建 filter | **純 HTML 信 read_email 只回佔位字**（本次實測踩到）；有 batch_delete，誤用風險高 |
| **claude.ai Gmail**（官方 connector） | search_threads, get_message, get_thread, create_draft, send_message, label_message, trash_message… | 讀信（支援 `PLAIN_TEXT` 格式）、寄信 | 走 claude.ai 帳號 OAuth；與本機 gmail 功能重疊，選一個為主 |
| **gdrive**（官方 reference server） | search | 搜 Drive 檔案 | 只有搜尋；要讀寫改用 claude.ai Google Drive |
| **claude.ai Google Drive** | search_files, read_file_content, create_file, update_file, share_file, trash_file… | 讀寫 Drive 檔案、分享 | share_file 會對外公開，要小心 |
| **google-calendar**（gongrzhe） / **claude.ai Google Calendar** | list_events, create_event, update_event, delete_event / suggest_time, respond_to_event | 查行程、排會議 | 兩套重疊；時區要明確給 |
| **google-docs** | google_docs_read_document, google_docs_auth | 讀 Google Doc | 只能讀；要先 auth |
| **notebooklm** | list_notebooks, ask_question, add_notebook, select_notebook, re_auth, get_health… | 對 NotebookLM 問答 | 走瀏覽器自動化，auth 約 1～2 小時就過期（啟動時 hook 已警告 220 小時） |
| **youtube** | videos_searchVideos, videos_getVideo, transcripts_getTranscript, channels_listVideos… | 搜影片、抓字幕 | 需 YouTube API key，有每日配額 |
| **nano-banana** | gemini_generate_image, gemini_edit_image, gemini_chat… | 生圖、修圖 | 需 Gemini API key，會產生費用 |
| **claude.ai Context7** | resolve-library-id, query-docs | 查最新套件文件 | 只讀；依賴 Context7 收錄範圍 |
| **claude.ai Notify Server**（自架） | send_telegram, send_line, send_gmail, send_all, upload_to_gdrive… | 一次推多管道通知 | 自架服務，伺服器掛掉就全斷 |
| **claude.ai Claude Docs** | batch, update, create, read, export… | 建協作文件 | 只在使用者要求建文件時用 |
| **plugin:telegram** | reply, react, edit_message, download_attachment | Telegram 雙向對話 | 只能回已收到的訊息，看不到歷史 |
| **claude.ai Notion** | （未登入，無工具） | 建頁面、資料庫 | **! Needs authentication** — 需在 claude.ai 完成 OAuth |
| **claude.ai Microsoft 365** | authenticate, complete_authentication | Outlook / OneDrive | **! Needs authentication** |

### 1-3 觀察

1. **功能重疊**：Gmail、Calendar、Drive 各有本機與 claude.ai 兩套。重疊會讓 Claude 選錯工具，也多吃 context（工具描述都要載入）。建議每個服務只留一套為主。
2. **破壞性工具很多**：github 的 `delete_repository`、gmail 的 `batch_delete_emails` 都直接暴露。能力地圖的「限制」欄最該寫的是這類風險。
3. **auth 型態決定穩定度**：API key（youtube、nano-banana）最穩；OAuth refresh token 次之；瀏覽器 cookie（notebooklm）最容易過期。

## 任務 2：MCP vs 直接 API 比較

任務：列出 `chenghyang2001/kindle-19-claude-code-pro` 的 open issues（**唯讀，只有 GET**）。

### 方式 A：GitHub MCP

```json
// 呼叫 mcp__github__list_issues
{ "owner": "chenghyang2001", "repo": "kindle-19-claude-code-pro",
  "state": "OPEN", "perPage": 10, "fields": ["number","title","state","created_at"] }
```

實際回應：

```json
{"issues":[],"pageInfo":{"hasNextPage":false,"hasPreviousPage":false},"totalCount":0}
```

### 方式 B：直接呼叫 REST API

**B-1 用 gh CLI（題目指定）**

```bash
gh api "repos/chenghyang2001/kindle-19-claude-code-pro/issues?state=open&per_page=10" \
  --jq '.[] | {number, title, state, created_at, is_pr: (.pull_request != null)}'
# 輸出：（空）
gh api repos/chenghyang2001/kindle-19-claude-code-pro --jq '{full_name, private, open_issues_count, has_issues}'
# {"full_name":"chenghyang2001/kindle-19-claude-code-pro","has_issues":true,"open_issues_count":0,"private":false}
gh api "repos/chenghyang2001/kindle-19-claude-code-pro/issues?state=all" --jq 'length'
# 0
```

**B-2 用 Python（`scripts/list_issues_api.py`，urllib，只發 GET）**

| 測試案例 | 指令 | 結果 |
| --- | --- | --- |
| 正常（不帶 token） | `python scripts/list_issues_api.py` | `{"open_issue_count": 0, "issues": []}`，exit 0 |
| 正常（帶 token） | `GITHUB_TOKEN=$(gh auth token) python ...` | 同上，exit 0 |
| 錯誤：repo 格式錯 | `... badrepo` | `錯誤：repo 格式應為 owner/name`，exit 1 |
| 錯誤：repo 不存在 | `... chenghyang2001/no-such-repo-xyz` | `錯誤：GitHub API 回傳 HTTP 404：Not Found`，exit 1 |

**B-3 curl**：`curl -s -w "HTTP %{http_code}" ".../issues?state=open"` → `HTTP 200`，body 為 `[]`。

> 結論一致：這個 repo **目前 0 個 issue**（open 和 closed 都是 0）。三種方式結果相同，只是格式不同。

### 比較

| 面向 | 方式 A：MCP | 方式 B：REST API（gh / Python / curl） |
| --- | --- | --- |
| **程式碼複雜度** | 0 行，一次 tool call，參數是 JSON | gh：1 行；Python：約 60 行（含錯誤處理、排除 PR、參數驗證） |
| **設定成本** | 一次性：`claude mcp add` + OAuth／PAT。設好後每個 session 都能用 | gh：`gh auth login` 一次；Python：自己管 token、header、API 版本、分頁 |
| **回應格式** | 已整理過（`issues`、`totalCount`、`pageInfo`），可用 `fields` 只取需要欄位，省 context | 原始 JSON，欄位很多；**PR 也會出現在 `/issues`**，要自己用 `pull_request` 欄位過濾 |
| **錯誤處理** | 由 MCP server 包裝，Claude 看得到錯誤文字，但不好寫程式重試 | 完全自己控制（HTTP 碼、重試、timeout） |
| **可重複／排程** | 需要 Claude 在迴路中，不適合 cron | 可放進 cron、CI、n8n，無人值守 |
| **成本** | 每次呼叫都吃 token；工具描述常駐 context | 不吃 token |
| **安全** | 工具清單包含寫入／刪除，靠權限設定擋 | 只會做你寫的事（本腳本只能 GET） |

### 適合的使用場景

- **選 MCP**：互動式探索、臨時查詢、需要 Claude 邊看結果邊決定下一步（例如「找出最舊的 bug issue 並讀內容」）。
- **選直接 API**：固定流程、排程、大量資料、要精準控制錯誤與重試、或不想燒 token 的情境。
- **折衷**：先用 MCP 摸清楚要什麼，定案後寫成腳本固定下來。
