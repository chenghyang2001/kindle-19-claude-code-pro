# STEP_LOG — [08] Agentic 工作流程

## 開始日期
2026-06-17

## 學習步驟記錄

| # | 步驟 | 狀態 | 耗時 | 備註 |
|---|------|------|------|------|
| 1 | 閱讀 README + 確認學習目標 | ✅ | 10 分鐘 | |
| 2 | 完成 exercise-01-基礎.md | ✅ | 20 分鐘 | parallel vs pipeline 依賴圖分析 |
| 3 | 完成 exercise-02-進階.md | ✅ | 15 分鐘 | E 提前並行 + pipeline 寄信設計 |
| 4 | 完成 exercise-03-綜合.md（選配） | ✅ | 15 分鐘 | Agent 合約 + critical/non-critical 決策 |
| 5 | 將解答存入 answer/ | ✅ | 5 分鐘 | ex01/02/03-answer.md |
| 6 | 填寫本課 STEP_LOG | ✅ | 5 分鐘 | |
| 7 | 執行 carry（攜帶答案到下一課） | ⬜ | | |

狀態符號：⬜ 未開始 / 🔄 進行中 / ✅ 完成 / ⏭️ 跳過

---

## 踩坑記錄

### 坑 1 — parallel vs pipeline 的時間計算
- **現象**：以為最優並行 = 90 秒（只算到 E 完成），實際是 180 秒
- **根本原因**：忘記計算 E（合成）之後的 F→G→H 嚴格依序鏈
- **解法**：畫完整依賴圖，找「關鍵路徑」= 最長依賴鏈，而非只看並行段

---

## 學習心得

1. **`parallel()` 是 barrier，`pipeline()` 沒有 barrier**：parallel 等全部完成才繼續，適合「需要所有結果才能做下一步」；pipeline 讓每個 item 各自流動，A 在 stage 2 時 B 還在 stage 1，wall-clock 是最慢的單一 item 路徑。

2. **Agent 合約的 `status` 欄位比 boolean 更有價值**：`timeout`（可重試）vs `empty`（繼續跑）vs `error`（停止），讓 orchestrator 能做出正確決策，而不是猜。

---

## 完成日期
2026-06-17

## 總耗時
約 1 小時 10 分鐘
