# 練習 01 解答 — 撰寫 CLAUDE.md

## 任務 1：最小可用 CLAUDE.md

實際檔案：專案根目錄 [`CLAUDE.md`](../CLAUDE.md)。為了讓「執行方式／常用指令」可以真的跑，另外建了最小 Flask 範例（`app/`、`tests/`、`run.py`），`pytest` 4 個測試通過。

六個區塊對照：

| 題目要求 | CLAUDE.md 區塊 | 內容摘要 |
| --- | --- | --- |
| 專案說明 | `## 1. 專案說明` | 待辦事項 REST API，資料存記憶體 |
| 技術堆疊 | `## 2. 技術堆疊` | Python 3.14 / Flask 3.1 / SQLite→PostgreSQL / Render |
| 執行方式 | `## 3. 執行方式` | `python run.py`、`PYTHONUTF8=1 python -m pytest -q` |
| 目錄結構 | `## 4. 目錄結構` | 表格列出 7 個路徑用途 |
| 禁止事項 | `## 5. 禁止事項` | 不可改 prod DB、不可 commit 機密、不可 force push 等 5 條 |
| 常用指令 | `## 6. 常用指令` | pytest / run.py / ruff format / ruff check / curl health |

完整內容：

````markdown
# Todo API（Flask 練習專案）

## 1. 專案說明

小型 REST API，提供「待辦事項」的新增與查詢，讓前端或腳本用 HTTP 管理待辦清單。
目前是教學 demo：資料存在記憶體，重啟就清空。

## 2. 技術堆疊

- 語言：Python 3.14
- 框架：Flask 3.1（app factory + Blueprint）
- 資料庫：目前沒有接資料庫（資料存在記憶體）；規劃開發用 SQLite（`sqlite:///dev.db`）、正式環境用 PostgreSQL
- 測試：pytest 8
- 格式化：ruff format（Write `.py` 後由 PostToolUse hook 自動執行）
- 部署平台：Render（規劃中，尚未部署）

## 3. 執行方式

- 啟動開發伺服器：`python run.py`（http://127.0.0.1:5000/api/health）
- 跑測試：`PYTHONUTF8=1 python -m pytest -q`
- 執行 Python 前一律加 `PYTHONUTF8=1`（Windows 預設 cp950）

## 4. 目錄結構

| 路徑 | 用途 |
| --- | --- |
| `app/__init__.py` | `create_app()` 應用程式工廠 |
| `app/routes.py` | API 路由（`/api/health`、`/api/todos`） |
| `tests/` | pytest 測試，每個 API 都要有正常／邊界／錯誤案例 |
| `run.py` | 開發伺服器入口 |
| `.claude/settings.json` | 專案 hooks（PostToolUse 格式化、SessionStart 狀態） |
| `.claude/hooks/` | hook 腳本 |
| `answer/` | 練習解答 |

## 5. 禁止事項

- 不可直接連線或修改正式（prod）資料庫，所有 schema 變更走遷移檔
- 不可把 API key、密碼、`.env` 寫進程式碼或 commit
- 不可 `git push --force`、不可用 `--no-verify` 跳過 hook
- 不可修改全域 `~/.claude/` 設定，設定只寫在本專案 `.claude/`
- 不可刪除或跳過既有測試讓 CI 變綠

## 6. 常用指令

```bash
PYTHONUTF8=1 python -m pytest -q          # 跑全部測試
python run.py                             # 啟動開發伺服器
python -m ruff format .                   # 格式化全部 .py
python -m ruff check .                    # 靜態檢查
curl http://127.0.0.1:5000/api/health     # 健康檢查
```
````

（原檔最後還保留了練習資料夾本來就有的「本專案例外」區塊，與題目無關，此處省略。）

## 任務 2：測試有效性

做法：用 `claude -p` 開三個**全新**的 non-interactive session（先 `env -u` 清掉所有 `CLAUDE*` 環境變數、`timeout 120`），各問一題。原始輸出存在 `answer/logs/ex01-q1~3.txt`。

```bash
UNSET=$(env | grep -o '^CLAUDE[A-Z_]*' | sed 's/^/-u /' | tr '\n' ' ')
env $UNSET timeout 120 claude -p "這個專案是做什麼的？ 請簡短回答（5 行內），並說明資訊來源檔案。"
```

| 問題 | 結果 | 引用來源 | 評分 |
| --- | --- | --- | --- |
| 這個專案是做什麼的？ | Flask 3.1 待辦 REST API、資料存記憶體、app factory + Blueprint、Render 規劃中 | CLAUDE.md §1～4 | ✅ 正確 |
| 我要怎麼跑測試？ | `PYTHONUTF8=1 python -m pytest -q`，並說明 PYTHONUTF8 原因 | CLAUDE.md §3、§6 | ✅ 正確 |
| 有什麼操作被禁止？ | 列出 prod DB、機密、force push / no-verify、全域設定、刪測試 | CLAUDE.md §5 | ✅ 正確（5 條併成 4 點） |

### 答得不好／可改進的地方

1. **資料庫描述有歧義**：Q1 回答「開發環境要用 SQLite」，但實際程式只把 `DATABASE_URL` 放進 config，資料存在記憶體。CLAUDE.md 的「開發用 SQLite」寫法會誤導 → 應改成「目前無資料庫（記憶體），SQLite/PostgreSQL 皆為規劃」。（**已修正**：上方 CLAUDE.md 為修正後版本。）
2. **自行推測的資訊**：Q1 說「這是 Kindle 書籍第 3 章的練習」，是從資料夾名稱與「本專案例外」推測的，不是專案說明本身——代表 CLAUDE.md 裡跟專案無關的段落也會被拿來回答。
3. **規則互相矛盾**：「禁止事項」說設定寫在 `.claude/`，原有「本專案例外」寫的是 `.claude/settings.local.json`，但本練習 hook 實際放在 `.claude/settings.json`。Q3 有把兩條一起引用，但沒發現兩者不一致。
4. 三題都沒被全域 `~/.claude/CLAUDE.md` 的大量規則干擾，專案層資訊優先被引用，代表六區塊結構有效。
