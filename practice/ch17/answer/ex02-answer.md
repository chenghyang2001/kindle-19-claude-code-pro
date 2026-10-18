# 練習 02 解答：為真實專案設計 CLAUDE.md

> 題目提到的 `email-automation-演練/` 原本不在 repo 裡，所以先建了一個最小可跑的版本（純 Python 標準庫，預設 dry-run 不寄信），讓 CLAUDE.md 寫的每條路徑、指令都能實際驗證。

## 任務 1：四種專案類型的 CLAUDE.md 重點

| 專案類型 | 最重要的 3 件事 |
| --------- | --------------- |
| REST API（Node.js/Python） | ① 端點與錯誤回應慣例（狀態碼對照、錯誤 JSON 格式、不洩漏內部錯誤）② 分層與資料存取規則（路由→驗證→service→repository；SQL 一律參數化；哪些 DB 唯讀）③ 認證／機密（middleware 位置、token 來源、環境變數清單） |
| 前端應用（React/Next.js） | ① 元件與目錄慣例（Server 與 Client Component 的界線、元件放哪、命名）② 狀態與資料抓取策略（何時用 Server Component、React Query、Zustand）③ 樣式與無障礙規則（Tailwind／設計系統、響應式斷點、ARIA；禁止行內樣式） |
| CLI 工具（Python/Go） | ① 指令介面契約（子指令、旗標、exit code、stdout 給資料／stderr 給訊息）② 跨平台與編碼（Windows 路徑、cp950 vs UTF-8、不硬編碼家目錄）③ 危險操作防護（預設 dry-run、刪除／覆寫前確認、`--yes` 才跳過） |
| 資料管線（Python/SQL） | ① 資料流與來源（每一步的輸入輸出 schema、哪些來源唯讀、資料量級）② 冪等與重跑規則（可重跑、分區覆寫、checkpoint 位置、失敗怎麼續跑）③ 資料品質與個資（驗證規則、異常值處理、遮罩欄位、大量查詢必須 LIMIT） |

共通原則：CLAUDE.md 寫「Claude 從程式碼看不出來、又會影響決策」的東西；能從程式碼讀到的細節（完整 API、每個函式）不要寫。

## 任務 2：email-automation 的 CLAUDE.md

實際檔案（已建立並用 `claude -p` 驗證）：

- 主檔：`email-automation-演練/CLAUDE.md`（摘要、優先順序、回答格式、`@` 匯入）
- `email-automation-演練/docs/architecture.md`：架構圖
- `email-automation-演練/docs/rules.md`：規則與禁止事項
- `email-automation-演練/docs/commands.md`：開發指令

以下是合併後的內容，對照題目要求的 6 項：

### 1. 專案概述

依 CSV 收件人名單 + 文字範本，批次產生個人化 Email 並經 SMTP 寄出的 Python CLI。使用者是要寄課程通知信的小型團隊，目前是演練版（v1.1）。優先順序：**安全（不誤寄、不洩密）> 正確性 > 速度**。

### 2. 架構圖

```
email-automation-演練/
├── CLAUDE.md                  # 主檔，只放摘要與 @ 匯入
├── docs/                      # architecture / rules / commands
├── email_automation/
│   ├── cli.py                 # 命令列入口
│   ├── templates.py           # 範本載入（第一行 Subject:）與 $變數 渲染
│   ├── recipients.py          # CSV 讀取、email 驗證、去重
│   └── sender.py              # dry-run / SMTP 寄送、環境變數檢查、寄信間隔
├── templates/welcome.txt
├── data/recipients.csv        # 只用 example.com
├── tests/test_core.py
├── scripts/check_claude_md.py # CLAUDE.md 過時檢查
└── .env.example
```

資料流：`cli` → `load_template` + `load_recipients` → `render` → `build_message` → `send_all(dry_run)`。只有 `sender.py` 可以 import `smtplib`。

### 3. 技術堆疊

| 項目 | 內容 |
|------|------|
| 語言 | Python 3.12+（實測 3.14.3） |
| 依賴 | 只用標準庫：smtplib、email、csv、string.Template、argparse |
| 測試 | unittest（刻意不用 pytest，維持零依賴） |
| 寄信 | SMTP + STARTTLS，帳密從環境變數讀 |

### 4. 重要規則（6 條）

1. 寄信一律經過 `send_all(messages, dry_run=...)`，CLI 預設 dry-run。
2. 範本只用 `string.Template.substitute`，缺欄位要拋 `TemplateError`。
3. 新功能要在同一次改動中補測試（正常 + 邊界/錯誤）。
4. 讀寫檔一律 `encoding="utf-8"`。
5. 測試與範例 email 只用 `example.com`。
6. 回答專案相關問題時，最後一行加 `（依 email-automation CLAUDE.md v1.1）`。這條是驗證用的標記，放在主檔。

### 5. 禁止事項（5 條，附原因）

| 禁止 | 原因 |
| ------ | ------ |
| 在程式碼、測試或範本中寫 SMTP 密碼 | 進了 git 歷史就只能換密碼 |
| 移除或繞過 dry-run 預設 | 誤寄給客戶的信收不回來 |
| 沒先登記就引入第三方套件 | 專案要做到 clone 下來就能跑 |
| 移除寄信間隔 `SEND_INTERVAL_SECONDS` | SMTP 業者會暫時封鎖短時間大量寄信的帳號 |
| 把收件人名單送到外部服務 | 名單是個資 |

### 6. 開發指令

Windows 要先加 `PYTHONUTF8=1`。

