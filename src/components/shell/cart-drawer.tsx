"use client";
import Image from "next/image";
import Link from "next/link";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";
import { useCart } from "@/components/cart/cart-provider";
import { BagIcon, CloseIcon, GiftIcon, TrashIcon, TruckIcon } from "@/components/icons";
import { QtyStepper } from "@/components/ui/primitives";
import { formatDT, FREE_SHIPPING_THRESHOLD, GIFT_WRAP_FEE, remainingForFreeShipping, shippingFor } from "@/lib/money";
import type { ProductCard } from "@/lib/catalog";
import { EASE_LUXE, tweenExit } from "@/lib/motion";

export function CartDrawer({ upsells }: { upsells: ProductCard[] }) {
  const cart = useCart();
  const reduce = useReducedMotion();
  const [confirmClear, setConfirmClear] = useState(false);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && cart.close();
    if (cart.isOpen) { window.addEventListener("keydown", onKey); document.body.style.overflow = "hidden"; }
    return () => { window.removeEventListener("keydown", onKey); document.body.style.overflow = ""; };
  }, [cart.isOpen, cart]);

  const remaining = remainingForFreeShipping(cart.subtotal);
  const progress = Math.min(100, (cart.subtotal / FREE_SHIPPING_THRESHOLD) * 100);
  const shipping = shippingFor(cart.subtotal);
  const wrap = cart.giftWrap ? GIFT_WRAP_FEE : 0;
  const suggestions = upsells.filter((u) => !cart.lines.some((l) => l.productId === u.id) && u.stock > 0).slice(0, 3);

  return (
    <AnimatePresence>
      {cart.isOpen && (
        <>
          <motion.button aria-label="Fermer le panier" initial={{ opacity: 0 }} animate={{ opacity: 1, transition: { duration: 0.5 } }} exit={{ opacity: 0, transition: tweenExit }} onClick={cart.close} className="fixed inset-0 z-50 bg-ink/30 backdrop-blur-sm" />
          <motion.aside
            role="dialog" aria-modal="true" aria-label="Votre panier"
            initial={reduce ? false : { x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 160, damping: 28, mass: 1 }}
            className="fixed inset-y-0 right-0 z-[60] flex w-full max-w-md flex-col bg-paper shadow-drawer"
            style={{ willChange: "transform" }}
          >
            <div className="flex h-16 items-center justify-between border-b border-stone px-5">
              <h2 className="font-display text-xl text-ink">Votre panier <span className="text-sm text-muted">({cart.count})</span></h2>
              <button onClick={cart.close} aria-label="Fermer" className="flex h-11 w-11 items-center justify-center text-ink"><CloseIcon /></button>
            </div>

            {cart.lines.length === 0 ? (
              <div className="flex flex-1 flex-col items-center justify-center px-8 text-center">
                <BagIcon size={36} className="mb-5 text-sand-2" />
                <p className="font-display text-display-sm text-ink">Votre panier est vide</p>
                <p className="mt-2 text-sm text-muted">Découvrez notre sélection de soins conseillés par nos pharmaciens.</p>
                <Link href="/boutique" onClick={cart.close} className="btn-primary mt-8">Découvrir la boutique</Link>
              </div>
            ) : (
              <>
                <div className="border-b border-stone px-5 py-4">
                  <div className="flex items-center gap-2 text-xs text-charcoal"><TruckIcon size={16} className="text-champagne-2" />{remaining > 0 ? <span>Plus que <strong className="text-ink">{formatDT(remaining)}</strong> pour la livraison offerte</span> : <span className="text-success">Livraison offerte</span>}</div>
                  <div className="mt-2.5 h-px w-full bg-stone"><motion.div className="h-px origin-left bg-champagne" initial={false} animate={{ scaleX: progress / 100 }} transition={{ duration: 0.9, ease: EASE_LUXE }} style={{ willChange: "transform" }} /></div>
                </div>

                <div className="flex-1 overflow-y-auto px-5">
                  <ul className="divide-y divide-stone">
                    <AnimatePresence initial={false}>
                      {cart.lines.map((l) => (
                        <motion.li key={l.productId} layout initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, transition: tweenExit }} className="flex gap-4 py-5">
                          <Link href={`/produit/${l.slug}`} onClick={cart.close} className="relative h-24 w-20 shrink-0 overflow-hidden bg-stone">{l.image && <Image src={l.image} alt="" fill sizes="80px" className="object-cover" />}</Link>
                          <div className="flex min-w-0 flex-1 flex-col">
                            <p className="text-[10px] uppercase tracking-[0.16em] text-muted">{l.brandName}</p>
                            <Link href={`/produit/${l.slug}`} onClick={cart.close} className="mt-0.5 line-clamp-2 text-sm text-ink">{l.name}</Link>
                            {l.volume && <p className="text-xs text-muted-2">{l.volume}</p>}
                            <div className="mt-auto flex items-center justify-between pt-3">
                              <QtyStepper size="sm" value={l.quantity} max={Math.min(20, l.stock)} onChange={(v) => cart.setQty(l.productId, v)} />
                              <span className="text-sm tabular-nums text-ink">{formatDT(l.priceMillimes * l.quantity)}</span>
                            </div>
                          </div>
                          <button onClick={() => cart.remove(l.productId)} aria-label={`Retirer ${l.name}`} className="flex h-11 w-8 items-start justify-center pt-1 text-muted-2 hover:text-error"><TrashIcon size={16} /></button>
                        </motion.li>
                      ))}
                    </AnimatePresence>
                  </ul>

                  {suggestions.length > 0 && (
                    <div className="border-t border-stone py-5">
                      <p className="eyebrow mb-3">Complétez votre routine</p>
                      <ul className="space-y-3">
                        {suggestions.map((s) => (
                          <li key={s.id} className="flex items-center gap-3">
                            <div className="relative h-14 w-12 shrink-0 overflow-hidden bg-stone">{s.image && <Image src={s.image} alt="" fill sizes="48px" className="object-cover" />}</div>
                            <div className="min-w-0 flex-1"><p className="truncate text-xs text-ink">{s.name}</p><p className="text-xs text-muted">{formatDT(s.priceMillimes)}</p></div>
                            <button onClick={() => cart.add({ productId: s.id, slug: s.slug, name: s.name, brandName: s.brandName, image: s.image, priceMillimes: s.priceMillimes, stock: s.stock, volume: s.volume })} className="min-h-11 border border-stone-2 px-3 text-[11px] uppercase tracking-[0.14em] text-ink hover:border-ink">Ajouter</button>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="space-y-4 border-t border-stone py-5">
                    <label className="flex min-h-11 cursor-pointer items-center justify-between gap-3 text-sm text-charcoal">
                      <span className="flex items-center gap-2"><GiftIcon size={16} className="text-champagne-2" /> Emballage cadeau <span className="text-muted">(+{formatDT(GIFT_WRAP_FEE)})</span></span>
                      <input type="checkbox" checked={cart.giftWrap} onChange={(e) => cart.setGiftWrap(e.target.checked)} className="h-4 w-4 accent-ink" />
                    </label>
                    <textarea value={cart.note} onChange={(e) => cart.setNote(e.target.value)} placeholder="Note pour la commande (facultatif)" rows={2} maxLength={500} className="field text-sm" aria-label="Note pour la commande" />
                  </div>
                </div>

                <div className="border-t border-stone bg-cream px-5 py-5">
                  <dl className="space-y-1.5 text-sm">
                    <div className="flex justify-between"><dt className="text-muted">Sous-total</dt><dd className="tabular-nums text-ink">{formatDT(cart.subtotal)}</dd></div>
                    <div className="flex justify-between"><dt className="text-muted">Livraison estimée</dt><dd className="tabular-nums text-ink">{shipping === 0 ? "Offerte" : formatDT(shipping)}</dd></div>
                    {wrap > 0 && <div className="flex justify-between"><dt className="text-muted">Emballage cadeau</dt><dd className="tabular-nums text-ink">{formatDT(wrap)}</dd></div>}
                    <div className="flex justify-between border-t border-stone pt-2 text-base"><dt className="text-ink">Total</dt><dd className="font-medium tabular-nums text-ink">{formatDT(cart.subtotal + shipping + wrap)}</dd></div>
                  </dl>
                  <Link href="/commande" onClick={cart.close} className="btn-primary mt-4 w-full">Commander</Link>
                  <div className="mt-3 flex items-center justify-between text-xs">
                    <Link href="/panier" onClick={cart.close} className="text-muted underline-offset-4 hover:text-ink hover:underline">Voir le panier</Link>
                    {confirmClear ? (
                      <span className="flex items-center gap-2 text-muted">Vider ? <button onClick={() => { cart.clear(); setConfirmClear(false); }} className="text-error">Oui</button><button onClick={() => setConfirmClear(false)} className="text-ink">Non</button></span>
                    ) : (
                      <button onClick={() => setConfirmClear(true)} className="text-muted hover:text-error">Vider le panier</button>
                    )}
                  </div>
                </div>
              </>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
