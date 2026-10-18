# 個人 Prompt 庫（附錄 A 快速參考）

> 原題要求建在 `~/.claude/prompts/`；本次演練限制不改全域設定，所以放在專案內 `prompts/`。
> 搬到全域時整個資料夾複製過去即可，結構不變。

## 索引

| 分類 | 檔案 | 用途 | 變數 |
| --- | --- | --- | --- |
| code | [code/write-tests.md](code/write-tests.md) | 為函式產生正常/邊界/錯誤三類測試 | framework, function_code, module_path, behaviors |
| code | [code/refactor.md](code/refactor.md) | 行為不變的前提下重構 | language, goals, constraints, code |
| review | [review/code-review.md](review/code-review.md) | 依指定標準審查程式碼 | language, standards, context, code |
| review | [review/security-review.md](review/security-review.md) | 聚焦注入/XSS/機密的安全審查 | entry_points, threats, code |
| writing | [writing/explain-code.md](writing/explain-code.md) | 依聽眾調整深度解釋程式碼（✅ 已用 claude -p 實跑） | audience, purpose, length, code |
| writing | [writing/commit-message.md](writing/commit-message.md) | 依 diff 產生 commit message | convention, diff |
| debug | [debug/error-analysis.md](debug/error-analysis.md) | 從錯誤訊息推根因與解法 | error_message, code, input, environment, tried |
| debug | [debug/log-triage.md](debug/log-triage.md) | 從大段 log 找關鍵錯誤與時間線 | symptom, time_window, log |

追蹤效果：[evolution-log.md](evolution-log.md)

## 每個模板的固定格式
`# 名稱` → `## 用途` → `## 變數`（表格）→ `## 模板`（兩條 `---` 包住）→ `## 範例填入` → `## 預期輸出格式` → `## 使用說明` → `## 版本紀錄`

## 怎麼用
```bash
# 1. 看模板需要哪些變數
python tools/fill_prompt.py prompts/writing/explain-code.md --list-vars
# 2. 填變數（長內容用 --var-file 讀檔）
python tools/fill_prompt.py prompts/writing/explain-code.md \
  --var audience="不寫程式的產品經理" --var purpose="折扣怎麼算" --var length="250 字以內" \
  --var-file code=samples/order_utils.py > /tmp/prompt.txt
# 3. 丟給 Claude
claude -p "$(cat /tmp/prompt.txt)"
```
缺變數時 `fill_prompt.py` 會回 exit code 2 並列出缺哪些，不會把 `{{xxx}}` 原樣送出。

## 驗證
`python -m pytest tests/` 會檢查每個模板段落齊全、變數表與模板一致、README 有索引。
