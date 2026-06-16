# 練習 03 解答 — 大規模重構計畫

## 1. 程式碼掃描結果（email-automation-演練/）

### 函式長度 > 30 行

| 檔案 | 函式 | 行數 |
|------|------|------|
| run_briefing.py | `main` | 106 行 |
| run_briefing.py | `_fetch_emails_today` | 70 行 |
| notion_creator.py | `_create_via_subprocess` | 70 行 |
| telegram_briefer.py | `format_briefing` | 67 行 |
| summarizer.py | `_parse_deadline` | 57 行 |
| notion_creator.py | `_create_via_api` | 53 行 |
| gmail_fetcher.py | `fetch_emails_today` | 50 行 |
| summarizer.py | `summarize_email` | 39 行 |
| email_filter.py | `_ai_judge_via_subprocess` | 38 行 |

### 重複邏輯

- `notion_creator._create_via_api` / `_create_via_subprocess`：兩者建構相同的 payload，只差在呼叫方式
- `run_briefing._fetch_emails_today` 與 `gmail_fetcher.fetch_emails_today`：功能重複，各維護一份
- `summarizer._summarize_via_api` / `_summarize_via_subprocess` 與 `notion_creator._create_via_api` / `_create_via_subprocess`：「雙實作 pattern」在兩個模組都重複

---

## 2. 優先級評估

| 問題 | 影響程度 | 重構難度 | 優先級得分 |
|------|---------|---------|----------|
| `notion_creator` API/subprocess 雙實作重複 | 4 | 2 | 2.00 |
| `run_briefing._fetch_emails_today` 與 `gmail_fetcher` 重複 | 4 | 2 | 2.00 |
| `run_briefing.main` 106 行，職責混雜 | 5 | 3 | 1.67 |
| `format_briefing` 67 行，格式與發送混在一起 | 3 | 2 | 1.50 |
| `_parse_deadline` 57 行，多種日期格式解析密集 | 3 | 3 | 1.00 |

---

## 3. 重構執行計畫（前 3 優先）

### #1：消除 notion_creator 的雙實作重複（得分 2.00）

- **手法**：Extract 共用的 payload 建構邏輯為 `_build_notion_payload()`，兩個實作函式各自只保留呼叫差異
- **先加測試**：mock API 回傳、mock subprocess 回傳各一個，確認輸出格式一致
- **預估時間**：30 分鐘
- **預期改善**：減少約 40 行重複碼；日後改 payload 格式只需改一處

### #2：刪除 run_briefing 中的重複 fetch 邏輯（得分 2.00）

- **手法**：Remove Duplicate → 刪除 `run_briefing._fetch_emails_today`，直接呼叫 `gmail_fetcher.fetch_emails_today`
- **先加測試**：確認兩者回傳格式完全一致（欄位名稱、型別）
- **預估時間**：20 分鐘
- **預期改善**：修 Gmail 抓取 bug 只需改一個地方

### #3：拆解 run_briefing.main 106 行（得分 1.67）

- **手法**：Extract Function → 拆出 `fetch_stage()`、`filter_stage()`、`summarize_stage()`、`notify_stage()`
- **先加測試**：整合測試覆蓋完整 pipeline（mock 外部服務）
- **預估時間**：60 分鐘（最複雜）
- **預期改善**：每個 stage 可獨立測試、獨立替換實作

---

## 4. 風險評估

**最危險的改動**：拆解 `run_briefing.main`

原因：`main` 內部有隱性的狀態共享（`cache`、`errors` 清單在 main 內部流轉）。提取子函式時若沒把這些狀態作為參數傳入，會靜默失敗（不拋出例外，只是不 cache）。

**降低風險的方式**：
1. 先加端對端測試覆蓋完整 pipeline（含 cache 行為驗證）
2. 每提取一個 stage 函式就立刻跑全測試，不要一次全部提取
3. 明確把 `cache`、`errors` 作為回傳值或參數傳遞，不依賴閉包共享狀態
