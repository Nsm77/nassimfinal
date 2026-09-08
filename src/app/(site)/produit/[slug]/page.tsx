import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { and, eq } from "drizzle-orm";
import { db } from "@/db";
import { wishlistItems } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { getProductBySlug, getRelated } from "@/lib/catalog";
import { SITE_URL } from "@/lib/env";
import { discountPercent, formatDT, formatDTShort } from "@/lib/money";
import { formatDate } from "@/lib/utils";
import { Badge, Breadcrumbs } from "@/components/ui/primitives";
import { Stars } from "@/components/ui/stars";
import { Reveal } from "@/components/motion/reveal";
import { ProductGrid } from "@/components/catalog/product-card";
import { RecentlyViewed, TrackView } from "@/components/catalog/recently-viewed";
import { BuyBox } from "@/components/product/buy-box";
import { ReviewForm } from "@/components/product/review-form";
import { SectionHeading } from "@/components/ui/primitives";

export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const p = await getProductBySlug((await params).slug);
  if (!p) return {};
  const title = `${p.name}${p.brand ? ` — ${p.brand.name}` : ""}`;
  return { title, description: p.shortDescription ?? undefined, openGraph: { title, description: p.shortDescription ?? undefined, images: p.image ? [p.image] : [], type: "website" }, twitter: { card: "summary_large_image", title, images: p.image ? [p.image] : [] } };
}

