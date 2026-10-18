# NOTES — 第 10 章練習（CI/CD 與部署策略）

> 快速 demo 模式：主 Claude 直接寫檔，沒有經過 code-writer / QA / reviewer 流程。

## 做了什麼

| 項目 | 檔案 |
| ------ | ------ |
| 給 CI 測的示範程式（購物車計價）＋測試 | `src/pricing/cart.py`、`tests/test_cart.py` |
| CI workflow：test → lint → security，含 pip 快取 | `.github/workflows/ci.yml` |
| 部署 workflow 範本（Vercel，staging / production） | `.github/workflows/deploy.yml` |
| 多環境設定檔 | `config/environments/staging.yaml`、`production.yaml` |
| 本機 .env 範本 | `.env.example`、`.env.staging.example` |
| YAML 驗證（`yaml.safe_load` + 結構檢查） | `scripts/validate_yaml.py` |
| 本機依 needs 順序執行 workflow 的 run 指令 | `scripts/run_ci_local.py` |
| 快取時間估算 | `scripts/cache_estimate.py` |
| 驗證腳本本身的測試 | `tests/test_ci_config.py` |
| 解答 | `answer/ex01-answer.md`、`answer/ex02-answer.md`、`answer/ci-local-run.log` |
| 工具設定 | `pyproject.toml`（pytest、ruff）、`requirements-dev.txt`、`.gitignore` |

工具（pytest、ruff、bandit、pyyaml）裝在專案內的 `.venv`，沒有動到全域 Python 或 `~/.claude/`。

## 驗證結果

| 驗證 | 指令 | 結果 |
| ------ | ------ | ------ |
| 所有 YAML 可解析（4 個檔） | `python scripts/validate_yaml.py` | ✅ 全部通過 |
| ci.yml 符合題目（觸發、needs 鏈、3.11、cache） | 同上 | ✅ |
| 多環境設定（變數一致、機密沒寫值、flag 值正確） | 同上 | ✅ |
| 本機跑 workflow 的測試指令 | `python scripts/run_ci_local.py` | ✅ pytest 16 passed → ruff check / format 通過 → bandit 0 issues |
| 失敗演練：暫時加一個必失敗的測試 | 同上 | ✅ test 失敗後停止，lint / security 沒有執行，exit 1（演練後已刪除該測試） |
| 快取估算 | `python scripts/cache_estimate.py` | 首次 20 秒；命中後理想省 20 秒，含還原開銷約省 17 秒 |
| 本機實測 pip 快取 | 暫存 venv 裝同一份依賴 | 無快取 19.7 秒 → 快取命中 16.6 秒（只省約 3 秒） |

重現方式（在專案根目錄）：

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements-dev.txt
PYTHONUTF8=1 .venv/Scripts/python scripts/validate_yaml.py
PYTHONUTF8=1 .venv/Scripts/python scripts/run_ci_local.py
```

## 和題目要求的差異

1. **沒有真的在 GitHub Actions 上跑**：照指示不 push、不建 repo。改用 `run_ci_local.py` 在本機照 needs 順序執行 workflow 裡的 `run` 指令。`uses:` 步驟（checkout、setup-python、cache）在本機會略過，所以 **actions/cache 的實際命中行為沒有驗證到**，只驗了 YAML 結構。
2. **本機 Python 是 3.14，不是 workflow 設定的 3.11**：程式碼只用 3.11 就有的語法（ruff 的 `target-version = "py311"`），但沒有在 3.11 上實際跑過。
3. **練習 02 的 Vercel 部分都只是範本**：`vercel env add`、`vercel env pull`、`vercel rollback`、`deploy.yml` 都需要 Vercel 帳號和 GitHub Secrets（`VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`，只寫名稱，沒有設定），沒有執行。題目情境是 Next.js，但本 repo 沒有建 Next.js 專案，所以 checklist 裡的 `npm run build`、`npm audit` 也沒有執行。
4. **多加的東西**：`concurrency`（取消同分支的舊執行）、`ruff format --check`、`deploy.yml` 範本、多環境設定的自動檢查（機密不可寫值）、快取實測。
5. **快取估算的假設**：題目的「每個套件 2 秒」若全算成下載時間，命中後省 20 秒。實測發現 pip 快取只省下載、不省安裝，這台機器省得少；答案中兩種數字都列出來了。
6. **YAML 小陷阱**：`yaml.safe_load` 用 YAML 1.1 規則，會把 workflow 的 `on:` 讀成布林 `True`。GitHub 本身讀得懂，但自己寫檢查腳本時要同時找 `"on"` 和 `True` 這兩個 key（`validate_yaml.py` 已處理）。

## 已知沒處理的風險

- bandit 用 `-ll`，低嚴重度問題不會讓 CI 失敗。
- `run_ci_local.py` 用 `shell=True` 執行 ci.yml 裡的指令，只適合跑自己 repo 的 workflow，不要拿來跑別人的 YAML。
- 兩環境共用 `OPENAI_API_KEY`（題目設定），staging 有可能用掉 production 的額度。
