# 練習 02 解答 — MCP 整合實戰

> 執行日期：2026-10-18｜流程：Gmail 讀信 → 整理摘要 → 建立 Notion 任務

## 任務 1：MCP 呼叫序列設計

先說明工具選擇：本環境有兩套 Gmail MCP（本機 `gmail` 和 `claude_ai_Gmail`），Notion 只有 `claude_ai_Notion`（**目前 Needs authentication**）。Notion 的工具名稱因為還沒登入、看不到實際清單，下面寫的是官方 Notion MCP 的命名，標記「⚠ 未驗證」。

```text
Step 0: 預檢（preflight）— 不是 MCP tool，是 Claude 端的檢查
  輸入: claude mcp list
  輸出: 每個 server 的 ✔ Connected / ! Needs authentication
  失敗處理: 任一必要 server 未連線 → 停止，告訴使用者要先登入哪個（不要跑到一半才發現）

Step 1: mcp__gmail__search_emails
  輸入: { "query": "is:unread newer_than:2d", "maxResults": 10 }
  輸出: 文字清單，每封含 ID / Subject / From / Date
  失敗處理: 
    - 回傳 0 封 → 正常結束（沒事可做），回報「沒有符合的信」
    - auth 錯誤 → 停止（後面都依賴這步）

Step 2: mcp__claude_ai_Gmail__get_message（每封信各一次）
  輸入: { "messageId": "<Step 1 的 ID>", "messageFormat": "PLAIN_TEXT" }
  輸出: { "id", "subject", "sender", "date", "labelIds", "plaintextBody", "snippet", "viewUrl" }
  失敗處理: 單封失敗 → 記錄並跳過，繼續處理其他封；全部失敗 → 停止
  備註: 不用 mcp__gmail__read_email，因為它對純 HTML 信只回佔位字（見任務 2）

Step 3: Claude 自己整理摘要（不呼叫 MCP）
  輸入: Step 2 的 subject + plaintextBody（為空或是佔位字時改用 snippet）
  輸出: [ { "source_id": "...", "title": "[摘要] ...", "summary": "3 行內", "priority": "高/中/低", "link": "<viewUrl>" } ]
  失敗處理: 內文太短無法摘要 → 用 subject 當 title、summary 留「需人工查看」

Step 4: mcp__claude_ai_Notion__notion-search   ⚠ 未驗證
  輸入: { "query": "任務清單" }
  輸出: 找到目標資料庫的 id
  失敗處理: 找不到資料庫 → 停止（不要自己亂建一個資料庫）

Step 5: mcp__claude_ai_Notion__notion-create-pages   ⚠ 未驗證（每筆摘要一次）
  輸入: { "parent": { "database_id": "<Step 4>" },
          "pages": [ { "properties": { "Name": "[摘要] ...", "Status": "待處理",
                                       "來源信件ID": "<source_id>" },
                       "content": "<summary>\n\n原信：<link>" } ] }
  輸出: { "id": "<page_id>", "url": "https://www.notion.so/..." }
  失敗處理: 
    - 先用 notion-search 查「來源信件ID」是否已存在 → 已存在就跳過（防重複）
    - auth 錯誤 → 立刻停止，回報「已建 N 筆、未建清單」，保留斷點

Step 6（選用）: mcp__gmail__modify_email
  輸入: { "messageId": "<source_id>", "addLabelIds": ["<已轉 Notion 的 label id>"] }
  失敗處理: 失敗只警告，不影響已建立的任務
  備註: 只在 Step 5 成功後才做，避免「標了已處理但 Notion 沒建」
```

## 任務 2：實際執行（Step 0～2，共三步）

### Step 0：預檢 — `claude mcp list`

結果：`gmail` ✔、`claude.ai Gmail` ✔、**`claude.ai Notion` ! Needs authentication**。
→ 依設計，Step 4～5 不能真的跑，只能停在 Step 3。這正好驗證了預檢的價值：在讀信前就知道最後一步會失敗。

### Step 1：`mcp__gmail__search_emails`

