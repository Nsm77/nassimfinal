import Image from "next/image";
import { redirect } from "next/navigation";
import Link from "next/link";
import { desc, eq } from "drizzle-orm";
import { db } from "@/db";
import { orders, wishlistItems } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { getByIds } from "@/lib/catalog";
import { formatDT } from "@/lib/money";
import { formatDate } from "@/lib/utils";
import { ORDER_STATUS_LABELS } from "@/lib/orders";
import { Badge } from "@/components/ui/primitives";
import { ArrowRightIcon, HeartIcon, PackageIcon, PhoneIcon, UserIcon } from "@/components/icons";
export const dynamic = "force-dynamic";
export default async function ComptePage() {
  // Do not rely on the layout having redirected: Next.js renders the page
  // alongside it, so an anonymous request would otherwise dereference null.
  const user = await getCurrentUser();
  if (!user) redirect("/connexion?next=/compte");
  const [recent, wishIds, spentRow] = await Promise.all([
    db.query.orders.findMany({ where: eq(orders.userId, user.id), orderBy: desc(orders.createdAt), limit: 3, with: { items: true } }),
    db.select({ id: wishlistItems.productId }).from(wishlistItems).where(eq(wishlistItems.userId, user.id)).orderBy(desc(wishlistItems.createdAt)).limit(4),
    db.select().from(orders).where(eq(orders.userId, user.id)),
  ]);
  const wished = await getByIds(wishIds.map((w) => w.id));
  const spent = spentRow.filter((o) => o.status !== "cancelled").reduce((a, o) => a + o.totalMillimes, 0);
  const next = recent.find((o) => ["pending", "confirmed", "preparing", "shipped"].includes(o.status));
  return (
    <div className="space-y-14">
      {/* Current order */}
      {next && (
        <section className="border border-stone bg-cream">
          <div className="grid gap-6 p-7 sm:grid-cols-[1fr_auto] sm:items-center lg:p-8">
            <div>
              <p className="eyebrow mb-3 text-champagne-2">En cours</p>
              <h2 className="font-display text-display-sm text-ink">Commande {next.number}</h2>
              <p className="mt-2 text-sm text-muted">Passée le {formatDate(next.createdAt)} · {next.items.reduce((a, i) => a + i.quantity, 0)} article(s) · {ORDER_STATUS_LABELS[next.status]}</p>
            </div>
            <div className="flex items-center gap-5">
              <span className="font-display text-3xl italic text-ink">{formatDT(next.totalMillimes)}</span>
              <Link href={`/compte/commandes/${next.number}`} className="btn-primary px-6">Suivre</Link>
            </div>
          </div>
          <ul className="flex gap-4 overflow-x-auto border-t border-stone px-7 py-4 lg:px-8">
            {next.items.map((i) => (
              <li key={i.id} className="flex shrink-0 items-center gap-3">
                <div className="relative h-16 w-14 overflow-hidden bg-stone">{i.image && <Image src={i.image} alt="" fill sizes="56px" className="object-cover" />}</div>
                <div className="w-40"><p className="truncate text-sm text-charcoal">{i.name}</p><p className="text-xs text-muted">{i.quantity} × {formatDT(i.unitPriceMillimes)}</p></div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Quick stats */}
      <section className="grid gap-px border border-stone bg-stone sm:grid-cols-3">
        {[
          { t: "Points fidélité", v: String(user.loyaltyPoints), d: "1 point par 10 DT d'achat" },
          { t: "Total commandé", v: formatDT(spent), d: "hors commandes annulées" },
          { t: "Favoris", v: String(wishIds.length), d: "dans votre sélection" },
        ].map((x) => (
          <div key={x.t} className="bg-paper p-7">
            <p className="eyebrow">{x.t}</p>
            <p className="mt-4 font-display text-[2.2rem] leading-none text-ink">{x.v}</p>
            <p className="mt-2 text-xs text-muted-2">{x.d}</p>
          </div>
        ))}
      </section>

      <div className="grid gap-12 lg:grid-cols-2">
        {/* Recent orders */}
        <section>
          <div className="mb-6 flex items-end justify-between gap-4">
            <div><p className="eyebrow mb-3">Historique</p><h2 className="font-display text-display-sm text-ink">Mes dernières commandes</h2></div>
            <Link href="/compte/commandes" className="btn-ghost">Tout voir</Link>
          </div>
          {recent.length === 0 ? (
            <div className="border border-dashed border-stone-2 bg-cream px-6 py-12 text-center">
              <PackageIcon size={22} className="mx-auto text-sand-2" />
              <p className="mt-4 font-display text-xl text-ink">Pas encore de commande</p>
              <p className="mx-auto mt-2 max-w-xs text-sm text-muted">Votre première commande est livrée gratuitement dès 99 DT.</p>
              <Link href="/boutique" className="btn-secondary mt-7">Découvrir la boutique</Link>
            </div>
          ) : (
            <ul className="divide-y divide-stone border-y border-stone">
              {recent.map((o) => (
                <li key={o.id}>
                  <Link href={`/compte/commandes/${o.number}`} className="flex items-center justify-between gap-4 py-5 transition-colors hover:bg-cream">
                    <div className="min-w-0">
                      <p className="text-sm text-ink">{o.number}</p>
                      <p className="mt-0.5 text-xs text-muted">{formatDate(o.createdAt)} · {o.items.reduce((a, i) => a + i.quantity, 0)} article(s)</p>
                    </div>
                    <div className="flex shrink-0 items-center gap-4">
                      <Badge tone={o.status === "delivered" ? "success" : o.status === "cancelled" ? "error" : o.status === "shipped" ? "outline" : "accent"}>{ORDER_STATUS_LABELS[o.status]}</Badge>
                      <span className="text-sm tabular-nums text-ink">{formatDT(o.totalMillimes)}</span>
                      <ArrowRightIcon size={14} className="text-sand-2" />
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Wishlist preview + shortcuts */}
        <section className="space-y-12">
          <div>
            <div className="mb-6 flex items-end justify-between gap-4">
              <div><p className="eyebrow mb-3">Sélection privée</p><h2 className="font-display text-display-sm text-ink">Mes favoris</h2></div>
              <Link href="/compte/favoris" className="btn-ghost">Gérer</Link>
            </div>
            {wished.length === 0 ? (
              <div className="border border-dashed border-stone-2 bg-cream px-6 py-8 text-center">
                <HeartIcon size={20} className="mx-auto text-sand-2" />
                <p className="mt-3 text-sm text-muted">Aucun favori pour l&apos;instant.</p>
                <Link href="/boutique" className="mt-5 inline-flex text-sm text-ink underline underline-offset-4">Trouver mes essentiels</Link>
              </div>
            ) : (
              <ul className="grid grid-cols-4 gap-3">
                {wished.map((w) => (
                  <li key={w.id}>
                    <Link href={`/produit/${w.slug}`} className="group block">
                      <div className="relative aspect-square overflow-hidden bg-stone">
                        {w.image && <Image src={w.image} alt="" fill sizes="100px" className="object-cover transition-transform duration-700 group-hover:scale-[1.05]" />}
                      </div>
                      <p className="mt-2 line-clamp-2 text-[11px] leading-snug text-charcoal">{w.name}</p>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Shortcuts */}
          <div>
            <p className="eyebrow mb-4">Raccourcis</p>
            <ul className="grid gap-px border border-stone bg-stone sm:grid-cols-2">
              {[
                { h: "/compte/profil", t: "Coordonnées", d: "Téléphone, e-mail, adresses", i: UserIcon },
                { h: "/compte/commandes", t: "Commandes & retours", d: "Historique complet", i: PackageIcon },
                { h: "/aide", t: "Aide & FAQ", d: "Livraison, retours, produits", i: PhoneIcon },
                { h: "/boutiques", t: "Nos boutiques", d: "Ezzahra · Hammam-Lif", i: UserIcon },
              ].map((x) => (
                <li key={x.h}><Link href={x.h} className="group flex items-start gap-4 bg-paper p-5 transition-colors hover:bg-cream"><x.i size={18} className="mt-0.5 shrink-0 text-champagne-2" /><span><span className="block text-sm text-ink">{x.t}</span><span className="mt-0.5 block text-xs text-muted">{x.d}</span></span></Link></li>
              ))}
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
