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
  return c ? { title: `${c.name}`, description: c.description ?? undefined, openGraph: { images: c.image ? [c.image] : [] } } : {};
}
export default async function CategoriePage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<SP> }) {
  const [{ slug }, sp] = await Promise.all([params, searchParams]);
  const [c, unis] = await Promise.all([getCategoryBySlug(slug), getUniverses()]);
  if (!c || c.isUniverse) notFound();
  const siblings = unis.find((x) => x.slug === c.parent?.slug)?.children ?? [];
  return (
    <>
      <PageIntro
        kicker={c.parent?.name ?? "Catégorie"}
        title={<>{c.name} <em className="text-champagne-2">· sélection</em></>}
        intro={c.description}
        breadcrumbs={[...(c.parent ? [{ href: `/univers/${c.parent.slug}`, label: c.parent.name }] : []), { label: c.name }]}
        className="py-10 lg:py-14"
      >
        {siblings.length > 0 && (
          <div className="mt-10 flex flex-wrap items-center gap-x-7 gap-y-3 border-t border-stone pt-6">
            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted">Dans {c.parent?.name}</span>
            {siblings.map((s) => (
              s.slug === c.slug
                ? <span key={s.id} className="border-b border-champagne pb-1 text-sm text-champagne-2" aria-current="page">{s.name}</span>
                : <Link key={s.id} href={`/categorie/${s.slug}`} className="group flex items-center gap-2 text-sm text-charcoal transition-colors hover:text-ink"><span className="text-xs text-muted-2 opacity-0 transition-opacity group-hover:opacity-100">→</span>{s.name}</Link>
            ))}
          </div>
        )}
      </PageIntro>
      <div className="container-lux py-10 lg:py-14">
        <Suspense fallback={<ProductGridSkeleton />}><Listing base={{ categoryId: c.id }} sp={sp} basePath={`/categorie/${c.slug}`} /></Suspense>
      </div>
      <div className="container-lux pb-14">
        <div className="flex flex-wrap items-center justify-between gap-4 border-t border-stone pt-8">
          {c.parent && <Link href={`/univers/${c.parent.slug}`} className="btn-ghost"><ArrowRightIcon size={14} className="rotate-180" /> Retour à {c.parent.name}</Link>}
          <Link href="/besoin/peau-sensible" className="text-sm text-muted underline-offset-4 hover:text-ink hover:underline">Un doute sur votre peau ? Parlez-en à un pharmacien</Link>
        </div>
      </div>
    </>
  );
}
