# NOTES — K19 第 1 章練習

> 2026-10-18｜快速 demo 模式（依本專案 CLAUDE.md，未走 writer／QA／reviewer）

## 做了什麼

| 檔案 | 內容 |
| --- | --- |
| `hello.py` | 印出 `Hello World` |
| `calculator/utils.py` | 加減乘除四個函式；除以 0 拋 `ValueError` |
| `calculator/main.py` | CLI：`python main.py 3 + 4`；參數錯誤回傳 exit code 2，數值錯誤回傳 1 |
| `calculator/tests/test_calc.py` | 9 個 pytest 測試（四則運算、負數／小數、除以 0、未知運算子、CLI 正常與錯誤參數） |
| `answer/ex01-answer.md` | 練習 01：Chat vs Code 比較、工具呼叫清單 |
| `answer/ex02-answer.md` | 練習 02：單步驟 vs 多步驟、中途干預、延伸思考 |

## 驗證結果（實際執行）

- `python hello.py` → `Hello World`
- `python calculator/main.py 3 + 4` → `7.0`（exit 0）
- `python calculator/main.py 1 / 0` → `錯誤：除數不可為 0`（exit 1）
- `pytest calculator/tests` → **9 passed**（在 `calculator/` 內與專案根目錄各跑一次都通過）
- 中途干預實測：用 shell 在 `utils.py` 檔尾追加一行 → Claude Code 環境立即通知「檔案在磁碟上被改動」並附上 diff；實驗後已移除該行並重跑測試，仍 9 passed。

## 和題目要求的差異

1. **Claude Chat 未實際操作**：依指示不開 claude.ai，Chat 的回應方式是依常識描述，不是實測截圖。
2. **「停，先做別的事」未實測**：本次是全自動執行，沒有人在中途按 Esc 或插話，改以文字描述 Claude Code 的行為。「修改檔案」那一項有用 shell 模擬並取得真實的偵測通知。
3. **兩個練習在同一個 session 內完成**：題目設想「先單步驟、再多步驟」分兩次下指令觀察；這次 hello.py 和 calculator 的四個檔案是同一回合平行寫入，再統一驗證。
4. **任務 2 的工具觀察對象是本 session 自己**：讀題目用的是 Bash `cat` 而不是 Read 工具，所以解答中註明 Read 本次未被使用。
5. **calculator 多做了一點**：題目只要求四個函式，另外加了 CLI 錯誤處理與除以 0 的明確錯誤，方便示範測試的錯誤案例。
6. 已知的小問題：Pyright 會對 `tests/test_calc.py` 報 import 警告（看不懂動態 `sys.path`），實際執行不受影響；若要消除可加 `conftest.py` 或 `pyproject.toml` 設定 `pythonpath`。
