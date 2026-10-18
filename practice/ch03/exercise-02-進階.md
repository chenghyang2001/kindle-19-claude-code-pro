# 練習 02 — 進階：設定 Hooks

## 情境說明
你想要在 Claude Code 的工作流程中加入自動化守門機制。

## 任務

### 任務 1：設計 PostToolUse Hook
在 `settings.json` 中設定一個 PostToolUse hook：
當 Write 工具寫入 .py 檔案時，自動執行格式化。

設計要求：
1. hook 只在寫入 .py 時觸發（不影響其他檔案類型）
2. 格式化工具選擇：black 或 ruff format
3. 格式化失敗時：記錄錯誤但不中斷流程

在 `answer/ex02-answer.md` 中寫出：
- 完整的 settings.json 片段
- 測試步驟（如何確認 hook 有效）

### 任務 2：設定 SessionStart Hook
加入一個 SessionStart hook，在每個 session 開始時：
1. 顯示當前 git branch 名稱
2. 顯示最近 3 個 commit 的訊息
3. 顯示有沒有未提交的變更

目的：讓 Claude Code 每次啟動時就知道當前工作狀態。

## 延伸思考
思考：如果 hook 本身出現 bug（例如格式化工具未安裝），你要如何設計讓它「靜默失敗」而不影響主要工作流？

## 完成後
將解答存入 `answer/ex02-answer.md`
