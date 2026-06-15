# 練習 01 — 基礎：現有 Pipeline 分析

## 情境說明
你要深度理解 `email-automation-演練/` 的 Pipeline 架構，才能安全地擴充功能。

## 任務

### 任務 1：繪製資料流圖
閱讀 `email-automation-演練/` 的以下檔案：
- `run_briefing.py`
- `gmail_fetcher.py`
- `email_filter.py`
- `summarizer.py`
- `notion_creator.py`
- `telegram_briefer.py`

然後繪製完整的資料流圖，對每一段列出：

| 段落 | 輸入 | 輸出 | 可能的失敗點 |
|------|------|------|------------|
| gmail_fetcher | Gmail MCP 設定 | 信件清單（list[dict]）| Gmail auth 過期 |
| email_filter | 信件清單 | 過濾後的清單 | ... |
| summarizer | ... | ... | ... |
| notion_creator | ... | ... | ... |
| telegram_briefer | ... | ... | ... |

### 任務 2：找改進機會
閱讀完程式碼後，找出至少 3 個可以改進的地方，分類為：

- **效能**：哪裡可以更快？（例如：可以並行的操作）
- **可靠性**：哪裡容易出錯？（例如：沒有錯誤處理的呼叫）
- **新功能**：哪個新功能最值得加？（你的建議）

## 完成後
將資料流圖 + 改進機會分析存入 `answer/ex01-answer.md`
