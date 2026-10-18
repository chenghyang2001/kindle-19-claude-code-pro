# NOTES — 第 8 章練習（快速 demo 模式，未經 QA／reviewer 審查）

## 做了什麼

| 項目 | 檔案 |
| --- | --- |
| 練習 01 解答（依賴圖、parallel/pipeline 架構、時間估算） | `answer/ex01-answer.md` |
| 練習 01 可執行模擬（asyncio，4 種排程 + 依賴順序檢查） | `src/ex01_dag_sim.py` |
| 練習 02 解答（合約、三種錯誤處理、可靠性 vs 彈性） | `answer/ex02-answer.md` |
| agent 間合約（JSON Schema draft 2020-12） | `contracts/research_output.schema.json`（嚴格）、`contracts/writer_input.schema.json`（寬鬆） |
| 合格／不合格樣本 | `samples/research_valid.json`、`samples/research_invalid.json` |
| 合約驗證 CLI | `src/contract.py` |
| 研究 → 寫作協作與錯誤處理模擬（mock agent，6 情境） | `src/ex02_orchestrator.py` |
| pytest | `tests/test_contracts.py` |
| 外部服務 token 範本（只寫範本） | `.env.example` |

環境：專案 `.venv`（Python 3.14.3），套件見 `requirements.txt`（jsonschema 4.26.0、rfc3339-validator、pytest）。

## 驗證結果（實際執行）

1. `src/ex01_dag_sim.py`：全依序 247.9s、parallel+barrier 186.6s、兩 lane pipeline 186.7s、逐項 pipeline 168.1s（理論 240/180/180/160），斷言全過。
2. `src/contract.py`：合格樣本 PASS（exit 0）；不合格樣本 FAIL，抓到 6 個違規（exit 1）。
3. `src/ex02_orchestrator.py`：ok / error / empty / flaky / malformed / garbage 六個情境全部符合預期。
4. `pytest tests`：**12 passed**。

重跑指令（Git Bash）：

```bash
PYTHONUTF8=1 .venv/Scripts/python src/ex01_dag_sim.py
PYTHONUTF8=1 .venv/Scripts/python src/contract.py contracts/research_output.schema.json samples/research_invalid.json
cd src && PYTHONUTF8=1 ../.venv/Scripts/python ex02_orchestrator.py && cd ..
PYTHONUTF8=1 .venv/Scripts/python -m pytest -q tests
```

## 和題目要求的差異

- **題目只要求寫文字解答，這裡多做了可執行的模擬與測試**，用來證明時間估算和錯誤處理策略可行。
- **時間是縮放模擬**：30 秒縮成 0.3 秒，實測多 3% 左右是 Windows 計時誤差，不是真的跑 GitHub/Notion/Drive/Telegram。
- **外部服務沒有串接**：週報系統需要的 GitHub、Notion、Google Drive、Telegram token 只寫在 `.env.example` 範本；研究 agent 用 mock 取代真實 LLM／搜尋 API。
- **題目說「簡化版 schema 即可」**，這裡寫的是完整 JSON Schema 2020-12（含 `if/then` 條件必填、`$defs`、format 檢查），並另做一份寬鬆的消費端 schema 來回答延伸思考。
- 加碼：除了題目的三種失敗，再加 `flaky`（重試後成功）與 `garbage`（信封整個壞掉）兩種情境。

## 已知沒處理的風險

- 重試沒有實作真正的指數退避等待（模擬中直接重試）。
- `parallel()` / `pipeline()` 是用 asyncio 自行模擬，不是 Claude Code Workflow 的真實 API。
- 寫作端合約寬鬆，若研究端改了欄位「意義」而不是名稱，schema 抓不到。
