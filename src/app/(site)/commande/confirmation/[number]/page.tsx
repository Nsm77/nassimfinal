import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { eq } from "drizzle-orm";
import { db } from "@/db";
import { orders } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { formatDT } from "@/lib/money";
import { PAYMENT_LABELS, SHIPPING_LABELS } from "@/lib/orders";
import { safeEqual } from "@/lib/orders";
import { deliveryEstimate } from "@/lib/tunisia";
import { OrderTimeline } from "@/components/account/order-timeline";
import { Reveal } from "@/components/motion/reveal";
import { CheckIcon } from "@/components/icons";
export const metadata: Metadata = { title: "Commande confirmée", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

/** Show `ines@x.tn` as `i••••@x.tn` — the customer knows their own address. */
function maskEmail(email: string): string {
  const [local, domain] = email.split("@");
  if (!domain) return "votre adresse e-mail";
  return `${local.charAt(0)}${"•".repeat(Math.max(3, local.length - 1))}@${domain}`;
}

export default async function ConfirmationPage({ params, searchParams }: { params: Promise<{ number: string }>; searchParams: Promise<{ k?: string }> }) {
  const { number } = await params;
  const { k } = await searchParams;
  const [o, user] = await Promise.all([db.query.orders.findFirst({ where: eq(orders.number, number.trim().toUpperCase()), with: { items: true, events: true } }), getCurrentUser()]);
  if (!o) notFound();

  /*
   * Authorisation. The order number alone is NOT a credential — it is short and
   * printable, and used to appear in e-mails, so anyone who guessed one could
   * previously read a stranger's name, address, e-mail and totals here.
   * Access now requires either ownership (session) or the per-order access key
   * handed back at checkout. Everything else is an indistinguishable 404, so
   * the page cannot be used to probe which order numbers exist.
   */
  const ownsIt = !!user && o.userId === user.id;
  const hasKey = safeEqual(k, o.accessKey);
  if (!ownsIt && !hasKey) notFound();

  const trackingHref = user && ownsIt ? `/compte/commandes/${o.number}` : `/suivi?n=${o.number}&e=${encodeURIComponent(o.email)}`;
  const invoiceHref = `/api/orders/${o.number}/invoice${hasKey && k ? `?k=${encodeURIComponent(k)}` : ""}`;
  return (
    <div className="container-lux py-14 lg:py-20">
      <div className="mx-auto max-w-2xl text-center">
        <Reveal y={0}><span className="mx-auto flex h-14 w-14 items-center justify-center border border-champagne text-champagne-2"><CheckIcon size={24} /></span></Reveal>
        <Reveal delay={0.1}><p className="eyebrow mt-8 mb-4">Merci</p><h1 className="font-display text-display-lg text-ink">Commande confirmée</h1><p className="mt-4 text-[15px] text-muted">Votre commande <span className="font-mono text-ink">{o.number}</span> a bien été enregistrée. Un e-mail de confirmation est envoyé à {maskEmail(o.email)}.</p></Reveal>
      </div>
      <div className="mx-auto mt-14 grid max-w-4xl gap-10 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <ul className="mb-10 divide-y divide-stone border-y border-stone" aria-label="Articles commandés">
            {o.items.map((i) => (
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
          <p className="eyebrow mb-4">Suivi de votre commande</p>
          <OrderTimeline status={o.status} events={o.events} />
        </div>
        <div className="space-y-6 text-sm lg:col-span-5">
          <div className="border border-stone bg-cream p-5"><p className="eyebrow mb-3">Prochaines étapes</p><ol className="list-decimal space-y-2 pl-4 text-charcoal"><li>Notre équipe confirme votre commande par téléphone sous 24 h ouvrées.</li><li>{o.shippingMethod === "pickup" ? "Nous vous appelons dès que la commande est prête en boutique." : `${SHIPPING_LABELS[o.shippingMethod]} — ${deliveryEstimate(o.shippingAddress.governorate, o.shippingMethod)}.`}</li><li>{PAYMENT_LABELS[o.paymentMethod]}{o.paymentMethod === "bank_transfer" ? " — le RIB vous sera communiqué." : "."}</li></ol></div>
          <dl className="space-y-1.5 border border-stone p-5"><div className="flex justify-between"><dt className="text-muted">Articles</dt><dd>{o.items.reduce((a, i) => a + i.quantity, 0)}</dd></div><div className="flex justify-between"><dt className="text-muted">Sous-total</dt><dd className="tabular-nums">{formatDT(o.subtotalMillimes)}</dd></div>{o.discountMillimes > 0 && <div className="flex justify-between text-success"><dt>Remise</dt><dd className="tabular-nums">−{formatDT(o.discountMillimes)}</dd></div>}<div className="flex justify-between"><dt className="text-muted">Livraison</dt><dd className="tabular-nums">{o.shippingMillimes ? formatDT(o.shippingMillimes) : "Offerte"}</dd></div>{o.giftWrapMillimes > 0 && <div className="flex justify-between"><dt className="text-muted">Emballage cadeau</dt><dd className="tabular-nums">{formatDT(o.giftWrapMillimes)}</dd></div>}<div className="flex justify-between border-t border-stone pt-2 text-base text-ink"><dt>Total</dt><dd className="font-medium tabular-nums">{formatDT(o.totalMillimes)}</dd></div></dl>
          <div className="border border-stone p-5 text-sm"><p className="eyebrow mb-2">Livraison</p><p className="text-ink">{SHIPPING_LABELS[o.shippingMethod]}</p><p className="mt-1 text-charcoal">{o.shippingAddress.fullName}<br />{o.shippingAddress.line1}{o.shippingAddress.line2 && <><br />{o.shippingAddress.line2}</>}<br />{o.shippingAddress.city}, {o.shippingAddress.governorate}</p></div>
          <div className="flex flex-wrap gap-3">
            <Link href={trackingHref} className="btn-primary">Suivre ma commande</Link>
            <a href={invoiceHref} className="btn-secondary">Télécharger la facture PDF</a>
            <Link href="/boutique" className="btn-ghost">Continuer mes achats</Link>
          </div>
          {!user && <p className="text-xs leading-relaxed text-muted-2">Conservez ce lien : il vous permet de retrouver votre commande et sa facture à tout moment. <Link href="/inscription" className="underline underline-offset-4">Créez un compte</Link> pour gérer vos commandes plus facilement.</p>}
        </div>
      </div>
    </div>
  );
}
