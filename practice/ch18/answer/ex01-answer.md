# 練習 01 解答：AI 程式碼資安風險識別

> 每種風險都附可執行示範：`answer/demo/ex01_ai_risk_demo.py`
> 實際執行輸出：`answer/reports/ex01-demo.txt`
> 執行方式：`PYTHONUTF8=1 .venv/Scripts/python answer/demo/ex01_ai_risk_demo.py`

## 任務 1：5 種 AI 特有的安全風險

### 1. 幻覺 API 呼叫

- **例子**：Claude 建議 `crypto.secureHash()`／`hashlib.secureHash()`，或 `pip install requests-secure-auth` 這類「聽起來很合理」的名稱，但它們不存在。
- **實測**：`hashlib.secureHash 存在? False`、`secrets.secure_random_string 存在? False`；真的函式 `hashlib.pbkdf2_hmac`、`secrets.token_urlsafe` 則為 True。
- **風險**：
  - 開發者為了讓程式跑起來，自己補一個同名函式，結果寫成不安全的版本（例如用 MD5 自製「secureHash」）。
  - **Slopsquatting**：攻擊者把 AI 常幻覺出的套件名稱搶先註冊到 PyPI／npm，裡面放惡意程式，`pip install` 一執行就中招（供應鏈攻擊）。
  - 存在但參數用錯（例如以為 `verify=False` 是預設），導致安全機制被關掉卻不自知。

### 2. 過時的安全建議

- **例子**：
  - 用 MD5／SHA-1 存密碼（舊教學很多）；`ch15-sample/vulnerable/app.py:29,42` 就是這樣寫的。
  - 建議使用已有 CVE 的舊版套件（例如舊版 `PyYAML` 的 `yaml.load()` 不帶 `Loader`、舊版 `jsonwebtoken`）。
  - 用已淘汰的 TLS 1.0／1.1，或 PBKDF2 輪數仍寫 1 萬輪（OWASP 2023 建議 PBKDF2-SHA256 至少 60 萬輪）。
- **實測**：單核每秒可算約 **55 萬次 MD5**，PBKDF2(20 萬輪) 每秒約 **3.9 次**，相差約 **14 萬倍**。資料庫外洩後，MD5 密碼幾乎可以直接暴力破解。
- **風險**：程式碼看起來「有做雜湊、有加密」，審查時容易放行；訓練截止日之後才公開的 CVE，AI 完全不知道。

### 3. 過度通用的程式碼

- **例子**：AI 預設 Linux 環境，寫出 `ping -c 1`、寫死 `/tmp/xxx`、`chmod 600`；或假設單機部署，把 session 存在記憶體，也沒考慮反向代理後的 `X-Forwarded-For`。
- **實測**：在本機（win32）執行 `ping -c 1 127.0.0.1` 回傳 exit code 1，因為 Windows 的 ping 沒有 `-c` 選項；本機暫存目錄也不是 `/tmp`。
- **風險**：
  - 安全相關的設定在你的環境下**靜默失效**，例如 `chmod` 在 Windows 沒作用，檔案仍然誰都能讀。
  - 頻率限制若以 `request.remote_addr` 計算，放在反向代理後面時所有使用者都是同一個 IP，限制形同失效，或反過來誤擋所有人。
  - 範例預設 `DEBUG=True`、`CORS: *`，直接上線就把除錯介面和跨站存取開放出去。

### 4. 缺少業務邏輯驗證

- **例子**：AI 寫出的結帳函式 `price * qty * (100 - coupon_pct) // 100` 語法正確、型別也正確，但沒有任何業務規則。
- **實測**：`qty=-3` 時總價為 **-3000**（變成退款）；`coupon_pct=150` 時總價為 **-500**（商家倒貼）。
- **風險**：AI 不知道「數量 1～99」「折扣上限 30%」「一人限用一張券」「只能看自己的訂單」這些規則。這類**邏輯漏洞**（IDOR、竄改價格、重複兌換）掃描工具通常抓不到，也最容易被利用來賺錢。ch15 修復版的 `get_user` 也一樣：SQL 注入修好了，但任何人仍可查任何 id（見 `answer/appendix-c-audit.md` 第 13 項）。

