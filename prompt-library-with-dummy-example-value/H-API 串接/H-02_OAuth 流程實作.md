# H-02　OAuth 流程實作

> **類別**：H. API 串接

---

```
實作 Google OAuth 登入：
流程：Authorization Code Flow
要求：
- state 參數防 CSRF
- PKCE（如果是 SPA）
- Token 刷新邏輯（Refresh Token）
- 儲存策略（HttpOnly Cookie，不存 localStorage）
- 連結既有帳號的邏輯（email 匹配）
```
