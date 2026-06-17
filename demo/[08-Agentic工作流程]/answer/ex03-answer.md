# Exercise 03 解答 — 有錯誤恢復的 Agent 合約設計

## 核心原則：合約決定錯誤的「可見性」

Agent 不能只回傳「資料或 null」，必須回傳「結構化結果」讓 orchestrator 做決策。

---

## Agent A 合約（抓 GitHub PR）

**問題**：timeout vs 真的沒資料，orchestrator 無法區分。

```typescript
// Agent A 必須回傳的格式
type GitHubResult =
  | { status: "ok";      data: PR[];    count: number }
  | { status: "timeout"; error: string; retryable: true;  elapsed_ms: number }
  | { status: "error";   error: string; retryable: false; code: number }
  | { status: "empty";   reason: string }  // 真的沒 PR，不是錯誤

// ✅ 正常
{ status: "ok", data: [...], count: 12 }

// ✅ 超時（可重試）
{ status: "timeout", error: "GitHub API timeout", retryable: true, elapsed_ms: 31000 }

// ✅ 真的空（昨天假日，沒人 merge）
{ status: "empty", reason: "no PRs merged on 2026-06-16 (holiday)" }

// ✅ 認證失敗（不可重試）
{ status: "error", error: "401 Unauthorized", retryable: false, code: 401 }
```

**關鍵**：`status: "timeout"` vs `status: "empty"` 是完全不同的情境，
orchestrator 對 timeout 要重試，對 empty 要繼續（報告寫「昨日無 PR」）。

---

## Agent F 合約（寄信）

**問題**：5 封信中 1 封失敗，orchestrator 不知道哪封。

```typescript
// Agent F 必須回傳每封的獨立結果
type EmailResult = {
  recipient: string
  status: "sent" | "failed" | "skipped"
  error?: string
  sent_at?: string   // ISO timestamp（成功時）
  message_id?: string  // SMTP message ID（成功時）
}

// ✅ 範例回傳（5 封的陣列）
[
  { recipient: "ceo@company.com",   status: "sent",   sent_at: "2026-06-17T08:00:01Z", message_id: "abc123" },
  { recipient: "cto@company.com",   status: "failed", error: "550 No such user" },
  { recipient: "pm@company.com",    status: "sent",   sent_at: "2026-06-17T08:00:02Z", message_id: "def456" },
  { recipient: "hr@company.com",    status: "sent",   sent_at: "2026-06-17T08:00:03Z", message_id: "ghi789" },
  { recipient: "cfo@company.com",   status: "failed", error: "Connection timeout" },
]
```

**不能這樣設計**（錯誤示範）：
```typescript
// ❌ 只回傳 true/false，orchestrator 不知道是誰失敗
{ success: true }

// ❌ 第一封失敗就 throw，其他 4 封不寄了
throw new Error("Email failed")
```

---

## Orchestrator 決策邏輯

**兩種失敗模式，策略完全不同**：

| 失敗類型 | 是否影響後續 | 策略 |
|---------|------------|------|
| A（資料來源）失敗 | 是 — 沒資料無法生成報告 | **整體放棄**，記錄錯誤，明天重試 |
| F（寄信）某封失敗 | 否 — 其他封不受影響 | **跳過繼續**，最後彙報哪封失敗 |

```javascript
// Orchestrator 的決策流程

// 1. 抓資料（A、B、C 是 critical，任一失敗就停）
const githubResult = await agent("fetch GitHub PRs")
if (githubResult.status === "timeout" && githubResult.retryable) {
  // 重試一次
  const retry = await agent("fetch GitHub PRs")
  if (retry.status !== "ok") {
    return { success: false, reason: "GitHub unavailable after retry", abort: true }
  }
}
if (githubResult.status === "error") {
  return { success: false, reason: githubResult.error, abort: true }
}

// 2. 寄信（F 是 non-critical，失敗的跳過，其他繼續）
const emailResults = await pipeline(
  mailingList,
  recipient => agent(`send email to ${recipient}`, { report })
)

// 3. 整理結果（把所有 F 的結果彙整）
const sent   = emailResults.filter(r => r.status === "sent")
const failed = emailResults.filter(r => r.status === "failed")

return {
  success: true,
  summary: {
    emails_sent: sent.length,
    emails_failed: failed.length,
    failed_recipients: failed.map(r => ({ to: r.recipient, reason: r.error }))
  }
}
```

---

## 合約設計三原則

1. **狀態碼優於 boolean**：`status: "timeout" | "error" | "ok" | "empty"` 比 `success: true/false` 給 orchestrator 更多決策依據。

2. **retryable 旗標**：Agent 本身最清楚哪些錯誤值得重試（timeout = 可重試，401 = 不可重試），不該讓 orchestrator 猜。

3. **partial success 陣列**：批次操作（寄 5 封信）回傳陣列而非單一結果，每個 item 有獨立的 status，才能精確報告哪個成功哪個失敗。

---

## 關鍵洞察

**「critical」vs「non-critical」的判斷標準**：
- 這個 agent 的輸出，是否被後續 agent 當成「必要輸入」？
  - 是 → critical（失敗要整體停止）
  - 否 → non-critical（失敗可跳過，最後彙報）

A、B、C 是 D 的必要輸入 → critical  
F 的每封信獨立 → non-critical，pipeline 自然處理 partial failure
