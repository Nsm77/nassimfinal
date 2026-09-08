"use client";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useEffect, useMemo, useState, useTransition } from "react";
import { useCart } from "@/components/cart/cart-provider";
import { BankIcon, CardIcon, CashIcon, CheckIcon, GiftIcon, StoreIcon, TruckIcon, LockIcon, TagIcon } from "@/components/icons";
import { Field, Steps } from "@/components/ui/primitives";
import { useToast } from "@/components/ui/toaster";
import { formatDT, GIFT_WRAP_FEE, EXPRESS_SHIPPING_FEE, shippingFor, type ShippingMethod } from "@/lib/money";
import { CITIES, deliveryEstimate, GOVERNORATES } from "@/lib/tunisia";
import { EASE_LUXE } from "@/lib/motion";
import { placeOrderAction } from "@/actions/checkout";
import { validatePromoAction } from "@/actions/shop";
import type { Address, Store } from "@/db/schema";
import type { SafeUser } from "@/lib/auth";

type Promo = { code: string; discount: number; freeShipping: boolean; label: string } | null;
const STEPS = ["Informations", "Livraison", "Paiement", "Récapitulatif"];

export function CheckoutFlow({ user, savedAddresses, stores }: { user: SafeUser | null; savedAddresses: Address[]; stores: Store[] }) {
  const cart = useCart();
  const router = useRouter();
  const { toast } = useToast();
  const reduce = useReducedMotion();
  const [step, setStep] = useState(0);
  const [email, setEmail] = useState(user?.email ?? "");
  const def = savedAddresses.find((a) => a.isDefault) ?? savedAddresses[0];
  const [addr, setAddr] = useState({ fullName: def?.fullName ?? (user ? `${user.firstName} ${user.lastName}` : ""), phone: def?.phone ?? user?.phone ?? "", line1: def?.line1 ?? "", line2: def?.line2 ?? "", city: def?.city ?? "", governorate: def?.governorate ?? "Ben Arous", postalCode: def?.postalCode ?? "" });
  const [shipping, setShipping] = useState<ShippingMethod>("standard");
  const [storeId, setStoreId] = useState<number>(stores[0]?.id ?? 0);
  const [payment, setPayment] = useState<"cod" | "bank_transfer" | "card" | "gift_card">("cod");
  const [promoInput, setPromoInput] = useState(cart.promoCode);
  const [promo, setPromo] = useState<Promo>(null);
  const [giftMessage, setGiftMessage] = useState("");
  const [createAccount, setCreateAccount] = useState(false);
  const [accountPassword, setAccountPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pending, start] = useTransition();
  const [idem] = useState(() => (typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID().replace(/-/g, "") : String(Date.now()) + Math.random().toString(16).slice(2)));

  useEffect(() => { if (cart.hydrated && cart.lines.length === 0) router.replace("/panier"); }, [cart.hydrated, cart.lines.length, router]);

  const subtotal = cart.subtotal;
  const discount = promo?.discount ?? 0;
  const shipFee = promo?.freeShipping && shipping !== "express" ? 0 : shippingFor(subtotal - discount, shipping);
  const wrap = cart.giftWrap ? GIFT_WRAP_FEE : 0;
  const total = subtotal - discount + shipFee + wrap;
  const cities = useMemo(() => CITIES[addr.governorate as keyof typeof CITIES] ?? [], [addr.governorate]);

  const validateInfo = () => {
    const e: Record<string, string> = {};
    if (!/^\S+@\S+\.\S+$/.test(email)) e.email = "E-mail invalide";
    if (addr.fullName.trim().length < 3) e.fullName = "Nom complet requis";
    if (!/^(\+216)?[2-9]\d{7}$/.test(addr.phone.replace(/\s/g, ""))) e.phone = "8 chiffres requis";
    if (addr.line1.trim().length < 5) e.line1 = "Adresse trop courte";
    if (addr.city.trim().length < 2) e.city = "Ville requise";
    if (createAccount && accountPassword.length < 8) e.accountPassword = "8 caractères minimum";
    setErrors(e);
    return Object.keys(e).length === 0;
  };
  const next = () => { if (step === 0 && !validateInfo()) return; setStep((s) => Math.min(3, s + 1)); window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); };

  const applyPromo = () => start(async () => {
    const r = await validatePromoAction(promoInput, cart.lines.map((l) => ({ productId: l.productId, quantity: l.quantity })));
    if (r.ok) { setPromo(r.data); cart.setPromoCode(r.data.code); toast({ kind: "success", title: "Code appliqué", description: r.data.label }); }
    else { setPromo(null); toast({ kind: "error", title: r.error }); }
  });

  const submit = () => start(async () => {
    const r = await placeOrderAction({
      email: email.trim(), address: { ...addr, phone: addr.phone.replace(/\s/g, "") }, shippingMethod: shipping, storeId: shipping === "pickup" ? storeId : undefined, paymentMethod: payment,
      promoCode: promo?.code ?? "", giftWrap: cart.giftWrap, giftMessage, customerNote: cart.note, createAccount, accountPassword, idempotencyKey: idem,
      lines: cart.lines.map((l) => ({ productId: l.productId, quantity: l.quantity })),
    });
    // The access key authorises guest access to the confirmation page; the order
    // number on its own is deliberately not enough.
    if (r.ok) { cart.clear(); router.push(`/commande/confirmation/${r.data.number}${r.data.accessKey ? `?k=${encodeURIComponent(r.data.accessKey)}` : ""}`); }
    else toast({ kind: "error", title: r.error, description: r.fieldErrors ? Object.values(r.fieldErrors)[0] : undefined });
  });

  if (!cart.hydrated) return <div className="skeleton h-64" />;

  const variants = { enter: { opacity: 0, x: reduce ? 0 : 16 }, center: { opacity: 1, x: 0, transition: { duration: 0.55, ease: EASE_LUXE } }, exit: { opacity: 0, x: reduce ? 0 : -12, transition: { duration: 0.25 } } };

  return (
    <div className="grid gap-12 lg:grid-cols-12">
      <div className="lg:col-span-7">
        <Steps steps={STEPS} current={step} />
        <div className="mt-10 overflow-hidden">
          <AnimatePresence mode="wait" initial={false}>
            {step === 0 && (
              <motion.section key="info" variants={variants} initial="enter" animate="center" exit="exit" className="space-y-5">
                <h2 className="font-display text-display-sm text-ink">Vos informations</h2>
                <Field label="E-mail" error={errors.email}><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" className="field" /></Field>
                {savedAddresses.length > 1 && <Field label="Adresse enregistrée"><select onChange={(e) => { const a = savedAddresses.find((x) => x.id === Number(e.target.value)); if (a) setAddr({ fullName: a.fullName, phone: a.phone, line1: a.line1, line2: a.line2 ?? "", city: a.city, governorate: a.governorate, postalCode: a.postalCode ?? "" }); }} className="field" defaultValue={def?.id}>{savedAddresses.map((a) => <option key={a.id} value={a.id}>{a.label} — {a.line1}, {a.city}</option>)}</select></Field>}
                <div className="grid gap-5 sm:grid-cols-2"><Field label="Nom complet" error={errors.fullName}><input value={addr.fullName} onChange={(e) => setAddr({ ...addr, fullName: e.target.value })} autoComplete="name" className="field" /></Field><Field label="Téléphone" error={errors.phone} hint="Pour la livraison"><input value={addr.phone} onChange={(e) => setAddr({ ...addr, phone: e.target.value })} inputMode="tel" autoComplete="tel" className="field" /></Field></div>
                <Field label="Adresse" error={errors.line1}><input value={addr.line1} onChange={(e) => setAddr({ ...addr, line1: e.target.value })} autoComplete="address-line1" className="field" /></Field>
                <Field label="Complément (facultatif)"><input value={addr.line2} onChange={(e) => setAddr({ ...addr, line2: e.target.value })} autoComplete="address-line2" className="field" /></Field>
                <div className="grid gap-5 sm:grid-cols-3">
                  <Field label="Gouvernorat"><select value={addr.governorate} onChange={(e) => setAddr({ ...addr, governorate: e.target.value, city: "" })} className="field">{GOVERNORATES.map((g) => <option key={g}>{g}</option>)}</select></Field>
                  <Field label="Ville" error={errors.city}>{cities.length ? <select value={addr.city} onChange={(e) => setAddr({ ...addr, city: e.target.value })} className="field"><option value="">Choisir…</option>{cities.map((c) => <option key={c}>{c}</option>)}<option value="Autre">Autre</option></select> : <input value={addr.city} onChange={(e) => setAddr({ ...addr, city: e.target.value })} className="field" />}</Field>
                  <Field label="Code postal"><input value={addr.postalCode} onChange={(e) => setAddr({ ...addr, postalCode: e.target.value })} inputMode="numeric" className="field" /></Field>
                </div>
                {!user && (
                  <div className="border border-stone bg-cream p-4"><label className="flex min-h-11 items-center gap-3 text-sm"><input type="checkbox" checked={createAccount} onChange={(e) => setCreateAccount(e.target.checked)} className="h-4 w-4 accent-ink" /> Créer un compte pour suivre mes commandes</label>{createAccount && <Field label="Mot de passe" error={errors.accountPassword}><input type="password" value={accountPassword} onChange={(e) => setAccountPassword(e.target.value)} autoComplete="new-password" className="field" /></Field>}</div>
                )}
              </motion.section>
            )}
            {step === 1 && (
              <motion.section key="ship" variants={variants} initial="enter" animate="center" exit="exit" className="space-y-5">
                <h2 className="font-display text-display-sm text-ink">Mode de livraison</h2>
                <div className="space-y-2" role="radiogroup">
                  {([
                    { v: "standard", l: "Livraison standard", d: deliveryEstimate(addr.governorate, "standard"), p: shippingFor(subtotal - discount, "standard"), i: TruckIcon },
                    { v: "express", l: "Livraison express", d: deliveryEstimate(addr.governorate, "express"), p: EXPRESS_SHIPPING_FEE, i: TruckIcon },
                    { v: "pickup", l: "Click & Collect", d: "Retrait sous 2 h en boutique", p: 0, i: StoreIcon },
                  ] as const).map((o) => (
                    <label key={o.v} className={`flex min-h-16 cursor-pointer items-center gap-4 border p-4 transition-colors ${shipping === o.v ? "border-ink bg-cream" : "border-stone hover:border-sand-2"}`}>
                      <input type="radio" name="shipping" value={o.v} checked={shipping === o.v} onChange={() => setShipping(o.v)} className="sr-only" />
                      <o.i size={20} className="text-champagne-2" /><div className="flex-1"><p className="text-sm text-ink">{o.l}</p><p className="text-xs text-muted">{o.d}</p></div><span className="text-sm tabular-nums text-ink">{o.p === 0 || (promo?.freeShipping && o.v === "standard") ? "Offerte" : formatDT(o.p)}</span>
                    </label>
                  ))}
                </div>
                {shipping === "pickup" && <Field label="Boutique de retrait"><select value={storeId} onChange={(e) => setStoreId(Number(e.target.value))} className="field">{stores.map((s) => <option key={s.id} value={s.id}>{s.name} — {s.address}</option>)}</select></Field>}
                <div className="border border-stone p-4">
                  <label className="flex min-h-11 items-center justify-between gap-3 text-sm"><span className="flex items-center gap-2"><GiftIcon size={16} className="text-champagne-2" /> Emballage cadeau (+{formatDT(GIFT_WRAP_FEE)})</span><input type="checkbox" checked={cart.giftWrap} onChange={(e) => cart.setGiftWrap(e.target.checked)} className="h-4 w-4 accent-ink" /></label>
                  {cart.giftWrap && <textarea value={giftMessage} onChange={(e) => setGiftMessage(e.target.value)} maxLength={300} rows={2} placeholder="Message à joindre (facultatif)" className="field mt-3 text-sm" />}
                </div>
                <Field label="Note pour la commande (facultatif)"><textarea value={cart.note} onChange={(e) => cart.setNote(e.target.value)} rows={2} maxLength={500} className="field text-sm" /></Field>
              </motion.section>
            )}
            {step === 2 && (
              <motion.section key="pay" variants={variants} initial="enter" animate="center" exit="exit" className="space-y-5">
                <h2 className="font-display text-display-sm text-ink">Paiement</h2>
                <div className="space-y-2" role="radiogroup">
                  {([
                    { v: "cod", l: "Paiement à la livraison", d: "Espèces au livreur ou en boutique", i: CashIcon, ok: true },
                    { v: "bank_transfer", l: "Virement bancaire", d: "RIB communiqué après validation", i: BankIcon, ok: true },
                    { v: "gift_card", l: "Carte cadeau Cléopâtre", d: "Le code vous sera demandé par téléphone", i: GiftIcon, ok: true },
                    { v: "card", l: "Carte bancaire", d: "Bientôt disponible", i: CardIcon, ok: false },
                  ] as const).map((o) => (
                    <label key={o.v} className={`flex min-h-16 items-center gap-4 border p-4 transition-colors ${!o.ok ? "cursor-not-allowed opacity-50" : payment === o.v ? "cursor-pointer border-ink bg-cream" : "cursor-pointer border-stone hover:border-sand-2"}`}>
                      <input type="radio" name="payment" value={o.v} disabled={!o.ok} checked={payment === o.v} onChange={() => setPayment(o.v)} className="sr-only" />
                      <o.i size={20} className="text-champagne-2" /><div className="flex-1"><p className="text-sm text-ink">{o.l}</p><p className="text-xs text-muted">{o.d}</p></div>{payment === o.v && <CheckIcon size={16} className="text-ink" />}
                    </label>
                  ))}
                </div>
                <div><p className="eyebrow mb-2">Code promo</p><div className="flex"><input value={promoInput} onChange={(e) => setPromoInput(e.target.value.toUpperCase())} placeholder="BIENVENUE10" className="field border-r-0 font-mono uppercase" aria-label="Code promo" /><button type="button" onClick={applyPromo} disabled={pending || !promoInput} className="btn-secondary shrink-0">Appliquer</button></div>
                  <AnimatePresence>{promo && <motion.p initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-2 flex items-center gap-2 text-sm text-success"><CheckIcon size={14} /> {promo.label}{promo.discount > 0 && ` · −${formatDT(promo.discount)}`}<button type="button" onClick={() => { setPromo(null); setPromoInput(""); cart.setPromoCode(""); }} className="ml-2 text-xs text-muted underline">Retirer</button></motion.p>}</AnimatePresence></div>
              </motion.section>
            )}
            {step === 3 && (
              <motion.section key="review" variants={variants} initial="enter" animate="center" exit="exit" className="space-y-6">
                <h2 className="font-display text-display-sm text-ink">Vérifiez votre commande</h2>
                <div className="grid gap-4 text-sm sm:grid-cols-2">
                  <div className="border border-stone p-4"><p className="eyebrow mb-2">Livraison</p><p className="text-ink">{addr.fullName}</p><p className="text-charcoal">{addr.line1}{addr.line2 && `, ${addr.line2}`}<br />{addr.city}, {addr.governorate}<br />{addr.phone}</p><p className="mt-2 text-xs text-muted">{shipping === "pickup" ? `Retrait : ${stores.find((s) => s.id === storeId)?.name}` : deliveryEstimate(addr.governorate, shipping)}</p><button onClick={() => setStep(0)} className="mt-2 text-xs text-muted underline">Modifier</button></div>
                  <div className="border border-stone p-4"><p className="eyebrow mb-2">Paiement</p><p className="text-ink">{{ cod: "Paiement à la livraison", bank_transfer: "Virement bancaire", card: "Carte bancaire", gift_card: "Carte cadeau" }[payment]}</p>{promo && <p className="mt-1 text-success">{promo.code} appliqué</p>}<p className="mt-1 text-charcoal">{email}</p><button onClick={() => setStep(2)} className="mt-2 text-xs text-muted underline">Modifier</button></div>
                </div>
                <ul className="divide-y divide-stone border-y border-stone">{cart.lines.map((l) => <li key={l.productId} className="flex items-center gap-4 py-3"><div className="relative h-14 w-12 shrink-0 bg-stone">{l.image && <Image src={l.image} alt="" fill sizes="48px" className="object-cover" />}</div><div className="min-w-0 flex-1"><p className="truncate text-sm text-ink">{l.name}</p><p className="text-xs text-muted">{l.quantity} × {formatDT(l.priceMillimes)}</p></div><span className="text-sm tabular-nums">{formatDT(l.priceMillimes * l.quantity)}</span></li>)}</ul>
                <p className="text-xs text-muted">En confirmant, vous acceptez nos <Link href="/cgv" className="underline">conditions générales de vente</Link>.</p>
              </motion.section>
            )}
          </AnimatePresence>
        </div>
        <div className="mt-10 flex items-center justify-between gap-4">
          {step > 0 ? <button onClick={() => setStep((s) => s - 1)} className="btn-ghost">Retour</button> : <Link href="/panier" className="btn-ghost">Retour au panier</Link>}
          {step < 3 ? <button onClick={next} className="btn-primary">Continuer</button> : <button onClick={submit} disabled={pending} className="btn-primary min-w-56"><LockIcon size={16} /> {pending ? "Traitement…" : `Confirmer · ${formatDT(total)}`}</button>}
        </div>
      </div>

      <aside className="lg:col-span-5"><div className="sticky top-28 border border-stone bg-cream p-6">
        <h3 className="mb-5 font-display text-xl text-ink">Récapitulatif</h3>
        <ul className="max-h-64 space-y-3 overflow-y-auto pr-1">{cart.lines.map((l) => <li key={l.productId} className="flex items-center gap-3 text-sm"><div className="relative h-12 w-10 shrink-0 bg-stone">{l.image && <Image src={l.image} alt="" fill sizes="40px" className="object-cover" />}<span className="absolute -right-1.5 -top-1.5 flex h-4 min-w-4 items-center justify-center bg-ink px-1 text-[9px] text-paper">{l.quantity}</span></div><span className="min-w-0 flex-1 truncate text-charcoal">{l.name}</span><span className="tabular-nums text-ink">{formatDT(l.priceMillimes * l.quantity)}</span></li>)}</ul>
        <dl className="mt-5 space-y-1.5 border-t border-stone pt-4 text-sm">
          <div className="flex justify-between"><dt className="text-muted">Sous-total</dt><dd className="tabular-nums">{formatDT(subtotal)}</dd></div>
          <AnimatePresence>{discount > 0 && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex justify-between text-success"><dt className="flex items-center gap-1"><TagIcon size={12} /> Remise</dt><dd className="tabular-nums">−{formatDT(discount)}</dd></motion.div>}</AnimatePresence>
          <div className="flex justify-between"><dt className="text-muted">Livraison</dt><dd className="tabular-nums">{shipFee === 0 ? "Offerte" : formatDT(shipFee)}</dd></div>
          {wrap > 0 && <div className="flex justify-between"><dt className="text-muted">Emballage cadeau</dt><dd className="tabular-nums">{formatDT(wrap)}</dd></div>}
          <div className="flex justify-between border-t border-stone pt-3 text-base text-ink"><dt>Total</dt><motion.dd key={total} initial={reduce ? false : { opacity: 0.4 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }} className="font-medium tabular-nums">{formatDT(total)}</motion.dd></div>
        </dl>
        <p className="mt-4 flex items-center gap-2 text-xs text-muted"><LockIcon size={12} /> Données chiffrées · Produits authentiques</p>
      </div></aside>
    </div>
  );
}
