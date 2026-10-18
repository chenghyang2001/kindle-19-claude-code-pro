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

## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。
