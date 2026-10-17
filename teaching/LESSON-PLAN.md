# K19 快速演練課表

依據：本 repo 的 `demo/`（2026-06-16 依書建好的 15 課＋3 附錄練習題，每課有 exercise-01 基礎／02 進階／03 綜合）。
快速模式只做 **exercise-01 基礎＋exercise-02 進階**，綜合挑戰略過。附錄 A／B／C 排成第 16／17／18 章。

每段提示詞前面都要加：「全自動執行：不要問我任何問題、不要用選擇題，所有選擇一律採用你的推薦，直接做完並回報」。

## 每章通用流程（教練執行）

1. 開練習視窗前，教練把 drill.json 的 `demo_dir` 底下 `exercise-01-基礎.md`、`exercise-02-進階.md` 複製到練習資料夾（**不要**複製 `answer/`、`starter/`、`STEP_LOG.md`，避免直接抄舊答案）。
2. 對練習視窗送：

   > 照 exercise-01-基礎.md 和 exercise-02-進階.md 依序完成。能動手的部分一律真的建檔並實際執行驗證（跑程式、跑測試、印出結果），不要只寫文字說明；需要外部帳號／token／付費服務的部分只寫範本並註明。解答存到 answer/ex01-answer.md、answer/ex02-answer.md。最後寫 NOTES.md：做了什麼、驗證結果、和題目要求的差異。完成後 git add＋commit。

3. 讀 NOTES.md，用 3–5 行回報，更新 HANDOFF 進度表。

## 共通限制（每章都適用）

- **絕不執行** `/logout`、`/login`、`/upgrade`、`/install-github-app`、`/statusline`、`/doctor`，也不要修改全域 `~/.claude/` 底下任何檔案。題目寫到全域設定的地方，一律改成專案層（`./.claude/`、`./CLAUDE.md`、`.mcp.json`）。
- `claude mcp add`、`claude plugin install` 一律 `--scope project`（或 `local`）。
- 不建立 GitHub repo、不 push、不部署到 Vercel 等雲端。
- 需要第三方 token 的只寫設定範本（值用 `${ENV_VAR}` 佔位）。
- 練習中要用 `claude -p` 時先清 `CLAUDE*` 環境變數（避免巢狀限制）。

## 各章補充

| 章 | 主題 | 補充 |
| --- | --- | --- |
| 01 | 從聊天機器人到開發夥伴 | Chat 那一側不實際開 claude.ai，依常識描述；Claude Code 那側真的建 hello.py、calculator 並跑測試。「中途干預」用文字描述即可 |
| 02 | 提示詞技巧 | 改寫前後的提示詞各用 `claude -p` 實跑一次比較輸出 |
| 03 | 專業開發環境（isolated） | CLAUDE.md＋PostToolUse／SessionStart hook 都寫在專案 `.claude/settings.json`，用 `claude -p` 觸發一次驗證 |
| 04 | 生產級程式碼 | pymysql 改用 sqlite3 也可，重點是參數化／環境變數／finally／logging，寫 pytest 驗證 |
| 05 | 快速除錯 | 自己做出會噴 stack trace 的小程式，再修復並驗證 |
| 06 | 無痛測試 | pytest 實跑，貼通過數 |
| 07 | 無懼重構 | 先加測試網再重構，前後測試都要綠 |
| 08 | Agentic 工作流程 | 合約用 JSON Schema 寫成檔，並用 python 驗一筆樣本資料 |
| 09 | MCP 白話文 | 能力地圖用 `claude mcp list` 的結果；MCP vs API 比較用 `gh api repos/chenghyang2001/kindle-19-claude-code-pro/issues` 唯讀查詢；不新增 user scope MCP |
| 10 | CI/CD | 寫 `.github/workflows/ci.yml`（含 pip 快取）＋多環境設定，`yaml.safe_load` 驗證；不 push |
| 11 | SaaS 登陸頁 | `npx create-next-app@latest --yes` 建本機專案，實作 Hero＋Pricing，`npm run build` 通過；不部署 |
| 12 | 自動化系統 | 先自建一支小型示範 pipeline（讀 CSV→處理→輸出）當現有系統，再做分析與評分擴充 |
| 13 | 客戶端 Web 應用 | Drizzle schema 改接本機 SQLite（better-sqlite3 或 libsql），實作最複雜端點＋測試 |
| 14 | 團隊中使用 | agents 放專案 `.claude/agents/`；模組化 CLAUDE.md 用 `@` 匯入 |
| 15 | 安全性 | 有漏洞的範例程式＋修復版，跑 bandit（裝在專案 .venv）比對前後 |
| 16 | 附錄 A 提示詞庫 | 整理成 `prompts/` 目錄，每個模板一檔 |
| 17 | 附錄 B 團隊 CLAUDE.md | 參考 `索引資源-中文/appendix-b-team-claude-md.md`（教練一併複製） |
| 18 | 附錄 C 資安清單 | 參考 `索引資源-中文/appendix-c-security-checklist.md`（教練一併複製），對第 15 章的範例程式做一次完整審查 |
