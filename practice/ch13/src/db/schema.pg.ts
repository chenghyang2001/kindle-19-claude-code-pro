/**
 * 題目要求的 PostgreSQL（Neon）版本 schema。
 * 本專案不連 Neon，這份只做型別檢查（npm run typecheck）與 SQL 產生參考。
 */
import { sql } from "drizzle-orm";
import {
  check,
  decimal,
  index,
  integer,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
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
    version: integer("version").notNull().default(1),
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
    clientId: uuid("client_id")
      .notNull()
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
    check(
      "projects_status_chk",
      sql`${t.status} in ('active','paused','completed','cancelled')`,
    ),
  ],
);

export const invoices = pgTable(
  "invoices",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    clientId: uuid("client_id")
      .notNull()
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
    check(
      "invoices_status_chk",
      sql`${t.status} in ('draft','sent','paid','void')`,
    ),
  ],
);

export const timeEntries = pgTable(
  "time_entries",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    projectId: uuid("project_id")
      .notNull()
      .references(() => projects.id, { onDelete: "cascade" }),
    invoiceId: uuid("invoice_id").references(() => invoices.id, {
      onDelete: "set null",
    }),
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
