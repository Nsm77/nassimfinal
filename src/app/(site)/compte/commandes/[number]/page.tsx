import Image from "next/image";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { and, eq } from "drizzle-orm";
import { db } from "@/db";
import { orders } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { formatDT } from "@/lib/money";
import { formatDate } from "@/lib/utils";
import { PAYMENT_LABELS, SHIPPING_LABELS } from "@/lib/orders";
import { OrderTimeline } from "@/components/account/order-timeline";
import { OrderActions } from "@/components/account/order-actions";
import { ArrowLeftIcon } from "@/components/icons";
export const dynamic = "force-dynamic";
export default async function CommandePage({ params }: { params: Promise<{ number: string }> }) {
  const { number } = await params;
  // The account layout redirects anonymous visitors, but the page must not rely
  // on that: ownership is enforced here so an order can never be read without a
  // session that owns it.
  const user = await getCurrentUser();
  if (!user) redirect("/connexion?next=/compte/commandes");
  const o = await db.query.orders.findFirst({ where: and(eq(orders.number, number.trim().toUpperCase()), eq(orders.userId, user.id)), with: { items: true, events: true } });
  if (!o) notFound();
  return (
    <div className="space-y-10">
      <Link href="/compte/commandes" className="inline-flex min-h-11 items-center gap-2 text-sm text-muted hover:text-ink"><ArrowLeftIcon size={14} /> Mes commandes</Link>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="eyebrow mb-2">Commande du {formatDate(o.createdAt)}</p><h2 className="font-display text-display-md text-ink">{o.number}</h2></div>
        <a href={`/api/orders/${o.number}/invoice`} className="btn-secondary">Télécharger la facture PDF</a>
      </div>
      <OrderTimeline status={o.status} events={o.events} />
      <OrderActions orderId={o.id} status={o.status} />
      <div className="grid gap-10 lg:grid-cols-12">
        <ul className="divide-y divide-stone border-y border-stone lg:col-span-7">{o.items.map((i) => <li key={i.id} className="flex gap-4 py-4"><div className="relative h-20 w-16 shrink-0 bg-stone">{i.image && <Image src={i.image} alt="" fill sizes="64px" className="object-cover" />}</div><div className="min-w-0 flex-1"><p className="text-[10px] uppercase tracking-[0.16em] text-muted">{i.brandName}</p><p className="text-sm text-ink">{i.name}</p><p className="text-xs text-muted">{i.quantity} × {formatDT(i.unitPriceMillimes)}</p></div><span className="text-sm tabular-nums text-ink">{formatDT(i.lineTotalMillimes)}</span></li>)}</ul>
        <div className="space-y-6 lg:col-span-5">
          <dl className="space-y-1.5 border border-stone bg-cream p-5 text-sm"><div className="flex justify-between"><dt className="text-muted">Sous-total</dt><dd className="tabular-nums">{formatDT(o.subtotalMillimes)}</dd></div>{o.discountMillimes > 0 && <div className="flex justify-between text-success"><dt>Remise {o.promoCode}</dt><dd className="tabular-nums">−{formatDT(o.discountMillimes)}</dd></div>}<div className="flex justify-between"><dt className="text-muted">Livraison</dt><dd className="tabular-nums">{o.shippingMillimes ? formatDT(o.shippingMillimes) : "Offerte"}</dd></div>{o.giftWrapMillimes > 0 && <div className="flex justify-between"><dt className="text-muted">Emballage cadeau</dt><dd className="tabular-nums">{formatDT(o.giftWrapMillimes)}</dd></div>}<div className="flex justify-between border-t border-stone pt-2 text-base text-ink"><dt>Total</dt><dd className="font-medium tabular-nums">{formatDT(o.totalMillimes)}</dd></div></dl>
          <div className="text-sm"><p className="eyebrow mb-2">Livraison</p><p className="text-ink">{SHIPPING_LABELS[o.shippingMethod]}</p><p className="text-charcoal">{o.shippingAddress.fullName}<br />{o.shippingAddress.line1}{o.shippingAddress.line2 && <><br />{o.shippingAddress.line2}</>}<br />{o.shippingAddress.city}, {o.shippingAddress.governorate}<br />{o.shippingAddress.phone}</p></div>
          <div className="text-sm"><p className="eyebrow mb-2">Paiement</p><p className="text-ink">{PAYMENT_LABELS[o.paymentMethod]}</p></div>
          {o.trackingCode && <div className="text-sm"><p className="eyebrow mb-2">Suivi transporteur</p><p className="font-mono text-ink">{o.trackingCode}</p></div>}
        </div>
      </div>
    </div>
  );
}
