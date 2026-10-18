# NOTES — K19 第 12 章練習（快速 demo 模式）

## 做了什麼

1. **自建「現有系統」**：題目要分析的 `email-automation-演練/` 不在 repo 裡，所以在 `legacy/` 建了同名模組的小型 pipeline：
   `gmail_fetcher`（讀 CSV）→ `email_filter` → `summarizer`（規則式取首句）→ `notion_creator`（寫 JSON）→ `telegram_briefer`（寫 txt）→ `run_briefing` 串接。
   範例資料 `legacy/data/emails.csv` 有 7 封信（老闆、客戶、CEO、同事、促銷、GitHub 通知、垃圾信）。
   原版先跑一次確認可用，並單獨 commit（`79a35d9`）留作對照。
2. **練習 01**：資料流圖（Mermaid + 文字）、每段輸入／輸出／失敗點表、效能／可靠性／新功能改進建議 → `answer/ex01-answer.md`。
3. **練習 02**：實作評分擴充，不只寫偽程式碼：
   - 新增 `legacy/email_scorer.py`（`EmailScore` dataclass + 6 個評分維度 + 截止日擷取）
   - `email_filter.py` 新增 `filter_and_score()`（評分、`min_score` 門檻、依分數排序）
   - `telegram_briefer.py` 顯示星等與截止日；4-5 分另組「🚨 緊急信件」訊息
   - `run_briefing.py` 加 `--no-score`、`--min-score`、`--csv` 參數，Notion 失敗不擋 Telegram，抓信失敗 exit 1
   - `gmail_fetcher.py` 加欄位驗證與 `FetchError`
   - 設計說明、規則 vs. Claude API 比較 → `answer/ex02-answer.md`
4. 新增 `.gitignore`（排除 `output/`、`__pycache__/`、`.pytest_cache/`）。

## 驗證結果（實際執行）

| 項目 | 指令 | 結果 |
| ------ | ------ | ------ |
| 原版 pipeline | `python run_briefing.py`（commit 79a35d9） | 抓到 7 封、保留 4 封，簡報正常輸出 |
| 擴充版 pipeline | `python run_briefing.py` | 保留 4 封，依分數排序（5/5/5/2），3 封觸發緊急通知 |
| 向下相容 | `python run_briefing.py --no-score` | 輸出與原版相同格式，無星等、無緊急通知 |
| 錯誤路徑 | `python run_briefing.py --csv nope.csv` | 印出「錯誤：找不到信件來源：nope.csv」，exit code 1 |
| pytest | `python -m pytest tests -q`（在 `legacy/`） | **15 passed**（正常 4、邊界 7、錯誤 2、整合 2） |

## 和題目要求的差異

- **分析對象是自建的示範版**，不是原書的 `email-automation-演練/`。模組名稱與資料流相同，但內容是簡化版，所以 ex01 的失敗點分析一部分是針對「真實版會怎樣」推論的。
- **外部服務全部本地模擬**：Gmail 改讀 CSV、Notion 寫 `output/notion_pages.json`、Telegram 寫 `output/telegram_message.txt`／`telegram_urgent.txt`。沒有連任何真實帳號，也沒有送出任何訊息。真實串接只在答案裡寫了範本（Gmail API／Notion／Telegram／Claude API），未執行。
- **summarizer 用規則（取第一句）**，不是呼叫 Claude API。
- **練習 02 題目只要偽程式碼**，這裡直接做成可執行程式並加上 pytest。
- 「延伸思考」的成本數字是估算，以官方價目表為準。

## 已知限制（快速模式，未經 QA／審查）

- 評分分布偏高：範例 4 封有 3 封拿 5 分，因為 VIP 寄件人的信通常同時有附件、問號、截止日。正式使用要用更多真實信件調整權重或門檻。
- 「需要回覆」只看問號與關鍵字，容易誤判（例如反問句）。
- 截止日只抓原文字串，沒有轉成日期，也無法判斷是否已過期。
- `labels` 只比對整個字串，多標籤信件會漏判（ex01 已列為改進點，未修）。
- VIP 名單寫死在程式碼裡，正式版應放設定檔。
