# 練習 01 解答：撰寫 CLAUDE.md

## 任務 1：Flask API 專案的最小可用 CLAUDE.md

```markdown
# CLAUDE.md — Flask Task API

## 專案說明
任務管理 REST API，供前端 SPA 消費。使用者可建立、編輯、刪除任務，支援標籤分類與截止日提醒。

## 技術堆疊
- Python 3.11 + Flask 3.0
- SQLAlchemy 2.0（ORM）+ PostgreSQL 15（開發用 SQLite）
- 部署：Render.com（Web Service）

## 執行方式
# 安裝依賴
pip install -r requirements.txt

# 啟動開發伺服器
flask run --debug

# 跑測試
pytest tests/ -v

# 資料庫 migration
flask db upgrade

## 目錄結構
app/
  models/     — SQLAlchemy 模型
  routes/     — Blueprint 路由（每個功能一個檔案）
  schemas/    — Marshmallow 序列化
tests/        — pytest 測試
migrations/   — Alembic 遷移檔

## 禁止事項
- 絕對不能直接對 Render 上的 production DB 執行 INSERT/UPDATE/DELETE
- 不能在沒有 migration 的情況下直接修改 DB schema
- 不能把 SECRET_KEY / DATABASE_URL 硬編碼進程式碼
- 不能跳過 pytest（--no-verify 模式下禁止 commit）

## 常用指令
flask run --debug          # 開發模式
pytest tests/ -v           # 跑全部測試
flask db upgrade           # 套用 migration
flask shell                # 進 Flask REPL（debug 用）
git push origin main       # 觸發 Render 自動部署
```

---

## 任務 2：有效性測試結果

| 問題 | 答得好？ | 原因 |
|------|---------|------|
| 這個專案是做什麼的？ | ✅ | 「專案說明」區塊直接引用 |
| 我要怎麼跑測試？ | ✅ | 「執行方式」有 `pytest tests/ -v` |
| 有什麼操作是被禁止的？ | ✅ | 「禁止事項」四條明確列出 |

---

## 核心洞察

**最容易被省略但最重要的是「禁止事項」。**

其他五個區塊定義「Claude 能做什麼」，「禁止事項」定義「Claude 絕對不能做什麼」。少了這塊，Claude Code 在 agentic 模式下可能自作主張做出不可逆操作（直接 DROP TABLE、修改 prod 環境）。

CLAUDE.md 的本質是「把你腦中的隱性規則顯性化」— 讓 Claude Code 在新 session 不需要重新問脈絡，直接知道邊界。
