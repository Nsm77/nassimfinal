import type { Metadata } from "next";
import Image from "next/image";
import { eq } from "drizzle-orm";
import { db } from "@/db";
import { orders, type Order, type OrderEvent, type OrderItem } from "@/db/schema";
import { safeEqual, PAYMENT_LABELS, SHIPPING_LABELS } from "@/lib/orders";
import { rateLimit } from "@/lib/rate-limit";
import { clientKey } from "@/lib/origin";
import { formatDT } from "@/lib/money";
import { formatDate } from "@/lib/utils";
import { Breadcrumbs, Field } from "@/components/ui/primitives";
import { OrderTimeline } from "@/components/account/order-timeline";
import { PackageIcon } from "@/components/icons";
export const metadata: Metadata = { title: "Suivre ma commande", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

export default async function SuiviPage({ searchParams }: { searchParams: Promise<{ n?: string; e?: string; k?: string }> }) {
  const { n, e, k } = await searchParams;
  const number = n?.trim().toUpperCase();
  const email = e?.trim().toLowerCase();
  let order: (Order & { events: OrderEvent[]; items: OrderItem[] }) | null = null;
  let blocked = false;

  if (number && (email || k)) {
    // Throttled so the form cannot be used to enumerate order numbers.
    if (!(await rateLimit(`suivi:${await clientKey()}`, 20, 600_000))) {
      blocked = true;
    } else {
      const candidates = await db.query.orders.findMany({ where: eq(orders.number, number), with: { events: true, items: true }, limit: 1 });
      const candidate = candidates[0];
      if (candidate) {
        // Order number + a second factor: the verified e-mail, or the per-order
        // access key issued at checkout. The number alone is never sufficient.
        const byEmail = !!email && candidate.email.toLowerCase() === email;
        const byKey = safeEqual(k, candidate.accessKey);
        if (byEmail || byKey) order = candidate;
      }
    }
  }

  const invoiceHref = order ? `/api/orders/${order.number}/invoice${k && safeEqual(k, order.accessKey) ? `?k=${encodeURIComponent(k)}` : email ? `?e=${encodeURIComponent(email)}` : ""}` : "#";

  return (
    <div className="container-lux py-10 lg:py-14">
      <Breadcrumbs items={[{ label: "Suivre ma commande" }]} />
      <div className="mx-auto mt-6 max-w-xl text-center">
        <p className="eyebrow mb-4">Suivi</p>
        <h1 className="font-display text-display-lg text-ink">Suivre ma commande</h1>
        <p className="mt-3 text-[15px] text-muted">Retrouvez l&apos;état de votre commande à tout moment.</p>
      </div>

      <div className="mx-auto mt-10 max-w-xl">
        <form className="space-y-4 border border-stone bg-cream p-6">
          <Field label="Numéro de commande">
            <input name="n" defaultValue={n} placeholder="CL-260907-XXXXXXXX" required className="field" />
          </Field>
          <Field label="E-mail utilisé pour la commande">
            <input name="e" type="email" defaultValue={e} required className="field" />
          </Field>
          <button className="btn-primary w-full">Suivre ma commande</button>
          <p className="text-center text-xs text-muted-2">Votre numéro de commande figure dans votre e-mail de confirmation.</p>
        </form>

        {blocked && <p className="mt-6 border border-error/30 bg-error-soft px-4 py-3 text-sm text-error" role="alert">Trop de tentatives. Merci de réessayer dans quelques minutes.</p>}
        {!blocked && number && (email || k) && !order && (
          <p className="mt-6 border border-error/30 bg-error-soft px-4 py-3 text-sm text-error" role="alert">Les informations saisies ne correspondent pas à une commande.</p>
        )}
      </div>

      {order && (
        <div className="mx-auto mt-14 max-w-4xl">
          {/* Order header */}
          <div className="flex flex-wrap items-end justify-between gap-6 border-b border-stone pb-8">
            <div>
              <p className="eyebrow mb-2">Commande</p>
              <p className="font-mono text-xl text-ink">{order.number}</p>
              <p className="mt-1 text-sm text-muted">Passée le {formatDate(order.createdAt)}</p>
            </div>
            <div className="text-right">
              <p className="eyebrow mb-2">Total</p>
              <p className="text-xl font-medium tabular-nums text-ink">{formatDT(order.totalMillimes)}</p>
              <p className="mt-1 text-sm text-muted">{PAYMENT_LABELS[order.paymentMethod]}</p>
            </div>
          </div>

          {/* Timeline */}
          <div className="mt-10"><OrderTimeline status={order.status} events={order.events} /></div>

          {/* Products */}
          <div className="mt-12">
            <p className="eyebrow mb-4">Vos articles</p>
            <ul className="divide-y divide-stone border-y border-stone">
              {order.items.map((i) => (
                <li key={i.id} className="flex gap-4 py-4">
                  <div className="relative h-20 w-16 shrink-0 bg-stone">{i.image && <Image src={i.image} alt="" fill sizes="64px" className="object-cover" />}</div>
                  <div className="min-w-0 flex-1">
                    <p className="text-[10px] uppercase tracking-[0.16em] text-muted">{i.brandName}</p>
                    <p className="text-sm text-ink">{i.name}</p>
                    <p className="text-xs text-muted">{i.quantity} × {formatDT(i.unitPriceMillimes)}</p>
                  </div>
                  <span className="text-sm tabular-nums text-ink">{formatDT(i.lineTotalMillimes)}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Delivery + actions */}
          <div className="mt-10 grid gap-8 sm:grid-cols-2">
            <div className="border border-stone bg-cream p-5 text-sm">
              <p className="eyebrow mb-2 flex items-center gap-2"><PackageIcon size={14} className="text-champagne-2" /> Livraison</p>
              <p className="text-ink">{SHIPPING_LABELS[order.shippingMethod]}</p>
              <p className="mt-1 text-charcoal">
                {order.shippingAddress.fullName}<br />
                {order.shippingAddress.line1}{order.shippingAddress.line2 && <><br />{order.shippingAddress.line2}</>}<br />
                {order.shippingAddress.city}, {order.shippingAddress.governorate}
              </p>
              {order.trackingCode && <p className="mt-2 text-xs text-muted">Suivi transporteur : <span className="font-mono text-ink">{order.trackingCode}</span></p>}
            </div>
            <div className="flex flex-col justify-center gap-3">
              <a href={invoiceHref} className="btn-primary w-full text-center">Télécharger la facture PDF</a>
              <a href={`/commande/confirmation/${order.number}${k ? `?k=${encodeURIComponent(k)}` : ""}`} className="btn-secondary w-full text-center">Voir la confirmation</a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
