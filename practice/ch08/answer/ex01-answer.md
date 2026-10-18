# 練習 01 解答 — 識別並行機會

> 可執行驗證：`PYTHONUTF8=1 .venv/Scripts/python src/ex01_dag_sim.py`（用 asyncio 把 30 秒縮成 0.3 秒模擬）

## 任務 1：依賴分析

### 依賴圖

```text
 A 取 GitHub PR ──► C 摘要每個 PR ──┐
                                     ├──► E 彙整 ──► F 生成 MD ──► G 上傳 Drive ──► H Telegram
 B 取 Notion 任務 ─► D 整理任務狀態 ─┘
        ▲                                ▲
   兩條 lane 互不相依                   唯一的匯合點（barrier）
```

| 任務 | 前置 | 層級 |
| --- | --- | --- |
| A, B | 無 | 第 1 層 |
| C | A | 第 2 層 |
| D | B | 第 2 層 |
| E | C, D | 第 3 層 |
| F → G → H | 前一個 | 第 4~6 層（純串列） |

### 1. 哪些可以並行？

- **A 與 B**：兩個不同資料來源，彼此完全無關。
- **C 與 D**：C 只依賴 A、D 只依賴 B，所以 C 和 D 互相獨立；甚至 **C 可以和 B 同時跑**、D 可以和 A 同時跑。
- **C 內部**：每個 PR 的摘要互不相依，可以對 N 個 PR 同時摘要（D 內部同理）。
- E、F、G、H 是一條直線，無法並行。

### 2. 哪些放進同一個 parallel()？

- `parallel(A, B)`：抓取兩個來源。
- `parallel(C, D)`：兩種整理工作。
- `parallel(summarize(pr) for pr in prs)`：C 內部對每個 PR fan-out。
- 更好的寫法是把 `A→C`、`B→D` 各包成一條 lane，再 `parallel(lane1, lane2)`，避免第 1 層、第 2 層之間多一個沒必要的 barrier。

### 3. pipeline() 的 item 是什麼？

- 在 A→C 這條 lane，**item = 單一 PR**；在 B→D 這條 lane，**item = 單一 Notion 任務**。
- PR 一抓到就送去摘要，不用等整批抓完。
- 到 E 之後 item 變成「整份週報」，只有 1 筆，pipeline 已無意義，直接串列即可。

## 任務 2：架構設計

```text
parallel(                                  ← barrier：E 需要兩邊都完成
  pipeline(fetch_prs  → summarize_pr),     ← item = PR
  pipeline(fetch_tasks → summarize_task),  ← item = 任務
)
→ E 彙整 → F 生成 Markdown → G 上傳 Drive → H Telegram 通知   ← 串列
```

- **為什麼需要 barrier**：E 要把「全部 PR 摘要」和「全部任務整理」放在同一份週報裡，少一筆就是錯誤的週報。barrier 保證 E 開始時兩邊資料都齊全。
- **barrier 放哪**：只放在 E 之前。如果寫成 `parallel(A,B)` 再 `parallel(C,D)`，中間多了一個 barrier，C 會被迫等 B——在每個任務時間相同時看不出差別，但 B 一旦變慢（例如 Notion API 很慢），C 就白等了。
- **哪些用 pipeline()**：A→C、B→D 兩條 lane。

### 時間估算（每個任務 30 秒）

| 排程方式 | 計算 | 理論 | 模擬實測（換算） |
| --- | --- | --- | --- |
| 全依序 | 8 × 30 | 240 秒 | 247.9 秒 |
| parallel(A,B) → parallel(C,D) → E..H | 6 × 30（關鍵路徑 A→C→E→F→G→H） | 180 秒 | 186.6 秒 |
| 兩條 lane 的 pipeline | 同上 | 180 秒 | 186.7 秒 |
| 逐項 pipeline（每邊 3 筆，抓與摘要重疊） | 30 + 10 + 4 × 30 | 160 秒 | 168.1 秒 |

- 最優並行比全依序省 **60 秒（25%）**；改成逐項 pipeline 再省約 20 秒。
- 實測多出 6~8 秒是 Windows 計時器與 asyncio 排程的誤差（每次 sleep 約多 1ms，放大 100 倍）。
- 上限受 **關鍵路徑** 限制：E→F→G→H 這 4 步（120 秒）無論怎麼並行都省不掉，這是 Amdahl 定律的典型例子。
