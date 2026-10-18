# 開發指令（在 `email-automation-演練/` 目錄下執行，Windows 加 `PYTHONUTF8=1`）

| 目的 | 指令 |
| ------ | ------ |
| 跑測試 | `python -m unittest discover -s tests -v` |
| 預覽（dry-run，不寄信） | `python -m email_automation.cli --template templates/welcome.txt --recipients data/recipients.csv` |
| 真的寄出 | 先設好 `.env.example` 列的 4 個環境變數，再加 `--send` |
| 檢查 CLAUDE.md 是否過時 | `python scripts/check_claude_md.py` |

部署：本專案是本機 CLI，無部署步驟；若要排程寄信，用系統排程器呼叫上面的「真的寄出」指令。
