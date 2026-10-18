# NOTES — k19 第 15 章（安全審查）練習紀錄

日期：2026-10-18 ／ 模式：kindle-drill 快速 demo（主 Claude 直接寫檔，未派三 agent）

## 做了什麼

1. **讀題**：`exercise-01-基礎.md`（手動找漏洞 + 設計審查 Prompt + 修復）、`exercise-02-進階.md`（自動化審查流程 + 工具 vs Claude 邊界 + 部署 Checklist）。
2. **寫解答**：`answer/ex01-answer.md`、`answer/ex02-answer.md`。
3. **本章補充（實作）**：
   - `vulnerable/app.py`：刻意植入 7 類漏洞（SQL 注入、硬編碼密鑰、弱雜湊 MD5、命令注入、不安全反序列化 pickle、eval、assert 權限檢查）。**所有密鑰為假值**。
   - `vulnerable/exploit_demo.py`：實際跑出攻擊，證明漏洞可被利用。
   - `fixed/app.py`：逐一修復（參數化查詢、環境變數讀密鑰、PBKDF2+salt、shell=False+白名單、json、literal_eval、顯式權限檢查）。
   - `fixed/test_app.py`：pytest 驗功能 + 驗注入防護。
   - 建 `.venv` 安裝 `bandit`、`pytest`，對修復前後各跑一次 bandit，報告存 `reports/`。

## 驗證結果（皆實際執行）

### Bandit 問題數比對（`reports/bandit-*.json`）

| 版本 | 總問題 | HIGH | MEDIUM | LOW |
|------|-------:|-----:|-------:|----:|
| `vulnerable/app.py` | **12** | 3 | 4 | 5 |
| `fixed/app.py` | **3** | **0** | **0** | 3 |

- 修復後 **HIGH 嚴重度歸零**，總問題數 12 → 3（降 75%）。
- 修復版殘留 3 個都是 **LOW**：`B404`（import subprocess）、`B607`（ping 用部分路徑）、`B603`（subprocess 呼叫）。皆因已加「主機名白名單 + shell=False」緩解，屬可接受的工具誤報 → 這也成了 ex02「工具盲區/誤報判讀」的實證素材。

### exploit_demo.py（漏洞版，攻擊成功）

```
V1 SQL 注入 get_user('0 OR 1=1')   -> 回傳全表 [(1,alice,admin),(2,bob,user)]
V1 SQL 注入 login("alice' --",...)  -> 未知密碼仍拿到 token（繞過認證）
V4 命令注入 ping_host('... & echo') -> 輸出含 INJECTED-CMD（額外指令被執行）
V5 pickle 反序列化惡意 blob         -> 攻擊者指定的函式被執行
V6 eval calc("__import__('os')...") -> 可呼叫任意模組
```

### pytest（修復版，防護有效）

```
13 passed in 4.35s
```

含 6 個功能正常測試 + 7 個攻擊防護測試（SQL 注入繞過失敗、命令注入被擋、eval RCE 被擋、非 admin 刪除被拒、缺環境變數密鑰時拒簽 token 等）。

## 重現指令

```bash
python -m venv .venv
.venv/Scripts/python -m pip install bandit pytest
# 攻擊示範
PYTHONUTF8=1 .venv/Scripts/python vulnerable/exploit_demo.py
# 修復版測試（需設假密鑰環境變數）
APP_SECRET_KEY=test-only-fake-key PYTHONUTF8=1 .venv/Scripts/python -m pytest fixed/test_app.py -q
# bandit 前後比對
.venv/Scripts/python -m bandit -r vulnerable/app.py -f json -o reports/bandit-vulnerable.json
.venv/Scripts/python -m bandit -r fixed/app.py      -f json -o reports/bandit-fixed.json
```

## 和題目要求的差異

- **題目 ex01 的程式碼片段是 Node.js**；本專案的可執行實作改用 **Python**（配合「建 .venv 裝 bandit」這個本章補充要求，bandit 只吃 Python）。Node 片段的漏洞分析與修復對映，已在 `answer/ex01-answer.md` 的表格與「修復對映回 Node.js」段落完整涵蓋，概念一對一。
- **ex01 任務 2「實際執行審查 Prompt」**：Prompt 已設計並記錄；「Claude 實跑結果」是以本次對話中我（Claude）對該片段的審查結論整理呈現，未另開 API 呼叫（快速模式、且避免額外成本）。
- **ex02 的 GitHub Actions / pre-commit YAML**：題目重點在「設計流程、Fail/Warn 策略、工具 vs Claude 邊界」，已用文字 + 表格完整設計；未產出實際 `.yml`（本機無 CI 可驗，依快速模式只做最小可玩版本，避免交付未驗證的設定檔）。本專案以「.venv + bandit 前後掃 + pytest」作為該流程的可執行縮影。
- **未做**：未建 GitHub repo、未 push（依限制）；未修改全域 `~/.claude/`。

## 已知限制

- 範例密鑰皆為假值（`my-secret-key`、`P@ssw0rd-FAKE-123`、`test-only-fake-key`），僅供 bandit 偵測與教學，非任何真實憑證。
- `vulnerable/` 是**刻意的壞範例**，切勿複製到正式專案。
