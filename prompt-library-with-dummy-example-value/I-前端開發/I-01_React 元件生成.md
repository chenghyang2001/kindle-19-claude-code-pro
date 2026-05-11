# I-01　React 元件生成

> **類別**：I. 前端開發

---

```
建立 ArticleCard React 元件：
功能：一個技術部落格平台，使用者可以發布 Markdown 文章、留言、收藏文章，管理員可管理所有內容
Props：article: Article; onBookmark: (id: string) => void; showAuthor?: boolean（預設 true）
狀態：isBookmarked: boolean; isLoading: boolean（用於 optimistic update）
要求：
- TypeScript（含完整的 prop types）
- Tailwind CSS 樣式（含響應式）
- 語意化 HTML + ARIA 標籤
- 錯誤狀態與載入狀態
- 匯出型別供外部使用
```
