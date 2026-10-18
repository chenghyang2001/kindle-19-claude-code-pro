/** 客戶資料存取。所有查詢都帶 ownerId，避免讀到別人的客戶。 */
import { and, desc, eq } from "drizzle-orm";
import type { Db } from "@/db/client";
import { clients, type Client } from "@/db/schema";
import type { CreateClientInput, UpdateClientInput } from "./validation";

export type ClientDto = Omit<Client, "ownerId" | "createdAt" | "updatedAt"> & {
  createdAt: string;
  updatedAt: string;
};

export function toDto(row: Client): ClientDto {
  const { ownerId: _owner, createdAt, updatedAt, ...rest } = row;
  return {
    ...rest,
    createdAt: createdAt.toISOString(),
    updatedAt: updatedAt.toISOString(),
  };
}

export function listClients(
  db: Db,
  ownerId: string,
  limit: number,
  offset: number,
) {
  return db
    .select()
    .from(clients)
    .where(eq(clients.ownerId, ownerId))
    .orderBy(desc(clients.createdAt))
    .limit(limit)
    .offset(offset)
    .all();
}

export function insertClient(
  db: Db,
  ownerId: string,
  input: CreateClientInput,
): Client {
  return db
    .insert(clients)
    .values({
      ownerId,
      name: input.name,
      company: input.company ?? null,
      email: input.email ?? null,
      phone: input.phone ?? null,
      notes: input.notes ?? null,
    })
    .returning()
    .get();
}

export function findClient(
  db: Db,
  ownerId: string,
  id: string,
): Client | undefined {
  return db
    .select()
    .from(clients)
    .where(and(eq(clients.id, id), eq(clients.ownerId, ownerId)))
    .get();
}

/** 樂觀鎖更新：version 不符時回 undefined，呼叫端回 409。 */
export function updateClient(
  db: Db,
  ownerId: string,
  id: string,
  input: UpdateClientInput,
): Client | undefined {
  const { version, ...fields } = input;
  return db
    .update(clients)
    .set({ ...fields, version: version + 1, updatedAt: new Date() })
    .where(
      and(
        eq(clients.id, id),
        eq(clients.ownerId, ownerId),
        eq(clients.version, version),
      ),
    )
    .returning()
    .get();
}

export function deleteClient(db: Db, ownerId: string, id: string): boolean {
  const result = db
    .delete(clients)
    .where(and(eq(clients.id, id), eq(clients.ownerId, ownerId)))
    .run();
  return result.changes > 0;
}
