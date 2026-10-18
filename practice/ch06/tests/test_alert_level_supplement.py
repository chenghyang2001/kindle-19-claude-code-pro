"""練習 02：人工補充——Claude 生成的測試沒涵蓋的案例。"""
import math

import pytest

from starter.alert_level import classify_alert_level


def test_treats_nan_reading_as_invalid_but_not_fault_when_mixed_with_valid():
    # Arrange：NaN 通過 isinstance(float) 檢查，但 0 <= nan 為 False
    readings = [math.nan, 20, 20, 20]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": "普通", "avg": 20.0, "valid_ratio": 0.75, "fault_count": 0}


def test_returns_insufficient_data_when_reading_is_infinite():
    # Arrange
    readings = [math.inf]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result["level"] == "資料不足"


def test_raises_type_error_when_min_valid_ratio_is_string():
    # Arrange：目前是 Python 內建比較錯誤，訊息對使用者不友善（記錄為改善點）
    readings = [10]

    # Act / Assert
    with pytest.raises(TypeError):
        classify_alert_level(readings, min_valid_ratio="0.5")


@pytest.mark.parametrize(
    "readings, expected_avg, expected_level",
    [
        ([15.4, 15.5], 15.4, "良好"),           # 均值 15.45 → 捨去
        ([35.45], 35.5, "對敏感族群不健康"),     # 35.45 → 進位
    ],
)
def test_pins_float_rounding_behavior_when_avg_ends_in_five(readings, expected_avg, expected_level):
    # 可能的 bug：round() 對 x.x5 的結果取決於二進位浮點表示，
    # 同樣是「…5」有時捨有時進，可能讓等級忽上忽下；正式版建議改用 Decimal ROUND_HALF_UP。
    # 這裡先釘住現況，避免不小心改變行為。

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert (result["avg"], result["level"]) == (expected_avg, expected_level)