### 5. 過度信任 Claude 的輸出

- **例子**：直接複製 AI 給的「產生重設密碼 token」程式碼 `random.choices(...)`，或複製「為了解決 SSL 錯誤先加 `verify=False`」的建議。
- **實測**：用相同種子重算 `random` 產生的 token，**攻擊者重算的結果和受害者的 token 完全相同（True）**；正確作法是 `secrets.token_hex()`。
- **風險**：
  - 開發者不理解程式碼，就無法判斷它在邊界條件下是否安全，出事後也不會修。
  - AI 的語氣很篤定，容易讓人省略 code review 與測試；「能跑」被誤當成「安全」。
  - 暫時性的 workaround（關掉 CSRF、關閉憑證驗證）被原封不動地帶上線。

## 任務 2：Claude 在安全性上的盲點

### (1) 知識截止日期的影響

- 模型只知道**訓練資料截止日之前**公開的漏洞與最佳實務（本次執行的模型截止於 2026 年中；舊版模型更早）。截止日之後的 CVE、套件被接管、演算法被攻破、框架預設值改變，它都不知道。
- 對策：版本與 CVE 一律以工具即時查詢為準（`pip-audit`、`npm audit`、GitHub Dependabot、OSV.dev），不要問 AI「這版本安全嗎」。本次實測：`pip-audit` 在剛建好的 venv 裡就抓到 **pip 25.3 有 PYSEC-2026-3721**，升級到 26.2.1 後才通過（見 `answer/reports/ex02-scan.txt`）。

### (2) Claude 不知道你環境的哪些資訊

| 類別 | Claude 看不到的資訊 |
| --- | --- |
| 部署 | production 設定檔、環境變數實際值、是否在反向代理／負載平衡後面、容器權限 |
| 網路 | 防火牆規則、哪些服務對外、TLS 由誰終止、內網信任邊界 |
| 資料 | 哪些欄位是個資／機敏資料、資料保存法規（個資法、GDPR）、資料量級 |
| 身分 | 使用者角色模型、帳號停用流程、SSO 整合方式 |
| 業務 | 價格、額度、狀態機規則、哪些操作需要二次確認 |
| 版本 | 實際安裝的套件版本與 lock 檔、OS 與執行環境（Windows／Linux） |
| 威脅模型 | 誰是攻擊者、哪些資產最值錢、過去被攻擊過什麼 |

### (3) 「看起來安全但其實不安全」的典型情況

本次對 ch15 修復版的審查實際找到其中幾種（證據見 `answer/appendix-c-audit.md`）：

1. **修了表面、漏了相鄰的問題**：修復版改用 PBKDF2，卻在帳號不存在時直接跳過雜湊計算，登入耗時差了約 **3 萬倍**（192 ms vs 0.01 ms），可以靠時間差列舉帳號。
2. **白名單看起來很嚴，其實有缺口**：主機名正規表示式 `^[A-Za-z0-9.-]{1,253}$` 擋掉了 shell 元字元，卻放行 `-t`、`--help`，這些會被當成 ping 的選項傳入（參數注入）。
3. **有簽章卻不安全的 token**：`user_id.HMAC(user_id)` 每次登入都一樣，沒有到期時間也無法撤銷，一旦外洩就永久有效。
4. **權限檢查的位置不對**：`delete_user(conn, current_role, ...)` 的角色由呼叫端傳入；如果上層直接拿使用者請求裡的 role，檢查就形同虛設。
5. **用了「看起來像安全」的 API**：例如 `assert` 做權限檢查（`python -O` 執行時會被移除，實測非 admin 成功刪除 alice）、`random` 產生 token、`yaml.load`、`verify=False`、`ast.literal_eval` 卻沒有限制輸入長度。
6. **只處理快樂路徑**：沒有逾時、沒有捕捉例外（`CalledProcessError` 直接往上丟），在 Web 層就可能洩漏堆疊追蹤或被拖垮（DoS）。
7. **測試全部通過的錯覺**：修復版 13 個 pytest 全綠，但測試只涵蓋 ch15 的 7 個漏洞，沒有測授權、列舉、頻率限制。測試通過不等於安全。
