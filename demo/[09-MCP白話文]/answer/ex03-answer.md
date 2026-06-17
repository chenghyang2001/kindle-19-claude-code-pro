# Exercise 03 解答 — 設計自訂 PM2.5 MCP Server

## 任務 1：兩個 MCP Tool 的 JSON Schema

### Tool 1：`get_room_pm25`

```json
{
  "name": "get_room_pm25",
  "description": "取得指定場域在指定日期的 PM2.5 數據。資料來源為 AWS RDS MySQL（唯讀）。",
  "inputSchema": {
    "type": "object",
    "properties": {
      "room_id": {
        "type": "integer",
        "description": "場域 ID（來自 AIHCR rooms 表，例如 142）"
      },
      "date": {
        "type": "string",
        "format": "date",
        "description": "查詢日期，格式 YYYY-MM-DD（例如 2026-06-17）"
      },
      "aggregation": {
        "type": "string",
        "enum": ["hourly", "daily"],
        "default": "daily",
        "description": "資料聚合粒度：hourly 回傳 24 筆，daily 回傳 1 筆日均值"
      }
    },
    "required": ["room_id", "date"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "room_id": { "type": "integer" },
      "room_name": { "type": "string" },
      "date": { "type": "string" },
      "aggregation": { "type": "string" },
      "records": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "timestamp": { "type": "string", "format": "datetime" },
            "pm25": { "type": "number", "description": "PM2.5 μg/m³，998 表示感測器故障" },
            "sensor_status": {
              "type": "string",
              "enum": ["ok", "fault", "missing"],
              "description": "ok: 正常, fault: 故障（998）, missing: 無資料"
            }
          }
        }
      },
      "summary": {
        "type": "object",
        "properties": {
          "avg_pm25": { "type": "number", "description": "排除 998 後的平均值" },
          "max_pm25": { "type": "number" },
          "fault_count": { "type": "integer", "description": "pm25=998 的筆數" },
          "valid_count": { "type": "integer" }
        }
      }
    }
  }
}
```

**範例回應（daily）**：
```json
{
  "room_id": 142,
  "room_name": "台北信義區辦公室",
  "date": "2026-06-17",
  "aggregation": "daily",
  "records": [
    {
      "timestamp": "2026-06-17T00:00:00+08:00",
      "pm25": 23.4,
      "sensor_status": "ok"
    }
  ],
  "summary": {
    "avg_pm25": 23.4,
    "max_pm25": 23.4,
    "fault_count": 0,
    "valid_count": 1
  }
}
```

---

### Tool 2：`get_anomaly_rooms`

```json
{
  "name": "get_anomaly_rooms",
  "description": "回傳指定日期有異常值的場域清單。異常定義：PM2.5=998（感測器故障）或 PM2.5>150（重度污染）。",
  "inputSchema": {
    "type": "object",
    "properties": {
      "date": {
        "type": "string",
        "format": "date",
        "description": "查詢日期，格式 YYYY-MM-DD"
      },
      "anomaly_type": {
        "type": "string",
        "enum": ["all", "fault", "pollution"],
        "default": "all",
        "description": "all: 兩種都查, fault: 只查 998, pollution: 只查 >150"
      }
    },
    "required": ["date"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "date": { "type": "string" },
      "total_rooms": { "type": "integer", "description": "總場域數（41）" },
      "anomaly_count": { "type": "integer" },
      "anomalies": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "room_id": { "type": "integer" },
            "room_name": { "type": "string" },
            "anomaly_type": {
              "type": "string",
              "enum": ["fault", "pollution"]
            },
            "anomaly_value": {
              "type": "number",
              "description": "故障時為 998，污染時為實際 PM2.5 值"
            },
            "first_occurrence": {
              "type": "string",
              "format": "datetime",
              "description": "異常首次發生時間"
            },
            "duration_minutes": {
              "type": "integer",
              "description": "異常持續分鐘數（估算）"
            }
          }
        }
      }
    }
  }
}
```

**範例回應**：
```json
{
  "date": "2026-06-17",
  "total_rooms": 41,
  "anomaly_count": 3,
  "anomalies": [
    {
      "room_id": 142,
      "room_name": "台北信義區辦公室",
      "anomaly_type": "fault",
      "anomaly_value": 998,
      "first_occurrence": "2026-06-17T09:30:00+08:00",
      "duration_minutes": 120
    },
    {
      "room_id": 207,
      "room_name": "新北板橋廠",
      "anomaly_type": "pollution",
      "anomaly_value": 178.5,
      "first_occurrence": "2026-06-17T14:00:00+08:00",
      "duration_minutes": 60
    }
  ]
}
```

---

## 任務 2：MCP Server 架構偽程式碼

