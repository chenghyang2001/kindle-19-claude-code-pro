# Exercise 02 解答 — 設定 Hooks

## 任務 1：PostToolUse Hook（寫 .py 時自動格式化）

### settings.json 片段

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c \"echo '$CLAUDE_TOOL_RESULT' | python3 -c \"import json,sys; r=json.load(sys.stdin); path=r.get('filePath',''); exit(0 if not path.endswith('.py') else 0)\" && ruff format \"$(echo '$CLAUDE_TOOL_RESULT' | python3 -c 'import json,sys; print(json.load(sys.stdin).get(\\\"filePath\\\",\\\"\\\"))')\" 2>/dev/null || true\""
          }
        ]
      }
    ]
  }
}
```

### 更簡潔的設計（推薦）

實務上 settings.json 的 command 不適合放複雜邏輯，改用外部腳本：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/format_py.py"
          }
        ]
      }
    ]
  }
}
```

對應 `~/.claude/hooks/format_py.py` 的邏輯（偽碼說明）：
```
1. 從 stdin 讀 JSON（CLAUDE_TOOL_RESULT）
2. 取出 filePath
3. 若不以 .py 結尾 → 直接 exit(0)
4. 嘗試執行 ruff format <filePath>
5. 失敗（ruff 未安裝 / 格式錯誤）→ 寫入 stderr log，exit(0)（靜默失敗）
6. 成功 → exit(0)
```

### 關鍵設計決策：靜默失敗

```bash
ruff format "$FILE" 2>/dev/null || true
# ↑ 失敗不回傳非零 exit code → Claude 工作流不中斷
```

**為什麼不用 black？**
- `ruff format` 速度比 `black` 快 10-100x（Rust 實作）
- `ruff` 同時處理 lint + format，只需裝一個工具
- 2024 年後 Python 社群主流已轉向 ruff

### 測試步驟
1. 讓 Claude 寫一個格式不標準的 .py 檔（例如縮排混亂）
2. 觀察 Write 工具執行後是否自動觸發 `ruff format`
3. 讀取檔案確認縮排已被標準化

---

## 任務 2：SessionStart Hook（顯示 git 工作狀態）

### settings.json 片段

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c \"echo '=== Git 狀態 ===' && git branch --show-current 2>/dev/null && echo '--- 最近 3 commits ---' && git log --oneline -3 2>/dev/null && echo '--- 未提交變更 ---' && git status --short 2>/dev/null || echo '（非 git 專案）'\""
          }
        ]
      }
    ]
  }
}
```

### 輸出範例

```
=== Git 狀態 ===
main
--- 最近 3 commits ---
cfa9ee5 新增 Session 6：study-scaffold 互動式調整
9caf6a3 完成 Session 02：真正有效的提示詞技巧
f0d1390 完成 Session 01：從聊天機器人到開發夥伴
--- 未提交變更 ---
M  demo/[03]/answer/ex01-answer.md
```

### 為什麼這個 hook 對 Claude 有價值？

Claude Code 每個 session 都從零開始，不記得上次做到哪。
SessionStart hook 讓 Claude 在回答任何問題前，**先看到當前工作狀態**，
相當於自動執行「恢復工作情境」，避免它提出與當前 branch 不符的操作。

---

## 延伸思考：Hook 靜默失敗設計

| 失敗情境 | 危險做法 | 安全做法 |
|---------|---------|---------|
| ruff 未安裝 | hook exit(1) → Claude 停工 | `command || true`，記錄 stderr 但不中斷 |
| git 指令在非 git 目錄失敗 | hook 噴錯 | `git ... 2>/dev/null \|\| echo "(非 git 專案)"` |
| 格式化工具改名 / 路徑變更 | hook 失效且無提示 | 加版本檢查：`which ruff \|\| echo "WARNING: ruff 未安裝"` |

**原則**：Hook 是「加分項目」，不是「核心流程」。核心流程失敗才該停工；hook 失敗只需記錄。

---

## 學習洞察
Hook 的本質是「強制執行 CLAUDE.md 做不到的事」：
- CLAUDE.md 說「請每次格式化」→ Claude 可能忘記
- PostToolUse Hook → **每次一定跑**，不依賴 Claude 記住
這就是文件描述的「CLAUDE.md 是 context，Hook 是 enforcement」的實際意義。
