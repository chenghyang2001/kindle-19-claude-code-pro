# 練習 01 解答 — 建立第一個 CI Pipeline

> 實際檔案：[`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
> 本機執行紀錄：[`answer/ci-local-run.log`](ci-local-run.log)

## 任務 1：GitHub Actions Workflow 設計

### 架構

```
push main / 任何 PR
        │
        ▼
   ┌─────────┐  失敗 → 整個 workflow 停止
   │  test   │  pytest
   └────┬────┘
        │ needs: test
        ▼
   ┌─────────┐
   │  lint   │  ruff check + ruff format --check
   └────┬────┘
        │ needs: lint
        ▼
   ┌──────────┐
   │ security │  bandit -r src -ll
   └──────────┘
```

### 完整 YAML

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: "3.11"

jobs:
  test:
    name: 測試（pytest）
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 設定 Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: 快取 pip 下載
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-py${{ env.PYTHON_VERSION }}-${{ hashFiles('requirements*.txt') }}
          restore-keys: |
            pip-${{ runner.os }}-py${{ env.PYTHON_VERSION }}-
      - name: 安裝依賴
        run: python -m pip install -r requirements-dev.txt
      - name: 執行測試
        run: python -m pytest -q

  lint:
    name: 格式檢查（ruff）
    needs: test
    runs-on: ubuntu-latest
    steps:
      # checkout / setup-python / cache / 安裝依賴 同上
      - name: ruff 檢查
        run: |
          python -m ruff check .
          python -m ruff format --check .

  security:
    name: 安全掃描（bandit）
    needs: lint
    runs-on: ubuntu-latest
    steps:
      # checkout / setup-python / cache / 安裝依賴 同上
      - name: bandit 掃描
        run: python -m bandit -r src -ll
```

### 設計說明

| 要求 | 做法 |
| ------ | ------ |
| push main + 任何 PR | `on.push.branches: [main]` + `on.pull_request`（不加過濾＝所有 PR） |
| 三個 job 依序 | `lint.needs: test`、`security.needs: lint`，形成一條鏈 |
| 測試失敗整個停止 | `needs` 的預設行為：上游失敗，下游就顯示 skipped，不會執行 |
| Python 3.11 | 頂層 `env.PYTHON_VERSION: "3.11"`，三個 job 共用（加引號，避免 YAML 把 `3.10` 這類值讀成數字 `3.1`） |
| 額外加的 | `concurrency`：同一分支有新的 push 時取消舊的執行，省 runner 時間 |

為什麼每個 job 都要重新 checkout 和安裝？GitHub Actions 每個 job 都跑在一台全新的 runner 上，彼此不共用檔案系統。這也是快取值得加的原因：一次 push 會裝 3 次依賴。

bandit 用 `-ll`：只有中、高嚴重度才讓 job 失敗，低嚴重度只顯示，避免太多誤報擋住 PR。

## 任務 2：pip 快取

### 快取設定重點

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip            # Linux runner 上 pip 的下載快取位置
    key: pip-${{ runner.os }}-py3.11-${{ hashFiles('requirements*.txt') }}
    restore-keys: |
      pip-${{ runner.os }}-py3.11-
```

- **key** 綁定作業系統、Python 版本、依賴檔的 hash：依賴檔一改，key 就變，不會用到過期的快取。
- **restore-keys** 是退而求其次：精確 key 沒命中時，取同 OS、同 Python 版本最近的快取，至少能少下載一部分。
- 更簡單的寫法是 `actions/setup-python@v5` 加 `cache: pip`，效果相同；題目指定 `actions/cache`，所以用手動寫法。

### 估算（10 個套件，每個 2 秒）

用 `scripts/cache_estimate.py` 計算：

| 情境 | 安裝時間 | 說明 |
| ------ | --------- | ------ |
| 首次執行（沒有快取） | **10 × 2 = 20 秒** | 全部從網路下載安裝，結束後把 `~/.cache/pip` 存成快取（存檔約多花幾秒） |
| 後續執行（快取命中），理想模型 | **省下約 20 秒** | 假設 2 秒全是下載時間 |
| 後續執行，較實際的模型 | 還原快取約 3 秒 → **省約 17 秒** | 還原快取本身要時間 |
| 整條 pipeline | 3 個 job × 20 秒 = **每次 push 理想省約 60 秒** | 每個 job 都會裝一次依賴 |

### 本機實測（補充）

在本機用同一份 `requirements-dev.txt`（4 個直接依賴，約 15 個套件）實測：

| 情境 | 時間 |
|------|------|
| 不用快取，首次下載安裝 | 19.7 秒 |
| 快取命中後重新安裝 | 16.6 秒 |

本機只省了約 3 秒，比估算少很多。原因：**pip 的下載快取只省「下載」，不省「解壓、安裝」**。這台機器網路快、Windows 上寫檔較慢，時間主要花在安裝。所以「每個 2 秒全省下」是樂觀估計；網路越慢、套件越大（例如 numpy、torch），快取省得越多。想連安裝也省掉，可以改快取整個 venv（key 一樣綁依賴檔 hash）。

## 驗證結果

| 驗證 | 結果 |
| ------ | ------ |
| `yaml.safe_load` 解析 ci.yml | ✅（`scripts/validate_yaml.py`） |
| 結構檢查：觸發條件、needs 鏈、3.11、每個 job 都有 cache | ✅ |
| 本機依 needs 順序跑 workflow 的所有 `run` 指令 | ✅ test 16 passed → ruff 通過 → bandit 0 issues |
| 失敗演練：暫時加一個必失敗的測試 | ✅ test job 失敗，lint、security 不執行（exit 1） |
