import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { desc, eq } from "drizzle-orm";
import { db } from "@/db";
import { articles } from "@/db/schema";
import { PageIntro } from "@/components/shell/page-intro";
import { Stagger, StaggerItem } from "@/components/motion/reveal";
import { formatDate } from "@/lib/utils";
import { ArrowRightIcon } from "@/components/icons";
export const metadata: Metadata = { title: "Le Journal", description: "Conseils de pharmaciens : routines, actifs, protection solaire, compléments — sans jargon ni promesses." };
export const dynamic = "force-dynamic";
export default async function JournalPage() {
  const list = await db.select().from(articles).where(eq(articles.isPublished, true)).orderBy(desc(articles.publishedAt));
  const [lead, ...rest] = list;
  return (
    <div className="border-b border-stone">
      <PageIntro
        index="Le Journal"
        kicker="Éditorial Cléopâtre"
        title={<>Comprendre, <em className="text-champagne-2">avant d&apos;acheter</em></>}
        intro="Des articles courts, écrits par notre équipe pharmaceutique : comment choisir, doser, appliquer — sans jargon et sans promesses excessives."
      />

      {/* Featured story */}
      {lead && (
        <section className="border-t border-stone bg-cream">
          <div className="container-lux py-14 lg:py-20">
            <Link href={`/journal/${lead.slug}`} className="group grid gap-8 lg:grid-cols-12 lg:items-center">
              <div className="frame relative aspect-[16/10] lg:col-span-7 lg:aspect-[16/9]">
                {lead.image && <Image src={lead.image} alt="" fill priority sizes="(max-width:1024px) 100vw, 58vw" className="object-cover transition-transform duration-[1600ms] ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:scale-[1.03]" />}
              </div>
              <div className="lg:col-span-5 lg:pl-6">
                <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-muted">{lead.tag} · {lead.readMinutes} min · {formatDate(lead.publishedAt)}</p>
                <h2 className="mt-4 font-display text-display-md text-ink transition-colors duration-500 group-hover:text-champagne-2 sm:text-display-lg">{lead.title}</h2>
                <p className="mt-4 line-clamp-3 max-w-md text-[15px] leading-relaxed text-muted">{lead.excerpt}</p>
                <span className="btn-ghost mt-8">Lire l&apos;article <ArrowRightIcon size={14} /></span>
              </div>
            </Link>
          </div>
        </section>
      )}

      {/* Archive */}
      <section className="container-lux py-14 lg:py-20">
        <p className="eyebrow mb-10">Tous les articles</p>
        <div className="grid gap-x-12 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
          {rest.map((a, i) => (
            <Link key={a.id} href={`/journal/${a.slug}`} className="group flex flex-col">
              <div className="relative aspect-[4/3] overflow-hidden bg-stone">
                {a.image && <Image src={a.image} alt="" fill sizes="(max-width:768px) 100vw, 33vw" className="object-cover transition-transform duration-[1400ms] ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:scale-[1.05]" />}
                <span className="absolute left-4 top-4 bg-paper/95 px-2 py-1 font-display text-sm italic text-champagne-2">{String(i + 2).padStart(2, "0")}</span>
              </div>
              <p className="mt-5 text-[9px] font-bold uppercase tracking-[0.2em] text-muted">{a.tag} · {a.readMinutes} min · {formatDate(a.publishedAt)}</p>
              <h2 className="mt-2 font-display text-display-sm text-ink transition-colors duration-500 group-hover:text-champagne-2">{a.title}</h2>
              <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-muted">{a.excerpt}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
