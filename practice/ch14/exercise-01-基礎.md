# 練習 01 — 基礎：團隊 CLAUDE.md 設計

## 情境說明
你的團隊（3 人）正在開發一個電商後台，有前端工程師、後端工程師和 DevOps。大家都在使用 Claude Code，但每個人的 CLAUDE.md 都不一樣，導致 Claude 對同樣的問題給出不一致的答案。

## 任務

### 任務 1：找出 CLAUDE.md 的三類資訊
一份好的 CLAUDE.md 應該包含哪三類資訊？
- 「Claude 能做什麼」
- 「Claude 不能做什麼」
- 「Claude 需要知道的架構/環境資訊」

為電商後台專案設計一份 CLAUDE.md 範本，包含以上三類各至少 3 條規則。

### 任務 2：模組化 CLAUDE.md
當 CLAUDE.md 超過 100 行時，應該如何模組化？

設計一個模組化結構，將上述範本拆分成：
- 主 CLAUDE.md（只含引用和重要規則）
- `docs/api-conventions.md`（API 設計規範）
- `docs/db-rules.md`（資料庫操作規則）
- `docs/deploy-rules.md`（部署規則）

用 `@docs/xxx.md` 語法設計引用結構。

### 任務 3：角色專用 context
不同角色（前端 / 後端 / DevOps）需要不同的 context。如何在同一個專案中為不同角色提供不同的 CLAUDE.md？

提示：有哪些做法？各有什麼優缺點？

## 完成後
將設計文件存入 `answer/ex01-answer.md`
