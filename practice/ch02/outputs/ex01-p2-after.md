<!-- prompt: ex01/p2-after | ok | 58.9s -->

1. **根因**
   - 函式沒有先檢查清單是不是空的，所以 `average_score([])` 會執行 `total / 0`，拋出 `ZeroDivisionError`。
   - 另外 `total += s` 遇到 `None` 會拋出 `TypeError`，而且 `len(scores)` 把缺考也算進分母。要先把 `None` 過濾掉，再判斷剩下的分數是不是空的。

2. **修正後完整程式碼**

```python
"""範例：平均分數計算（已修正空清單與 None 分數問題）"""


def average_score(scores):
    """計算平均分數，四捨五入到小數 2 位。

    None 視為缺考，不列入計算；
    空清單或全部為 None 時回傳 None（沒有可計算的分數）。
    """
    # 用 is not None 判斷，避免把 0 分誤當缺考濾掉
    valid_scores = [s for s in scores if s is not None]
    if not valid_scores:
        return None
    return round(sum(valid_scores) / len(valid_scores), 2)


if __name__ == "__main__":
    print(average_score([80, 90, 100]))
    print(average_score([]))
```

3. **4 個 assert 測試案例**

```python
assert average_score([80, 90, 100]) == 90.0        # 正常
assert average_score([]) is None                   # 空清單
assert average_score([80, None, 91]) == 85.5       # 含 None：只算 80、91
assert average_score([None, None]) is None         # 全 None
```

補充：
- 過濾 `None` 時用的是 `s is not None`，不是 `if s`，所以 0 分會照常計入平均，不會被當成缺考。
- 以上測試是我手動推算的結果，沒有實際執行過。
