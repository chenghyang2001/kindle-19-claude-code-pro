<!-- prompt: ex01/p2-before | ok | 59.0s -->

## 問題在哪

| 情境 | 出錯的地方 | 錯誤 |
| --- | --- | --- |
| `average_score([])` | `total / len(scores)`，分母是 0 | `ZeroDivisionError` |
| `average_score([80, None])` | `total += s`，`int + None` | `TypeError` |
| `average_score(None)` | `for s in scores` | `TypeError: 'NoneType' is not iterable` |

## 修正版

```python
"""計算平均分數：略過 None，沒有有效分數時回傳 None"""
import math


def average_score(scores):
    """回傳有效分數的平均（四捨五入到小數 2 位）。

    - scores 為 None 或空清單 → 回傳 None（「沒有平均」不等於「平均 0 分」）
    - 個別分數為 None → 視為缺考，略過不計
    - 非數字（如字串、NaN）→ 拋 TypeError / ValueError，不讓壞資料默默混進平均
    """
    if scores is None:
        return None

    valid_scores = []
    for s in scores:
        if s is None:
            continue
        # bool 是 int 的子類別，True 會被當成 1 分，要明確排除
        if isinstance(s, bool) or not isinstance(s, (int, float)):
            raise TypeError(f"分數必須是數字，收到 {s!r}（{type(s).__name__}）")
        if math.isnan(s):
            raise ValueError("分數不可為 NaN")
        valid_scores.append(s)

    if not valid_scores:
        return None
    return round(sum(valid_scores) / len(valid_scores), 2)


if __name__ == "__main__":
    # 正常案例
    assert average_score([80, 90, 100]) == 90.0
    assert average_score([85, 90]) == 87.5
    # 邊界案例
    assert average_score([]) is None
    assert average_score(None) is None
    assert average_score([None, None]) is None
    assert average_score([80, None, 100]) == 90.0  # None 不算進分母
    # 錯誤案例
    for bad in (["80"], [True], [float("nan")]):
        try:
            average_score(bad)
            raise AssertionError(f"{bad} 應該要拋錯")
        except (TypeError, ValueError):
            pass
    print("全部測試通過")
```

## 幾個設計決定（可依需求調整）

1. **空清單回傳 `None`，不是 `0`**：回傳 0 的話，呼叫端分不出「真的考 0 分」和「沒有資料」。如果你的情境比較適合直接報錯，就把 `return None` 改成 `raise ValueError("沒有有效分數")`。
2. **`None` 不算進分母**：`[80, None, 100]` 的結果是 90，不是 60。如果缺考要算 0 分，就改成 `valid_scores.append(0)`。
3. **字串 `"80"` 直接拋錯，不自動轉型**：自動轉型會把資料來源的問題藏起來，所以讓它早點報錯。

呼叫端記得處理 `None`，例如 `avg = average_score(xs); print(avg if avg is not None else "無資料")`。

你只貼了程式碼，沒有指定檔案，所以我沒有改動任何檔案，上面的測試也沒有實際執行過。要我寫進檔案並跑一次測試的話，跟我說路徑就好。
