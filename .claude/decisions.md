# 架構決策記錄

> 這個檔案由 AI 自動更新。每當做出重要的學習策略決策或架構決定，
> 只需告訴 Claude「記錄到 decisions.md」，它就會寫入這裡。

---

## 課程設計決策

### [Lesson 01] 學習工具選擇：Claude Code CLI 優先

**決策**：使用 Claude Code CLI（本機）而非 Claude Chat，做所有有檔案操作的練習。
**原因**：Claude Code 有 Read/Write/Bash 工具，可以真正修改本機檔案；Claude Chat 只能對話。
**生效範圍**：所有 demo/ 練習。

### [Lesson 03] 禁止事項設計：雙重保護策略

**決策**：Flask API 的 CLAUDE.md 禁止事項採「DB 安全 + Git 安全」雙層保護。
**原因**：使用者在 AskUserQuestion 中明確選擇此設計，強調 production DB 不可直接操作 + 禁止 force push。
**生效範圍**：所有後端 API 類型專案的 CLAUDE.md 範本。

### [Lesson 03] Hook 設計原則：靜默失敗

**決策**：所有 Hook 使用 `command || true` 確保不中斷主流程。
**原因**：Hook 是「加分工具」不是「核心流程」，ruff 未安裝或 git 失敗時不應讓 Claude 停工。
**生效範圍**：所有 PostToolUse / SessionStart Hook 設計。

### [Lesson 03] MCP Token 安全規則

**決策**：MCP server 的 API Token 一律用 `${ENV_VAR}` 語法引用，不 commit 進 settings.json。
**原因**：settings.json 可能會被 commit 到 GitHub，明文 token 會洩漏。
**生效範圍**：所有 MCP 環境配置練習。

---

## 學習策略決策

### study-scaffold Carry 機制：answer/ → starter/

**決策**：每課完成後執行 `/study-scaffold carry N`，不手動複製。
**原因**：自動化攜帶確保下一課有正確的前置作業，避免遺漏。

### pptx 內容提取：視覺讀取策略

**決策**：第03章 pptx 是純圖片（PNG embed），改用 vision 讀取投影片圖片。
**原因**：XML 解析 `<a:t>` 返回 0 個文字，所有內容在 `ppt/media/image*.png` 中。
**2026-06-16 驗證**：10 張投影片全部成功讀取。
