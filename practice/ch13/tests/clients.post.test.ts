/**
 * POST /api/clients 整合測試：直接呼叫 Route Handler，
 * 走真的 Zod 驗證 + 真的 SQLite（記憶體）+ 真的 JWT 驗證。
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SignJWT } from "jose";
import { POST, GET } from "@/app/api/clients/route";
import { getDb } from "@/db/client";
import { clients, projects } from "@/db/schema";
import { signToken } from "@/lib/auth";

const URL_BASE = "http://localhost/api/clients";

function postRequest(
  body: unknown,
  token?: string,
  contentType = "application/json",
) {
  const headers: Record<string, string> = { "content-type": contentType };
  if (token) headers.authorization = `Bearer ${token}`;
  return new Request(URL_BASE, {
    method: "POST",
    headers,
    body: typeof body === "string" ? body : JSON.stringify(body),
  });
}

const validBody = {
  name: "  王小明  ",
  company: "小明設計工作室",
  email: "Ming@Example.com",
  phone: "+886 912-345-678",
};

let token: string;

beforeEach(async () => {
  const db = getDb();
  db.delete(projects).run();
  db.delete(clients).run();
  token = await signToken("user-a");
});

describe("POST /api/clients — 認證 (401)", () => {
  it("沒有 Authorization header → 401", async () => {
    const res = await POST(postRequest(validBody));
    expect(res.status).toBe(401);
    expect((await res.json()).error.code).toBe("UNAUTHORIZED");
  });

  it("token 是亂碼 → 401", async () => {
    const res = await POST(postRequest(validBody, "not-a-jwt"));
    expect(res.status).toBe(401);
  });

  it("用錯誤密鑰簽的 token → 401", async () => {
    const forged = await new SignJWT({})
      .setProtectedHeader({ alg: "HS256" })
      .setSubject("attacker")
      .setIssuer("freelancer-dashboard")
      .setExpirationTime("1h")
      .sign(new TextEncoder().encode("another-secret-another-secret-123456"));
    const res = await POST(postRequest(validBody, forged));
    expect(res.status).toBe(401);
  });

  it("過期的 token → 401", async () => {
    const expired = await signToken("user-a", "-1s");
    const res = await POST(postRequest(validBody, expired));
    expect(res.status).toBe(401);
  });

  it("401 時不會寫入資料庫", async () => {
    await POST(postRequest(validBody));
    expect(getDb().select().from(clients).all()).toHaveLength(0);
  });
});

describe("POST /api/clients — 驗證 (400 / 415)", () => {
  it("缺少必填欄位 name → 400 並指出欄位", async () => {
    const res = await POST(postRequest({ company: "無名公司" }, token));
    expect(res.status).toBe(400);
    const json = await res.json();
    expect(json.error.code).toBe("VALIDATION_ERROR");
    expect(json.error.details.name).toBeDefined();
  });

  it("name 只有空白 → 400", async () => {
    const res = await POST(postRequest({ name: "   " }, token));
    expect(res.status).toBe(400);
  });

  it("email 格式錯 → 400", async () => {
    const res = await POST(
      postRequest({ name: "A", email: "not-email" }, token),
    );
    expect(res.status).toBe(400);
    expect((await res.json()).error.details.email).toBeDefined();
  });

  it("未知欄位（例如偷塞 ownerId）→ 400", async () => {
    const res = await POST(
      postRequest({ name: "A", ownerId: "user-b" }, token),
    );
    expect(res.status).toBe(400);
  });

  it("body 不是合法 JSON → 400 INVALID_JSON", async () => {
    const res = await POST(postRequest("{name:", token));
    expect(res.status).toBe(400);
    expect((await res.json()).error.code).toBe("INVALID_JSON");
  });

  it("Content-Type 不是 JSON → 415", async () => {
    const res = await POST(
      postRequest("name=A", token, "application/x-www-form-urlencoded"),
    );
    expect(res.status).toBe(415);
  });
});

describe("POST /api/clients — 成功 (201) 與衝突 (409)", () => {
  it("成功建立 → 201 + 回傳資料 + Location", async () => {
    const res = await POST(postRequest(validBody, token));
    expect(res.status).toBe(201);
    const { data } = await res.json();
    expect(data).toMatchObject({
      name: "王小明",
      company: "小明設計工作室",
      email: "ming@example.com",
      phone: "+886 912-345-678",
      notes: null,
      version: 1,
    });
    expect(data.id).toMatch(/^[0-9a-f-]{36}$/);
    expect(data.ownerId).toBeUndefined();
    expect(res.headers.get("location")).toBe(`/api/clients/${data.id}`);

    const rows = getDb().select().from(clients).all();
    expect(rows).toHaveLength(1);
    expect(rows[0].ownerId).toBe("user-a");
  });

  it("只給 name 也能建立，選填欄位為 null", async () => {
    const res = await POST(postRequest({ name: "B", company: "" }, token));
    expect(res.status).toBe(201);
    expect((await res.json()).data.company).toBeNull();
  });

  it("同一使用者重複 email → 409", async () => {
    await POST(postRequest(validBody, token));
    const res = await POST(
      postRequest({ ...validBody, name: "另一人" }, token),
    );
    expect(res.status).toBe(409);
  });

  it("不同使用者可用同一 email，且列表互相看不到", async () => {
    const tokenB = await signToken("user-b");
    expect((await POST(postRequest(validBody, token))).status).toBe(201);
    expect((await POST(postRequest(validBody, tokenB))).status).toBe(201);

    const listReq = new Request(URL_BASE, {
      headers: { authorization: `Bearer ${tokenB}` },
    });
    const { data } = await (await GET(listReq)).json();
    expect(data).toHaveLength(1);
  });
});

describe("POST /api/clients — 伺服器錯誤 (500)", () => {
  it("資料庫壞掉 → 500，且不洩漏內部訊息", async () => {
    const db = getDb();
    const spy = vi.spyOn(db, "insert").mockImplementation(() => {
      throw new Error("SQLITE_IOERR: disk I/O error at /secret/path");
    });
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    const res = await POST(postRequest(validBody, token));
    expect(res.status).toBe(500);
    const text = await res.text();
    expect(text).not.toContain("SQLITE");
    expect(text).not.toContain("/secret/path");
    spy.mockRestore();
    errSpy.mockRestore();
  });
});
