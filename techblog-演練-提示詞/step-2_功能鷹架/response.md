# Step 2 Claude 的回應

> B-01 鷹架提示詞讓 Claude 先列清單、等確認，不會直接亂寫一堆你不要的檔案

---

## 【將會建立/修改的檔案清單】

```
新建檔案
├── db/schema/bookmarks.ts          ← Drizzle schema（bookmarks 資料表）
├── db/migrations/0005_bookmarks.sql ← 資料庫遷移腳本
├── lib/bookmarks.ts                ← 查詢函式（getBookmarks, toggleBookmark）
├── app/api/bookmarks/route.ts      ← POST + GET 端點
├── app/api/bookmarks/[id]/route.ts ← DELETE 端點
├── components/BookmarkButton.tsx   ← 收藏按鈕元件（含樂觀更新）
└── __tests__/api/bookmarks.test.ts ← Vitest 測試

修改檔案
├── db/schema/index.ts              ← 匯出新的 bookmarks schema
└── app/api/articles/[id]/route.ts  ← 加入 isBookmarked 欄位
```

**執行順序**（依賴關係）：
1. `db/schema/bookmarks.ts` → 2. migration → 3. `lib/bookmarks.ts` → 4. API routes → 5. 元件 → 6. 測試

---

確認檔案清單後，我將逐一產出程式碼。請回覆「確認，開始」。

---

> 等你確認「確認，開始」後，Claude 才會逐檔輸出，不會一次塞給你 300 行看不完的程式碼。
> 這是 B-01 的核心價值：**先對齊架構，再動手實作**。
