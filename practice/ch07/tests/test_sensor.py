"""特性化測試（characterization tests）：鎖住 process 的「現有行為」，
包含看起來奇怪的行為，重構時一律不能改變。"""
import pytest

from sensor import clean_sensor_readings as target


# ── 題目要求 1：PM2.5 模式 ──
def test_pm25_normal_average():
    assert target([10, 20, 30], "pm25") == 20


def test_pm25_excludes_998_sensor_error():
    # 998 是感測器故障碼，不可算進平均
    assert target([10, 998, 20], "pm25") == 15


def test_pm25_empty_list_returns_zero():
    assert target([], "pm25") == 0


def test_pm25_out_of_range_and_none_excluded():
    assert target([-1, 501, None, 500, 0], "pm25", return_average=False) == [500, 0]


# ── 題目要求 2：Temperature 模式 ──
def test_temp_keeps_only_minus40_to_85():
    assert target([-41, -40, 25, 85, 86], "temp", return_average=False) == [-40, 25, 85]


def test_temp_average_rounded_to_2_places():
    assert target([20, 21, 21], "temp") == pytest.approx(20.67)


# ── 題目要求 3：回傳清單模式 ──
def test_return_list_mode_keeps_order():
    assert target([30, 998, 10, None, 20], "pm25", return_average=False) == [30, 10, 20]


# ── 邊界：鎖住容易被重構弄壞的怪行為 ──
def test_none_input_returns_zero_or_empty_list():
    assert target(None, "pm25") == 0
    assert target(None, "pm25", return_average=False) == []


def test_unknown_type_passes_everything_except_none():
    assert target([998, -999, None, 5], "humidity", return_average=False) == [998, -999, 5]


def test_all_filtered_out_returns_int_zero():
    value = target([998, 999], "pm25")
    assert value == 0 and isinstance(value, int)


def test_r_uses_equality_with_true():
    # r == True：1 也算 True；其他 truthy 值（如 "yes"）走回傳清單分支
    assert target([10, 20], "pm25", return_average=1) == 15
    assert target([10, 20], "pm25", return_average="yes") == [10, 20]


def test_float_values_supported():
    assert target([1.5, 2.5], "pm25") == 2.0


# ── 手法 A 新增：舊名稱別名仍可用（含位置參數 r） ──
def test_legacy_alias_process_still_works():
    from sensor import process
    assert process([10, 998, 20], "pm25") == 15
    assert process([10, 20], "pm25", False) == [10, 20]


# ── 手法 B 新增：提取出來的子函式可以單獨測，不必繞道主函式 ──
from sensor import average, filter_pm25, filter_temperature  # noqa: E402


def test_filter_pm25_boundaries_and_error_code():
    assert filter_pm25([-1, 0, 500, 501, 998, None, 35]) == [0, 500, 35]


def test_filter_temperature_boundaries():
    assert filter_temperature([-40.1, -40, 85, 85.1, None]) == [-40, 85]


def test_average_empty_and_rounding():
    assert average([]) == 0
    assert average([1, 2, 2]) == 1.67
