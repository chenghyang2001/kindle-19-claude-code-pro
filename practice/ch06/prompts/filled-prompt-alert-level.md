

你是資深 Python 測試工程師。請為下面的函式撰寫 **pytest** 測試檔。

## 目標
- 模組匯入路徑：`from starter.alert_level import classify_alert_level`（例：`from starter.alert_level import classify_alert_level`）
- 輸出檔案：`tests/test_alert_level_generated.py`
- 函式原始碼：

```python
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
```

- 業務背景 / 額外規格（沒有就寫「無」）：PM2.5 單位 μg/m³；998 是感測器故障碼；門檻上限為含（<=）。

## 必須涵蓋的案例（缺一不可）
1. **Happy path ≥ 1**：典型正常輸入，斷言**完整的回傳值**（不能只斷言型別或「不為 None」）。
2. **Edge case ≥ 2**：從下列挑最相關的——空集合、None、單一元素、門檻值本身與門檻 ±最小單位、極大/極小值、特殊字元、浮點四捨五入邊界。
3. **Error case ≥ 1**：非法輸入要用 `pytest.raises(具體例外, match=...)` 驗證**例外類型與訊息**。
4. 函式中**每一個 if / 分支 / 門檻**都至少有一個測試走到；用 `@pytest.mark.parametrize` 一次覆蓋多個門檻。

## 寫法規定
- 測試名稱描述「**場景 + 預期**」，格式 `test_<預期結果>_when_<場景>`，例如 `test_returns_insufficient_data_when_valid_ratio_below_threshold`；禁止 `test_function1`、`test_calc` 這種描述動作的名稱。
- 每個測試只驗證一件事，內部用 `# Arrange / # Act / # Assert` 註解分段。
- 只用標準庫 + pytest；不要依賴網路、檔案系統、目前時間或亂數。
- 若函式依賴外部服務（DB / API / 檔案 / 時間），一律用 `unittest.mock` 或 pytest `monkeypatch` 隔離，並**斷言 mock 被呼叫的參數**；不得真的連線。
- 不要修改被測函式；如果你認為函式有 bug，寫一個預期正確行為的測試並在註解標 `# 可能的 bug：...`，不要為了讓測試通過而遷就錯誤行為。

## 輸出
1. 只輸出一個完整、可直接執行的測試檔（單一 ```python 區塊），不要附解說。
2. 檔案最上方用註解列出「案例清單」：每一行標註 [happy] / [edge] / [error]。
