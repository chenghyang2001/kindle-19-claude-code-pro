# H-07　API 版本控制

> **類別**：H. API 串接

---

```
設計 API 版本控制策略：
目前版本：v1（已有外部使用者）
需要的破壞性變更：[描述]
評估方案：
1. URL 版本（/api/v2/...）
2. Header 版本（Accept: application/vnd.api+json;version=2）
3. 查詢參數（?version=2）
建議過渡期策略（v1 維持多久？如何通知使用者？）
```
