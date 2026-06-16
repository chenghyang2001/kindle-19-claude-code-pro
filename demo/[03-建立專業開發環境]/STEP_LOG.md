# STEP_LOG — [03] 建立專業開發環境

## 開始日期
2026-06-16

## 學習步驟記錄

| # | 步驟 | 狀態 | 耗時 | 備註 |
|---|------|------|------|------|
| 1 | 閱讀 README + 確認學習目標 | ✅ | 5 分鐘 | 三主題：CLAUDE.md / Hooks / MCP |
| 2 | 完成 exercise-01-基礎.md | ✅ | 15 分鐘 | Flask API 6 區塊 + 3 問題測試 |
| 3 | 完成 exercise-02-進階.md | ✅ | 20 分鐘 | PostToolUse ruff + SessionStart git hook |
| 4 | 完成 exercise-03-綜合.md（選配） | ✅ | 10 分鐘 | GitHub MCP 配置 + 工具表 |
| 5 | 將解答存入 answer/ | ✅ | — | ex01/02/03-answer.md |
| 6 | 填寫本課 STEP_LOG | ✅ | — | |
| 7 | 執行 carry（攜帶答案到下一課） | ✅ | — | answer/ → [04]/starter/ |

狀態符號：⬜ 未開始 / 🔄 進行中 / ✅ 完成 / ⏭️ 跳過

---

## 踩坑記錄

本課為概念設計練習（無實際執行程式碼），無工具層面的踩坑。

---

## 學習心得

1. **CLAUDE.md / Hook / MCP 三層分工明確**：CLAUDE.md 說規則、Hook 強制執行、MCP 擴充能力。三層缺一則 Claude 只能部分發揮——只有文件而無 Hook，Claude 可能「忘記」遵守規則。

2. **Hook 的靜默失敗設計是生產心態**：Hook 應視為「加分工具」，失敗時記錄但不中斷主流程。`command || true` 是最簡單的靜默失敗設計，適用於所有非關鍵的自動化 hook。

---

## 完成日期
2026-06-16

## 總耗時
約 50 分鐘
