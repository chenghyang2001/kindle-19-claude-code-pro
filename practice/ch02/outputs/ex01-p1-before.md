<!-- prompt: ex01/p1-before | ok | 61.8s -->

這段程式只在對話裡貼出來，沒有對應的檔案，所以我直接在這裡回覆，不寫檔。重構後的**行為和原版完全一樣**（包含浮點數的乘法順序），只改可讀性：

```python
"""計算訂單金額：依客戶類型與數量套用折扣，金額超過門檻再折抵固定金額。"""

BULK_QUANTITY_THRESHOLD = 10      # 數量「大於」此值才算大量購買
REBATE_THRESHOLD = 1000           # 金額「大於」此值才折抵
REBATE_AMOUNT = 50

# 客戶類型 -> (一般折扣率, 大量購買折扣率)
# 不在表中的類型一律不打折，對應原本的 else 分支
DISCOUNT_RATES = {
    1: (1.0, 0.9),
    2: (0.95, 0.8),
}
NO_DISCOUNT = (1.0, 1.0)


def calculate_order_total(unit_price, customer_type, quantity):
    """回傳折扣與折抵後的訂單金額。"""
    normal_rate, bulk_rate = DISCOUNT_RATES.get(customer_type, NO_DISCOUNT)
    is_bulk = quantity > BULK_QUANTITY_THRESHOLD
    rate = bulk_rate if is_bulk else normal_rate

    total = unit_price * quantity * rate
    if total > REBATE_THRESHOLD:
        total -= REBATE_AMOUNT
    return total


if __name__ == "__main__":
    # 冒煙測試：與原版 calc 逐一比對，確認行為沒變
    def calc(p, t, q):
        if t == 1:
            r = p * q * 0.9 if q > 10 else p * q
        elif t == 2:
            r = p * q * 0.8 if q > 10 else p * q * 0.95
        else:
            r = p * q
        if r > 1000:
            r = r - 50
        return r

    cases = [
        (p, t, q)
        for p in (0, 1, 9.99, 50, 100, 101)
        for t in (0, 1, 2, 3, None)
        for q in (0, 1, 10, 11, 20)
    ]
    for p, t, q in cases:
        assert calculate_order_total(p, t, q) == calc(p, t, q), (p, t, q)
    print(f"全部 {len(cases)} 組與原版一致")
```

**改了什麼**
- **命名**：`p/t/q/r` 改成 `unit_price/customer_type/quantity/total`。
- **魔術數字**：`10`、`1000`、`50` 和各個折扣率都改成具名常數，集中在檔案上方。
- **重複邏輯**：原本的兩層 if/else 合併成一張折扣表。以後要加新的客戶類型，只要在 `DISCOUNT_RATES` 加一行。
- **乘法順序不變**：還是先算 `unit_price * quantity` 再乘折扣率，所以結果和原版一位不差，包括浮點數。比對測試直接用 `==`，沒有用近似值。

**請跟同事確認幾件事**（這次我刻意保留原本的行為，沒有改）
1. `t == 1` / `t == 2` 實際代表什麼（會員等級？通路？）。確認後可以把 key 換成 `Enum`，常數也能取更準確的名字。
2. 未知的 `customer_type` 目前一律不打折，也不會報錯。這是刻意的設計，還是應該拋出 `ValueError`？
3. 沒有檢查負數或 `None` 的價格和數量。原版也沒有檢查，所以我沒有加，免得改變行為。
4. 折抵用的是 `> 1000`，金額剛好 1000 不會折抵。要確認這是不是預期的規則。

測試區塊會把重構版和原版在 150 組輸入上逐一比對；我還沒有實際執行過，你可以跑 `PYTHONUTF8=1 python 檔名.py` 驗證。如果要把它寫進專案裡的 `.py` 檔，依你的規則會走 writer → QA 流程，告訴我路徑就好。
