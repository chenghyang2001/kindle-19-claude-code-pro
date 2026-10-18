# 練習 01 解答 — 三層測試實戰

- 目標函式：`src/pm25.py`
- 測試檔：`tests/test_pm25.py`
- 執行指令：`PYTHONUTF8=1 python -m pytest tests/test_pm25.py -v`
- **實際執行結果：8 passed**（6 個題目要求的測試 + 1 個補充的參數化測試展開成 2 個）

## 測試對照表

| # | 題目要求 | 測試函式 | 輸入 | 預期 |
|---|---|---|---|---|
| 1 | Happy path | `test_returns_rounded_mean_for_normal_readings` | `[10, 20, 30.5]` | `20.17` |
| 2 | Edge：全部 998 | `test_returns_zero_when_all_readings_invalid` | `[998]*3` | `0.0` |
| 3 | Error：空清單 | `test_returns_zero_without_raising_when_readings_empty` | `[]` | `0.0`，不拋例外 |
| 4 | 混合 998 | `test_excludes_fault_code_998_when_mixed_with_valid_readings` | `[10, 998, 20, 998]` | `15.0` |
| 5 | 單一有效值 | `test_returns_that_value_when_only_one_reading_is_valid` | `[998, 42.37, 998]` | `42.37` |
| 6 | 邊界 0 / 500 | `test_includes_boundary_values_zero_and_five_hundred` | `[0, 500]` | `250.0` |
| 補 | 區間外一點點 | `test_excludes_values_just_outside_valid_range` | `-0.01` / `500.01` | 被排除 |

設計重點：

- 每個預期值都選成「若邏輯錯會得到不同數字」，例如測 4 若沒排除 998 會得 506.5；測 6 若排除 0 會得 500、排除 500 會得 0。這樣測試才真的能抓錯，不只是能跑。
- 測 1 特意用 `30.5` 讓均值是循環小數，順便驗證 `round(..., 2)`。
- 測 3 題目歸類為 error case，但這個函式的設計是不拋例外、直接回 0.0，所以測試驗證的是「不會出現 ZeroDivisionError」。

## 完整測試程式碼

```python
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
```

## 執行輸出

```
tests/test_pm25.py::test_returns_rounded_mean_for_normal_readings PASSED [ 12%]
tests/test_pm25.py::test_returns_zero_when_all_readings_invalid PASSED   [ 25%]
tests/test_pm25.py::test_returns_zero_without_raising_when_readings_empty PASSED [ 37%]
tests/test_pm25.py::test_excludes_fault_code_998_when_mixed_with_valid_readings PASSED [ 50%]
tests/test_pm25.py::test_returns_that_value_when_only_one_reading_is_valid PASSED [ 62%]
tests/test_pm25.py::test_includes_boundary_values_zero_and_five_hundred PASSED [ 75%]
tests/test_pm25.py::test_excludes_values_just_outside_valid_range[-0.01] PASSED [ 87%]
tests/test_pm25.py::test_excludes_values_just_outside_valid_range[500.01] PASSED [100%]
============================== 8 passed in 0.05s ==============================
```
