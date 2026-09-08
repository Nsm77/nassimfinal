import { desc } from "drizzle-orm";
import { db } from "@/db";
import { orders, products, users } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { toCsv } from "@/lib/utils";
export const dynamic = "force-dynamic";
export async function GET(_req: Request, { params }: { params: Promise<{ kind: string }> }) {
  const me = await getCurrentUser();
  if (!me || (me.role !== "admin" && me.role !== "support")) return new Response("Forbidden", { status: 403 });
  const { kind } = await params;
  let rows: Record<string, unknown>[] = [];
  if (kind === "orders") rows = (await db.select().from(orders).orderBy(desc(orders.createdAt)).limit(5000)).map((o) => ({ numero: o.number, date: o.createdAt.toISOString(), client: o.shippingAddress.fullName, email: o.email, telephone: o.phone, ville: o.shippingAddress.city, gouvernorat: o.shippingAddress.governorate, statut: o.status, paiement: o.paymentMethod, livraison: o.shippingMethod, sous_total_dt: o.subtotalMillimes / 1000, remise_dt: o.discountMillimes / 1000, livraison_dt: o.shippingMillimes / 1000, total_dt: o.totalMillimes / 1000, promo: o.promoCode ?? "" }));
  else if (kind === "products") rows = (await db.select().from(products)).map((p) => ({ sku: p.sku, nom: p.name, slug: p.slug, prix_dt: p.priceMillimes / 1000, prix_barre_dt: p.compareAtMillimes ? p.compareAtMillimes / 1000 : "", stock: p.stock, statut: p.status, ventes: p.salesCount }));
  else if (kind === "customers") { if (me.role !== "admin") return new Response("Forbidden", { status: 403 }); rows = (await db.select().from(users)).map((u) => ({ id: u.id, prenom: u.firstName, nom: u.lastName, email: u.email, telephone: u.phone ?? "", role: u.role, points: u.loyaltyPoints, inscrit: u.createdAt.toISOString() })); }
  else return new Response("Not found", { status: 404 });
  return new Response("\uFEFF" + toCsv(rows), { headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="cleopatre-${kind}-${new Date().toISOString().slice(0, 10)}.csv"` } });
}
