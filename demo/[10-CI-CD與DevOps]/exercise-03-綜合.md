# 練習 03 — 綜合挑戰：完整 DevOps Pipeline

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
為 `freelancer-dashboard/` 設計一個完整的 DevOps Pipeline，從 PR 到 production 全自動化。

## 要求

### Pipeline 四個階段設計

**階段 1：PR 觸發（CI）**
- TypeScript 類型檢查
- ESLint 程式碼規範
- pytest / Jest 測試
- PR 必須通過以上所有才能 merge

**階段 2：Merge to main（Auto Deploy to Staging）**
- 自動部署到 Vercel preview 環境
- 執行冒煙測試（smoke test）：確認首頁可以載入
- 自動通知（Telegram 或 Slack）部署結果

**階段 3：手動確認（Gate）**
- Staging 部署成功後，需要手動點擊「確認部署到 Production」
- （可以是 GitHub Actions 的 Environment 功能，或簡單的 workflow_dispatch）

**階段 4：Production 部署**
- 部署到 Vercel production
- 自動執行生產環境冒煙測試
- 部署失敗自動回滾（rollback）到上一個版本

### 輸出格式
設計文件（不需要完全可執行的 YAML，但要足夠具體）：
1. 每個階段的觸發條件
2. 每個 job 的步驟
3. 部署失敗時的回滾指令
4. 需要設定哪些 GitHub Secrets

## 完成標準
- [ ] 四個階段都有設計
- [ ] 回滾機制有具體指令
- [ ] GitHub Secrets 清單完整

## 完成後
將解答存入 `answer/ex03-answer.md`
