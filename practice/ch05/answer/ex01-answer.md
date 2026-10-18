# 練習 01 解答 — Stack Trace 解讀

> 實作檔案：`ex01/buggy/`（重現 bug）、`ex01/fixed/`（修復版＋測試）、`ex01/data/`（測試資料）
> 實際輸出：`ex01/traceback-before.txt`（修復前）、`ex01/run-after.txt`（修復後＋測試結果）

## 0. 先重現：自己做出同一個 traceback

照題目的行號寫了 `ex01/buggy/main.py`（第 23 行呼叫 `process_data`）與 `ex01/buggy/processor.py`（第 45 行 `apply`、第 12 行 `strptime`），餵一份混了 `2024/01/15` 的 CSV：

```
$ cd ex01/buggy && python main.py
讀到 3 筆，欄位：['id', 'timestamp', 'amount']
Traceback (most recent call last):
  File "~\...\ex01\buggy\main.py", line 23, in <module>
    result = process_data(df)
  File "~\...\ex01\buggy\processor.py", line 45, in process_data
    return df["timestamp"].apply(parse_date)
  File "...\pandas\core\series.py", line 5084, in apply        ← pandas 內部（共 7 層，略）
  ...
  File "pandas/_libs/lib.pyx", line 3071, in pandas._libs.lib.map_infer
  File "~\...\ex01\buggy\processor.py", line 12, in parse_date
    return datetime.strptime(s, "%Y-%m-%d")
  File "...\Lib\_strptime.py", line 555, in _strptime          ← 標準庫內部
ValueError: time data '2024/01/15' does not match format '%Y-%m-%d'
```

和題目的差別：真實 traceback 中間夾了 7 層 pandas 框架與 2 層 `_strptime` 框架。**讀 traceback 的技巧就是跳過第三方／標準庫的框架，只看自己專案的檔案**——剩下的三層正好就是題目給的那三層。

## 任務 1：解讀錯誤

| 問題 | 答案 |
| --- | --- |
| 1. 錯誤類型 | `ValueError`（值的型別對，但內容不符合預期格式） |
| 2. 發生位置 | 直接拋出點：`processor.py` 第 12 行 `parse_date()` 內的 `datetime.strptime(s, "%Y-%m-%d")`。往上追：由第 45 行 `process_data()` 的 `.apply(parse_date)` 呼叫，最外層是 `main.py` 第 23 行。 |
| 3. 根本原因 | 不是「某一筆資料壞掉」，而是 **`parse_date` 把日期格式寫死成單一 `%Y-%m-%d`，假設上游永遠只給 ISO 格式**，而且沒有任何容錯。結果只要一筆資料格式不同，`apply` 就整批中斷（前面成功的資料也全部丟掉）。附帶原因：資料進來時沒有做格式驗證／正規化。 |
| 4. 資料來源推測 | `2024/01/15` 是斜線分隔，典型來自 **Excel／Google Sheets 匯出的 CSV**（Windows 地區設定為 zh-TW、ja-JP 時預設短日期就是 `yyyy/MM/dd`），或人工手動輸入、另一套系統的匯出。代表資料來源不只一個，或有人手動編輯過檔案，之後很可能還會出現其他格式。 |

## 任務 2：修復程式碼

完整檔案：`ex01/fixed/processor.py`

```python
import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

# 依序嘗試。YYYY 開頭與 DD 開頭的格式靠「第一段是 4 位數還是 2 位數」自然區分，
# 不會互相誤判；但 DD-MM 與 MM-DD 無法區分，所以刻意不支援 MM-DD-YYYY。
SUPPORTED_FORMATS = (
    "%Y-%m-%d",  # 2024-01-15（原本支援）
    "%Y/%m/%d",  # 2024/01/15（Excel / 地區設定匯出常見）
    "%d-%m-%Y",  # 15-01-2024（預防性支援，歐洲慣例）
)


def parse_date(s):
    """把字串解析成 datetime；所有格式都失敗時 log 警告並回傳 None。"""
    if s is None or (not isinstance(s, str) and pd.isna(s)):
        logger.warning("parse_date 收到空值：%r", s)
        return None
    if not isinstance(s, str):
        logger.warning("parse_date 收到非字串：%r（型別 %s）", s, type(s).__name__)
        return None

    text = s.strip()
    for fmt in SUPPORTED_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    logger.warning("無法解析日期 %r，支援格式：%s", s, ", ".join(SUPPORTED_FORMATS))
    return None
```

設計重點：

- **格式清單集中成常數**，之後要加格式只改一處。
- **空值（None / NaN / pd.NA）** 也回 None 並警告——CSV 空欄位讀進 pandas 會變 NaN，不處理的話 `strptime` 會丟 `TypeError`。
- **前後空白先去掉**，`" 2024-01-15 "` 這種手動輸入很常見。
- **不合法的日期（2024-02-30）也會被擋下**，`strptime` 本身會驗證日期是否存在。
- 不支援 `MM-DD-YYYY`：`01-02-2024` 是 1 月 2 日還是 2 月 1 日無法判斷，寧可回 None 讓人處理，也不要靜默猜錯。

## 驗證結果（實際執行）

```
$ cd ex01/fixed && python main.py ../data/messy.csv
WARNING processor: 無法解析日期 'Jan 17 2024'，支援格式：%Y-%m-%d, %Y/%m/%d, %d-%m-%Y
WARNING processor: parse_date 收到空值：nan
WARNING processor: 無法解析日期 '2024-02-30'，支援格式：%Y-%m-%d, %Y/%m/%d, %d-%m-%Y
讀到 6 筆，欄位：['id', 'timestamp', 'amount']
0   2024-01-14
1   2024-01-15
2   2024-01-16
3          NaT
4          NaT
5          NaT

$ python -m pytest test_processor.py
17 passed
```

測試涵蓋（`ex01/fixed/test_processor.py`）：三種支援格式＋前後空白、traceback 中那個原始值、5 種無法解析的字串（含 `MM-DD-YYYY` 與不存在的 2/30）、3 種空值、非字串、`sample.csv` 與 `messy.csv` 整合測試、缺欄位時仍拋 `KeyError`。

## 補充：後續建議

- 回傳 None 之後，呼叫端要決定怎麼處理（丟棄、標記、寄通知），不然壞資料會在下游悄悄變成 `NaT`。
- 資料量大時可改用 `pd.to_datetime(..., format="mixed", errors="coerce")` 向量化處理，效能比逐列 `apply` 好很多；但它會把 `MM-DD` 與 `DD-MM` 自行猜測，需搭配 `dayfirst` 參數小心使用。
