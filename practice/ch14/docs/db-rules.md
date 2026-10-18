# 資料庫操作規則（被 CLAUDE.md 匯入）

驗證暗號：DB-7731

- 一律參數化查詢，禁止字串拼接 SQL
- Schema 變更必須寫 migration（up + down），不可手動改正式 DB
- 金額用 INTEGER（以「分」為單位）或 DECIMAL，禁用 FLOAT
- 時間欄位存 UTC
- 報表類查詢必須有 WHERE 時間區間 + 索引支援，禁止全表掃描
- Claude 只能連 dev/test DB；正式 DB 只有 DBA 能操作
