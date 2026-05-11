# B-02　CRUD 操作生成

> **類別**：B. 功能開發

---

```
為 Article（文章） 資源產生完整 CRUD：
- 資料模型：id: serial primary key, title: varchar(200) not null, content: text not null, author_id: integer references users(id), status: enum('draft','published'), created_at: timestamptz default now()
- 框架：Next.js App Router
- 資料庫：PostgreSQL（Neon Serverless）
包含：建立、讀取（單筆+列表+搜尋）、更新、刪除。
每個端點要有輸入驗證與適當的 HTTP 狀態碼。
```
