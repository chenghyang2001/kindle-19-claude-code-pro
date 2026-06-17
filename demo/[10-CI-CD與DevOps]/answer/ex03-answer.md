# Exercise 03 解答 — 完整 DevOps Pipeline（freelancer-dashboard）

## Pipeline 全貌圖

```
PR opened/updated
      │
      ▼
┌─────────────────────────────────┐
│  Stage 1：PR CI                 │
│  tsc → eslint → jest → pytest   │
│  全過 → 可 merge；任一失敗 → block │
└─────────────┬───────────────────┘
              │ merge to main
              ▼
┌─────────────────────────────────┐
│  Stage 2：Auto Deploy Staging   │
│  vercel deploy --env staging    │
│  smoke test：curl 首頁 = 200？   │
│  Telegram 通知結果              │
└─────────────┬───────────────────┘
              │ 人工確認（手動觸發）
              ▼
┌─────────────────────────────────┐
│  Stage 3：Gate                  │
│  workflow_dispatch 按鈕         │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Stage 4：Production 部署       │
│  vercel deploy --prod           │
│  smoke test：curl prod 首頁     │
│  失敗 → 自動 rollback           │
└─────────────────────────────────┘
```

---

## Stage 1：PR CI（`.github/workflows/ci.yml`）

**觸發條件**：`on: pull_request`（對 main branch 的所有 PR）

```yaml
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx tsc --noEmit

  lint:
    needs: typecheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx eslint . --max-warnings 0

  test:
    needs: typecheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: npm ci && npm test
      - run: pip install -r requirements.txt && pytest
```

Branch Protection Rule：Required status checks = `typecheck` / `lint` / `test`

---

## Stage 2：Auto Deploy Staging（`.github/workflows/staging.yml`）

**觸發條件**：`on: push: branches: [main]`

```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 部署到 Vercel Staging
        run: |
          npx vercel deploy \
            --token ${{ secrets.VERCEL_TOKEN }} \
            --env NEXT_PUBLIC_API_URL=${{ secrets.STAGING_API_URL }} \
            > deployment_url.txt
          echo "DEPLOY_URL=$(cat deployment_url.txt)" >> $GITHUB_ENV

      - name: Smoke Test（首頁 200）
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" $DEPLOY_URL)
          [ "$STATUS" = "200" ] || exit 1

      - name: Telegram 通知
        if: always()
        run: |
          MSG="[freelancer-dashboard] Staging ${{ job.status }}\nURL: $DEPLOY_URL\nCommit: ${{ github.sha }}"
          curl -s -X POST \
            "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
            -d "chat_id=${{ secrets.TELEGRAM_CHAT_ID }}&text=$MSG"
```

---

## Stage 3：Gate（手動確認）

**做法 A — `workflow_dispatch`**：

```yaml
on:
  workflow_dispatch:
    inputs:
      confirm:
        description: '輸入 "deploy" 確認部署到 production'
        required: true

jobs:
  gate-check:
    runs-on: ubuntu-latest
    steps:
      - name: 驗證確認輸入
        run: |
          [ "${{ inputs.confirm }}" = "deploy" ] || exit 1
```

**做法 B — GitHub Environment 審核**：
- Settings → Environments → 建立 `production` environment
- 設定 Required reviewers（指定誰可以批准）
- workflow 中 `environment: production` → 自動等待審核員點「Approve」

---

## Stage 4：Production 部署 + 自動回滾

```yaml
  deploy-production:
    needs: gate-check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 記錄當前版本（供回滾用）
        id: prev-version
        run: |
          PREV=$(curl -s \
            -H "Authorization: Bearer ${{ secrets.VERCEL_TOKEN }}" \
            "https://api.vercel.com/v6/deployments?projectId=${{ secrets.VERCEL_PROJECT_ID }}&target=production&limit=1" \
            | jq -r '.deployments[0].uid')
          echo "prev_deployment_id=$PREV" >> $GITHUB_OUTPUT

      - name: 部署到 Production
        id: deploy
        run: |
          npx vercel deploy --prod \
            --token ${{ secrets.VERCEL_TOKEN }} \
            > prod_url.txt

      - name: Production Smoke Test
        id: smoke
        run: |
          sleep 10
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://freelancer-dashboard.vercel.app)
          [ "$STATUS" = "200" ] || exit 1

      - name: 自動回滾（Smoke Test 失敗時）
        if: failure() && steps.smoke.outcome == 'failure'
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.VERCEL_TOKEN }}" \
            "https://api.vercel.com/v13/deployments/${{ steps.prev-version.outputs.prev_deployment_id }}/promote" \
            -d '{"target": "production"}'

      - name: 最終通知
        if: always()
        run: |
          curl -s -X POST \
            "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
            -d "chat_id=${{ secrets.TELEGRAM_CHAT_ID }}&text=Production 部署 ${{ job.status }}"
```

---

## GitHub Secrets 清單

| Secret 名稱 | 用途 | Stage |
|------------|------|-------|
| `VERCEL_TOKEN` | Vercel CLI 部署認證 | 2、4 |
| `VERCEL_PROJECT_ID` | 識別專案（回滾 API 用）| 4 |
| `STAGING_API_URL` | Staging API endpoint | 2 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot 推送通知 | 2、4 |
| `TELEGRAM_CHAT_ID` | 通知目標 chat ID | 2、4 |
| `NEON_DATABASE_URL` | Staging DB 連線字串 | 2 |
| `NEON_DATABASE_URL_PROD` | Production DB 連線字串 | 4 |

---

## 學習洞察

**完整 DevOps Pipeline 的設計核心是「信任梯度」**：
- Stage 1（PR CI）= 機器信任（跑得過就信）
- Stage 2（Staging）= 機器 + 初步人工（smoke test + 通知）
- Stage 3（Gate）= 人工信任（人確認 staging 沒問題才放行）
- Stage 4（Production）= 機器自動 + 失敗自動救援

每個 stage 的信任來源不同，合在一起形成「層層把關但不依賴單一節點」的防線。
回滾的核心是：**先記錄「現在是哪個版本」，才有能力「回去」**。
