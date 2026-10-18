# 練習 02 解答 — 客戶管理 CRUD API

> 技術：Next.js 15 App Router Route Handlers + Drizzle ORM + **better-sqlite3（本機 SQLite）** + Zod 4 + jose（JWT）+ vitest
> 題目只要求實作 `POST /api/clients`；五個端點都已實作，POST 測得最完整。

| 檔案 | 內容 |
| --- | --- |
| `src/app/api/clients/route.ts` | GET 列表、**POST 建立** |
| `src/app/api/clients/[id]/route.ts` | GET / PUT / DELETE 單一客戶 |
| `src/lib/auth.ts` | Bearer JWT 驗證（認證中介層） |
| `src/lib/validation.ts` | Zod schema |
| `src/lib/http.ts` | 統一錯誤格式、`withErrorHandling`、JSON 解析 |
| `src/lib/clients-repo.ts` | Drizzle 查詢（都帶 `owner_id`） |
| `tests/clients.post.test.ts` | POST 整合測試（16 個） |
| `tests/clients.id.test.ts` | GET/PUT/DELETE 測試（8 個） |

---

## 任務 1：API 端點設計

所有端點都要 `Authorization: Bearer <JWT>`，所有查詢都限定 `owner_id = JWT.sub`，看不到別人的客戶。

### 統一回應格式

```jsonc
// 成功
{ "data": { ...客戶 } }
// 失敗
{ "error": { "code": "VALIDATION_ERROR", "message": "欄位驗證失敗", "details": { "name": ["..."] } } }
```

客戶物件（`ownerId` 不對外輸出）：

```json
{
  "id": "83afdead-cf31-4baf-a120-4db6767d1826",
  "name": "Wang", "company": null, "email": "w@example.com",
  "phone": null, "notes": null, "version": 1,
  "createdAt": "2026-10-18T00:51:26.028Z", "updatedAt": "2026-10-18T00:51:26.028Z"
}
```

### 端點總表

| Method | 路徑 | Request | 成功 | 錯誤 |
| --- | --- | --- | --- | --- |
| GET | `/api/clients?limit=20&offset=0` | query：limit 1~100、offset ≥ 0 | 200 `{ data: [], limit, offset }` | 400 分頁參數錯、401、500 |
| POST | `/api/clients` | `createClientSchema` | **201** `{ data }` + `Location` header | 400、401、409 email 重複、415、500 |
| GET | `/api/clients/[id]` | — | 200 `{ data }` | 401、404（不存在／不是 uuid／別人的）、500 |
| PUT | `/api/clients/[id]` | `updateClientSchema`（部分欄位 + **必填 version**） | 200 `{ data }`（version + 1） | 400、401、404、409 版本衝突／email 重複、415、500 |
| DELETE | `/api/clients/[id]` | — | **204** 無 body | 401、404、409 仍有專案／發票、500 |

狀態碼的取捨：

- **別人的客戶回 404 不回 403**：回 403 等於告訴攻擊者「這個 ID 存在」。
- **415**：Content-Type 不是 JSON 時，和「JSON 壞掉（400）」分開。
- **500 不帶細節**：錯誤細節只寫進 server log（`console.error`），回應只有 `"伺服器內部錯誤"`。

### Zod 驗證 schema（`src/lib/validation.ts`）

```ts
// 空字串視為沒填，存 null，避免 DB 裡混著 "" 和 NULL
const optionalText = (max: number) =>
  z.string().trim().max(max).transform((v) => (v === "" ? null : v)).nullish();

export const createClientSchema = z.strictObject({
  name: z.string().trim().min(1, "name 為必填").max(100),
  company: optionalText(100),
  email: z.string().trim().toLowerCase()
    .pipe(z.email("email 格式錯誤").max(254)).nullish(),
  phone: z.string().trim()
    .regex(/^[0-9+\-() ]{6,20}$/, "phone 只能包含數字、空白、+-()，長度 6~20").nullish(),
  notes: optionalText(2000),
});

export const updateClientSchema = createClientSchema.partial().extend({
  version: z.number().int().positive(), // 樂觀鎖
});

export const idSchema = z.uuid();
```

`z.strictObject` 會擋掉未知欄位，例如 client 想偷塞 `ownerId` 把客戶掛到別人名下，會直接回 400。

---

## 任務 2：POST /api/clients 實作

### 1. 認證中介層（`src/lib/auth.ts` + `src/lib/http.ts`）

