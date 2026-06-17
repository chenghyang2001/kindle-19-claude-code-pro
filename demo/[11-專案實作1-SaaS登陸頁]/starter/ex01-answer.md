# Exercise 01 解答 — 建立第一個 CI Pipeline

## 任務 1：GitHub Actions Workflow 設計

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 設定 Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: 安裝依賴
        run: pip install -r requirements.txt

      - name: 跑測試
        run: pytest

  lint:
    needs: test          # test 通過才跑
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff
      - run: ruff check .

  security:
    needs: lint          # lint 通過才跑
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install bandit
      - run: bandit -r . -ll
```

**關鍵設計決策**：
- `needs` 讓三個 job 依序執行：test → lint → security
- 每個 job 各自 checkout + setup（jobs 跑在獨立虛擬機，不共用檔案）
- `push` 和 `pull_request` 都觸發，確保 PR 和 merge 都受保護

---

## 任務 2：加入 pip 快取

快取機制加在 `test` job 的安裝步驟之前：

```yaml
      - name: 快取 pip 套件
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
```

**時間估算**（10 個套件 × 2 秒/個）：

| 情境 | 時間 |
|------|------|
| 首次執行（無快取）| 20 秒 |
| 快取命中 | ~1–2 秒（解壓縮） |
| **節省** | 約 18–19 秒 |

**為什麼用 `hashFiles('requirements.txt')` 當 key**：
requirements.txt 內容改變時才重建快取。沒變就直接用舊快取，確保快而不過期。

---

## 學習洞察

CI Pipeline 的核心設計問題只有一個：**「什麼順序讓失敗最早曝光、成本最低？」**。
測試先跑（最貴但最重要）→ lint（快但沒它也會讓 reviewer 痛苦）→ security（最少人關注但不能省）。
用 `needs` 在 job 層級控制順序，用 `steps` 在同一 job 內部控制步驟。
