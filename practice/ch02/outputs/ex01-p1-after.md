<!-- prompt: ex01/p1-after | ok | 72.5s -->

## 1. 重構後程式碼

```python
"""電商訂單金額計算：依會員等級與購買數量套用折扣，再套用滿額折抵。"""
from enum import IntEnum


class MemberLevel(IntEnum):
    """會員等級；不在此列舉中的值一律視為非會員。"""

    REGULAR = 1  # 一般會員
    VIP = 2      # VIP 會員


# 數量「超過」此值（不含）才算大量購買
BULK_QUANTITY_THRESHOLD = 10

# 折扣倍率；NO_DISCOUNT 刻意用 int 1，乘上去不會把整數結果變成 float，維持與原版相同的回傳型別
NO_DISCOUNT = 1
REGULAR_BULK_RATE = 0.9
VIP_BULK_RATE = 0.8
VIP_BASE_RATE = 0.95

# 小計「超過」此金額（不含）才折抵
REBATE_THRESHOLD = 1000
REBATE_AMOUNT = 50


def _discount_rate(member_level: int, quantity: int) -> float:
    """依會員等級與數量回傳折扣倍率。

    用 if/elif 比較而不是 dict 查表：原版用 `==` 比較，
    查表遇到不可雜湊的 member_level 會拋 TypeError，行為就變了。
    """
    is_bulk = quantity > BULK_QUANTITY_THRESHOLD
    if member_level == MemberLevel.REGULAR:
        return REGULAR_BULK_RATE if is_bulk else NO_DISCOUNT
    if member_level == MemberLevel.VIP:
        return VIP_BULK_RATE if is_bulk else VIP_BASE_RATE
    return NO_DISCOUNT


def calculate_order_total(unit_price: float, member_level: int, quantity: int) -> float:
    """計算訂單應付金額。

    Args:
        unit_price: 商品單價。
        member_level: 會員等級（1=一般會員、2=VIP、其他=非會員）。
        quantity: 購買數量。

    Returns:
        折扣後金額；若超過 REBATE_THRESHOLD 再折抵 REBATE_AMOUNT。
        全程沒有折扣時，整數輸入會回傳整數（與原版一致）。
    """
    subtotal = unit_price * quantity
    total = subtotal * _discount_rate(member_level, quantity)
    if total > REBATE_THRESHOLD:
        total -= REBATE_AMOUNT
    return total


def calc(p: float, t: int, q: int) -> float:
    """舊介面相容層：保留 calc(p, t, q) 簽名（含關鍵字參數名稱），內部轉呼叫新函式。"""
    return calculate_order_total(p, t, q)


if __name__ == "__main__":
    assert calc(100, 1, 11) == 990.0   # 一般會員大量：1100 × 0.9 = 990，未超過 1000 不折抵
    assert calc(100, 2, 5) == 475.0    # VIP 少量：500 × 0.95
    assert calc(50, 3, 30) == 1450     # 非會員：1500 > 1000，折抵 50
    assert type(calc(50, 3, 30)) is int  # 回傳型別也和原版相同
    print("全部通過")
```

## 2. 改了什麼、為什麼

1. **魔術數字改成具名常數，等級改用 `IntEnum`**：`0.9`、`10`、`1000`、`50` 這些數字現在都有名稱。`MemberLevel` 繼承 `int`，所以 `t == 1` 的比較結果和原版一樣。
2. **拆出 `_discount_rate`**：原版每個分支都重複寫 `p * q`，現在先算一次小計，再乘上倍率。巢狀 if 改成提前 return，讀起來比較直。
3. **保留浮點運算順序和回傳型別**：原版算法是 `(p*q)*0.9`，新版也是先算小計再乘倍率，捨入誤差和原版相同。沒有折扣時乘的是整數 `1` 而不是 `1.0`，所以 `calc(50,3,30)` 仍然回傳整數 `1450`，不會變成 `1450.0`。
4. **加上相容層**：新增語意清楚的 `calculate_order_total`。原本的 `calc(p, t, q)` 保留下來，參數名稱不變，用關鍵字呼叫（例如 `calc(p=…, t=…, q=…)`）也能照常運作。
5. **加上型別提示和繁中 docstring**：特別標明「超過」是嚴格大於（`> 10`、`> 1000`），以後的人才不會誤改成 `>=`。

## 3. 證明行為不變的 assert

```python
assert calc(100, 1, 11) == 990.0   # 一般會員 + 大量折扣（剛好沒超過 1000）
assert calc(100, 2, 5) == 475.0    # VIP 基本 95 折
assert calc(50, 3, 30) == 1450     # 非會員，超過 1000 折抵 50
```

另外兩個邊界值也可以拿來核對：`calc(100, 1, 10)` 會回傳 `1000`（數量剛好 10，沒有大量折扣，金額也剛好不超過 1000，所以不折抵）；`calc(100, 2, 11)` 會回傳 `830.0`（1100 × 0.8 = 880，沒超過 1000）。

這次只在回覆中提供程式碼，沒有寫成檔案，也沒有在本機實際執行。上面的 assert 結果是我逐一手算核對的。
