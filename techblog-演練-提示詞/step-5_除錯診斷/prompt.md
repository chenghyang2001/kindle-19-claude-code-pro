# Step 5 使用的提示詞
> 來源：`C-除錯與診斷/C-01_標準除錯協議.md`

---

```
除錯這個錯誤：

錯誤訊息：
  Error: duplicate key value violates unique constraint "bookmarks_user_id_article_id_unique"
  at Object.query (/app/node_modules/drizzle-orm/pg-core/session.js:42:11)
  at POST (app/api/bookmarks/route.ts:28:5)

重現步驟：
  1. 用戶 A 在手機和電腦同時快速連點「收藏」按鈕
  2. 兩個請求幾乎同時打到伺服器
  3. 第二個請求拋出 UniqueConstraint 錯誤，回傳 500

環境：Node.js 20.11.0, Neon PostgreSQL, Vercel Edge Runtime

請按以下步驟回應：
步驟 1：根本原因分析
步驟 2：修復方案（含程式碼）
步驟 3：這個錯誤本來應該被哪個測試抓到？
步驟 4：如何防止類似的 race condition 再次發生？
```
