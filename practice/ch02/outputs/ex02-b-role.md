<!-- prompt: ex02/b-role | ok | 87.2s -->

# Code Review：`user.ts` 型別安全審查

這段程式碼在 `tsc --strict` 下能過，原因是 `any` 和三種斷言（`as`、`!`、widening `as string`）把所有 runtime 錯誤藏起來了，編譯器看到的都是被斷言改寫過的型別。

## 問題清單

| 嚴重度 | 位置 | 問題 | 會造成的 runtime 後果 |
| --- | --- | --- | --- |
| 🔴 | `isAdmin`：`(user.role as string) == "Admin"` | `role` 的型別是 `"admin" \| "member"`，寫 `user.role == "Admin"` 時 tsc 會報 *"This comparison appears to be unintentional"*。`as string` 把型別放寬，剛好讓這個錯誤消失。另外大小寫寫錯了。 | 永遠回傳 `false`，所有 admin 都不會被當成 admin，權限判斷失效。這是標準的「斷言藏住邏輯 bug」。 |
| 🔴 | `fetchUser`：沒檢查 `res.ok` | 404 或 500 的錯誤 body（例如 `{ "error": "not found" }`）會被當成 `User` 回傳。 | 呼叫端拿到 `user.name === undefined`，錯誤要到很後面才爆。這個錯誤物件還會被**永久寫進快取**，之後同一個 id 一直回傳錯誤資料。 |
| 🔴 | `fetchUser`：`data as User` | `res.json()` 回傳 `any`，`as User` 什麼都沒驗證，只是告訴編譯器「相信我」。 | API 改版、欄位改名，或 `role` 變成 `"owner"`，都會一路流進系統。後面所有拿 `User` 型別做 narrowing 的程式碼都可能判斷錯。 |
| 🔴 | `parseUsers`：`return JSON.parse(raw)` | `JSON.parse` 回傳 `any`，被**隱式**轉成 `User[]`，連 `as` 都沒寫，最難在 review 時看到。 | 傳入 `"{}"`、`"null"`、`"[1,2]"` 都會被當成 `User[]`，之後 `.map` 或 `.name` 才爆。不合法的 JSON 直接丟出沒包裝的 `SyntaxError`。 |
| 🔴 | `emailDomain`：`user.email!` | `email?` 是選填，`!` 把 `undefined` 的可能性抹掉了。 | 沒有 email 的使用者會觸發 `TypeError: Cannot read properties of undefined (reading 'split')`。 |
| 🔴 | `emailDomain`：`split("@")[1]` | 沒開 `noUncheckedIndexedAccess` 時，索引存取的結果被當成 `string`，實際上可能是 `undefined`。 | email 是 `"foo"`（沒有 `@`）時回傳 `undefined`，但宣告的型別是 `string`。`"a@b@c.com"` 會回傳 `"b"`，結果錯誤。 |
| 🔴 | `cache: any` + `cache[id]` | 拿一般物件當快取，key 會繼承原型鏈上的屬性。 | `fetchUser("constructor")` 會命中 `Object.prototype.constructor`，**直接把一個函式當 `User` 回傳**。`"__proto__"`、`"toString"` 也一樣。 |
| 🔴 | `id: any` | 沒有限制，也沒驗證，就直接放進 URL。 | `1` 和 `"1"` 共用快取 key。傳物件會變成 `/api/users/[object Object]`。`"../admin"` 會造成路徑穿越，打到別的 API。 |
| 🟡 | `fetchUser`：沒有 `try/catch` | 網路錯誤和 `res.json()` 的解析錯誤都是原始例外，沒有上下文。 | 呼叫端分不出是斷線、逾時、還是格式錯誤，log 裡也沒有 id。 |
| 🟡 | `fetchUser`：沒有逾時 | `fetch` 預設沒有 timeout。 | 後端卡住時 Promise 永遠不會 resolve。 |
| 🟡 | `fetchUser`：沒有 in-flight 去重 | 同一個 id 同時被呼叫 N 次，會發 N 個請求。 | 浪費請求。最後寫入快取的不一定是最新的回應（race）。 |
| 🟡 | 快取回傳的是同一個物件參考 | 呼叫端修改回傳值，就會改到快取。 | 某處寫了 `user.role = "admin"`，所有之後讀快取的地方都被污染。 |
| 🟡 | `==` | 寬鬆比較。 | 這裡剛好沒有型別轉換問題，但會鼓勵錯誤的習慣，應該一律用 `===`。 |

## 修正後完整程式碼

沒有引入第三方套件，型別驗證用手寫的 type guard。`Error` 的 `{ cause }` 參數需要 `lib` 包含 `ES2022`。

