# Session 5 Summary — 2026-05-11

## 主題
Freelancer Dashboard 演練 — 環境設定、Schema Push、Seed、Dev Server 啟動

---

## 完成事項

- **建立 `.env.local`**：填入使用者提供的 Neon DATABASE_URL（`ep-proud-queen-aog2c9l0-pooler.c-2.ap-southeast-1.aws.neon.tech`）與生成的 AUTH_SECRET (`f3k9mX2pQ7rLvN8wBjYsUhCeAoDtZgIx`)，AUTH_URL=http://localhost:3000
- **修正 `drizzle.config.ts`**：新增 `import * as dotenv from 'dotenv'; dotenv.config({ path: '.env.local' })` — `drizzle-kit` 不自動讀 `.env.local`，需手動載入
- **安裝 `dotenv` devDependency**：`npm install dotenv --save-dev`，供 drizzle.config.ts 與 seed.ts 使用
- **修正 `lib/db/seed.ts`**：原本 `import 'dotenv/config'` 只讀 `.env`，改為 `import * as dotenv from 'dotenv'; dotenv.config({ path: '.env.local' })` 才能讀 `.env.local`
- **`npm run db:push` 成功**：Drizzle schema（users / projects / tasks / project_members 四張表）推送至 Neon PostgreSQL，顯示 `✓ Changes applied`
- **`npm run db:seed` 成功**：建立 demo 資料：admin（ad084d30）/ team / client 三位使用者、1 個專案（82015212）、6 個任務跨四種 status、3 筆 project_members 關聯
- **`npm run dev` 啟動**：Next.js 15.5.18（Turbopack）在 `http://localhost:3001` 啟動（port 3000 被 PID 20868 佔用，自動降至 3001），Ready in 2.3s

---

## 關鍵技術筆記

### dotenv 與 Next.js 的環境載入差異
- **Next.js dev server**：自動注入 `.env.local`，Server Components / API Routes 直接讀 `process.env`
- **`npx tsx`（drizzle-kit / seed）**：不自動注入任何 `.env*`，必須在入口檔案手動 `dotenv.config({ path: '.env.local' })`
- **`import 'dotenv/config'`**：只讀 `.env`（預設路徑），不讀 `.env.local`
- 正確寫法：`import * as dotenv from 'dotenv'; dotenv.config({ path: '.env.local' })`

### `node --env-file` 與 tsx ESM 的衝突
- 嘗試 `node --env-file=.env.local --import tsx/esm lib/db/seed.ts`
- Node.js 24 下觸發 `ERR_REQUIRE_CYCLE_MODULE`（CJS/ESM 循環依賴）
- 解法：放棄 `--env-file`，改在 seed.ts 入口手動 dotenv.config

### 同一台機器多個 package-lock.json 的 turbopack 警告
- `C:\Users\B00332\package-lock.json`（user root）與專案的 lockfile 同時存在
- Turbopack 會猜 workspace root 猜錯，可在 `next.config.ts` 加 `turbopack.root` 解決（本 session 未處理）

---

## 產出檔案

| 檔案 | 狀態 | 說明 |
|------|------|------|
| `freelancer-dashboard-演練/.env.local` | 新建 | Neon DATABASE_URL + AUTH_SECRET + AUTH_URL |
| `freelancer-dashboard-演練/drizzle.config.ts` | 修改 | 新增 dotenv.config({ path: '.env.local' }) |
| `freelancer-dashboard-演練/lib/db/seed.ts` | 修改 | import 'dotenv/config' → dotenv.config({ path: '.env.local' }) |
| `freelancer-dashboard-演練/package.json` | 修改 | 加入 dotenv devDependency（試過後 db:seed script 維持原 npx tsx） |

---

## Demo 帳號

| 角色 | Email | Password |
|------|-------|----------|
| admin | admin@demo.com | password |
| team_member | team@demo.com | password |
| client | client@demo.com | password |

Dev Server: http://localhost:3001（port 3000 已被佔用）

---

## HANDOFF（下次 session 優先處理）

### 立即行動
- [ ] 用 Puppeteer 截圖驗證 app：login → admin dashboard → kanban 拖曳 → client 唯讀視角（http://localhost:3001）
- [ ] 確認 kanban 四欄（Todo / In Progress / Review / Done）有任務卡片顯示
- [ ] Git commit + push freelancer-dashboard-演練 的所有變更（drizzle.config.ts / seed.ts / package.json）

### 進行中（需接續）
- Dev server 已在 port 3001 跑起來（背景程序），但本 session 未完成 Puppeteer 截圖驗證（使用者中斷了 agent 派遣）
- `.env.local` 已建立但沒有 commit（內含 credentials，應加進 .gitignore 確認）

### 注意事項
- `.env.local` 不應 commit，確認 `.gitignore` 有排除（專案建立時應已排除，但需確認）
- 若 port 3001 未佔用，次次 session 重新 `npm run dev` 可能回到 3000
- Neon DB 已有種子資料，若要重跑 seed 需先確認 `onConflictDoNothing` 不會產生重複錯誤（目前 seed 有 onConflictDoNothing 保護）
- Turbopack workspace root 警告（`C:\Users\B00332\package-lock.json`）不影響功能，可在 `next.config.ts` 加 `turbopack: { root: __dirname }` 消除
