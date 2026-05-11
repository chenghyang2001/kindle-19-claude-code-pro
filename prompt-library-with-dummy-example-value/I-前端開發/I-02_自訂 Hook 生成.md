# I-02　自訂 Hook 生成

> **類別**：I. 前端開發

---

```
建立 useArticleList 自訂 Hook：
功能：管理文章列表的分頁載入、關鍵字搜尋與標籤篩選，封裝 API 呼叫邏輯
參數：page: number; pageSize?: number（預設 20）; keyword?: string; tagId?: number
回傳值：{ articles, isLoading, hasMore, loadMore, reset, error }
要求：
- 完整的 TypeScript 型別
- 清理副作用（useEffect cleanup）
- 錯誤處理
- 撰寫對應的單元測試
```
