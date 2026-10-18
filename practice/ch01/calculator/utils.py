"""計算機的四則運算函式。"""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    # 明確拋錯，避免回傳 inf 或讓呼叫端拿到不明的 ZeroDivisionError 訊息
    if b == 0:
        raise ValueError("除數不可為 0")
    return a / b
