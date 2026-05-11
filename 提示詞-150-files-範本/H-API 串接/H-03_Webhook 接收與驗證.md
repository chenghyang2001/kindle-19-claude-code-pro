# H-03　Webhook 接收與驗證

> **類別**：H. API 串接

---

```
實作 [Stripe / GitHub / LINE] Webhook 接收端點：
Webhook 事件：[事件清單]
要求：
- 驗證 Webhook 簽名（防偽造）
- 冪等性處理（重複事件不重複執行）
- 立即回應 200（非同步處理事件）
- 事件記錄（含原始 payload）
- 失敗告警
```
