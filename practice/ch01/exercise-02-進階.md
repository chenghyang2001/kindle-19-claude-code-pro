# 練習 02 — 進階：第一個 agentic 任務

## 情境說明
你要讓 Claude Code 自主完成一個多步驟任務：建立專案結構 + 寫基礎程式 + 驗證結果。

## 任務

### 任務 1：單步驟 vs 多步驟
先給 Claude Code 一個單步驟指令：「建立一個 hello.py，印出 Hello World」
再給一個需要 3 個步驟的指令：「建立一個 calculator 專案，包含 main.py、utils.py、tests/test_calc.py，實作加減乘除四個函式」

比較：
- 哪個任務 Claude Code 更需要「自主規劃」？
- 它是怎麼決定執行順序的？

### 任務 2：中途干預實驗
在 Claude Code 執行中途任務時，試著：
1. 修改它正在處理的檔案
2. 或者直接說「停，先做別的事」

觀察：
- Claude Code 如何應對？
- 它有沒有偵測到你的修改？

## 延伸思考
思考：如果任務更複雜（涉及 10 個檔案），你會怎麼把它拆解給 Claude Code？
在你的實際工作中，agentic 工作流最可能用在哪裡？

## 完成後
將解答存入 `answer/ex02-answer.md`
