# Session 15 — 三實作專案部署上線 + Email 排程修復

**日期**：2026-06-18

---

## 完成事項

### 1. Lesson 11（實作1：SaaS 登陸頁）— EX01 元件拆解分析

- 完成基礎練習解答，存入 `demo/[11-專案實作1-SaaS登陸頁]/answer/ex01-answer.md`
- 內容：元件樹設計（葉/組合/共用元件分類）+ Server vs Client Component 決策表
- 核心觀念：互動下沉（push client down）、重複即抽取、預設 Server Component
- EX02/EX03 尚未進行（收工後繼續）

### 2. Email 自動化（實作2）收斂 + 修復

- **副本收斂**：發現同份 code 散在 5 處，且 `claude-code-pro-resources` repo 已改名為 `kindle-19-claude-code-pro`（兩本機資料夾是同 repo 的兩個 clone）
- 刪除舊名 clone `~/workspace/claude-code-pro-resources/`，移除 kindle-19 內嵌副本
- 最終單一真相源：GitHub `email-automation-demo` + 本機 `~/workspace/email-automation-demo/`
- **排程故障修復**：根因為 Gmail OAuth refresh token 失效（`invalid_grant`）。使用者重新 OAuth 授權 → 更新 GitHub Secret `GMAIL_TOKEN_JSON` → workflow_dispatch 實測 13 秒成功
- **OAuth 確認**：Google Cloud 專案 `jessica-459902` 發布狀態已是「實際運作中（正式版）」，token 不會 7 天過期
- **排程時間調整**：09:00 → 07:30（cron `0 1 * * 1-5` → `30 23 * * 0-4`，UTC 23:30 隔日），維持週一至週五

### 3. freelancer-dashboard（實作3）部署上線

- 從 `freelancer-dashboard-演練` 抽出獨立 repo `chenghyang2001/freelancer-dashboard`
- 刪除空殼 `freelancer-dashboard`（無 app/ 的骨架）
- 修 build 錯誤：`tasksByProject` 改 const（prefer-const）
- Neon DB：沿用既有 `claude-code-pro` 專案的 `neondb`（已有 3 帳號/1 專案/6 任務種子）
- Vercel 部署：設 `DATABASE_URL` + `AUTH_SECRET`，連結 GitHub 自動部署
- **線上**：<https://freelancer-dashboard-coral.vercel.app> （admin/client/team@demo.com，密碼 password）
- 登入實測：curl 模擬 CSRF + credentials 登入 → 302 進 /dashboard，認證 + DB 全通
- 移除 kindle-19 內嵌副本

### 4. techblog（實作1周邊）部署上線

- 從 `techblog-演練-網站` 抽出獨立 repo `chenghyang2001/techblog-demo`（Next.js 16）
- **建獨立 Neon database `techblog`**（避免與 freelancer 的 `users` 表撞表，同專案不同 DB）
- `drizzle-kit push` 建表（users/articles/bookmarks）+ 灌最小種子（1 user + 3 articles 對應 mockArticles id 1/2/3）
- Vercel 部署：設 `DATABASE_URL` 指向 techblog DB
- **線上**：<https://techblog-demo.vercel.app>
- 書籤 POST 實測：加書籤 true → 再 POST 移除 false，HTTP 200，DB 讀寫全通
- 移除 kindle-19 內嵌副本（保留 `techblog-演練-提示詞` 教材）

---

## 關鍵技術筆記

- **GitHub repo 改名 redirect**：push 到舊名 remote 會回報 "This repository moved"，但仍成功（GitHub 自動轉址）。本機 clone 的 remote URL 不會自動更新
- **git archive 抽子資料夾**：`git archive HEAD | tar -x -C 目標` 只取版控檔，乾淨排除 node_modules/.next
- **Next.js `.gitignore` 的 `.env*` 會連 `.env.local.example` 一起擋**，需 `git add -f` 強制追蹤範本
- **drizzle.config 是否載 dotenv 不一致**：freelancer 有 `dotenv.config({path:'.env.local'})`，techblog 沒有 → 需手動 `DATABASE_URL=... npx drizzle-kit push`
- **Neon 同專案多 database 隔離**：`neondb_owner` 有 CREATEDB 權限，`CREATE DATABASE techblog` 可成功；連線字串只需改結尾 DB 名
- **NextAuth v5 在 Vercel**：只需 `AUTH_SECRET`，URL 自動偵測（trustHost auto on Vercel），不必設 AUTH_URL
- **Vercel CLI 部署**：`vercel link --yes` 自動連結 GitHub repo；`printf '%s' value | vercel env add NAME production` 設加密變數；`vercel --prod --yes` 部署
- **本機殘留空資料夾鎖定**：git rm 後本機殘留的空資料夾可能因 IDE/檔案總管開啟而 "Device or resource busy"，無害

---

## 產出檔案表格

| 檔案 / 資源 | 狀態 | 說明 |
|------|------|------|
| `demo/[11...]/answer/ex01-answer.md` | 新增 | Lesson 11 EX01 解答 |
| GitHub `freelancer-dashboard` | 新增 repo | 實作3 獨立 repo + Vercel |
| GitHub `techblog-demo` | 新增 repo | 實作1 獨立 repo + Vercel |
| Neon database `techblog` | 新增 | techblog 專屬 DB（隔離） |
| `email-automation-demo/.github/workflows/daily-briefing.yml` | 修改 | 排程 09:00→07:30，commit db9a37c |
| `email-automation-demo` GitHub Secret `GMAIL_TOKEN_JSON` | 更新 | 新 OAuth token |
| kindle-19 `.gitignore` | 修改 | 清掉已刪資料夾的條目 |
| kindle-19：移除 3 個嵌入副本 | 刪除 | email-演練/freelancer-演練+空殼/techblog-網站 |

### 三實作專案最終狀態

| 實作 | GitHub repo | 線上網址 | DB |
|------|-------------|---------|-----|
| 實作2 Email | email-automation-demo | GitHub Actions 排程（週一~五 07:30） | — |
| 實作3 freelancer | freelancer-dashboard | freelancer-dashboard-coral.vercel.app | Neon neondb |
| 實作1 techblog | techblog-demo | techblog-demo.vercel.app | Neon techblog |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 繼續 Lesson 11：EX02 核心元件實作（互動式一題一答模式）
- [ ] 接著 Lesson 11 EX03（完整登陸頁 + 部署）→ 完成後 carry to L12
- [ ] （可選）三個部署網站若要自訂 domain 或加 monitoring，再處理

### 進行中（需接續）

- Lesson 11 只完成 EX01（元件拆解分析），EX02/EX03 待做
- MEMORY.md 課程進度表本 session 已更新至 L10 完成 + 三實作部署

### 注意事項

- **互動式鐵律**：Lesson 練習一題一答，出一題→等回答→給回饋→才下一題
- 三個部署都連 Neon 同一專案 `claude-code-pro`：freelancer 用 `neondb`、techblog 用 `techblog` database（勿混用，會撞 users 表）
- email-automation 排程若再失敗，先查 GitHub Secret（token），OAuth 已正式版不會 7 天過期
- Vercel 已登入（chenghyang2001-6766），之後部署不需重新 login
- 三個獨立 repo 改 code 在 `~/workspace/{email-automation-demo,freelancer-dashboard,techblog-demo}/`，push 自動部署
