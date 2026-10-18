# NOTES — K19 第 16 章（附錄 A 快速參考提示詞庫）演練紀錄

> 快速 demo 模式（專案 CLAUDE.md 已指定），未經 code-qa / code-reviewer 審查。

## 做了什麼
| 項目 | 產出 |
| --- | --- |
| 練習 01：5 個場景模板 + 共同模式 | `answer/ex01-answer.md`；完整模板在 `prompts/` |
| 練習 02：Prompt 庫結構 + 進化機制 + 版本控制 | `answer/ex02-answer.md`、`prompts/README.md`、`prompts/evolution-log.md` |
| 本章補充：提示詞庫 | `prompts/` 4 分類 × 2 = 8 個模板，每檔含用途、變數佔位、範例、預期輸出、版本紀錄 |
| 填變數工具 | `tools/fill_prompt.py`（`--var` / `--var-file` / `--list-vars`，缺變數 exit 2） |
| 自動驗證 | `tests/test_prompts.py` |
| 範例素材 | `samples/order_utils.py`（刻意留空清單除以零與折扣無上限） |
| 實跑紀錄 | `runs/explain-code.prompt.txt`（送出的 prompt）、`runs/explain-code.output.md`（Claude 回覆） |

## 驗證結果
1. `python samples/order_utils.py` → `total = 225.0`、`avg = 75.0`；`average_price([])` → `ZeroDivisionError`（當作除錯模板的真實錯誤訊息）。
2. `python -m pytest tests/ -q` → **21 passed**（8 個模板結構 + 8 個 README 索引 + 分類數量 + fill 的正常/邊界/錯誤 4 案）。
3. `fill_prompt.py --list-vars` 正確列出 4 個變數；只給 1 個變數時輸出「錯誤：缺少變數 'purpose, length, code'」、exit 2。
4. **`claude -p` 實跑**：先 `unset` 所有 `CLAUDE*` 環境變數（確認剩 0 個），`timeout 120 claude -p "$(cat runs/explain-code.prompt.txt)"` → exit 0、約 31 秒。
   - 三段小標題完全照模板 ✅
   - 用 100×2 + 50×1、打九折 = 225 元走一遍，和程式實際輸出一致 ✅
   - 主動指出「折扣填 150 會變負數」「平均單價沒考慮數量」 ✅
   - 長度約 285 字（含標點，中文字 164），略超 250 上限 ⚠️ → 已記入 `prompts/evolution-log.md`

## 與題目要求的差異
- **路徑**：練習 02 要求 `~/.claude/prompts/`，因限制「不修改全域 `~/.claude/`」改建在專案內 `prompts/`，結構相同。
- **格式加強**：題目格式只有「用途 / 模板 / 使用說明」，我多加「變數表、範例填入、預期輸出格式、版本紀錄」，讓進化機制有地方記版本，測試也能檢查變數一致性。
- **slash command**：只在 ex02 寫做法，沒有寫入 `~/.claude/commands`（依限制）。
- **實跑範圍**：只用 `claude -p` 實跑 1 個模板（explain-code）；其餘 7 個只驗證結構與填變數，沒有逐一送給 Claude。
- **團隊版本控制**：屬延伸思考，只寫設計；「黃金測試」需要額度，未實作。
- 沒有 push、沒有建 GitHub repo。
