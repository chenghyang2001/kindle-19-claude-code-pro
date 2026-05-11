# Step 3 Claude 的回應

> G-01 讓 Claude 一次給你 Schema + 索引 + 查詢範例，不用你來回問

---

## 資料表設計

### bookmarks 資料表

```typescript
// db/schema/bookmarks.ts
import { pgTable, serial, integer, timestamp, unique } from 'drizzle-orm/pg-core'
import { users } from './users'
import { articles } from './articles'

export const bookmarks = pgTable(
  'bookmarks',
  {
    id:         serial('id').primaryKey(),
    userId:     integer('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
    articleId:  integer('article_id').notNull().references(() => articles.id, { onDelete: 'cascade' }),
    createdAt:  timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => ({
    // 複合唯一：同一用戶不能重複收藏同一篇文章
    uniqueUserArticle: unique().on(t.userId, t.articleId),
  })
)

export type Bookmark = typeof bookmarks.$inferSelect
export type NewBookmark = typeof bookmarks.$inferInsert
```

---

## 索引策略

```sql
-- 0005_bookmarks.sql

CREATE TABLE bookmarks (
  id          SERIAL PRIMARY KEY,
  user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  article_id  INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (user_id, article_id)   -- 防重複收藏
);

-- 索引 1：查詢某用戶的所有收藏（查詢模式 2）
CREATE INDEX idx_bookmarks_user_id ON bookmarks(user_id, created_at DESC);

-- 索引 2：查詢某篇文章的收藏數（查詢模式 3）
CREATE INDEX idx_bookmarks_article_id ON bookmarks(article_id);

-- 注意：(user_id, article_id) 已被 UNIQUE 約束建立複合索引，
-- 可直接用於 isBookmarked 查詢（查詢模式 1），不需再建索引。
```

---

## 三種查詢模式的 Drizzle 寫法

```typescript
// lib/bookmarks.ts
import { db } from '@/db'
import { bookmarks } from '@/db/schema'
import { eq, and, desc, count } from 'drizzle-orm'

// 查詢模式 1：isBookmarked 檢查（< 1ms，走複合唯一索引）
export async function isBookmarked(userId: number, articleId: number) {
  const result = await db
    .select({ id: bookmarks.id })
    .from(bookmarks)
    .where(and(eq(bookmarks.userId, userId), eq(bookmarks.articleId, articleId)))
    .limit(1)
  return result.length > 0
}

// 查詢模式 2：用戶收藏列表（cursor-based 分頁）
export async function getUserBookmarks(userId: number, limit = 20, cursor?: number) {
  return db.query.bookmarks.findMany({
    where: cursor
      ? and(eq(bookmarks.userId, userId), lt(bookmarks.id, cursor))
      : eq(bookmarks.userId, userId),
    orderBy: desc(bookmarks.createdAt),
    limit,
    with: { article: { columns: { id: true, title: true, slug: true } } },
  })
}

// 查詢模式 3：文章被收藏次數
export async function getBookmarkCount(articleId: number) {
  const [result] = await db
    .select({ count: count() })
    .from(bookmarks)
    .where(eq(bookmarks.articleId, articleId))
  return result.count
}

// 切換收藏（toggle）
export async function toggleBookmark(userId: number, articleId: number) {
  const already = await isBookmarked(userId, articleId)
  if (already) {
    await db.delete(bookmarks)
      .where(and(eq(bookmarks.userId, userId), eq(bookmarks.articleId, articleId)))
    return false   // 已取消收藏
  } else {
    await db.insert(bookmarks).values({ userId, articleId })
    return true    // 已收藏
  }
}
```

---

**設計決策說明：**
- `UNIQUE(user_id, article_id)` 由資料庫層保證冪等，不需要應用層加鎖
- 使用 `cursor-based` 分頁而非 `OFFSET`，避免大資料集時跳頁效能退化
- `ON DELETE CASCADE` 確保用戶或文章刪除後，收藏記錄自動清除

---
> G-01 的價值：**Schema 設計先行**，資料庫結構確認後才實作 API，避免邊寫邊改 Schema 的惡夢。
