"""感測資料處理（手法 B：提取 filter_pm25 / filter_temperature）"""

PM25_MIN, PM25_MAX = 0, 500
# 998 是感測器故障碼，不是真實污染值
PM25_SENSOR_ERROR = 998
TEMP_MIN, TEMP_MAX = -40, 85


def filter_pm25(readings):
    """保留 0~500 且非故障碼 998 的 PM2.5 數值（略過 None）。"""
    return [
        value for value in readings
        if value is not None
        and PM25_MIN <= value <= PM25_MAX
        and value != PM25_SENSOR_ERROR
    ]


def filter_temperature(readings):
    """保留 -40~85 度的溫度數值（略過 None）。"""
    return [
        value for value in readings
        if value is not None and TEMP_MIN <= value <= TEMP_MAX
    ]


def _drop_none(readings):
    """未知感測類型：不檢查範圍，只去掉 None。"""
    return [value for value in readings if value is not None]


SENSOR_FILTERS = {"pm25": filter_pm25, "temp": filter_temperature}


def average(values):
    """平均值取到小數 2 位；空清單回傳 0（沿用舊行為，型別為 int）。"""
    if not values:
        return 0
    return round(sum(values) / len(values), 2)


def clean_sensor_readings(readings, sensor_type, return_average=True):
    """依感測類型過濾數值，回傳平均值或過濾後的清單。"""
    sensor_filter = SENSOR_FILTERS.get(sensor_type, _drop_none)
    valid_readings = sensor_filter(readings or [])
    # 刻意用 == True 而非 truthy 判斷：舊行為 return_average="yes" 會回傳清單
    if return_average == True:  # noqa: E712
        return average(valid_readings)
    return valid_readings


# 舊呼叫端仍用 process(d, t, r=...)，保留別名避免一次改壞所有呼叫點
process = clean_sensor_readings
