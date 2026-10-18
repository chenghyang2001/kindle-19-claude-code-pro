# 練習 02 解答 — 程式碼品質 Checklist 實戰

## 任務 1：10 項程式碼品質 Checklist（最危險在前）

> 可直接複製進 PR 模板。「自動」欄表示 `tools/quality_gate.py` 能自動抓到。

| # | 支柱 | 檢查項目 | 如何驗證 | 違反後果 | 自動 |
| --- | ------ | --------- | --------- | --------- | :---: |
| 1 | 安全 | - [ ] 所有 SQL 查詢使用參數化，不用 f-string／`+`／`%` 組字串 | grep `execute(f"`；寫含 `' OR '1'='1` 的 pytest | SQL 注入：資料外洩、毀表 | ✅ C1 |
| 2 | 安全 | - [ ] API Key／密碼／token 從環境變數或 secret manager 讀取，`.env` 已進 `.gitignore` | grep `api_key = "`；`git ls-files` 不應出現 `.env` | 機密外洩，需全面輪換金鑰 | ✅ C2 |
| 3 | 安全 | - [ ] 外部輸入都有驗證（型別、範圍、長度、格式） | 邊界測試：None、空字串、負數、超長字串、特殊字元 | 注入、崩潰、髒資料入庫 | — |
| 4 | 錯誤處理 | - [ ] 沒有裸 `except:` 或 `except: pass`，例外要記錄或重新拋出 | grep `except:`；檢查每個 except 區塊 | 靜默失敗，出事無從查起 | ✅ C4/C5 |
| 5 | 錯誤處理 | - [ ] 連線／檔案等資源用 `with` 或 `try/finally` 釋放 | 測試模擬例外後確認 `close()` 有被呼叫 | 連線耗盡、檔案鎖死 | — |
| 6 | 錯誤處理 | - [ ] 外部呼叫（HTTP、DB）有 timeout，並檢查回應狀態碼 | grep `requests.` 是否帶 `timeout=`；測非 200 回應 | 程式卡死、把錯誤回應當成功 | ✅ C6 |
| 7 | 錯誤處理 | - [ ] 邊界情況已處理：空集合、除以零、None | 測空輸入、零筆資料 | 正式環境 `ZeroDivisionError` 等崩潰 | — |
| 8 | 安全／維護 | - [ ] log 與錯誤訊息不含機密、個資、SQL 全文；用 `logging` 不用 `print` | 檢視 log 呼叫；grep `print(` | 機密寫進 log 外洩；無法控制 log 等級 | — |
| 9 | 維護 | - [ ] 沒有硬編碼路徑／主機／魔術數字，改用設定或具名常數 | grep `C:/Users`、IP、裸數字 | 換機器或環境就壞 | ✅ C3 |
| 10 | 維護 | - [ ] 有型別標註與 docstring、命名具體、函式 ≤ 30 行，且有對應測試 | `ruff`／`mypy`；pytest 覆蓋正常＋邊界＋錯誤三類 | 難讀難改，改壞也沒人發現 | — |

## 任務 2：套用到真實程式碼

`starter/` 原本不存在，所以自己寫了一個約 30 行的函式 `starter/order_report.py`（查客戶訂單 → 算平均 → POST 到報表 API），刻意保留常見缺陷。

### 1. 逐項標記

| # | 項目 | 結果 | 位置 / 說明 |
| --- | ------ | :---: | ------ |
| 1 | 參數化 SQL | ❌ 不通過 | L12 `f"... customer = '{customer}'"` |
| 2 | 機密從環境變數 | ❌ 不通過 | L5 `API_KEY = "sk-..."` |
| 3 | 輸入驗證 | ❌ 不通過 | `customer` 沒有任何檢查 |
| 4 | 無裸 except | ❌ 不通過 | L25 `except: pass` 吞掉所有錯誤（含 KeyboardInterrupt） |
| 5 | 資源釋放 | ❌ 不通過 | 連線從未 close |
| 6 | timeout + 狀態碼 | ❌ 不通過 | `requests.post` 無 timeout，`res` 從未檢查 |
| 7 | 邊界情況 | ❌ 不通過 | L17 沒訂單時 `total / len(rows)` → ZeroDivisionError |
| 8 | log 安全、用 logging | ❌ 不通過 | `print("sent", d)` 印出客戶資料；送出失敗也照印 sent |
| 9 | 無硬編碼路徑 | ❌ 不通過 | L6 `C:/Users/demo/shop.db` |
| 10 | 型別／命名／測試 | ❌ 不通過 | 無型別標註、`d`／`r`／`res` 命名含糊、無測試 |