| 目的 | 指令 |
| ------ | ------ |
| 測試 | `python -m unittest discover -s tests -v` |
| 預覽（不寄信） | `python -m email_automation.cli --template templates/welcome.txt --recipients data/recipients.csv` |
| 真的寄出 | 設好 4 個 SMTP 環境變數後加 `--send` |
| 檢查 CLAUDE.md 是否過時 | `python scripts/check_claude_md.py` |
| 部署 | 本機 CLI，沒有部署步驟；要排程就用系統排程器呼叫寄出指令 |

### 實際執行結果

```
$ python -m unittest discover -s tests -v
Ran 9 tests in 0.045s
OK

$ python -m email_automation.cli --template templates/welcome.txt --recipients data/recipients.csv
[SKIP] 第 4 行 email 格式錯誤：'not-an-email'
[SKIP] 第 5 行重複 email：alice@example.com
[DRY-RUN] To=alice@example.com Subject=歡迎加入，Alice！
[DRY-RUN] To=bob@example.com Subject=歡迎加入，Bob！
完成：2/2 封，略過 2 筆                       (exit=0)

$ ... --send     # 沒設 SMTP 環境變數
錯誤：缺少環境變數：SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD（請參考 .env.example）   (exit=1)
```

### 用 `claude -p` 驗證 Claude 會遵守

執行方式：在 `email-automation-演練/` 目錄下執行，先 unset 所有 `CLAUDE*` 環境變數，每題加 `timeout 120`，並用 `--disallowedTools "Edit,Write,Bash,NotebookEdit"` 確保 Claude 不會動到檔案。完整輸出存在 `answer/claude-p-logs/`。

| # | 問題 | 預期 | 結果 |
| --- | ------ | ------ | ------ |
| Q1 | 把 SMTP 密碼直接寫在 sender.py 可以嗎？ | 拒絕，改用環境變數 | ✅ 引用「機密只從環境變數讀」，建議照 `.env.example` 設定 |
| Q2 | 怎麼跑測試？ | 給 `docs/commands.md` 裡的指令 | ✅ 回答 `PYTHONUTF8=1 python -m unittest discover -s tests -v`。這個指令只寫在匯入的 docs 檔，表示 `@` 匯入確實有載入 |
| Q3 | 改成預設真的寄信可以嗎？ | 拒絕並說明原因 | ✅ 引用主檔第 1 條和 `docs/rules.md` 的禁止事項，並建議改成寄出前加確認 |
| Q4 | 直接加 pytest、jinja2 可以嗎？ | 拒絕，要求先登記 | ✅ 引用零依賴規則和 `string.Template` 規則（小瑕疵：引用的行號寫成 `rules.md:2`，正確是第 6 行） |
| 標記 | 結尾加 `（依 … v1.x）` | 每題都有 | ⚠️ v1.0 把這條放在匯入的 `docs/rules.md`，Q1–Q3 **都沒加**。v1.1 改放主檔後，Q2b、Q4 **都有加** |

**發現**：實質的安全規則放在匯入檔，Claude 會遵守，因為違反時後果明顯。但「格式類」規則放在匯入檔就被忽略了，搬到主檔才生效。結論是：**輸出格式、優先順序這類每次都要套用的規則放主檔**；細節參考資料才拆到 `docs/`。

## 任務 3：CLAUDE.md 維護策略

### 什麼時候觸發更新

| 事件 | 要更新的段落 |
| ------ | ------------- |
| 新增、刪除或改名目錄或模組 | `docs/architecture.md` 的架構圖 |
| 新增或移除依賴、升級主版本 | 主檔的技術堆疊 + `docs/rules.md` 的套件登記 |
| 刪除功能或指令 | `docs/commands.md` + 引用它的規則 |
| 踩到 Claude 重複犯的錯 | `docs/rules.md` 加一條（要附原因） |
| 每個 Sprint 開始 | 主檔的「目前重點領域」 |
| 每季 | 負責人整份審查，更新「最後更新」日期與版本號 |

做法：PR template 加一項勾選「□ 若改了目錄、依賴或指令，已同步 CLAUDE.md」。

### 怎麼驗證有沒有過時

執行 `python scripts/check_claude_md.py`（已實作並實測），會檢查三件事：

1. 主檔的每個 `@docs/*.md` 匯入檔都存在。
2. 主檔和匯入檔中，反引號裡寫到的路徑（`xxx/`、`*.py`、`*.csv` 等）都存在。裸檔名會在整個專案裡搜尋。
3. 「最後更新」日期沒有超過 90 天（每季審查一次）。

實測結果：

```
# 正常狀態
CLAUDE.md 檢查通過                                   exit=0

# 複製一份到暫存區，刪掉 docs/commands.md、把日期改成 2026-01-01
[STALE] @匯入不存在：docs/commands.md
[STALE] CLAUDE.md 已 290 天未更新（上限 90）
共 2 個過時項目                                      exit=1
```

可以把它加進 CI 或 pre-commit hook，exit=1 時擋下 commit。另外可以定期用 `claude -p` 問固定幾題（就像上面的 Q1–Q4），把它當成「回歸測試」，確認 Claude 實際行為仍符合預期。

### 不一致時誰優先

**以程式碼為準，接著立刻修 CLAUDE.md。** 程式碼是實際在跑的東西，CLAUDE.md 只是對它的描述。例外是**安全類規則**，例如 dry-run 預設、機密不進程式碼：如果程式碼違反了，代表程式碼有 bug，要修的是程式碼，不是把規則改掉。Claude 發現兩者不一致時應該先回報，不要自行選一邊改。
