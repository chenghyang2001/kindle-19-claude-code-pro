# 練習 02 解答 — 設計 Sub-agent 合約

> 合約檔：`contracts/research_output.schema.json`（研究端，嚴格）、`contracts/writer_input.schema.json`（寫作端，寬鬆）
> 驗證：`.venv/Scripts/python src/contract.py contracts/research_output.schema.json samples/research_valid.json`
> 情境模擬：`cd src && ../.venv/Scripts/python ex02_orchestrator.py`；測試：`.venv/Scripts/python -m pytest tests`

## 任務 1：資料合約

### 研究 agent 輸出（ResearchOutput，簡化說明）

```text
{
  contract_version: string  必填  "1.x"，主版號不同即不相容
  status:           enum    必填  ok | empty | error
  topic:            string  必填  3~200 字
  generated_at:     string  必填  ISO 8601 date-time
  findings: [               ok 時必填且 ≥1 筆；empty 時必須是 0 筆；最多 10 筆
    {
      title:      string   必填  1~120 字
      key_points: string[] 必填  1~5 點
      sources:    [{url 必填(http/https), title 選填, published 選填(date)}]  必填 ≥1
      confidence: number   必填  0~1
      tags:       string[] 選填  不可重複
    }
  ]
  summary:  string  選填 ≤1000 字
  error:    {code: NETWORK|TIMEOUT|RATE_LIMIT|INTERNAL, message, retryable: bool}  error 時必填
  attempts: int     選填 1~5
}
不允許額外欄位（additionalProperties: false）
```

重點設計：

- **用 `status` 當信封**：失敗、空結果、成功都走同一個合約，寫作端不用猜「沒回應」是什麼意思。
- **用 `if/then` 做條件必填**：`status=ok` 才要求 findings，`status=error` 才要求 error 物件。
- **每筆發現都要有來源和可信度**，寫作端才能決定引用強度。

### 寫作 agent 的輸入期望（WriterInput）

- 只要求 `topic` 與 `findings[].title`、`findings[].key_points`。
- `sources`、`confidence` 選填；`confidence` 缺失時用 0.5 當預設。
- **允許額外欄位**：研究端在 1.1 版新增欄位，寫作端不會壞掉。

### 驗證結果（實際執行）

```text
PASS  samples/research_valid.json 符合 contracts/research_output.schema.json

FAIL  samples/research_invalid.json 有 6 個違規：
  - contract_version: '2.0' does not match '^1\\.\\d+$'
  - findings/0: 'sources' is a required property
  - findings/0: Additional properties are not allowed ('author' was unexpected)
  - findings/0/confidence: 1.7 is greater than the maximum of 1
  - findings/0/key_points: [] should be non-empty
  - topic: 'AI' is too short
```

## 任務 2：錯誤處理

| 情境 | 偵測方式 | 處理 | 寫作端結果 |
| --- | --- | --- | --- |
| 1. 研究完全失敗（網路／timeout） | `status=error`；若連信封都拿不到，由 orchestrator 的 try/except + timeout 補一個 error 信封 | `retryable=true` 才重試，最多 3 次（指數退避）；用盡就停止 | **停止**，回報錯誤碼。沒資料硬寫會產生幻覺內容 |
| 2. 空結果 | `status=empty` | 重試 2 次（共 3 次），每次放寬關鍵字 | **fallback**：輸出「大綱 + 待補資料」草稿，明確標示查無資料 |
| 3. 格式不符合約 | 用 JSON Schema 驗證；逐筆驗 finding | 信封（status/topic）壞 → 停止；只有部分 finding 壞 → 丟棄壞的、保留好的 | 剩 ≥1 筆合格 → **partial 繼續**並在文章標註；否則停止 |

模擬實測（`ex02_orchestrator.py`，6 個情境全符合預期）：

```text
[PASS] mode=ok        → ok
[PASS] mode=error     → stopped   研究 agent 失敗：TIMEOUT
[PASS] mode=empty     → fallback  3 次皆 empty → 大綱模式
[PASS] mode=flaky     → ok        前 2 次 empty、第 3 次成功
[PASS] mode=malformed → partial   findings[1] 缺 sources 被丟棄，保留 1 筆
[PASS] mode=garbage   → stopped   信封缺 contract_version/status
```

### 為什麼情境 1 停止、情境 2 卻 fallback？

- 情境 1 是「不知道有沒有資料」，寫出來可能和事實相反，風險高 → 停止。
- 情境 2 是「確定沒資料」，可以誠實地產出大綱讓人補 → 有產出比沒產出好。
- 情境 3 的 partial 規則：資料是「多筆獨立的發現」，丟掉一筆不影響其他筆的正確性；但信封壞掉代表整個回應不可信。

## 延伸思考：可靠性 vs 彈性

採用 **「生產端嚴格、消費端寬鬆」**（Postel 法則 / Tolerant Reader）：

1. **兩份 schema**：研究端用嚴格版自我檢查（`additionalProperties: false`），寫作端只鎖自己真正用到的欄位。測試 `test_consumer_is_tolerant_of_extra_fields` 證明：新增欄位時，嚴格版會擋、寬鬆版照收。
2. **版本號**：`contract_version` 主版號變動才代表不相容，小版號只能新增選填欄位。
3. **嚴格的地方放在「錯了會造成錯誤輸出」的欄位**：來源、可信度、status；**寬鬆的地方放在「純附加資訊」**：tags、summary。
4. **逐筆驗證而非整包否決**：讓局部錯誤不會擴大成整體失敗。
