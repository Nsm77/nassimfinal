"use client";
import Image from "next/image";
import Link from "next/link";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { useCart } from "@/components/cart/cart-provider";
import { CheckIcon, HeartIcon, PlusIcon } from "@/components/icons";
import { Badge } from "@/components/ui/primitives";
import { Stars } from "@/components/ui/stars";
import { useToast } from "@/components/ui/toaster";
import type { ProductCard as PC } from "@/lib/catalog";
import { discountPercent, formatDT } from "@/lib/money";
import { EASE_LUXE } from "@/lib/motion";
import { toggleWishlistAction } from "@/actions/shop";
import { cn } from "@/lib/utils";

export function ProductCard({ p, wished = false, priority = false, isAuthed = false }: { p: PC; wished?: boolean; priority?: boolean; isAuthed?: boolean }) {
  const cart = useCart();
  const { toast } = useToast();
  const router = useRouter();
  const reduce = useReducedMotion();
  const [added, setAdded] = useState(false);
  const [w, setW] = useState(wished);
  const [pending, start] = useTransition();
  const pct = discountPercent(p.priceMillimes, p.compareAtMillimes);
  const out = p.stock <= 0;
  const low = !out && p.stock <= p.lowStockThreshold;

  const quickAdd = () => {
    if (out) return;
    cart.add({ productId: p.id, slug: p.slug, name: p.name, brandName: p.brandName, image: p.image, priceMillimes: p.priceMillimes, stock: p.stock, volume: p.volume });
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
    toast({ kind: "success", title: "Ajouté au panier", description: p.name, action: { label: "Voir le panier", onClick: cart.open } });
  };
  const wish = () => {
    if (!isAuthed) { router.push("/connexion?next=" + encodeURIComponent(window.location.pathname)); return; }
    start(async () => {
      const r = await toggleWishlistAction(p.id);
      if (r.ok) { setW(r.data.wished); toast({ kind: "success", title: r.message ?? "" }); } else toast({ kind: "error", title: r.error });
    });
  };

  return (
    <motion.article whileHover={reduce ? undefined : { y: -4 }} transition={{ duration: 0.5, ease: EASE_LUXE }} className="group relative flex h-full flex-col">
      <div className="relative aspect-square overflow-hidden bg-cream">
        <Link href={`/produit/${p.slug}`} aria-label={p.name} tabIndex={-1} className="absolute inset-0">
          {p.image && (
            <Image
              src={p.image}
              alt={p.name}
              fill
              priority={priority}
              sizes="(max-width: 768px) 50vw, (max-width: 1280px) 33vw, 25vw"
              className={cn("object-cover transition-transform duration-[1400ms] ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:scale-[1.04]", out && "opacity-90 saturate-[0.85]")}
            />
          )}
        </Link>
        {out && (
          <span className="pointer-events-none absolute bottom-3 left-3 z-10 border border-ink/15 bg-paper/90 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.22em] text-ink/80 backdrop-blur-sm">Épuisé</span>
        )}
        <div className="pointer-events-none absolute left-3 top-3 z-10 flex flex-col items-start gap-1.5">
          {pct > 0 && <Badge tone="ink">-{pct} %</Badge>}
          {p.isNew && !pct && <Badge tone="accent">Nouveau</Badge>}
        </div>
        <button
          onClick={wish}
          disabled={pending}
          aria-pressed={w}
          aria-label={w ? `Retirer ${p.name} des favoris` : `Ajouter ${p.name} aux favoris`}
          className={cn("absolute right-4 top-4 z-10 flex h-9 w-9 items-center justify-center rounded-full bg-paper/85 backdrop-blur-sm transition-colors duration-300", w ? "text-champagne-2" : "text-ink/60 hover:text-ink")}
        >
          <motion.span animate={w && !reduce ? { scale: [1, 1.22, 1] } : {}} transition={{ duration: 0.55, ease: EASE_LUXE }} className="flex drop-shadow-[0_1px_2px_rgba(255,255,255,0.6)]"><HeartIcon size={18} filled={w} /></motion.span>
        </button>
        {!out && (
          <div className="absolute inset-x-3 bottom-3 z-10">
            <button
              onClick={quickAdd}
              aria-label={`Ajouter ${p.name} au panier`}
              className="flex h-11 w-full items-center justify-center gap-2 bg-paper/95 text-[10px] font-bold uppercase tracking-[0.2em] text-ink backdrop-blur transition-all duration-500 md:translate-y-2 md:opacity-0 md:group-hover:translate-y-0 md:group-hover:opacity-100 md:group-focus-within:opacity-100"
            >
              <AnimatePresence mode="wait" initial={false}>
                {added ? (
                  <motion.span key="ok" initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="flex items-center gap-2 text-success"><CheckIcon size={14} /> Ajouté</motion.span>
                ) : (
                  <motion.span key="add" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex items-center gap-2"><PlusIcon size={13} /> Ajout rapide</motion.span>
                )}
              </AnimatePresence>
            </button>
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col pt-5">
        <div className="flex items-center justify-between gap-3">
          {p.brandName ? <Link href={`/marque/${p.brandSlug}`} className="text-[9px] font-bold uppercase tracking-[0.2em] text-muted transition-colors hover:text-champagne-2">{p.brandName}</Link> : <span />}
          {p.volume && <span className="text-[10px] text-muted-2">{p.volume}</span>}
        </div>
        <h3 className="mt-2 text-[15px] leading-snug text-ink"><Link href={`/produit/${p.slug}`} className="line-clamp-2 underline-offset-4 hover:underline">{p.name}</Link></h3>
        <div className="mt-3 flex flex-1 items-end justify-between gap-2">
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-[15px] font-medium tabular-nums tracking-tight text-ink">{formatDT(p.priceMillimes)}</span>
              {pct > 0 && p.compareAtMillimes && <span className="text-xs tabular-nums text-muted-2 line-through">{formatDT(p.compareAtMillimes)}</span>}
            </div>
            {low && <p className="mt-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-warning">Plus que {p.stock} en stock</p>}
            {!low && !out && <p className="mt-1 text-[10px] text-muted-2">En stock · livré 24–72 h</p>}
          </div>
          {p.ratingCount > 0 && <Stars value={p.ratingAvg / 100} count={p.ratingCount} size={10} />}
        </div>
      </div>
    </motion.article>
  );
}

export function ProductGrid({ items, wishedIds = [], isAuthed = false, priorityCount = 4 }: { items: PC[]; wishedIds?: number[]; isAuthed?: boolean; priorityCount?: number }) {
  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-12 md:grid-cols-3 md:gap-x-6 lg:grid-cols-4">
      {items.map((p, i) => <ProductCard key={p.id} p={p} wished={wishedIds.includes(p.id)} isAuthed={isAuthed} priority={i < priorityCount} />)}
    </div>
  );
}
