---
paths:
  - "demo/**/*.ts"
  - "demo/**/*.tsx"
  - "freelancer-dashboard/**/*.ts"
  - "freelancer-dashboard/**/*.tsx"
  - "freelancer-dashboard-演練/**/*.ts"
  - "freelancer-dashboard-演練/**/*.tsx"
---

# TypeScript / Next.js 規則（按需載入）

> 只在存取 .ts / .tsx 檔案時載入。

## 技術堆疊（本專案）

- Next.js 16 App Router（TypeScript strict）
- Tailwind CSS + shadcn/ui
- Neon Serverless PostgreSQL（`@neondatabase/serverless`）
- NextAuth v5（JWT）

## 禁止事項

- 禁止用 `any` 型別（用 `unknown` + 型別縮窄，或明確定義介面）
- 禁止 Client Component 直接查詢資料庫（一律透過 API Route）
- 禁止 `dangerouslySetInnerHTML`（XSS 風險）
- 禁止暴露 Prisma types 到 API 回應（建立獨立 DTO）

## API Route 標準結構

```typescript
// app/api/[resource]/route.ts
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  try {
    // 1. 認證檢查
    // 2. 參數驗證（Zod）
    // 3. 資料庫查詢（SELECT only for read-only DB）
    // 4. 回傳結果
    return NextResponse.json({ data }, { status: 200 });
  } catch (error) {
    console.error("錯誤：", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
```

## 元件規則

```tsx
// 語意化標籤（不全用 div）
// ARIA 標籤（aria-label, role）
// Tailwind 響應式（sm: md: lg:）

interface Props {
  // 明確定義，不用 any
}

export function Component({ prop }: Props) {
  return <main aria-label="...">...</main>;
}
```

## 環境變數

```typescript
// 存取前驗證
const dbUrl = process.env.DATABASE_URL;
if (!dbUrl) throw new Error("缺少 DATABASE_URL 環境變數");
```
