import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/ui/primitives";
import { PackageIcon, RefreshIcon, StoreIcon, TruckIcon } from "@/components/icons";
import { formatDTShort, EXPRESS_SHIPPING_FEE, FREE_SHIPPING_THRESHOLD, STANDARD_SHIPPING_FEE } from "@/lib/money";
export const metadata: Metadata = { title: "Livraison & retours" };
export default function LivraisonPage() {
  const rows = [
    { i: <TruckIcon size={22} />, t: "Livraison standard", d: `${formatDTShort(STANDARD_SHIPPING_FEE)} · offerte dès ${formatDTShort(FREE_SHIPPING_THRESHOLD)}. 24–48 h Grand Tunis, 48–72 h autres gouvernorats.` },
    { i: <PackageIcon size={22} />, t: "Livraison express", d: `${formatDTShort(EXPRESS_SHIPPING_FEE)} · sous 24 h sur le Grand Tunis pour toute commande passée avant 14 h.` },
    { i: <StoreIcon size={22} />, t: "Click & Collect", d: "Gratuit · prête sous 2 h à Ezzahra ou Hammam-Lif. Nous vous prévenons par téléphone." },
    { i: <RefreshIcon size={22} />, t: "Retours", d: "7 jours après réception pour tout produit non ouvert. Demande depuis votre compte, remboursement ou avoir sous 5 jours." },
  ];
  return (
    <div className="container-lux py-10 lg:py-14">
      <Breadcrumbs items={[{ label: "Livraison & retours" }]} />
      <header className="mt-6 mb-12 max-w-2xl"><p className="eyebrow mb-4">Livraison & retours</p><h1 className="font-display text-display-lg text-ink">Simple, rapide, partout en Tunisie</h1></header>
      <div className="grid gap-px bg-stone sm:grid-cols-2">{rows.map((r) => <div key={r.t} className="bg-paper p-8"><span className="text-champagne-2">{r.i}</span><h2 className="mt-5 text-[15px] text-ink">{r.t}</h2><p className="mt-2 text-sm leading-relaxed text-muted">{r.d}</p></div>)}</div>
    </div>
  );
}
