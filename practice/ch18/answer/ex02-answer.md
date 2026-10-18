# 練習 02 解答：個人資安檢查清單

> 標 🤖 的項目已自動化在 `answer/demo/ex02_checklist_scan.py`（只讀取目標，不修改）。
> 對 ch15 兩個版本的實際掃描結果：`answer/reports/ex02-scan.txt`
> 用法：`PYTHONUTF8=1 .venv/Scripts/python answer/demo/ex02_checklist_scan.py <資料夾> [...]`
> 另搭配 `bandit -r <資料夾>` 做 Python 靜態掃描（報告在 `answer/reports/bandit-*.txt`）。

## A. 程式碼層面（審查每個 Claude 生成的片段）

- [ ] A1 🤖 SQL 查詢是否使用參數化查詢（沒有 f-string 或 `+` 拼接）？
- [ ] A2 使用者輸入有沒有驗證型別、格式、**範圍與長度**（前端＋後端都要，後端為準）？
- [ ] A3 🤖 API Key／密碼／密鑰有沒有寫死在程式碼中？
- [ ] A4 🤖 密碼有沒有明文儲存或傳輸？雜湊是否用 bcrypt／Argon2／scrypt（或 PBKDF2 ≥ 60 萬輪），並使用隨機 salt？
- [ ] A5 🤖 **（補）** 執行外部指令時是否 `shell=False`＋參數陣列，且參數不能以 `-` 開頭（防參數注入）？
- [ ] A6 🤖 **（補）** 有沒有對不受信任的資料使用 `eval`／`exec`／`pickle.loads`／`yaml.load`？
- [ ] A7 🤖 **（補）** 權限檢查有沒有用 `assert`（`python -O` 會被移除）？是否用顯式的 `if`＋例外？
- [ ] A8 **（補）** 每個讀寫資源的端點都有檢查「這筆資料屬於目前登入者」（防 IDOR）？
- [ ] A9 **（補）** 驗證失敗的回應訊息與**耗時**都一致（防帳號列舉；帳號不存在時也要跑一次假雜湊）？
- [ ] A10 **（補）** 輸出到 HTML 時有跳脫（用 `textContent` 而非 `innerHTML`，避免 XSS）？
- [ ] A11 **（補）** 檔案路徑由使用者輸入組成時，是否以 `resolve()` 後確認仍在允許的目錄內（防路徑穿越）？

## B. 依賴管理層面（定期執行）

- [ ] B1 🤖 有沒有已知漏洞的依賴？（`pip-audit`／`npm audit`；`pip check` 只檢查相依衝突，不查 CVE）
- [ ] B2 🤖 依賴版本有沒有鎖定？（`requirements.txt` 用 `==` 加 hash，或 `uv.lock`／`poetry.lock`／`package-lock.json`）
- [ ] B3 **（補）** 新增的套件確認過來源：下載量、維護者、最近更新時間、GitHub repo 是否對得上（防 typosquatting／slopsquatting）？
- [ ] B4 **（補）** CI 有開 Dependabot／Renovate，並在 PR 中跑 `pip-audit`，有高風險 CVE 時讓 build 失敗？
- [ ] B5 **（補）** 移除沒用到的依賴，減少攻擊面？

## C. 環境設定層面（部署前必查）

- [ ] C1 🤖 `.env` 有沒有加入 `.gitignore`？有沒有提供 `.env.example`？
- [ ] C2 🤖 Production 環境的 DEBUG 模式有沒有關閉？
- [ ] C3 錯誤訊息有沒有把 stack trace 洩漏給使用者（只回通用訊息＋錯誤代碼，細節寫到伺服器 log）？
- [ ] C4 **（補）** git 歷史中是否曾經 commit 過機密？（`gitleaks detect`；一旦外洩就必須 rotate，光刪檔不夠）
- [ ] C5 **（補）** 是否強制 HTTPS／HSTS，Cookie 有沒有設 `Secure`、`HttpOnly`、`SameSite`？
- [ ] C6 **（補）** CORS 沒有設成 `*`＋credentials？安全標頭（CSP、X-Content-Type-Options）是否到位？
- [ ] C7 **（補）** 服務與資料庫帳號是否採最小權限（例如報表用唯讀帳號），且不以 root／admin 身分執行？

## D. AI 特有的額外檢查（任務 2）

- [ ] D1 🤖 Claude 提到的第三方套件／函式真的存在嗎？（本機 `find_spec`／`hasattr`，再到 PyPI／npm 確認名稱、作者與下載量）
- [ ] D2 **（補）** Claude 建議的版本號、演算法、參數有沒有用**當下**的資料查證？（OWASP Cheat Sheet、官方文件、`pip-audit`），不採信模型記憶中的版本號
- [ ] D3 🤖 **（補）** 產生 token、OTP、重設密碼連結時，是否使用 `secrets`／`crypto.randomBytes`，而不是 `random`／`Math.random()`？
- [ ] D4 **（補）** 生成的程式碼是否套上**我的**業務規則與威脅模型（數量與金額範圍、角色、資料歸屬）？要求 AI 對每個輸入列出邊界案例，並寫成測試
- [ ] D5 **（補）** 我能逐行說明這段程式碼在做什麼嗎？AI 留下的 `TODO`、`verify=False`、`# 暫時關閉 CSRF`、`except: pass` 這類 workaround 是否都已處理？
- [ ] D6 **（補）** 修補 AI 提出的漏洞後，有另外寫「攻擊測試」證明攻擊真的被擋下（如 ch15 的 `exploit_demo.py` 對照 `test_app.py`），而不是只看 AI 說「已修復」？
- [ ] D7 **（補）** 有沒有把機密、客戶資料、production 設定貼進 AI 對話？是否改用遮罩後的範例資料？

## 自動化掃描實測（ch15-sample）

| 項目 | vulnerable | fixed |
| --- | --- | --- |
| A1 SQL 拼接 | FAIL（app.py:36, 43） | PASS |
| A3 硬編碼密鑰 | FAIL（19, 20） | PASS |
| A4 弱雜湊 | FAIL（29, 42） | PASS |
| A5 shell=True | FAIL（58；另有 7、57 為 docstring 誤報） | PASS |
| A6 eval／pickle | FAIL（63, 68） | PASS |
| A7 assert 權限 | FAIL（73） | PASS |
| C2 DEBUG=True | PASS | PASS |
| D1 幻覺 import | PASS | PASS |
| D3 random 產 token | PASS | PASS |
| B2 鎖定檔 | FAIL（找不到） | FAIL（找不到） |
| C1 .env／.gitignore | N/A（沒有 .env） | N/A |
| B1 pip check／pip-audit | PASS／PASS（pip 升級到 26.2.1 之後） | 同左 |

**限制**：以正規表示式掃描只能抓「長得像」的問題。A8（IDOR）、A9（時間差列舉）、D4（業務規則）這類邏輯漏洞掃描器抓不到，必須人工審查加上動態探測，詳見 `answer/appendix-c-audit.md`。
