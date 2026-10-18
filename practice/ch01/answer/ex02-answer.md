# 練習 02 解答 — 第一個 agentic 任務

> 執行日期：2026-10-18｜環境：Windows 10、Python 3.14.3、pytest 8.4.2

## 任務 1：單步驟 vs 多步驟

### 單步驟：「建立一個 hello.py，印出 Hello World」

- 動作：Write `hello.py` → Bash `python hello.py`。
- 結果：`Hello World`。
- 幾乎不需要規劃：一個檔案、一個驗證，順序是唯一的。

### 多步驟：「建立 calculator 專案，含 main.py、utils.py、tests/test_calc.py，實作加減乘除」

實際產出結構：

```text
calculator/
├── main.py            # CLI 入口：python main.py 3 + 4
├── utils.py           # add / subtract / multiply / divide
└── tests/
    └── test_calc.py   # 9 個測試（正常、邊界、錯誤）
```

實際驗證輸出：

```text
$ python main.py 3 + 4
7.0
$ python main.py 1 / 0
錯誤：除數不可為 0          (exit code 1)

$ python -m pytest -v tests
tests/test_calc.py::test_add PASSED
tests/test_calc.py::test_subtract PASSED
tests/test_calc.py::test_multiply PASSED
tests/test_calc.py::test_divide PASSED
tests/test_calc.py::test_negative_and_float PASSED
tests/test_calc.py::test_divide_by_zero PASSED
tests/test_calc.py::test_calculate_unknown_operator PASSED
tests/test_calc.py::test_main_cli PASSED
tests/test_calc.py::test_main_cli_bad_args PASSED
============================== 9 passed in 0.08s ==============================
```

從專案根目錄執行 `python -m pytest calculator/tests` 也是 9 passed（測試檔自己把 `calculator/` 加進 `sys.path`，所以在哪裡執行都行）。

### 比較

**哪個更需要自主規劃？** 多步驟的 calculator。它要自己決定：

- 檔案之間的依賴：`main.py` 和測試都 `import utils`。
- 規格裡沒寫的細節：除以 0 怎麼處理（決定拋 `ValueError`）、CLI 參數格式（`<數字> <運算子> <數字>`）、測試要涵蓋哪些情況。
- 怎樣才算「完成」：檔案建好不夠，要跑過測試才算。

**怎麼決定執行順序？** 依「被依賴的先做」：

1. `utils.py`（最底層，沒有依賴）
2. `main.py`（依賴 utils）
3. `tests/test_calc.py`（依賴 utils 和 main）
4. 執行 CLI 與 pytest 驗證（依賴以上全部）

> 實務上，因為三個檔案彼此不需要先讀對方的執行結果，Claude Code 這次其實是在**同一回合平行送出 4 個 Write**（hello.py + 三個 calculator 檔），再用一次 Bash 統一驗證。也就是：「寫」的步驟可平行，「驗證」一定排在最後。

另外有個小插曲：寫完後編輯器的 Pyright 報「`calculate` is unknown import symbol」，因為靜態分析看不懂測試檔裡動態插入的 `sys.path`，把 `main` 解析成根目錄的別的模組。Claude Code 沒有因此去亂改程式，而是**實際跑 pytest** 確認 9 個全過，判定是靜態分析誤判。這就是「以執行結果為準」的 agentic 驗證。

## 任務 2：中途干預實驗

### 干預方式 1：修改它正在處理的檔案（有實測）

模擬方式：在 Claude Code 寫完 `calculator/utils.py` 之後，從 shell 直接在檔尾加一行：

```python
# 使用者中途手動加的註解
```

觀察到的結果：

- Claude Code 的執行環境**立刻送出通知**：「`calculator/utils.py` changed on disk since you last read it」，並附上改動行的內容。
- 系統還會提示：外部改動通常是使用者刻意的，應視為目前狀態，不要擅自還原；若看起來有問題，要先說出來。
- 如果此時 Claude 拿舊內容去用 Edit 工具改這個檔，Edit 會拒絕（要求先重新讀檔），避免把使用者的改動蓋掉。

結論：**有偵測到**。Claude Code 會追蹤「上次讀到的檔案狀態」，磁碟上的版本一變就會知道。（本次因為這行是實驗刻意加的，實驗後已手動移除並重跑 pytest，仍是 9 passed。）

### 干預方式 2：直接說「停，先做別的事」（文字描述）

- 在 Claude Code 執行中按 **Esc** 可以中斷目前這一步；工具呼叫跑到一半會被取消，已完成的檔案改動會留著。
- 接著輸入「停，先做別的事：……」，Claude 會以新指令為優先，但對話上下文還在，所以之後說「回到剛才的 calculator」可以接著做。
- 若在它執行中直接打字送出（不按 Esc），訊息會排隊，在目前這個工具呼叫結束後被讀到，Claude 再依新指令調整方向。
- 要退回之前的狀態可用 **Esc 兩下**（回到先前訊息改寫）或 checkpoint／rewind 功能；也可以用 git 自己回復。

## 延伸思考

### 如果任務涉及 10 個檔案，怎麼拆給 Claude Code？

1. **先要計畫，不先要程式**：叫它用 Plan 模式（Shift+Tab）列出檔案清單、各檔職責、依賴關係，確認後才開工。
2. **依依賴分層**：資料模型／工具函式 → 商業邏輯 → 介面（CLI／API）→ 測試與文件。每層做完先跑測試再進下一層。
3. **一次一個可驗證的小目標**：例如「先完成 models.py 和它的測試，跑過再停」，而不是一次要 10 個檔。
4. **給驗收標準**：明確說「pytest 全過」「`python main.py --help` 能執行」這種可以自動檢查的條件。
5. **把規則寫進 CLAUDE.md**：命名、目錄結構、測試指令，避免每輪重講。
6. **獨立的部分交給 sub-agent 平行處理**，主 session 只負責整合；每個階段完成就 git commit，出錯好回滾。

### 實際工作中 agentic 工作流最可能用在哪裡？

- **重複又有固定步驟的工作**：週報整理、資料清洗腳本、批次轉檔。
- **有明確驗收標準的開發**：補測試、修 bug（可以用測試驗證修好了沒）、小幅重構。
- **跨多檔的機械性修改**：改 API 名稱、升級套件後修相容性、統一錯誤處理寫法。
- **探索陌生程式碼**：讓它先讀整個專案，回答「X 在哪裡做的」、「這個流程怎麼跑」。

不適合完全放手的：需要商業判斷、正式環境部署、刪資料等不可逆操作——這些應保留人工確認。
