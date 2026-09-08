import "server-only";
import { and, eq, sql } from "drizzle-orm";
import { db, type Tx } from "@/db";
import { orders, promotions, type Promotion } from "@/db/schema";
import type { Millimes } from "./money";

export type PromoLine = { productId: number; universeId: number | null; lineTotal: Millimes };
export type PromoResult =
  | { ok: true; promo: Promotion; discount: Millimes; freeShipping: boolean; label: string }
  | { ok: false; reason: string };

const normalize = (code: string) => code.trim().toUpperCase();

/**
 * Pure eligibility + discount maths, shared by the read-only preview path and
 * the transactional checkout path so the two can never drift apart.
 * `promo` must be a freshly-read row: callers are responsible for reading it
 * under whatever lock their context requires.
 */
function evaluate(promo: Promotion, lines: PromoLine[]): PromoResult {
  const now = new Date();
  if (promo.startsAt && promo.startsAt > now) return { ok: false, reason: "Ce code n'est pas encore actif." };
  if (promo.endsAt && promo.endsAt < now) return { ok: false, reason: "Ce code a expiré." };
  if (promo.usageLimit !== null && promo.usageCount >= promo.usageLimit) return { ok: false, reason: "Ce code a atteint sa limite d'utilisation." };

  const eligible = promo.universeId ? lines.filter((l) => l.universeId === promo.universeId) : lines;
  const eligibleTotal = eligible.reduce((s, l) => s + l.lineTotal, 0);
  const subtotal = lines.reduce((s, l) => s + l.lineTotal, 0);
  if (subtotal < promo.minSubtotalMillimes) {
    return { ok: false, reason: `Minimum d'achat : ${(promo.minSubtotalMillimes / 1000).toFixed(0)} DT.` };
  }
  if (promo.universeId && eligibleTotal === 0) return { ok: false, reason: "Aucun article éligible à ce code." };

  let discount = 0;
  let freeShipping = false;
  if (promo.type === "percent") discount = Math.floor((eligibleTotal * promo.value) / 100);
  else if (promo.type === "fixed") discount = Math.min(promo.value, eligibleTotal);
  else freeShipping = true;
  if (promo.maxDiscountMillimes) discount = Math.min(discount, promo.maxDiscountMillimes);
  discount = Math.max(0, Math.min(discount, subtotal));
  return { ok: true, promo, discount, freeShipping, label: promo.label };
}

/**
 * Read-only preview (cart / checkout « Appliquer » button).
 * Best-effort by nature: the authoritative check happens at order time in
 * `reservePromoUsage`, under a row lock.
 */
export async function evaluatePromo(code: string, lines: PromoLine[], userId?: number | null, email?: string | null): Promise<PromoResult> {
  const normalized = normalize(code);
  if (!normalized) return { ok: false, reason: "Code requis." };
  const promo = await db.query.promotions.findFirst({ where: eq(promotions.code, normalized) });
  if (!promo || !promo.isActive) return { ok: false, reason: "Ce code n'est pas valide." };
  const base = evaluate(promo, lines);
  if (!base.ok) return base;
  if (promo.perUserLimit > 0 && (userId || email)) {
    const used = await countUserUses(userId ?? null, email ?? null, normalized);
    if (used >= promo.perUserLimit) return { ok: false, reason: "Vous avez déjà utilisé ce code." };
  }
  return base;
}

async function countUserUses(userId: number | null, email: string | null, code: string): Promise<number> {
  const cond = userId ? eq(orders.userId, userId) : eq(orders.email, email!);
  const rows = await db
    .select({ n: sql<number>`count(*)::int` })
    .from(orders)
    .where(and(cond, eq(orders.promoCode, code), sql`${orders.status} <> 'cancelled'`));
  return rows[0]?.n ?? 0;
}

/**
 * Authoritative, transaction-safe promotion consumption.
 *
 * Concurrency model: the promotion row is locked `FOR UPDATE` before any check,
 * so every concurrent checkout using the same code serialises here. That makes
 * both limits race-free:
 *   • global  — re-checked against the locked row, then enforced a second time
 *               by the conditional `UPDATE … WHERE usage_count < usage_limit`.
 *   • per-user — the count is read while holding the lock, and the consuming
 *               order is inserted in the *same* transaction, so the next waiter
 *               sees it as soon as it acquires the lock.
 *
 * No in-memory state is involved, so this holds across app instances.
 * Must be called inside the checkout transaction, before the order is inserted.
 */
export async function reservePromoUsage(
  tx: Tx,
  code: string,
  lines: PromoLine[],
  userId?: number | null,
  email?: string | null,
): Promise<PromoResult> {
  const normalized = normalize(code);
  if (!normalized) return { ok: false, reason: "Code requis." };

  const locked = await tx.select().from(promotions).where(sql`upper(${promotions.code}) = ${normalized}`).for("update").limit(1);
  const promo = locked[0];
  if (!promo || !promo.isActive) return { ok: false, reason: "Ce code n'est pas valide." };

  const base = evaluate(promo, lines);
  if (!base.ok) return base;

  if (promo.perUserLimit > 0 && (userId || email)) {
    const cond = userId ? eq(orders.userId, userId) : eq(orders.email, email!);
    const rows = await tx
      .select({ n: sql<number>`count(*)::int` })
      .from(orders)
      .where(and(cond, eq(orders.promoCode, normalized), sql`${orders.status} <> 'cancelled'`));
    if ((rows[0]?.n ?? 0) >= promo.perUserLimit) return { ok: false, reason: "Vous avez déjà utilisé ce code." };
  }

  // Atomic consumption. The guard is in SQL, so the counter can never pass its
  // limit even if two writers somehow reached this point together.
  const bumped = await tx
    .update(promotions)
    .set({ usageCount: sql`${promotions.usageCount} + 1`, updatedAt: new Date() })
    .where(
      and(
        eq(promotions.id, promo.id),
        eq(promotions.isActive, true),
        sql`(${promotions.startsAt} IS NULL OR ${promotions.startsAt} <= now())`,
        sql`(${promotions.endsAt} IS NULL OR ${promotions.endsAt} > now())`,
        sql`(${promotions.usageLimit} IS NULL OR ${promotions.usageCount} < ${promotions.usageLimit})`,
      ),
    )
    .returning({ id: promotions.id });
  if (!bumped.length) return { ok: false, reason: "Ce code a atteint sa limite d'utilisation." };

  return base;
}
