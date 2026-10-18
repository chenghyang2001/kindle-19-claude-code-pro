# NOTES — 第 17 章練習（CLAUDE.md 設計）＋附錄 B 團隊範本

快速模式：未經 QA/reviewer 流程，只做冒煙與單元測試。

## 做了什麼

| 項目 | 產出 |
| ------ | ------ |
| 練習 01 | `answer/ex01-answer.md`：根目錄 CLAUDE.md 五維度評分（平均 3.4）＋ 5 個反模式的壞例子與改法 |
| 練習 02 任務 1 | `answer/ex02-answer.md`：REST API / 前端 / CLI / 資料管線各 3 個重點 |
| 練習 02 任務 2 | 新建可跑的 `email-automation-演練/`（Python 標準庫，CLI＋9 個單元測試），並依附錄 B 主模板寫團隊版 `CLAUDE.md`，用 `@docs/architecture.md`、`@docs/rules.md`、`@docs/commands.md` 拆分 |
| 練習 02 任務 3 | 維護策略＋實作 `email-automation-演練/scripts/check_claude_md.py`（檢查 @匯入、文件內路徑、最後更新日期） |
| 附錄 B 驗證 | 用 `claude -p` 在專案內問 5 題（Q1–Q4 + Q2b），輸出存 `answer/claude-p-logs/` |

## 驗證結果

- 單元測試：`python -m unittest discover -s tests -v` → **9/9 OK**
- CLI dry-run：2 封預覽、略過 2 筆（格式錯誤 1、重複 1），exit 0
- `--send` 但沒設 SMTP 環境變數 → 清楚錯誤訊息，exit 1（沒有真的連 SMTP）
- 過時檢查腳本：正常 → 通過（exit 0）；在暫存區複製一份並刪匯入檔＋改舊日期 → 抓到 2 項（exit 1）
- `claude -p`（unset 所有 `CLAUDE*` 環境變數、`timeout 120`、禁用寫入工具）：
  - Q1 拒絕寫死密碼 ✅、Q2 給出只存在於 `docs/commands.md` 的指令（證明 `@` 匯入有載入）✅、Q3 拒絕把預設改成真寄信 ✅、Q4 拒絕直接加 pytest/jinja2 ✅
  - 「結尾加版本標記」規則：放在匯入檔（v1.0）時 0/3 遵守；搬到主檔（v1.1）後 2/2 遵守 → 已把 CLAUDE.md 升到 v1.1 並記在變更紀錄

## 和題目要求的差異

1. **`email-automation-演練/` 原本不存在**：題目假設 repo 裡已經有這個專案，實際上沒有。我自己建了一個最小版本，讓 CLAUDE.md 寫到的路徑和指令都能實際執行與檢查。
2. **團隊 CLAUDE.md 放在子專案，沒有覆蓋根目錄的 CLAUDE.md**：根目錄那份是演練流程的例外設定，覆蓋會影響本次作業流程。附錄 B 範本中與這個專案無關的欄位（前端、DB、Auth、85% 覆蓋率、E2E）已經刪掉或改寫，沒有照抄。
3. **真的寄信沒有測**：需要 SMTP 帳號和 App Password，只提供 `.env.example` 範本，並驗證沒設時會安全失敗。
4. **過時檢查腳本的限制**：只檢查行內反引號裡的路徑，``` 程式碼區塊（例如架構樹狀圖）裡的路徑不會檢查。
5. **小瑕疵**：Q4 的回答把引用行號寫錯（`rules.md:2`，正確是第 6 行），結論本身正確。
6. Markdown formatter hook 把 CLAUDE.md 檔頭的 `# 版本…` 註解行轉成 H1 標題，已手動改回一般文字行。
7. 依指示只在本機 commit，沒有 push，也沒有建 GitHub repo。
