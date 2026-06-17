# Exercise 02 解答 — MCP 整合實戰

## 任務 1：MCP 呼叫序列設計（Gmail → 摘要 → Notion/Google Docs 任務）

> 說明：本環境無 Notion MCP，以 `mcp__google-docs__createDocument`（Google Docs）替代。
> 同樣的設計模式完全可平移至 Notion MCP（`mcp__notion__create_page`）。

---

```
Step 1: mcp__claude_ai_Gmail__search_threads
  輸入: {
    "query": "is:unread",
    "max_results": 10
  }
  輸出: [
    {
      "id": "19xxx",
      "snippet": "信件摘要前 100 字...",
      "subject": "...",
      "from": "..."
    },
    ...
  ]
  失敗處理: 回傳空陣列，繼續執行（空收件匣也是合法狀態，不應停止 workflow）

Step 2: mcp__claude_ai_Gmail__get_thread
  說明: 對每封信抓完整內容（Step 1 的 snippet 太短）
  輸入: {
    "thread_id": "19xxx"   ← 從 Step 1 取得的 id
  }
  輸出: {
    "id": "19xxx",
    "messages": [
      {
        "id": "msg_id",
        "from": "sender@example.com",
        "subject": "會議提醒...",
        "body": "完整信件內文...",
        "date": "2026-06-17T08:00:00Z"
      }
    ]
  }
  失敗處理: 記錄 thread_id + 錯誤訊息，跳過此封信（non-critical），繼續下一封

Step 3: Claude 內部處理（無 MCP 呼叫）
  說明: 把 Step 2 的 body 整理為 action item 清單
  輸出 (in-context):
    {
      "subject": "週五例行會議",
      "action_items": [
        "準備 Q2 銷售報告",
        "更新 Jira 票號 KND-123 狀態"
      ],
      "priority": "high",
      "deadline": "2026-06-20"
    }

Step 4: mcp__google-docs__createDocument
  說明: 建立 Google Docs 任務文件（Notion 替代方案）
  輸入: {
    "title": "任務：週五例行會議 (2026-06-17)",
    "content": "## 行動項目\n- 準備 Q2 銷售報告\n- 更新 Jira KND-123\n\n**截止：** 2026-06-20\n**來源：** Gmail thread 19xxx"
  }
  輸出: {
    "documentId": "1abc...",
    "title": "任務：週五例行會議 (2026-06-17)",
    "webViewLink": "https://docs.google.com/document/d/1abc..."
  }
  失敗處理: 停止（critical — 建不了任務，整個 workflow 失效），回報錯誤給使用者
```

---

## 任務 2：實際執行記錄

### 執行 Step 1：`mcp__claude_ai_Gmail__search_threads`

**實際參數**：
```json
{ "query": "is:unread", "max_results": 5 }
```

**實際回應格式（抽樣）**：
```json
[
  {
    "id": "thread_id_實際值",
    "snippet": "信件前段摘要...",
    "messages": [
      {
        "id": "msg_id",
        "subject": "...",
        "from": "sender@...",
        "date": "..."
      }
    ]
  }
]
```

**設計 vs 實際的差異**：
- 設計時以為 Step 1 只回傳簡單清單，實際上 Gmail MCP 的 `search_threads` 已包含 messages 陣列（含 subject/from），不一定需要另做 `get_thread`
- 但 `snippet` 仍是截短的，完整 body 仍需 `get_thread`

### 執行 Step 2：`mcp__claude_ai_Gmail__get_thread`

**遇到的情況**：
- thread_id 格式必須用 Step 1 回傳的原始 id（不能自己猜格式）
- 回傳的 body 有時是 HTML，需要 Claude 剝離 HTML tag 才能摘要

**解決方式**：
- body 預處理：Claude 在 Step 3 內部處理時自動忽略 `<div>`、`<br>` 等 HTML tag
- 若 body 完全是 base64 encoded，需先 decode — 這是實際踩坑，設計文件沒提

---

## 延伸思考：Auth Token 過期的「優雅失敗」設計

**問題情境**：workflow 執行到 Step 3（已讀 Gmail、已整理），Step 4 建 Docs 時 Google auth 過期。

**錯誤設計（靜默失敗）**：
```
Step 4 失敗 → 回傳 null → 當作空字串繼續 → 沒有建任何任務 → 使用者以為完成了
```

**優雅失敗設計（三層）**：

```
Layer 1：偵測
  catch (error) {
    if (error.message.includes("401") || error.message.includes("auth")) {
      → 明確標記為 AUTH_EXPIRED，不是普通失敗
    }
  }

Layer 2：補救（auth 過期才值得重試）
  if (error.type === "AUTH_EXPIRED") {
    mcp__notebooklm__refresh_auth()  ← 嘗試刷新 token
    retry Step 4 一次
  }

Layer 3：保全（重試失敗才觸發）
  if (retry also fails) {
    → 把整理好的 action_items 存到本地檔案（fallback）
    → 通知使用者：「auth 過期，任務清單已暫存，請重新認證後執行 Step 4」
    → 不繼續，不假裝成功
  }
```

**關鍵原則**：
- auth 過期 ≠ 任務失敗。前面做的工作（讀信、整理）是有價值的，要保存。
- 讓使用者「知道卡在哪一步」，而不是看到「workflow completed: 0 tasks created」

---

## 學習洞察

MCP 序列設計的最重要洞察：**設計文件描述的是理想路徑，實際格式往往有差異**（HTML body、base64 encoding、多餘欄位），真正的 MCP 整合一定要先用「小試一下」模式取得真實回應，再設計 downstream 的處理邏輯。
