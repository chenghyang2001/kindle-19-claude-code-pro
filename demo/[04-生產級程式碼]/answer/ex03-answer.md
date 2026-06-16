# 練習 03 解答 — 自動化品質守門

## 任務 1：PreToolUse Hook 架構設計

在 Claude Code 寫入 `.py` 前攔截，掃描即將寫入的內容：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python -c \"\nimport sys, json, re\ndata = json.load(sys.stdin)\npath = data.get('tool_input', {}).get('file_path', '')\nif not path.endswith('.py'):\n    sys.exit(0)\ncontent = data.get('tool_input', {}).get('content', '')\nrules = [\n    (r'execute\\s*\\(\\s*f[\\\"\\']', 'SQL 注入風險', '改用參數化查詢：cursor.execute(sql, (val,))'),\n    (r'password\\s*=\\s*[\\\"\\'][^\\\"\\']+[\\\"\\']', '機密硬編碼', '改用 os.environ[\\\"DB_PASS\\\"]'),\n    (r'(secret|api_key|token)\\s*=\\s*[\\\"\\'][^\\\"\\']+[\\\"\\']', '機密硬編碼', '改用 os.environ[\\\"KEY_NAME\\\"]'),\n]\nfound = []\nfor i, line in enumerate(content.splitlines(), 1):\n    for pattern, label, fix in rules:\n        if re.search(pattern, line, re.IGNORECASE):\n            found.append((i, label, line.strip(), fix))\nif found:\n    print('[QUALITY GATE] 發現問題，建議修正後再寫入：')\n    for lineno, label, code, fix in found:\n        print(f'  行 {lineno} [{label}]')\n        print(f'    程式碼：{code}')\n        print(f'    修正：{fix}')\n    sys.exit(2)\n\""
          }
        ]
      }
    ]
  }
}
```

**關鍵設計決策**：
- `sys.exit(2)` → Claude Code 把 exit code ≠ 0 視為 block，停止 Write
- 只掃 `.py`，其他副檔名直接 `sys.exit(0)` 放行
- 掃的是即將寫入的 `content`（PreToolUse），不是硬碟上的舊檔案
- PreToolUse 比 PostToolUse 更好：**事前阻止比事後補救便宜 10 倍**

## 任務 2：輸出格式範例

當發現問題時的實際輸出：

```
[QUALITY GATE] 發現問題，建議修正後再寫入：
  行 8 [SQL 注入風險]
    程式碼：cursor.execute(f"SELECT * FROM users WHERE id={user_id}")
    修正：改用參數化查詢：cursor.execute(sql, (val,))

  行 12 [機密硬編碼]
    程式碼：password='supersecret123'
    修正：改用 os.environ["DB_PASS"]

⛔ 寫入已中止。修正上述問題後重新產生程式碼。
```

## 任務 3：quality-rules.md（5 條規則）

| # | Pattern（正規表達式） | 危險原因 | 正確替代方式 |
|---|---------------------|---------|------------|
| 1 | `execute\s*\(\s*f["']` | f-string 拼接 SQL → 注入漏洞 | `cursor.execute(sql, (val,))` 參數化 |
| 2 | `password\s*=\s*["'][^"']+["']` | 密碼硬編碼進程式碼 | `os.environ["DB_PASS"]` |
| 3 | `(secret\|api_key\|token)\s*=\s*["'][^"']+["']` | 機密寫死 → git 永久洩漏 | `os.environ["SECRET_KEY"]` |
| 4 | `except:\s*$` | 裸 except 吞掉所有例外（含 KeyboardInterrupt） | `except pymysql.Error as e:` 具體類型 |
| 5 | `subprocess.*shell=True` | shell injection，使用者輸入可注入 shell 指令 | `subprocess.run(["cmd", arg])` list 形式 |

## 核心洞察

這個 PreToolUse hook 把練習 02 checklist 的第 1、2 項「機器化」。

**三層品質防線**：
1. **PreToolUse hook**（本文）— 寫入前阻擋，最早、成本最低
2. **PostToolUse hook**（Lesson 03）— 寫入後格式化（ruff）
3. **pre-commit / CI** — commit 前 / push 後掃全域

工具能做的事就不要靠人的記憶，這是生產級工程與學生作業的根本差異。
