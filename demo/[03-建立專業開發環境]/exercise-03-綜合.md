# 練習 03 — 綜合挑戰：MCP 環境配置

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
完成你個人開發環境的完整 MCP 整合設定。

## 要求

1. **加入一個 MCP server**
   在 `settings.json` 中加入一個你實際會用到的 MCP server：
   - GitHub MCP（PR / Issue 管理）
   - Google Drive MCP（檔案存取）
   - 或其他你有的 MCP
   
   記錄：設定過程、遇到的問題、如何驗證它可用

2. **寫最小測試**
   設計並執行一個測試，確認 MCP 工具可以被 Claude Code 呼叫：
   - 呼叫什麼工具？
   - 傳入什麼參數？
   - 期望看到什麼回應？

3. **更新 CLAUDE.md**
   在 CLAUDE.md 中加入「可用 MCP 工具」章節，格式如下：
   
   | 工具名稱 | 何時使用 | 注意事項 |
   |---------|---------|---------|
   | mcp__github__list_issues | 查詢 GitHub Issue 時 | 需要有 repo 存取權限 |
   | ... | ... | ... |

## 完成標準
- [ ] settings.json 中有至少一個 MCP server 配置
- [ ] MCP 工具測試成功執行
- [ ] CLAUDE.md 的「可用 MCP 工具」章節完成

## 完成後
將解答存入 `answer/ex03-answer.md`