```python
"""PM2.5 MCP Server — 唯讀查詢，連接 AWS RDS MySQL（zap_api）"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import pymysql
import os

server = Server("pm25-mcp-server")

# ━━━ 1. 工具註冊 ━━━
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_room_pm25",
            description="取得指定場域在指定日期的 PM2.5 數據",
            inputSchema=GET_ROOM_PM25_SCHEMA  # 上面設計的 JSON Schema
        ),
        Tool(
            name="get_anomaly_rooms",
            description="回傳指定日期有異常值的場域清單",
            inputSchema=GET_ANOMALY_ROOMS_SCHEMA
        )
    ]

# ━━━ 2. 接收呼叫請求 ━━━
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_room_pm25":
        return await handle_get_room_pm25(arguments)
    elif name == "get_anomaly_rooms":
        return await handle_get_anomaly_rooms(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

# ━━━ 3. 連接 MySQL（唯讀）━━━
def get_connection():
    return pymysql.connect(
        host=os.environ["ZAP_DB_HOST"],
        user=os.environ["ZAP_DB_USER"],  # rd2（唯讀帳號）
        password=os.environ["ZAP_DB_PASS"],
        database="zap_api",
        cursorclass=pymysql.cursors.DictCursor
    )

# ━━━ 4. Tool 實作（只能 SELECT）━━━
async def handle_get_room_pm25(args: dict):
    room_id = args["room_id"]
    date = args["date"]
    aggregation = args.get("aggregation", "daily")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 參數化查詢，防 SQL injection；排除 998 故障值計算平均
        if aggregation == "hourly":
            cursor.execute("""
                SELECT DATE_FORMAT(timestamp, '%Y-%m-%dT%H:00:00') as ts,
                       AVG(pm25) as pm25
                FROM median
                WHERE room_id = %s AND DATE(timestamp) = %s
                GROUP BY HOUR(timestamp)
                ORDER BY ts
            """, (room_id, date))
        else:
            cursor.execute("""
                SELECT AVG(CASE WHEN pm25 != 998 THEN pm25 END) as avg_pm25,
                       MAX(CASE WHEN pm25 != 998 THEN pm25 END) as max_pm25,
                       SUM(CASE WHEN pm25 = 998 THEN 1 ELSE 0 END) as fault_count
                FROM median
                WHERE room_id = %s AND DATE(timestamp) = %s
            """, (room_id, date))
        rows = cursor.fetchall()
        return [TextContent(type="text", text=json.dumps(build_pm25_response(room_id, date, aggregation, rows)))]
    finally:
        conn.close()

# ━━━ 5. 啟動 MCP Server ━━━
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    asyncio.run(stdio_server(server))
```

**關鍵設計決策**：
- 用 `rd2`（唯讀 MySQL 帳號）確保物理上無法寫入
- `try/finally` 確保連線關閉
- 每個 tool 的 handler 是獨立函式，易於測試
- 密碼從環境變數讀取，不 hardcode

---

## 任務 3：CLAUDE.md 章節設計

```markdown
## 可用 MCP 工具：PM2.5 數據查詢

### `get_room_pm25` — 單一場域查詢

**何時使用**：
- 調查特定場域某天的 PM2.5 趨勢
- 確認特定感測器是否有故障（pm25=998）
- 生成場域日報告

**範例呼叫**：
```
get_room_pm25(room_id=142, date="2026-06-17", aggregation="hourly")
```

**使用注意事項**：
- pm25=998 是感測器故障信號，**不是真實污染值**，分析時必須排除
- 計算平均值時，應使用 `summary.avg_pm25`（已排除 998），不要自己算
- `aggregation="hourly"` 才會回傳 24 筆，`daily` 只回傳 1 筆日均值

---

### `get_anomaly_rooms` — 全場域異常掃描

**何時使用**：
- 每日例行檢查（有哪些場域今天有問題？）
- 重度污染告警（PM2.5 > 150 的場域清單）
- 感測器維修排程（fault 類型的異常清單）

**範例呼叫**：
```
get_anomaly_rooms(date="2026-06-17", anomaly_type="fault")
```

**使用注意事項**：
- 兩種異常類型含義不同：
  - `fault`（998）= 設備問題，需聯繫維修
  - `pollution`（>150）= 空氣品質問題，需通報場域管理員
- 這個工具會掃描全部 41 個場域，不能指定單一場域（那用 `get_room_pm25`）

---

### 絕對禁止

- **不能寫入資料**：這些工具連接的是唯讀 MySQL 帳號（rd2），嘗試任何寫入都會 403
- **不能修改感測器設定**：如需維修，請透過 AIHCR 管理後台，不是 MCP
```

---

## 學習洞察

**自訂 MCP Server 的核心設計思想**：MCP 不是把 API 包裝一層，而是把「Claude 需要做什麼決策」翻譯成「Claude 能直接呼叫什麼工具」。好的 MCP tool 設計應該讓 Claude 呼叫一次就得到完整決策所需的資訊（包含 summary 欄位、fault_count 等），而不是讓 Claude 拿到原始資料再自己計算 — 那樣容易在 998 值的處理上出錯。
