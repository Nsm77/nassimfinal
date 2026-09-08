"use client";
import Image from "next/image";
import Link from "next/link";
import { useCart } from "@/components/cart/cart-provider";
import { BagIcon, TrashIcon } from "@/components/icons";
import { EmptyState, QtyStepper } from "@/components/ui/primitives";
import { formatDT, remainingForFreeShipping, shippingFor } from "@/lib/money";

export function CartPage() {
  const cart = useCart();
  if (!cart.hydrated) return <div className="skeleton h-64" />;
  if (!cart.lines.length) return <EmptyState icon={<BagIcon size={22} />} title="Votre panier est vide" description="Découvrez notre sélection de soins conseillés par nos pharmaciens." action={{ href: "/boutique", label: "Découvrir la boutique" }} />;
  const ship = shippingFor(cart.subtotal);
  const remaining = remainingForFreeShipping(cart.subtotal);
  return (
    <div className="grid gap-12 lg:grid-cols-12">
      <div className="lg:col-span-8">
        <ul className="divide-y divide-stone border-y border-stone">
          {cart.lines.map((l) => (
            <li key={l.productId} className="flex gap-5 py-6">
              <Link href={`/produit/${l.slug}`} className="relative h-32 w-24 shrink-0 bg-stone sm:h-36 sm:w-28">{l.image && <Image src={l.image} alt="" fill sizes="112px" className="object-cover" />}</Link>
              <div className="flex min-w-0 flex-1 flex-col">
                <p className="text-[10px] uppercase tracking-[0.16em] text-muted">{l.brandName}</p>
                <Link href={`/produit/${l.slug}`} className="mt-1 text-[15px] text-ink">{l.name}</Link>
                {l.volume && <p className="text-xs text-muted-2">{l.volume}</p>}
                <p className="mt-1 text-sm tabular-nums text-muted">{formatDT(l.priceMillimes)} l&apos;unité</p>
                <div className="mt-auto flex flex-wrap items-center justify-between gap-3 pt-4">
                  <div className="flex items-center gap-4"><QtyStepper value={l.quantity} max={Math.min(20, l.stock)} onChange={(v) => cart.setQty(l.productId, v)} /><button onClick={() => cart.remove(l.productId)} aria-label="Retirer" className="flex h-11 w-11 items-center justify-center text-muted-2 hover:text-error"><TrashIcon size={16} /></button></div>
                  <span className="text-[15px] font-medium tabular-nums text-ink">{formatDT(l.priceMillimes * l.quantity)}</span>
                </div>
              </div>
            </li>
          ))}
        </ul>
        <div className="mt-6 flex justify-between"><Link href="/boutique" className="btn-ghost">Continuer mes achats</Link></div>
      </div>
      <aside className="lg:col-span-4"><div className="sticky top-28 border border-stone bg-cream p-6">
        <h2 className="font-display text-xl text-ink">Récapitulatif</h2>
        <dl className="mt-5 space-y-2 text-sm"><div className="flex justify-between"><dt className="text-muted">Sous-total</dt><dd className="tabular-nums">{formatDT(cart.subtotal)}</dd></div><div className="flex justify-between"><dt className="text-muted">Livraison estimée</dt><dd className="tabular-nums">{ship ? formatDT(ship) : "Offerte"}</dd></div><div className="flex justify-between border-t border-stone pt-3 text-base text-ink"><dt>Total</dt><dd className="font-medium tabular-nums">{formatDT(cart.subtotal + ship)}</dd></div></dl>
        {remaining > 0 && <p className="mt-3 text-xs text-muted">Plus que {formatDT(remaining)} pour la livraison offerte.</p>}
        <Link href="/commande" className="btn-primary mt-6 w-full">Passer la commande</Link>
        <p className="mt-3 text-center text-xs text-muted-2">Code promo à l&apos;étape paiement</p>
      </div></aside>
    </div>
  );
}
