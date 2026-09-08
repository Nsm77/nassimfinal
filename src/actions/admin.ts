"use server";
import { and, desc, eq, sql } from "drizzle-orm";
import { revalidatePath } from "next/cache";
import { db } from "@/db";
import { articles, orders, productConcerns, products, promotions, reviews, stores, supportTickets, users, type OrderStatus } from "@/db/schema";
import { requireAdmin, requireStaff } from "@/lib/auth";
import { fail, MESSAGES, ok, zodFieldErrors, type ActionResult } from "@/lib/api";
import { ALLOWED_TRANSITIONS, addOrderEvent, audit, awardLoyaltyForOrder, lockOrder, lockProducts, recordMovement, restockOrder, reverseLoyaltyForOrder } from "@/lib/orders";
import { orderStatusSchema, productSchema, promotionSchema, stockAdjustSchema, userRoleSchema } from "@/lib/validation";
import { slugify } from "@/lib/utils";

async function staff() {
  try { return await requireStaff(); } catch { return null; }
}
async function adminOnly() {
  try { return await requireAdmin(); } catch { return null; }
}

export async function updateOrderStatusAction(orderId: number, next: string, message?: string): Promise<ActionResult> {
  const me = await staff();
  if (!me) return fail(MESSAGES.forbidden);
  const parsed = orderStatusSchema.safeParse(next);
  if (!parsed.success) return fail("Statut invalide.");
  try {
    await db.transaction(async (tx) => {
      const o = await lockOrder(tx, orderId);
      if (!o) throw new Error(MESSAGES.notFound);
      if (!ALLOWED_TRANSITIONS[o.status].includes(parsed.data)) throw new Error(`Transition ${o.status} → ${parsed.data} non autorisée.`);
      const patch: Partial<typeof orders.$inferInsert> = { status: parsed.data, updatedAt: new Date() };
      if (parsed.data === "delivered" && o.paymentMethod === "cod") patch.paymentStatus = "paid";
      if (parsed.data === "cancelled" || parsed.data === "returned") {
        await restockOrder(tx, o.id, me.id);
        // Claw back any points already granted for this order.
        await reverseLoyaltyForOrder(tx, o, `${parsed.data === "returned" ? "Retour" : "Annulation"} commande ${o.number}`);
        if (o.paymentStatus === "paid") patch.paymentStatus = "refunded";
      }
      // Conditional on the status we actually read: if another actor moved the
      // order first, this updates 0 rows and we bail instead of double-applying.
      const updated = await tx.update(orders).set(patch).where(and(eq(orders.id, o.id), eq(orders.status, o.status))).returning({ id: orders.id });
      if (!updated.length) throw new Error("Cette commande vient d'être modifiée. Merci de recharger la page.");
      if (parsed.data === "delivered") {
        // Settlement point: COD is marked paid above, and this is where loyalty
        // is actually earned. Idempotent — one award per order, enforced by a
        // partial unique index.
        await awardLoyaltyForOrder(tx, { ...o, status: parsed.data, paymentStatus: patch.paymentStatus ?? o.paymentStatus });
      }
      await addOrderEvent(tx, o.id, parsed.data as OrderStatus, message || undefined, me.id);
    });
    await audit(me.id, "order.status", "order", orderId, { next: parsed.data });
    revalidatePath("/admin/commandes");
    revalidatePath(`/admin/commandes/${orderId}`);
    return ok(undefined, "Statut mis à jour.");
  } catch (e) {
    return fail(e instanceof Error ? e.message : MESSAGES.generic);
  }
}

const BULK_LIMIT = 100;

export async function bulkOrderStatusAction(ids: number[], next: string): Promise<ActionResult<{ done: number }>> {
  const me = await staff();
  if (!me) return fail(MESSAGES.forbidden);
  if (!Array.isArray(ids)) return fail(MESSAGES.invalid);
  // Each id costs a locked transaction; an unbounded array is a cheap DoS.
  if (ids.length > BULK_LIMIT) return fail(`Maximum ${BULK_LIMIT} commandes à la fois.`);
  let done = 0;
  for (const id of ids) {
    const r = await updateOrderStatusAction(id, next);
    if (r.ok) done++;
  }
  return ok({ done }, `${done}/${ids.length} commande(s) mise(s) à jour.`);
}

