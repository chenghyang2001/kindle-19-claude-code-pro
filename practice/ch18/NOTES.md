# NOTES — K19 第 18 章練習＋附錄 C 資安審查

> 快速 demo 模式（依本專案 CLAUDE.md）：主 Claude 直接寫檔，未經 writer／QA／reviewer 三 agent 流程。

## 做了什麼

| 項目 | 產出 |
| --- | --- |
| 練習 01：5 種 AI 特有風險＋盲點 | `answer/ex01-answer.md`；可執行示範 `answer/demo/ex01_ai_risk_demo.py` |
| 練習 02：個人資安清單（A 11 條／B 5 條／C 7 條／D 7 條） | `answer/ex02-answer.md`；自動掃描器 `answer/demo/ex02_checklist_scan.py` |
| 附錄 C：逐項審查 ch15 兩個版本（26 項 × 2） | `answer/appendix-c-audit.md`；動態探測 `answer/audit/probe_checklist.py` |
| 證據 | `answer/reports/`（exploit、pytest、bandit txt/json、探測、掃描輸出） |
| 環境 | 本專案 `.venv`（bandit 1.9.4、pytest 9.1.1、pip-audit），`.gitignore` 排除 `.venv`、`__pycache__`、`.env` |

## 驗證結果（全部實際執行）

1. **漏洞版攻擊重現**（`exploit_demo.py`）：SQL 注入撈出全表、`alice' --` 繞過密碼、命令注入、pickle 反序列化執行函式、eval 呼叫任意模組，5 項全部成功。
2. **V7 assert**：用 `python -O` 執行，非 admin 成功刪除 alice。
3. **修復版 pytest**：13 passed。
4. **bandit**：漏洞版 13 個（High 3／Medium 4／Low 6）；修復版 12 個，全部 Low，其中 9 個是測試檔的 assert。
5. **附錄 C 打勾**：漏洞版 ✅3／❌16／➖7，修復版 ✅5／❌14／➖7（以腳本自動複核表格數字）。
6. **修復版新發現，bandit 與原測試都沒抓到**：
   - 時間差帳號列舉：存在帳號登入 192 ms、不存在帳號 0.01 ms
   - 主機名白名單放行 `-t`、`--help`，造成 ping 參數注入，且 `CalledProcessError` 沒被捕捉
   - token 固定不變、無法撤銷，也沒有驗證函式
   - IDOR、沒有頻率限制、沒有逾時、沒有依賴鎖定檔
7. **ex01 示範**：5 種風險都重現出來，包括幻覺 API 不存在、MD5 比 PBKDF2 快約 14 萬倍、`ping -c` 在 Windows 失敗、負數量造成負總價、random token 可被重算。
8. **ex02 掃描器**：漏洞版命中 A1、A3、A4、A5、A6、A7、B2；修復版只剩 B2。錯誤案例（資料夾不存在）會以 exit 1 結束。
9. **pip-audit 真實發現**：新建的 venv 中 pip 25.3 有 PYSEC-2026-3721；升級到 26.2.1 後重跑，結果為 PASS。

## 與題目要求的差異

- **「回顧整本書（第 15 章、附錄 A-C）」**：資料夾中只有附錄 C 與 ch15 範例程式，沒有附錄 A、B 原文。ex02 清單是依附錄 C、ch15 範例和一般資安實務（OWASP）整理，**沒有逐條對照附錄 A、B**。
- **附錄 C 清單有重複**：#10 和 #11 原文是同一句話被斷成兩行。審查時把 #11 解讀成「防帳號列舉（含時間差）」分開評分，總數照原文算 26 項。
- **清單只有「通過／不通過／不適用」三種狀態**：部分通過的項目（例如 #15 role 由呼叫端傳入、#24 PBKDF2 輪數低於 OWASP 建議）標為 ✅ 並加附註；驗證存在但有缺口的（#2）從嚴標為 ❌。
- **`pip check` 不查 CVE**：題目寫「已知漏洞（`npm audit` / `pip check`）」，但 `pip check` 只檢查相依衝突，所以另外加裝 `pip-audit` 才能真的查 CVE。
- **需要外部帳號或服務的部分沒有實作**：Dependabot／Renovate、CI 的 pip-audit gate、`gitleaks`、到 PyPI 網頁人工確認套件來源，都只寫在清單裡，沒有實際設定。
- **沒有修改 ch15-sample**：11 個檔案的數量與時間戳都沒變；有發現的問題只記錄在報告中，沒有修程式碼。
- **掃描器限制**：使用正規表示式，A5 會把 docstring 裡的 `shell=True` 字樣算成命中（漏洞版第 7、57 行）。邏輯類漏洞（IDOR、時間差）不在自動化範圍內。
- 依指示：沒有 push、沒有建 GitHub repo、沒有改全域 `~/.claude/`。

## 已知未處理的風險（快速模式）

- 示範、探測與掃描腳本沒有經過獨立 QA 或 review。
- 時間差數值會因機器而不同；結論依據的是數量級差距（約 3 萬倍），不是絕對數值。
