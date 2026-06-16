# 練習 02 解答 — 安全重構六步驟

## 任務 1：測試網（重構前先加）

```python
import pytest
from sensor import process

def test_pm25_filters_valid_readings():
    assert process([10.0, 50.0, 998, 600.0], "pm25") == 30.0

def test_pm25_returns_zero_for_empty_valid():
    assert process([998, 998], "pm25") == 0

def test_pm25_returns_list_when_r_false():
    assert process([10.0, 998, 50.0], "pm25", r=False) == [10.0, 50.0]

def test_temperature_filters_valid_range():
    assert process([-50.0, 25.0, 85.0, 100.0], "temp") == 55.0
```

---

## 任務 2：重構後完整程式碼

### 手法 A：Rename + 手法 B：Extract Function

```python
def filter_pm25(readings: list) -> list:
    """過濾 PM2.5 有效讀數（0-500，排除 998 故障碼）。"""
    return [r for r in readings if r is not None and 0 <= r <= 500 and r != 998]


def filter_temperature(readings: list) -> list:
    """過濾溫度有效讀數（-40 到 85 度）。"""
    return [r for r in readings if r is not None and -40 <= r <= 85]


def aggregate_sensor_readings(
    readings: list,
    sensor_type: str,
    return_average: bool = True
):
    """過濾感測器讀數並計算均值或回傳清單。"""
    if sensor_type == "pm25":
        valid = filter_pm25(readings)
    elif sensor_type == "temp":
        valid = filter_temperature(readings)
    else:
        valid = [r for r in readings if r is not None]

    if return_average:
        return round(sum(valid) / len(valid), 2) if valid else 0
    return valid
```

### 每步驟說明

1. 加測試網（4 個測試），確認全 PASS
2. Rename：`d→readings`、`t→sensor_type`、`r→return_average`，測試仍全 PASS
3. Extract：抽出 `filter_pm25`、`filter_temperature`，主函式變乾淨，測試仍全 PASS
4. 移除 `for i in range(len(d))` → list comprehension，測試仍全 PASS
5. `sum()` 取代手動累加，測試仍全 PASS

---

## 延伸思考

提取子函式後，`filter_pm25` 可以獨立測試，不需設定 `sensor_type`、`return_average`。

重構前要測「998 排除」需要跑整個 `process`，重構後只需要：
```python
assert filter_pm25([10, 998]) == [10]
```

每個子函式職責單一 → 測試案例更簡單、意圖更清楚。
