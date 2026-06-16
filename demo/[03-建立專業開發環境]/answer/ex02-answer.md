# 練習 02 解答：設定 Hooks

## 任務 1：PostToolUse Hook（寫入 .py 時自動格式化）

### 完整 settings.json 片段

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python -c \"\nimport sys, subprocess, json\ndata = json.load(sys.stdin)\npath = data.get('tool_input', {}).get('file_path', '')\nif not path.endswith('.py'):\n    sys.exit(0)\nresult = subprocess.run(['ruff', 'format', path], capture_output=True, text=True)\nif result.returncode != 0:\n    print(f'[hook] ruff format failed: {result.stderr}', file=sys.stderr)\n\""
          }
        ]
      }
    ]
  }
}
```

### 關鍵設計決策

- `matcher: "Write"` — 只攔 Write 工具
- `.endswith('.py')` 在 Python 內判斷（matcher 不支援 glob pattern）
- `returncode != 0` 時只印 stderr，`sys.exit(0)` 讓流程繼續，不中斷

### 測試步驟

1. 用 Claude Code 建立格式不整齊的 .py（例如 `x=1+2`，無空格）
2. 寫入後查看檔案，確認已被 ruff 改成 `x = 1 + 2`
3. 卸載 ruff（`pip uninstall ruff`），再寫一次，確認工作流程不中斷，只在 stderr 看到 hook 警告

---

## 任務 2：SessionStart Hook（顯示工作狀態）

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c \"echo '=== Git 狀態 ===' && git branch --show-current && echo '--- 最近 3 commits ---' && git log --oneline -3 && echo '--- 未提交變更 ---' && git status --short || echo '（非 git 目錄）'\""
          }
        ]
      }
    ]
  }
}
```

### 每次 claude 啟動時輸出範例

```
=== Git 狀態 ===
main
--- 最近 3 commits ---
aa955c4 完成 Lesson 02：真正有效的提示詞技巧
6497db3 新增 epub/README.md
cd65155 重新命名 EPUB
--- 未提交變更 ---
M  src/app.py
```

---

## 延伸思考：靜默失敗設計

三層防禦：

| 層 | 做法 | 效果 |
|----|------|------|
| 指令層 | `sys.exit(0)`（Python）或 `command \|\| true`（bash） | hook crash 不影響 Claude |
| 工具層 | `which ruff \|\| exit 0` 先確認工具存在 | 工具未安裝靜默跳過 |
| 通知層 | 錯誤只寫 `stderr`，不寫 `stdout` | Claude Code 不會把錯誤訊息當指令輸出 |

**核心原則：hook 的角色是「旁觀者」，不是「守門員」。**

守門員失職會擋住整條流程；旁觀者失職只是少做了一件事。格式化 hook 屬於後者 — 失敗最差結果是程式碼沒被格式化，不是整個工作流程卡死。
