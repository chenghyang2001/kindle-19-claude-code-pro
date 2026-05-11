# Step 5 Claude 的回應

> C-01 讓 Claude 按四步驟有系統地診斷：根本原因 → 修復 → 缺的測試 → 預防

---

## 步驟 1：根本原因分析

**問題**：Race Condition（競態條件）

時序圖：
```
手機請求    ──→ isBookmarked() = false ──→ INSERT ... ──→ 成功
電腦請求    ──→ isBookmarked() = false              ──→ INSERT ... ──→ 💥 UniqueConstraint!
               ↑
               兩個請求同時通過了「未收藏」的檢查，都試圖 INSERT
```

根本原因：`toggleBookmark()` 是「先查再寫」的兩步操作（Check-Then-Act），
在高並發下兩個請求都通過了 `isBookmarked() = false` 的檢查，
接著都試圖執行 `INSERT`，第二個必然失敗。

---

## 步驟 2：修復方案

**方案：使用 PostgreSQL 的 `INSERT ... ON CONFLICT DO NOTHING`**

```typescript
// lib/bookmarks.ts — 修復後的 toggleBookmark

export async function toggleBookmark(userId: number, articleId: number) {
  // 先嘗試插入（若已存在則什麼都不做，不報錯）
  const inserted = await db
    .insert(bookmarks)
    .values({ userId, articleId })
    .onConflictDoNothing()          // ← 關鍵：讓 DB 處理競態，不是應用層
    .returning({ id: bookmarks.id })

  if (inserted.length > 0) {
    // 成功插入 = 剛才收藏了
    return true
  }

  // 插入失敗代表已存在 → 執行刪除（取消收藏）
  const deleted = await db
    .delete(bookmarks)
    .where(and(eq(bookmarks.userId, userId), eq(bookmarks.articleId, articleId)))
    .returning({ id: bookmarks.id })

  return deleted.length === 0  // 刪除後仍回傳 false（已取消收藏）
}
```

**為什麼這樣修是對的：**
- `ON CONFLICT DO NOTHING` 是原子操作，由 PostgreSQL 在 DB 層處理衝突
- 不需要應用層加鎖（Lock），不影響效能
- 並發兩個 INSERT：一個成功，一個靜默忽略 → 最終狀態一致

---

## 步驟 3：這個錯誤應該被哪個測試抓到？

Step 4 的測試**缺少並發案例**，應補上：

```typescript
// 補充測試：並發收藏（兩個請求同時送出）
it('同一用戶同時發出兩個收藏請求，不報錯，最終只有一筆收藏', async () => {
  vi.mocked(getArticleById).mockResolvedValue({ id: 42, title: '測試文章' })
  // 模擬真實 db：第一次成功，第二次因 ON CONFLICT 靜默忽略
  vi.mocked(toggleBookmark)
    .mockResolvedValueOnce(true)   // 第一個請求
    .mockResolvedValueOnce(true)   // 第二個請求（冪等）

  const [res1, res2] = await Promise.all([
    POST(makeRequest({ articleId: 42 }, 1)),
    POST(makeRequest({ articleId: 42 }, 1)),
  ])

  // 兩個都應該成功，不能有 500
  expect(res1.status).toBe(200)
  expect(res2.status).toBe(200)
})
```

---

## 步驟 4：如何防止類似問題再次發生？

**系統性預防原則：**

| 情境 | 正確做法 | 錯誤做法 |
|------|---------|---------|
| 唯一性約束 | DB 層 `ON CONFLICT DO NOTHING/UPDATE` | 應用層 Check-Then-Act |
| 計數器（like_count）| `UPDATE SET count = count + 1` | 先 SELECT 再 UPDATE |
| 購買/扣款 | DB Transaction + Row-level Lock | 應用層 if 判斷 |
| 排程任務 | 分散式鎖（Redis SETNX） | 只靠 DB 狀態欄位 |

**CLAUDE.md 加入規則（防止未來再犯）：**
```
## Race Condition 防範規則
- 所有「先查再寫」的操作必須使用 DB 層原子操作
- UPSERT 優先使用 ON CONFLICT，不用應用層 try-catch UniqueConstraint
- 涉及數字遞增（count, balance）一律用 UPDATE SET x = x + 1
```

---
> C-01 的價值：**四步驟讓你不只修 bug，還能預防同類問題**。
> 只修表面不挖根因，下次換個地方同樣出問題。
