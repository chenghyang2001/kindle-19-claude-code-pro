# Exercise 01 解答 — 撰寫 CLAUDE.md

## 任務 1：最小可用 CLAUDE.md（Flask API 版）

```markdown
# Task Manager API — CLAUDE.md

## 專案說明
這是一個 RESTful 任務清單 API，提供任務的 CRUD 操作與使用者認證。
解決問題：讓前端 SPA 和行動 App 能透過統一 API 管理個人任務與協作清單。

## 技術堆疊
- 語言：Python 3.11
- 框架：Flask 3.x + Flask-SQLAlchemy + Flask-Migrate
- 資料庫：PostgreSQL 15（開發用 SQLite）
- 認證：JWT（flask-jwt-extended）
- 部署：Heroku（Eco Dyno + Heroku Postgres）
- 測試：pytest + pytest-flask

## 執行方式

### 開發伺服器
```bash
cp .env.example .env      # 填入本機設定
flask db upgrade          # 套用 migration
flask run --debug         # 啟動在 localhost:5000
```

### 跑測試
```bash
pytest                    # 全部測試
pytest -k test_auth       # 只跑認證相關
pytest --cov=app          # 含覆蓋率報告
```

### 建立新 migration
```bash
flask db migrate -m "描述變更"   # 生成 migration 檔
flask db upgrade                 # 套用到本機 DB
```

## 目錄結構
```
app/
  __init__.py       — 工廠函式（create_app）
  models/           — SQLAlchemy 資料模型
  routes/           — Blueprint 路由（auth / tasks / users）
  schemas/          — Marshmallow 序列化 schema
  utils/            — 共用工具（auth_guard / error_handler）
migrations/         — Flask-Migrate 自動生成，不手動修改
tests/              — pytest 測試，與 app/ 鏡像結構
.env.example        — 環境變數範本（不含真實值）
```

## 禁止事項
- **直接操作 production DB**（所有改動走 migration，不跑裸 SQL）
- **執行 DROP / TRUNCATE**（任何環境都禁止）
- **force push 到 main / staging**（PR + review 才能 merge）
- **刪除 migrations/ 下的任何檔案**（會破壞 migration 歷史鏈）
- **commit 任何 .env 或 secret**（.env 已在 .gitignore，不可移除此設定）

## 常用指令
```bash
flask run --debug                     # 啟動開發伺服器
pytest -x                             # 遇第一個失敗停下
flask db migrate -m "add column X"   # 新增 migration
flask db upgrade / downgrade          # 套用 / 回滾 migration
heroku logs --tail -a task-api-prod   # 看 production log
```
```

---

## 任務 2：測試有效性

在新 session 中提問 + Claude 的回答品質評估：

### 問題 1：「這個專案是做什麼的？」
**Claude 應能引用**：「RESTful 任務清單 API，提供任務 CRUD + 使用者認證」
**評估**：✅ 專案說明區塊清晰，Claude 能直接引用

### 問題 2：「我要怎麼跑測試？」
**Claude 應能引用**：`pytest` / `pytest -k test_auth` / `pytest --cov=app`
**評估**：✅ 執行方式區塊有明確指令，Claude 能逐步引導

### 問題 3：「這個專案有什麼操作是被禁止的？」
**Claude 應能引用**：5 條禁止事項（prod DB / DROP / force push / 刪 migration / commit secret）
**評估**：✅ 禁止事項區塊條列式，Claude 能完整回答

### 觀察：哪些問題答不好？
- 若問「現在有哪些 API endpoint？」→ CLAUDE.md 沒有 endpoint 清單，Claude 只能說「看 routes/ 目錄」
- 若問「資料庫 schema 長什麼樣？」→ 沒有 schema 說明，需要 Claude 自己去讀 models/

### 改善建議
可以補一個「API 端點一覽」區塊，但這會讓 CLAUDE.md 隨著 API 演進而需要手動維護。
→ 更好的做法：用 `@doc/api.md` 引用獨立文件，讓主 CLAUDE.md 保持精簡。

---

## 學習洞察
**CLAUDE.md 的「禁止事項」是最高 ROI 的投資**：Claude 的預設行為傾向「幫你做事」，
而不是「主動問這件事能不能做」。明確的禁止事項讓 Claude 在提議操作前會先自我檢查，
避免它在不知情的情況下提出危險指令（例如「直接 UPDATE 一下 prod DB 的資料吧」）。