export default async function ProduitPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [p, user] = await Promise.all([getProductBySlug(slug), getCurrentUser()]);
  if (!p) notFound();
  const [related, wishedRow] = await Promise.all([
    getRelated(p.id, p.categoryId, p.universeId, 4),
    user ? db.select().from(wishlistItems).where(and(eq(wishlistItems.userId, user.id), eq(wishlistItems.productId, p.id))).limit(1) : Promise.resolve([]),
  ]);
  const pct = discountPercent(p.priceMillimes, p.compareAtMillimes);
  const out = p.stock <= 0;
  const jsonLd = {
    "@context": "https://schema.org", "@type": "Product", name: p.name, image: p.image ? [`${SITE_URL}${p.image}`] : [], description: p.shortDescription, sku: p.sku, brand: p.brand ? { "@type": "Brand", name: p.brand.name } : undefined,
    offers: { "@type": "Offer", url: `${SITE_URL}/produit/${p.slug}`, priceCurrency: "TND", price: (p.priceMillimes / 1000).toFixed(3), availability: p.stock > 0 ? "https://schema.org/InStock" : "https://schema.org/OutOfStock", itemCondition: "https://schema.org/NewCondition" },
    aggregateRating: p.ratingCount > 0 ? { "@type": "AggregateRating", ratingValue: (p.ratingAvg / 100).toFixed(1), reviewCount: p.ratingCount } : undefined,
    review: p.reviews.slice(0, 5).map((r) => ({ "@type": "Review", author: { "@type": "Person", name: r.authorName }, reviewRating: { "@type": "Rating", ratingValue: r.rating }, reviewBody: r.body })),
  };
  const crumbs = { "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Accueil", item: SITE_URL }, ...(p.universe ? [{ "@type": "ListItem", position: 2, name: p.universe.name, item: `${SITE_URL}/univers/${p.universe.slug}` }] : []), { "@type": "ListItem", position: 3, name: p.name, item: `${SITE_URL}/produit/${p.slug}` }] };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(crumbs) }} />
      <TrackView id={p.id} />
      <div className="border-b border-stone">
        <div className="container-lux pt-6 lg:pt-10">
          <Breadcrumbs items={[...(p.universe ? [{ href: `/univers/${p.universe.slug}`, label: p.universe.name }] : []), ...(p.category ? [{ href: `/categorie/${p.category.slug}`, label: p.category.name }] : []), { label: p.name }]} />
          <div className="mt-8 grid gap-12 pb-14 lg:grid-cols-12 lg:gap-14 lg:pb-20">
            {/* Gallery */}
            <div className="lg:col-span-7">
              <div className="relative aspect-square overflow-hidden bg-stone lg:sticky lg:top-28">
                {p.image && <Image src={p.image} alt={`${p.name} — ${p.brand?.name ?? "Cléopâtre"}`} fill priority sizes="(max-width:1024px) 100vw, 58vw" className={`object-cover transition-transform duration-[1600ms] ease-[cubic-bezier(0.22,1,0.36,1)] ${out ? "opacity-70" : ""}`} />}
                <div className="absolute left-5 top-5 flex flex-col items-start gap-2">
                  {pct > 0 && <Badge tone="ink">-{pct} %</Badge>}
                  {p.isNew && !pct && <Badge tone="accent">Nouveau</Badge>}
                </div>
                <p className="absolute bottom-0 left-0 right-0 flex items-center justify-between bg-paper/80 px-4 py-2 text-[9px] font-bold uppercase tracking-[0.2em] text-muted backdrop-blur-sm">
                  <span>{p.brand?.name ?? "Cléopâtre"} · Réf. {p.sku}</span>
                  <span>{p.volume}</span>
                </p>
              </div>
            </div>

            {/* Information */}
            <div className="lg:col-span-5">
              <div className="lg:sticky lg:top-28">
                {p.brand && (
                  <Link href={`/marque/${p.brand.slug}`} className="group inline-flex items-center gap-3 text-[10px] font-bold uppercase tracking-[0.22em] text-muted transition-colors hover:text-ink">
                    <span className="font-display text-base italic text-champagne-2">{p.brand.name}</span>
                  </Link>
                )}
                <h1 className="mt-3 font-display text-display-md text-ink">{p.name}</h1>
                {p.ratingCount > 0 && (
                  <a href="#avis" className="mt-4 inline-flex items-center gap-2"><Stars value={p.ratingAvg / 100} count={p.ratingCount} size={13} /><span className="text-xs text-muted">· {p.ratingCount} avis</span></a>
                )}
                <div className="mt-6 flex items-baseline gap-3 border-y border-stone py-5">
                  <span className="text-[1.7rem] font-medium tabular-nums tracking-tight text-ink">{formatDT(p.priceMillimes)}</span>
                  {pct > 0 && p.compareAtMillimes && (
                    <span className="flex items-baseline gap-2">
                      <span className="text-sm tabular-nums text-muted-2 line-through">{formatDT(p.compareAtMillimes)}</span>
                      <Badge tone="success">Économisez {formatDTShort(p.compareAtMillimes - p.priceMillimes)}</Badge>
                    </span>
                  )}
                </div>

                <p className="mt-6 text-[15px] leading-[1.8] text-charcoal">{p.shortDescription}</p>

                {p.concerns.length > 0 && (
                  <div className="mt-6">
                    <p className="eyebrow mb-3">Répond à vos besoins</p>
                    <ul className="flex flex-wrap gap-2">
                      {p.concerns.map((c) => (
                        <li key={c.concernId}><Link href={`/besoin/${c.concern.slug}`} className="inline-flex min-h-9 items-center border border-stone-2 px-3.5 text-[10px] font-bold uppercase tracking-[0.16em] text-charcoal transition-colors hover:border-ink hover:bg-ink hover:text-paper">{c.concern.name}</Link></li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="mt-8"><BuyBox p={{ id: p.id, slug: p.slug, name: p.name, brandName: p.brand?.name ?? null, image: p.image, priceMillimes: p.priceMillimes, compareAtMillimes: p.compareAtMillimes, stock: p.stock, lowStockThreshold: p.lowStockThreshold, volume: p.volume }} wished={wishedRow.length > 0} isAuthed={!!user} /></div>

                <div className="mt-9 divide-y divide-stone border-y border-stone">
                  {[["Description", p.description], ["Composition & ingrédients", p.ingredients], ["Conseils d'utilisation", p.howToUse]].map(([t, body], i) => body ? (
                    <details key={t} open={i === 0} className="group py-1">
                      <summary className="flex min-h-12 cursor-pointer list-none items-center justify-between text-[11px] font-bold uppercase tracking-[0.18em] text-ink">
                        {t}<span aria-hidden="true" className="pl-4 font-display text-2xl font-normal text-muted transition-transform duration-500 group-open:rotate-45">+</span>
                      </summary>
                      <p className="pb-5 text-[14px] leading-[1.85] text-charcoal">{body}</p>
                    </details>
                  ) : null)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Avis */}
      <section id="avis" className="border-b border-stone bg-cream">
        <div className="container-lux grid gap-12 py-section-sm lg:grid-cols-12">
          <div className="lg:col-span-4">
            <p className="eyebrow mb-6 flex items-center gap-3"><span className="font-display text-lg italic text-champagne-2">Avis</span> L&apos;expérience réelle</p>
            <div className="flex items-end gap-3">
              <span className="font-display text-[4rem] leading-none text-ink">{p.ratingCount > 0 ? (p.ratingAvg / 100).toFixed(1) : "—"}</span>
              <span className="pb-2 text-lg text-muted">/ 5</span>
            </div>
            {p.ratingCount > 0 && <Stars value={p.ratingAvg / 100} count={p.ratingCount} size={15} className="mt-3" />}
            <p className="mt-5 max-w-xs text-sm leading-relaxed text-muted">Avis authentiques, modérés par notre équipe. Nous ne supprimons jamais un retour négatif fondé.</p>
          </div>
          <div className="space-y-8 lg:col-span-8">
            {p.reviews.length === 0 ? (
              <p className="rounded-sm border border-dashed border-stone-2 bg-paper px-6 py-10 text-sm text-muted">Aucun avis pour l&apos;instant. Soyez la première à partager votre expérience — elle aide les autres clientes à choisir.</p>
            ) : (
              <ul className="space-y-0">
                {p.reviews.map((r, i) => (
                  <li key={r.id} className={i > 0 ? "border-t border-stone pt-7" : ""}>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-full border border-stone-2 bg-paper font-display text-sm italic text-champagne-2">{r.authorName.charAt(0)}</span>
                        <div><p className="text-sm font-medium text-ink">{r.authorName}</p><p className="text-xs text-muted">{formatDate(r.createdAt)}</p></div>
                      </div>
                      <Stars value={r.rating} showCount={false} size={12} />
                    </div>
                    {r.title && <p className="mt-4 text-[15px] font-medium text-ink">{r.title}</p>}
                    <p className="mt-1.5 text-sm leading-[1.8] text-charcoal">{r.body}</p>
                    {r.reply && (
                      <div className="mt-4 border-l-2 border-champagne bg-paper px-5 py-4 text-sm leading-relaxed text-charcoal">
                        <p className="eyebrow mb-1.5 text-champagne-2">Réponse de Cléopâtre</p>{r.reply}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
            <ReviewForm productId={p.id} defaultName={user ? `${user.firstName} ${user.lastName[0]}.` : ""} />
          </div>
        </div>
      </section>

      {related.length > 0 && (
        <section className="border-b border-stone bg-paper">
          <div className="container-lux py-section-sm">
            <SectionHeading index="→" eyebrow="Complétez votre routine" title="Vous aimerez aussi" />
            <div className="mt-12"><ProductGrid items={related} isAuthed={!!user} priorityCount={0} /></div>
          </div>
        </section>
      )}
      <RecentlyViewed excludeId={p.id} isAuthed={!!user} />
      <div className="h-20 lg:hidden" />
    </>
  );
}
