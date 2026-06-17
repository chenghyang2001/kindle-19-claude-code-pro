# Exercise 01 解答 — 依賴圖分析與架構設計

## 任務 A–H 依賴關係

```
A（抓 GitHub PR）──┐
                   ├──→ C（PR 摘要）──┐
B（抓 Notion 任務）──┘                  ├──→ E（合併 C+D）──→ F（生 Markdown）──→ G（上傳 Drive）──→ H（Telegram 通知）
                   ├──→ D（任務狀態）──┘
```

## 並行機會分析

| 階段 | 可並行的任務 | 原因 |
|------|------------|------|
| Stage 1 | A ∥ B | 互相沒有依賴，可同時抓資料 |
| Stage 2 | C ∥ D | C 只需要 A，D 只需要 B，A+B 完成後可同時進行 |
| Stage 3～6 | E → F → G → H | 嚴格依序，每個都只有一個前置，無法並行 |

## 架構設計

```
// Stage 1：parallel（有 barrier — 需要 A 和 B 都完成後，C 和 D 才能開始）
const [prData, notionData] = await parallel([
  () => agent("fetch GitHub PRs"),    // A
  () => agent("fetch Notion tasks"),  // B
])

// Stage 2：parallel（C 和 D 互相獨立）
const [prSummary, taskStatus] = await parallel([
  () => agent("summarize PRs", { input: prData }),       // C
  () => agent("format task status", { input: notionData }), // D
])

// Stage 3：嚴格依序（每步只有一個前置）
const merged   = await agent("merge C+D", { input: [prSummary, taskStatus] })  // E
const markdown = await agent("generate markdown", { input: merged })            // F
const driveUrl = await agent("upload to Drive", { input: markdown })           // G
await agent("send Telegram notification", { input: driveUrl })                  // H
```

**注意**：Stage 1 和 Stage 2 之間有 **barrier**（parallel → parallel），
因為 C 必須等 A 完成、D 必須等 B 完成，不能用 pipeline。

## 時間估算

| 方案 | 計算 | 總時間 |
|------|------|--------|
| 全部依序 | 8 × 30s | **240 秒** |
| 最優並行 | max(A,B)=30 + max(C,D)=30 + E+F+G+H=120 | **180 秒** |

**節省：60 秒（25%）**，靠 A∥B 和 C∥D 各省一個 30 秒。

## 關鍵洞察

- C 需要 A → D 需要 B → 兩者完成後才能開 C、D（barrier 必要）
- F、G、H 是嚴格鏈狀依賴，**沒有並行空間**，是整個工作流的效能瓶頸
- `pipeline()` 適合「多個 PR 各自走相同流程」；`parallel()` 適合「不同資料來源同時抓取」