```typescript
// 使用者資料存取：所有外部資料一律以 unknown 進入，經 type guard 驗證後才成為 User
export interface User {
  id: number;
  name: string;
  email?: string;
  role: "admin" | "member";
}

// 用 satisfies 綁定 User["role"]：之後聯集新增角色時，這裡漏改會編譯失敗
const ROLES = ["admin", "member"] as const satisfies readonly User["role"][];

const FETCH_TIMEOUT_MS = 10_000;

/** 使用者資料取得或解析失敗；status 只有 HTTP 錯誤時才有值 */
export class UserDataError extends Error {
  constructor(message: string, readonly status?: number, options?: { cause?: unknown }) {
    super(message, options);
    this.name = "UserDataError";
  }
}

// ---------- Type guards ----------

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isRole(value: unknown): value is User["role"] {
  return typeof value === "string" && (ROLES as readonly string[]).includes(value);
}

export function isUser(value: unknown): value is User {
  if (!isRecord(value)) return false;
  const email = value["email"];
  return (
    Number.isSafeInteger(value["id"]) &&
    typeof value["name"] === "string" &&
    (email === undefined || typeof email === "string") &&
    isRole(value["role"])
  );
}

/** 只挑已知欄位重建物件（丟掉後端多給的欄位），並凍結以防呼叫端改到快取 */
function toFrozenUser(source: User): Readonly<User> {
  const user: User = { id: source.id, name: source.name, role: source.role };
  if (source.email !== undefined) user.email = source.email;
  return Object.freeze(user);
}

// ---------- fetchUser ----------

// 用 Map 而不是一般物件：不會碰到原型鏈上的 "constructor" / "__proto__" 等 key
const cache = new Map<number, Readonly<User>>();
const inFlight = new Map<number, Promise<Readonly<User>>>();

export function fetchUser(id: number): Promise<Readonly<User>> {
  // number 型別擋不住 NaN、負數、小數，執行期仍要再檢查
  if (!Number.isSafeInteger(id) || id <= 0) {
    return Promise.reject(new RangeError(`無效的使用者 id：${String(id)}`));
  }

  const cached = cache.get(id);
  if (cached !== undefined) return Promise.resolve(cached);

  const pending = inFlight.get(id);
  if (pending !== undefined) return pending;

  const request = loadUser(id).finally(() => inFlight.delete(id));
  inFlight.set(id, request);
  return request;
}

async function loadUser(id: number): Promise<Readonly<User>> {
  let res: Response;
  try {
    res = await fetch(`/api/users/${encodeURIComponent(id)}`, {
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
  } catch (err) {
    throw new UserDataError(`網路錯誤或逾時：無法取得使用者 ${id}`, undefined, { cause: err });
  }

  if (!res.ok) {
    throw new UserDataError(`HTTP ${res.status}：無法取得使用者 ${id}`, res.status);
  }

  let body: unknown;
  try {
    body = await res.json();
  } catch (err) {
    throw new UserDataError(`回應不是合法 JSON（使用者 ${id}）`, res.status, { cause: err });
  }

  if (!isUser(body)) {
    throw new UserDataError(`回應格式不符合 User 結構（使用者 ${id}）`, res.status);
  }
  if (body.id !== id) {
    throw new UserDataError(`回應 id 不一致：要求 ${id}，收到 ${body.id}`, res.status);
  }

  // 只快取驗證通過的資料，錯誤回應永遠不會進快取
  const user = toFrozenUser(body);
  cache.set(id, user);
  return user;
}

// ---------- 其他函式 ----------

/** 沒有 email 或格式不合法時回傳 undefined，由型別強制呼叫端處理 */
export function emailDomain(user: User): string | undefined {
  if (user.email === undefined) return undefined;
  const atIndex = user.email.lastIndexOf("@");
  if (atIndex <= 0 || atIndex === user.email.length - 1) return undefined;
  return user.email.slice(atIndex + 1);
}

export function isAdmin(user: User): boolean {
  // 不加任何斷言：如果字面值打錯，tsc 會直接報錯
  return user.role === "admin";
}

export function parseUsers(raw: string): User[] {
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    throw new UserDataError("parseUsers：輸入不是合法 JSON", undefined, { cause: err });
  }

  if (!Array.isArray(parsed)) {
    throw new UserDataError("parseUsers：JSON 頂層必須是陣列");
  }

  return parsed.map((item: unknown, index): User => {
    if (!isUser(item)) {
      throw new UserDataError(`parseUsers：第 ${index} 筆不符合 User 結構`);
    }
    return { ...toFrozenUser(item) };
  });
}
```

### 建議加進 tsconfig 和 lint 的設定

加上這些之後，上面多數問題會從 runtime 錯誤變成編譯錯誤：

- `tsconfig.json`：開啟 `noUncheckedIndexedAccess`，讓 `split("@")[1]` 的型別變成 `string | undefined`。開啟 `exactOptionalPropertyTypes`。
- ESLint：
  - `@typescript-eslint/no-explicit-any`
  - `@typescript-eslint/no-non-null-assertion`
  - `@typescript-eslint/consistent-type-assertions`（設成 `assertionStyle: "never"`）
  - `@typescript-eslint/no-unsafe-return`：可以抓到 `parseUsers` 的隱式 `any` 回傳
  - `eqeqeq`

**最大風險**：`fetchUser` 沒檢查 `res.ok`，又用 `as User` 直接信任回應，所以 HTTP 錯誤的 body 會被當成合法的 `User` **永久寫進快取**。再加上 `isAdmin` 因為 `as string` 永遠回傳 `false`，這兩個「編譯器看不到」的錯誤會一起讓身分與權限判斷變得不可信。
