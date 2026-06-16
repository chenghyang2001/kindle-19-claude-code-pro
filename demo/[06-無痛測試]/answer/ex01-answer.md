# 練習 01 解答 — 三層測試實戰

## 目標函式

```python
def calculate_daily_avg(readings: list[float]) -> float:
    """計算有效 PM2.5 讀數的日均值。998 是感測器故障碼，需排除。"""
    valid = [r for r in readings if 0 <= r <= 500]
    return round(sum(valid) / len(valid), 2) if valid else 0.0
```

## 任務 1：三個基礎測試

```python
import pytest
from calculator import calculate_daily_avg

def test_returns_correct_average_for_valid_readings():
    # Arrange
    readings = [12.5, 35.0, 78.3, 120.0]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 61.45

def test_returns_zero_when_all_readings_are_fault_code():
    # Arrange
    readings = [998, 998, 998]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 0.0

def test_returns_zero_for_empty_list():
    # Arrange
    readings = []

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 0.0
```

## 任務 2：三個邊界值測試

```python
def test_excludes_fault_code_from_mixed_readings():
    # Arrange
    readings = [50.0, 998, 100.0, 998]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 75.0  # 只算 50.0 和 100.0

def test_returns_correct_average_for_single_valid_reading():
    # Arrange
    readings = [42.5]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 42.5

def test_includes_boundary_values_zero_and_five_hundred():
    # Arrange
    readings = [0.0, 500.0]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 250.0  # 0 和 500 都是有效值，不應被排除
```
