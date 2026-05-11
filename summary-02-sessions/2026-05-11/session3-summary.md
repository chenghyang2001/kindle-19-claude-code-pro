---
date: 2026-05-11
session: 3
---

# Session 3 Summary

**日期**：2026-05-11

---

## 完成事項

### 1. 建立 techblog-演練-網站 全端示範專案
- 在 `C:\Users\B00332\workspace\techblog-演練-網站` 建立完整 Next.js 16 App Router 專案
- 使用書籍附錄提示詞範本實際產出 7 個 TypeScript 檔案
- 所有檔案經過 writer → code-qa → code-reviewer 三 agent 鐵律流程（22/22 QA test cases PASS）

### 2. 實作完整書籤功能（Bookmark Feature）
- `db/schema/bookmarks.ts`：Drizzle pgTable 定義（users + articles + bookmarks 三張表，composite unique constraint）
- `db/index.ts`：解決 Next.js build 相容問題，最終用 lazy init + Proxy pattern 避免模組載入時拋錯
- `lib/bookmarks.ts`：toggleBookmark（ON CONFLICT DO NOTHING 原子操作）+ getUserBookmarks（cursor-based pagination）
- `app/api/bookmarks/route.ts`：REST API（GET/POST/OPTIONS），OPTIONS handler 解決 CORS preflight
- `components/BookmarkButton.tsx`：Optimistic Update 模式，`aria-label`/`aria-pressed` 無障礙設計
- `app/page.tsx`：Server Component，3 篇模擬文章 + 響應式 grid

### 3. 修正 code-reviewer 發現的 MUST_FIX 問題（共 4 項）
- 補 OPTIONS CORS handler（原本缺失）
- 修 null JSON body → 500 bug（改為 400 Bad Request）
- cursor 分頁 ORDER BY 不一致（`orderBy createdAt` 但 `lt(id)`）→ 改為 `desc(bookmarks.id)`
- cursor 空值檢查從 `if (cursor)` 改為 `if (cursor !== undefined)`（`0` 會誤判）

### 4. 解決 Next.js Build 相容性問題（兩輪修正）
- 第一輪：模組頂層 `throw Error("Missing DATABASE_URL")` → Next.js build 時即拋錯
- 第二輪：`neon(process.env.DATABASE_URL ?? "")` → neon() 在建構時驗證 URL 也拋錯
- 最終方案：`getDb()` 工廠函式 + `new Proxy(...)` export，查詢時才初始化

### 5. 合併 techblog-demo 進 claude-code-pro-resources
- 刪除 `techblog-demo/.git`（Option A：吸收入外層 repo）
- `git add -A` 追蹤所有新檔案後 commit push

### 6. 資料夾命名整理（8 個資料夾改名）
| 原名 | 新名 |
|------|------|
| `中文` | `索引資源-中文` |
| `english` | `索引資源-英文` |
| `demo-1` | `techblog-演練-提示詞` |
| `prompt-library` | `提示詞-150-files-範本` |
| `prompt-library-with-dummy-example-value` | `提示詞-150-files-演練` |
| `techblog-demo` | `techblog-演練-網站` |
| `pptx` | `chapter-pptx` |
| `techblog-提示詞演練` | `techblog-演練-提示詞` |

### 7. 附錄 MD 整理進 索引資源-英文
- 移入 appendix-a/b/c 英文 MD 三個
- 中文版（1823 行）加 `-中文` 後綴（避免與英文版同名衝突）保留兩份

---

## 關鍵技術筆記

### Lazy Init + Proxy Pattern（Next.js + neon-http）
neon-http transport 在呼叫 `neon(url)` 時就驗證 URL 格式，不是等到查詢時。模組層級任何 throw 都會讓 Next.js build 失敗。解法：
```typescript
export const db = new Proxy({} as DrizzleDb, {
  get(_, prop) { return Reflect.get(getDb(), prop); }
});
```

### ON CONFLICT DO NOTHING（書籤 toggle 原子操作）
```typescript
const [inserted] = await db.insert(bookmarks)
  .values({ userId, articleId })
  .onConflictDoNothing()
  .returning();
// inserted = undefined → 已有書籤，執行刪除
```
避免 check-then-act race condition。

### Cursor Pagination 規則
`ORDER BY` 欄位必須和 `WHERE ... < cursor` 的欄位一致。用 `createdAt` 排序但用 `id` 做 cursor 會產生頁面跳行。

### git mv 前提條件
`git mv` 只能操作已追蹤的檔案。新建但尚未 `git add` 的目錄用 `git mv` 會報 `source directory is empty`。需先 `git add <dir>/` 再 mv。

---

## 產出檔案表格

| 檔案路徑 | 行數 | 說明 |
|---------|------|------|
| `techblog-演練-網站/db/schema/bookmarks.ts` | 56 | Drizzle schema |
| `techblog-演練-網站/db/index.ts` | 31 | lazy init + Proxy DB export |
| `techblog-演練-網站/lib/bookmarks.ts` | 108 | toggleBookmark + getUserBookmarks |
| `techblog-演練-網站/app/api/bookmarks/route.ts` | 89 | REST API + OPTIONS |
| `techblog-演練-網站/components/BookmarkButton.tsx` | 115 | Optimistic Update 元件 |
| `techblog-演練-網站/app/page.tsx` | 118 | Server Component 首頁 |
| `techblog-演練-網站/drizzle.config.ts` | 19 | Drizzle 設定 |
| `索引資源-英文/appendix-a-prompt-library-中文.md` | 1823 | 附錄 A 中文完整版 |
| `.gitignore`（claude-code-pro-resources） | 11 | 排除 Next.js build artifacts |
| `summary-02-sessions/2026-05-11/session3-summary.md` | — | 本文件 |

---

## HANDOFF（下次 session 優先處理）

### 立即行動
- [ ] 設定 `techblog-演練-網站/.env.local`（填入 Neon PostgreSQL `DATABASE_URL`）並跑 `npm run dev` 實際連資料庫測試書籤功能
- [ ] 確認 `chapter-pptx/` 目錄改名後 GitHub Pages（`gen_viewer.py` 掃描路徑）仍正確指向 PNG 圖片
- [ ] 補齊 `索引資源-英文/` 的 appendix-b/c 中文版（目前只移入 appendix-a 中文版）

### 進行中（需接續）
- `techblog-演練-網站` 已建立並通過 `npm run build`，但尚未連真實 Neon DB（DATABASE_URL 未設）
- 書籤功能的前端 optimistic update 已完成，後端 API 已完成，資料庫 schema 已定義，等待真實連線驗證

### 注意事項
- `pptx/` 已改名為 `chapter-pptx/`，若 `gen_viewer.py` 或任何腳本 hardcode `pptx/` 路徑需更新
- `mermaid-viewer` repo 的 tab 8 連結指向 GitHub Pages `chenghyang2001/claude-code-pro-pptx`，改名若影響路徑需同步更新
- Next.js dev server 持有 node.exe 時，`git mv` 操作可能失敗；需先 `taskkill /F /IM node.exe`
