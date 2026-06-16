# 提示詞範本：新 Session 快速恢復

> 每次開新的 Claude Code session 時，貼此提示詞快速恢復學習情境。

---

## 完整版（適合跨日後第一次）

```
這是《Claude Code Pro》學習專案。請讀取以下文件恢復情境：
1. CLAUDE.md — 專案架構說明
2. .claude/decisions.md — 過去的學習決策
3. .claude/gotchas.md — 已知踩坑
4. ~/.claude/projects/.../memory/MEMORY.md — 長期學習記憶

讀完後告訴我：
- 目前學到第幾課？
- 哪些課已完成？
- 下一步應該做什麼？
```

---

## 精簡版（同日繼續）

```
繼續《Claude Code Pro》學習。
目前做到第NN課。請確認 .claude/decisions.md 有記錄最新決策。
```

---

## 驗證版（驗證 CLAUDE.md 有效性）

```
Without me telling you anything, describe this project:
the tech stack, the folder structure, the conventions,
and the things I've asked you never to do.
```

通過標準：正確辨識技術棧版本 + 架構職責 + 禁忌規範。
