import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import { LogoMark, ShieldIcon, StoreIcon, TruckIcon } from "@/components/icons";

/* Split-screen authentication — maison on the left, form on the right. */
export function AuthShell({ title, kicker, children }: { title: ReactNode; kicker: string; children: ReactNode }) {
  return (
    <div className="grid min-h-dvh lg:grid-cols-2">
      {/* Editorial panel */}
      <div className="relative hidden overflow-hidden bg-noir text-paper lg:block">
        <Image src="/images/atelier.jpg" alt="" fill priority sizes="50vw" className="object-cover opacity-70" />
        <div className="absolute inset-0 bg-gradient-to-t from-noir via-noir/40 to-noir/30" />
        <div className="relative flex h-full flex-col justify-between p-12 xl:p-16">
          <Link href="/" className="flex items-center gap-3 text-paper">
            <LogoMark size={32} className="text-champagne-3" />
            <span className="flex flex-col leading-none">
              <span className="font-display text-2xl">Cléopâtre</span>
              <span className="mt-1 text-[8px] font-bold uppercase tracking-[0.34em] text-paper/50">Espace Santé Beauté</span>
            </span>
          </Link>
          <div className="max-w-md">
            <p className="eyebrow mb-6 text-champagne-3">L&apos;espace client</p>
            <p className="font-display text-display-md italic leading-tight">Vos commandes,<br />votre fidélité,<br />votre routine — réunis.</p>
            <ul className="mt-10 space-y-4 text-sm text-paper/70">
              <li className="flex items-center gap-3"><TruckIcon size={16} className="shrink-0 text-champagne-3" /> Suivi de commande 24–72 h partout en Tunisie</li>
              <li className="flex items-center gap-3"><StoreIcon size={16} className="shrink-0 text-champagne-3" /> Retrait 2 h à Ezzahra ou Hammam-Lif</li>
              <li className="flex items-center gap-3"><ShieldIcon size={16} className="shrink-0 text-champagne-3" /> Produits authentiques, conseil de pharmacien</li>
            </ul>
          </div>
          <p className="text-xs text-paper/40">© {new Date().getFullYear()} Cléopâtre — Espace Santé Beauté</p>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center bg-paper px-5 py-14 sm:px-10">
        <div className="w-full max-w-md">
          <div className="mb-8 lg:hidden">
            <Link href="/" className="flex items-center gap-3 text-ink"><LogoMark size={28} className="text-champagne-2" /><span className="font-display text-xl">Cléopâtre</span></Link>
          </div>
          <p className="eyebrow mb-4">{kicker}</p>
          <h1 className="font-display text-display-md text-ink">{title}</h1>
          <div className="mt-9">{children}</div>
        </div>
      </div>
    </div>
  );
}
