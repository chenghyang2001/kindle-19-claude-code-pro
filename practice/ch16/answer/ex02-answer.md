# 練習 02 解答 — 個人化 Prompt 庫 + Prompt 進化機制

## 任務 1：Prompt 庫結構

> 題目要求 `~/.claude/prompts/`；本次限制不可修改全域 `~/.claude/`，所以建在專案內 `prompts/`，結構完全相同，之後整包複製到 `~/.claude/prompts/` 即可。

```
prompts/
  README.md            — 索引（用途、變數、使用方式）
  evolution-log.md     — 效果追蹤紀錄（任務 2）
  code/
    write-tests.md     — 產生正常/邊界/錯誤三類測試
    refactor.md        — 行為不變的重構
  review/
    code-review.md     — 依指定標準審查
    security-review.md — 注入/XSS/機密審查
  writing/
    explain-code.md    — 依聽眾解釋程式碼（已實跑）
    commit-message.md  — 依 diff 寫 commit message
  debug/
    error-analysis.md  — 錯誤訊息 → 根因 → 解法
    log-triage.md      — 大段 log → 關鍵錯誤 + 時間線
tools/fill_prompt.py   — 填變數工具（缺變數 exit 2）
tests/test_prompts.py  — 結構驗證（21 個測試）
```

每檔格式（比題目多了「變數」「範例填入」「預期輸出格式」「版本紀錄」四段）：
```markdown
# Prompt 名稱
## 用途
## 變數        ← 表格：變數 / 說明 / 範例
## 模板
---
[Prompt 內容，含 {{變數}}]
---
## 範例填入
## 預期輸出格式
## 使用說明
## 版本紀錄    ← v1（日期）初版；vN 改了什麼、為什麼
```

**怎麼在 Claude Code 裡快速存取**
- 直接：`@prompts/review/code-review.md` 引用，再口頭給變數。
- 腳本化：`claude -p "$(python tools/fill_prompt.py prompts/writing/explain-code.md --var ... --var-file code=xxx.py)"`
- 進一步：把常用的做成 slash command（`.claude/commands/*.md`，用 `$ARGUMENTS`）。本次限制不寫入 `~/.claude/commands`，此項只列做法未實作。

## 任務 2：Prompt 進化機制

實作於 `prompts/evolution-log.md`。

### 1. 如何記錄效果
每次正式使用後追加一列，三個欄位就夠：
| 欄位 | 定義 |
| --- | --- |
| 命中（1–5） | 有沒有回答我真正想問的 |
| 格式（是/否） | 有沒有遵守「預期輸出格式」 |
| 修改次數 | 拿到結果後還追問/手改幾次 |

另加「問題觀察」「決定」兩欄，記下為什麼要不要改。

**第一筆真實紀錄**（`explain-code` v1，`claude -p` 實跑）：命中 5、格式 是、修改 0；但長度約 285 字（含標點），超出「250 字以內」。

### 2. 什麼時候要優化
- 同一模板連續 2 次命中 ≤ 3，或格式「否」
- 修改次數平均 ≥ 2
- 換模型後表現明顯變差
- 有一個固定缺點反覆出現（如上面的長度超標）→ 再出現一次就改

### 3. 優化方向
| 症狀 | 方向 | 例子 |
| --- | --- | --- |
| 答非所問、太泛 | 調整角色 / 補背景 | 「工程師」→「負責電商金流的資深工程師」 |
| 格式亂 | 更嚴格格式 | 直接給輸出範本、限制小標題數量 |
| 品質不穩 | 加範例（few-shot） | 附一個「好的審查意見」範例 |
| 做太多、太長 | 加約束 | 「嚴格 250 字（含標點），超過就刪注意事項」 |

一次只改一個方向，才知道是哪個改動有效。

## 延伸思考：團隊共用的 Prompt 版本控制

1. **放進 git repo**（例如 `team-prompts/`），每個模板就是一個 .md，改動走 PR，review 時附「改版前後輸出對照」。
2. **檔內版本號 + CHANGELOG**：模板 frontmatter 或「版本紀錄」段落寫 `v2`；破壞性改動（變數改名、輸出格式改變）升主版號，因為依賴輸出格式的腳本會壞。
3. **自動檢查（CI）**：像本專案的 `tests/test_prompts.py`，確認段落齊全、變數表和模板一致、README 有索引；可再加「黃金測試」——固定輸入跑 `claude -p`，檢查輸出包含必要標題（需 API 額度，可設成手動觸發）。
4. **擁有者**：每個分類指定 owner（CODEOWNERS），避免大家各改各的。
5. **效果紀錄共享**：evolution-log 放同一 repo，大家都往裡記，決定改版時有數據。
6. **個人覆寫**：團隊版放 `team-prompts/`，個人微調放 `~/.claude/prompts/`，同名時個人版優先，不污染團隊版。
