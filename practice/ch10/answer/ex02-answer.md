# 練習 02 解答 — 部署策略設計（Next.js → Vercel）

> 實際檔案：
>
> - 多環境設定：[`config/environments/staging.yaml`](../config/environments/staging.yaml)、[`production.yaml`](../config/environments/production.yaml)
> - 本機 .env 範本：[`.env.example`](../.env.example)、[`.env.staging.example`](../.env.staging.example)
> - 部署 workflow 範本：[`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)（**未實際執行**，需要 Vercel 帳號與 GitHub Secrets）

## 任務 1：多環境設定

### 1. 哪些相同、哪些不同？

| 變數 | staging | production | 相同？ | 機密？ |
| ------ | --------- | ----------- | :---: | :---: |
| `DATABASE_URL` | staging DB | production DB | ❌ 不同 | ✅ |
| `NEXT_PUBLIC_API_URL` | `https://api-staging.example.com` | `https://api.example.com` | ❌ 不同 | ❌（會打包進前端，人人看得到） |
| `OPENAI_API_KEY` | 同一把 key | 同一把 key | ✅ 相同 | ✅ |
| `FEATURE_FLAG_NEW_UI` | `true` | `false` | ❌ 不同 | ❌ |

注意兩點：

- **`NEXT_PUBLIC_` 開頭的變數會在 build 時寫進瀏覽器的 JS**，絕對不能放機密。而且它在 build 時就固定，改值要重新部署。
- **`OPENAI_API_KEY` 兩環境共用一把 key 有風險**：staging 跑壓力測試可能把 production 的額度用完。題目設定是共用，所以做法是在 OpenAI 後台設用量上限並監控；更好的做法是兩環境各用一把 key（同一組織下的不同 project key），各自設上限。

### 2. 在 Vercel 設定變數（不洩漏到程式碼）

Vercel 有三個內建環境：**Production / Preview / Development**。對應方式：

| 我們的環境 | Vercel 環境 | 觸發 |
| ----------- | ------------ | ------ |
| production | Production | push / merge 到 `main` |
| staging | Preview，限定 `staging` 分支 | push 到 `staging` 分支 |
| 本機 | Development | `vercel env pull` |

設定方式（**範本，需要 Vercel 帳號，本練習沒有執行**）：

```bash
# production
vercel env add DATABASE_URL production          # 互動輸入值，不會留在 shell history
vercel env add NEXT_PUBLIC_API_URL production
vercel env add OPENAI_API_KEY production
vercel env add FEATURE_FLAG_NEW_UI production   # 輸入 false

# staging（Preview 環境，只套用到 staging 分支）
vercel env add DATABASE_URL preview staging
vercel env add NEXT_PUBLIC_API_URL preview staging
vercel env add OPENAI_API_KEY preview staging
vercel env add FEATURE_FLAG_NEW_UI preview staging   # 輸入 true
```

也可以在 Vercel Dashboard → Project → Settings → Environment Variables 設定，機密欄位勾 **Sensitive**（設定後連自己都看不到明文）。

不洩漏的原則：

1. repo 只放 `.env.example` 這類**沒有真值的範本**；`.env`、`.env.*.local` 都在 `.gitignore`。
2. repo 裡的 `config/environments/*.yaml` 只描述「有哪些變數、是不是機密、值從哪來」，機密只寫 `source: vercel-env`，不寫值。`scripts/validate_yaml.py` 會檢查：標成 `secret: true` 卻寫了 `value` 就判失敗。
3. 如果用 GitHub Actions 部署，需要的 GitHub Secrets 名稱：`VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`（本練習只寫名稱，沒有設定）。DB 連線字串等應用程式變數仍放在 Vercel，不放 GitHub。
4. production 的 GitHub Environment 設「需人工核准」，避免誤推。

### 3. 本機模擬 staging 的 .env 管理

Next.js 載入順序（後面蓋前面）：`.env` → `.env.local` → `.env.[mode]` → `.env.[mode].local`。

建議的檔案配置：

| 檔案 | 入版控？ | 用途 |
| ------ | :---: | ------ |
| `.env.example` | ✅ | 列出所有變數名稱與假值，新人照著複製 |
| `.env.staging.example` | ✅ | staging 用的範本（非機密值可以直接寫，例如 API URL） |
| `.env.local` | ❌ | 平常本機開發，連本機 DB |
| `.env.staging.local` | ❌ | 模擬 staging，用 `vercel env pull` 產生 |

操作方式：

```bash
# 從 Vercel 拉 staging 的真值到本機（不入版控）
vercel env pull .env.staging.local --environment=preview --git-branch=staging

# 用 staging 設定啟動（dotenv-cli 指定要載入的檔）
npx dotenv -e .env.staging.local -- next dev
```

要點：

- 本機模擬 staging 時，**連 staging DB 而不是 production DB**；最好用 staging DB 的唯讀帳號，避免本機誤寫資料。
- 在 `package.json` 加 `"dev:staging": "dotenv -e .env.staging.local -- next dev"`，大家指令一致。
- 啟動時檢查必要變數都存在，缺了就直接報錯，不要用空字串當預設值（錯誤會延後才出現）。

## 任務 2：部署前 Checklist（10 項）

| # | 檢查項目 | 如何驗證 | 失敗怎麼辦 |
| --- | --------- | --------- | ----------- |
| 1 | CI 全部通過（test → lint → security） | GitHub PR 頁面顯示綠勾；或本機 `python scripts/run_ci_local.py` | **延後部署**，修好再重跑 |
| 2 | 在 staging 驗證過同一個 commit | 對照 Vercel staging 部署的 commit SHA 與要上線的 SHA | **延後**，先部署到 staging 驗證 |
| 3 | production 環境變數齊全且正確 | `vercel env ls production`，對照 `config/environments/production.yaml` 的變數清單 | **修復**：補上變數後重新 build（`NEXT_PUBLIC_*` 必須重新 build） |
| 4 | Feature flag 值正確（`FEATURE_FLAG_NEW_UI=false`） | `vercel env ls production` + `python scripts/validate_yaml.py` | **修復**：改值，重新部署 |
| 5 | 資料庫 migration 已備好且可回退 | 在 staging 跑過 up + down；確認 migration 是向下相容的（舊程式碼也能跑新 schema） | 不相容 → **延後**，拆成「先加欄位、後刪欄位」兩次部署 |
| 6 | production DB 有最新備份 | 在 DB 後台確認備份時間（Neon 可建 branch 當快照） | **延後**，先備份 |
| 7 | 正式 build 沒有錯誤與型別錯誤 | `npm run build`、`npx tsc --noEmit` | **延後**，修好再部署 |
| 8 | 依賴沒有高風險漏洞 | `npm audit --audit-level=high` | high/critical → **修復**（升級套件）；確認不影響的可記錄後放行 |
| 9 | 沒有機密寫進程式碼或前端 | `git grep -nE "sk-[A-Za-z0-9]{20,}\|postgres(ql)?://"`；確認機密沒有用 `NEXT_PUBLIC_` 開頭 | **延後**；已 push 的 key 一律視為外洩，立刻作廢重發 |
| 10 | 回滾方案就緒、有人值班 | 確認知道上一個正常部署的 URL；部署後 30 分鐘內有人看監控 | **延後**到有人值班的時段（避免週五晚上部署） |

判斷「修復還是延後」的原則：**能在 10 分鐘內修好、且修完能重跑同一套檢查的，就修；其他一律延後**。不要在部署當下臨時改程式碼又跳過檢查。

## 延伸思考：緊急回滾流程

Vercel 的每次部署都是不可變的，舊版本一直存在，所以回滾**不需要重新 build**，只是把 production 網域指回舊的部署。

| 步驟 | 動作 | 時間 |
| ------ | ------ | ------ |
| 1. 發現 | 監控告警（錯誤率、Vercel Logs）或使用者回報 | 0 分 |
| 2. 判斷 | 確認和本次部署有關（時間點吻合），決定回滾，**先回滾、後查原因** | 1–3 分 |
| 3. 回滾 | Dashboard → Deployments → 選上一個正常版本 → **Instant Rollback**；或 CLI：`vercel rollback <上一版部署 URL>` | 約 1 分（網域切換幾秒內生效） |
| 4. 確認 | 打開網站、看錯誤率回落、跑冒煙測試 | 2–3 分 |
| 5. 處置 | 關掉自動部署避免又被推上去；在 GitHub `git revert` 有問題的 commit（不用 force push） | 回滾後 |
| 6. 檢討 | 寫事後檢討，補一個能抓到這個 bug 的測試 | 當天 |

**最快：從發現到回滾完成約 3–5 分鐘**（判斷 1–3 分 + 操作 1 分 + 確認 1–2 分）。

會讓回滾變慢的情況：

- **資料庫已經改了 schema**：程式碼可以秒回，但資料回不去。所以 checklist 第 5 項要求 migration 向下相容。
- **環境變數也改了**：回滾部署會用回舊部署當時的變數，但如果是外部服務（例如 key 已作廢）就要另外處理。
- 比回滾更快的作法：新功能放在 feature flag 後面，出問題時直接把 flag 關掉，連部署都不用回滾。

## 驗證結果

| 驗證 | 結果 |
| ------ | ------ |
| `yaml.safe_load` 解析 staging.yaml / production.yaml / deploy.yml | ✅ |
| 兩環境變數名稱一致 | ✅ |
| 機密變數沒有寫真值（`secret: true` 不可有 `value`） | ✅；另有測試確認寫了值會被抓到 |
| `FEATURE_FLAG_NEW_UI`：staging `true`、production `false` | ✅ |
| Vercel CLI 指令、deploy.yml、回滾 | ⚠️ 只寫範本，需要 Vercel 帳號，未執行 |
