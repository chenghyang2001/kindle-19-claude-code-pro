# Step 4 使用的提示詞
> 來源：`D-測試策略/D-05_API 端點測試.md`

---

```
為以下 API 端點撰寫測試：

端點：POST /api/bookmarks（收藏文章）

要測試的案例：
- 正常請求：登入用戶收藏一篇存在的文章 → 回傳 { bookmarked: true, articleId }
- 重複收藏：同一篇文章收藏兩次 → 第二次回傳 { bookmarked: true }（冪等，不報錯）
- 認證失敗（401）：未登入用戶呼叫 → 回傳 { error: 'Unauthorized' }
- 文章不存在（404）：收藏一個不存在的 articleId → 回傳 { error: 'Article not found' }
- 輸入驗證失敗（400）：沒有帶 articleId → 回傳 { error: 'articleId is required' }
- 伺服器錯誤（500）：模擬資料庫斷線 → 回傳 { error: 'Internal server error' }

使用 Vitest，mock 掉 db 和 withAuth，不連真實資料庫。
```
