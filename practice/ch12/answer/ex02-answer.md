# 練習 02 解答 — 信件重要度評分擴充

> 本解答不只是偽程式碼，已實作在 `legacy/` 並跑過測試：
> `legacy/email_scorer.py`（新增）、`email_filter.py`、`telegram_briefer.py`、`run_briefing.py`、`gmail_fetcher.py`（修改）、`legacy/tests/test_pipeline.py`（15 個測試，全過）。

## 任務 1：評分邏輯

### Schema（實際程式碼）

```python
@dataclass
class EmailScore:
    score: int                       # 1-5
    reasons: list[str]               # 為什麼給這個分數
    requires_reply: bool = False
    deadline: str | None = None      # 抓到的截止日原文，例如 "2026-10-20"、"今天 17:00"

    @property
    def is_urgent(self) -> bool:     # 4-5 分 → 緊急
        return self.score >= 4
```

### 計分規則（基礎 1 分，累加後夾在 1-5）

| 維度 | 判斷方式 | 加分 |
| ------ | --------- | ----- |
| 重要聯絡人 | `sender` 在 `VIP_SENDERS` | +1 |
| 緊急關鍵字 | 主旨含 urgent / ASAP / 緊急 / 重要（不分大小寫） | +2 |
| 需要回覆 | 主旨或內文含 `?`／`？`、「請確認」「請回覆」「可以嗎」「是否」等 | +1 |
| 有截止日 | regex：`YYYY-MM-DD`、`今天 HH:MM`、`今天下班前`、`下週X`、`明天` | +1 |
| 長信 | 內文 ≥ 80 字（中文以字元計） | +1 |
| 有附件 | `has_attachment is True` | +1 |

設計理由：緊急關鍵字是寄件人自己標的訊號，權重最高（+2）；其他維度各 +1，避免單一訊號就衝到 5 分。

### 範例資料實際評分

| 信件 | 分數 | 原因 |
| ------ | ----- | ------ |
| boss：URGENT Q3 報告 | 5 | 重要聯絡人、緊急關鍵字、需要回覆、截止今天 17:00、附件 |
| alice：合約草稿確認 | 5 | 重要聯絡人、需要回覆、截止 2026-10-20、附件 |
| ceo：重要：董事會簡報 | 5 | 重要聯絡人、緊急關鍵字、需要回覆、截止下週一、附件 |
| bob：午餐要不要一起 | 2 | 需要回覆（問號） |

## 任務 2：整合方案

### 1. 在哪個步驟加入評分？

**filter 之後、summarizer 之前。**

- 在 filter 之後：垃圾信、促銷信不值得花力氣評分。
- 在 summarizer 之前：可以用 `min_score` 先丟掉低分信，減少要摘要的封數（真實版摘要是付費 API，這樣能省錢）；也能依分數排序，讓摘要與簡報都照重要度排列。

```
fetch_emails → filter_and_score(min_score) → summarize_all → create_pages
                                                          └→ send_briefing（一般簡報 + 緊急通知）
```

### 2. `email_filter.py` 的修改

保留原本的 `filter_emails()` 不動（向下相容），新增：

```python
def filter_and_score(emails, min_score=1):
    scored = []
    for email in filter_emails(emails):
        result = score_email(email)
        if result.score >= min_score:
            scored.append({**email, "score": result})   # 不改原 dict，複製後加欄位
    return sorted(scored, key=lambda e: e["score"].score, reverse=True)
```

另外把 `email["labels"]` 改成 `email.get(...)`，缺欄位不會 `KeyError`。

### 3. `telegram_briefer.py` 顯示評分

每封信前面加星等，有截止日就加一行 ⏰；沒有 `score` 欄位時維持舊格式（`--no-score` 時輸出與擴充前一致）：

```
📬 今日信件簡報（4 封）
1. ⭐⭐⭐⭐⭐ URGENT: Q3 報告今天下班前要交 — boss@acme.com
   請在今天 17:00 前把 Q3 報告寄給我，可以嗎
   ⏰ 截止：今天 17:00
...
4. ⭐⭐ 午餐要不要一起 — bob@team.com
   中午要一起吃飯嗎
```

### 4. 4-5 分觸發緊急通知

`send_briefing()` 會把 `is_urgent` 的信另外組成獨立訊息（真實版是另發一則 Telegram，可設 `disable_notification=False` 讓手機響鈴；一般簡報可設靜音）：

```
🚨 緊急信件（5/5）
寄件人：boss@acme.com
主旨：URGENT: Q3 報告今天下班前要交
摘要：請在今天 17:00 前把 Q3 報告寄給我，可以嗎
截止：今天 17:00｜需要回覆
原因：重要聯絡人、主旨含緊急關鍵字、需要回覆、有截止日：今天 17:00、有附件
```

示範版寫到 `output/telegram_urgent.txt`，不會真的送出。

### 命令列

```bash
cd legacy
PYTHONUTF8=1 python run_briefing.py               # 評分版
PYTHONUTF8=1 python run_briefing.py --min-score 3 # 只看 3 分以上
PYTHONUTF8=1 python run_briefing.py --no-score    # 擴充前行為
PYTHONUTF8=1 python -m pytest tests -q            # 15 passed
```

## 延伸思考：規則 vs. 用 Claude API 評分

| 面向 | 規則式（目前實作） | Claude API |
| ------ | ------------------ | ----------- |
| 準確度 | 只看表面訊號；「我們再約時間？」也算需要回覆；VIP 名單要手動維護 | 能理解語意與語氣，例如客氣但其實很急的信 |
| 可解釋性 | `reasons` 清楚、可測試、結果固定 | 可要求輸出理由，但同一封信每次結果可能略有不同 |
| 延遲 | 每封 < 1 毫秒 | 每封約 1-3 秒；20 封串行約 20-60 秒，並行 5 條約 5-12 秒 |
| 成本 | 0 | 以 Haiku 估算：每封約 500 輸入 token＋100 輸出 token，約 $0.0008／封；每天 50 封約 $0.04，一個月約 $1.2（實際價格以官方價目表為準） |
| 隱私 | 信件不離開本機 | 信件內容會送到外部 API |
| 失敗模式 | 不會因網路失敗 | 需處理逾時、429、JSON 解析失敗 |

**建議做法：混合式。** 先用規則評分；只有落在 2-3 分的「灰色地帶」信件再送 Claude 判斷，並設好逾時，失敗就退回規則分數。這樣大部分信件零成本，只有少數模糊的信才付 API 費用。

範本（未執行，需要 `ANTHROPIC_API_KEY`，依使用者規則不設全域環境變數）：

```python
import json, anthropic
def score_with_claude(email, fallback):
    client = anthropic.Anthropic()  # 從獨立腳本的 .env 讀 key
    try:
        resp = client.messages.create(
            model="claude-haiku-5-5", max_tokens=200, timeout=10,
            messages=[{"role": "user", "content":
                "為這封信評 1-5 分重要度，只回 JSON："
                '{"score":int,"reasons":[str],"requires_reply":bool,"deadline":str|null}\n\n'
                f"寄件人：{email['sender']}\n主旨：{email['subject']}\n內文：{email['body'][:2000]}"}])
        data = json.loads(resp.content[0].text)
        return EmailScore(**data)
    except (anthropic.APIError, json.JSONDecodeError, TypeError, KeyError):
        return fallback   # 失敗退回規則分數
```
