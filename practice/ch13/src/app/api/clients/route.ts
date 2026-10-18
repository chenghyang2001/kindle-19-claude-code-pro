/** GET /api/clients（列表）與 POST /api/clients（建立）。 */
import { NextResponse } from "next/server";
import { z } from "zod";
import { getDb } from "@/db/client";
import { insertClient, listClients, toDto } from "@/lib/clients-repo";
import {
  HttpError,
  isUniqueViolation,
  parseJsonBody,
  requireUser,
  withErrorHandling,
} from "@/lib/http";
import { createClientSchema } from "@/lib/validation";

// better-sqlite3 需要 Node.js runtime，且每次請求都要即時查詢
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const paginationSchema = z.object({
  limit: z.coerce.number().int().min(1).max(100).default(20),
  offset: z.coerce.number().int().min(0).default(0),
});

export const GET = withErrorHandling(
  "GET /api/clients",
  async (request: Request) => {
    const user = await requireUser(request);
    const params = Object.fromEntries(new URL(request.url).searchParams);
    const page = paginationSchema.safeParse(params);
    if (!page.success) {
      throw new HttpError(
        400,
        "VALIDATION_ERROR",
        "分頁參數錯誤",
        z.flattenError(page.error).fieldErrors,
      );
    }
    const rows = listClients(
      getDb(),
      user.id,
      page.data.limit,
      page.data.offset,
    );
    return NextResponse.json(
      { data: rows.map(toDto), ...page.data },
      { status: 200 },
    );
  },
);

export const POST = withErrorHandling(
  "POST /api/clients",
  async (request: Request) => {
    // 1. 認證 → 2. 驗證 → 3. 寫入 → 4. 201
    const user = await requireUser(request);
    const input = await parseJsonBody(request, createClientSchema);
    try {
      const created = insertClient(getDb(), user.id, input);
      return NextResponse.json(
        { data: toDto(created) },
        { status: 201, headers: { Location: `/api/clients/${created.id}` } },
      );
    } catch (err) {
      if (isUniqueViolation(err)) {
        throw new HttpError(409, "CONFLICT", "已有相同 email 的客戶");
      }
      throw err;
    }
  },
);
