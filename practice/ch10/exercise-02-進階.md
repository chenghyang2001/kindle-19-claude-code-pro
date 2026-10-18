# 練習 02 — 進階：部署策略設計

## 情境說明
你要部署一個 Next.js 應用到 Vercel，需要管理 staging 和 production 兩個環境。

## 任務

### 任務 1：多環境設定
設計兩個環境的完整管理策略：

**環境變數清單（假設的）：**
- `DATABASE_URL`（不同環境連不同 DB）
- `NEXT_PUBLIC_API_URL`（API endpoint）
- `OPENAI_API_KEY`（相同 key，但有使用量限制）
- `FEATURE_FLAG_NEW_UI`（staging 開啟，production 關閉）

回答：
1. 哪些變數在兩個環境相同？哪些不同？
2. 如何在 Vercel 設定這些變數（不洩漏到程式碼）？
3. 如果開發者需要在本機模擬 staging 環境，怎麼設計 .env 管理？

### 任務 2：建立部署前 Checklist
設計一個 10 項「部署前 Checklist」，確保每次部署到 production 前都有確認：

格式（每項包含）：
- 檢查項目
- 如何驗證（指令或手動步驟）
- 如果失敗應該怎麼處理（修復 vs 延後部署）

## 延伸思考
思考：如果 production 部署後發現嚴重 bug，你的「緊急回滾」流程是什麼？從發現問題到回滾完成，最快可以幾分鐘？

## 完成後
將環境管理策略 + 部署 Checklist 存入 `answer/ex02-answer.md`
