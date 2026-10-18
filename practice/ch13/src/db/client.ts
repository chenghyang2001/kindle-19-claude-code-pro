/** 建立 Drizzle + better-sqlite3 連線，第一次連線時自動跑 migration。 */
import path from "node:path";
import fs from "node:fs";
import Database from "better-sqlite3";
import {
  drizzle,
  type BetterSQLite3Database,
} from "drizzle-orm/better-sqlite3";
import { migrate } from "drizzle-orm/better-sqlite3/migrator";
import * as schema from "./schema";

export type Db = BetterSQLite3Database<typeof schema>;

const MIGRATIONS_DIR = path.join(process.cwd(), "drizzle");

export function createDb(file: string): Db {
  if (file !== ":memory:") {
    fs.mkdirSync(path.dirname(path.resolve(file)), { recursive: true });
  }
  const sqlite = new Database(file);
  sqlite.pragma("journal_mode = WAL");
  // SQLite 預設不檢查外鍵，每條連線都要手動開
  sqlite.pragma("foreign_keys = ON");
  const db = drizzle(sqlite, { schema });
  migrate(db, { migrationsFolder: MIGRATIONS_DIR });
  return db;
}

// Next.js dev 會熱重載模組，掛在 globalThis 避免重複開連線
const globalForDb = globalThis as unknown as { __db?: Db };

export function getDb(): Db {
  if (!globalForDb.__db) {
    const file = process.env.DATABASE_FILE;
    if (!file) throw new Error("缺少環境變數 DATABASE_FILE");
    globalForDb.__db = createDb(file);
  }
  return globalForDb.__db;
}
