/** API Route 共用的回應與錯誤處理工具。 */
import { NextResponse } from "next/server";
import { z } from "zod";
import { authenticate, type AuthUser } from "./auth";

export type ErrorCode =
  | "UNAUTHORIZED"
  | "INVALID_JSON"
  | "VALIDATION_ERROR"
  | "NOT_FOUND"
  | "CONFLICT"
  | "VERSION_CONFLICT"
  | "UNSUPPORTED_MEDIA_TYPE"
  | "INTERNAL_ERROR";

export function errorResponse(
  status: number,
  code: ErrorCode,
  message: string,
  details?: unknown,
) {
  return NextResponse.json(
    { error: { code, message, ...(details !== undefined ? { details } : {}) } },
    { status },
  );
}

/** 控制流程用的例外：在 handler 任何地方 throw，最外層統一轉成回應。 */
export class HttpError extends Error {
  constructor(
    readonly status: number,
    readonly code: ErrorCode,
    message: string,
    readonly details?: unknown,
  ) {
    super(message);
  }
}

export async function requireUser(request: Request): Promise<AuthUser> {
  const user = await authenticate(request);
  if (!user) throw new HttpError(401, "UNAUTHORIZED", "缺少或無效的認證 token");
  return user;
}

export async function parseJsonBody<T extends z.ZodType>(
  request: Request,
  schema: T,
): Promise<z.output<T>> {
  const contentType = request.headers.get("content-type") ?? "";
  if (!contentType.toLowerCase().startsWith("application/json")) {
    throw new HttpError(
      415,
      "UNSUPPORTED_MEDIA_TYPE",
      "Content-Type 必須是 application/json",
    );
  }
  let raw: unknown;
  try {
    raw = await request.json();
  } catch {
    throw new HttpError(400, "INVALID_JSON", "Request body 不是合法的 JSON");
  }
  const parsed = schema.safeParse(raw);
  if (!parsed.success) {
    throw new HttpError(
      400,
      "VALIDATION_ERROR",
      "欄位驗證失敗",
      z.flattenError(parsed.error).fieldErrors,
    );
  }
  return parsed.data;
}

type DbError = { code?: string; message?: string; cause?: DbError };

/** Drizzle 有時把驅動錯誤包在 cause 裡，往下找到真正的 DB 錯誤 */
function dbErrorOf(err: unknown): DbError | null {
  if (typeof err !== "object" || err === null) return null;
  const e = err as DbError;
  return e.code ? e : (e.cause ?? e);
}

/** SQLite / Postgres 的唯一鍵衝突辨識 */
export function isUniqueViolation(err: unknown): boolean {
  const e = dbErrorOf(err);
  return e?.code === "SQLITE_CONSTRAINT_UNIQUE" || e?.code === "23505";
}

/**
 * 外鍵衝突辨識。
 * SQLite 的 ON DELETE RESTRICT 擋下刪除時，錯誤碼是 SQLITE_CONSTRAINT_TRIGGER
 * （不是 _FOREIGNKEY），所以另外比對錯誤訊息。
 */
export function isForeignKeyViolation(err: unknown): boolean {
  const e = dbErrorOf(err);
  if (!e) return false;
  if (e.code === "SQLITE_CONSTRAINT_FOREIGNKEY" || e.code === "23503")
    return true;
  return (
    e.code?.startsWith("SQLITE_CONSTRAINT") === true &&
    /FOREIGN KEY constraint failed/i.test(e.message ?? "")
  );
}

/** 包住 handler：HttpError 轉成對應狀態碼，其餘一律 500 且不洩漏內部細節。 */
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
      console.error(`${label} error:`, err);
      return errorResponse(500, "INTERNAL_ERROR", "伺服器內部錯誤");
    }
  };
}
