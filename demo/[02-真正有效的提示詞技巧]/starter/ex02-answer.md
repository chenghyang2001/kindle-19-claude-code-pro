# 練習 02 解答 — 第一個 agentic 任務

## 任務 1：單步驟 vs 多步驟對比

### 單步驟任務
指令：「建立一個 hello.py，印出 Hello World」

**Claude Code 的執行過程：**
1. 思考：「需要什麼工具？」→ 只需要 Write
2. 呼叫 `Write` 建立 `hello.py`
3. （選配）呼叫 `Bash` 驗證
4. 完成

**自主規劃程度**：低，路徑明確

---

### 多步驟任務
指令：「建立 calculator 專案：main.py + utils.py + tests/test_calc.py，實作加減乘除」

**Claude Code 的執行過程（本次觀察）：**
1. **規劃**：決定需要 `mkdir -p calculator/tests` 先建目錄
2. **建立 utils.py**：先寫工具函式（其他檔案會依賴它）
3. **建立 main.py**：import utils，依賴 utils.py 已存在
4. **建立 tests/test_calc.py**：測試需要知道函式的 signature
5. **驗證**：執行測試確認通過，再執行 main.py 確認輸出

**關鍵觀察：執行順序有依賴性**
- utils.py 必須在 main.py 之前（import 關係）
- 測試必須在被測函式確定後才能寫
- Claude Code 自動識別這個依賴關係並排序

**自主規劃程度**：高，需要推理步驟順序

---

### 比較表

| 維度 | 單步驟 | 多步驟 |
|------|--------|--------|
| 工具呼叫次數 | 1-2 次 | 5+ 次 |
| 自主決策 | 幾乎不需要 | 需要規劃執行順序 |
| 失敗風險 | 低 | 某一步失敗影響後續 |
| 中途干預空間 | 少 | 每步之間都有 |

---

## 任務 2：中途干預實驗

### 場景：執行多步驟任務時修改正在處理的檔案

**觀察（理論分析，因為這次是批次執行）：**
- 如果在 Claude Code 寫 `utils.py` 時，你同時修改 `utils.py`，Claude Code **不會即時偵測到**（它沒有 file watcher）
- 但如果修改後呼叫 Bash 執行測試，新的磁碟狀態會被讀入
- Claude Code 的「感知」是透過工具（Read/Bash）取得資訊，不是即時監控

**說「停，先做別的事」的影響：**
- Claude Code 會立刻停止，等待下一個指令
- 已完成的步驟（已寫入的檔案）不會被撤銷
- 恢復後可以繼續，但需要 Claude 重新了解當前狀態

---

## 延伸思考

### 10 個檔案的複雜任務如何拆解

分解策略：**依賴圖拆解**
```
Step 1（並行）：types.ts / constants.ts / config.ts（無依賴）
Step 2（串行）：utils.ts / api.ts（依賴 types + config）
Step 3（串行）：services/*.ts（依賴 utils + api）
Step 4（串行）：main.ts / index.ts（依賴所有）
Step 5（最後）：tests/**/*.test.ts（依賴所有實作）
```

### 實際工作中最適合用 agentic 工作流的場景

1. **重複性程式碼生成**：為每個 DB 表格生成 CRUD API + 測試
2. **批次重構**：把 callback 改成 async/await（多檔同類型修改）
3. **專案初始化**：建立標準目錄結構 + 設定檔 + boilerplate
4. **Bug 修復 + 驗證**：找 bug → 修改 → 跑測試 → 確認通過的完整循環
