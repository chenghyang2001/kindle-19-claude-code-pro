"""示範用的訂單工具函式（刻意留有幾個問題，給審查/除錯/重構模板當素材）"""


def calc_total(items, discount=0):
    total = 0
    for i in items:
        total = total + i["price"] * i["qty"]
    if discount > 0:
        total = total - total * discount / 100
    return round(total, 2)


def average_price(items):
    # 空清單時會 ZeroDivisionError（故意保留，給除錯模板用）
    return sum(i["price"] for i in items) / len(items)


if __name__ == "__main__":
    demo = [{"price": 100, "qty": 2}, {"price": 50, "qty": 1}]
    print("total =", calc_total(demo, discount=10))
    print("avg   =", average_price(demo))
