# API 設計規範（被 CLAUDE.md 匯入）

驗證暗號：API-4417

- RESTful 路徑用複數名詞：`/api/orders`、`/api/reports/orders`
- 回應格式統一：成功 `{"data": ...}`，失敗 `{"error": {"code": "...", "message": "..."}}`
- 狀態碼：200 成功、201 建立、400 參數錯誤、401 未認證、404 不存在、500 內部錯誤（不洩漏堆疊）
- 日期參數一律 ISO 8601（`YYYY-MM-DD`），區間為 `[from, to]` 含頭含尾
- 列表 API 必須分頁：`?page=1&page_size=20`，page_size 上限 100
- 所有輸入參數先驗證再進商業邏輯