10 項全部不通過（沒有「不適用」項）。

### 2. 問題清單

1. SQL 注入（L12）—— 最嚴重
2. API Key 硬編碼（L5）
3. `except: pass` 吞錯，送出失敗卻印「sent」並回傳成功（L25-27）
4. 零筆訂單除以零崩潰（L17）
5. HTTP 無 timeout、未檢查回應（L20）
6. DB 連線洩漏
7. 硬編碼使用者路徑（L6）
8. `customer` 無輸入驗證
9. 用 `print` 輸出客戶資料
10. 命名含糊、無型別、無測試

`tools/quality_gate.py` 實際掃描結果（自動抓到其中 6 項）：

```
starter\order_report.py:12: C1 SQL 字串組合
starter\order_report.py:5: C2 硬編碼機密
starter\order_report.py:6: C3 硬編碼使用者路徑
starter\order_report.py:25: C4 裸 except
starter\order_report.py:25: C5 except 後直接 pass
starter\order_report.py:20: C6 HTTP 呼叫沒有 timeout
掃描 1 個檔案，問題 6 個   (exit=1)
```

### 3. 修復最嚴重的問題：SQL 注入

```python
# 修復前
cur.execute(f"SELECT id, amount FROM orders WHERE customer = '{customer}'")
# 修復後
conn.execute("SELECT amount FROM orders WHERE customer = ?", (customer,))
```

理由：注入能直接讀取或刪除整個資料庫，影響最大，而攻擊者只要能控制 `customer` 參數就能發動。

修正版 `src/order_report.py` 也順手修掉其餘 9 項（金鑰改讀 `REPORT_API_KEY`、DB 路徑改讀 `SHOP_DB_PATH`、`try/finally` 關連線、零筆時 avg=0、HTTP 加 timeout 並檢查狀態、送出失敗記 log 後拋出、`print` 改 `logging`、加型別與具體命名）。報表送出改成可注入的 `sender`，測試不必連網。`starter/` 原檔保留不動，作為對照。

### 驗證結果（實際執行）

`python -m pytest -q tests/test_order_report.py` → **7 passed**

- 正常彙總：amy 2 筆、總額 400、平均 200
- 零筆訂單不會除以零
- 3 種注入字串（`' OR '1'='1`、`amy' --`、`x'; DROP TABLE orders; --`）都查到 0 筆，orders 表仍是 3 筆
- sender 拋錯時會往上傳，不被吞掉
- 缺 `SHOP_DB_PATH` 時明確報錯

修正版再跑品質閘門：`掃描 2 個檔案，問題 0 個 (exit=0)`

## 延伸思考：讓 checklist「不得不做」

靠人記一定會漏。做法是**把能自動化的項目變成擋路的機器檢查，人只審機器做不到的部分**：

1. **分層攔截，越早越便宜**
   - 編輯時：Claude Code `PreToolUse` hook 在 Write/Edit 前跑 `quality_gate.py`，命中就擋。
   - commit 時：pre-commit hook（範本 `templates/pre-commit-config.yaml`）跑閘門 + pytest，失敗就不能 commit。
   - PR 時：CI（範本 `templates/github-quality.yml`）再跑一次，搭配 branch protection 設為必過，本機用 `--no-verify` 也繞不過。
2. **自動化的項目從人工 checklist 拿掉**：10 項中有 6 項由閘門自動判定，人工只剩 4 項（輸入驗證、資源釋放、邊界、log 內容），短到真的會有人做。
3. **用正式工具取代 regex**：正式專案改用 `bandit`（安全）、`ruff`（含 `S` 安全規則）、`gitleaks`（機密掃描）、`mypy`，比自寫 regex 準、誤報少。
4. **PR 模板強制勾選**：剩下的人工項目放進 `.github/pull_request_template.md`，沒勾就不核准。
5. **測試即規格**：每個 checklist 項目對應一類測試（例如每個查詢函式都要有注入字串測試），覆蓋率門檻掛在 CI。
