# Exercise 01 解答 — MCP 工具探索

## 任務 1：MCP 能力地圖（目前環境已啟用）

| MCP Server | 最常用工具 | 適合場景 | 限制 / 注意事項 |
|-----------|----------|---------|--------------|
| **github** | `list_issues`、`create_pull_request`、`get_file_contents`、`search_code` | 管理 GitHub 專案、審查 PR、搜尋 codebase | 需有 repo 存取權；不能直接 push binary 大檔 |
| **gmail** | `search_threads`、`get_thread`、`create_draft`、`send_email` | 信件 triage、自動草稿、讀信摘要 | 只能存取已 OAuth 授權的帳號；附件無法直接讀取內容 |
| **notebooklm** | `notebook_create`、`notebook_add_local_file`、`audio_overview_create` | 建立知識庫、生成語音摘要、整理書籍章節 | auth 1-2 小時過期；MCP 和 CLI 是獨立 auth，需分別管理 |
| **google-drive** | `create_file`、`read_file_content`、`search_files` | 上傳 EPUB/PDF、讀取備份、搜尋檔案 | `disableConversionToGoogleType: true` 才能保留原格式，否則自動轉 Docs/Sheets |
| **puppeteer** | `puppeteer_screenshot`、`puppeteer_navigate`、`puppeteer_fill` | UI 驗證截圖、表單自動填寫、本地服務測試 | 只能開新的 Chromium 實例，無法接管已登入的 Chrome；只適用 localhost |
| **context7** | `resolve-library-id`、`query-docs` | 查詢第三方套件最新文件（React/Next.js/Drizzle 等） | 需先 resolve id 才能 query；文件有時不完整 |
| **nano-banana** | `gemini_generate_image`、`gemini_edit_image` | 手繪風格圖片生成、中文文字嵌入圖片 | 只能生成圖片，不能分析或 OCR；額度有限 |

---

## 任務 2：MCP vs 直接 REST API 比較（以 GitHub 為例）

**目標任務**：列出本 repo 最近 5 個 open issues

### 方式 A：透過 MCP

```
mcp__github__list_issues({
  "owner": "chenghyang2001",
  "repo": "kindle-19-claude-code-pro",
  "state": "open",
  "per_page": 5
})
```

- **程式碼複雜度**：1 行 JSON
- **設定成本**：已在 settings.json 設定好 token，之後零設定
- **Claude 的體驗**：直接看到結構化結果，可立刻繼續分析或操作

### 方式 B：直接 REST API

```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     "https://api.github.com/repos/chenghyang2001/kindle-19-claude-code-pro/issues?state=open&per_page=5"
```

```python
import os, urllib.request, json
token = os.environ["GITHUB_TOKEN"]
req = urllib.request.Request(
    "https://api.github.com/repos/chenghyang2001/kindle-19-claude-code-pro/issues?state=open&per_page=5",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
)
with urllib.request.urlopen(req) as r:
    issues = json.load(r)
```

- **程式碼複雜度**：~8 行（含錯誤處理更多）
- **設定成本**：每台機器都要設環境變數、管 token 過期、處理 rate limit 回應
- **Claude 的體驗**：需要額外解析 JSON，一個錯誤就中斷

### 比較總結

| 維度 | MCP | 直接 REST API |
|------|-----|--------------|
| 使用複雜度 | 極低（Claude 直接呼叫） | 中等（需處理 HTTP + JSON） |
| 首次設定 | 一次設定 settings.json | 每個環境單獨設定 token |
| 彈性 | 受限於 MCP server 提供的 tools | 完整 API 存取（任何 endpoint） |
| 適合場景 | 互動式、Claude 主導的操作 | 自動化排程、細粒度控制 |
| 錯誤處理 | MCP server 封裝好了 | 需要自行處理 4xx/5xx |

### 結論

**MCP 不是「更強」，而是「更方便 Claude 使用」**。

- 短時間內互動操作 → MCP（Claude 直接呼叫，零設定開銷）
- 長期自動化排程腳本 → 直接 API（VPS cron 不依賴 MCP server 的 auth 狀態）
- 需要 MCP 沒有的 endpoint → 直接 API（例如 GitHub GraphQL、Webhooks 設定）

---

## 關鍵洞察

**MCP 的本質**：把「API 呼叫」變成「Claude 認識的工具」。就像工人的工具箱 — 錘子（MCP tool）讓工人直接用，不需要先知道錘子的金屬冶煉過程（REST API 細節）。

**三種 MCP 能力**：
- **Tool**（可呼叫）：Claude 主動觸發，有副作用（建立、修改、刪除）
- **Resource**（可讀取）：靜態數據，Claude 可訂閱，不改變狀態
- **Prompt**（可注入）：預設的提示詞模板，讓使用者快速套用
