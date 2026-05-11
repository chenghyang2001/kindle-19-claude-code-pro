# G-09　資料庫 Transaction 設計

> **類別**：G. 資料庫

---

```
這個操作需要 transaction 確保資料一致性：
操作步驟：[列出所有步驟，如「扣款 + 建立訂單 + 發送通知」]
請實作：
- 完整的 transaction 包裝
- 每個步驟的錯誤處理與回滾
- 避免長 transaction（哪些步驟可以移到 transaction 外？）
- 鎖定策略（樂觀鎖 vs 悲觀鎖）
```
