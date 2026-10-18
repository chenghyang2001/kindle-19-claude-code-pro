# NOTES — K19 第 6 章練習（測試）

> 快速 demo 模式：主 Claude 直接寫檔，未經 code-writer / QA / reviewer 流程。

## 做了什麼

| 項目 | 檔案 |
|---|---|
| 練習 01 目標函式 | `src/pm25.py` |
| 練習 01 測試（6 題 + 1 補充） | `tests/test_pm25.py` |
| 練習 02 starter 函式（自建） | `starter/alert_level.py` |
| 提示詞模板 | `prompts/generate-tests-template.md` |
| 填好的提示詞 / Claude 原始輸出 | `prompts/filled-prompt-alert-level.md`、`prompts/outputs/claude-raw-output.md` |
| Claude 生成的測試（未修改） | `tests/test_alert_level_generated.py` |
| 人工補充測試 | `tests/test_alert_level_supplement.py` |
| 突變測試工具 | `tools/mutation_check.py` |
| 延伸思考：mock 示範 | `starter/room_alert_service.py`、`tests/test_room_alert_service_mock.py` |
| 解答 | `answer/ex01-answer.md`、`answer/ex02-answer.md` |

## 驗證結果（Python 3.14.3、pytest 8.4.2、Windows 10）

執行：`PYTHONUTF8=1 python -m pytest -q`

| 測試檔 | 結果 |
|---|---|
| `tests/test_pm25.py` | 8 passed |
| `tests/test_alert_level_generated.py`（Claude 生成） | 39 passed |
| `tests/test_alert_level_supplement.py` | 5 passed |
| `tests/test_room_alert_service_mock.py` | 4 passed |
| **全部** | **56 passed, 0 failed** |

突變測試：`PYTHONUTF8=1 python tools/mutation_check.py` → **10/10** 突變被生成的測試抓到，執行後原檔自動還原。

## 和題目要求的差異

1. **`starter/` 原本不存在**：練習 02 要求「為 starter/ 中的一個函式生成測試」，但 repo 沒有這個目錄，所以自建 `starter/alert_level.py`（含分支、門檻、例外，夠複雜才有評估意義）。
2. **生成測試是真的呼叫 Claude Code**：用 `claude -p`（Max 訂閱，不用 API Key）跑填好的模板，不是自己寫了假裝是生成的。輸出原封不動保存。
3. **練習 01 多加一個測試**：補了「區間外一點點（-0.01、500.01）要被排除」的參數化測試，所以是 8 個不是 6 個。
4. **練習 01 第 3 題「Error case」**：函式本身對空清單不拋例外，所以測試驗證的是「回傳 0.0 且不拋 ZeroDivisionError」，跟題目描述一致。
5. **評估多了突變測試**：題目只要主觀評分，這裡另外用突變測試量化第 4 項「是否真的驗證行為」。
6. **延伸思考有實作**：除了文字回答，額外寫了依賴注入 + `unittest.mock` 的可執行示範。沒有連任何真實 DB / API，不需要帳號或 token。

## 已知沒處理的風險

- `classify_alert_level` 的浮點四捨五入不一致（15.45→15.4、35.45→35.5）只用測試記錄現況，沒有改函式。
- `min_valid_ratio` 傳非數字時的錯誤訊息不友善，同樣只記錄。
- 突變測試是手寫的 10 種，不是 mutmut 之類的完整工具。
