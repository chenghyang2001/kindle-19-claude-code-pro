# 練習 02 解答 — 自動化安全審查流程

> 對應題目：`exercise-02-進階.md`。本專案已實作一個可跑的縮影：`.venv` + Bandit 對 `vulnerable/` 與 `fixed/` 各掃一次，pytest 驗注入防護（見 `../NOTES.md`）。

---

## 任務 1：靜態分析工具選擇（Python API + TypeScript 前端）

### 需安裝的工具與設定檔

| 層 | 工具 | 設定檔 | 角色 |
| ---- | ------ | -------- | ------ |
| Python 安全 | **Bandit** | `pyproject.toml` `[tool.bandit]` 或 `.bandit` | 掃 SQL 注入、eval、pickle、硬編碼密碼、subprocess |
| Python 相依 | **pip-audit**（或 safety） | — | 掃有已知 CVE 的套件版本 |
| Python 風格/型別（可選） | ruff + mypy | `pyproject.toml` | 間接減少 bug，非純安全 |
| TS/JS 安全 | **ESLint + eslint-plugin-security** | `.eslintrc`/`eslint.config.js` | 掃 `eval`、`child_process`、不安全正則、`innerHTML` |
| TS/JS 相依 | **npm audit**（或 `pnpm audit`） | — | node 相依 CVE |
| 祕密掃描 | **gitleaks**（或 detect-secrets） | `.gitleaks.toml` | 掃 commit 內的金鑰/token（跨語言） |
| SQL | 無標準工具 → **自定義** | 自寫 grep/規則：抓字串拼接 SQL、`f"...{}..."` 進 `execute` | 補工具盲區 |

### 執行順序（快的、廣的先跑，fail-fast）

```
1. gitleaks           # 最快，一有祕密外洩立即 Fail，省後面時間
2. 相依掃描           # pip-audit + npm audit（可平行）
3. 靜態安全掃描       # bandit + eslint-security（可平行）
4. 自定義 SQL 規則    # grep 規則
5. 測試               # pytest（含注入防護測試）
6. Claude 輔助審查    # 只對本次 diff，補工具盲區（見任務 2）
```

### Fail vs Warn 策略

| 條件 | 動作 |
| ------ | ------ |
| gitleaks 命中任何祕密 | **Fail** |
| Bandit `severity=HIGH`（任何信心）、或 `MEDIUM` 且 `confidence=HIGH` | **Fail** |
| pip-audit / npm audit 有 **High/Critical** CVE 且有修復版本 | **Fail** |
| ESLint security plugin `error` 等級規則 | **Fail** |
| 測試失敗（含注入防護測試） | **Fail** |
| Bandit `LOW`、或無修復版本的中低 CVE | **Warn**（記錄，不擋，排進技術債） |
| ESLint `warn` 等級 | **Warn** |

> 本專案實測印證此策略：`fixed/` 殘留 3 個 Bandit **LOW**（B404 import subprocess、B607 部分路徑、B603 subprocess 呼叫）——皆已用輸入白名單緩解，屬可接受的 Warn，不該擋合入。這正說明「只擋 HIGH / MED-HIGHconf」的門檻是對的。

---

## 任務 2：Claude 輔助審查的邊界

### 靜態分析工具擅長

- 有明確語法特徵的漏洞：`eval`、`pickle.loads`、`shell=True`、字串拼接 SQL、硬編碼密鑰。
- 快、可重複、可量化（問題數可當 CI 門檻）、零幻覺、覆蓋全檔。
- 相依 CVE 比對（查資料庫，Claude 記不全也會過時）。

### Claude 審查擅長

- **跨函式 / 跨檔的邏輯漏洞**：授權檢查漏在某條分支、先查後用的 TOCTOU。
- **缺失型問題**（沒有壞碼、而是缺好碼）：缺速率限制、缺紀錄、JWT 缺 `expiresIn`、缺錯誤處理。
- **業務邏輯漏洞**：可改價格、可越權看他人訂單——工具完全看不懂語意。
- **誤報判讀**：解釋某個 Bandit LOW 為何在此情境無害。

