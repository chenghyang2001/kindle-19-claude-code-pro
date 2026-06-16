---
paths:
  - "demo/**/*.py"
  - "email-automation-演練/**/*.py"
  - "freelancer-dashboard/**/*.py"
---

# Python 程式碼規則（按需載入）

> 只在存取 .py 檔案時載入。

## 必要前置

Windows 環境執行 Python 必須加 `PYTHONUTF8=1`：

```bash
PYTHONUTF8=1 python3 script.py
```

## 標準檔案開頭

```python
"""模組說明（繁體中文）"""
import os
import sys
from pathlib import Path

def main():
    try:
        pass  # 主邏輯
    except Exception as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 路徑規則

禁止硬編碼：

```python
# 禁止
path = "C:/Users/B00332/workspace/..."

# 正確
path = Path.home() / "workspace" / "..."
```

## 每個 .py 必須有冒煙測試

```python
if __name__ == "__main__":
    # 至少一個 happy path 測試
    result = my_function("normal_input")
    assert result is not None, "基本測試失敗"
    print("✅ 冒煙測試通過")
```

## subprocess 呼叫

```python
# 必須加 encoding='utf-8'
result = subprocess.run(
    ["command", "arg"],
    capture_output=True,
    encoding='utf-8',
    check=True
)
```
