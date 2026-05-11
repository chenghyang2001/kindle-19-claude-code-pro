# Step 4 Claude 的回應

> D-05 讓 Claude 一次覆蓋所有 API 測試案例，包含錯誤路徑（這才是 bug 最常躲的地方）

---

```typescript
// __tests__/api/bookmarks.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { POST } from '@/app/api/bookmarks/route'
import { NextRequest } from 'next/server'

// ── Mock 外部依賴（不連真實 DB）──
vi.mock('@/lib/bookmarks', () => ({
  toggleBookmark: vi.fn(),
  isBookmarked:   vi.fn(),
}))

vi.mock('@/lib/articles', () => ({
  getArticleById: vi.fn(),
}))

vi.mock('@/lib/auth', () => ({
  withAuth: vi.fn(),
}))

import { toggleBookmark } from '@/lib/bookmarks'
import { getArticleById } from '@/lib/articles'
import { withAuth } from '@/lib/auth'

// ── 工具函式 ──
function makeRequest(body: object, userId?: number) {
  const req = new NextRequest('http://localhost/api/bookmarks', {
    method: 'POST',
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json' },
  })
  // 模擬 withAuth 注入 userId
  if (userId) {
    vi.mocked(withAuth).mockImplementation(async (req, handler) =>
      handler(req, { userId })
    )
  } else {
    vi.mocked(withAuth).mockImplementation(async () =>
      Response.json({ error: 'Unauthorized' }, { status: 401 })
    )
  }
  return req
}

// ────────────────────────────────────────────────
describe('POST /api/bookmarks', () => {

  beforeEach(() => { vi.clearAllMocks() })

  // ✅ 正常案例
  it('登入用戶收藏存在的文章，回傳 bookmarked: true', async () => {
    vi.mocked(getArticleById).mockResolvedValue({ id: 42, title: '測試文章' })
    vi.mocked(toggleBookmark).mockResolvedValue(true)

    const res = await POST(makeRequest({ articleId: 42 }, 1))
    const data = await res.json()

    expect(res.status).toBe(200)
    expect(data).toEqual({ bookmarked: true, articleId: 42 })
    expect(toggleBookmark).toHaveBeenCalledWith(1, 42)
  })

  // ✅ 冪等：重複收藏不報錯
  it('重複收藏同一篇文章，第二次仍回傳 bookmarked: true（冪等）', async () => {
    vi.mocked(getArticleById).mockResolvedValue({ id: 42, title: '測試文章' })
    vi.mocked(toggleBookmark).mockResolvedValue(true) // DB UNIQUE 保證冪等

    const req = makeRequest({ articleId: 42 }, 1)
    const res = await POST(req)
    const data = await res.json()

    expect(res.status).toBe(200)
    expect(data.bookmarked).toBe(true)
  })

  // ❌ 401 未登入
  it('未登入用戶呼叫，回傳 401 Unauthorized', async () => {
    const res = await POST(makeRequest({ articleId: 42 })) // 無 userId
    const data = await res.json()

    expect(res.status).toBe(401)
    expect(data).toEqual({ error: 'Unauthorized' })
    expect(toggleBookmark).not.toHaveBeenCalled()
  })

  // ❌ 404 文章不存在
  it('文章不存在，回傳 404 Article not found', async () => {
    vi.mocked(getArticleById).mockResolvedValue(null) // 查不到

    const res = await POST(makeRequest({ articleId: 9999 }, 1))
    const data = await res.json()

    expect(res.status).toBe(404)
    expect(data).toEqual({ error: 'Article not found' })
    expect(toggleBookmark).not.toHaveBeenCalled()
  })

  // ❌ 400 缺少 articleId
  it('請求沒有帶 articleId，回傳 400 驗證錯誤', async () => {
    const res = await POST(makeRequest({}, 1)) // 空 body

    expect(res.status).toBe(400)
    expect(await res.json()).toEqual({ error: 'articleId is required' })
  })

  // ❌ 500 DB 斷線
  it('資料庫斷線，回傳 500 Internal server error（不洩漏錯誤細節）', async () => {
    vi.mocked(getArticleById).mockResolvedValue({ id: 42, title: '測試文章' })
    vi.mocked(toggleBookmark).mockRejectedValue(new Error('ECONNREFUSED'))

    const res = await POST(makeRequest({ articleId: 42 }, 1))
    const data = await res.json()

    expect(res.status).toBe(500)
    expect(data).toEqual({ error: 'Internal server error' })
    // 確保不洩漏真實錯誤訊息給前端
    expect(data.error).not.toContain('ECONNREFUSED')
  })
})
```

---

**測試涵蓋率分析：**

| 案例 | 狀態碼 | 涵蓋路徑 |
|------|--------|---------|
| 正常收藏 | 200 | Happy path |
| 重複收藏 | 200 | 冪等設計 |
| 未登入 | 401 | Auth middleware |
| 文章不存在 | 404 | 資源驗證 |
| 缺少參數 | 400 | 輸入驗證 |
| DB 斷線 | 500 | 錯誤處理 + 不洩漏細節 |

---
> D-05 的價值：**測試和程式碼同步產生**，而且特別強調錯誤路徑（401/404/400/500）。
> 只測 happy path 的測試，等於沒測。
