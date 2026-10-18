# 練習 01 — 基礎：三層測試實戰

## 情境說明
你要為一個「計算 PM2.5 日均值」的函式建立完整測試套件。

## 目標函式

```python
def calculate_daily_avg(readings: list[float]) -> float:
    """計算有效 PM2.5 讀數的日均值。998 是感測器故障碼，需排除。"""
    valid = [r for r in readings if 0 <= r <= 500]
    return round(sum(valid) / len(valid), 2) if valid else 0.0
```

## 任務

### 任務 1：三個單元測試
寫以下三個測試（使用 pytest）：

1. **Happy path**：正常讀數清單，驗證均值計算正確
2. **Edge case**：全部是 998（感測器故障碼），驗證回傳 0.0
3. **Error case**：空清單，驗證回傳 0.0（不拋出例外）

格式要求：
- 使用描述性的測試函式名稱（`test_returns_zero_when_all_readings_invalid`）
- 每個測試只測一件事
- 有 Arrange / Act / Assert 三段結構（可用空行分隔）

### 任務 2：再加三個邊界值測試
4. 混合正常值與 998（確認 998 被正確排除）
5. 只有一個有效讀數（確認單一值的均值計算正確）
6. 包含 0 和 500（邊界值，確認被包含而不是被排除）

## 完成後
將所有測試程式碼存入 `answer/ex01-answer.md`
