import { randomBytes } from "node:crypto";

// 測試一律用記憶體資料庫，不碰 data/dev.db
process.env.DATABASE_FILE = ":memory:";
// 每次執行隨機產生密鑰，不在程式碼裡寫死任何 secret
process.env.AUTH_SECRET = randomBytes(32).toString("hex");
