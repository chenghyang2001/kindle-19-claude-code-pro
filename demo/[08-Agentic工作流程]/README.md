# [08] Agentic 工作流程

## 學習目標
- 理解 Sub-agent 設計模式與觸發時機
- 掌握 parallel() vs pipeline() 的選擇策略
- 設計你的第一個多代理工作流

## 前置條件
- [03] 建立專業開發環境
- [04] 生產級程式碼

## 課程結構
- `exercise-01-基礎.md`：識別並行機會
- `exercise-02-進階.md`：設計 Sub-agent 合約
- `exercise-03-綜合.md`：實作三代理工作流

## 完成標準
- [ ] 閱讀本課 README
- [ ] 完成基礎練習，解答存入 `answer/`
- [ ] 完成進階練習，解答存入 `answer/`
- [ ] 填寫 STEP_LOG.md
- [ ] 執行 carry（攜帶答案到下一課）

## 本課重點概念
- parallel()：所有任務同時開始，等全部完成才繼續（有 barrier）
- pipeline()：每個 item 流過所有 stage，無全局等待（預設選擇）
- Agent 間合約（contract）：輸入/輸出 schema 的重要性
- 信號檔模式（Signal File）：agent 間的非同步溝通
