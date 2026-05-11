# Step 1 Claude 的回應

> Claude 收到 A-01 五要素提示詞後，會先確認理解再動手

---

了解，我將以資深 TypeScript / Next.js 開發者的角色，為 TechBlog
建立「文章收藏（Bookmark）」功能。

**確認理解如下：**

| 項目 | 內容 |
|------|------|
| 技術堆疊 | Next.js 16 App Router + Drizzle ORM + Neon PostgreSQL |
| 目標功能 | 收藏 / 取消收藏 / 查看清單 |
| 認證方式 | withAuth middleware（現有） |
| 限制 | 不改 schema 定義規範、不加大型依賴 |

**計畫建立的端點：**

```
POST   /api/bookmarks           → 收藏文章
DELETE /api/bookmarks/[id]      → 取消收藏
GET    /api/bookmarks           → 取得收藏列表（cursor-based 分頁）
GET    /api/articles/[id]       → 文章詳情（加入 isBookmarked 欄位）
```

**建議執行順序：**
1. 先設計 bookmarks 資料表 Schema
2. 建立 Drizzle migration
3. 實作 API Route
4. 撰寫測試

確認後我開始進入 Step 2（鷹架規劃）。

---
> 這就是 A-01 的價值：Claude 先複述理解，雙方對齊後才動手，避免做了一半才發現方向錯誤。
