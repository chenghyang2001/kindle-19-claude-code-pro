# 練習 03 — 綜合挑戰：設計自訂 MCP Server

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
設計一個「PM2.5 數據查詢 MCP Server」，讓 Claude Code 可以直接查詢感測器數據。

## 要求

1. **定義 2 個 MCP Tools**

   **Tool 1：`get_room_pm25`**
   - 功能：取得指定場域在指定日期的 PM2.5 數據
   - 設計 JSON Schema（inputSchema）：
     - room_id（必填，整數）
     - date（必填，格式 YYYY-MM-DD）
     - aggregation（選填，"hourly" 或 "daily"，預設 "daily"）
   - 回傳格式設計（含 PM2.5 值、時間戳、感測器狀態）

   **Tool 2：`get_anomaly_rooms`**
   - 功能：回傳指定日期有異常值的場域清單
   - 異常定義：PM2.5 = 998（感測器故障）或 PM2.5 > 150（重度污染）
   - 回傳格式設計（含場域 ID、異常類型、異常時間）

2. **設計 MCP Server 架構**
   用偽程式碼描述 MCP server 的基本結構：
   - 如何註冊 tools
   - 如何接收 Claude 的呼叫請求
   - 如何連接到實際資料庫（唯讀 MySQL）
   - 如何回傳結果

3. **設計 CLAUDE.md 章節**
   在 CLAUDE.md 中加入「可用 MCP 工具」說明：
   - 何時應該使用 `get_room_pm25`
   - 何時應該使用 `get_anomaly_rooms`
   - 使用注意事項（只讀、不能修改資料）

## 完成標準
- [ ] 2 個 Tool 的 JSON Schema 設計完整
- [ ] MCP server 架構偽程式碼清楚
- [ ] CLAUDE.md 章節說明清晰

## 完成後
將解答存入 `answer/ex03-answer.md`
