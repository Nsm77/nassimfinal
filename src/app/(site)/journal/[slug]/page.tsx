import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { and, desc, eq, ne } from "drizzle-orm";
import { db } from "@/db";
import { articles } from "@/db/schema";
import { formatDate } from "@/lib/utils";
import { SITE_URL } from "@/lib/env";
import { ArrowLeftIcon, ArrowRightIcon } from "@/components/icons";
export const dynamic = "force-dynamic";
async function get(slug: string) { return db.query.articles.findFirst({ where: and(eq(articles.slug, slug), eq(articles.isPublished, true)) }); }
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const a = await get((await params).slug);
  return a ? { title: a.title, description: a.excerpt ?? undefined, openGraph: { type: "article", title: a.title, description: a.excerpt ?? undefined, images: a.image ? [a.image] : [], publishedTime: a.publishedAt.toISOString() }, twitter: { card: "summary_large_image" } } : {};
}
export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const a = await get((await params).slug);
  if (!a) notFound();
  const others = await db.select().from(articles).where(and(eq(articles.isPublished, true), ne(articles.id, a.id))).orderBy(desc(articles.publishedAt)).limit(2);
  const ld = { "@context": "https://schema.org", "@type": "Article", headline: a.title, image: a.image ? [`${SITE_URL}${a.image}`] : [], datePublished: a.publishedAt.toISOString(), author: { "@type": "Organization", name: "Cléopâtre — Espace Santé Beauté" } };
  return (
    <article>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }} />
      <div className="bg-noir text-paper">
        <div className="container-lux py-12 lg:py-16">
          <Link href="/journal" className="inline-flex min-h-10 items-center gap-2 text-[11px] font-bold uppercase tracking-[0.18em] text-paper/60 transition-colors hover:text-champagne-3"><ArrowLeftIcon size={13} /> Le Journal</Link>
          <div className="mx-auto mt-10 max-w-3xl text-center">
            <p className="eyebrow mb-6 text-paper/55">{a.tag} · {a.readMinutes} min de lecture</p>
            <h1 className="font-display text-display-md leading-tight sm:text-display-lg">{a.title}</h1>
            <p className="mx-auto mt-6 max-w-xl text-[15px] italic leading-relaxed text-paper/65">{a.excerpt}</p>
            <p className="mt-6 text-[10px] font-bold uppercase tracking-[0.2em] text-paper/40">{formatDate(a.publishedAt)} — L&apos;équipe Cléopâtre</p>
          </div>
        </div>
      </div>

      {a.image && (
        <div className="relative mx-auto aspect-[21/9] w-full max-w-6xl overflow-hidden bg-stone lg:-mt-10">
          <Image src={a.image} alt="" fill priority sizes="(max-width:1280px) 100vw, 1024px" className="object-cover" />
        </div>
      )}

      <div className="container-lux py-14 lg:py-20">
        <div className="mx-auto max-w-2xl">
          {a.body.split("\n\n").map((p, i) => (
            <p key={i} className={`font-display ${i === 0 ? "first-para text-xl leading-[1.75] text-ink sm:text-[1.35rem]" : "mt-7 text-[1.125rem] leading-[1.85] text-charcoal"}`}>{p}</p>
          ))}
          <div className="mt-14 flex items-center gap-5 border-t border-stone pt-8">
            <span className="h-px w-10 bg-champagne" />
            <p className="text-xs leading-relaxed text-muted">Cet article est donné à titre informatif. En cas de doute sur votre peau ou votre santé, nos pharmaciens vous reçoivent à Ezzahra et Hammam-Lif, sans rendez-vous.</p>
          </div>
        </div>
      </div>

      {/* À lire ensuite */}
      {others.length > 0 && (
        <div className="border-t border-stone bg-cream">
          <div className="container-lux py-14">
            <p className="eyebrow mb-8">À lire ensuite</p>
            <div className="grid gap-10 sm:grid-cols-2">
              {others.map((o) => (
                <Link key={o.id} href={`/journal/${o.slug}`} className="group flex items-center gap-6 border-t border-stone pt-6">
                  <div className="relative h-24 w-24 shrink-0 overflow-hidden bg-stone">
                    {o.image && <Image src={o.image} alt="" fill sizes="96px" className="object-cover transition-transform duration-[1200ms] group-hover:scale-[1.06]" />}
                  </div>
                  <div className="min-w-0">
                    <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-muted">{o.tag} · {o.readMinutes} min</p>
                    <p className="mt-1.5 font-display text-xl text-ink transition-colors group-hover:text-champagne-2">{o.title}</p>
                  </div>
                  <ArrowRightIcon size={16} className="ml-auto shrink-0 text-sand-2 transition-transform duration-500 group-hover:translate-x-1 group-hover:text-ink" />
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </article>
  );
}
