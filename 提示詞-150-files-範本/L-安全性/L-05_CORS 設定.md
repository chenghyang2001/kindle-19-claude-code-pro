# L-05　CORS 設定

> **類別**：L. 安全性

---

```
為 [API 服務] 設定正確的 CORS：
允許的來源：[清單，如「https://myapp.com」]
要求：
- 不使用 origin: * （除了公開 API）
- 明確設定允許的 HTTP 方法
- 認證請求需設 credentials: true
- 預檢請求（OPTIONS）的快取
- 子域名萬用字元的安全性考量
```
