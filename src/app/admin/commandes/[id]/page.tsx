import Link from "next/link";
import { notFound } from "next/navigation";
import { eq } from "drizzle-orm";
import { db } from "@/db";
import { orders, stores } from "@/db/schema";
import { formatDT } from "@/lib/money";
import { formatDateTime } from "@/lib/utils";
import { ORDER_STATUS_LABELS, PAYMENT_LABELS, SHIPPING_LABELS } from "@/lib/orders";
import { AdminPage, Panel, StatusBadge } from "@/components/admin/ui";
import { NotesForm, StatusButtons } from "@/components/admin/order-controls";
export const dynamic = "force-dynamic";
export default async function AdminOrder({ params }: { params: Promise<{ id: string }> }) {
  const id = Number((await params).id);
  const o = await db.query.orders.findFirst({ where: eq(orders.id, id), with: { items: true, events: true, user: true } });
  if (!o) notFound();
  const store = o.storeId ? await db.query.stores.findFirst({ where: eq(stores.id, o.storeId) }) : null;
  return (
    <AdminPage title={o.number} sub={formatDateTime(o.createdAt)} action={<StatusBadge s={o.status} />}>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Panel className="p-5"><h2 className="mb-4 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Workflow</h2><StatusButtons orderId={o.id} status={o.status} /></Panel>
          <Panel><h2 className="border-b border-admin-border px-5 py-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Articles — vue préparation</h2><ul className="divide-y divide-admin-border">{o.items.map((i) => <li key={i.id} className="flex items-center gap-4 px-5 py-3 text-sm"><span className="flex h-9 w-9 shrink-0 items-center justify-center border border-admin-border font-mono">{i.quantity}</span><div className="min-w-0 flex-1"><p className="truncate">{i.name}</p><p className="text-xs text-admin-muted">{i.brandName} · {i.sku}</p></div><span className="tabular-nums">{formatDT(i.lineTotalMillimes)}</span></li>)}</ul>
            <dl className="space-y-1 border-t border-admin-border px-5 py-4 text-sm"><div className="flex justify-between"><dt className="text-admin-muted">Sous-total</dt><dd className="tabular-nums">{formatDT(o.subtotalMillimes)}</dd></div>{o.discountMillimes > 0 && <div className="flex justify-between"><dt className="text-admin-muted">Remise ({o.promoCode})</dt><dd className="tabular-nums">−{formatDT(o.discountMillimes)}</dd></div>}<div className="flex justify-between"><dt className="text-admin-muted">Livraison</dt><dd className="tabular-nums">{formatDT(o.shippingMillimes)}</dd></div>{o.giftWrapMillimes > 0 && <div className="flex justify-between"><dt className="text-admin-muted">Emballage cadeau</dt><dd className="tabular-nums">{formatDT(o.giftWrapMillimes)}</dd></div>}<div className="flex justify-between border-t border-admin-border pt-2 text-base"><dt>Total</dt><dd className="tabular-nums">{formatDT(o.totalMillimes)}</dd></div></dl></Panel>
          <Panel className="p-5"><h2 className="mb-4 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Chronologie</h2><ul className="space-y-3 text-sm">{o.events.map((e) => <li key={e.id}><span>{ORDER_STATUS_LABELS[e.status]}</span>{e.message && <span className="text-admin-muted"> — {e.message}</span>}<span className="block text-xs text-admin-muted">{formatDateTime(e.createdAt)}</span></li>)}</ul></Panel>
        </div>
        <div className="space-y-6">
          <Panel className="p-5 text-sm"><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Client</h2><p>{o.shippingAddress.fullName}</p><p className="text-admin-muted">{o.email}</p><p className="text-admin-muted">{o.phone}</p>{o.user && <Link href={`/admin/clients/${o.user.id}`} className="mt-2 inline-block text-xs underline">Fiche client</Link>}</Panel>
          <Panel className="p-5 text-sm"><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Livraison</h2><p>{SHIPPING_LABELS[o.shippingMethod]}{store && ` — ${store.name}`}</p><p className="mt-2 text-admin-muted">{o.shippingAddress.line1}{o.shippingAddress.line2 && <>, {o.shippingAddress.line2}</>}<br />{o.shippingAddress.city}, {o.shippingAddress.governorate} {o.shippingAddress.postalCode}</p>{o.giftWrap && <p className="mt-2 text-champagne">Emballage cadeau{o.giftMessage && ` — « ${o.giftMessage} »`}</p>}{o.customerNote && <p className="mt-2 text-admin-muted">Note client : {o.customerNote}</p>}</Panel>
          <Panel className="p-5 text-sm"><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Paiement</h2><p>{PAYMENT_LABELS[o.paymentMethod]}</p><p className="text-admin-muted">{o.paymentStatus}</p></Panel>
          <Panel className="p-5"><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Suivi & notes internes</h2><NotesForm orderId={o.id} internalNote={o.internalNote ?? ""} trackingCode={o.trackingCode ?? ""} /></Panel>
        </div>
      </div>
    </AdminPage>
  );
}
