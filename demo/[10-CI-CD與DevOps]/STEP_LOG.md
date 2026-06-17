# STEP_LOG — [10] CI/CD 與 DevOps

## 開始日期
2026-06-17

## 學習步驟記錄

| # | 步驟 | 狀態 | 耗時 | 備註 |
|---|------|------|------|------|
| 1 | 閱讀 README + 確認學習目標 | ✅ | 5 分鐘 | CI/CD 三層結構：on / jobs / steps |
| 2 | 完成 exercise-01-基礎.md | ✅ | 20 分鐘 | GitHub Actions YAML + pip 快取設計 |
| 3 | 完成 exercise-02-進階.md | ✅ | 20 分鐘 | 多環境變數策略 + 10 項部署 Checklist |
| 4 | 完成 exercise-03-綜合.md（選配） | ✅ | 25 分鐘 | 四階段 DevOps Pipeline + 自動回滾設計 |
| 5 | 將解答存入 answer/ | ✅ | 5 分鐘 | ex01/02/03-answer.md |
| 6 | 填寫本課 STEP_LOG | ✅ | 3 分鐘 | |
| 7 | 執行 carry（攜帶答案到下一課） | ✅ | 1 分鐘 | L10 answer/ → L11 starter/ |

狀態符號：⬜ 未開始 / 🔄 進行中 / ✅ 完成 / ⏭️ 跳過

---

## 踩坑記錄

### 坑 1 — jobs 和 steps 的虛擬機邊界
- **現象**：以為 jobs 之間可以共用檔案（像 steps 一樣）
- **根本原因**：jobs 跑在各自獨立的虛擬機，steps 才共用同一台機器的檔案系統
- **解法**：每個 job 都要各自 checkout + setup，或用 `actions/upload-artifact` 在 jobs 間傳遞產物

### 坑 2 — Vercel 回滾需要「事先記錄」prev_deployment_id
- **現象**：部署失敗想回滾，但不知道要回滾到哪個版本
- **根本原因**：Vercel promote API 需要 deployment ID，不能「回上一個」（沒有相對位置的概念）
- **解法**：部署前的第一步先用 Vercel API 查詢並記錄當前 production deployment ID，存進 `$GITHUB_OUTPUT`

---

## 學習心得

1. **CI/CD 的信任梯度**：PR CI（機器信任）→ Staging（機器+人工）→ Gate（人工確認）→ Production（機器+自動回滾）。每層信任來源不同，合起來才形成完整防線。

2. **環境隔離是 DevOps 的基石**：staging 和 production 共用任何資源（DB、API key）就破壞了隔離，在 staging 通過不代表 production 安全。

3. **回滾速度取決於部署平台架構**：Vercel 的 immutable deployment 讓回滾變成「換指針」（< 30 秒），傳統 VPS 需要 git checkout + build + restart（5–15 分鐘）。

---

## 完成日期
2026-06-17

## 總耗時
約 1 小時 15 分鐘
