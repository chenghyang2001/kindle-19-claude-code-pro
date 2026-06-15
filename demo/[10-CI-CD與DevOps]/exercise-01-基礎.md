# 練習 01 — 基礎：建立第一個 CI Pipeline

## 情境說明
你的 Python 專案每次 push 都需要自動跑測試、檢查格式、掃描安全性，確保程式碼品質。

## 任務

### 任務 1：設計 GitHub Actions Workflow
設計一個 `.github/workflows/ci.yml`，包含：

**觸發條件：**
- push 到 main branch
- 任何 Pull Request（PR）

**三個 job（必須依序執行）：**
1. `test`：用 pytest 跑所有測試，失敗時阻止後續 job
2. `lint`：用 ruff 檢查程式碼格式
3. `security`：用 bandit 掃描安全性問題

**要求：**
- job 之間用 `needs` 設定依賴（test 先跑，通過才跑 lint）
- 測試失敗時整個 workflow 停止
- 設定 Python 3.11 環境

設計重點：不需要完全可執行，但 YAML 結構必須正確，步驟邏輯要說得通。

### 任務 2：加入 pip 快取
在 workflow 中加入 pip 快取機制（`actions/cache`），減少重複安裝套件的時間。

估算：一個有 10 個依賴套件的專案，每個安裝需要 2 秒，加入快取後：
- 首次執行：需要幾秒？
- 後續執行（快取命中）：節省幾秒？

## 完成後
將 workflow YAML 設計 + 快取估算存入 `answer/ex01-answer.md`
