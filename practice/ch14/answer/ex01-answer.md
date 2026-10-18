# 練習 01 解答 — 團隊 CLAUDE.md 設計

> 本解答已實際建檔，不只是文字範本。對應檔案：
> `CLAUDE.md`、`docs/api-conventions.md`、`docs/db-rules.md`、`docs/deploy-rules.md`、
> `docs/roles/{frontend,backend,devops}.md`、`CLAUDE.local.md.example`、
> `.claude/settings.json`（團隊）、`.claude/settings.local.json`（個人）、`.gitignore`

---

## 任務 1：CLAUDE.md 的三類資訊

| 類別 | 目的 | 範本中的規則（各 ≥ 3 條） |
| --- | --- | --- |
| **Claude 能做什麼（Do）** | 告訴 Claude 可以主動做、不必每次問 | 1. 寫/改程式碼並同時補測試<br>2. 執行測試、lint、本機啟動服務驗證<br>3. 撰寫 migration（含 up/down） |
| **Claude 不能做什麼（Don't）** | 劃出紅線，避免破壞性操作 | 1. 不連正式 DB、不 DROP/TRUNCATE<br>2. 不 push main、不 force push<br>3. 不把 API key / 密碼寫進程式碼 |
| **架構 / 環境資訊** | 讓 Claude 不用猜 | 1. 技術堆疊：React+TS 前端、Python API、SQLite/PostgreSQL<br>2. 測試指令：`PYTHONUTF8=1 python -m unittest discover -s tests -v`<br>3. 分支策略：feature → PR → main（受保護） |

團隊不一致問題的根因是「每個人各自寫 CLAUDE.md」。解法：**專案根目錄的 `CLAUDE.md` 進版控**，成為唯一的團隊共識；個人差異只放在不進版控的檔案。

### 範本（主 CLAUDE.md 的電商段落，實際內容見專案根目錄 `CLAUDE.md`）

```markdown
# 電商後台 — 團隊共用 CLAUDE.md

## 架構 / 環境
- 前端：React + TypeScript（web/）；後端：Python API（order_report/）；DB：SQLite / PostgreSQL
- 測試指令：PYTHONUTF8=1 python -m unittest discover -s tests -v
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
```

---

## 任務 2：模組化 CLAUDE.md

超過 100 行時的原則：**主檔只留「每次對話都必須知道」的事 + 匯入清單**，主題細節拆到 `docs/`。

```
k19-ch14-practice/
├── CLAUDE.md                  ← 主檔：架構摘要 + Do/Don't + @ 匯入
├── CLAUDE.local.md            ← 個人（gitignore），只寫 @docs/roles/<角色>.md
├── docs/
│   ├── api-conventions.md     ← API 設計規範（路徑、回應格式、狀態碼、分頁）
│   ├── db-rules.md            ← DB 規則（參數化、migration、金額型別、索引）
│   ├── deploy-rules.md        ← 部署規則（只走 CI、回滾、週五不部署）
│   └── roles/
│       ├── frontend.md
│       ├── backend.md
│       └── devops.md
└── .claude/
    ├── settings.json          ← 團隊共用設定（進版控）
    ├── settings.local.json    ← 個人設定（gitignore）
    └── agents/                ← 專案 subagents（練習 02）
```

匯入語法重點：

- 在 CLAUDE.md 中獨立一行寫 `@docs/xxx.md`，路徑相對於「寫匯入的那個檔案」。
- 被匯入檔也可以再 `@` 匯入其他檔（可遞迴，有深度上限）。
- 寫在 `` `反引號` `` 或程式碼區塊內的 `@路徑` **不會**被當成匯入，可安全地拿來舉例。

**驗證方式**：每份 docs 檔放一個「驗證暗號」（API-4417 / DB-7731 / DEPLOY-2093），用 `claude -p` 在**禁用 Read/Bash/Grep 等工具**的狀態下詢問暗號。Claude 三個都答對，證明內容是透過匯入進到 context，而不是臨時讀檔（輸出存在 `answer/claude-p-verify.txt`）。

---

## 任務 3：角色專用 context

| 做法 | 怎麼做 | 優點 | 缺點 |
| --- | --- | --- | --- |
| **A. `CLAUDE.local.md` + 角色檔匯入**（本專案採用） | 角色規則放 `docs/roles/*.md`（進版控）；每人的 `CLAUDE.local.md`（gitignore）只寫一行 `@docs/roles/backend.md` | 角色規則有版控、可 review；個人只選角色，不會互相覆蓋；團隊規則仍一致 | 新成員要記得建 `CLAUDE.local.md`（提供 `.example` 降低門檻） |
| **B. 子目錄 CLAUDE.md** | `web/CLAUDE.md`、`order_report/CLAUDE.md`、`infra/CLAUDE.md` | 依「在哪個目錄工作」自動載入，零設定 | 依目錄不依人；全端改動跨目錄時規則會混在一起 |
| **C. 個人 `~/.claude/CLAUDE.md`** | 每人在家目錄寫自己的角色偏好 | 完全個人化、跨專案 | 不進版控，又回到「每人不一樣」的原問題；不適合放專案規則 |
| **D. Subagent 承載角色** | `.claude/agents/frontend-dev.md` 等，角色規則寫在 agent system prompt | context 隔離最乾淨，主對話不被干擾 | 只有派 agent 時才生效；日常對話不適用 |
| **E. `--append-system-prompt` / 啟動腳本** | `claude --append-system-prompt "$(cat docs/roles/devops.md)"` | 一次性、可寫進 alias | 要記得用特定指令啟動，容易忘 |

**建議**：A（團隊規則 + 個人選角色）為主，搭配 B 處理目錄專屬規則，需要隔離的大任務用 D。

**驗證結果**：`CLAUDE.local.md` 匯入 `docs/roles/backend.md` 後，`claude -p` 回答「目前角色是後端工程師」並複述該檔規則。

---

## 補充：團隊設定 vs 個人設定

| 檔案 | 版控 | 放什麼 | 本專案內容 |
| --- | --- | --- | --- |
| `.claude/settings.json` | ✅ 進版控 | 全隊一致的權限與環境變數 | 允許 `python -m unittest`、`git status/diff`；禁止 `git push`、禁讀 `.env`；`PYTHONUTF8=1` |
| `.claude/settings.local.json` | ❌ gitignore | 個人習慣、個人額外放行的指令 | 放行 `claude -p` 驗證指令 |
