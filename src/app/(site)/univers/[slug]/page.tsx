import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { getCategoryBySlug, getUniverses } from "@/lib/catalog";
import { Listing, type SP } from "@/components/catalog/listing";
import { ProductGridSkeleton } from "@/components/ui/primitives";
import { PageIntro } from "@/components/shell/page-intro";
import { ArrowRightIcon } from "@/components/icons";

export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const c = await getCategoryBySlug((await params).slug);
  return c ? { title: `Univers ${c.name}`, description: c.description ?? undefined, openGraph: c.image ? { images: [c.image] } : undefined } : {};
}

export default async function UniversPage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<SP> }) {
  const [{ slug }, sp] = await Promise.all([params, searchParams]);
  const [u, all] = await Promise.all([getCategoryBySlug(slug), getUniverses()]);
  if (!u || !u.isUniverse) notFound();
  const idx = all.findIndex((x) => x.id === u.id);
  const others = all.filter((x) => x.id !== u.id);
  return (
    <>
      <PageIntro
        index={`${String(idx + 1).padStart(2, "0")} / ${String(all.length).padStart(2, "0")}`}
        kicker="Univers"
        title={<>{u.name} — <em className="text-champagne-2">le rayon</em></>}
        intro={u.story}
        image={u.image}
        imageAlt={u.name}
        imagePriority
        breadcrumbs={[{ label: "Univers" }]}
      >
        <div className="mt-12 border-t border-stone pt-7">
          <p className="eyebrow mb-5">Dans cet univers</p>
          <ul className="grid gap-px bg-stone sm:grid-cols-2 lg:grid-cols-3">
            {u.children.map((c, i) => (
              <li key={c.id}>
                <Link href={`/categorie/${c.slug}`} className="group flex h-full min-h-24 items-center justify-between gap-4 bg-paper px-5 py-4 transition-colors duration-500 hover:bg-cream">
                  <span className="flex items-center gap-4">
                    <span className="font-display text-xs italic text-champagne-2">{String(i + 1).padStart(2, "0")}</span>
                    <span className="text-[15px] text-ink">{c.name}</span>
                  </span>
                  <ArrowRightIcon size={15} className="text-sand-2 transition-transform duration-500 group-hover:translate-x-1 group-hover:text-ink" />
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </PageIntro>

      <div className="container-lux py-10 lg:py-14">
        <Suspense fallback={<ProductGridSkeleton />}><Listing base={{ universeId: u.id }} sp={sp} basePath={`/univers/${u.slug}`} /></Suspense>
      </div>

      {/* Other universes — keep discovery flowing */}
      {others.length > 0 && (
        <div className="border-t border-stone bg-cream">
          <div className="container-lux flex flex-wrap gap-x-10 gap-y-4 py-8">
            <p className="mr-2 flex items-center text-[10px] font-bold uppercase tracking-[0.2em] text-muted">Autres univers</p>
            {others.map((o) => <Link key={o.id} href={`/univers/${o.slug}`} className="flex items-center gap-2 font-display text-lg text-charcoal transition-colors hover:text-champagne-2"><span className="text-xs italic text-muted-2">→</span>{o.name}</Link>)}
          </div>
        </div>
      )}
    </>
  );
}
