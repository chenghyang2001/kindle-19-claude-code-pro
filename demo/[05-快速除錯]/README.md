# [05] 快速除錯

## 學習目標
- 掌握系統化 debug 流程（假設-驗證循環）
- 學會解讀 stack trace 並快速定位根本原因
- 建立個人 debug 工具箱

## 前置條件
- [04] 生產級程式碼

## 課程結構
- `exercise-01-基礎.md`：Stack Trace 解讀
- `exercise-02-進階.md`：系統化 Debug 流程
- `exercise-03-綜合.md`：建立 Debug 工具箱

## 完成標準
- [ ] 閱讀本課 README
- [ ] 完成基礎練習，解答存入 `answer/`
- [ ] 完成進階練習，解答存入 `answer/`
- [ ] 填寫 STEP_LOG.md
- [ ] 執行 carry（攜帶答案到下一課）

## 本課重點概念
- 二分搜尋法定位 bug（縮小範圍策略）
- Stack trace 三要素：錯誤類型 / 發生位置 / 呼叫鏈
- 假設-驗證循環（提出假設 → 設計驗證 → 確認/排除）
- Claude Code debug 提示詞模板設計
