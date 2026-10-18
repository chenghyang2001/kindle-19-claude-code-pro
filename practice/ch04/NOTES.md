# NOTES — K19 第 4 章練習

> 快速 demo 模式（依專案 CLAUDE.md），未經獨立 QA／code review agent 審查。

## 做了什麼

| 檔案 | 內容 |
| ------ | ------ |
| `src/legacy_fetch_user.py` | 原始「快樂路徑」版本，改用 sqlite3 以便本機重現 SQL 注入 |
| `src/user_repo.py` | 練習 01 生產級 `fetch_user`：參數化查詢、`APP_DB_PATH` 環境變數、try/finally、logging、型別驗證 |
| `tests/test_user_repo.py` | 21 個 pytest（正常、邊界、4 種注入攻擊字串、連線關閉、log） |
| `starter/order_report.py` | 練習 02 審查對象（自寫約 30 行，刻意含 10 類缺陷，保留不改） |
| `src/order_report.py` | 練習 02 修正版 |
| `tests/test_order_report.py` | 7 個 pytest（含 3 種注入字串） |
| `tools/quality_gate.py` | regex 品質閘門，6 條規則，命中回 exit 1 |
| `templates/pre-commit-config.yaml`、`templates/github-quality.yml` | hook／CI 範本（未啟用） |
| `answer/ex01-answer.md`、`answer/ex02-answer.md` | 解答 |

## 驗證結果（實際執行）

- `PYTHONUTF8=1 python -m pytest -q` → **28 passed**（Python 3.14.3、pytest 8.4.2、Windows 10）
- `python -m src.user_repo` 冒煙：id=1 回 dict、id=99 回 None
- `python tools/quality_gate.py starter` → 6 個問題，exit=1
- `python tools/quality_gate.py src/user_repo.py src/order_report.py tools` → 0 個問題，exit=0
- 對照測試證明原始 f-string 版本確實會被 `999 OR 1=1` 打穿

## 和題目要求的差異

1. **pymysql → sqlite3**：依本章補充改用標準庫，不需 MySQL 伺服器；佔位符從 `%s` 變 `?`。pymysql 寫法只寫在解答文字裡，未實測。
2. **環境變數**：sqlite 只要檔案路徑，所以讀 `APP_DB_PATH`，而不是 host／user／password 等多個變數。
3. **`starter/` 不存在**：練習 02 改用題目允許的「自己寫一個 30 行函式」。
4. **題目只要求修最嚴重一項**，修正版其實 10 項都修了；最嚴重的（SQL 注入）在解答中單獨說明。
5. **修正版改用 `urllib`**，不依賴 `requests`；報表送出改成可注入 `sender`，測試不連網。starter 仍 import `requests`，但它只用來審查、不會被執行。
6. **需外部服務的部分只寫範本**：pre-commit（需安裝 pre-commit 套件）、GitHub Actions（需 GitHub repo）放在 `templates/`，未啟用、未執行；報表 API 網址是虛構的 `report.example.com`。
7. **starter 裡的金鑰與路徑是假值**（`sk-demo-not-a-real-key`、`C:/Users/demo/...`），是刻意的反面教材。

## 已知限制

- `quality_gate.py` 是 regex 粗篩，會漏報（例如跨行組字串的 SQL），也可能誤報；正式專案應改用 bandit／ruff／gitleaks。
- `fetch_user` 會拒絕字串 `"1"`，若 id 來自 HTTP 參數，呼叫端要先轉成 int。
