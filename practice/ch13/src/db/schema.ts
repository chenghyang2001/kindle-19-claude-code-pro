/**
 * Freelancer Dashboard 的 SQLite schema（實際執行用）。
 *
 * 和題目要求（PostgreSQL）的對應：
 * - uuid        → text + crypto.randomUUID()（SQLite 沒有 uuid 型別）
 * - decimal     → integer「分」（SQLite 沒有真正的 decimal，存整數分最安全）
 * - timestamptz → integer（timestamp_ms，一律存 UTC 毫秒）
 * PostgreSQL 版本見 schema.pg.ts。
 */
import { sql } from "drizzle-orm";
import {
  check,
  index,
  integer,
  sqliteTable,
  text,
  uniqueIndex,
} from "drizzle-orm/sqlite-core";

export const PROJECT_STATUSES = [
  "active",
  "paused",
  "completed",
  "cancelled",
] as const;
export const INVOICE_STATUSES = ["draft", "sent", "paid", "void"] as const;

const id = () =>
  text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID());

const timestampMs = (name: string) => integer(name, { mode: "timestamp_ms" });

const createdAt = () =>
  timestampMs("created_at")
    .notNull()
    .$defaultFn(() => new Date());

const updatedAt = () =>
  timestampMs("updated_at")
    .notNull()
    .$defaultFn(() => new Date());

export const clients = sqliteTable(
  "clients",
  {
    id: id(),
    // 擁有者：登入接案者的 ID（JWT sub），做多租戶隔離
    ownerId: text("owner_id").notNull(),
    name: text("name").notNull(),
    company: text("company"),
    email: text("email"),
    phone: text("phone"),
    notes: text("notes"),
    // 樂觀鎖版本號：PUT 時比對，防止兩人同時編輯互相覆蓋
    version: integer("version").notNull().default(1),
    createdAt: createdAt(),
    updatedAt: updatedAt(),
  },
  (t) => [
    index("clients_owner_idx").on(t.ownerId),
    // 同一接案者底下 email 不可重複（NULL 不受限）
    uniqueIndex("clients_owner_email_uq").on(t.ownerId, t.email),
  ],
);

export const projects = sqliteTable(
  "projects",
  {
    id: id(),
    clientId: text("client_id")
      .notNull()
      .references(() => clients.id, { onDelete: "restrict" }),
    name: text("name").notNull(),
    status: text("status", { enum: PROJECT_STATUSES })
      .notNull()
      .default("active"),
    budgetCents: integer("budget_cents"),
    hourlyRateCents: integer("hourly_rate_cents").notNull(),
    createdAt: createdAt(),
    updatedAt: updatedAt(),
  },
  (t) => [
    index("projects_client_idx").on(t.clientId),
    index("projects_status_idx").on(t.status),
    check(
      "projects_status_chk",
      sql`${t.status} in ('active','paused','completed','cancelled')`,
    ),
    check(
      "projects_budget_chk",
      sql`${t.budgetCents} is null or ${t.budgetCents} >= 0`,
    ),
    check("projects_rate_chk", sql`${t.hourlyRateCents} >= 0`),
  ],
);

export const invoices = sqliteTable(
  "invoices",
  {
    id: id(),
    clientId: text("client_id")
      .notNull()
      .references(() => clients.id, { onDelete: "restrict" }),
    invoiceNumber: text("invoice_number").notNull().unique(),
    status: text("status", { enum: INVOICE_STATUSES })
      .notNull()
      .default("draft"),
    issuedAt: timestampMs("issued_at"),
    dueAt: timestampMs("due_at"),
    // 開立時由工時彙整後寫死，之後費率變動不影響已開的發票
    totalCents: integer("total_cents").notNull().default(0),
    createdAt: createdAt(),
  },
  (t) => [
    index("invoices_client_idx").on(t.clientId),
    index("invoices_status_idx").on(t.status),
    check(
      "invoices_status_chk",
      sql`${t.status} in ('draft','sent','paid','void')`,
    ),
  ],
);

export const timeEntries = sqliteTable(
  "time_entries",
  {
    id: id(),
    projectId: text("project_id")
      .notNull()
      .references(() => projects.id, { onDelete: "cascade" }),
    // NULL = 尚未請款；開發票時填入，一筆工時只能進一張發票
    invoiceId: text("invoice_id").references(() => invoices.id, {
      onDelete: "set null",
    }),
    description: text("description"),
    startedAt: timestampMs("started_at").notNull(),
    minutes: integer("minutes").notNull(),
    createdAt: createdAt(),
  },
  (t) => [
    index("time_entries_project_started_idx").on(t.projectId, t.startedAt),
    index("time_entries_invoice_idx").on(t.invoiceId),
    check("time_entries_minutes_chk", sql`${t.minutes} > 0`),
  ],
);

export type Client = typeof clients.$inferSelect;
export type NewClient = typeof clients.$inferInsert;
