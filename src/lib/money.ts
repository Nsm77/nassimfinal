/** All money is stored as integer millimes. 1 DT = 1000 millimes. */
export type Millimes = number;

export const FREE_SHIPPING_THRESHOLD: Millimes = 99_000;
export const STANDARD_SHIPPING_FEE: Millimes = 7_000;
export const EXPRESS_SHIPPING_FEE: Millimes = 12_000;
export const GIFT_WRAP_FEE: Millimes = 5_000;

const fmt = new Intl.NumberFormat("fr-TN", { minimumFractionDigits: 3, maximumFractionDigits: 3 });

export function formatDT(millimes: Millimes): string {
  return `${fmt.format(millimes / 1000)} DT`;
}

export function formatDTShort(millimes: Millimes): string {
  const dt = millimes / 1000;
  return Number.isInteger(dt) ? `${dt} DT` : formatDT(millimes);
}

export function discountPercent(price: Millimes, compareAt?: Millimes | null): number {
  if (!compareAt || compareAt <= price) return 0;
  return Math.round(((compareAt - price) / compareAt) * 100);
}

export type ShippingMethod = "standard" | "express" | "pickup";

export function shippingFor(subtotal: Millimes, method: ShippingMethod = "standard"): Millimes {
  if (method === "pickup") return 0;
  if (method === "express") return EXPRESS_SHIPPING_FEE;
  return subtotal >= FREE_SHIPPING_THRESHOLD ? 0 : STANDARD_SHIPPING_FEE;
}

export function remainingForFreeShipping(subtotal: Millimes): Millimes {
  return Math.max(0, FREE_SHIPPING_THRESHOLD - subtotal);
}

export function loyaltyPointsFor(total: Millimes): number {
  return Math.floor(total / 10_000); // 1 point per 10 DT
}
