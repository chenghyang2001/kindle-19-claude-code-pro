# 練習 01 解答 — Freelancer Dashboard 資料庫 Schema 設計

> 實際檔案：
>
> - `src/db/schema.pg.ts` — 題目要求的 PostgreSQL（Neon）版，通過 `tsc` 型別檢查，並用 `drizzle-kit export` 產出 SQL
> - `src/db/schema.ts` — 本章補充要求的 **SQLite 版**，實際被 API 和測試使用
> - `drizzle/0000_init.sql` — 由 SQLite 版 schema 用 `drizzle-kit generate` 產生的 migration

---

## 任務 1：資料需求分析

### 白話描述拆解

「接案者有多個客戶。每個客戶可以有多個專案。每個專案可以有多筆工時記錄。發票由多筆工時彙整而成，並寄給特定客戶。」

### Entity（資料表）

| 資料表 | 代表什麼 | 備註 |
| --- | --- | --- |
| `clients` | 客戶 | 帶 `owner_id`（接案者 ID），做多租戶隔離 |
| `projects` | 專案 | 屬於一個客戶 |
| `time_entries` | 工時記錄 | 屬於一個專案；請款後掛到一張發票 |
| `invoices` | 發票 | 寄給一個客戶，彙整多筆工時 |

「接案者」本身不另建表：登入系統（NextAuth / JWT）提供使用者 ID，存在 `clients.owner_id`。專案、工時、發票都能透過 client 追溯回擁有者。

### 關係

```
接案者(owner_id) 1 ──< clients 1 ──< projects 1 ──< time_entries >── 0..1 invoices >── 1 clients
```

| 關係 | 類型 | 實作方式 |
| --- | --- | --- |
| 客戶 → 專案 | 一對多 | `projects.client_id` FK |
| 專案 → 工時 | 一對多 | `time_entries.project_id` FK |
| 客戶 → 發票 | 一對多 | `invoices.client_id` FK |
| 發票 → 工時 | 一對多 | `time_entries.invoice_id` FK（可為 NULL） |

**為什麼「發票 ↔ 工時」不是多對多？** 一筆工時只能請款一次，不然會重複收費。所以用工時表上的 nullable `invoice_id` 就夠了：NULL 表示「未請款」，有值表示「已進某張發票」。不需要中介表，也直接擋掉重複請款。

### 必填欄位

| 資料表 | 必填 | 選填 |
| --- | --- | --- |
| clients | id, owner_id, name, version, created_at, updated_at | company, email, phone, notes |
| projects | id, client_id, name, status, hourly_rate, 時間戳 | budget |
| time_entries | id, project_id, started_at, minutes, created_at | invoice_id, description |
| invoices | id, client_id, invoice_number, status, total, created_at | issued_at, due_at |

---

## 任務 2：Drizzle Schema（PostgreSQL 版，對應題目要求）

```ts
import { sql } from "drizzle-orm";
import {
  check, decimal, index, integer, pgTable, text, timestamp, uniqueIndex, uuid,
} from "drizzle-orm/pg-core";

const tsz = (name: string) => timestamp(name, { withTimezone: true });

export const clients = pgTable(
  "clients",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    ownerId: text("owner_id").notNull(),
    name: text("name").notNull(),
    company: text("company"),
    email: text("email"),
    phone: text("phone"),
    notes: text("notes"),
    version: integer("version").notNull().default(1), // 樂觀鎖（見 ex02 延伸思考）
    createdAt: tsz("created_at").notNull().defaultNow(),
    updatedAt: tsz("updated_at").notNull().defaultNow(),
  },
  (t) => [
    index("clients_owner_idx").on(t.ownerId),
    uniqueIndex("clients_owner_email_uq").on(t.ownerId, t.email),
  ],
);

export const projects = pgTable(
  "projects",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    clientId: uuid("client_id").notNull()
      .references(() => clients.id, { onDelete: "restrict" }),
    name: text("name").notNull(),
    status: text("status").notNull().default("active"),
    budget: decimal("budget", { precision: 12, scale: 2 }),
    hourlyRate: decimal("hourly_rate", { precision: 10, scale: 2 }).notNull(),
    createdAt: tsz("created_at").notNull().defaultNow(),
    updatedAt: tsz("updated_at").notNull().defaultNow(),
  },
  (t) => [
    index("projects_client_idx").on(t.clientId),
    index("projects_status_idx").on(t.status),
    check("projects_status_chk",
      sql`${t.status} in ('active','paused','completed','cancelled')`),
  ],
);

export const invoices = pgTable(
  "invoices",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    clientId: uuid("client_id").notNull()
      .references(() => clients.id, { onDelete: "restrict" }),
    invoiceNumber: text("invoice_number").notNull().unique(),
    status: text("status").notNull().default("draft"),
    issuedAt: tsz("issued_at"),
    dueAt: tsz("due_at"),
    total: decimal("total", { precision: 12, scale: 2 }).notNull().default("0"),
    createdAt: tsz("created_at").notNull().defaultNow(),
  },
  (t) => [
    index("invoices_client_idx").on(t.clientId),
    index("invoices_status_idx").on(t.status),
    check("invoices_status_chk", sql`${t.status} in ('draft','sent','paid','void')`),
  ],
);

export const timeEntries = pgTable(
  "time_entries",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    projectId: uuid("project_id").notNull()
      .references(() => projects.id, { onDelete: "cascade" }),
    invoiceId: uuid("invoice_id")
      .references(() => invoices.id, { onDelete: "set null" }),
    description: text("description"),
    startedAt: tsz("started_at").notNull(),
    minutes: integer("minutes").notNull(),
    createdAt: tsz("created_at").notNull().defaultNow(),
  },
  (t) => [
    index("time_entries_project_started_idx").on(t.projectId, t.startedAt),
    index("time_entries_invoice_idx").on(t.invoiceId),
    check("time_entries_minutes_chk", sql`${t.minutes} > 0`),
  ],
);
```

