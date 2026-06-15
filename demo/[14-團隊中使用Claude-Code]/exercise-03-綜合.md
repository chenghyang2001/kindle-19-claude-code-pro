# 練習 03 — 綜合挑戰：完整團隊工作流建立

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
為你的個人開發環境（或學習專案）建立一套完整的 Claude Code 工作流，包含：CLAUDE.md、Hooks、Custom Slash Commands。

## 要求

### 1. 建立個人化 CLAUDE.md
為你常用的一個專案（或本學習課程）建立 CLAUDE.md：
- 3 條「必做規則」（例：commit message 格式、測試要求）
- 3 條「禁止事項」（例：不能修改哪些檔案）
- 專案架構說明（Claude 每次對話都需要知道的背景）

### 2. 建立一個 Custom Slash Command
設計一個提升個人開發效率的 Slash Command，例如：
- `/review-pr`：自動審查當前 branch 的變更
- `/write-tests`：為當前檔案自動補寫測試
- `/explain-error`：解釋最近的錯誤訊息

用 `.claude/commands/` 目錄建立這個 Slash Command。

### 3. 建立一個 Pre-commit Hook
設計一個在 `git commit` 前自動執行的 Hook，例如：
- 檢查是否有未處理的 TODO 註解
- 確認 .env 沒有被加入 commit

### 4. 驗收
執行 Slash Command 一次，截圖或記錄結果。
觸發 pre-commit Hook 一次（嘗試 commit 含 TODO 的程式碼），確認 Hook 正確攔截。

## 完成標準
- [ ] CLAUDE.md 建立完成
- [ ] Slash Command 可以執行
- [ ] Hook 可以正確攔截違規 commit

## 完成後
將 CLAUDE.md 內容 + 執行截圖存入 `answer/ex03-answer.md`
