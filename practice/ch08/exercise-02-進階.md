# 練習 02 — 進階：設計 Sub-agent 合約

## 情境說明
你要讓「研究 agent」和「寫作 agent」協作完成技術文章，但兩個 agent 是獨立的，只能透過合約溝通。

## 任務

### 任務 1：定義資料合約
設計研究 agent 和寫作 agent 之間的「資料合約」（JSON Schema）。

研究 agent 應該輸出什麼？考慮：
- 研究發現的結構（標題 / 重點 / 來源 / 可信度）
- 資料類型（string / array / object）
- 必填 vs 選填欄位
- 最大/最小數量限制

寫作 agent 的輸入期望：
- 它需要哪些欄位？
- 欄位缺失時如何處理？

設計 JSON Schema（可以是簡化版，不需要完整 JSON Schema 語法）。

### 任務 2：錯誤處理設計
設計以下三種失敗情境的處理方式：

1. **研究 agent 完全失敗**（network error / timeout）
   - 寫作 agent 應該如何知道？
   - 寫作 agent 能繼續嗎？還是應該停止？

2. **研究 agent 回傳了空結果**（找不到相關資料）
   - 應該重試嗎？重試幾次？
   - 如果依然沒有結果，寫作 agent 的 fallback 是什麼？

3. **研究 agent 回傳的資料格式不符合合約**
   - 如何偵測？
   - 是繼續（用 partial data）還是停止？

## 延伸思考
思考：合約越嚴格，agent 間的耦合就越高。你如何在「可靠性」和「彈性」之間取得平衡？

## 完成後
將 JSON Schema 設計 + 錯誤處理策略存入 `answer/ex02-answer.md`
