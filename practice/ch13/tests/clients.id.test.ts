/** GET / PUT / DELETE /api/clients/[id] 的重點測試（404、樂觀鎖 409、刪除限制）。 */
import { beforeEach, describe, expect, it } from "vitest";
import { POST } from "@/app/api/clients/route";
import { DELETE, GET, PUT } from "@/app/api/clients/[id]/route";
import { getDb } from "@/db/client";
import { clients, projects } from "@/db/schema";
import { signToken } from "@/lib/auth";

let token: string;
const ctx = (id: string) => ({ params: Promise.resolve({ id }) });

function req(method: string, body?: unknown, auth = token) {
  return new Request("http://localhost/api/clients/x", {
    method,
    headers: {
      authorization: `Bearer ${auth}`,
      "content-type": "application/json",
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

async function createClient(name = "測試客戶") {
  const res = await POST(
    new Request("http://localhost/api/clients", {
      method: "POST",
      headers: {
        authorization: `Bearer ${token}`,
        "content-type": "application/json",
      },
      body: JSON.stringify({ name }),
    }),
  );
  return (await res.json()).data as { id: string; version: number };
}

beforeEach(async () => {
  const db = getDb();
  db.delete(projects).run();
  db.delete(clients).run();
  token = await signToken("user-a");
});

describe("GET /api/clients/[id]", () => {
  it("存在 → 200", async () => {
    const c = await createClient();
    const res = await GET(req("GET"), ctx(c.id));
    expect(res.status).toBe(200);
  });

  it("非 uuid → 404", async () => {
    expect((await GET(req("GET"), ctx("abc"))).status).toBe(404);
  });

  it("別人的客戶 → 404（不透露存在與否）", async () => {
    const c = await createClient();
    const other = await signToken("user-b");
    expect((await GET(req("GET", undefined, other), ctx(c.id))).status).toBe(
      404,
    );
  });
});

describe("PUT /api/clients/[id] — 樂觀鎖", () => {
  it("帶正確 version → 200，version +1", async () => {
    const c = await createClient();
    const res = await PUT(
      req("PUT", { name: "新名字", version: 1 }),
      ctx(c.id),
    );
    expect(res.status).toBe(200);
    const { data } = await res.json();
    expect(data).toMatchObject({ name: "新名字", version: 2 });
  });

  it("兩人同時編輯：第二個用舊 version → 409", async () => {
    const c = await createClient();
    const first = await PUT(
      req("PUT", { name: "A 改的", version: 1 }),
      ctx(c.id),
    );
    const second = await PUT(
      req("PUT", { name: "B 改的", version: 1 }),
      ctx(c.id),
    );
    expect(first.status).toBe(200);
    expect(second.status).toBe(409);
    const json = await second.json();
    expect(json.error.code).toBe("VERSION_CONFLICT");
    expect(json.error.details.currentVersion).toBe(2);
  });

  it("缺 version → 400", async () => {
    const c = await createClient();
    expect((await PUT(req("PUT", { name: "X" }), ctx(c.id))).status).toBe(400);
  });
});

describe("DELETE /api/clients/[id]", () => {
  it("刪除成功 → 204，再查 → 404", async () => {
    const c = await createClient();
    expect((await DELETE(req("DELETE"), ctx(c.id))).status).toBe(204);
    expect((await GET(req("GET"), ctx(c.id))).status).toBe(404);
  });

  it("還有專案 → 409", async () => {
    const c = await createClient();
    getDb()
      .insert(projects)
      .values({ clientId: c.id, name: "網站改版", hourlyRateCents: 150000 })
      .run();
    expect((await DELETE(req("DELETE"), ctx(c.id))).status).toBe(409);
  });
});
