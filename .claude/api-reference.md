# Claude Code 概念速查表

> 這個檔案是學習專案的「內部 API 文件」，記錄 Claude Code 核心概念。
> 遇到練習需要查詢某個概念時，Claude 可以直接引用此處，不用重新解釋。

---

## 記憶系統

| 類型 | 位置 | 變動頻率 | 由誰寫入 | 用途 |
|------|------|---------|---------|------|
| 靜態基石 | `CLAUDE.md` | 低 | 開發者手動 | 技術棧、禁止事項、架構說明 |
| 動態大腦 | `.claude/` | 高 | AI 自動 | 決策記錄、踩坑、API 參考 |
| 動態規則 | `.claude/rules/*.md` | 中 | 開發者手動 | 依檔案路徑按需載入的規則 |
| Auto Memory | `~/.claude/projects/.../memory/` | 中 | AI 自動 | 跨 session 學習記憶 |

## CLAUDE.md 六大支柱

1. **Project Overview** — 專案目標與受眾定義（解決什麼問題）
2. **Tech Stack** — 核心技術棧與**精確版本號**（不寫版本 = 無效）
3. **Architecture** — 資料夾結構與設計模式（每個目錄的職責）
4. **Code Conventions** — 程式碼撰寫慣例（命名、格式、風格）
5. **Testing Approach** — 測試框架與執行規範（怎麼跑測試）
6. **Standing Constraints** — 絕對禁忌與強制規則（永遠不能做的事）

## Hooks 事件類型

| 事件 | 觸發時機 | 典型用途 |
|------|---------|---------|
| `PreToolUse` | 工具執行前 | 攔截危險操作、驗證前置條件 |
| `PostToolUse` | 工具執行後 | 自動格式化、記錄日誌 |
| `SessionStart` | session 開始時 | 顯示 git 狀態、環境檢查 |
| `SessionEnd` | session 結束時 | 提交提醒、清理暫存 |

## `.claude/rules/` 動態載入規則

```yaml
---
# 有 paths: → 只在存取對應路徑時載入（動態）
paths:
  - "demo/**/*.py"
---
規則內容...
```

```markdown
<!-- 無 paths: frontmatter → 每個 session 都載入（靜態行為） -->
規則內容...
```

## MCP 工具命名規範

格式：`mcp__{server-name}__{tool-name}`

本專案已配置：

- `mcp__github__list_commits` — 列出 commit 歷史
- `mcp__github__get_file_contents` — 讀取 GitHub 上的檔案
- `mcp__github__list_issues` — 查詢 Issue 清單
- `mcp__github__create_or_update_file` — 更新 GitHub 上的檔案（謹慎使用）

## study-scaffold Skill 指令

| 指令 | 說明 |
|------|------|
| `/study-scaffold carry N` | 把第 N 課 answer/ 複製到第 N+1 課 starter/ |
| `/study-scaffold nlm` | 補跑 NotebookLM（若當初跳過） |

## 5 分鐘 CLAUDE.md 驗證測試（Slide 10）

在全新 session 中輸入：

```
Without me telling you anything, describe this project: the tech stack,
the folder structure, the conventions, and the things I've asked you never to do.
```

通過標準：

- ✅ 正確辨識核心技術棧與版本
- ✅ 準確描述資料夾與架構職責
- ✅ 完整列出禁忌與絕對規範
