/**
 * 認證：驗證 `Authorization: Bearer <JWT>`（HS256）。
 * 教學用自簽 JWT；正式環境改接 NextAuth v5 的 session / JWT 即可，介面不變。
 */
import { jwtVerify, SignJWT } from "jose";

const ISSUER = "freelancer-dashboard";
const MIN_SECRET_LENGTH = 32;

function getSecretKey(): Uint8Array {
  const secret = process.env.AUTH_SECRET;
  if (!secret || secret.length < MIN_SECRET_LENGTH) {
    throw new Error(
      `環境變數 AUTH_SECRET 缺少或少於 ${MIN_SECRET_LENGTH} 字元`,
    );
  }
  return new TextEncoder().encode(secret);
}

export type AuthUser = { id: string };

/** 回傳登入者；token 缺少、格式錯、簽章錯、過期一律回 null（呼叫端回 401）。 */
export async function authenticate(request: Request): Promise<AuthUser | null> {
  const header = request.headers.get("authorization");
  const match = header?.match(/^Bearer\s+(\S+)$/i);
  if (!match) return null;
  // 金鑰設定錯誤是伺服器問題，要往外拋成 500，不能被當成 401 吞掉
  const key = getSecretKey();
  try {
    const { payload } = await jwtVerify(match[1], key, {
      issuer: ISSUER,
      algorithms: ["HS256"],
    });
    if (typeof payload.sub !== "string" || payload.sub.length === 0)
      return null;
    return { id: payload.sub };
  } catch {
    return null;
  }
}

export async function signToken(
  userId: string,
  expiresIn = "1h",
): Promise<string> {
  return new SignJWT({})
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(userId)
    .setIssuer(ISSUER)
    .setIssuedAt()
    .setExpirationTime(expiresIn)
    .sign(getSecretKey());
}
