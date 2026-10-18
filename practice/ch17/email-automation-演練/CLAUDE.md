# email-automation Claude 上下文

版本：1.1.0 | 最後更新：2026-10-18 | 負責人：演練團隊（每季審查一次，下次：2027-01-18）

## 關於此程式庫

依 CSV 收件人名單 + 文字範本，批次產生個人化 Email 並經 SMTP 寄出的 Python CLI。
使用者是需要寄課程通知信的小型團隊；目前階段為演練版（v1.0）。
優先考量 **安全（不誤寄、不洩密）> 正確性 > 速度**。

## 技術堆疊

語言：    Python 3.12+（實測 3.14.3）
依賴：    僅標準庫（smtplib / email / csv / string.Template / argparse）
測試：    unittest（不引入 pytest，保持零依賴）
寄信：    SMTP + STARTTLS，帳密只來自環境變數（見 `.env.example`）

## 詳細文件（@ 匯入，各自維護）

- 架構與資料夾：@docs/architecture.md
- 規則與禁止事項（含原因）：@docs/rules.md
- 開發指令：@docs/commands.md

## 最重要的三件事（衝突時依此順序）

1. 預設 dry-run，真的寄信只能透過 `--send` 旗標。
2. 機密只從環境變數讀，絕不出現在程式碼、測試或範本裡。
3. 改程式就要跑 `python -m unittest discover -s tests` 並全綠。

## 回答格式

回答「關於本專案」的問題時，最後一行固定加上 `（依 email-automation CLAUDE.md v1.1）`，讓團隊知道答案有參照本文件。

## 目前重點領域

[Sprint 2026-10]：附件支援（尚未開始，動工前先更新 docs/architecture.md）

## 變更紀錄

2026-10-18 v1.0.0 — 初始版本（依附錄 B 主模板，拆分為 docs/ 三檔）
2026-10-18 v1.1.0 — 「回答標註」規則從 docs/rules.md 搬到主檔（claude -p 實測：放在匯入檔 3 題都沒遵守）
