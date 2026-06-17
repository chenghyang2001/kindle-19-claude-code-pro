# Session 16 — VPS 開發環境備份 + Lesson 11 EX02

**日期**：2026-06-18（接續 Session 15）

---

## 完成事項

### 1. 三實作專案 VPS 開發環境備份（主任務）

- **需求釐清**：使用者原以為三專案「跑在這台家用 PC」，實際早已雲端（freelancer/techblog 在 Vercel、email 在 GitHub Actions）。真正目的是「跨電腦開發延續」—— 家裡 PC 關機後，到公司用別台筆電也能存取/執行/修改三專案
- **方案決定**：使用者選「備份金庫 + 遠端開發據點」（非搬 production 離開 Vercel）。VPS 當機密金庫 + 永遠在線的開發據點，Vercel 維持不動
- **VPS（claude@187.127.109.145，srv1548225）環境**：Node v20.20.2、Python 3.12.3、git 2.43、57G 可用
- **執行內容**：
  - 三 repo clone 到 `~/workspace/`（freelancer-dashboard / techblog-demo / email-automation-demo）
  - 機密 env 就位：freelancer + techblog 的 `.env.local` 完整寫入；email `.env` 填已知值（NOTION_DATABASE_ID / TIMEZONE），TELEGRAM token 留空（在 GitHub Secrets 讀不到）
  - 依賴安裝：freelancer npm 660 套件、techblog 71 套件、email Python venv + pip
  - 可執行驗證：freelancer build 8/8 頁、techblog build 5/5 頁、email 7 個 .py 全編譯通過
  - 建 `~/workspace/SETUP-GUIDE.md`（公司筆電兩種存取方式 + 各專案執行指令）

### 2. Lesson 11 EX02 核心元件實作（互動教學）

- 任務 1：Hero Section（Server Component + 共用 CTAButton，漸層背景、響應式雙欄、hover 動畫）
- 任務 2：Pricing Table（plans 陣列 + .map()、Pro 方案 ring-2 + scale-105 + 推薦徽章、手機堆疊、Enterprise mailto）
- 延伸思考：Pricing 改 API 動態載入（多幣別）→ PricingCard 維持 props-driven 純展示元件，一行不用改，只改資料來源層
- 解答存入 `answer/ex02-answer.md`

---

## 關鍵技術筆記

- **三專案 production 不依賴本機 PC**：freelancer/techblog 在 Vercel、email 在 GitHub Actions，家裡 PC 關機照常運作
- **跨機器開發的正解 = GitHub（code）+ 機密備份（VPS）+ bootstrap**，不是搬執行環境
- **VPS 公司筆電存取兩法**：(A) SSH/Cursor Remote 連 VPS 直接開發（推薦）；(B) 本機 clone GitHub + `scp` 從 VPS 抓 .env
- **公司筆電首次 SSH 需加金鑰**：新筆電的 public key 要加到 VPS authorized_keys（待使用者到公司時處理）
- **元件邊界設計價值**：props-driven 展示元件（PricingCard）讓資料源從「寫死」換成「API」時零改動

---

## 產出檔案表格

| 檔案 / 資源 | 狀態 | 說明 |
|------|------|------|
| `demo/[11...]/answer/ex02-answer.md` | 新增 | Lesson 11 EX02 解答（Hero + Pricing）|
| VPS `~/workspace/{3 repos}/` | 新增 | 三專案 clone + env + deps |
| VPS `~/workspace/SETUP-GUIDE.md` | 新增 | 公司筆電使用指南 |
| VPS `email-automation-demo/.env` | 新增 | 已知值填入，機密待補 |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 繼續 Lesson 11 EX03（綜合：完整登陸頁 + 部署）→ 完成後 carry to L12
- [ ] （到公司筆電時）把該筆電 SSH public key 加到 VPS，才能 SSH 連入開發
- [ ] （可選）若要在 VPS 跑完整 email pipeline，從 GitHub Secrets 補 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 到 `.env`

### 進行中（需接續）

- Lesson 11 EX01 + EX02 完成，EX03 待做（最後一題）
- VPS 開發環境備份已完成並驗證，三專案在 VPS 皆可 build/編譯

### 注意事項

- 互動式鐵律：Lesson 練習一題一答
- VPS = claude@187.127.109.145，三專案在 `~/workspace/`，指南在 `~/workspace/SETUP-GUIDE.md`
- freelancer 用 Neon `neondb`、techblog 用 Neon `techblog`（勿混，會撞 users 表）
- 三專案改 code 在各自獨立 repo（本機或 VPS），push 後 freelancer/techblog 自動觸發 Vercel 部署
