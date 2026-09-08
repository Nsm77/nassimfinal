import type { Metadata } from "next";
import { Suspense } from "react";
import { and, eq, gte, isNull, or } from "drizzle-orm";
import { db } from "@/db";
import { promotions } from "@/db/schema";
import { Listing, type SP } from "@/components/catalog/listing";
import { ProductGridSkeleton } from "@/components/ui/primitives";
import { TagIcon } from "@/components/icons";
import { formatDTShort } from "@/lib/money";
export const metadata: Metadata = { title: "Offres & promotions", description: "Prix justes et codes promo réels sur vos soins essentiels chez Cléopâtre." };
export const dynamic = "force-dynamic";
export default async function PromotionsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const sp = await searchParams;
  const codes = await db.select().from(promotions).where(and(eq(promotions.isActive, true), or(isNull(promotions.endsAt), gte(promotions.endsAt, new Date()))));
  return (
    <>
      <section className="border-b border-stone bg-noir text-paper">
        <div className="container-lux grid gap-10 py-12 lg:grid-cols-12 lg:py-16">
          <div className="lg:col-span-7">
            <p className="eyebrow mb-6 flex items-center gap-3 text-paper/55"><span className="font-display text-lg italic text-champagne-3">La campagne</span> Offres du moment</p>
            <h1 className="font-display text-display-lg">Prix justes, <em className="text-champagne-3">sans artifice.</em></h1>
            <p className="mt-6 max-w-xl text-[15px] leading-relaxed text-paper/70">Pas de fausses remises ni de prix gonflés : les offres ci-dessous portent sur des références que nous conseillons toute l&apos;année, avec des conditions écrites noir sur blanc.</p>
          </div>
          <div className="lg:col-span-5">
            <ul className="space-y-px border-y border-paper/15">
              {codes.map((p, i) => (
                <li key={p.id} className="grid grid-cols-[auto_1fr_auto] items-center gap-4 py-4">
                  <span className="font-display text-xs italic text-champagne-3">{String(i + 1).padStart(2, "0")}</span>
                  <div>
                    <p className="font-display text-lg tracking-[0.04em] text-paper"><code>{p.code}</code></p>
                    <p className="text-xs text-paper/60">{p.label}</p>
                  </div>
                  <span className="text-right text-[9px] font-bold uppercase leading-relaxed tracking-[0.14em] text-paper/45">{p.minSubtotalMillimes > 0 && <>dès {formatDTShort(p.minSubtotalMillimes)}<br /></>}{p.endsAt ? <>jusqu&apos;au {new Intl.DateTimeFormat("fr-TN", { day: "numeric", month: "long" }).format(p.endsAt)}</> : "permanent"}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="border-b border-stone bg-cream">
        <div className="container-lux grid gap-px bg-stone sm:grid-cols-3">
          {[
            { n: "01", t: "Choisissez", d: "Repérez un produit en promotion — la remise est déjà visible sur sa fiche." },
            { n: "02", t: "Ajoutez le code", d: "Au moment du paiement, saisissez le code promo. La remise s'applique aussitôt." },
            { n: "03", t: "Soyez livrée", d: "Livraison 24–72 h partout en Tunisie, ou retrait en 2 h en boutique." },
          ].map((s) => (
            <div key={s.n} className="bg-cream px-8 py-9">
              <p className="font-display text-2xl italic text-champagne-2">{s.n}</p>
              <p className="mt-3 flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.16em] text-ink"><TagIcon size={13} /> {s.t}</p>
              <p className="mt-2 text-sm leading-relaxed text-muted">{s.d}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="container-lux py-10 lg:py-14">
        <Suspense fallback={<ProductGridSkeleton />}><Listing base={{ promo: true }} sp={sp} basePath="/promotions" /></Suspense>
      </div>
    </>
  );
}
