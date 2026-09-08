import type { Metadata } from "next";
import Link from "next/link";
import { eq } from "drizzle-orm";
import { db } from "@/db";
import { brands } from "@/db/schema";
import { getBrands } from "@/lib/catalog";
import { PageIntro } from "@/components/shell/page-intro";
import { ArrowRightIcon } from "@/components/icons";
export const metadata: Metadata = { title: "Nos marques", description: "Laboratoires dermatologiques et maisons de soin disponibles chez Cléopâtre, Ezzahra et Hammam-Lif." };
export const dynamic = "force-dynamic";
export default async function MarquesPage() {
  const [list, featured] = await Promise.all([getBrands(), db.select().from(brands).where(eq(brands.isFeatured, true))]);
  const featuredIds = new Set(featured.map((f) => f.id));
  const rest = list.filter((b) => !featuredIds.has(b.id));
  const groups = rest.reduce<Record<string, typeof rest>>((a, b) => { const k = b.name[0].toUpperCase(); (a[k] ??= []).push(b); return a; }, {});
  return (
    <div className="border-b border-stone">
      <PageIntro
        index={`${list.length} maisons`}
        kicker="Nos marques"
        title={<>Des maisons qui <em className="text-champagne-2">engagent</em> leur nom</>}
        intro="Laboratoires dermatologiques européens et maisons de soin, distribués officiellement en Tunisie. Nous travaillons exclusivement avec des acteurs dont nous pouvons défendre les formules."
      />

      {/* Featured maisons */}
      <section className="border-t border-stone bg-cream">
        <div className="container-lux py-12 lg:py-16">
          <p className="eyebrow mb-8">Maisons invitées en boutique</p>
          <div className="grid gap-px border border-stone bg-stone sm:grid-cols-2 lg:grid-cols-3">
            {featured.map((b, i) => (
              <Link key={b.id} href={`/marque/${b.slug}`} className="group flex min-h-56 flex-col justify-between bg-cream p-7 transition-colors duration-500 hover:bg-paper lg:min-h-64 lg:p-9">
                <div className="flex items-baseline justify-between">
                  <span className="font-display text-2xl leading-tight text-ink transition-colors duration-500 group-hover:text-champagne-2 lg:text-[1.7rem]">{b.name}</span>
                  <span className="font-display text-xs italic text-muted-2">{String(i + 1).padStart(2, "0")}</span>
                </div>
                <div>
                  <p className="mb-4 line-clamp-3 max-w-sm text-xs leading-relaxed text-muted">{b.story}</p>
                  <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.2em] text-muted-2"><span className="text-champagne-2">{b.country}</span><span className="h-px w-6 bg-stone-2" /> Découvrir <ArrowRightIcon size={11} className="transition-transform duration-500 group-hover:translate-x-1" /></p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Répertoire A–Z */}
      <section className="container-lux py-14 lg:py-20">
        <p className="eyebrow mb-8">Le répertoire complet</p>
        <div className="grid gap-x-12 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(groups).sort().map(([l, bs]) => (
            <div key={l}>
              <p className="border-b border-stone pb-3 font-display text-3xl italic text-champagne-2">{l}</p>
              <ul className="mt-2">
                {bs.map((b) => (
                  <li key={b.id}>
                    <Link href={`/marque/${b.slug}`} className="group flex items-baseline justify-between gap-3 border-b border-stone/50 py-3">
                      <span className="text-[15px] text-charcoal transition-colors group-hover:text-ink">{b.name}</span>
                      <span className="shrink-0 text-[10px] uppercase tracking-[0.14em] text-muted-2">{b.country}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
