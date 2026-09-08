"use client";
import Link from "next/link";
import { useActionState } from "react";
import { ArrowRightIcon, BankIcon, CardIcon, CashIcon, LogoMark, MailIcon, MapPinIcon, PhoneIcon, ShieldIcon, TruckIcon } from "@/components/icons";
import { subscribeNewsletterAction } from "@/actions/shop";
import type { Store } from "@/db/schema";

export function Footer({ universes, stores }: { universes: { slug: string; name: string }[]; stores: Store[] }) {
  const [state, action, pending] = useActionState(subscribeNewsletterAction, null);
  return (
    <footer className="bg-noir text-paper">
      {/* Statement band */}
      <div className="border-b border-paper/10">
        <div className="container-lux flex flex-col gap-10 py-16 lg:flex-row lg:items-end lg:justify-between lg:py-20">
          <div className="max-w-3xl">
            <p className="eyebrow mb-6 text-paper/50">La maison Cléopâtre</p>
            <p className="font-display text-display-md italic leading-tight text-paper sm:text-display-lg">
              La santé de la peau mérite une maison.
            </p>
          </div>
          <p className="max-w-sm text-sm leading-relaxed text-paper/60 lg:pb-2">
            Depuis Ezzahra et Hammam-Lif, nos pharmaciennes et pharmaciens sélectionnent chaque référence — authentique,
            tolérante, utile — et vous la livrent partout en Tunisie.
          </p>
        </div>
      </div>

      <div className="container-lux grid gap-14 py-16 lg:grid-cols-12 lg:gap-10">
        {/* Brand + newsletter */}
        <div className="lg:col-span-4">
          <div className="flex items-center gap-3">
            <LogoMark size={32} className="text-champagne-3" />
            <span className="flex flex-col leading-none">
              <span className="font-display text-[26px] font-medium tracking-[0.01em]">Cléopâtre</span>
              <span className="mt-1 text-[8px] font-bold uppercase tracking-[0.34em] text-paper/45">Espace Santé Beauté</span>
            </span>
          </div>
          <p className="mt-6 text-sm leading-relaxed text-paper/60">Parapharmacie premium fondée à Ezzahra. Une sélection resserrée,
            un conseil de pharmacien, aucune promesse excessive.</p>

          <form action={action} className="mt-9 max-w-sm" aria-label="Inscription au Journal">
            <label htmlFor="nl" className="eyebrow mb-4 block text-champagne-3">Le Journal, chaque mois</label>
            <div className="flex border-b border-paper/30 transition-colors focus-within:border-champagne-3">
              <input id="nl" name="email" type="email" required placeholder="Votre adresse e-mail" className="min-h-12 w-full bg-transparent text-sm text-paper placeholder:text-paper/35 focus:outline-none" />
              <button disabled={pending} aria-label="S'inscrire à la newsletter" className="flex shrink-0 items-center gap-2 px-2 text-[11px] font-bold uppercase tracking-[0.18em] text-champagne-3 transition-opacity hover:opacity-70 disabled:opacity-40">
                {pending ? "…" : "S'inscrire"} <ArrowRightIcon size={13} />
              </button>
            </div>
            {state && <p className={`mt-2 text-xs ${state.ok ? "text-success-soft" : "text-error-soft"}`} role="status">{state.ok ? state.message : state.error}</p>}
          </form>
        </div>

        {/* Link columns */}
        <div className="grid grid-cols-2 gap-10 sm:grid-cols-3 lg:col-span-8">
          <div>
            <p className="eyebrow mb-6 text-paper/45">Univers</p>
            <ul className="space-y-3.5 text-sm">
              {universes.map((u) => <li key={u.slug}><Link href={`/univers/${u.slug}`} className="text-paper/80 transition-colors hover:text-champagne-3">{u.name}</Link></li>)}
              <li><Link href="/marques" className="text-paper/80 transition-colors hover:text-champagne-3">Toutes les marques</Link></li>
            </ul>
          </div>
          <div>
            <p className="eyebrow mb-6 text-paper/45">La maison</p>
            <ul className="space-y-3.5 text-sm">
              {[["/promotions", "Offres du moment"], ["/journal", "Le Journal"], ["/boutiques", "Nos boutiques"], ["/aide", "Aide & FAQ"], ["/suivi", "Suivre ma commande"], ["/livraison", "Livraison & retours"]].map(([h, l]) => (
                <li key={h}><Link href={h} className="text-paper/80 transition-colors hover:text-champagne-3">{l}</Link></li>
              ))}
            </ul>
          </div>
          <div className="col-span-2 sm:col-span-1">
            <p className="eyebrow mb-6 text-paper/45">Nos boutiques</p>
            <ul className="space-y-6 text-sm">
              {stores.map((s) => (
                <li key={s.id}>
                  <p className="font-medium text-paper">{s.name}</p>
                  <p className="mt-1 text-paper/55"><MapPinIcon size={12} className="mr-1.5 inline text-champagne-3" />{s.address} · {s.city}</p>
                  <p className="mt-1 text-xs text-paper/40">{s.hours}</p>
                  <a href={`tel:+216${s.phone}`} className="mt-2 inline-flex min-h-10 items-center gap-2 text-paper/80 hover:text-champagne-3"><PhoneIcon size={13} className="text-champagne-3" /> {s.phone.replace(/(\d{2})(\d{3})(\d{3})/, "$1 $2 $3")}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Legal */}
      <div className="border-t border-paper/10">
        <div className="container-lux flex flex-col gap-6 py-7 text-xs text-paper/45 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
            <span className="inline-flex items-center gap-2"><ShieldIcon size={14} className="text-champagne-3" /> Produits authentiques</span>
            <span className="inline-flex items-center gap-2"><TruckIcon size={14} className="text-champagne-3" /> Livraison 24–72 h</span>
            <span className="inline-flex items-center gap-2"><CashIcon size={14} className="text-champagne-3" /> Paiement à la livraison</span>
            <span className="inline-flex items-center gap-2"><BankIcon size={14} className="text-champagne-3" /> Virement</span>
            <span className="inline-flex items-center gap-2"><CardIcon size={14} className="text-champagne-3" /> Carte — bientôt</span>
          </div>
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
            <Link href="/cgv" className="transition-colors hover:text-champagne-3">CGV</Link>
            <Link href="/confidentialite" className="transition-colors hover:text-champagne-3">Confidentialité</Link>
            <Link href="/journal" className="transition-colors hover:text-champagne-3">Journal</Link>
            <span>© {new Date().getFullYear()} Cléopâtre — Espace Santé Beauté</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
