"use server";
import { and, eq, inArray, sql } from "drizzle-orm";
import { revalidatePath } from "next/cache";
import { db } from "@/db";
import { newsletterSubscribers, products, reviews, searchEvents, supportTickets, wishlistItems } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { fail, MESSAGES, ok, zodFieldErrors, type ActionResult } from "@/lib/api";
import { evaluatePromo } from "@/lib/promotions";
import { rateLimit } from "@/lib/rate-limit";
import { clientKey } from "@/lib/origin";
import { cartLineSchema, newsletterSchema, reviewSchema, ticketSchema } from "@/lib/validation";
import { track } from "@/lib/orders";

export async function toggleWishlistAction(productId: number): Promise<ActionResult<{ wished: boolean }>> {
  const me = await getCurrentUser();
  if (!me) return fail(MESSAGES.unauthorized);
  if (!Number.isInteger(productId) || productId <= 0) return fail(MESSAGES.invalid);
  const [p] = await db.select({ id: products.id }).from(products).where(and(eq(products.id, productId), eq(products.status, "active"))).limit(1);
  if (!p) return fail(MESSAGES.notFound);
  /*
   * Atomic toggle. The DELETE is the single arbiter of who owned the row, so two
   * concurrent clicks can no longer both take the "insert" branch: previously
   * that hit the (user_id, product_id) primary key and surfaced as a 500, and
   * the item ended up not saved at all.
   */
  const removed = await db.delete(wishlistItems).where(and(eq(wishlistItems.userId, me.id), eq(wishlistItems.productId, p.id))).returning({ productId: wishlistItems.productId });
  revalidatePath("/compte/favoris");
  if (removed.length) return ok({ wished: false }, "Retiré de vos favoris.");
  await db.insert(wishlistItems).values({ userId: me.id, productId: p.id }).onConflictDoNothing();
  await track("wishlist.add", { productId: p.id }, me.id);
  return ok({ wished: true }, "Ajouté à vos favoris.");
}

export async function submitReviewAction(_prev: ActionResult | null, form: FormData): Promise<ActionResult> {
  if (!(await rateLimit(`review:${await clientKey()}`, 5, 600_000))) return fail(MESSAGES.rateLimited);
  const me = await getCurrentUser();
  const parsed = reviewSchema.safeParse({ productId: Number(form.get("productId")), rating: Number(form.get("rating")), title: form.get("title"), body: form.get("body"), authorName: form.get("authorName") || (me ? `${me.firstName} ${me.lastName[0]}.` : "") });
  if (!parsed.success) return fail(MESSAGES.invalid, zodFieldErrors(parsed.error.issues));
  // Reject unknown products up front: otherwise the foreign key raises and the
  // caller gets an opaque failure instead of a usable message.
  const [target] = await db.select({ id: products.id }).from(products).where(and(eq(products.id, parsed.data.productId), eq(products.status, "active"))).limit(1);
  if (!target) return fail(MESSAGES.notFound);
  await db.insert(reviews).values({ ...parsed.data, title: parsed.data.title || null, userId: me?.id ?? null, status: "pending" });
  return ok(undefined, "Merci ! Votre avis sera publié après modération.");
}

export async function validatePromoAction(code: string, lines: { productId: number; quantity: number }[]): Promise<ActionResult<{ discount: number; freeShipping: boolean; label: string; code: string }>> {
  if (!(await rateLimit(`promo:${await clientKey()}`, 20, 60_000))) return fail(MESSAGES.rateLimited);
  const me = await getCurrentUser();
  if (!Array.isArray(lines) || !lines.length) return fail("Votre panier est vide.");
  if (lines.length > 100) return fail("Panier trop volumineux.");
  // `lines` is client-supplied. Prices are always re-read from the database below,
  // but an unchecked quantity would still let a caller quote a nonsense discount
  // (or an absurd `IN (...)` list), so validate against the same bounds the cart
  // itself uses.
  for (const l of lines) {
    if (!cartLineSchema.safeParse(l).success) return fail(MESSAGES.invalid);
  }
  const ids = lines.map((l) => l.productId);
  const rows = await db.select({ id: products.id, price: products.priceMillimes, universeId: products.universeId }).from(products).where(and(inArray(products.id, ids), eq(products.status, "active")));
  const promoLines = lines.map((l) => { const p = rows.find((r) => r.id === l.productId); return { productId: l.productId, universeId: p?.universeId ?? null, lineTotal: (p?.price ?? 0) * l.quantity }; });
  const res = await evaluatePromo(code, promoLines, me?.id);
  if (!res.ok) return fail(res.reason);
  return ok({ discount: res.discount, freeShipping: res.freeShipping, label: res.label, code: res.promo.code }, "Code appliqué.");
}

export async function subscribeNewsletterAction(_prev: ActionResult | null, form: FormData): Promise<ActionResult> {
  // Public, unauthenticated write. Without a limiter this is a free way to fill
  // the subscriber table; the unique email only dedupes identical addresses.
  if (!(await rateLimit(`newsletter:${await clientKey()}`, 5, 3_600_000))) return fail(MESSAGES.rateLimited);
  const parsed = newsletterSchema.safeParse({ email: form.get("email") });
  if (!parsed.success) return fail("Adresse e-mail invalide.");
  await db.insert(newsletterSubscribers).values({ email: parsed.data.email }).onConflictDoNothing();
  return ok(undefined, "Merci, vous êtes inscrit(e).");
}

export async function createTicketAction(_prev: ActionResult | null, form: FormData): Promise<ActionResult> {
  if (!(await rateLimit(`ticket:${await clientKey()}`, 3, 600_000))) return fail(MESSAGES.rateLimited);
  const me = await getCurrentUser();
  const parsed = ticketSchema.safeParse(Object.fromEntries(form));
  if (!parsed.success) return fail(MESSAGES.invalid, zodFieldErrors(parsed.error.issues));
  await db.insert(supportTickets).values({ ...parsed.data, orderNumber: parsed.data.orderNumber || null, userId: me?.id ?? null });
  return ok(undefined, "Message envoyé. Nous répondons sous 24 h ouvrées.");
}

export async function logSearchAction(query: string, resultsCount: number) {
  const q = query.trim().slice(0, 200);
  if (q.length < 2) return;
  // One row per call on a public endpoint: without a limiter a single client can
  // grow `search_events` without bound. Over budget the analytics event is simply
  // dropped — search itself is unaffected.
  if (!(await rateLimit(`search:${await clientKey()}`, 30, 60_000))) return;
  const me = await getCurrentUser();
  try { await db.insert(searchEvents).values({ query: q.toLowerCase(), resultsCount, userId: me?.id ?? null }); } catch {}
}
