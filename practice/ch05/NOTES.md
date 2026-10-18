# 第 5 章演練筆記（快速模式）

> 快速 demo 模式：主 Claude 直接寫檔，未經 code-writer／QA／reviewer 三 agent 流程。
> 環境：Windows 10、Python 3.14.3、pandas 3.0.3、Flask 3.1.3、pytest 8.4.2。

## 做了什麼

### 練習 01 — Stack Trace 解讀

1. **自己做出會噴 stack trace 的程式**：`ex01/buggy/main.py` + `processor.py`，行號刻意對齊題目（main.py:23、processor.py:45、processor.py:12），餵 `ex01/data/sample.csv`（混了一筆 `2024/01/15`）。
2. **實際執行取得真實 traceback**，存到 `ex01/traceback-before.txt`。
3. **修復**：`ex01/fixed/processor.py` 的 `parse_date` 支援 `YYYY-MM-DD`、`YYYY/MM/DD`、`DD-MM-YYYY`，解析失敗或空值時回 None 並 log 警告。
4. **測試**：`ex01/fixed/test_processor.py`，再用 `ex01/data/messy.csv`（6 種狀況）實跑。輸出存到 `ex01/run-after.txt`。
5. 解答：`answer/ex01-answer.md`。

### 練習 02 — 系統化 Debug 流程

1. **Debug checklist**：10 個步驟（題目要求至少 8 個），每步含「怎麼做」與「有發現 → 下一步」。
2. **`@log_request` decorator**：`ex02/request_logger.py`，記錄方法／路徑／參數／毫秒／狀態碼；例外時記完整 traceback 再 re-raise；額外加了敏感欄位遮蔽與抽樣（`make_log_request(sample_rate, slow_ms)`）。
3. **示範 API**：`ex02/app.py`，刻意放一個「舊資料沒有 email → KeyError → 500」的 bug，再加一個會吞掉錯誤的全域 error handler，重現題目「log 只有 Internal Server Error」的情境；並保留一個沒套 decorator 的 `/legacy/...` route 做對照。
4. **真實伺服器驗證**：`python app.py 5055 server.log` 啟動、curl 打 6 種請求，log 存成 `ex02/server-run.log`。
5. **測試**：`ex02/test_request_logger.py`。
6. 解答（含延伸思考：每分鐘 1 萬次的 logging 問題與採樣設計）：`answer/ex02-answer.md`。

## 驗證結果

| 項目 | 指令 | 結果 |
| --- | --- | --- |
| 重現 bug | `cd ex01/buggy && python main.py` | exit 1，`ValueError: time data '2024/01/15' does not match format '%Y-%m-%d'` ✅ |
| 修復後跑 sample.csv | `cd ex01/fixed && python main.py` | exit 0，3 筆全部解析成功 ✅ |
| 修復後跑 messy.csv | `python main.py ../data/messy.csv` | exit 0，3 筆成功、3 筆 NaT＋3 行 WARNING，沒有中斷 ✅ |
| 練習 01 測試 | `python -m pytest test_processor.py` | **17 passed** ✅ |
| 練習 02 測試 | `cd ex02 && python -m pytest test_request_logger.py` | **11 passed** ✅ |
| 真實伺服器 | curl 6 種請求 | 沒套 decorator 的 500 只有一行 access log；套了之後印出完整 `KeyError: 'email'` traceback；404 記 WARNING；密碼顯示為 `***` ✅ |

重跑方式（Git Bash）：

```bash
export PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1
(cd ex01/buggy && python main.py)                 # 預期噴 traceback
(cd ex01/fixed && python main.py ../data/messy.csv && python -m pytest -q)
(cd ex02 && python -m pytest -q)
```

## 和題目要求的差異

1. **真實 traceback 比題目多了 9 層**：中間夾著 7 層 pandas 內部框架、2 層 `_strptime` 標準庫框架；錯誤訊息用單引號 `'2024/01/15'`（題目用雙引號）。自己專案的三層（23 / 45 / 12 行）與題目完全一致。
2. **存檔的 traceback 與 log 已把本機使用者路徑換成 `~`**，並移除終端機色碼（遵守不硬編碼使用者路徑的規則），所以和終端機上看到的略有不同。
3. **`parse_date` 額外處理空值、非字串、前後空白**，題目沒要求；刻意不支援 `MM-DD-YYYY`（與 `DD-MM-YYYY` 無法區分）。
4. **decorator 額外功能**：敏感欄位遮蔽、`abort()` 類 HTTP 錯誤分開處理、抽樣與慢請求門檻。延伸思考題原本只要求「思考」，這裡把基本採樣直接實作並測試；request-id 一致性採樣、非同步 QueueHandler、metrics 系統只寫在解答中，未實作。
5. **Debug checklist 是 10 步**（題目要求至少 8 步）。checklist 本身是文件，沒有逐步實際執行；其中第 1～3、5 步在本練習的示範 API 上實際走過（重現 → 找到吞錯的 handler → 取得 traceback → 發現資料缺欄位）。
6. **沒有用到外部帳號／付費服務**，所以沒有只寫範本的部分。Flask 用的是開發伺服器，非正式環境的 gunicorn。
7. 沒有建 GitHub repo、沒有 push（依指示），只在本機 commit。
