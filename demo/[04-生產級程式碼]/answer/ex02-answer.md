# 練習 02 解答 — 程式碼品質 Checklist 實戰

## 任務 1：10 項品質 Checklist

| 優先 | 項目 | 如何驗證 | 違反後果 |
|:---:|------|---------|---------|
| 🔴 1 | 所有 SQL 查詢用參數化（`%s`，不用 f-string） | grep `execute(f"` 應該零結果 | SQL 注入，資料庫整個被讀取/刪除 |
| 🔴 2 | API Key / 密碼從環境變數讀取，不硬編碼 | grep `password=` 應該只有 `os.environ` | 一旦 commit 永久洩漏，git history 留著 |
| 🔴 3 | 所有外部 I/O（DB / HTTP / 檔案）有 try/except | 找每個 connect() / requests.get() / open() 確認有包 try | 外部失敗讓整個程式 crash，無降級 |
| 🟠 4 | DB 連線 / 檔案 handle 必定關閉（finally 或 with） | 找每個 `conn = ` 確認有 finally 或 with | 連線池耗盡，服務掛掉 |
| 🟠 5 | 使用者輸入有驗證（型別、範圍、長度） | 看每個接受外部輸入的函式入口 | 崩潰或非預期行為，可被利用做 DoS |
| 🟠 6 | 敏感資訊不寫進 log（密碼、token、信用卡號） | 搜尋 logger 輸出確認無 password / token 欄位 | log 系統洩漏機密，被 log 收集系統索引 |
| 🟡 7 | 函式有明確回傳型別標注，None 可能性明確說明 | 看函式簽名有無 `-> dict | None` 等 | 呼叫方不知道要判斷 None，NPE 風險 |
| 🟡 8 | 不用裸 `except:`，只捕捉具體例外類型 | grep `except:` 應該零結果 | 把 KeyboardInterrupt、SystemExit 也吞掉 |
| 🟡 9 | 迴圈內不重複建立 DB 連線 | 看迴圈裡有無 connect() | N+1 連線，效能急劇惡化 |
| 🟢 10 | 有 `if __name__ == "__main__":` 冒煙測試 | 直接 python file.py 跑一次 | 基本功能沒有任何驗證，錯誤延後爆發 |

## 任務 2：套用到 fetch_user（原始有問題版本）

| # | 項目 | 結果 | 說明 |
|---|------|------|------|
| 1 | 參數化查詢 | ❌ 不通過 | `f"SELECT * WHERE id={user_id}"` |
| 2 | 環境變數 | ❌ 不通過 | `password='1234'` 硬編碼 |
| 3 | try/except | ❌ 不通過 | 完全沒有 |
| 4 | 連線關閉 | ❌ 不通過 | 無 finally，無 with |
| 5 | 輸入驗證 | ❌ 不通過 | user_id 未驗證型別 |
| 6 | log 無機密 | ✅ 不適用 | 完全沒有 log（但這本身是問題 3）|
| 7 | 回傳型別 | ❌ 不通過 | 無型別標注，fetchone 回 tuple 或 None |
| 8 | 具體例外 | ❌ 不通過 | 沒有任何 except |
| 9 | 迴圈連線 | ✅ 通過 | 只建一次連線 |
| 10 | 冒煙測試 | ❌ 不通過 | 無任何測試 |

**最嚴重問題**：SQL 注入（#1）— 修復見練習 01 任務 2。

## 延伸思考：讓 Checklist「不得不做」

光靠人工 checklist 會被省略，有三層強制機制：

| 層級 | 工具 | 觸發時機 |
|------|------|---------|
| 本機即時 | Claude Code PostToolUse hook → `ruff` / `bandit` | 每次 Write .py 自動掃 |
| commit 前 | `pre-commit` hook → `bandit -r .` | `git commit` 時強制通過 |
| CI 遠端 | GitHub Actions → bandit + pytest | push 後自動跑，失敗不讓 merge |

**結論**：checklist 是「知道要查什麼」，hook + CI 才是「保證有查」。人的記憶不可靠，exit code 永遠可靠。
