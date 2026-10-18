# 案例清單
# [happy] 一般正常讀數 → 回傳完整 dict（level / avg / valid_ratio / fault_count）
# [happy] 有效比例剛好等於預設 min_valid_ratio（0.75）時仍正常判定
# [happy] 自訂 min_valid_ratio 時，valid_ratio 四捨五入到 2 位
# [edge] 各等級門檻值本身與門檻 +0.1（上限為含 <=）parametrize 全覆蓋，含最高等級「危害」
# [edge] 有效範圍邊界 0 與 500 視為有效
# [edge] 超出範圍（-0.1、500.1）視為無效但不計入故障
# [edge] 空 list → 資料不足、valid_ratio 0.0
# [edge] 單一元素 998 → 資料不足、fault_count 1
# [edge] 有效比例低於預設門檻 → 資料不足
# [edge] 有效比例低於自訂門檻 → 資料不足，且故障與超範圍分開計算
# [edge] min_valid_ratio = 1（區間上限，含）合法
# [edge] 均值先四捨五入再對照門檻（35.42 → 35.4 → 普通）
# [edge] 均值四捨五入到 1 位（10.333… → 10.3）
# [edge] 998.0（float）也視為故障
# [error] readings 不是 list（tuple / None / str）→ TypeError
# [error] 元素不是數字（str / None）→ TypeError，訊息含該值
# [error] 元素是 bool → TypeError
# [error] min_valid_ratio 超出 (0, 1]（0 / 負數 / >1）→ ValueError
# [error] readings 型別錯誤優先於 min_valid_ratio 錯誤被檢查
import re

import pytest

from starter.alert_level import classify_alert_level


# ---------- happy path ----------

def test_returns_full_result_when_readings_are_typical_valid_values():
    # Arrange
    readings = [10, 20, 30]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": "普通", "avg": 20.0, "valid_ratio": 1.0, "fault_count": 0}


def test_classifies_level_when_valid_ratio_equals_default_threshold():
    # Arrange：4 筆中 3 筆有效 → 0.75，剛好等於預設門檻（應通過，因判斷是 <）
    readings = [20, 20, 20, 998]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": "普通", "avg": 20.0, "valid_ratio": 0.75, "fault_count": 1}


def test_rounds_valid_ratio_to_two_decimals_when_custom_min_ratio_is_given():
    # Arrange：3 筆中 2 筆有效 → 0.666… → 0.67
    readings = [20, 20, 998]

    # Act
    result = classify_alert_level(readings, min_valid_ratio=0.6)

    # Assert
    assert result == {"level": "普通", "avg": 20.0, "valid_ratio": 0.67, "fault_count": 1}


# ---------- 門檻（parametrize） ----------

@pytest.mark.parametrize(
    "reading, expected_level",
    [
        (0, "良好"),
        (15.4, "良好"),
        (15.5, "普通"),
        (35.4, "普通"),
        (35.5, "對敏感族群不健康"),
        (54.4, "對敏感族群不健康"),
        (54.5, "不健康"),
        (150.4, "不健康"),
        (150.5, "非常不健康"),
        (250.4, "非常不健康"),
        (250.5, "危害"),
        (500, "危害"),
    ],
)
def test_returns_expected_level_when_avg_is_at_or_just_above_threshold(reading, expected_level):
    # Arrange
    readings = [reading]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": expected_level, "avg": float(reading),
                      "valid_ratio": 1.0, "fault_count": 0}


# ---------- edge cases ----------

@pytest.mark.parametrize("boundary_value", [0, 500])
def test_treats_reading_as_valid_when_value_is_on_valid_range_boundary(boundary_value):
    # Arrange
    readings = [boundary_value]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result["valid_ratio"] == 1.0


@pytest.mark.parametrize("out_of_range_value", [-0.1, 500.1])
def test_returns_insufficient_data_without_fault_when_reading_is_out_of_range(out_of_range_value):
    # Arrange
    readings = [out_of_range_value]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": "資料不足", "avg": None, "valid_ratio": 0.0, "fault_count": 0}


