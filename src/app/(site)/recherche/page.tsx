import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { Listing, type SP } from "@/components/catalog/listing";
import { getUniverses, listProducts } from "@/lib/catalog";
import { ProductGridSkeleton } from "@/components/ui/primitives";
import { logSearchAction } from "@/actions/shop";
import { SearchIcon } from "@/components/icons";
export const metadata: Metadata = { title: "Recherche", robots: { index: false } };
export const dynamic = "force-dynamic";
export default async function RecherchePage({ searchParams }: { searchParams: Promise<SP> }) {
  const sp = await searchParams;
  const q = typeof sp.q === "string" ? sp.q.trim() : "";
  if (q.length >= 2 && !sp.page) { const { total } = await listProducts({ q, perPage: 1 }); await logSearchAction(q, total); }
  const unis = await getUniverses();
  return (
    <div className="border-b border-stone">
      <section className="bg-noir text-paper">
        <div className="container-lux py-12 lg:py-16">
          <p className="eyebrow mb-6 flex items-center gap-3 text-paper/55"><span className="font-display text-lg italic text-champagne-3">Recherche</span> L&apos;archive Cléopâtre</p>
          <h1 className="font-display text-display-lg">
            {q ? <>«&nbsp;<em className="text-champagne-3">{q}</em>&nbsp;»</> : <>Que cherchez-vous&nbsp;?</>}
          </h1>
          <p className="mt-5 max-w-xl text-sm leading-relaxed text-paper/60">{q ? "Voici les produits qui correspondent le mieux à votre recherche." : "Un actif, une marque, un besoin : cherchez dans toute la sélection — produits, marques, univers et conseils."}</p>
        </div>
      </section>
      <div className="container-lux py-10 lg:py-14">
        {q.length >= 2 ? (
          <Suspense fallback={<ProductGridSkeleton />}><Listing base={{ q }} sp={sp} basePath="/recherche" /></Suspense>
        ) : (
          <div className="border border-dashed border-stone-2 bg-cream px-6 py-14 text-center">
            <SearchIcon size={26} className="mx-auto text-sand-2" />
            <p className="mt-5 font-display text-display-sm text-ink">Saisissez au moins deux caractères</p>
            <p className="mx-auto mt-2 max-w-sm text-sm text-muted">Ou explorez un univers pour commencer :</p>
            <ul className="mt-7 flex flex-wrap justify-center gap-2">
              {unis.map((u) => <li key={u.id}><Link href={`/univers/${u.slug}`} className="inline-flex min-h-10 items-center border border-stone-2 px-4 text-[11px] font-bold uppercase tracking-[0.16em] text-charcoal transition-colors hover:border-ink hover:bg-ink hover:text-paper">{u.name}</Link></li>)}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
