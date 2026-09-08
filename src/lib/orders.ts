import "server-only";
import { randomBytes } from "node:crypto";
import { and, eq, sql } from "drizzle-orm";
import { db, type Tx } from "@/db";
import {
  analyticsEvents,
  auditLogs,
  inventoryMovements,
  loyaltyTransactions,
  orderEvents,
  orders,
  products,
  users,
  type Order,
  type OrderStatus,
} from "@/db/schema";
import { loyaltyPointsFor } from "./money";

/* ── Public identifiers ────────────────────────────────── */

/**
 * Order numbers keep their historical shape (`CL-YYMMDD-XXXX`) but the random
 * suffix is widened from 2 bytes (65 536 values per day — trivially enumerable)
 * to 10 characters of an unambiguous base-32 alphabet (~2^50 values per day).
 *
 * The number is a *reference*, not a credential: guest access to an order is
 * granted by `accessKey`, never by the number alone.
 */
const ORDER_SUFFIX_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"; // no 0/O, 1/I, L

export function generateOrderNumber(date = new Date()): string {
  const ymd = `${date.getFullYear().toString().slice(2)}${String(date.getMonth() + 1).padStart(2, "0")}${String(date.getDate()).padStart(2, "0")}`;
  return `CL-${ymd}-${randomSuffix(10)}`;
}

function randomSuffix(len: number): string {
  const bytes = randomBytes(len);
  let out = "";
  for (let i = 0; i < len; i++) out += ORDER_SUFFIX_ALPHABET[bytes[i] % ORDER_SUFFIX_ALPHABET.length];
  return out;
}

/** Bearer token for guest order access. 256 bits — not guessable, not enumerable. */
export function generateAccessKey(): string {
  return randomBytes(32).toString("hex");
}

export function newIdempotencyKey() {
  return randomBytes(16).toString("hex");
}

/** Constant-time-ish comparison for access keys (avoids leaking via timing). */
export function safeEqual(a: string | null | undefined, b: string | null | undefined): boolean {
  if (!a || !b || a.length !== b.length) return false;
  const ba = Buffer.from(a);
  const bb = Buffer.from(b);
  let diff = 0;
  for (let i = 0; i < ba.length; i++) diff |= ba[i] ^ bb[i];
  return diff === 0;
}

/**
 * Pick an order number that is not already taken. With ~2^50 candidates per day
 * this loop essentially never repeats; the unique index on `orders.number`
 * remains the real guarantee.
 */
export async function reserveOrderNumber(tx: Tx, attempts = 5): Promise<string> {
  for (let i = 0; i < attempts; i++) {
    const candidate = generateOrderNumber();
    const clash = await tx.select({ id: orders.id }).from(orders).where(eq(orders.number, candidate)).limit(1);
    if (!clash.length) return candidate;
  }
  throw new Error("Impossible de générer un numéro de commande. Veuillez réessayer.");
}

/* ── Row-level locking helpers ─────────────────────────── */

/** Lock product rows FOR UPDATE and return them (throws if any missing). */
export async function lockProducts(tx: Tx, ids: number[]) {
  if (!ids.length) return [];
  const rows = await tx.execute(sql`SELECT id, name, sku, price_millimes, stock, image, brand_id, universe_id, status FROM products WHERE id IN ${ids} FOR UPDATE`);
  return rows.rows as Array<{ id: number; name: string; sku: string; price_millimes: number; stock: number; image: string | null; brand_id: number | null; universe_id: number | null; status: string }>;
}

/**
 * Lock a single order row FOR UPDATE.
 * Every status-changing path (customer cancel, admin transition, restock) must
 * go through this so concurrent requests serialise instead of double-applying.
 */
export async function lockOrder(tx: Tx, orderId: number): Promise<Order | null> {
  const rows = await tx.select().from(orders).where(eq(orders.id, orderId)).for("update").limit(1);
  return rows[0] ?? null;
}

/* ── Inventory ─────────────────────────────────────────── */

export async function recordMovement(tx: Tx, args: { productId: number; type: "in" | "out" | "adjust" | "sale" | "restock" | "return"; quantity: number; reason?: string; orderId?: number; userId?: number }) {
  const [p] = await tx.update(products).set({ stock: sql`${products.stock} + ${args.quantity}`, updatedAt: new Date() }).where(eq(products.id, args.productId)).returning({ stock: products.stock });
  if (!p) throw new Error("Article introuvable.");
  // Invariant: stock can never go negative. The transaction rolls back if it would.
  if (p.stock < 0) throw new Error("Stock insuffisant.");
  await tx.insert(inventoryMovements).values({ productId: args.productId, type: args.type, quantity: args.quantity, stockAfter: p.stock, reason: args.reason, orderId: args.orderId, userId: args.userId });
  return p.stock;
}