| 項目 | 設計時 | 實際 |
| --- | --- | --- |
| 參數 | `query`, `max_results` | **`query`, `maxResults`**（駝峰命名；題目範例的 `max_results` 會被 schema 拒絕） |
| query | `is:unread subject:urgent` | `is:unread newer_than:2d`（我的信箱沒有標題含 urgent 的信，改成「兩天內未讀」才有資料） |
| maxResults | 10 | 3（示範用，少佔 context） |

實際回應（**純文字，不是 JSON 陣列**）：

```text
ID: 1a14c4ff27a2deb8
Subject: 📈 台股每日盤前報告 2026-10-18（週日）｜三大法人同買賣超 × 國際因素 × 基本面前10
From: ChengHsien Yang <chenghyang2001@gmail.com>
Date: Sat, 17 Oct 2026 17:01:10 -0700

ID: 1a14c4ef6c25df8b
Subject: 📊 訂閱稽核 2026-10-18 — 本月月費 …（15 項訂閱）
...

ID: 1a14c45eebca8f54
Subject: 【Kindle 19】Claude Code Pro 影片摘要已上傳 YouTube（18 支＋播放清單）
From: ChengHsien Yang <chenghyang2001@gmail.com>
Date: Sat, 17 Oct 2026 16:50:13 -0700
```

格式和預期不同：設計時預期 `[{id, subject, body}]`，實際是人看的文字，**也沒有 body**。要內文必須再呼叫一次讀信工具（所以序列多了 Step 2）。

### Step 2：讀信 — 第一次失敗、換工具後成功

**2a. `mcp__gmail__read_email`（本機 gongrzhe 版）**

```json
{ "messageId": "1a14c45eebca8f54" }
```

回應：

```text
Subject: 【Kindle 19】Claude Code Pro 影片摘要已上傳 YouTube（18 支＋播放清單）
...
此信件為 HTML 格式，請用支援 HTML 的用戶端閱讀。
```

問題：這封信的 text/plain 部分只放了一行佔位字，真正內容在 HTML 部分，這個 MCP 不轉 HTML。**這是「靜默產生錯誤結果」的典型例子**：工具回傳成功、沒有錯誤，但內容是假的。如果直接拿去摘要，Notion 任務會寫成「此信件為 HTML 格式」。

**2b. `mcp__claude_ai_Gmail__get_message`（官方 connector，備援）**

```json
{ "messageId": "1a14c45eebca8f54", "messageFormat": "PLAIN_TEXT" }
```

回應（節錄）：

```json
{
  "id": "1a14c45eebca8f54",
  "labelIds": ["UNREAD", "SENT", "INBOX"],
  "plaintextBody": "此信件為 HTML 格式，請用支援 HTML 的用戶端閱讀。",
  "snippet": "《Claude Code Pro》影片摘要已全部上傳。 播放清單與影片皆為私人，需登入你的 YouTube 帳號觀看 播放清單：19｜Claude Code Pro 影片摘要 https://www.youtube.com/playlist?list=… 19｜Claude Code Pro 01 第1章｜從聊天機器人到程式開發夥伴 https://youtu.be/…",
  "subject": "【Kindle 19】Claude Code Pro 影片摘要已上傳 YouTube（18 支＋播放清單）",
  "viewUrl": "https://mail.google.com/mail/?authuser=…#all/thread-f:…"
}
```

`plaintextBody` 一樣是佔位字（因為信本身有 text/plain 部分，工具不會再去轉 HTML），**但 `snippet` 有真正內容**，還多了 `viewUrl` 可以當 Notion 任務的原信連結。
解法：Step 3 加規則「`plaintextBody` 是佔位字或太短 → 改用 `snippet`」。要完整內文可改用 `messageFormat: "FULL_CONTENT"` 取 `html_body` 再轉文字。

另外確認：`labelIds` 仍有 `UNREAD`，表示讀信**不會**把信標成已讀，重跑不影響信箱狀態。

### Step 3：摘要（Claude 端，實際產出）

```json
[{
  "source_id": "1a14c45eebca8f54",
  "title": "[摘要] Kindle 19 影片摘要已上傳 YouTube（18 支）",
  "summary": "《Claude Code Pro》18 支章節影片摘要與播放清單已上傳，皆為私人，需登入 YouTube 帳號觀看。",
  "priority": "低",
  "link": "https://mail.google.com/mail/?authuser=…#all/thread-f:1879342856482230100"
}]
```

