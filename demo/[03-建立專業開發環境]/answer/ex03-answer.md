# 練習 03 解答：MCP 環境配置

## 1. 加入 MCP Server（Google Drive）

### settings.json 片段

```json
{
  "mcpServers": {
    "claude.ai": {
      "type": "http",
      "url": "https://mcp.claude.ai/mcp/claude-ai",
      "headers": {
        "anthropic-beta": "mcp-client-octet-stream-20250916"
      }
    }
  }
}
```

### 設定過程

1. 在 Claude.ai 網頁版連結 Google Drive integration
2. MCP server URL 由 Claude Code 透過 OAuth 自動取得 token
3. 重啟 Claude Code，執行 `/mcp` 確認 server 狀態為 connected

### 驗證可用

在 chat 中問「幫我列出 Google Drive 最近的檔案」，Claude 呼叫 `mcp__claude_ai_Google_Drive__list_recent_files` 並回傳結果，驗證通過。

---

## 2. 最小測試

| 項目 | 內容 |
|------|------|
| 呼叫工具 | `mcp__claude_ai_Google_Drive__list_recent_files` |
| 傳入參數 | 無（列出最近存取的檔案） |
| 期望回應 | 至少 1 個檔案物件，含 `id`、`title`、`mimeType` 欄位 |

**實測結果（本專案已驗證）：** 工具回傳包含 `lesson-01-claude-code-pro.epub`、`lesson-02-claude-code-pro.epub`，`mimeType` 為 `application/epub+zip`，通過。

---

## 3. CLAUDE.md「可用 MCP 工具」章節

```markdown
## 可用 MCP 工具

| 工具名稱 | 何時使用 | 注意事項 |
|---------|---------|---------|
| `mcp__claude_ai_Google_Drive__create_file` | 上傳 EPUB / 檔案到 Google Drive | `disableConversionToGoogleType: true` 保留原格式 |
| `mcp__claude_ai_Google_Drive__list_recent_files` | 確認上傳是否成功 | 只顯示最近存取，非全部 |
| `mcp__claude_ai_Google_Drive__search_files` | 搜尋特定檔案 | 用 `q` 參數過濾 |
| `mcp__github__list_issues` | 查詢 GitHub Issue | 需指定 owner + repo |
| `mcp__github__create_pull_request` | 建立 PR | 需先 push branch |
| `mcp__gmail__search_emails` | 搜尋 Gmail 信件 | 用 Gmail query 語法 |
```

---

## 核心洞察

MCP 讓 Claude Code 從「只能讀寫本機檔案」升級為「可以操作外部服務」：

| 維度 | 沒有 MCP | 有 MCP |
|------|---------|-------|
| 上傳檔案 | 手動上傳 | Claude 直接呼叫 Drive API |
| 查 GitHub Issue | 複製貼上 | Claude 直接 query |
| session 結束後 | 靠記憶 | 靠工具查詢即時狀態 |

**安全邊界：** Claude Code 只能呼叫已在 settings.json 配置的 MCP server 上的工具 — 沒有授權的外部服務 Claude 無法自行連接。