### 型別選擇理由

| 題目要求 | 做法 | 理由 |
| --- | --- | --- |
| 金額用 decimal | `decimal(12,2)` / 時薪 `decimal(10,2)` | float 會讓 `0.1 + 0.2 ≠ 0.3`，發票對不起帳 |
| 時間用 timestamptz | `timestamp(..., { withTimezone: true })` | 客戶可能跨時區，DB 一律存 UTC |
| ID 用 uuid | `uuid().defaultRandom()` | URL 上不會被猜到下一筆；多台機器產生也不衝突 |
| 狀態用 text + 限制 | `text` + `CHECK (status in (...))` | 比 pgEnum 好改（加狀態不用 `ALTER TYPE`），DB 層仍擋非法值 |
| 工時用分鐘 | `integer minutes` | 整數不會有浮點誤差，金額 = 分鐘 × 時薪 / 60，算完四捨五入一次 |

### 索引設計

| 索引 | 對應查詢 | 用途 |
| --- | --- | --- |
| `clients(owner_id)` | `WHERE owner_id = ?` | 每個 API 都帶擁有者過濾 |
| `clients(owner_id, email)` UNIQUE | 新增／更新客戶 | 同一接案者底下 email 不重複（NULL 不受限） |
| `projects(client_id)` | JOIN clients、列某客戶的專案 | FK 欄位，PostgreSQL **不會**自動幫 FK 建索引 |
| `projects(status)` | 「進行中專案」看板 | 常見 WHERE 條件 |
| `time_entries(project_id, started_at)` | 「某專案某月份工時」 | 複合索引，同時支援 JOIN 和日期區間 |
| `time_entries(invoice_id)` | 列發票明細、找未請款工時（`IS NULL`） | 開發票時必查 |
| `invoices(client_id)` | 某客戶的發票 | FK 欄位 |
| `invoices(status)` | 「未付款發票」 | 常見 WHERE 條件 |
| `invoices(invoice_number)` UNIQUE | 依發票號碼查 | 發票號碼不可重複 |

### 刪除行為（onDelete）

| FK | 行為 | 理由 |
| --- | --- | --- |
| projects → clients | `restrict` | 客戶還有專案時不能直接刪，避免誤刪整串資料 |
| invoices → clients | `restrict` | 發票是會計紀錄，不該跟著客戶消失 |
| time_entries → projects | `cascade` | 專案刪了，工時沒有存在意義 |
| time_entries → invoices | `set null` | 作廢刪掉發票時，工時回到「未請款」 |

### 驗證結果

- `npx tsc --noEmit`：PG 版與 SQLite 版 schema 型別檢查通過
- `npx drizzle-kit export --dialect postgresql --schema ./src/db/schema.pg.ts`：成功產出 4 張表 + 4 個 FK + 9 個索引的 SQL
- `npx drizzle-kit generate`（SQLite 版）：`4 tables`，產出 `drizzle/0000_init.sql`，測試時實際 migrate 進記憶體 SQLite

---

## SQLite 版的差異（本章補充：不連 Neon）

| PostgreSQL | SQLite（`src/db/schema.ts`） | 原因 |
| --- | --- | --- |
| `uuid().defaultRandom()` | `text().$defaultFn(() => crypto.randomUUID())` | SQLite 沒有 uuid 型別，由應用層產生 |
| `decimal(12,2)` | `integer` 存「分」（`budget_cents`） | SQLite 的 NUMERIC 底層可能存成浮點數，整數分最安全 |
| `timestamptz` | `integer({ mode: "timestamp_ms" })` | 存 UTC 毫秒，Drizzle 自動轉回 `Date` |
| `text` + CHECK | `text({ enum })` + CHECK | 多了 TypeScript 層的列舉型別 |
| FK 預設生效 | 需 `PRAGMA foreign_keys = ON` | SQLite 預設不檢查外鍵，`src/db/client.ts` 每條連線都會打開 |