def test_returns_insufficient_data_when_readings_is_empty():
    # Arrange
    readings = []

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": "資料不足", "avg": None, "valid_ratio": 0.0, "fault_count": 0}


def test_returns_insufficient_data_with_fault_count_when_only_reading_is_fault_code():
    # Arrange
    readings = [998]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": "資料不足", "avg": None, "valid_ratio": 0.0, "fault_count": 1}


def test_returns_insufficient_data_when_valid_ratio_below_default_threshold():
    # Arrange：3 筆中 2 筆有效 → 0.67 < 0.75
    readings = [20, 20, 998]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": "資料不足", "avg": None, "valid_ratio": 0.67, "fault_count": 1}


def test_counts_faults_separately_from_out_of_range_when_valid_ratio_below_custom_threshold():
    # Arrange：1 有效、2 故障、1 超範圍 → 0.25 < 0.5；超範圍不算故障
    readings = [20, 998, 998, 600]

    # Act
    result = classify_alert_level(readings, min_valid_ratio=0.5)

    # Assert
    assert result == {"level": "資料不足", "avg": None, "valid_ratio": 0.25, "fault_count": 2}


def test_returns_insufficient_data_when_min_valid_ratio_is_one_and_any_reading_invalid():
    # Arrange：min_valid_ratio=1 是合法上限（含），任何一筆無效就不足
    readings = [20, 20, 20, 998]

    # Act
    result = classify_alert_level(readings, min_valid_ratio=1)

    # Assert
    assert result == {"level": "資料不足", "avg": None, "valid_ratio": 0.75, "fault_count": 1}


def test_rounds_avg_before_comparing_threshold_when_raw_avg_slightly_exceeds_limit():
    # Arrange：原始均值 35.42 > 35.4，但四捨五入後 35.4 → 普通
    readings = [35.4, 35.44]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result == {"level": "普通", "avg": 35.4, "valid_ratio": 1.0, "fault_count": 0}


def test_rounds_avg_to_one_decimal_when_mean_is_repeating_decimal():
    # Arrange：均值 10.333…
    readings = [10, 10, 11]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result["avg"] == 10.3


def test_counts_fault_when_fault_code_is_given_as_float():
    # Arrange
    readings = [20, 20, 20, 998.0]

    # Act
    result = classify_alert_level(readings)

    # Assert
    assert result["fault_count"] == 1


# ---------- error cases ----------

@pytest.mark.parametrize("bad_readings", [(10, 20), None, "10,20"])
def test_raises_type_error_when_readings_is_not_list(bad_readings):
    # Arrange（由 parametrize 提供）

    # Act / Assert
    with pytest.raises(TypeError, match="readings 必須是 list"):
        classify_alert_level(bad_readings)


@pytest.mark.parametrize("bad_element", ["20", None])
def test_raises_type_error_when_element_is_not_number(bad_element):
    # Arrange
    readings = [10, bad_element]

    # Act / Assert
    with pytest.raises(TypeError, match=re.escape(f"讀數必須是數字，收到 {bad_element!r}")):
        classify_alert_level(readings)


@pytest.mark.parametrize("bool_element", [True, False])
def test_raises_type_error_when_element_is_bool(bool_element):
    # Arrange：bool 是 int 的子類別，必須被額外排除
    readings = [10, bool_element]

    # Act / Assert
    with pytest.raises(TypeError, match=re.escape(f"讀數必須是數字，收到 {bool_element!r}")):
        classify_alert_level(readings)


@pytest.mark.parametrize("bad_ratio", [0, -0.5, 1.01, 1.5])
def test_raises_value_error_when_min_valid_ratio_outside_range(bad_ratio):
    # Arrange
    readings = [10, 20]

    # Act / Assert
    with pytest.raises(ValueError, match=re.escape("min_valid_ratio 必須介於 (0, 1]")):
        classify_alert_level(readings, min_valid_ratio=bad_ratio)


def test_raises_type_error_first_when_both_readings_and_ratio_are_invalid():
    # Arrange
    readings = (10, 20)

    # Act / Assert
    with pytest.raises(TypeError, match="readings 必須是 list"):
        classify_alert_level(readings, min_valid_ratio=0)
