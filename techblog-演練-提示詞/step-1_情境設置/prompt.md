# Step 1 使用的提示詞
> 來源：`A-核心框架/A-01_五要素提示詞結構.md`
> 操作：把 [xxx] 換成我的專案值後直接貼給 Claude

---

```
角色：擔任資深 TypeScript / Next.js 開發者。

情境：這是一個使用 Next.js 16 App Router + PostgreSQL（Neon）+
Tailwind CSS + Drizzle ORM 的全端部落格平台專案（TechBlog）。
相關檔案為 app/api/bookmarks/route.ts。

任務：實作「文章收藏（Bookmark）」功能，讓登入用戶可以收藏或
取消收藏文章，並在個人頁查看收藏清單。

限制：
- 遵循現有的 withAuth middleware 驗證登入狀態
- 使用 Drizzle ORM，遵循 db/schema.ts 的 schema 定義
- 錯誤回應一律用 NextResponse.json({ error: string }, { status })
- 不引入新的大型依賴

成功標準：
- POST /api/bookmarks → 收藏文章，回傳 { bookmarked: true }
- DELETE /api/bookmarks/[articleId] → 取消收藏，回傳 { bookmarked: false }
- GET /api/bookmarks → 回傳當前用戶的收藏列表（含分頁）
- 所有端點有完整的型別定義與錯誤處理
```
