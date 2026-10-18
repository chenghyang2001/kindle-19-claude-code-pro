
## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。

---

# 電商後台（練習用範本）— 團隊共用 CLAUDE.md

> 本段是 ex01 的「主 CLAUDE.md」：只放最重要的規則 + @ 匯入，細節拆到 docs/。

## 架構 / 環境（Claude 需要知道的）
- 前端：React + TypeScript（`web/`）；後端：Python API（`order_report/`）；DB：SQLite（練習）/ PostgreSQL（正式）
- 測試指令：`PYTHONUTF8=1 python -m unittest discover -s tests -v`
- 分支策略：feature branch → PR → main；main 受保護

## Claude 可以做（Do）
- 撰寫/修改程式碼並同時補測試
- 執行測試、lint、本機啟動服務驗證
- 撰寫 migration 檔（含 up / down）

## Claude 不可以做（Don't）
- 不可直接連正式資料庫，不可執行 DROP / TRUNCATE
- 不可 push 到 main、不可 force push
- 不可把 API key / 密碼寫進程式碼或 commit

## 詳細規範（模組化匯入）
@docs/api-conventions.md
@docs/db-rules.md
@docs/deploy-rules.md

## 角色專用 context
各角色個人的 `CLAUDE.local.md`（已 gitignore）只寫一行匯入自己的角色檔，例如：
`@docs/roles/backend.md`
