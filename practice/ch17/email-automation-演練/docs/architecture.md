# 架構與資料夾結構

```
email-automation-演練/
├── CLAUDE.md                  # 團隊版 Claude 上下文（主檔，只放摘要與 @ 匯入）
├── docs/                      # CLAUDE.md 拆出的細節
├── email_automation/
│   ├── cli.py                 # 命令列入口，組裝流程、處理錯誤碼
│   ├── templates.py           # 範本載入（第一行 Subject:）與 $變數 渲染
│   ├── recipients.py          # CSV 名單讀取、email 格式驗證、去重
│   └── sender.py              # dry-run / SMTP 寄送、環境變數檢查、寄信間隔
├── templates/welcome.txt      # 範例範本
├── data/recipients.csv        # 範例名單（只用 example.com）
├── tests/test_core.py         # 單元 + 端到端（dry-run）測試
├── scripts/check_claude_md.py # CLAUDE.md 過時檢查
└── .env.example               # SMTP 環境變數範本
```

資料流：`cli.py` → `load_template` + `load_recipients` → `render` → `build_message` → `send_all(dry_run)`

分層原則：只有 `sender.py` 可以 import `smtplib`；其他模組不得接觸網路。
