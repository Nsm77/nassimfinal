import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { Listing, type SP } from "@/components/catalog/listing";
import { getUniverses } from "@/lib/catalog";
import { ProductGridSkeleton } from "@/components/ui/primitives";
import { PageIntro } from "@/components/shell/page-intro";
import { ArrowRightIcon } from "@/components/icons";

export const metadata: Metadata = {
  title: "Boutique",
  description: "Toute la sélection Cléopâtre : dermo-cosmétique, solaire, cheveux, bébé & maman, compléments — produits authentiques conseillés par nos pharmaciens.",
};
export const dynamic = "force-dynamic";

export default async function BoutiquePage({ searchParams }: { searchParams: Promise<SP> }) {
  const [sp, universes] = await Promise.all([searchParams, getUniverses()]);
  return (
    <div className="border-b border-stone">
      <PageIntro
        index="La boutique"
        kicker="Toute la sélection"
        title={<>La boutique<br className="hidden sm:block" /> <em className="text-champagne-2">Cléopâtre</em></>}
        intro="Chaque référence est choisie par nos pharmaciens pour sa tolérance, son efficacité et son authenticité. Filtrez par univers, marque, besoin ou prix — la sélection reste humaine."
      />
      <div className="container-lux pt-9">
        <div className="scrollbar-none -mx-1 flex gap-2 overflow-x-auto pb-1 lg:flex-wrap">
          {universes.map((u) => (
            <Link key={u.id} href={`/univers/${u.slug}`} className="group inline-flex shrink-0 items-center gap-2 border border-stone-2 bg-cream px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.16em] text-charcoal transition-colors hover:border-ink hover:bg-ink hover:text-paper">
              {u.name} <ArrowRightIcon size={11} className="opacity-0 transition-opacity group-hover:opacity-100" />
            </Link>
          ))}
          <Link href="/promotions" className="group inline-flex shrink-0 items-center gap-2 bg-champagne-soft px-4 py-2.5 text-[11px] font-bold uppercase tracking-[0.16em] text-champagne-2 transition-colors hover:bg-ink hover:text-paper">
            Offres <ArrowRightIcon size={11} />
          </Link>
        </div>
      </div>
      <div className="container-lux py-10 lg:py-14">
        <Suspense fallback={<ProductGridSkeleton />}><Listing base={{}} sp={sp} basePath="/boutique" /></Suspense>
      </div>
    </div>
  );
}
