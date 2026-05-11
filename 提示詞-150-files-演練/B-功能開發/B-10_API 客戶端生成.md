# B-10　API 客戶端生成

> **類別**：B. 功能開發

---

```
為 OpenAI API 建立 API 客戶端封裝：
基礎 URL：https://api.stripe.com/v1
認證方式：Bearer Token（Authorization: Bearer sk_test_xxx）
要包含的端點：GET /customers/{id}（查詢客戶）、POST /payment_intents（建立付款意圖）、POST /refunds（退款）
要求：
- 統一的錯誤處理
- 自動重試（429 Too Many Requests）
- 請求/回應日誌（開發模式）
- TypeScript 型別定義
```
