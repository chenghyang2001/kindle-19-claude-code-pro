# STEP_LOG — [09] MCP 白話文

## 開始日期
2026-06-17

## 學習步驟記錄

| # | 步驟 | 狀態 | 耗時 | 備註 |
|---|------|------|------|------|
| 1 | 閱讀 README + 確認學習目標 | ✅ | 5 分鐘 | MCP = Tool/Resource/Prompt 三種能力 |
| 2 | 完成 exercise-01-基礎.md | ✅ | 20 分鐘 | 能力地圖 + MCP vs REST API 比較 |
| 3 | 完成 exercise-02-進階.md | ✅ | 20 分鐘 | Gmail→Docs 呼叫序列設計 + auth 優雅失敗 |
| 4 | 完成 exercise-03-綜合.md（選配） | ✅ | 25 分鐘 | PM2.5 MCP Server JSON Schema 設計 |
| 5 | 將解答存入 answer/ | ✅ | 5 分鐘 | ex01/02/03-answer.md |
| 6 | 填寫本課 STEP_LOG | ✅ | 5 分鐘 | |
| 7 | 執行 carry（攜帶答案到下一課） | ✅ | 1 分鐘 | L09 answer/ → L10 starter/ |

狀態符號：⬜ 未開始 / 🔄 進行中 / ✅ 完成 / ⏭️ 跳過

---

## 踩坑記錄

### 坑 1 — 本環境無 Notion MCP
- **現象**：Exercise 02 要求 Gmail→Notion 流程，但 settings.json 無 Notion MCP
- **根本原因**：Notion MCP 需另行安裝 `@notionhq/notion-mcp-server`，不在預設環境
- **解法**：用 `mcp__google-docs__createDocument` 替代，MCP 呼叫模式完全相同，只是 tool name 不同

### 坑 2 — Gmail MCP search_threads 回應比預期更豐富
- **現象**：設計時以為 Step 1（搜尋）只回傳 id，實際已包含 messages 陣列
- **根本原因**：文件描述和實際回應格式不完全一致（常見問題）
- **解法**：設計序列時加「小試一下」步驟，先跑一次看實際格式，再設計 downstream

---

## 學習心得

1. **MCP 的三種能力有明確分工**：Tool（有副作用，Claude 主動呼叫）、Resource（唯讀靜態數據）、Prompt（預設模板）。設計自訂 MCP 時，99% 的場景是 Tool。

2. **MCP vs REST API 的選擇標準很簡單**：Claude 互動操作 → MCP（零設定開銷）；VPS 排程自動化 → 直接 API（不依賴 MCP server 的 auth 狀態）。兩者不是替代關係，是互補。

---

## 完成日期
2026-06-17

## 總耗時
約 1 小時 20 分鐘
