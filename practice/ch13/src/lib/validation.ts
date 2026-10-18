/** 客戶 API 的 Zod schema（前後端可共用）。 */
import { z } from "zod";

// 空字串視為「沒填」，存成 null，避免 DB 裡混著 "" 和 NULL
const optionalText = (max: number) =>
  z
    .string()
    .trim()
    .max(max)
    .transform((v) => (v === "" ? null : v))
    .nullish();

export const createClientSchema = z.strictObject({
  name: z.string().trim().min(1, "name 為必填").max(100),
  company: optionalText(100),
  email: z
    .string()
    .trim()
    .toLowerCase()
    .pipe(z.email("email 格式錯誤").max(254))
    .nullish(),
  phone: z
    .string()
    .trim()
    .regex(/^[0-9+\-() ]{6,20}$/, "phone 只能包含數字、空白、+-()，長度 6~20")
    .nullish(),
  notes: optionalText(2000),
});

export const updateClientSchema = createClientSchema.partial().extend({
  // 樂觀鎖：客戶端必須帶上讀取時拿到的 version
  version: z.number().int().positive(),
});

export const idSchema = z.uuid();

export type CreateClientInput = z.infer<typeof createClientSchema>;
export type UpdateClientInput = z.infer<typeof updateClientSchema>;
