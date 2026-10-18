# 練習 02 解答：安全重構六步驟

所有步驟都實際執行過，每一步的 pytest 輸出存在 `logs/`，每一步都有獨立 commit。

## 步驟紀錄

| 步驟 | 動作 | 測試結果 | Commit | 紀錄檔 |
|---|---|---|---|---|
| 1. 確認測試網 | 原始碼原封不動放進 `src/sensor.py`，寫 12 個特性化測試 | **12 passed** | `f0f5f04` | `logs/step0-before.txt` |
| 2-4. 手法 A：Rename | `process→clean_sensor_readings`、`d→readings`、`t→sensor_type`、`r→return_average`；邏輯一行不動；保留 `process` 別名；測試改用新名稱並加 1 個別名測試 | **13 passed** | `5c2de39` | `logs/step1-rename.txt` |
| 2-4. 手法 B：Extract Function | 提取 `filter_pm25`、`filter_temperature`（題目要求）＋ `average`、`_drop_none`，以字典分派取代 if/elif；先用既有 13 個測試確認全綠，再補 3 個子函式單元測試 | **13 passed → 16 passed** | `c2ca135` | `logs/step2a-*.txt`、`logs/step2b-after.txt` |
| 額外驗證 1 | 舊版 vs 新版隨機比對 20,000 組輸入（含 None、998、邊界值、怪異 `r` 值），比對回傳值與型別 | **全部一致** | — | `logs/equivalence.txt` |
| 額外驗證 2 | 變異測試：故意改壞 6 處，看測試網能否抓到 | **5/6 被抓到**；沒抓到的是「拿掉 998 條件」，證明那是死碼 | — | `logs/mutation.txt` |

### 測試網設計重點（步驟 1）

題目要求的 3 類之外，額外鎖住 5 個「重構時最容易不小心改掉」的怪行為：

- `None` 輸入 → 回 `0` 或 `[]`
- 未知感測類型 → 只去 None，不檢查範圍（998 也會留下）
- 全部被過濾 → 回傳的是 **int** `0`，不是 `0.0`
- `r == True` 判斷：`r=1` 視為 True、`r="yes"` 卻回傳清單
- 浮點數輸入

特性化測試的原則：**先鎖住「現在是什麼」，不是「應該是什麼」**。怪行為要修，應該在重構之後另開一個「改行為」的 commit。

## 重構後完整程式碼（`src/sensor.py`）

```python
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
```

## 完整測試（`tests/test_sensor.py`）

```python
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
```

`tests/conftest.py` 只負責把 `src/` 加進 `sys.path`。執行方式：`python -m pytest -v`

## 步驟 6：回顧（前後比較）

| 指標 | 重構前 | 重構後 |
|---|---|---|
| 主函式行數 | 30 行 | 8 行（`clean_sensor_readings`） |
| 最深巢狀 | 6 層 | 1 層 |
| 魔術數字 | 5 個 | 0 個（全部具名常數） |
| 可單獨測試的單元 | 1 個 | 4 個（`filter_pm25`、`filter_temperature`、`average`、主函式） |
| 新增感測類型 | 插一層 `elif` | 寫一個 filter 函式 + 在 `SENSOR_FILTERS` 加一行 |
| 舊呼叫端 | — | 不用改（`process` 別名＋位置參數相容） |

## 延伸思考

**重構後比較容易測試嗎？是。**

- 重構前要測「PM2.5 上限 500 是否包含」，得透過主函式、還要記得帶 `r=False` 才看得到清單。重構後直接 `filter_pm25([500, 501]) == [500]`，一行搞定。
- 每個子函式只有一個職責、輸入輸出都是清單，測試不用排列組合 `t × r` 的所有情況（原本 3 種類型 × 2 種回傳 = 6 條路徑交錯）。
- `average` 獨立後，「空清單回 0」「四捨五入 2 位」這種規則可以單獨測，不必塞資料讓過濾後剛好為空。

**但也有代價**：主函式的測試沒有變少——特性化測試仍要保留，因為它保護的是「組裝起來的行為」（例如 `r == True` 的怪判斷就只存在主函式）。子函式測試是「新增的精準測試」，不是「取代」。

**下一步可做（本練習未做，因為會改變行為）**：把旗標參數 `return_average` 拆成兩個函式 `get_valid_readings()` / `get_average_reading()`；未知 `sensor_type` 改成丟 `ValueError`；沒資料時回 `None` 而不是 `0`。這些要先和呼叫端溝通，屬於「改行為」，不是「重構」。
