-- 訂單資料表（金額以「分」為單位，時間存 UTC）
CREATE TABLE IF NOT EXISTS orders (
  id           INTEGER PRIMARY KEY,
  created_at   TEXT    NOT NULL,             -- ISO 8601 UTC
  status       TEXT    NOT NULL CHECK (status IN ('paid','refunded','pending')),
  amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
);
-- 報表依時間區間查詢，必須有索引避免全表掃描
CREATE INDEX IF NOT EXISTS idx_orders_created_status ON orders(created_at, status);
