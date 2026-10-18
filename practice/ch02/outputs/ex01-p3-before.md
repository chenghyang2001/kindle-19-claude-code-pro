<!-- prompt: ex01/p3-before | ok | 47.3s -->

## 需要先確認的事

「寫個 API」的範圍太廣，我先問清楚再動手，免得做錯方向。請回答以下幾題，不確定的可以跳過，我會用括號裡的預設值：

**1. 這個 API 要做什麼？**（這題一定要回答）
例如：待辦事項 CRUD、查 PM2.5 場域資料、接收 webhook、轉發 Telegram 通知、包一層 Claude API……

**2. 用什麼技術？**
- A. Next.js App Router API Routes（TypeScript，部署到 Vercel）（預設）
- B. Python FastAPI
- C. Express.js
- D. 其他

**3. 資料從哪裡來、存到哪裡？**
- 不需要資料庫，例如計算或轉發（預設）
- Neon PostgreSQL
- AWS RDS MySQL `zap_api`：**只能 SELECT**，API 不會做任何寫入
- Google Sheets 或其他外部 API

**4. 需要登入驗證嗎？**
不需要（預設）、API Key header，或 JWT / NextAuth

**5. 這是正式專案還是學習演練？**
- **學習／演練**：用快速 demo 模式，做出最小可執行版本，只跑一次冒煙測試。
- **正式專案**：走三個 sub-agent 的流程（writer → QA → reviewer），再看情況寫規格書、建 GitHub repo 並 push。

**6. 專案放哪裡？**
目前的工作目錄是暫存資料夾，也不是 git repo。預設改放在 `~/workspace/<名稱>/`。

如果你只想快速看個範例，回「**待辦清單 CRUD、FastAPI、快速模式**」這類一句話就行，我會直接開始做。
