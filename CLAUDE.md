# Claude Code 專業指南 — Claude Code 學習專案

## 專案說明

這是《Claude Code Pro》（Ethan Cole）的結構化學習課程，由 study-scaffold skill 自動生成。

## 架構

- `demo/[NN-課程名]/` — 各課練習（基礎→進階→綜合）
- `demo/[NN]/answer/` — 本課解答（完成後填入）
- `demo/[NN]/starter/` — 來自上一課的 answer/（自動攜帶）
- `docs/` — 學習指南與踩坑記錄
- `chapter-pdfs/` — 各章 PDF
- `chapter-pptx/` — 各章簡報

## 攜帶機制

完成第 N 課後執行：
`/study-scaffold carry N`
→ 自動把 [N]/answer/ 複製到 [N+1]/starter/

## 現有演練專案

- `email-automation-演練/` — 第 12 章實作（Gmail→Notion→Telegram Pipeline）
- `freelancer-dashboard/` — 第 13 章實作（Next.js + Neon PostgreSQL）

## 技術堆疊

- Python 3.9+（第 4–7、12 章練習）
- TypeScript / Next.js（第 11–13 章練習）
- Claude CLI / MCP（第 3、8–9 章練習）

## 共用規則（兩個 Kindle 專案共享）

@../shared-kindle/epub-techniques.md
@../shared-kindle/kindle-workflow.md