export async function saveOrderNotesAction(orderId: number, internalNote: string, trackingCode: string): Promise<ActionResult> {
  const me = await staff();
  if (!me) return fail(MESSAGES.forbidden);
  await db.update(orders).set({ internalNote: internalNote.slice(0, 2000) || null, trackingCode: trackingCode.slice(0, 80) || null, updatedAt: new Date() }).where(eq(orders.id, orderId));
  revalidatePath(`/admin/commandes/${orderId}`);
  return ok(undefined, "Notes enregistrées.");
}

function parseProductForm(form: FormData) {
  const num = (k: string) => { const v = String(form.get(k) ?? "").trim(); return v === "" ? null : Number(v); };
  const dt = (k: string) => Math.round(Number(String(form.get(k) ?? "0").replace(",", ".")) * 1000);
  return productSchema.safeParse({
    name: form.get("name"), slug: String(form.get("slug") || slugify(String(form.get("name") || ""))), sku: form.get("sku"),
    shortDescription: form.get("shortDescription"), description: form.get("description"), ingredients: form.get("ingredients"), howToUse: form.get("howToUse"),
    brandId: num("brandId"), categoryId: num("categoryId"), universeId: num("universeId"),
    priceMillimes: dt("priceDT"), compareAtMillimes: String(form.get("compareAtDT") || "").trim() ? dt("compareAtDT") : null,
    stock: Number(form.get("stock") || 0), lowStockThreshold: Number(form.get("lowStockThreshold") || 5),
    volume: form.get("volume"), image: form.get("image"), status: form.get("status"), isFeatured: form.get("isFeatured") === "on", isNew: form.get("isNew") === "on",
    concernIds: form.getAll("concernIds").map(Number).filter(Boolean),
  });
}

export async function saveProductAction(_prev: ActionResult<{ id: number }> | null, form: FormData): Promise<ActionResult<{ id: number }>> {
  const me = await adminOnly();
  if (!me) return fail(MESSAGES.forbidden);
  const parsed = parseProductForm(form);
  if (!parsed.success) return fail(MESSAGES.invalid, zodFieldErrors(parsed.error.issues));
  const id = Number(form.get("id") || 0);
  const { concernIds, ...d } = parsed.data;
  const values = { ...d, shortDescription: d.shortDescription || null, description: d.description || null, ingredients: d.ingredients || null, howToUse: d.howToUse || null, volume: d.volume || null, image: d.image || null, images: d.image ? [d.image] : [] };
  try {
    const pid = await db.transaction(async (tx) => {
      let productId = id;
      if (id) {
        const before = await tx.query.products.findFirst({ where: eq(products.id, id) });
        if (!before) throw new Error(MESSAGES.notFound);
        const { stock, ...rest } = values;
        await tx.update(products).set({ ...rest, updatedAt: new Date() }).where(eq(products.id, id));
        if (stock !== before.stock) await recordMovement(tx, { productId: id, type: "adjust", quantity: stock - before.stock, reason: "Modification fiche produit", userId: me.id });
        await tx.delete(productConcerns).where(eq(productConcerns.productId, id));
      } else {
        const [p] = await tx.insert(products).values({ ...values, stock: 0 }).returning({ id: products.id });
        productId = p.id;
        if (values.stock > 0) await recordMovement(tx, { productId, type: "in", quantity: values.stock, reason: "Stock initial", userId: me.id });
      }
      if (concernIds.length) await tx.insert(productConcerns).values(concernIds.map((c) => ({ productId, concernId: c })));
      return productId;
    });
    await audit(me.id, id ? "product.update" : "product.create", "product", pid);
    revalidatePath("/admin/produits");
    revalidatePath("/boutique");
    return ok({ id: pid }, "Produit enregistré.");
  } catch (e) {
    const msg = e instanceof Error ? e.message : MESSAGES.generic;
    return fail(msg.includes("unique") ? "Slug ou SKU déjà utilisé." : msg);
  }
}