export async function addOrderEvent(tx: Tx | typeof db, orderId: number, status: OrderStatus, message?: string, actorId?: number) {
  await tx.insert(orderEvents).values({ orderId, status, message, actorId });
}

export async function audit(actorId: number | null, action: string, entity: string, entityId?: string | number, details: Record<string, unknown> = {}) {
  try { await db.insert(auditLogs).values({ actorId, action, entity, entityId: entityId != null ? String(entityId) : null, details }); } catch { /* never block */ }
}
export async function track(name: string, payload: Record<string, unknown> = {}, userId?: number | null) {
  try { await db.insert(analyticsEvents).values({ name, payload, userId: userId ?? null }); } catch { /* never block */ }
}

export { ORDER_STATUS_LABELS, ORDER_FLOW, ALLOWED_TRANSITIONS, PAYMENT_LABELS, SHIPPING_LABELS } from "./order-constants";

export async function restockOrder(tx: Tx, orderId: number, actorId?: number) {
  const items = await tx.execute(sql`SELECT product_id, quantity FROM order_items WHERE order_id = ${orderId} AND product_id IS NOT NULL`);
  for (const it of items.rows as Array<{ product_id: number; quantity: number }>) {
    await recordMovement(tx, { productId: it.product_id, type: "return", quantity: it.quantity, reason: "Annulation commande", orderId, userId: actorId });
    await tx.update(products).set({ salesCount: sql`greatest(${products.salesCount} - ${it.quantity}, 0)` }).where(eq(products.id, it.product_id));
  }
}

/* ── Loyalty accounting ────────────────────────────────── */

/**
 * Points are earned when an order is *settled*, not when it is created.
 * Cléopâtre's model is COD-first: `pending` means "we have not been paid yet",
 * so awarding points at creation let a customer earn (and later spend) points
 * on an order they could still cancel or refuse at the door.
 *
 * Trigger: the order reaching `delivered` — which is also the moment COD is
 * marked paid. Idempotent by construction: the partial unique index
 * `loyalty_order_award_idx` allows a single positive row per order, and
 * `onConflictDoNothing` turns a retry into a no-op instead of a second award.
 */
export async function awardLoyaltyForOrder(tx: Tx, order: Order): Promise<number> {
  if (!order.userId) return 0;
  const pts = loyaltyPointsFor(order.totalMillimes);
  if (pts <= 0) return 0;
  const inserted = await tx
    .insert(loyaltyTransactions)
    .values({ userId: order.userId, points: pts, reason: `Commande ${order.number}`, orderId: order.id })
    .onConflictDoNothing({ target: loyaltyTransactions.orderId, where: sql`${loyaltyTransactions.points} > 0` })
    .returning({ id: loyaltyTransactions.id });
  if (!inserted.length) return 0; // already awarded — duplicate request
  await tx.update(users).set({ loyaltyPoints: sql`${users.loyaltyPoints} + ${pts}` }).where(eq(users.id, order.userId));
  return pts;
}

/**
 * Reverse a previous award when an order is cancelled or returned.
 * Idempotent via `loyalty_order_reversal_idx` (one negative row per order).
 */
export async function reverseLoyaltyForOrder(tx: Tx, order: Order, reason: string): Promise<number> {
  if (!order.userId) return 0;
  const prior = await tx
    .select({ points: loyaltyTransactions.points })
    .from(loyaltyTransactions)
    .where(and(eq(loyaltyTransactions.orderId, order.id), sql`${loyaltyTransactions.points} > 0`))
    .limit(1);
  const awarded = prior[0]?.points ?? 0;
  if (awarded <= 0) return 0; // nothing to claw back (e.g. cancelled while still pending)
  const inserted = await tx
    .insert(loyaltyTransactions)
    .values({ userId: order.userId, points: -awarded, reason, orderId: order.id })
    .onConflictDoNothing({ target: loyaltyTransactions.orderId, where: sql`${loyaltyTransactions.points} < 0` })
    .returning({ id: loyaltyTransactions.id });
  if (!inserted.length) return 0; // already reversed
  await tx.update(users).set({ loyaltyPoints: sql`greatest(${users.loyaltyPoints} - ${awarded}, 0)` }).where(eq(users.id, order.userId));
  return awarded;
}

export { orders };
