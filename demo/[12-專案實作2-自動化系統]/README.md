# [12] 專案實作 2：自動化系統

## 學習目標
- 深度理解並擴充 Gmail→Notion→Telegram 四段 Pipeline
- 掌握 MCP 跨服務整合的實戰技巧
- 建立可排程的自動化工作流

## 前置條件
- [08] Agentic 工作流程
- [09] MCP 白話文

## 課程結構
- `exercise-01-基礎.md`：現有 Pipeline 分析
- `exercise-02-進階.md`：擴充 Pipeline 功能
- `exercise-03-綜合.md`：完整自動化系統升級

## 完成標準
- [ ] 閱讀本課 README
- [ ] 完成基礎練習，解答存入 `answer/`
- [ ] 完成進階練習，解答存入 `answer/`
- [ ] 填寫 STEP_LOG.md
- [ ] 執行 carry（攜帶答案到下一課）

## 本課重點概念
- Pipeline 設計：每段職責清晰、可獨立測試
- 乾跑模式（dry-run）：在不執行副作用的情況下驗證邏輯
- 排程設定：Windows schtasks / Linux cron
- 錯誤通知：失敗時發送 Telegram 告警而不是靜默
