# 練習慣例（每 session 載入）

> 無 paths: frontmatter — 每個 session 都載入。
> 適用於所有與 demo/ 練習相關的工作。

## 課程結構規範

每課目錄固定格式：

```
demo/[NN-課程名]/
  README.md          — 學習目標與完成標準
  exercise-01-基礎.md
  exercise-02-進階.md
  exercise-03-綜合.md  （選配）
  answer/            — 完成後填入解答
  starter/           — 前一課 answer/ 攜帶來的起點（02課起才有）
  STEP_LOG.md        — 學習步驟記錄
```

## 解答命名規則

| 練習 | 解答檔名 |
|------|---------|
| exercise-01-基礎.md | answer/ex01-answer.md |
| exercise-02-進階.md | answer/ex02-answer.md |
| exercise-03-綜合.md | answer/ex03-answer.md |

## STEP_LOG 更新規則

完成每個步驟後立刻更新 STEP_LOG.md（不要最後一次更新）：

- `⬜` → `🔄` → `✅`
- 耗時欄位填入實際分鐘數
- 踩坑記錄填入 `.claude/gotchas.md`（不只寫在 STEP_LOG）

## carry 規則

完成第 N 課後：

1. 確認 `answer/` 有 ex01/ex02-answer.md（至少兩個）
2. 執行 `/study-scaffold carry N`
3. 驗證 `[N+1]/starter/` 已有檔案

## 學習語言

所有解答用繁體中文撰寫，程式碼保留原語言但註解用繁中。
