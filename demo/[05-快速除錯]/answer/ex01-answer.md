# 練習 01 解答 — Stack Trace 解讀

## 任務 1：解讀錯誤

**1. 錯誤類型**
`ValueError` — 值的格式不符合預期。

**2. 錯誤發生位置**
`processor.py` 第 12 行（`parse_date` 函式內）。
呼叫鏈：`main.py:23` → `processor.py:45` → `processor.py:12`（最終爆點）。

**3. 根本原因**
程式碼只認識 `YYYY-MM-DD`（破折號分隔），但資料中出現了 `YYYY/MM/DD`（斜線分隔）。`strptime` 格式字串寫死，無法處理多種格式。

**4. 資料來源暗示**
`2024/01/15` 是典型的日本/台灣/中國本地 Excel 匯出格式，或舊系統 CSV。
說明資料來源不只一個，或換了輸入方式（例如原本系統匯出改成手動 Excel 填入）。

---

## 任務 2：修復程式碼

```python
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = [
    "%Y-%m-%d",   # 2024-01-15
    "%Y/%m/%d",   # 2024/01/15
    "%d-%m-%Y",   # 15-01-2024
]

def parse_date(s: str) -> Optional[datetime]:
    for fmt in SUPPORTED_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    logger.warning("無法解析日期格式：%r，回傳 None", s)
    return None
```

**關鍵設計決策：**
- 格式列表放函式外（`SUPPORTED_FORMATS`），加格式只改一處
- `try/except` 在迴圈內，每個格式獨立嘗試
- `Optional[datetime]` 型別標注，呼叫方知道可能拿到 `None`
