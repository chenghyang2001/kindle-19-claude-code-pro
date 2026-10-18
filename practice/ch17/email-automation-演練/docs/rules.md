# 規則與禁止事項

## 必須遵守

1. 所有寄信都經過 `sender.send_all(messages, dry_run=...)`；CLI 預設 `dry_run=True`。
2. 範本渲染只用 `string.Template.substitute`；缺欄位要拋 `TemplateError`，不可默默留空。
3. 新增功能時，同一次改動要在 `tests/` 補對應測試（正常 + 邊界/錯誤各至少一個）。
4. 讀寫檔案一律指定 `encoding="utf-8"`（Windows 預設 cp950 會讓中文範本亂碼）。
5. 測試與範例資料的 email 只用 `example.com` 網域。
6. （回答標註規則已於 v1.1 搬到主檔 CLAUDE.md 的「回答格式」）

## 禁止事項（附原因）

| 禁止 | 原因 |
| ------ | ------ |
| 在程式碼、測試、範本中寫 SMTP 帳號密碼或 App Password | repo 會被 commit/分享，機密一旦進 git 歷史就得換密碼 |
| 移除或繞過 dry-run 預設（例如把 `--send` 改成預設開啟） | 誤寄給真實客戶無法收回，dry-run 是最後防線 |
| 引入第三方套件（pytest、jinja2、requests…）而未先在本檔登記 | 本專案定位零依賴，任何人 clone 下來就能跑 |
| 移除 `SEND_INTERVAL_SECONDS` 寄信間隔 | Gmail 等 SMTP 對短時間大量寄信會暫時封鎖帳號 |
| 用 `print` 以外的方式把收件人名單送到外部服務 | 名單是個資，不可外流 |
