import "server-only";
import { randomBytes, scrypt as _scrypt, timingSafeEqual } from "node:crypto";
import { promisify } from "node:util";
import { cookies } from "next/headers";
import { and, eq, gt, lte } from "drizzle-orm";
import { cache } from "react";
import { db } from "@/db";
import { sessions, users, type User } from "@/db/schema";

const scrypt = promisify(_scrypt) as (p: string, s: string, n: number) => Promise<Buffer>;
export const SESSION_COOKIE = "cleo_session";
const SESSION_DAYS = 30;

export async function hashPassword(password: string): Promise<string> {
  const salt = randomBytes(16).toString("hex");
  const key = await scrypt(password, salt, 64);
  return `scrypt$${salt}$${key.toString("hex")}`;
}

export async function verifyPassword(password: string, stored: string): Promise<boolean> {
  const [algo, salt, hash] = stored.split("$");
  if (algo !== "scrypt" || !salt || !hash) return false;
  const key = await scrypt(password, salt, 64);
  const expected = Buffer.from(hash, "hex");
  return key.length === expected.length && timingSafeEqual(key, expected);
}

export async function createSession(userId: number, userAgent?: string | null) {
  const id = randomBytes(32).toString("hex");
  const expiresAt = new Date(Date.now() + SESSION_DAYS * 86_400_000);
  await db.insert(sessions).values({ id, userId, expiresAt, userAgent: userAgent ?? null });
  const jar = await cookies();
  jar.set(SESSION_COOKIE, id, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    expires: expiresAt,
    path: "/",
  });
  void pruneExpiredSessions();
}

/**
 * Sessions are validated by expiry on read but were never deleted, so the table
 * grew forever. Prune opportunistically (at most once a minute per process) so
 * no separate cron job is required.
 */
let lastPrune = 0;
async function pruneExpiredSessions() {
  const now = Date.now();
  if (now - lastPrune < 60_000) return;
  lastPrune = now;
  try {
    await db.delete(sessions).where(lte(sessions.expiresAt, new Date()));
  } catch { /* best effort — never block a login */ }
}

export async function destroySession() {
  const jar = await cookies();
  const id = jar.get(SESSION_COOKIE)?.value;
  if (id) await db.delete(sessions).where(eq(sessions.id, id));
  jar.delete(SESSION_COOKIE);
}

export type SafeUser = Omit<User, "passwordHash">;

export const getCurrentUser = cache(async (): Promise<SafeUser | null> => {
  const jar = await cookies();
  const id = jar.get(SESSION_COOKIE)?.value;
  if (!id) return null;
  const rows = await db
    .select({
      id: users.id,
      email: users.email,
      firstName: users.firstName,
      lastName: users.lastName,
      phone: users.phone,
      role: users.role,
      loyaltyPoints: users.loyaltyPoints,
      notes: users.notes,
      createdAt: users.createdAt,
      updatedAt: users.updatedAt,
    })
    .from(sessions)
    .innerJoin(users, eq(users.id, sessions.userId))
    .where(and(eq(sessions.id, id), gt(sessions.expiresAt, new Date())))
    .limit(1);
  return rows[0] ?? null;
});

export async function requireUser(): Promise<SafeUser> {
  const u = await getCurrentUser();
  if (!u) throw new Error("UNAUTHORIZED");
  return u;
}

export async function requireStaff(): Promise<SafeUser> {
  const u = await getCurrentUser();
  if (!u || (u.role !== "admin" && u.role !== "support")) throw new Error("FORBIDDEN");
  return u;
}

export async function requireAdmin(): Promise<SafeUser> {
  const u = await getCurrentUser();
  if (!u || u.role !== "admin") throw new Error("FORBIDDEN");
  return u;
}
