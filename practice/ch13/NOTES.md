# NOTES — K19 第 13 章練習（Freelancer Dashboard）

> 快速 demo 模式：主 Claude 直接寫檔，未經 code-writer / code-qa / code-reviewer 三 agent 流程。

## 做了什麼

| 項目 | 產出 |
| --- | --- |
| ex01 Schema 設計 | `src/db/schema.pg.ts`（PostgreSQL 版，題目原規格）、`src/db/schema.ts`（SQLite 版，實際使用）、`drizzle/0000_init.sql`（migration） |
| ex02 CRUD API | 5 個端點全實作：`src/app/api/clients/route.ts`、`src/app/api/clients/[id]/route.ts` |
| 認證 | `src/lib/auth.ts`：Bearer JWT（HS256，jose） |
| 驗證／錯誤處理 | `src/lib/validation.ts`（Zod 4）、`src/lib/http.ts`（統一錯誤格式 + 400/401/404/409/415/500） |
| 延伸思考 | `clients.version` 樂觀鎖，PUT 版本不符回 409，有測試 |
| 測試 | `tests/clients.post.test.ts`（16 個）、`tests/clients.id.test.ts`（8 個） |
| 工具 | `scripts/make-token.mjs`：產生本機測試用 JWT |
| 解答 | `answer/ex01-answer.md`、`answer/ex02-answer.md` |

技術堆疊：Next.js 15.5 App Router、Drizzle ORM 0.45 + better-sqlite3、Zod 4、jose 6、vitest 5、TypeScript 5.9。

## 驗證結果（全部實際執行過）

| 驗證 | 指令 | 結果 |
| --- | --- | --- |
| 單元／整合測試 | `npx vitest run` | ✅ 24 / 24 通過 |
| 型別檢查（含 PG 版 schema） | `npx tsc --noEmit` | ✅ 通過 |
| 正式建置 | `npm run build` | ✅ 通過，`/api/clients`、`/api/clients/[id]` 為動態路由 |
| SQLite migration | `npx drizzle-kit generate` | ✅ 4 張表、FK、CHECK、索引 |
| PG SQL 產生 | `npx drizzle-kit export --dialect postgresql ...` | ✅ 成功產出 SQL（未連 DB 執行） |
| HTTP 冒煙測試 | `next start -p 3199` + curl | ✅ 401 / 400 / 201（含 Location）/ 409 / 200，測完已關閉伺服器並刪除測試 DB |

### 過程中修掉的問題

1. **刪除仍有專案的客戶回 500，而不是 409**：SQLite 的 `ON DELETE RESTRICT` 擋下刪除時，錯誤碼是 `SQLITE_CONSTRAINT_TRIGGER`，不是 `SQLITE_CONSTRAINT_FOREIGNKEY`。`isForeignKeyViolation` 改成另外比對 `FOREIGN KEY constraint failed` 訊息後修好。
2. **測試密鑰寫死在程式碼裡**被 hook 擋下：`tests/setup.ts` 改成每次執行用 `crypto.randomBytes` 隨機產生。
3. npm 預設裝到 TypeScript 7，改裝 5.x 以確保和 Next.js 15 的型別檢查相容。
4. 冒煙測試第一次關伺服器時，Git Bash 把 `taskkill //PID` 參數轉壞了，沒關成功；改用 `MSYS_NO_PATHCONV=1 taskkill /PID ... /T /F` 後確認 3199 埠已釋放。

## 怎麼跑

```bash
npm install
npx vitest run                     # 測試（記憶體 DB，免設定）
npm run build

# 本機起服務
export AUTH_SECRET=$(node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")
export DATABASE_FILE=data/dev.db   # 第一次連線自動 migrate
npm start
TOKEN=$(node scripts/make-token.mjs my-user)
curl -X POST localhost:3000/api/clients -H "authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' -d '{"name":"王小明"}'
```

環境變數範本（`.env.example` 被本機權限設定擋住，沒能建檔，內容放這裡）：

```
AUTH_SECRET=<至少 32 字元的隨機字串>
DATABASE_FILE=data/dev.db
```

## 和題目要求的差異

| 題目 | 實際做法 | 原因 |
| --- | --- | --- |
| Neon PostgreSQL | 本機 SQLite（better-sqlite3） | 本章補充指定，不需雲端帳號。PG 版 schema 另存 `schema.pg.ts`，只做型別檢查和 SQL 產生，**沒連 Neon 實跑**（需要帳號，只留範本） |
| `decimal` 金額 | SQLite 版改用 integer「分」 | SQLite 沒有真正的 decimal；PG 版仍是 `decimal(12,2)` |
| `uuid` / `timestamptz` | SQLite 版用 text + `randomUUID()`、integer 毫秒 | SQLite 沒有這兩種型別 |
| 認證中介軟體（NextAuth） | 自簽 HS256 JWT（jose） | NextAuth 需要登入提供者設定；`authenticate()` 介面不變，之後可換成 NextAuth 的 `auth()` |
| 只要求實作 POST | 5 個端點都實作 | 樂觀鎖的延伸思考需要 PUT 才能實測 |
| 3 個整合測試 | 24 個 | 多涵蓋過期 token、偽造 token、415、409、500 不外洩、多租戶隔離、樂觀鎖 |
| 測試走 HTTP | 直接呼叫 Route Handler 函式 + 另做一次真實 HTTP 冒煙測試 | 測試不必起伺服器，速度快又穩定；HTTP 層由冒煙測試補上 |

## 已知沒處理的風險（快速模式）

- 沒有 rate limit、沒有 request body 大小限制。
- JWT 沒有撤銷機制（登出後 token 在到期前仍有效）。
- 沒有 Next.js `middleware.ts`；認證在每個 handler 內用 `requireUser()` 處理。
- 未經 code review / security audit。
- 未部署、未 push（依題目限制）。
