# Exercise 03 解答 — MCP 環境配置

## 任務 1：加入 MCP Server

### 選擇：GitHub MCP（已實際使用中）

本機已配置 GitHub MCP，可在 `~/.claude.json` 或 `settings.json` 中看到。

### settings.json 配置範例

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**注意事項**：
- `GITHUB_TOKEN` 必須有 `repo` 和 `issues` 的讀寫權限
- token 放環境變數，不寫進 settings.json 本身（避免 git 洩漏）
- 使用 `${ENV_VAR}` 語法引用環境變數

### 設定驗證步驟
1. 重啟 Claude Code session
2. 在 session 中輸入：「列出 chenghyang2001/kindle-19-claude-code-pro 的最近 3 個 commit」
3. 若 MCP 正常，Claude 會呼叫 `mcp__github__list_commits` 並回傳結果

---

## 任務 2：最小測試

### 測試設計

| 項目 | 內容 |
|------|------|
| 呼叫工具 | `mcp__github__list_commits` |
| 參數 | `owner: "chenghyang2001"`, `repo: "kindle-19-claude-code-pro"`, `perPage: 3` |
| 期望回應 | 含 SHA + 訊息 + 時間的 commit 列表 |

### 實際測試結果（Session 中驗證）
- 呼叫 `mcp__github__list_commits` ✅ 可用
- 回傳最近 commits（包含 cfa9ee5 等）✅
- `mcp__github__get_file_contents` 可讀取 CLAUDE.md ✅

---

## 任務 3：更新 CLAUDE.md — 加入「可用 MCP 工具」章節

```markdown
## 可用 MCP 工具

| 工具名稱 | 何時使用 | 注意事項 |
|---------|---------|---------|
| mcp__github__list_commits | 查看 commit 歷史 | 需要 GITHUB_TOKEN |
| mcp__github__get_file_contents | 讀取 GitHub 上的特定檔案 | 預設讀 main branch |
| mcp__github__list_issues | 查詢 GitHub Issue 清單 | 需要有 repo 存取權限 |
| mcp__github__create_or_update_file | 更新 GitHub 上的檔案 | 會直接 commit，謹慎使用 |
| mcp__github__list_pull_requests | 列出 PR 清單 | 含草稿 PR |
```

---

## MCP vs 內建工具 選用原則

| 情境 | 用 MCP | 用內建工具（Bash/Read） |
|------|--------|----------------------|
| 讀取 GitHub 上的 PR/Issue | ✅ GitHub MCP | ❌（需要 gh CLI） |
| 讀取本機檔案 | ❌ | ✅ Read 工具 |
| 查 git log | ❌ | ✅ Bash `git log` |
| 在 GitHub 建立 Issue | ✅ GitHub MCP | ❌（需要 gh CLI + 更複雜） |

---

## 學習洞察
MCP 的本質是「讓 Claude 能呼叫外部服務」，而不只是讀寫本機檔案。
GitHub MCP 讓 Claude 從「只能看本機 repo」升級到「能直接操作 GitHub 的遠端狀態」。
設定 MCP 的最重要原則：**token 放環境變數，永遠不 commit 進 settings.json**。
