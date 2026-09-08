import type { OrderStatus } from "@/db/schema";

export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  pending: "En attente", confirmed: "Confirmée", preparing: "En préparation", shipped: "Expédiée", delivered: "Livrée", cancelled: "Annulée", returned: "Retournée",
};
export const ORDER_FLOW: OrderStatus[] = ["pending", "confirmed", "preparing", "shipped", "delivered"];
export const ALLOWED_TRANSITIONS: Record<OrderStatus, OrderStatus[]> = {
  pending: ["confirmed", "cancelled"],
  confirmed: ["preparing", "cancelled"],
  preparing: ["shipped", "cancelled"],
  shipped: ["delivered", "returned"],
  delivered: ["returned"],
  cancelled: [],
  returned: [],
};
export const PAYMENT_LABELS = { cod: "Paiement à la livraison", bank_transfer: "Virement bancaire", card: "Carte bancaire", gift_card: "Carte cadeau" } as const;
export const SHIPPING_LABELS = { standard: "Livraison standard", express: "Livraison express", pickup: "Click & Collect" } as const;