```ts
export async function authenticate(request: Request): Promise<AuthUser | null> {
  const header = request.headers.get("authorization");
  const match = header?.match(/^Bearer\s+(\S+)$/i);
  if (!match) return null;
  // 金鑰設定錯誤是伺服器問題，要往外拋成 500，不能被當成 401 吞掉
  const key = getSecretKey();
  try {
    const { payload } = await jwtVerify(match[1], key, {
      issuer: ISSUER,
      algorithms: ["HS256"],   // 鎖死演算法，防 alg 混淆攻擊
    });
    if (typeof payload.sub !== "string" || payload.sub.length === 0) return null;
    return { id: payload.sub };
  } catch {
    return null; // 簽章錯、過期、格式錯 → 401
  }
}

export async function requireUser(request: Request): Promise<AuthUser> {
  const user = await authenticate(request);
  if (!user) throw new HttpError(401, "UNAUTHORIZED", "缺少或無效的認證 token");
  return user;
}
```

### 2~5. Route Handler（`src/app/api/clients/route.ts`）

```ts
export const runtime = "nodejs";        // better-sqlite3 需要 Node.js runtime
export const dynamic = "force-dynamic";

export const POST = withErrorHandling("POST /api/clients", async (request: Request) => {
  // 1. 認證 → 2. 驗證 → 3. 寫入 → 4. 201
  const user = await requireUser(request);                          // 401
  const input = await parseJsonBody(request, createClientSchema);   // 415 / 400
  try {
    const created = insertClient(getDb(), user.id, input);          // Drizzle insert ... returning
    return NextResponse.json(
      { data: toDto(created) },
      { status: 201, headers: { Location: `/api/clients/${created.id}` } },
    );
  } catch (err) {
    if (isUniqueViolation(err)) throw new HttpError(409, "CONFLICT", "已有相同 email 的客戶");
    throw err;                                                       // 5. 其餘 → 500
  }
});
```

### 錯誤處理骨架（`src/lib/http.ts`）

```ts
export function withErrorHandling<A extends unknown[]>(
  label: string,
  handler: (...args: A) => Promise<Response>,
) {
  return async (...args: A): Promise<Response> => {
    try {
      return await handler(...args);
    } catch (err) {
      if (err instanceof HttpError) {
        return errorResponse(err.status, err.code, err.message, err.details);
      }
      console.error(`${label} error:`, err);              // 細節只進 log
      return errorResponse(500, "INTERNAL_ERROR", "伺服器內部錯誤");
    }
  };
}

export async function parseJsonBody<T extends z.ZodType>(request: Request, schema: T) {
  const contentType = request.headers.get("content-type") ?? "";
  if (!contentType.toLowerCase().startsWith("application/json")) {
    throw new HttpError(415, "UNSUPPORTED_MEDIA_TYPE", "Content-Type 必須是 application/json");
  }
  let raw: unknown;
  try { raw = await request.json(); }
  catch { throw new HttpError(400, "INVALID_JSON", "Request body 不是合法的 JSON"); }
  const parsed = schema.safeParse(raw);
  if (!parsed.success) {
    throw new HttpError(400, "VALIDATION_ERROR", "欄位驗證失敗",
      z.flattenError(parsed.error).fieldErrors);
  }
  return parsed.data;
}
```

### Drizzle 寫入（`src/lib/clients-repo.ts`）

```ts
export function insertClient(db: Db, ownerId: string, input: CreateClientInput): Client {
  return db.insert(clients).values({
    ownerId,                      // 一律從 JWT 取，不信任 body
    name: input.name,
    company: input.company ?? null,
    email: input.email ?? null,
    phone: input.phone ?? null,
    notes: input.notes ?? null,
  }).returning().get();
}
```

---

## 整合測試

測試直接呼叫 Route Handler 的 `POST(request)`，跑的是**真的** JWT 驗證、Zod、Drizzle，以及 migrate 過的記憶體 SQLite（`DATABASE_FILE=:memory:`），沒有 mock DB。`AUTH_SECRET` 每次執行隨機產生（`tests/setup.ts`）。

### 題目要求的三個測試

```ts
it("token 是亂碼 → 401", async () => {
  const res = await POST(postRequest(validBody, "not-a-jwt"));
  expect(res.status).toBe(401);
});

it("缺少必填欄位 name → 400 並指出欄位", async () => {
  const res = await POST(postRequest({ company: "無名公司" }, token));
  expect(res.status).toBe(400);
  const json = await res.json();
  expect(json.error.code).toBe("VALIDATION_ERROR");
  expect(json.error.details.name).toBeDefined();
});

it("成功建立 → 201 + 回傳資料 + Location", async () => {
  const res = await POST(postRequest(validBody, token));
  expect(res.status).toBe(201);
  const { data } = await res.json();
  expect(data).toMatchObject({
    name: "王小明",                 // trim 過
    email: "ming@example.com",      // 轉小寫
    version: 1,
  });
  expect(data.ownerId).toBeUndefined();  // 不外洩
  expect(res.headers.get("location")).toBe(`/api/clients/${data.id}`);
  const rows = getDb().select().from(clients).all();
  expect(rows[0].ownerId).toBe("user-a"); // 真的寫進 DB
});
```

