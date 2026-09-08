"use client";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { useCart } from "@/components/cart/cart-provider";
import { CheckIcon, HeartIcon, ShieldIcon, StoreIcon, TruckIcon } from "@/components/icons";
import { QtyStepper } from "@/components/ui/primitives";
import { useToast } from "@/components/ui/toaster";
import { formatDT, FREE_SHIPPING_THRESHOLD } from "@/lib/money";
import { EASE_LUXE } from "@/lib/motion";
import { toggleWishlistAction } from "@/actions/shop";

type P = { id: number; slug: string; name: string; brandName: string | null; image: string | null; priceMillimes: number; compareAtMillimes: number | null; stock: number; lowStockThreshold: number; volume: string | null };

export function BuyBox({ p, wished, isAuthed }: { p: P; wished: boolean; isAuthed: boolean }) {
  const cart = useCart();
  const { toast } = useToast();
  const router = useRouter();
  const reduce = useReducedMotion();
  const [qty, setQty] = useState(1);
  const [added, setAdded] = useState(false);
  const [w, setW] = useState(wished);
  const [pending, start] = useTransition();
  const out = p.stock <= 0;
  const low = !out && p.stock <= p.lowStockThreshold;

  const add = () => {
    cart.add({ productId: p.id, slug: p.slug, name: p.name, brandName: p.brandName, image: p.image, priceMillimes: p.priceMillimes, stock: p.stock, volume: p.volume }, qty);
    setAdded(true); setTimeout(() => setAdded(false), 1600);
    toast({ kind: "success", title: "Ajouté au panier", description: `${qty} × ${p.name}`, action: { label: "Voir le panier", onClick: cart.open } });
  };
  const wish = () => {
    if (!isAuthed) { router.push(`/connexion?next=/produit/${p.slug}`); return; }
    start(async () => { const r = await toggleWishlistAction(p.id); if (r.ok) { setW(r.data.wished); toast({ kind: "success", title: r.message ?? "" }); } else toast({ kind: "error", title: r.error }); });
  };

  return (
    <>
      <div className="space-y-5">
        {out ? <p className="text-sm text-muted">Ce produit est momentanément épuisé. Contactez nos boutiques pour être prévenu(e) du réassort.</p>
          : <div className="flex flex-wrap items-center gap-4"><QtyStepper value={qty} onChange={setQty} max={Math.min(20, p.stock)} />{low && <p className="text-xs text-warning">Plus que {p.stock} en stock</p>}{!low && <p className="text-xs text-success">En stock</p>}</div>}
        <div className="flex gap-3">
          <button onClick={add} disabled={out} className="btn-primary relative flex-1 overflow-hidden">
            <AnimatePresence mode="wait" initial={false}>
              {added ? <motion.span key="ok" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.4, ease: EASE_LUXE }} className="flex items-center gap-2"><CheckIcon size={16} /> Ajouté au panier</motion.span>
                : <motion.span key="add" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex items-center gap-2">{out ? "Épuisé" : `Ajouter · ${formatDT(p.priceMillimes * qty)}`}</motion.span>}
            </AnimatePresence>
          </button>
          <button onClick={wish} disabled={pending} aria-pressed={w} aria-label={w ? "Retirer des favoris" : "Ajouter aux favoris"} className={`flex h-12 w-12 shrink-0 items-center justify-center border transition-colors ${w ? "border-champagne text-champagne-2" : "border-ink text-ink hover:bg-ink hover:text-paper"}`}>
            <motion.span animate={w && !reduce ? { scale: [1, 1.2, 1] } : {}} transition={{ duration: 0.5, ease: EASE_LUXE }} className="flex"><HeartIcon size={18} filled={w} /></motion.span>
          </button>
        </div>
        <ul className="space-y-2.5 border-t border-stone pt-5 text-sm text-charcoal">
          <li className="flex items-center gap-3"><TruckIcon size={16} className="text-champagne-2" /> Livraison 24–72 h · offerte dès {formatDT(FREE_SHIPPING_THRESHOLD)}</li>
          <li className="flex items-center gap-3"><StoreIcon size={16} className="text-champagne-2" /> Retrait gratuit sous 2 h à Ezzahra ou Hammam-Lif</li>
          <li className="flex items-center gap-3"><ShieldIcon size={16} className="text-champagne-2" /> Produit authentique, distribution officielle</li>
        </ul>
      </div>
      {/* Sticky mobile bar */}
      <div className="fixed inset-x-0 bottom-0 z-30 flex items-center gap-3 border-t border-stone bg-paper/95 px-4 py-3 backdrop-blur-xl lg:hidden" style={{ paddingBottom: "max(0.75rem, env(safe-area-inset-bottom))" }}>
        <div className="min-w-0 flex-1"><p className="truncate text-xs text-muted">{p.name}</p><p className="text-sm font-medium tabular-nums text-ink">{formatDT(p.priceMillimes * qty)}</p></div>
        <button onClick={add} disabled={out} className="btn-primary px-6">{added ? <CheckIcon size={16} /> : out ? "Épuisé" : "Ajouter"}</button>
      </div>
    </>
  );
}