export async function adjustStockAction(_prev: ActionResult | null, form: FormData): Promise<ActionResult> {
  const me = await staff();
  if (!me) return fail(MESSAGES.forbidden);
  const parsed = stockAdjustSchema.safeParse({ productId: Number(form.get("productId")), delta: Number(form.get("delta")), reason: form.get("reason") });
  if (!parsed.success) return fail(MESSAGES.invalid, zodFieldErrors(parsed.error.issues));
  try {
    await db.transaction(async (tx) => {
      // Lock the product row: an admin adjustment racing a concurrent checkout
      // must not read a stale stock value.
      const [p] = await lockProducts(tx, [parsed.data.productId]);
      if (!p) throw new Error(MESSAGES.notFound);
      if (p.stock + parsed.data.delta < 0) throw new Error("Le stock ne peut pas devenir négatif.");
      await recordMovement(tx, { productId: p.id, type: parsed.data.delta > 0 ? "restock" : "adjust", quantity: parsed.data.delta, reason: parsed.data.reason, userId: me.id });
    });
    await audit(me.id, "stock.adjust", "product", parsed.data.productId, parsed.data);
    revalidatePath("/admin/stock");
    return ok(undefined, "Stock ajusté.");
  } catch (e) {
    return fail(e instanceof Error ? e.message : MESSAGES.generic);
  }
}

export async function savePromotionAction(_prev: ActionResult | null, form: FormData): Promise<ActionResult> {
  const me = await adminOnly();
  if (!me) return fail(MESSAGES.forbidden);
  const type = String(form.get("type"));
  const parsed = promotionSchema.safeParse({
    code: form.get("code"), label: form.get("label"), type,
    value: type === "fixed" ? Math.round(Number(form.get("value") || 0) * 1000) : Number(form.get("value") || 0),
    minSubtotalMillimes: Math.round(Number(form.get("minDT") || 0) * 1000),
    maxDiscountMillimes: String(form.get("maxDT") || "").trim() ? Math.round(Number(form.get("maxDT")) * 1000) : null,
    usageLimit: String(form.get("usageLimit") || "").trim() ? Number(form.get("usageLimit")) : null,
    perUserLimit: Number(form.get("perUserLimit") || 1), isActive: form.get("isActive") === "on", endsAt: form.get("endsAt"),
  });
  if (!parsed.success) return fail(MESSAGES.invalid, zodFieldErrors(parsed.error.issues));
  const id = Number(form.get("id") || 0);
  const universeId = Number(form.get("universeId") || 0) || null;
  const values = { ...parsed.data, universeId, endsAt: parsed.data.endsAt ? new Date(parsed.data.endsAt) : null };
  try {
    if (id) await db.update(promotions).set({ ...values, updatedAt: new Date() }).where(eq(promotions.id, id));
    else await db.insert(promotions).values(values);
    await audit(me.id, id ? "promo.update" : "promo.create", "promotion", id || values.code);
    revalidatePath("/admin/promotions");
    return ok(undefined, "Promotion enregistrée.");
  } catch {
    return fail("Ce code existe déjà.");
  }
}
export async function deletePromotionAction(id: number): Promise<ActionResult> {
  const me = await adminOnly();
  if (!me) return fail(MESSAGES.forbidden);
  await db.delete(promotions).where(eq(promotions.id, id));
  await audit(me.id, "promo.delete", "promotion", id);
  revalidatePath("/admin/promotions");
  return ok(undefined, "Promotion supprimée.");
}

export async function moderateReviewAction(id: number, status: "approved" | "rejected", reply?: string): Promise<ActionResult> {
  const me = await staff();
  if (!me) return fail(MESSAGES.forbidden);
  // Status change and rating re-aggregation must commit together, otherwise a
  // failure in between leaves products.rating_avg out of sync with the reviews.
  await db.transaction(async (tx) => {
    const [r] = await tx.update(reviews).set({ status, reply: reply?.trim() || null, updatedAt: new Date() }).where(eq(reviews.id, id)).returning();
    if (!r) return;
    const agg = await tx.select({ avg: sql<number>`coalesce(round(avg(rating)*100),0)::int`, n: sql<number>`count(*)::int` }).from(reviews).where(sql`${reviews.productId} = ${r.productId} AND ${reviews.status} = 'approved'`);
    await tx.update(products).set({ ratingAvg: agg[0]?.avg ?? 0, ratingCount: agg[0]?.n ?? 0 }).where(eq(products.id, r.productId));
  });
  await audit(me.id, "review.moderate", "review", id, { status });
  revalidatePath("/admin/avis");
  return ok(undefined, status === "approved" ? "Avis publié." : "Avis rejeté.");
}

export async function replyTicketAction(id: number, reply: string, close: boolean): Promise<ActionResult> {
  const me = await staff();
  if (!me) return fail(MESSAGES.forbidden);
  if (reply.trim().length < 2) return fail("Réponse trop courte.");
  await db.update(supportTickets).set({ reply: reply.trim(), status: close ? "closed" : "answered", updatedAt: new Date() }).where(eq(supportTickets.id, id));
  await audit(me.id, "ticket.reply", "ticket", id);
  revalidatePath("/admin/support");
  return ok(undefined, "Réponse enregistrée.");
}

