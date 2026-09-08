import "server-only";

/**
 * Payment-method policy.
 *
 * The DB enum (`payment_method`) intentionally lists every value the schema can
 * store, but only the methods listed here may actually be *submitted* by a client.
 * Frontend disabling is cosmetic: a hand-crafted request can send any enum value,
 * so the server is the only real gate.
 *
 * `card` has no implementation — the checkout UI shows it as « Bientôt disponible ».
 * Accepting it would create an order that looks card-paid while nothing was
 * collected, so it is rejected server-side until a real integration exists.
 *
 * `gift_card` is an *offline* method, exactly like `bank_transfer`: no automated
 * authorisation happens, the code is verified by phone, and the order stays
 * `paymentStatus = 'pending'` until staff settle it. It never marks an order paid.
 * It stays enabled because it is a live customer-facing option; drop it from
 * `PAYMENT_METHODS_ENABLED` (no code change needed) if you would rather not offer it.
 */
export const ALL_PAYMENT_METHODS = ["cod", "bank_transfer", "card", "gift_card"] as const;
export type PaymentMethod = (typeof ALL_PAYMENT_METHODS)[number];

const DEFAULT_ENABLED: readonly PaymentMethod[] = ["cod", "bank_transfer", "gift_card"];

export function enabledPaymentMethods(): readonly PaymentMethod[] {
  const raw = process.env.PAYMENT_METHODS_ENABLED;
  if (!raw?.trim()) return DEFAULT_ENABLED;
  const parsed = raw
    .split(",")
    .map((s) => s.trim())
    .filter((s): s is PaymentMethod => (ALL_PAYMENT_METHODS as readonly string[]).includes(s));
  // Never end up with an empty allow-list from a typo'd env value.
  return parsed.length ? parsed : DEFAULT_ENABLED;
}

export function isPaymentMethodEnabled(method: string): boolean {
  return enabledPaymentMethods().includes(method as PaymentMethod);
}
