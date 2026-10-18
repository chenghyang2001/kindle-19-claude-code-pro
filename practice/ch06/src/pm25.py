"""練習 01 目標函式：計算 PM2.5 日均值。"""


def calculate_daily_avg(readings: list[float]) -> float:
    """計算有效 PM2.5 讀數的日均值。998 是感測器故障碼，需排除。"""
    valid = [r for r in readings if 0 <= r <= 500]
    return round(sum(valid) / len(valid), 2) if valid else 0.0
