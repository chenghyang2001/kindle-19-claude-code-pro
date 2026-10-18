# 練習 02 — 進階：個人化 Prompt 庫建立

## 任務

### 任務 1：建立個人 Prompt 庫結構
設計一個 Markdown 格式的個人 Prompt 庫，可以在 Claude Code 中快速存取：

建立 `~/.claude/prompts/` 目錄結構：
```
~/.claude/prompts/
  code/        — 程式碼相關
  review/      — 審查相關
  writing/     — 文件撰寫相關
  debug/       — 除錯相關
  README.md    — 索引，說明每個 Prompt 的用途
```

為每個目錄設計至少 2 個 Prompt 檔案，格式：
```markdown
# Prompt 名稱

## 用途
什麼場景下使用

## 模板
---
[Prompt 內容]
---

## 使用說明
如何填入變數
```

### 任務 2：設計「Prompt 進化」機制
一個 Prompt 第一次用可能效果不好。設計一個追蹤 Prompt 效果的方法：
- 如何記錄「這個 Prompt 的效果」？
- 什麼情況下要優化 Prompt？
- 優化方向（更多範例 / 更嚴格格式 / 調整角色 / 加約束條件）？

## 延伸思考
如果你的團隊也要共用 Prompt 庫，要如何設計「Prompt 版本控制」？

## 完成後
將 Prompt 庫結構 + 進化機制存入 `answer/ex02-answer.md`
