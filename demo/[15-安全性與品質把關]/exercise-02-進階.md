# 練習 02 — 進階：自動化安全審查流程

## 情境說明
在每次 PR 合入之前，你想要自動執行安全審查。設計一個可以在 GitHub Actions 或 pre-commit hook 中執行的流程。

## 任務

### 任務 1：靜態分析工具選擇
根據專案類型選擇合適的靜態分析工具：

| 語言 | 工具 | 檢查重點 |
|------|------|---------|
| Python | Bandit | 安全漏洞 |
| JavaScript/TypeScript | ESLint（eslint-plugin-security） | 安全規則 |
| SQL | — | 需要自定義 |

為一個「Python API + TypeScript 前端」的專案，設計完整的靜態分析流程：
- 列出需要安裝的工具和設定檔
- 設計執行順序（哪些先哪些後）
- 設定哪些問題要 Fail（阻止合入）哪些是 Warn（只通知）

### 任務 2：Claude 輔助審查的邊界
靜態分析工具和 Claude 審查各有擅長：
- 靜態分析工具擅長什麼？
- Claude 審查擅長什麼？
- 哪些問題只有 Claude 能找到（工具找不到的）？
- 哪些問題工具更準確（Claude 可能漏掉或誤報的）？

根據這個分析，設計一個「工具先跑、Claude 後審」的工作流，說明 Claude 的審查 Prompt 要補充哪些工具的盲區。

### 任務 3：設計安全 Checklist
為生產環境部署設計一個 10 項安全 Checklist，涵蓋：
- 認證與授權
- 輸入驗證
- 機密管理
- API 安全
- 日誌（不洩漏敏感資訊）

## 延伸思考
如果 Claude 在審查過程中發現一個「可能是安全問題，但不確定」的地方，它應該如何回報？Prompt 要怎麼設計才能讓 Claude 表達「信心程度」？

## 完成後
將自動化流程設計 + Checklist 存入 `answer/ex02-answer.md`
