# K-10　Log 聚合設置

> **類別**：K. DevOps & 部署

---

```
設置集中式 Log 聚合系統：
規模：每天約 500MB JSON 結構化 logs
工具：Loki + Grafana
要包含：
- Log 收集 Agent 設置
- Log 解析（structured JSON）
- 保留策略（熱儲存 7 天，冷儲存 90 天）
- 快速搜尋（按 TraceID / 用戶 ID）
- 異常 Log 告警
```

---

## L. 安全性（10 個）
