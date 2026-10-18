# NOTES — K19 第 14 章練習（團隊 CLAUDE.md + Sub-agent 拆解）

> 快速 demo 模式：主 Claude 直接寫檔，未走 writer / QA / reviewer 流程。

## 做了什麼

### 練習 01：團隊 CLAUDE.md

- 在既有 `CLAUDE.md`（保留原本的「本專案例外」段落）後面加上電商後台團隊範本：架構環境、Do、Don't 各 3 條，加上 3 行 `@docs/...` 匯入。
- 建立 `docs/api-conventions.md`、`docs/db-rules.md`、`docs/deploy-rules.md`，每份放一個驗證暗號。
- 角色 context：`docs/roles/{frontend,backend,devops}.md` + `CLAUDE.local.md.example`；本機的 `CLAUDE.local.md` 匯入 backend 角色。
- 設定分層：`.claude/settings.json`（團隊，進版控）、`.claude/settings.local.json`（個人，gitignore）。
- 解答：`answer/ex01-answer.md`

### 練習 02：Sub-agent 拆解

- `.claude/agents/` 建 5 個專案 subagent：`report-db-schema`、`report-api-endpoint`、`report-frontend-chart`、`report-csv-export`、`report-test-writer`。
- 真的實作「訂單報表」：SQLite schema + 聚合查詢、`GET /api/reports/orders`（含 `.csv` 匯出）、SVG 長條圖頁面、12 個 unittest。
- 解答：`answer/ex02-answer.md`（依賴圖 + API 子任務 prompt）

## 驗證結果

| 項目 | 指令 | 結果 |
| --- | --- | --- |
| 單元 / 整合測試 | `PYTHONUTF8=1 python -W error -X dev -m unittest discover -s tests` | 12 tests OK |
| 真實伺服器 | `python -m order_report.api 8799` + curl | 200 JSON、400 INVALID_RANGE、CSV（BOM `ef bb bf`）都正確；測完已關閉 |
| @ 匯入有被載入 | `claude -p`（禁用 Read/Bash/Grep/Glob/Edit/Write） | 三個暗號 API-4417 / DB-7731 / DEPLOY-2093 全答對；角色答「後端工程師」 |
| subagent 有被讀到 | 同上 | 列出 5 個 report-* agent 與依賴關係 |
| subagent 可被派遣 | `claude -p` 要求用 Agent 工具派 `report-test-writer` | 實際執行並回報 12 tests OK |

`claude -p` 執行前已清掉所有 `CLAUDE*` 開頭的環境變數，並加 `timeout 120`。輸出存在 `answer/claude-p-verify.txt`、`answer/claude-p-agent-run.txt`。

### 過程中發現並修正的問題

1. 測試預期營收 5447 是手算錯誤，正確為 5448（1200+350+350+899+150+2499）。這就是 ex02 任務 1 說的「自我驗證偏差」實例。
2. subagent 回報 `HTTPError` 未關閉造成 ResourceWarning → 用 `with e:` 關閉；另補上 sqlite 連線的 `close()`。
3. Write 工具把 `"﻿"` 寫成不可見的 BOM 實體字元 → 改回跳脫寫法，避免日後維護時看不見。
4. 一開始用一個巨大的 bash heredoc 建檔失敗（解析錯誤，什麼都沒寫入），改用逐檔寫入。

## 和題目要求的差異

- **題目只要求設計文件**；這次額外把設計真的建出來（CLAUDE.md 匯入、settings、agents、可執行的訂單報表），並用測試與 `claude -p` 驗證。
- **前端**：題目情境是 React，這裡為了零安裝改用單一 HTML + 原生 JS + SVG 長條圖；只用 HTTP 測試確認頁面能回傳，**沒有用瀏覽器截圖驗證畫面**（快速模式省略）。
- **資料庫**：用 SQLite 記憶體資料庫代替 PostgreSQL；沒有 migration 工具（只有 `schema.sql`）。
- **subagent 並行**：依賴圖有標出並行點，但這次程式碼是主 Claude 直接寫的，**沒有真的同時派 5 個 agent 開發**；實際派遣只示範了 `report-test-writer` 一個。
- **不進版控的檔案**：`CLAUDE.local.md`、`.claude/settings.local.json` 依設計被 `.gitignore` 排除，所以 commit 裡看不到；團隊版範本是 `CLAUDE.local.md.example`。
- **沒有認證**：API 未做登入驗證（假設由 gateway 處理），正式使用前要補。
- 未 push、未建 GitHub repo、未修改全域 `~/.claude/`。
