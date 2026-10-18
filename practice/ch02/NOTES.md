# NOTES — K19 第 2 章練習（提示詞改寫與角色提示詞）

快速 demo 模式（依本專案 CLAUDE.md），全自動執行，2026-10-18。

## 做了什麼

| 項目 | 檔案 |
| --- | --- |
| 範例程式碼（讓提示詞有具體對象） | `samples/discount.py`（待重構）、`samples/avg_bug.py`（空清單 bug）、`samples/user_service.ts`（藏型別問題，`tsc --strict` 0 錯誤）、`samples/quotes_spider.py`（情境 A，未執行） |
| 提示詞（改寫前後／有無角色） | `prompts/ex01/p{1,2,3}-{before,after}.txt`、`prompts/ex02/b-{norole,role}.txt` |
| 批次實跑腳本 | `scripts/run_compare.py`：清掉 `CLAUDE*` 環境變數、每次 `timeout=120s`、提示詞走 stdin、在空暫存目錄執行、`--tools ""`、4 個並行、輸出 + 指標 JSON；支援 `--dry-run` |
| claude -p 原始輸出 | `outputs/ex01-*.md`（6 份）、`outputs/ex02-*.md`（2 份）、`outputs/metrics-ex01-ex02.json` |
| 驗證測試 | `tests/test_outputs.py`：把子 claude 寫的程式碼抽出來**實際執行** |
| 解答 | `answer/ex01-answer.md`、`answer/ex02-answer.md` |

重跑方式：

```bash
PYTHONUTF8=1 python scripts/run_compare.py            # 重新實跑 8 個提示詞（約 1.5 分鐘，並行）
PYTHONUTF8=1 python -m pytest tests/test_outputs.py -v # 驗證產出的程式碼
```

## 驗證結果

- `claude -p` 實跑 **8/8 成功**，無逾時（47～87 秒）。
- pytest：**13 passed、1 xfailed**。
  - ex01①：兩版重構與原版在 120 組輸入上結果一致；**原版提示詞的重構刪掉了 `calc` 名稱且回傳型別 int→float**，改寫版兩者都保住。
  - ex01②：原 bug 可重現；兩版修正都符合規格；改寫版自附 assert 全過。原版多加了 3 種沒要求的錯誤規則。
  - ex01③：原版只反問 6 題、0 行程式碼；改寫版 FastAPI 程式用 TestClient 實測 401/201/409/422/200/204/404 與 RFC 7807 全過，**但 138 行超過 120 行限制**（xfail，模型自稱約 115 行）。
  - ex02：原始 TS 在 `tsc --strict` 0 錯誤（拿掉 `as string` 才出現 TS2367）；無角色／有角色兩份修正版都過 `tsc --strict` 與 6 項 runtime 測試。有角色多找到 4 個問題（13 vs 9），但嚴重度偏高、修正版長 2 倍以上。

## 和題目要求的差異

1. **多做**：題目只要求寫文字，這裡額外建了範例程式碼，並用 pytest／tsc／node 實際執行子 claude 產出的程式碼，把「品質差異」變成可驗證的結果。
2. **ex01 也實跑**：題目只在 ex02 要求實測；依使用者補充要求，ex01 的 3 組改寫前後也各跑一次 `claude -p`。
3. **ex02 只實測情境 B**：題目要求「選一個」實測。情境 A 需要 Scrapy（本機未安裝，且要連外部網站），情境 C 是純設計題，兩者只提供角色提示詞範本，未實跑。
4. **每個提示詞只跑 1 次**：LLM 輸出有隨機性，樣本數 1 只能當示意，不是統計結論。
5. **對照組有污染**：子 claude 仍會讀到使用者的全域 `~/.claude/CLAUDE.md`（大量程式碼品質規則），所以「原版／無角色」輸出比一般環境好，差距被縮小。要完全乾淨的對照需用 `claude -p --bare`，但 `--bare` 只接受 `ANTHROPIC_API_KEY`（會扣 API Credits，且違反「不在全域設 API Key」的成本規則），所以**未執行**。範本如下（需自備 API key）：

   ```bash
   # 範本：需 API key，會產生 API 費用，本練習未執行
   ANTHROPIC_API_KEY=<你的 key> env -u CLAUDECODE timeout 120 claude -p --bare --tools "" < prompts/ex01/p3-before.txt
   ```

6. **`--tools ""`**：為了只比較「提示詞 → 文字回答」的品質，子 claude 不給任何工具（不能讀檔、跑程式），所以它們的程式碼都標註「未實際執行」，由本專案的 pytest 補驗證。
7. 未修改全域 `~/.claude/`、未 push、未建 GitHub repo；只在本機 commit。

## 已知限制

- `run_compare.py` 的 `asks_back`（是否反問）指標是關鍵字啟發式，③原版明明是反問卻判成 `false`（用語是「請回答」），以人工判讀為準。
- `tests/test_outputs.py` 依賴 `outputs/` 的內容；重跑 `run_compare.py` 後輸出會變，部分斷言（例如 `test_p1_before_breaks_interface`、xfail 的行數）可能不再成立——它們記錄的是 2026-10-18 這次的觀察。
