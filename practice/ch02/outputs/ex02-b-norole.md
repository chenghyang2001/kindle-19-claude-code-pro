<!-- prompt: ex02/b-norole | ok | 69.8s -->

這段程式碼共有 **9 個問題**。最嚴重的是 `isAdmin` 一定回傳 `false`，以及 `fetchUser` 會把錯誤回應當成 `User` 存進快取。整體來看，`any`、`as` 和 `!` 讓 TypeScript 無法替你檢查型別，原本能在編譯期抓到的錯誤，都要等執行時才會出現。

## 🔴 必修（會產生錯誤結果或直接崩潰）

### 1. `isAdmin` 永遠回傳 `false`
```ts
return (user.role as string) == "Admin";
```
- `role` 的型別只有 `"admin" | "member"`，所以 `"Admin"`（大寫 A）永遠不會相等。
- 原本 TS 會報錯（*This comparison appears to be unintentional*）。`as string` 把型別放寬了，所以這個錯誤沒有被發現。
- 另外用的是 `==`，應改為 `===`。

### 2. `emailDomain` 的 `!` 會讓程式崩潰
```ts
return user.email!.split("@")[1];
```
- `email` 是選填欄位（`email?`）。用 `!` 只是告訴 TS「不會是 undefined」，執行時並沒有真的檢查，遇到沒有 email 的使用者就會丟出 `TypeError: Cannot read properties of undefined`。
- 如果 email 裡沒有 `@`，`[1]` 會是 `undefined`，但函式宣告回傳的是 `string`，型別和實際值不符。

### 3. `fetchUser` 沒有檢查 `res.ok`
- 遇到 404 或 500 時，錯誤內容（例如 `{ error: "Not found" }`）會被當成 `User` 回傳。
- 這筆錯誤資料還會被**永久存進快取**，之後再呼叫也不會重新抓取。

### 4. `data as User` 只是型別斷言，沒有驗證
`res.json()` 回傳的是 `any`。加上 `as User` 只是讓編譯器不再檢查，執行時完全不會驗證資料內容。後端格式一改，錯誤會在很遠的地方才爆出來，難以追查。

### 5. `parseUsers` 有一樣的問題
`JSON.parse` 回傳 `any`，會被隱性轉成 `User[]`，同樣沒有驗證。格式錯誤的 JSON 會直接丟出例外，而且沒有被處理。

## 🟡 應修

### 6. `cache: any` 加上 `id: any` 有原型鏈陷阱
```ts
fetchUser("constructor")  // cache["constructor"] 是 Object 函式，條件為 truthy，直接被回傳
```
物件會從原型繼承 `constructor`、`toString` 等屬性，所以用一般物件當字典不安全，應改用 `Map<number, User>`。

### 7. `id: any` 可能造成路徑注入
`id` 可以傳入 `"../admin"` 這類字串，直接被拼進 URL。應該把型別限定為 `number`，或至少用 `encodeURIComponent` 處理。

### 8. 同時請求會重複抓取
快取只在 `await` 完成後才寫入，所以同時對同一個 id 呼叫 N 次，就會發出 N 個請求。改成快取 `Promise` 可以避免。

### 9. 快取沒有上限，也不會過期
- 快取會一直變大。
- 如果在 SSR 或伺服器端執行，這個模組層級的快取會被所有使用者共用，可能造成資料外洩。

## ✅ 修正版

```ts
interface User {
  id: number;
  name: string;
  email?: string;
  role: "admin" | "member";
}

// 執行時型別守衛：外部資料必須驗證，不能只靠 as 斷言
function isUser(value: unknown): value is User {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.id === "number" &&
    typeof v.name === "string" &&
    (v.email === undefined || typeof v.email === "string") &&
    (v.role === "admin" || v.role === "member")
  );
}

// 快取 Promise，避免同時請求同一 id 時重複發送
const userCache = new Map<number, Promise<User>>();

export function fetchUser(id: number): Promise<User> {
  if (!Number.isInteger(id) || id <= 0) {
    return Promise.reject(new RangeError(`無效的使用者 id：${id}`));
  }
  const cached = userCache.get(id);
  if (cached) return cached;

  const request = (async () => {
    const res = await fetch(`/api/users/${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error(`取得使用者失敗：HTTP ${res.status}`);
    const data: unknown = await res.json();
    if (!isUser(data)) throw new TypeError("API 回傳的資料不是有效的 User");
    return data;
  })();

  // 失敗時移除快取，避免把錯誤永久存起來
  request.catch(() => userCache.delete(id));
  userCache.set(id, request);
  return request;
}

export function emailDomain(user: User): string | undefined {
  const at = user.email?.lastIndexOf("@") ?? -1;
  return at >= 0 ? user.email!.slice(at + 1) || undefined : undefined;
}

export function isAdmin(user: User): boolean {
  return user.role === "admin";
}

export function parseUsers(raw: string): User[] {
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (e) {
    throw new SyntaxError(`使用者 JSON 格式錯誤：${(e as Error).message}`);
  }
  if (!Array.isArray(parsed) || !parsed.every(isUser)) {
    throw new TypeError("資料不是有效的 User 陣列");
  }
  return parsed;
}
```

> `emailDomain` 裡留著一個 `!`，那是因為 `at >= 0` 已經保證 `email` 存在，TS 無法自己推斷出來。如果想完全不用 `!`，可以先寫 `const { email } = user;`，再對 `email` 本身做檢查。

## 🛡️ 防止再犯：把規則交給工具檢查

**tsconfig.json**
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true
  }
}
```
開啟 `noUncheckedIndexedAccess` 後，`split("@")[1]` 會被推斷為 `string | undefined`，第 2 點的問題在編譯時就會被發現。

**ESLint（typescript-eslint）**
- `@typescript-eslint/no-explicit-any`：禁止使用 `any`
- `@typescript-eslint/no-non-null-assertion`：禁止使用 `!`
- `@typescript-eslint/no-unsafe-assignment` 和 `no-unsafe-return`：抓出 `any` 外流到有型別的變數或回傳值
- `eqeqeq`：強制使用 `===`

如果欄位較多，建議改用 **Zod** 定義 schema，用 `UserSchema.parse(data)` 驗證，再用 `z.infer` 推導出型別。這樣型別和驗證邏輯寫在同一處，不會各改各的。
