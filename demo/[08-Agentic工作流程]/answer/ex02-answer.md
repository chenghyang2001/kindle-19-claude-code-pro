# Exercise 02 解答 — 真實 Multi-Agent Workflow 設計

## 任務 1：依賴圖

```
A（GitHub，30s）──┐
B（Jira，45s）────┼──→ D（合成報告，60s）──┐
C（Jenkins，20s）─┘                         ├──→ F×5（寄信，每封 10s）
E（名單，15s）────────────────────────────────┘
```

**關鍵觀察**：E（抓名單）與 A、B、C 完全無依賴，可以「最早」並行跑。

## 任務 2：F 的 5 封信 — parallel() 還是 pipeline()？

**各封信之間沒有依賴關係**（寄給不同人，互不影響）。

| 情境 | 選擇 | 原因 |
|------|------|------|
| 每封信只做「寄出」這一件事 | `parallel()` | 5 個獨立任務同時跑，wall-clock = 10s |
| 每封信要經過「個人化→排版→寄出」三個 stage | `pipeline()` | 5 個 item 各自流過 3 個 stage，不需等全部完成才進下一 stage |

**本題建議**：用 `pipeline()`，因為真實寄信通常有多個 stage：

```javascript
// 5 位主管各自走 3 個 stage，互不干擾
const results = await pipeline(
  mailingList,                                          // 5 個收件人
  recipient => agent(`personalise report for ${recipient}`),  // stage 1：個人化
  content   => agent(`format HTML email`, { input: content }), // stage 2：排版
  html      => agent(`send email`, { input: html })           // stage 3：寄出
)
```

主管 A 在做排版時，主管 B 可以同時在個人化 — 這就是 pipeline 的優勢。

## 完整架構程式碼

```javascript
// Stage 1：A、B、C、E 全部並行（互無依賴）
const [prData, jiraData, ciData, mailingList] = await parallel([
  () => agent("fetch GitHub PR status"),     // A (30s)
  () => agent("fetch Jira task counts"),     // B (45s)
  () => agent("fetch Jenkins failure rate"), // C (20s)
  () => agent("fetch mailing list"),         // E (15s)
])
// 完成時間 = max(30, 45, 20, 15) = 45s

// Stage 2：合成報告（需要 A+B+C，E 此時也已完成）
const report = await agent("synthesize productivity report", {
  input: { prData, jiraData, ciData }  // D (60s)
})
// 完成時間 = 45 + 60 = 105s

// Stage 3：5 封信走 pipeline（需要 D 和 E）
await pipeline(
  mailingList,
  recipient => agent(`personalise for ${recipient}`, { input: report }),
  content   => agent("format HTML email", { input: content }),
  html      => agent("send email", { input: html })
)
// 完成時間 = 105 + 10 = 115s（pipeline wall-clock = 最慢的單封）
```

## 時間比較

| 方案 | 計算 | 總時間 |
|------|------|--------|
| 全部依序 | 30+45+20+60+15+(5×10) | **220 秒** |
| 最優並行 | max(A,B,C,E)=45 + D=60 + pipeline(F)=10 | **115 秒** |

**節省 105 秒（48%）**

## 關鍵洞察

1. **E 要儘早並行**：E 不依賴任何任務，不要等 D 完成才抓，要和 A、B、C 一起跑。
2. **barrier 的位置**：Stage 1→2 之間有 barrier（D 需要 A+B+C 全部完成）；Stage 2→3 之間也有 barrier（F 需要 D 和 E 都完成）。
3. **pipeline 的 wall-clock = 最慢的單一 item 的完整路徑**，不是「所有 item 的總和」。
