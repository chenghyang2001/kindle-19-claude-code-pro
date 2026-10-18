# 提示詞模板：為 Python 函式生成 pytest 測試

> 使用方式：把 `{{...}}` 佔位符換成實際內容後，整段貼給 Claude Code（或 `claude -p`）。

---

你是資深 Python 測試工程師。請為下面的函式撰寫 **pytest** 測試檔。

## 目標
- 模組匯入路徑：`{{IMPORT_PATH}}`（例：`from starter.alert_level import classify_alert_level`）
- 輸出檔案：`{{TEST_FILE_PATH}}`
- 函式原始碼：

```python
{{FUNCTION_SOURCE}}
```

- 業務背景 / 額外規格（沒有就寫「無」）：{{BUSINESS_CONTEXT}}

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
