# 附錄 B：團隊 CLAUDE.md 主模板

從第 14 章補全您的上下文。Commit 後指定負責人，每季審查。

---

```markdown
# [團隊 / 產品名稱] Claude 上下文
# 版本：1.2.0 | 最後更新：[YYYY-MM-DD]
# 負責人：[主要開發者姓名]

## 關於此程式庫
[2-3 句話：產品說明、使用者、目前階段。]
優先考量 [速度與迭代 / 穩定性 / 效能]。

## 技術堆疊
前端：    [例：React.js 18 App Router + TypeScript + Tailwind]
後端：    [例：Node.js v21]
資料庫：  [例：PostgreSQL（t-managed）]
驗證：    [例：Auth.js v5 + Google OAuth]
測試：    [例：Vitest + Playwright]
部署：    [例：Vercel + GitHub Actions]
HTTP：    400 驗證錯誤、401 禁止、403 未授權、
          404 找不到、500 內部錯誤（不回傳原始錯誤
          或內部 API 呼叫細節）
日誌：    使用 lib/logger.ts — 禁止 console.log

## 資料夾結構
[列出主要目錄及其用途。]

## 程式碼慣例
命名：    嚴格模式 — 禁止 @ts-ignore — 禁止無 TODO 的 "any"
錯誤：    { error: array | errors: string | } API 回應
HTTP：    400 驗證錯誤、401 禁止、403 未授權、
          404 找不到、500 內部錯誤（不回傳原始 TF API 呼叫（待確認））
日誌：    使用 lib/lib/logger.ts — 禁止 console.log

## 測試要求
函式、動作、輔助函式：85% 以上覆蓋率。
E2E：關鍵使用者流程。在 main 推送至 main 時執行。
SIG：關鍵使用流程。每次測試時執行。

## 我們使用的規則 — 複製貼上
- 禁止行內樣式
- 禁止無 // TODO 註解的 "any"
- 禁止從 RSC 直接進行 DB 查詢
- 禁止 console.log — 使用 lib/logger

## 我們不要的模式
[在此填入您的 Server Action / Repository / Error handler 模式]

## 目前重點領域
[每個 Sprint 更新]：___

## 開發指令
npm run dev  |  npm run test  |  npm run db:push
[姓名 / 代號] [負責領域]

[YYYY-MM-DD] v1.0.0 — 初始版本
```
