"""練習 02 的 starter 函式：依 PM2.5 讀數判定場域警示等級。"""

FAULT_CODE = 998
VALID_MIN, VALID_MAX = 0, 500

# 等級門檻採台灣環境部 PM2.5 指標的簡化版（μg/m³，上限為含）
LEVEL_THRESHOLDS = [
    (15.4, "良好"),
    (35.4, "普通"),
    (54.4, "對敏感族群不健康"),
    (150.4, "不健康"),
    (250.4, "非常不健康"),
]
HAZARDOUS = "危害"


def classify_alert_level(readings: list[float], min_valid_ratio: float = 0.75) -> dict:
    """依一組 PM2.5 讀數回傳警示等級。

    規則：
    - readings 不是 list → TypeError；元素不是數字（含 bool）→ TypeError
    - min_valid_ratio 必須在 (0, 1] → 否則 ValueError
    - 998 視為故障；其他超出 [0, 500] 的值視為無效
    - 有效比例 < min_valid_ratio（或沒有讀數）→ level 為 "資料不足"
    - 否則以有效讀數均值（四捨五入到 1 位）對照門檻
    """
    if not isinstance(readings, list):
        raise TypeError("readings 必須是 list")
    if not 0 < min_valid_ratio <= 1:
        raise ValueError("min_valid_ratio 必須介於 (0, 1]")
    for value in readings:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"讀數必須是數字，收到 {value!r}")

    fault_count = sum(1 for r in readings if r == FAULT_CODE)
    valid = [r for r in readings if VALID_MIN <= r <= VALID_MAX]
    total = len(readings)
    valid_ratio = len(valid) / total if total else 0.0

    if not valid or valid_ratio < min_valid_ratio:
        return {"level": "資料不足", "avg": None,
                "valid_ratio": round(valid_ratio, 2), "fault_count": fault_count}

    avg = round(sum(valid) / len(valid), 1)
    level = next((name for limit, name in LEVEL_THRESHOLDS if avg <= limit), HAZARDOUS)
    return {"level": level, "avg": avg,
            "valid_ratio": round(valid_ratio, 2), "fault_count": fault_count}