export async function saveArticleAction(_prev: ActionResult | null, form: FormData): Promise<ActionResult> {
  const me = await adminOnly();
  if (!me) return fail(MESSAGES.forbidden);
  const id = Number(form.get("id") || 0);
  const title = String(form.get("title") || "").trim();
  const body = String(form.get("body") || "").trim();
  if (title.length < 3 || body.length < 20) return fail("Titre ou contenu trop court.");
  const values = { title, slug: String(form.get("slug") || slugify(title)), excerpt: String(form.get("excerpt") || "").slice(0, 400) || null, body, tag: String(form.get("tag") || "") || null, image: String(form.get("image") || "") || null, readMinutes: Math.max(1, Math.ceil(body.split(/\s+/).length / 200)), isPublished: form.get("isPublished") === "on" };
  try {
    if (id) await db.update(articles).set({ ...values, updatedAt: new Date() }).where(eq(articles.id, id));
    else await db.insert(articles).values(values);
    revalidatePath("/journal"); revalidatePath("/admin/journal");
    return ok(undefined, "Article enregistré.");
  } catch { return fail("Slug déjà utilisé."); }
}

export async function saveStoreAction(_prev: ActionResult | null, form: FormData): Promise<ActionResult> {
  const me = await adminOnly();
  if (!me) return fail(MESSAGES.forbidden);
  const id = Number(form.get("id") || 0);
  const v = { name: String(form.get("name") || ""), slug: String(form.get("slug") || slugify(String(form.get("name") || ""))), address: String(form.get("address") || ""), city: String(form.get("city") || ""), phone: String(form.get("phone") || ""), hours: String(form.get("hours") || ""), mapsUrl: String(form.get("mapsUrl") || "") || null, isActive: form.get("isActive") === "on" };
  if (v.name.length < 2 || v.address.length < 3 || v.phone.length < 8) return fail("Champs obligatoires manquants.");
  try {
    if (id) await db.update(stores).set({ ...v, updatedAt: new Date() }).where(eq(stores.id, id));
    else await db.insert(stores).values(v);
  } catch {
    // stores.slug is unique; report it instead of leaking a driver error.
    return fail("Une boutique utilise déjà cet identifiant (slug).");
  }
  revalidatePath("/boutiques"); revalidatePath("/admin/boutiques");
  return ok(undefined, "Boutique enregistrée.");
}

export async function updateUserRoleAction(userId: number, role: "customer" | "support" | "admin"): Promise<ActionResult> {
  const me = await adminOnly();
  if (!me) return fail(MESSAGES.forbidden);
  // The declared type is not a runtime guarantee: validate, otherwise a bad value
  // reaches the Postgres enum and surfaces as an unhandled driver error.
  const parsedRole = userRoleSchema.safeParse(role);
  if (!parsedRole.success) return fail("Rôle invalide.");
  if (!Number.isInteger(userId) || userId <= 0) return fail(MESSAGES.invalid);
  if (me.id === userId) return fail("Vous ne pouvez pas modifier votre propre rôle.");
  const updated = await db.update(users).set({ role: parsedRole.data, updatedAt: new Date() }).where(eq(users.id, userId)).returning({ id: users.id });
  if (!updated.length) return fail(MESSAGES.notFound);
  await audit(me.id, "user.role", "user", userId, { role: parsedRole.data });
  revalidatePath("/admin/clients");
  return ok(undefined, "Rôle mis à jour.");
}
export async function saveCustomerNoteAction(userId: number, notes: string): Promise<ActionResult> {
  const me = await staff();
  if (!me) return fail(MESSAGES.forbidden);
  if (!Number.isInteger(userId) || userId <= 0) return fail(MESSAGES.invalid);
  const updated = await db.update(users).set({ notes: notes.slice(0, 2000) || null }).where(eq(users.id, userId)).returning({ id: users.id });
  if (!updated.length) return fail(MESSAGES.notFound);
  revalidatePath(`/admin/clients/${userId}`);
  return ok(undefined, "Note enregistrée.");
}

export async function recentOrdersForExport() {
  await requireStaff();
  return db.select().from(orders).orderBy(desc(orders.createdAt)).limit(2000);
}
