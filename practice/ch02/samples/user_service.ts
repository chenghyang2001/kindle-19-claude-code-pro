// 範例：待 Code Review 的 TypeScript（刻意埋了型別安全問題）
interface User {
  id: number;
  name: string;
  email?: string;
  role: "admin" | "member";
}

const cache: any = {};

export async function fetchUser(id: any): Promise<User> {
  if (cache[id]) return cache[id];
  const res = await fetch(`/api/users/${id}`);
  const data = await res.json();
  cache[id] = data;
  return data as User;
}

export function emailDomain(user: User): string {
  return user.email!.split("@")[1];
}

export function isAdmin(user: User): boolean {
  return (user.role as string) == "Admin";
}

export function parseUsers(raw: string): User[] {
  return JSON.parse(raw);
}
