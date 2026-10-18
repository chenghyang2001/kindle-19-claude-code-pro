# 練習 02 解答 — 用 Claude Code 生成測試

## 任務 1：「生成測試」提示詞模板

檔案：`prompts/generate-tests-template.md`（佔位符：`{{IMPORT_PATH}}`、`{{TEST_FILE_PATH}}`、`{{FUNCTION_SOURCE}}`、`{{BUSINESS_CONTEXT}}`）


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

### 模板怎麼滿足題目要求

| 題目要求 | 模板裡對應的規定 |
|---|---|
| ≥1 happy path | 「Happy path ≥ 1」，且要斷言**完整回傳值** |
| ≥2 edge case | 「Edge case ≥ 2」，並列出候選清單（空、None、門檻 ±最小單位…） |
| ≥1 error case | 「Error case ≥ 1」，強制 `pytest.raises(例外, match=...)` |
| 命名描述場景 | 規定 `test_<預期結果>_when_<場景>` 格式，並舉反例 |
| （額外）真的驗證行為 | 每個分支/門檻都要有測試、禁止只斷言「不為 None」、不要遷就 bug |

## 任務 2：評估生成品質

### 做法（實際執行）

1. `starter/` 原本不存在，自建 `starter/alert_level.py`：`classify_alert_level()`，依 PM2.5 讀數判定 6 級警示，含型別檢查、有效比例門檻、998 故障計數。
2. 用模板填入後存成 `prompts/filled-prompt-alert-level.md`，交給 `claude -p`（非互動模式、關閉工具）生成。
3. 原始輸出：`prompts/outputs/claude-raw-output.md`；抽出程式碼存到 `tests/test_alert_level_generated.py`，**一個字都沒改**。
4. 執行 pytest：**39 passed**（19 個測試函式，parametrize 展開成 39 個案例）。
5. 突變測試 `tools/mutation_check.py`：把被測函式故意改壞 10 種方式，看測試會不會失敗。結果 **10/10 被抓到**。

```
39 passed in 0.07s

[殺死 ✓] 門檻上限含→不含
[殺死 ✓] 有效比例 < 改 <=
[殺死 ✓] 有效下限 0 改 >0
[殺死 ✓] 有效上限 500 改 <500
[殺死 ✓] 移除 bool 檢查
[殺死 ✓] 均值不四捨五入
[殺死 ✓] fault_count 恆為 0
[殺死 ✓] ratio 允許 0
[殺死 ✓] 危害等級改名
[殺死 ✓] valid_ratio 不四捨五入
突變分數：10/10
```

### 評分（每項 1-5）

| 維度 | 分數 | 理由 |
|---|:---:|---|
| 1. 覆蓋是否全面 | **4** | 6 個等級門檻都測了「門檻值」與「門檻 +0.1」、有效範圍 0/500、ratio 剛好 0.75、bool、型別錯誤優先順序都有。遺漏：NaN、inf、`min_valid_ratio` 傳字串、浮點四捨五入落在 x.x5 的不一致（見下）。 |
| 2. 能否直接執行 | **5** | 原封不動 39/39 通過，import 路徑正確，沒有用到不存在的 API。 |
| 3. 命名描述場景 | **5** | 全部遵守 `test_<預期>_when_<場景>`，例如 `test_counts_faults_separately_from_out_of_range_when_valid_ratio_below_custom_threshold`。少數名稱偏長。 |
| 4. 是否真的驗證行為 | **5** | 大多數測試斷言整個 dict；error case 用 `match=re.escape(...)` 驗證訊息；突變測試 10/10。 |

### 哪裡好

- 主動抓到「先四捨五入再比門檻」這個容易誤解的細節（35.42 → 35.4 → 普通）。
- 主動區分「超出範圍」與「故障碼 998」兩種無效讀數的計數差異。
- 測到檢查順序（readings 和 ratio 同時錯時先報哪個）。
- 檔頭的案例清單有標 [happy]/[edge]/[error]，方便人工審查。

### 需要人工補充（已補在 `tests/test_alert_level_supplement.py`，5 passed）

| 補充案例 | 為什麼重要 |
|---|---|
| NaN 讀數 | NaN 會通過 `isinstance(float)` 檢查，要確認它被當無效值而不是讓均值變 NaN |
| inf 讀數 | 同上，確認被排除 |
| `min_valid_ratio="0.5"` | 目前拋的是 Python 內建比較錯誤，訊息不友善 → 記錄為函式改善點 |
| 均值結尾是 5 的四捨五入 | **發現業務風險**：均值 15.45 會變 15.4（良好），35.45 卻變 35.5（升一級）。因為二進位浮點數表示不精確，`round()` 對「…5」有時捨有時進。正式版應改用 `Decimal` + `ROUND_HALF_UP`。測試先釘住現況並加註解。 |

結論：模板把「必須斷言完整回傳值」「每個門檻都要測」寫死後，生成品質很高；人工最該補的是**語言層面的怪輸入**（NaN、浮點捨入）和**業務上該不該這樣**的判斷——AI 會照現有程式碼寫測試，不會質疑規格本身。

## 延伸思考：依賴外部服務的函式

### Claude Code 生成時常見的問題

1. **真的去連線**：直接 import 真實 DB client，測試在 CI 上 timeout 或寫髒資料（對唯讀的生產 DB 尤其危險）。
2. **mock 錯地方**：patch 了定義處（`pymysql.connect`）而不是使用處（`mymodule.pymysql.connect`），mock 沒生效。
3. **只 mock 不斷言**：mock 回傳假資料就結束，沒驗證「用什麼參數呼叫」「有沒有呼叫」，等於只測了假資料。
4. **只測成功路徑**：沒測連線失敗、timeout、回傳空值、API 回 500。
5. **mock 過頭**：把被測邏輯本身也 mock 掉，測試永遠通過。

### 在提示詞裡怎麼引導（模板中已加入第 3 條規則，可再追加以下段落）

```text
## 外部依賴規則
- 被測函式依賴：{{EXTERNAL_DEPENDENCIES}}（例：repo.fetch_readings 讀 MySQL、notifier.send 發 Telegram）
- 一律用 unittest.mock.Mock 或 monkeypatch 取代，禁止真實連線；patch 目標寫「使用處」的路徑。
- 每個 mock 都要斷言：assert_called_once_with(...) 或 assert_not_called()。
- 至少一個失敗路徑測試：side_effect=ConnectionError / TimeoutError，驗證函式的降級行為。
- 只 mock 邊界（DB、網路、時間），不要 mock 被測模組內部的純邏輯。
```

### 實作示範（實際執行）

- 被測函式：`starter/room_alert_service.py` 的 `check_room_and_notify()`，用**依賴注入**接收 `repo`（DB）與 `notifier`（通知），所以測試不需要 patch 模組路徑。
- 測試：`tests/test_room_alert_service_mock.py`，**4 passed**。涵蓋「不健康→發通知且斷言訊息內容」「良好→不發通知」「DB 拋 ConnectionError→回傳查詢失敗且不發通知」「全是 998→不發通知」。

```
9 passed in 0.03s
```