### 完整測試清單（24 個）

| 分類 | 測試 |
| --- | --- |
| POST 401 | 沒 header、亂碼 token、錯密鑰簽的 token、過期 token、401 時不寫入 DB |
| POST 400/415 | 缺 name、name 只有空白、email 格式錯、偷塞 `ownerId`、JSON 壞掉、Content-Type 錯（415） |
| POST 201/409 | 成功建立、只給 name、同使用者 email 重複（409）、不同使用者資料互相隔離 |
| POST 500 | DB 拋錯 → 500 且回應不含 `SQLITE`、檔案路徑 |
| GET [id] | 200、非 uuid → 404、別人的客戶 → 404 |
| PUT [id] | 正確 version → 200 且 version+1、**兩人同時編輯第二個 → 409**、缺 version → 400 |
| DELETE [id] | 204 後再查 404、還有專案 → 409 |

### 執行結果

```
$ npx vitest run
 Test Files  2 passed (2)
      Tests  24 passed (24)
```

真實 HTTP 冒煙測試（`next build` → `next start -p 3199` → curl，測完已關閉伺服器）：

```
--- 無 token     → {"error":{"code":"UNAUTHORIZED",...}} [401]
--- 缺 name      → {"error":{"code":"VALIDATION_ERROR",...,"details":{"name":[...]}}} [400]
--- 成功         → HTTP/1.1 201 Created / location: /api/clients/83afdead-...
--- 重複 email   → {"error":{"code":"CONFLICT",...}} [409]
--- 列表         → {"data":[{...}],"limit":20,"offset":0} [200]
```

---

## 延伸思考：兩個使用者同時編輯同一客戶

### 會發生什麼：Lost Update（更新遺失）

```
時間  A                               B
t1    GET → {name:"王", phone:"111"}
t2                                    GET → {name:"王", phone:"111"}
t3    PUT {name:"王小明", phone:"111"}
t4                                    PUT {name:"王", phone:"222"}   ← A 改的名字被蓋回去
```

兩次 PUT 都回 200，沒有人知道 A 的修改不見了。

### 防範：樂觀鎖（已實作並測試）

1. `clients` 表加 `version` 欄位，GET 時回傳給前端。
2. PUT body **必須**帶 `version`，SQL 用條件更新，比對和遞增在同一條 UPDATE 完成（原子操作）：

   ```sql
   UPDATE clients SET ..., version = version + 1
   WHERE id = ? AND owner_id = ? AND version = ?   -- 帶上讀到的版本
   ```

3. 影響 0 筆時再查一次：不存在 → 404；存在但版本不同 → **409 VERSION_CONFLICT**，附 `currentVersion`，前端提示「資料已被其他人修改，請重新載入」。

```ts
export function updateClient(db, ownerId, id, input) {
  const { version, ...fields } = input;
  return db.update(clients)
    .set({ ...fields, version: version + 1, updatedAt: new Date() })
    .where(and(eq(clients.id, id), eq(clients.ownerId, ownerId), eq(clients.version, version)))
    .returning().get();
}
```

測試 `兩人同時編輯：第二個用舊 version → 409` 驗證了上面的情境。

### 其他做法比較

| 做法 | 優點 | 缺點 | 適用 |
| --- | --- | --- | --- |
| **樂觀鎖 version（採用）** | 不鎖資料表、無狀態、適合 serverless | 衝突時使用者要重做 | 衝突少的表單編輯 |
| HTTP `ETag` + `If-Match` → 412 | 走 HTTP 標準，可配合快取 | 前端要處理 header | 公開 API |
| 悲觀鎖 `SELECT ... FOR UPDATE` | 保證不衝突 | 鎖要在同一 transaction 內，跨 HTTP 請求做不到；SQLite 沒有 | 同一請求內的讀改寫（如扣庫存） |
| 欄位級 PATCH 只送有改的欄位 | 改不同欄位就不會互蓋 | 改同一欄位仍會蓋掉 | 搭配樂觀鎖使用 |
| Last-write-wins | 最簡單 | 會遺失資料 | 不重要的資料 |
