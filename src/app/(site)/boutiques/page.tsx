import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { eq } from "drizzle-orm";
import { db } from "@/db";
import { stores } from "@/db/schema";
import { ClockIcon, ExternalIcon, MapPinIcon, PhoneIcon, StoreIcon, TruckIcon, ChatIcon } from "@/components/icons";
import { SITE_URL } from "@/lib/env";
export const metadata: Metadata = { title: "Nos boutiques", description: "Parapharmacie Cléopâtre à Ezzahra et Hammam-Lif : adresses, horaires, téléphone, retrait de commande." };
export const dynamic = "force-dynamic";
export default async function BoutiquesPage() {
  const list = await db.select().from(stores).where(eq(stores.isActive, true));
  const ld = { "@context": "https://schema.org", "@type": "Organization", name: "Cléopâtre — Espace Santé Beauté", url: SITE_URL, location: list.map((s) => ({ "@type": "Pharmacy", name: s.name, telephone: `+216${s.phone}`, address: { "@type": "PostalAddress", streetAddress: s.address, addressLocality: s.city, addressCountry: "TN" }, openingHours: s.hours })) };
  return (
    <div className="border-b border-stone">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }} />
      {/* Intro */}
      <section className="grid lg:grid-cols-2">
        <div className="flex items-center bg-noir text-paper">
          <div className="container-lux py-14 lg:py-24 lg:pr-16">
            <p className="eyebrow mb-6 flex items-center gap-3 text-paper/55"><span className="font-display text-lg italic text-champagne-3">La maison</span> Deux adresses</p>
            <h1 className="font-display text-display-lg">Venez rencontrer <em className="text-champagne-3">vos pharmaciens</em></h1>
            <p className="mt-6 max-w-lg text-[15px] leading-relaxed text-paper/70">Au cœur d&apos;Ezzahra et de Hammam-Lif, nos équipes vous reçoivent pour un conseil personnalisé — analyse de besoin, choix d&apos;actifs, retrait de votre commande en ligne sous deux heures.</p>
            <ul className="mt-9 flex flex-wrap gap-x-8 gap-y-3 text-[11px] font-bold uppercase tracking-[0.18em] text-paper/60">
              <li className="flex items-center gap-2"><TruckIcon size={14} className="text-champagne-3" /> Livraison depuis nos boutiques</li>
              <li className="flex items-center gap-2"><StoreIcon size={14} className="text-champagne-3" /> Retrait 2 h</li>
            </ul>
          </div>
        </div>
        <div className="relative min-h-72 lg:min-h-[480px]">
          <Image src="/images/maison.jpg" alt="Intérieur de la parapharmacie Cléopâtre" fill priority sizes="(max-width:1024px) 100vw, 50vw" className="object-cover" />
        </div>
      </section>

      {/* Store cards */}
      <section className="container-lux grid gap-px border-b border-stone bg-stone py-14 md:grid-cols-2 lg:py-20">
        {list.map((s, i) => (
          <div key={s.id} className="bg-paper p-8 lg:p-12">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-baseline gap-4">
                <span className="font-display text-lg italic text-champagne-2">{String(i + 1).padStart(2, "0")}</span>
                <h2 className="font-display text-display-sm text-ink">{s.name.replace("Cléopâtre ", "")}</h2>
              </div>
              <MapPinIcon size={20} className="shrink-0 text-champagne-2" />
            </div>
            <dl className="mt-9 space-y-5 border-t border-stone pt-7 text-sm">
              <div className="grid grid-cols-[24px_1fr] gap-3">
                <dt className="sr-only">Adresse</dt>
                <MapPinIcon size={16} className="mt-0.5 text-muted" />
                <dd className="leading-relaxed text-charcoal">{s.address}<br />{s.city}, Tunisie</dd>
              </div>
              <div className="grid grid-cols-[24px_1fr] gap-3">
                <dt className="sr-only">Horaires</dt>
                <ClockIcon size={16} className="mt-0.5 text-muted" />
                <dd className="leading-relaxed text-charcoal">{s.hours}</dd>
              </div>
              <div className="grid grid-cols-[24px_1fr] gap-3">
                <dt className="sr-only">Téléphone</dt>
                <PhoneIcon size={16} className="mt-0.5 text-muted" />
                <dd><a href={`tel:+216${s.phone}`} className="text-charcoal underline-offset-4 hover:text-ink hover:underline">{s.phone.replace(/(\d{2})(\d{3})(\d{3})/, "$1 $2 $3")}</a></dd>
              </div>
            </dl>
            <div className="mt-9 flex flex-wrap gap-3">
              <a href={`tel:+216${s.phone}`} className="btn-primary">Appeler la boutique</a>
              {s.mapsUrl && <a href={s.mapsUrl} target="_blank" rel="noopener noreferrer" className="btn-secondary">Itinéraire <ExternalIcon size={14} /></a>}
            </div>
          </div>
        ))}
      </section>

      {/* Services */}
      <section className="bg-cream">
        <div className="container-lux grid gap-px bg-stone py-14 sm:grid-cols-2 lg:grid-cols-3 lg:py-20">
          {[
            { i: ChatIcon, t: "Conseil sans rendez-vous", d: "Un doute sur une routine ? Passez nous voir : l'analyse est gratuite et sans engagement." },
            { i: StoreIcon, t: "Click & collect en 2 h", d: "Commandez sur le site et choisissez « retrait en boutique » : c'est prêt en deux heures." },
            { i: TruckIcon, t: "Livraison depuis le Grand Tunis", d: "Nos boutiques préparent et expédient vos commandes partout en Tunisie, 24–72 h." },
          ].map((x) => (
            <div key={x.t} className="bg-cream px-8 py-10">
              <x.i size={22} className="text-champagne-2" />
              <h2 className="mt-5 font-display text-xl text-ink">{x.t}</h2>
              <p className="mt-2 text-sm leading-relaxed text-muted">{x.d}</p>
            </div>
          ))}
        </div>
        <div className="container-lux flex flex-col items-center gap-6 pb-14 text-center">
          <p className="max-w-md text-sm text-muted">Une question avant de vous déplacer&nbsp;? Nos équipes répondent au téléphone pendant les horaires d&apos;ouverture.</p>
          <Link href="/aide" className="btn-secondary">Consulter l&apos;aide &amp; FAQ</Link>
        </div>
      </section>
    </div>
  );
}
