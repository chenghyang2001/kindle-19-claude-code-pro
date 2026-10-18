# NOTES — 第 11 章練習（SaaS 登陸頁）

> 快速 demo 模式：主 Claude 直接寫檔，未走 writer / QA / reviewer 流程。

## 做了什麼

1. **練習 01**：設計完整登陸頁元件樹（葉節點 / 組合 / 共用元件）與 Server vs Client 決策表 → `answer/ex01-answer.md`
2. **練習 02**：用 `npx create-next-app@latest landing --yes` 建 Next.js 專案，實作：
   - `landing/components/Hero.tsx`：漸層背景、h1 + 副標、「免費試用」「查看 Demo」兩顆 CTA、hover 動畫、手機單欄 / 桌面雙欄
   - `landing/components/Pricing.tsx`：Free / Pro / Enterprise 三方案，Pro 有「最受歡迎」標籤與加粗邊框，手機垂直堆疊，Enterprise「聯絡銷售」連到 mailto
   - `landing/lib/pricing.ts`：方案資料與型別，跟元件分開（為延伸思考的 API 動態載入預留）
   - `app/layout.tsx` 改 `lang="zh-TW"` 與標題
   - 程式碼、驗收對照與延伸思考 → `answer/ex02-answer.md`

## 驗證結果

| 項目 | 指令 | 結果 |
| --- | --- | --- |
| 正式建置 | `npm run build`（timeout 600s） | ✅ 編譯、TypeScript 都通過，`/` 為靜態頁 |
| Lint | `npx eslint .` | ✅ 無錯誤、無警告 |
| 啟動服務 | `npx next start -p 3125` + `curl` | ✅ HTTP 200 |
| 內容檢查 | grep 首頁 HTML | ✅ 主標題、兩顆 CTA、「最受歡迎」、`$29`、「聯絡銷售」、`mailto:`、`aria-labelledby`、`lang="zh-TW"` 都在 |
| 三寬度目視 | headless 截圖 375 / 768 / 1280 | ✅ 見 `answer/screenshots/`，手機堆疊、桌面雙欄正確，無水平溢出 |
| 關閉服務 | 依埠號找 PID 後 `taskkill` | ✅ 3124、3125 都已關閉 |

## 和題目要求的差異

- **題目要求「用 Claude Code 實作」**：照做，但快速模式下沒跑三 agent 品質流程。
- **只做 Hero 與 Pricing**：練習 01 的元件樹含 Navbar、Features、FAQ、Footer 等，但練習 02 與本章補充只要求這兩個元件，其他沒實作。
- **元件命名**：題目寫「HeroSection / PricingSection」，實作檔名用 `Hero.tsx` / `Pricing.tsx`（照本章補充的說法）；`CTAButton`、`SectionHeading` 等共用元件在 ex01 有規劃，實作時沒抽出（兩個元件內直接寫）。
- **Enterprise mailto**：用範例信箱 `sales@example.com`，真實上線要換成公司信箱。
- **CTA 連結**：「免費試用」「查看 Demo」連到 `#signup` / `#demo` 錨點，頁面上沒有對應區塊（示意用）。
- **延伸思考（API 動態幣別）**：只寫設計說明，未實作（需要真實的定價 API）。
- **沒部署 Vercel、沒 push、沒建 GitHub repo**（依指示）。

## 過程中遇到的問題

- **Chrome headless 截 375px 失真**：Windows 版 Chrome `--headless=new` 最小視窗寬度是 500px，375 的截圖實際是 500 寬再裁切。改用 Playwright 內附的 `chrome-headless-shell`（實測 `innerWidth=375`）重截。
- **`timeout` 沒殺掉 next 伺服器**：`timeout 120 npx next start` 只會結束 npx，底下的 node 子程序還在聽埠。最後依埠號查 PID 用 `taskkill /T` 關閉。下次應直接用 `node node_modules/next/dist/bin/next start` 或記下 PID。
- **create-next-app 產生 `AGENTS.md`**：Next.js 16 新增的檔案，提醒 AI 先讀 `node_modules/next/dist/docs/`。本次只用到基本的 App Router 與 Tailwind，沒碰到新版 API 變動。
- `npm install` 回報 5 個 high 漏洞（來自 eslint 相關套件），demo 專案未處理。

## 已知未處理的風險（快速模式）

- 無單元測試 / E2E 測試，只有 build、lint、curl 與截圖冒煙驗證
- 未做深色模式配色（Pricing 區塊固定淺色背景，深色系統下仍是淺色）
- 未做色彩對比度量測（白字在粉紅漸層末端的對比可能偏低）
