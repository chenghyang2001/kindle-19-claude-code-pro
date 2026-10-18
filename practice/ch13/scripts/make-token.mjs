// 產生本機測試用 JWT：AUTH_SECRET=... node scripts/make-token.mjs [userId]
import { SignJWT } from "jose";

const secret = process.env.AUTH_SECRET;
if (!secret || secret.length < 32) {
  console.error("錯誤：環境變數 AUTH_SECRET 缺少或少於 32 字元");
  process.exit(1);
}
const userId = process.argv[2] ?? "demo-user";

try {
  const token = await new SignJWT({})
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(userId)
    .setIssuer("freelancer-dashboard")
    .setIssuedAt()
    .setExpirationTime("1h")
    .sign(new TextEncoder().encode(secret));
  console.log(token);
} catch (err) {
  console.error(`錯誤：產生 token 失敗：${err.message}`);
  process.exit(1);
}