### 只有 Claude 能找到（工具找不到）

- IDOR / 水平越權（`/order/123` 改成別人的 id）。
- 認證流程設計缺陷（無鎖定、token 不過期、可列舉帳號）。
- 敏感資訊寫進日誌（工具不知道哪個變數算敏感）。
- 「這段其實不需要這個權限」這類最小權限判斷。

### 工具更準、Claude 可能漏報/誤報

- 相依套件 CVE（Claude 記憶會過時）。
- 大檔逐行掃描（Claude 可能跳讀遺漏）。
- 精確行號定位（Claude 偶爾飄行號）。
- 可重複性：同段碼 Claude 兩次結論可能不同；工具穩定。

### 「工具先跑、Claude 後審」工作流

```
diff → gitleaks → 相依掃描 → bandit/eslint → pytest
                         ↓ 產出機器報告（JSON）
          Claude 審查（只看本次 diff + 工具報告）
```

**Claude 的 Prompt 要補的工具盲區（明確寫進 prompt）：**

1. 「工具已掃過注入/密鑰類語法漏洞，**請把重心放在工具抓不到的**：授權/IDOR、業務邏輯、認證設計缺陷（速率限制、token 生命週期、帳號列舉）、敏感資料入日誌。」
2. 「附上的 Bandit LOW 報告，請逐條判定是**真問題**還是**此情境誤報**，並說明理由。」
3. 「跨函式追資料流：使用者輸入從哪進來、流到哪個危險匯點。」
4. 「每個發現標信心程度（見延伸思考），不確定的標【需人工確認】。」

---

## 任務 3：生產環境部署 10 項安全 Checklist

**認證與授權**

1. [ ] 所有需登入端點都有認證中介層；敏感操作額外做授權檢查（含水平越權 / IDOR 測試）。
2. [ ] 密碼用 bcrypt/argon2id + salt；登入有速率限制與帳號鎖定；JWT 設 `expiresIn` 並鎖定 `algorithm`。

**輸入驗證**
3. [ ] 所有外部輸入經 schema 驗證（Zod / Pydantic），型別/範圍/長度皆檢查。
4. [ ] SQL 全參數化；系統指令 `shell=False` + 白名單；上傳檔案限型別與大小。

**機密管理**
5. [ ] 無任何金鑰/密碼/token 寫在程式碼；全走環境變數 / Secret Manager。
6. [ ] `.env`、`credentials.json`、`token.json` 在 `.gitignore`；CI 跑 gitleaks。

**API 安全**
7. [ ] HTTPS 強制；CORS 白名單（非 `*`）；設安全標頭（CSP、HSTS、X-Content-Type-Options）。
8. [ ] 回應只回必要欄位（不漏 hash/內部欄位）；錯誤訊息不含堆疊/SQL；加全域速率限制。

**日誌（不洩漏敏感資訊）**
9. [ ] 記錄認證成敗、授權拒絕、異常，供監控/告警；但日誌中遮蔽密碼、token、PII。

**相依與流程**
10. [ ] CI 跑相依 CVE 掃描（pip-audit / npm audit）+ 靜態安全掃描，HIGH 阻擋合入；定期更新套件。

---

## 延伸思考：Claude 如何回報「不確定的安全問題」

**回報方式**：對每個發現附一個**信心等級 + 依據**，而非只給是/否。

建議 Prompt 加上：

```
每個發現標註信心程度，三選一並附一句理由：
- 【高信心】有明確可利用證據（給 payload）
- 【中信心】程式碼有風險特徵，但要看呼叫端/設定才能確定可利用
- 【需人工確認 / 低信心】疑似問題，但缺上下文，說明「需要看到什麼才能定論」
嚴禁：為了多列而猜；不確定就明說不確定，不要假裝確定。
```

**為什麼**：安全審查最怕兩種失敗——**漏報**（高信心沒抓到）與**狼來了**（一堆低信心誤報讓人麻痺）。分級讓人類審查者能先處理高信心、對「需人工確認」投入眼球、並要求 Claude 說出「還需要什麼資訊」而不是硬猜，直接壓低幻覺。
