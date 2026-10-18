"""練習 01：calculate_daily_avg 的三層測試（單元 + 邊界值）。"""
import pytest

from src.pm25 import calculate_daily_avg


# ── 任務 1：三個單元測試 ──────────────────────────────

def test_returns_rounded_mean_for_normal_readings():
    # Arrange
    readings = [10.0, 20.0, 30.5]

    # Act
    result = calculate_daily_avg(readings)

    # Assert（60.5 / 3 = 20.1666… → 20.17）
    assert result == 20.17


def test_returns_zero_when_all_readings_invalid():
    # Arrange：全部是感測器故障碼 998
    readings = [998.0, 998.0, 998.0]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 0.0


def test_returns_zero_without_raising_when_readings_empty():
    # Arrange
    readings: list[float] = []

    # Act（若拋 ZeroDivisionError，pytest 會直接判失敗）
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 0.0


# ── 任務 2：三個邊界值測試 ────────────────────────────

def test_excludes_fault_code_998_when_mixed_with_valid_readings():
    # Arrange：若 998 沒被排除，均值會是 (10+998+20+998)/4 = 506.5
    readings = [10.0, 998.0, 20.0, 998.0]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 15.0


def test_returns_that_value_when_only_one_reading_is_valid():
    # Arrange
    readings = [998.0, 42.37, 998.0]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 42.37


def test_includes_boundary_values_zero_and_five_hundred():
    # Arrange：0 與 500 都在有效區間 [0, 500] 內，必須被納入
    readings = [0.0, 500.0]

    # Act
    result = calculate_daily_avg(readings)

    # Assert（若 0 被排除會得 500；若 500 被排除會得 0）
    assert result == 250.0


@pytest.mark.parametrize("out_of_range", [-0.01, 500.01])
def test_excludes_values_just_outside_valid_range(out_of_range):
    # Arrange：額外補充——區間外一點點也要排除
    readings = [100.0, out_of_range]

    # Act
    result = calculate_daily_avg(readings)

    # Assert
    assert result == 100.0
