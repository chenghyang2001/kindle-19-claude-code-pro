# 練習 03 — 綜合挑戰：完整品質閘道建立

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
為 Freelancer Dashboard（課程 13 建立的專案）建立一個完整的品質閘道，在每次 git push 前自動執行。

## 閘道設計要求

品質閘道必須包含以下三層，按順序執行。任何一層失敗，整個閘道 FAIL：

### 第一層：靜態分析（最快，最先）
- TypeScript 型別檢查（`tsc --noEmit`）
- ESLint 安全規則（至少 `no-eval`, `no-implied-eval`, `no-unused-vars`）
- Prettier 格式檢查（非 blocking，只 warn）

### 第二層：測試（中）
- 單元測試（至少測試 Zod schema 驗證邏輯）
- API 整合測試（至少測試認證失敗的 401 案例）

### 第三層：安全掃描（最後）
- 使用 `npm audit` 檢查依賴漏洞（Critical 等級必須 fix 才能通過）
- 檢查是否有硬編碼的密鑰（可以用 `grep -r "API_KEY"` 簡單掃描）

## 實作方式
選擇以下一種方式實作：
- GitHub Actions Workflow（`.github/workflows/quality-gate.yml`）
- 或 pre-push Git Hook（`.git/hooks/pre-push`）

## 驗收測試

**測試 1：正常情況**
Push 一個乾淨的改動，閘道應該通過。

**測試 2：故意引入型別錯誤**
加入一個 TypeScript 型別錯誤，閘道應該在第一層 FAIL。

**測試 3：故意加入硬編碼密鑰**
加入 `const API_KEY = "sk-..."` 到程式碼中，閘道應該在第三層 FAIL。

## 完成標準
- [ ] 三層閘道都有實作
- [ ] 三個驗收測試都通過（包含 FAIL 的兩個）
- [ ] 閘道執行時間 < 2 分鐘

## 完成後
將 Workflow YAML / Hook 腳本 + 驗收截圖存入 `answer/ex03-answer.md`
