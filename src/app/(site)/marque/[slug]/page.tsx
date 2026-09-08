import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { getBrandBySlug } from "@/lib/catalog";
import { Listing, type SP } from "@/components/catalog/listing";
import { ProductGridSkeleton } from "@/components/ui/primitives";
import { PageIntro } from "@/components/shell/page-intro";
import { ShieldIcon } from "@/components/icons";

export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const b = await getBrandBySlug((await params).slug);
  return b ? { title: `${b.name} — tous les produits`, description: b.story ?? undefined } : {};
}
export default async function MarquePage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<SP> }) {
  const [{ slug }, sp] = await Promise.all([params, searchParams]);
  const b = await getBrandBySlug(slug);
  if (!b) notFound();
  return (
    <>
      <PageIntro
        index="Maison partenaire"
        kicker={b.country ?? "Laboratoire"}
        title={<><em className="text-champagne-2">La maison</em> {b.name}</>}
        intro={b.story}
        breadcrumbs={[{ href: "/marques", label: "Marques" }, { label: b.name }]}
      >
        <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-3 border-t border-stone pt-6 text-xs text-muted">
          <span className="flex items-center gap-2"><ShieldIcon size={14} className="text-champagne-2" /> Distribution officielle en Tunisie</span>
          {b.isFeatured && <span className="flex items-center gap-2 text-champagne-2">Sélection maison</span>}
          <Link href={`/marque/${b.slug}?sort=price_asc`} className="ml-auto text-charcoal underline-offset-4 hover:text-ink hover:underline">Trier par prix croissant</Link>
        </div>
      </PageIntro>
      <div className="container-lux py-10 lg:py-14">
        <Suspense fallback={<ProductGridSkeleton />}><Listing base={{ brandId: b.id }} sp={sp} hideBrands basePath={`/marque/${b.slug}`} /></Suspense>
      </div>
    </>
  );
}
