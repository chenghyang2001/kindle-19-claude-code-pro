# Exercise 02 解答 — 部署策略設計

## 任務 1：多環境設定

### 環境變數相同 vs 不同

| 變數 | Staging | Production | 相同？ | 理由 |
|------|---------|-----------|--------|------|
| `DATABASE_URL` | staging DB | prod DB | ❌ 不同 | 絕對不能共用 DB，否則測試資料污染生產 |
| `NEXT_PUBLIC_API_URL` | `https://api-staging.example.com` | `https://api.example.com` | ❌ 不同 | 不同環境打不同 endpoint |
| `OPENAI_API_KEY` | 同一把 key（建議獨立）| 同一把 key | ⚠️ 建議不同 | 技術上可共用，但 staging 測試請求消耗 prod 配額，建議各環境獨立 key 或設 spending limit |
| `FEATURE_FLAG_NEW_UI` | `true` | `false` | ❌ 不同 | feature flag 本質就是環境差異控制 |

### Vercel 設定方式

```
Vercel Dashboard → Project → Settings → Environment Variables

每個變數可選擇適用環境：
☑ Production   ← prod 值
☑ Preview      ← staging/PR preview 值
☑ Development  ← 本機 vercel dev 用
```

程式碼一律用 `process.env.DATABASE_URL` 讀取，值由 Vercel 根據環境注入。

### 本機 .env 管理

```
專案根目錄
  .env                  ← gitignore，本機開發預設值
  .env.example          ← commit 進去，給新人參考（不含真實值）
  .env.staging.local    ← gitignore，本機模擬 staging 用
  .env.production.local ← gitignore，緊急 debug 時臨時用
```

`.gitignore` 必須包含：
```
.env
.env.local
.env.*.local
```

切換方式：
```bash
cp .env.staging.local .env.local   # 模擬 staging
```

---

## 任務 2：部署前 Checklist（10 項）

| # | 檢查項目 | 驗證方式 | 失敗處理 |
|---|---------|---------|---------|
| 1 | 所有測試通過 | GitHub Actions 全綠 | 🔴 修復後才部署 |
| 2 | 無 lint 錯誤 | `ruff check .` 回傳 0 | 🔴 修復後才部署 |
| 3 | 環境變數齊全 | 比對 `.env.example` 確認無缺漏 | 🔴 補設定後才部署 |
| 4 | DB Migration 已在 staging 跑過 | 手動確認 staging schema 正確 | 🔴 先在 staging 驗證通過 |
| 5 | Staging 功能人工驗收 | 手動點過核心流程（登入/主功能）| 🔴 發現問題修復後才部署 |
| 6 | 安全性掃描 | `bandit -r . -ll` 無 HIGH severity | 🔴 修復後才部署 |
| 7 | 第三方 API 連線正常 | `curl` 測試 OpenAI endpoint | ⚠️ 非核心功能可延後 |
| 8 | 回滾版本確認 | 確認 Git 有可回滾的 tag | 🟡 先打 tag 再部署 |
| 9 | 監控 / Alert 正常 | 確認 Sentry 有在收事件 | ⚠️ 可部署但需立即修監控 |
| 10 | 非尖峰時間部署 | 避免週五下午、大促銷日、早上 9-10 點 | 🟡 急件可例外，需告知團隊 |

---

## 延伸思考：緊急回滾流程

**情境：production 部署後發現嚴重 bug**

```
T+0   發現問題（用戶回報 / Sentry alert / 監控異常）
T+1   確認嚴重程度，決定「回滾 vs 熱修」
        ↓ 嚴重（功能全壞）→ 回滾
T+2   Vercel 一鍵回滾：
        Dashboard → Deployments → 找上一個成功 deploy → "Promote to Production"
T+5   回滾完成，舊版本上線
T+6   確認問題消失（smoke test）
T+10  寫 incident report：根本原因 + 如何避免重演
```

**最快約 3–5 分鐘**。Vercel 的 Promote to Production 是「換指針」不是重新 build，幾乎即時。

---

## 學習洞察

**環境管理的本質是「隔離」**：staging 的存在是讓問題在生產前曝光。
一旦 staging 和 production 共用任何資源（DB、API key、Feature Flag），
隔離就失效了——在 staging 測試通過，不代表 production 安全。
每個環境必須是完全獨立的沙盒，才能發揮環境隔離的價值。
