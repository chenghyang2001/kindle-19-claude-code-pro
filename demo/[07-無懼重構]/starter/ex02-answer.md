# 練習 02 解答 — Claude Code 生成測試

## 任務 1：生成測試提示詞模板

```
你是一位 Python 測試專家，請為以下函式生成完整的 pytest 測試套件。

目標函式：
```python
{貼入函式程式碼}
```

生成規則（必須全部遵守）：
1. 至少 1 個 happy path：標準正常輸入 → 驗證回傳值正確
2. 至少 2 個 edge case：
   - 空值（空清單 / 空字串 / None）
   - 邊界值（最小值、最大值、剛好在邊界上）
3. 至少 1 個 error case：非法輸入應拋出特定例外類型
4. 命名規則：test_<場景描述>（英文，描述「什麼情況下發生什麼」）
5. 每個測試只測一件事，結構為 Arrange / Act / Assert

外部依賴處理：
- 如果函式呼叫資料庫或 API，一律用 pytest-mock 的 mocker.patch() mock 掉
- mock 的回傳值要真實（不要 return None，要模擬真實資料格式）

輸出格式：
- 完整可執行的 pytest 程式碼
- 每個測試前加一行註解說明測試目的
```

---

## 任務 2：品質評估

以 `calculate_daily_avg` 為目標函式生成測試後的評估：

| 維度 | 分數 | 說明 |
|------|------|------|
| 覆蓋全面性 | 4/5 | 涵蓋主要路徑；負數輸入未測試 |
| 可直接執行 | 5/5 | 無需修改，import 路徑正確 |
| 命名清晰度 | 5/5 | 函式名稱完整描述場景 |
| 真實驗證行為 | 4/5 | assert 值精確；浮點精度可改用 pytest.approx |

**哪裡好：** 自動涵蓋 998 故障碼排除、空清單兩個核心 edge case。

**需要人工補充：**
- 負數輸入（-1 應被排除，但 Claude 常忽略）
- 浮點比較改用 `pytest.approx(61.45, rel=1e-3)` 更嚴謹

---

## 延伸思考：外部依賴的 Mock 問題

Claude 對外部依賴常犯兩個錯誤：

1. **忘記 mock**：直接打真實 DB/API，測試環境沒有連線就失敗
2. **mock 回傳值太假**：回 `None` 或空 dict，函式剛好跑過但沒測到真實邏輯

**引導方式（加入提示詞）：**
```
外部依賴處理：
- 資料庫查詢用 mocker.patch("module.db.query", return_value=[{"id": 1, "value": 42.5}])
- API 呼叫用 mocker.patch("requests.get", return_value=Mock(status_code=200, json=lambda: {...}))
- mock 回傳值必須模擬真實格式，不能用 None 或空值
```
