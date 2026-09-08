import { sql } from "drizzle-orm";
import { db } from "@/db";
import { rateLimits } from "@/db/schema";

/**
 * Rate limiting.
 *
 * Primary store is PostgreSQL, so counters are shared across every app instance
 * and survive restarts — an in-process Map cannot enforce a limit when the app
 * runs more than one worker. The whole check is a single atomic upsert, so two
 * simultaneous requests cannot both slip through.
 *
 * The in-memory bucket below is a *fallback only*, used when the database is
 * unreachable (local tooling, DB outage). It is deliberately fail-open on error
 * so a limiter problem can never take the storefront down.
 */

const buckets = new Map<string, { count: number; resetAt: number }>();

function memoryRateLimit(key: string, limit: number, windowMs: number): boolean {
  const now = Date.now();
  const b = buckets.get(key);
  if (!b || b.resetAt < now) {
    if (buckets.size > 5000) buckets.clear();
    buckets.set(key, { count: 1, resetAt: now + windowMs });
    return true;
  }
  if (b.count >= limit) return false;
  b.count += 1;
  return true;
}

// Opportunistic sweep so the table does not grow without bound.
let lastSweep = 0;
async function sweep() {
  const now = Date.now();
  if (now - lastSweep < 60_000) return;
  lastSweep = now;
  try {
    await db.delete(rateLimits).where(sql`${rateLimits.resetAt} < now()`);
  } catch { /* best effort */ }
}

export async function rateLimit(key: string, limit = 10, windowMs = 60_000): Promise<boolean> {
  const bucket = key.slice(0, 190);
  try {
    const rows = await db
      .insert(rateLimits)
      .values({ key: bucket, count: 1, resetAt: sql`now() + make_interval(secs => ${windowMs} / 1000.0)` })
      .onConflictDoUpdate({
        target: rateLimits.key,
        set: {
          count: sql`CASE WHEN ${rateLimits.resetAt} <= now() THEN 1 ELSE ${rateLimits.count} + 1 END`,
          resetAt: sql`CASE WHEN ${rateLimits.resetAt} <= now() THEN now() + make_interval(secs => ${windowMs} / 1000.0) ELSE ${rateLimits.resetAt} END`,
        },
      })
      .returning({ count: rateLimits.count });
    void sweep();
    return (rows[0]?.count ?? 1) <= limit;
  } catch {
    return memoryRateLimit(bucket, limit, windowMs);
  }
}
