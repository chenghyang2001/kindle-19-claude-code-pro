# Demo-1：如何使用提示詞範本庫

## 這個 Demo 在示範什麼

**提示詞範本庫的使用流程分三步：**

```
Step 1                    Step 2                    Step 3
打開範本             →    填入你的專案資訊        →    貼到 Claude 執行
prompt-library-with-       把 [xxx] 換成真實值          複製 response.md
dummy-example-value/       （範本已幫你填好）           的輸出用在專案
```

## Demo 情境

**專案**：TechBlog 部落格平台（Next.js 16 + PostgreSQL）
**任務**：建立「文章收藏（Bookmark）」功能

## 5 個步驟 × 使用哪個範本

| 步驟 | 範本檔案 | 用途 |
|------|---------|------|
| Step 1 | `A-核心框架/A-01_五要素提示詞結構.md` | 告訴 Claude 專案情境 |
| Step 2 | `B-功能開發/B-01_新功能鷹架.md` | 規劃功能架構與檔案清單 |
| Step 3 | `G-資料庫/G-01_Schema 設計.md` | 設計資料庫 Schema |
| Step 4 | `D-測試策略/D-05_API 端點測試.md` | 撰寫 API 測試 |
| Step 5 | `C-除錯與診斷/C-01_標準除錯協議.md` | 診斷並修復 Bug |

## 每個步驟的資料夾結構

```
step-N_名稱/
├── prompt.md     ← 你貼給 Claude 的提示詞（已填好值）
└── response.md   ← Claude 實際產生的輸出（含程式碼）
```

## 怎麼在你的專案複用

1. 打開 `prompt-library-with-dummy-example-value/` 中的任意範本
2. 將 TechBlog 的範例值換成你的專案值
3. 貼到 Claude Code（`claude`）或 Claude Chat（claude.ai）
4. 得到 `response.md` 這樣的輸出，直接用在專案中
