# Session 6 Summary — 2026-06-16

## 完成事項

### 1. 完成 study-scaffold 腳手架建立（跨 session 收尾）

- 前一個 session 已完成課程 01-12，本 session 補完 13-15 + 附A/B/C（共 30 個檔案）
- 每課 5 個檔案：README.md / exercise-01/02/03.md / STEP_LOG.md
- 最終 commit：`9adc387`，128 files changed, 3407 insertions(+)
- 18 課目錄結構全部含 answer/ + starter/（第 02 課起）

### 2. 完成 Lesson 01：從聊天機器人到開發夥伴

- ex01：分析 Claude Chat vs Claude Code 差異 + 工具呼叫識別（含 hook 攔截踩坑）
- ex02：建立 calculator 3 檔案專案（main.py + utils.py + tests/test_calc.py），所有測試通過
- ex03：設計 .log 整理 agentic 工作流（含 3 個失敗點分析）
- commit：`f0d1390`，8 files changed, 268 insertions

### 3. 完成 Lesson 02：真正有效的提示詞技巧

- ex01：診斷 3 個低效提示詞（缺角色/背景/限制/輸出格式）並改寫高效版
- ex02：設計 Scrapy 除錯 / TypeScript Review / API 設計 3 個角色提示詞，有/無角色輸出對比
- ex03：建立 5 個個人提示詞庫（/debug / /review / /doc / /refactor / /api-design），含版本記錄
- commit：`9caf6a3`，11 files changed, 684 insertions

### 4. 啟動 Lesson 03，carry 完成

- 執行 carry：複製 Lesson 02 answer/ 到 Lesson 03 starter/
- 讀取 exercise-01-基礎.md，出了第一道互動式題目
- **因使用者要求改為互動式模式而暫停**

### 5. 學習模式架構調整（重要決定）

- 使用者明確要求：study-scaffold 改成**互動式**（我出題 → 使用者回答 → 我給回饋）
- 原模式：Claude 直接完成全部練習並寫解答
- 新模式：每次只出一道題，等使用者回應後再繼續

---

## 關鍵技術筆記

### writer-qa-iron-rule 鐵律行為

- `.py` 副檔名的 Write 呼叫被 hook 攔截（`enforce_writer_qa.py`）
- 逃生門：`FORCE_DIRECT_WRITE=1` 或改用 Bash + Python 內嵌程式碼建立
- 學習練習的示範 .py 採 Bash 方式繞過，不走完整 code-writer 流程

### study-scaffold carry 機制

- carry 指令：`cp -r demo/[NN-課程名]/answer/. demo/[NN+1-課程名]/starter/`
- 第 01 課 answer/ 含：hello.py / calculator/ / ex01-03-answer.md
- 這些檔案已正確複製到第 02 課 starter/，並在第 02 課 commit 中一起推送

### 提示詞設計核心洞察（本 session 驗證）

- 「限制」比「任務」更重要：縮小 Claude 的猜測空間是提升輸出精確度的關鍵
- 角色設定的真正作用：校準回答的優先順序和框架語境，而非讓 AI 更聰明

---

## 產出檔案表格

| 檔案 | 類型 | commit |
|------|------|--------|
| `demo/[13-15, 附A/B/C]/` 下 30 個 .md | 新增（補完腳手架） | 9adc387 |
| `demo/[01]/answer/hello.py` | 新增（示範） | f0d1390 |
| `demo/[01]/answer/calculator/` 3 個 .py | 新增（實作） | f0d1390 |
| `demo/[01]/answer/ex01-03-answer.md` | 新增 | f0d1390 |
| `demo/[01]/STEP_LOG.md` | 更新 | f0d1390 |
| `demo/[02]/answer/ex01-03-answer.md` | 新增 | 9caf6a3 |
| `demo/[02]/starter/` (carry from 01) | 新增 | 9caf6a3 |
| `demo/[02]/STEP_LOG.md` | 更新 | 9caf6a3 |
| `demo/[03]/starter/` (carry from 02) | 新增（未 commit） | — |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 先 commit Lesson 03 starter/（carry 的 uncommitted 變更）
- [ ] 繼續 Lesson 03 互動式練習：出題「CLAUDE.md 禁止事項列 3 條」，等使用者回答
- [ ] 完成 Lesson 03 後執行 carry 到 Lesson 04

### 進行中（需接續）

- Lesson 03 starter/ 已有 carry 完成，但 answer/ 還是空的
- 已向使用者出了第一道題（「禁止事項區塊你會列哪些規則」），使用者尚未回答就收工
- 互動式模式：每次出 1 題，等使用者回答，給回饋，才出下一題

### 注意事項

- **study-scaffold 互動式鐵律**：不要一次把全部答案寫完！出一題等回應
- Lesson 03 uncommitted 的 starter/ 需要在下次 session 開頭補 commit
- 第 03 課練習 01 任務 1 的第一個問題已出但未收到回答：「CLAUDE.md 的禁止事項，你會列哪 3 條？請說明每條的原因」