### Step 4～5：Notion — 未執行（需登入）

`claude.ai Notion` 顯示 `! Needs authentication`。要接上有兩種方式：

1. 在 claude.ai 的 Connectors 完成 Notion OAuth（最簡單）。
2. 用本機版 server，**只寫在本專案 `.mcp.json`**（本次已實際加入示範，token 用佔位）：

```bash
claude mcp add --scope project notion-local -e 'NOTION_TOKEN=${NOTION_TOKEN}' -- npx -y @notionhq/notion-mcp-server
```

產生的 `.mcp.json`：

```json
{
  "mcpServers": {
    "notion-local": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": { "NOTION_TOKEN": "${NOTION_TOKEN}" }
    }
  }
}
```

`claude mcp get notion-local` → `Scope: Project config (shared via .mcp.json)`、`Status: ⏸ Pending approval`。
`${NOTION_TOKEN}` 會在啟動時從環境變數展開，所以 `.mcp.json` 可以進版控而不洩漏 token。要真正使用：到 Notion 建 internal integration 取得 token → 設環境變數 `NOTION_TOKEN` → 把目標資料庫分享給該 integration → 重開 `claude` 並核准這個 project server。

### 設計 vs 實際 差異總表

| 項目 | 設計 | 實際 | 處理 |
| --- | --- | --- | --- |
| 參數命名 | `max_results` | `maxResults` | 照工具 schema，不要照記憶 |
| 搜尋結果格式 | JSON 陣列含 body | 純文字、無 body | 增加讀信步驟 |
| 讀信內容 | 有內文 | HTML 信只有佔位字 | 換工具 + 改用 snippet |
| Notion | 可呼叫 | 未登入 | 預檢擋下，只寫範本 |

## 延伸思考：token 中途過期，怎麼「優雅失敗」

核心原則：**寧可大聲停下，也不要安靜地產出錯的結果。**

| 機制 | 做法 | 防的是什麼 |
| --- | --- | --- |
| 1. 預檢（fail fast） | 開跑前檢查所有 server 的 auth，有任何一個不行就不開始 | 讀了一堆信、最後一步才失敗 |
| 2. 區分「空」與「錯」 | 0 封信 = 正常；auth 錯誤 = 停止。絕不把錯誤轉成空陣列繼續跑 | 「沒有新信」其實是「讀不到信」 |
| 3. 內容合理性檢查 | 回應成功但內容可疑（如「此信件為 HTML 格式」）→ 視為失敗或改走備援 | 本次實測踩到的靜默錯誤 |
| 4. Checkpoint | 每完成一筆就寫入斷點檔（來源 ID → 結果 ID） | 重跑時從頭來過 |
| 5. 冪等（idempotency key） | 用「來源信件 ID」當 key，建任務前先查是否已存在 | 續跑時重複建立任務 |
| 6. 副作用排最後 | 「標記信件已處理」只在 Notion 建立成功後做 | 標了已處理卻沒有任務，信從此被忽略 |
| 7. 明確回報 | 結束時回 `{status: ok / partial_failed / preflight_failed, created, pending, error}` | 使用者不知道做到哪 |

### 可執行示範：`scripts/graceful_workflow.py`

用假的服務模擬「Notion 在建第 2 筆時 token 過期」，實際執行結果：

```text
第 1 次執行（第 2 筆時 token 過期）： {"status": "partial_failed", "created": ["task-1"], "pending": ["m2", "m3"], "error": "Notion token expired (401)"}
第 2 次執行（重新授權後續跑）： {"status": "ok", "created": ["task-1", "task-2", "task-3"], "pending": [], "error": null}
第 3 次執行（preflight 就發現 Notion 未授權）： {"status": "preflight_failed", "created": [], "pending": [], "error": "未授權：['notion']"}
全部斷言通過
```

驗證了三件事：過期時停下並列出未完成清單；重新授權後從斷點續跑；續跑後 Notion 只有 3 筆、沒有重複。
