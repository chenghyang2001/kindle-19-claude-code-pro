# 練習 01 — 基礎：MCP 工具探索

## 情境說明
你安裝了幾個 MCP server，但不確定每個能做什麼、什麼時候最適合用。

## 任務

### 任務 1：建立 MCP 能力地圖
列出你目前環境中已啟用的 MCP server（在 `settings.json` 中可以看到），為每個建立能力地圖：

| MCP Server | 提供的 Tools | 適合場景 | 限制 / 注意事項 |
|-----------|------------|---------|--------------|
| github | list_issues, create_pr, ... | 管理 GitHub 專案 | 需要有 repo 存取權限 |
| gmail | search_emails, send_email, ... | 信件自動化 | 只能存取已授權帳號 |
| ... | ... | ... | ... |

### 任務 2：MCP vs 直接 API 比較
選一個你熟悉的 MCP server（例如 GitHub MCP），比較兩種使用方式：

**方式 A：透過 MCP**
用 Claude Code 直接呼叫 MCP tool 完成一個任務（例如：列出本週 open issues）

**方式 B：直接呼叫 REST API**
用 curl 或 Python 呼叫相同的 API 完成同樣任務

比較：
- 程式碼複雜度
- 設定成本（首次使用的準備工作）
- 適合的使用場景

## 完成後
將 MCP 能力地圖 + 比較結果存入 `answer/ex01-answer.md`
