# 部署規則（被 CLAUDE.md 匯入）

驗證暗號：DEPLOY-2093

- 部署只能透過 CI（main 合併後自動跑），Claude 不可手動部署正式環境
- CI 順序：lint → test → build → deploy（前一步失敗即停止）
- 環境變數放 CI Secrets，`.env` 不入版控，提供 `.env.example`
- 每次部署必須可回滾（保留前一版 image tag）
- 週五 17:00 後不部署正式環境
