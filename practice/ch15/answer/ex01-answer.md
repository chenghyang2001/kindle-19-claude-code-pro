# 練習 01 解答 — 常見安全漏洞偵測

> 對應題目：`exercise-01-基礎.md`。本練習另以 `vulnerable/app.py`（Python 版、密鑰全用假值）實作題目的 Node.js 片段，並用 `vulnerable/exploit_demo.py` 實際跑出攻擊、用 `fixed/app.py` 示範修復、用 bandit 量化前後問題數。

---

## 任務 1：識別漏洞（題目的 Node.js 片段）

題目片段有以下安全問題（> 3 個）：

| # | 位置 | 威脅類型 | 攻擊者如何利用 |
| --- | ------ | ---------- | ---------------- |
| 1 | `` `...WHERE id = ${userId}` `` | **SQL Injection** | `?id=0 OR 1=1` 回傳全表；`?id=0; DROP TABLE users--` 可破壞資料；`UNION SELECT` 可竊取其他表 |
| 2 | `u.password === password` | **明文密碼儲存** | 使用者物件直接存明文密碼，資料庫或記憶體一旦外洩即全員帳密曝光；且用 `===` 比對有時序側通道風險 |
| 3 | `jwt.sign({...}, 'my-secret-key')` | **硬編碼 JWT 密鑰** | 密鑰寫死在原始碼，任何能看到 repo 的人都能偽造任意使用者的 token（含 admin），完全繞過認證 |
| 4 | `res.json(result)` | **過度回傳 / 資訊洩漏** | 直接把整列（可能含 password_hash、內部欄位）回傳給前端 |
| 5 | login 成功後無 `else` | **帳號列舉 / 無錯誤處理** | 登入失敗不回應，攻擊者可用回應差異推斷帳號是否存在；缺 try/catch 也會讓 DB 錯誤訊息外洩 |
| 6 | （整體）JWT 無 `expiresIn` | **Token 永不過期** | 一次外洩的 token 永久有效，無法撤銷 |

---

## 任務 2：安全審查 Prompt 設計

### 設計的 Prompt

```
你是一位資深應用程式安全（AppSec）審查員。請依 OWASP Top 10 (2021) 逐項審查下面這段程式碼。

程式碼：
<在此貼上程式碼，請保留行號>

輸出要求：
1. 逐項對照 OWASP Top 10（A01 權限控制失效 … A10 SSRF），命中才列出，沒命中標「無」。
2. 每個發現用下列格式：
   - 【漏洞名稱】
   - OWASP 分類：Axx
   - 位置：第 N 行（引用該行程式碼）
   - 嚴重程度：Critical / High / Medium / Low（並說明評分理由：可利用性 × 影響）
   - 攻擊情境：攻擊者具體怎麼打（給一個 payload 範例）
   - 修復建議：具體到可直接改的程式碼
3. 最後給一個「依嚴重程度排序」的修復優先順序清單。
4. 若某處「疑似有問題但不確定」，標示【需人工確認】並說明不確定的原因，不要猜。
```

### 為什麼這樣設計

- **綁 OWASP Top 10**：強制框架化、避免漏項，而非自由發揮。
- **要行號 + 引用該行**：避免 Claude 泛泛而談，逼它指到具體位置。
- **要 payload**：驗證它真的理解可利用性，而非背名詞。
- **分級 + 評分理由**：讓結果可排優先序。
- **【需人工確認】出口**：降低幻覺與過度自信（延伸到 ex02 的信心程度設計）。

### 實際審查這段程式碼，Claude（本次）找到的

- SQL Injection（A03）— Critical：與我手動找的一致。
- 硬編碼密鑰（A02 / A05）— Critical。
- 明文密碼（A02）— High。
- **我原本較少強調、Claude 會額外點出的**：
  - **A09 紀錄與監控不足**：無任何登入失敗紀錄，暴力破解無法偵測。
  - **A07 認證失敗**：無速率限制 / 鎖定機制，可無限嘗試登入。
  - **JWT 無 `expiresIn` + 無 `algorithm` 鎖定**（`alg:none` 攻擊風險）。
  - 回傳 `result` 未挑欄位，屬 A01 資料過度曝露。

> 小結：工具/手動容易抓到「注入、密鑰、明文」這類有明確特徵的問題；Claude 擅長補「缺速率限制、缺紀錄、token 生命週期、欄位過度曝露」這類**設計面/缺失型**問題（沒有壞程式碼、而是缺好程式碼）。

---

## 任務 3：修復程式碼

對應 `fixed/app.py`（Python 實作），修復手法可直接對映回 Node.js：

### SQL Injection

- **做法**：一律參數化查詢。

  ```python
  conn.execute("SELECT id, username, role FROM users WHERE id = ?", (int(user_id),))
  ```

  Node（`mysql2`）等價：`db.query('SELECT ... WHERE id = ?', [userId])`。
- 另外把 `user_id` 強制轉型 `int()`，非數字直接拋錯。

### 密碼安全性

- **不存明文**：用 PBKDF2-HMAC-SHA256 + 每人隨機 16-byte salt、200,000 回合。

  ```python
  digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
  ```

  （生產環境可用 bcrypt / argon2id，原理相同。）
- **常數時間比對**：`hmac.compare_digest(...)` 防時序側通道。

### JWT / 密鑰安全性

- **密鑰移到環境變數**，缺少就報錯，絕不寫死：

  ```python
  key = os.environ.get("APP_SECRET_KEY")
  if not key: raise RuntimeError("缺少環境變數 APP_SECRET_KEY")
  ```

  Node 等價：`jwt.sign(payload, process.env.APP_SECRET_KEY, { expiresIn: '1h', algorithm: 'HS256' })`，並務必設定 `expiresIn` 與鎖定 `algorithm`。

### 其餘一併修復（見 fixed/app.py）

- 命令注入 → `shell=False` + 參數陣列 + 主機名白名單。
- 不安全反序列化 → `pickle` 改 `json`。
- `eval` → `ast.literal_eval`。
- 用 `assert` 做權限檢查 → 改顯式 `if ... raise PermissionError`（`python -O` 不會被移除）。

### 驗證結果

- `fixed/test_app.py`：**13 個 pytest 全數通過**（6 個功能正常 + 7 個注入/權限防護）。
- Bandit 問題數：**漏洞版 12 → 修復版 3**，HIGH 嚴重度 **3 → 0**（詳見 `../NOTES.md` 與 `../reports/`）。
