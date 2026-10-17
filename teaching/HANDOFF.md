# K19 演練交接

## 原機器結果

2026-06-16 起在 `demo/` 依書做過一輪學習課程（15 課＋3 附錄），各課解答在 `demo/[NN-…]/answer/`、過程在 `STEP_LOG.md`。快速模式的差異以「和 demo 原解答／題目要求的差異」記錄。

## 快速模式進度表

| 章 | 完成日 | 實際耗時 | 和原解答／題目要求的差異 |
| --- | --- | --- | --- |
| 01 | 2026-10-18 | 4 分 | Chat 端依常識描述未實測；中途干預用 shell 改檔模擬；calculator 多做 CLI 錯誤處理，9 passed |
| 02 | 2026-10-18 | 11 分 | 改寫前後 8 份提示詞皆 claude -p 實跑並用 pytest 驗產出（13 passed 1 xfailed）；對照組受全域 CLAUDE.md 污染，--bare 需 API key 只留範本；ex02 只實測情境 B |
| 03 | 2026-10-18 | 9 分 | hooks 只寫專案 .claude/settings.json，claude -p 實測觸發通過、pytest 4 passed；用 ruff format 取代 black；本章無 MCP 任務；開窗時誤開兩個已關閉，改預先允許外部 imports |
| 04 | 2026-10-18 | 5 分 | pymysql 改 sqlite3，參數化／環境變數／finally／logging 全做，28 passed（含 SQL 注入測試）；無 starter 改自寫函式；pre-commit 與 Actions 只寫範本 |
| 05 | 2026-10-18 | 7 分 | 實際重現 pandas ValueError traceback 再修復（17 passed）＋Flask log decorator（11 passed）；真實 traceback 比題目多 9 層內部框架；decorator 多做遮蔽與抽樣 |
