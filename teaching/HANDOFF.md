# K19 演練交接

## 原機器結果

2026-06-16 起在 `demo/` 依書做過一輪學習課程（15 課＋3 附錄），各課解答在 `demo/[NN-…]/answer/`、過程在 `STEP_LOG.md`。快速模式的差異以「和 demo 原解答／題目要求的差異」記錄。

## 快速模式進度表

| 章 | 完成日 | 實際耗時 | 和原解答／題目要求的差異 |
| --- | --- | --- | --- |
| 01 | 2026-10-18 | 4 分 | Chat 端依常識描述未實測；中途干預用 shell 改檔模擬；calculator 多做 CLI 錯誤處理，9 passed |
| 02 | 2026-10-18 | 11 分 | 改寫前後 8 份提示詞皆 claude -p 實跑並用 pytest 驗產出（13 passed 1 xfailed）；對照組受全域 CLAUDE.md 污染，--bare 需 API key 只留範本；ex02 只實測情境 B |
| 03 | 2026-10-18 | 9 分 | hooks 只寫專案 .claude/settings.json，claude -p 實測觸發通過、pytest 4 passed；用 ruff format 取代 black；本章無 MCP 任務；開窗時誤開兩個已關閉，改預先允許外部 imports |
| 04 | 2026-10-18 | 5 分 | pymysql 改 sqlite3，參數化／環境變數／finally／logging 全做，28 passed（含 SQL 注入測試）；無 starter 改自寫函式；pre-commit 與 Actions 只寫範本 |
| 05 | 2026-10-18 | 7 分 | 實際重現 pandas ValueError traceback 再修復（17 passed）＋Flask log decorator（11 passed）；真實 traceback 比題目多 9 層內部框架；decorator 多做遮蔽與抽樣 |
| 06 | 2026-10-18 | 7 分 | 三層測試＋claude -p 實際生成測試，共 56 passed；無 starter 自建 alert_level.py；ex01 8 個測試（題目 6）；多做突變測試量化品質 |
| 07 | 2026-10-18 | 3 分 | 先建 12 個特性化測試再 Rename→Extract，12→13→16 全綠、每步獨立 commit；找 14 個異味（題目 5）；刻意保留怪行為不修 |
| 08 | 2026-10-18 | 7 分 | 合約寫成 JSON Schema 2020-12 並驗證合格／不合格樣本（抓 6 違規）、DAG 時間模擬、mock 協作 6 情境，12 passed；題目原只要文字與簡化 schema |
| 09 | 2026-10-18 | 6 分 | 能力地圖用 claude mcp list（17 server）；gh api GET 與 GitHub MCP 對照（repo 0 issue）；Notion 只用 --scope project 寫 .mcp.json 範本；Gmail 唯讀實查；使用者層 MCP 未變 |
| 10 | 2026-10-18 | 8 分 | ci.yml（pip 快取）＋deploy 範本＋多環境設定，yaml.safe_load 驗證並本機依 needs 跑 run 指令；未上 GitHub 實跑故快取命中未驗；本機 3.14 非 3.11；Vercel 只範本 |
| 11 | 2026-10-18 | 7 分 | create-next-app 建 landing/，Hero＋Pricing，npm run build＋eslint 通過、next start curl 200、三寬度截圖；只做兩元件；npm 5 個 high 漏洞未處理；不部署 |
| 12 | 2026-10-18 | 6 分 | 自建 legacy 信件簡報 pipeline 當現有系統，再加失敗點分析與重要度評分，15 passed；外部服務全本地模擬、摘要用規則；題目原只要偽程式碼 |
| 13 | 2026-10-18 | 14 分 | Neon 改本機 SQLite（另留 PG schema 範本）、NextAuth 改自簽 JWT；5 端點全做，vitest 24/24、tsc、build 通過、curl 冒煙；中途 vitest 報錯後停下，教練送「繼續」才完成 |
| 14 | 2026-10-18 | 9 分 | 模組化 CLAUDE.md（@ 匯入 docs/）＋settings 分層＋5 個專案 agents，訂單報表 12 unittest 通過、claude -p 驗證匯入；前端用原生 HTML 非 React；只實派 1 個 agent |
| 15 | 2026-10-18 | 7 分 | 漏洞版＋修復版（Python，題目片段為 Node.js），bandit 12→3 且 HIGH 歸零、pytest 13 passed；ex02 CI YAML 只文字設計未產檔 |
| 16 | 2026-10-18 | 5 分 | 專案 prompts/ 8 模板＋索引＋填變數工具，21 passed、claude -p 實跑 1 模板；題目要 ~/.claude/prompts/ 改專案層；slash command 未寫入全域 |
| 17 | 2026-10-18 | 9 分 | 自建最小 email-automation 子專案套用附錄 B 團隊 CLAUDE.md（@ 匯入），9/9 OK、claude -p 5 題皆遵守；匯入檔內規則 0/3 遵守、移到主檔 2/2；真寄信只範本 |
