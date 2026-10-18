/** GET / PUT / DELETE /api/clients/[id] */
import { NextResponse } from "next/server";
import { getDb } from "@/db/client";
import {
  deleteClient,
  findClient,
  toDto,
  updateClient,
} from "@/lib/clients-repo";
import {
  HttpError,
  isForeignKeyViolation,
  isUniqueViolation,
  parseJsonBody,
  requireUser,
  withErrorHandling,
} from "@/lib/http";
import { idSchema, updateClientSchema } from "@/lib/validation";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Ctx = { params: Promise<{ id: string }> };

async function resolveId(ctx: Ctx): Promise<string> {
  const { id } = await ctx.params;
  // 非 uuid 一律當作不存在，不透露 ID 格式規則
  if (!idSchema.safeParse(id).success) throw notFound();
  return id;
}

const notFound = () => new HttpError(404, "NOT_FOUND", "找不到此客戶");

export const GET = withErrorHandling(
  "GET /api/clients/[id]",
  async (request: Request, ctx: Ctx) => {
    const user = await requireUser(request);
    const client = findClient(getDb(), user.id, await resolveId(ctx));
    if (!client) throw notFound();
    return NextResponse.json({ data: toDto(client) });
  },
);

export const PUT = withErrorHandling(
  "PUT /api/clients/[id]",
  async (request: Request, ctx: Ctx) => {
    const user = await requireUser(request);
    const id = await resolveId(ctx);
    const input = await parseJsonBody(request, updateClientSchema);
    const db = getDb();
    let updated;
    try {
      updated = updateClient(db, user.id, id, input);
    } catch (err) {
      if (isUniqueViolation(err))
        throw new HttpError(409, "CONFLICT", "已有相同 email 的客戶");
      throw err;
    }
    if (updated) return NextResponse.json({ data: toDto(updated) });
    // 沒更新到：分辨「不存在」和「版本衝突」
    const current = findClient(db, user.id, id);
    if (!current) throw notFound();
    throw new HttpError(
      409,
      "VERSION_CONFLICT",
      "資料已被其他人修改，請重新載入",
      {
        currentVersion: current.version,
      },
    );
  },
);

export const DELETE = withErrorHandling(
  "DELETE /api/clients/[id]",
  async (request: Request, ctx: Ctx) => {
    const user = await requireUser(request);
    const id = await resolveId(ctx);
    try {
      if (!deleteClient(getDb(), user.id, id)) throw notFound();
    } catch (err) {
      if (isForeignKeyViolation(err)) {
        throw new HttpError(409, "CONFLICT", "此客戶仍有專案或發票，無法刪除");
      }
      throw err;
    }
    return new Response(null, { status: 204 });
  },
);
