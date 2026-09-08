import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { getConcernBySlug, getConcerns } from "@/lib/catalog";
import { Listing, type SP } from "@/components/catalog/listing";
import { ProductGridSkeleton } from "@/components/ui/primitives";
import { InfoIcon } from "@/components/icons";

export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const c = await getConcernBySlug((await params).slug);
  return c ? { title: `${c.name} — conseils & produits`, description: c.intro ?? undefined } : {};
}
export default async function BesoinPage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<SP> }) {
  const [{ slug }, sp] = await Promise.all([params, searchParams]);
  const [c, all] = await Promise.all([getConcernBySlug(slug), getConcerns()]);
  if (!c) notFound();
  const i = all.findIndex((x) => x.id === c.id);
  return (
    <>
      <section className="border-b border-stone bg-noir text-paper">
        <div className="container-lux py-10 lg:py-14">
          <p className="eyebrow mb-6 flex items-center gap-3 text-paper/55"><span className="font-display text-lg italic text-champagne-3">{String(i + 1).padStart(2, "0")} / {String(all.length).padStart(2, "0")}</span> Par besoin</p>
          <div className="grid items-end gap-8 lg:grid-cols-12">
            <h1 className="font-display text-display-lg lg:col-span-8">{c.name} — <em className="text-champagne-3">que faire&nbsp;?</em></h1>
            <p className="max-w-md text-sm leading-relaxed text-paper/65 lg:col-span-4 lg:pb-2">Sélection guidée par nos pharmaciens. Chaque produit ci-dessous répond à ce besoin précis.</p>
          </div>
        </div>
      </section>

      <section className="border-b border-stone bg-cream">
        <div className="container-lux py-8 lg:py-10">
          <div className="grid gap-8 lg:grid-cols-12">
            <div className="lg:col-span-7">
              <div className="flex gap-5 border-l-2 border-champagne bg-paper p-6">
                <InfoIcon size={20} className="mt-1 shrink-0 text-champagne-2" />
                <p className="text-[15px] leading-[1.8] text-charcoal">{c.intro}</p>
              </div>
            </div>
            <nav className="lg:col-span-5" aria-label="Autres besoins">
              <p className="eyebrow mb-4">Autres besoins</p>
              <div className="flex flex-wrap gap-2">
                {all.filter((x) => x.id !== c.id).map((x) => (
                  <Link key={x.id} href={`/besoin/${x.slug}`} className="inline-flex min-h-10 items-center border border-stone-2 bg-paper px-3.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-charcoal transition-colors hover:border-ink hover:text-ink">{x.name}</Link>
                ))}
              </div>
            </nav>
          </div>
        </div>
      </section>

      <div className="container-lux py-10 lg:py-14">
        <Suspense fallback={<ProductGridSkeleton />}><Listing base={{ concernId: c.id }} sp={sp} hideConcerns basePath={`/besoin/${c.slug}`} /></Suspense>
      </div>
    </>
  );
}
