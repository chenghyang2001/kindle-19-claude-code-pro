# 練習 02 — 進階：擴充 Pipeline 功能

## 情境說明
你要為 Pipeline 加入「信件重要度評分」功能，讓系統能自動區分緊急與非緊急信件。

## 任務

### 任務 1：設計評分邏輯
設計一個 1-5 分的信件重要度評分系統：

**評分維度（建議，可以調整）：**
- 寄件人是否在「重要聯絡人」清單
- 主旨是否包含緊急關鍵字（urgent / ASAP / 緊急 / 重要）
- 是否需要回覆（含問號 / 要求確認 / 設有截止日）
- 信件長度（長信通常更重要）
- 是否有附件

**設計 schema：**
```python
class EmailScore:
    score: int          # 1-5
    reasons: list[str]  # 為什麼給這個分數
    requires_reply: bool
    deadline: str | None  # 如果有截止日
```

### 任務 2：設計整合方案
設計如何將評分功能加入現有 Pipeline：

1. 在哪個步驟加入評分？（filter 之後？summarizer 之前？）
2. `email_filter.py` 需要哪些修改？
3. `telegram_briefer.py` 要如何顯示評分資訊？
4. 4-5 分的信件要觸發「緊急通知」（例如：不同的 Telegram 通知格式）

輸出：修改方案文件 + 關鍵函式的偽程式碼

## 延伸思考
思考：如果這個評分邏輯用 AI（呼叫 Claude API）而不是規則，會有什麼優缺點？成本和延遲分別是多少？

## 完成後
將評分 schema 設計 + 整合方案存入 `answer/ex02-answer.md`
