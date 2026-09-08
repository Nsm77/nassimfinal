export type Locale = "fr" | "ar";
export const DEFAULT_LOCALE: Locale = "fr";
export const DIRECTION: Record<Locale, "ltr" | "rtl"> = { fr: "ltr", ar: "rtl" };

const fr = {
  nav: { boutique: "Boutique", marques: "Marques", promotions: "Offres", journal: "Journal", boutiques: "Nos boutiques", aide: "Aide" },
  actions: { addToCart: "Ajouter au panier", added: "Ajouté", outOfStock: "Épuisé", viewAll: "Tout voir", search: "Rechercher", close: "Fermer", continue: "Continuer", back: "Retour", checkout: "Commander", clear: "Vider", apply: "Appliquer" },
  cart: { title: "Votre panier", empty: "Votre panier est vide.", subtotal: "Sous-total", shipping: "Livraison", free: "Offerte", total: "Total", note: "Note pour la commande", giftWrap: "Emballage cadeau" },
  shipping: { freeFrom: "Livraison offerte dès 99 DT", remaining: (x: string) => `Plus que ${x} pour la livraison offerte` },
  trust: { authentic: "Produits 100 % authentiques", pharmacists: "Conseils de pharmaciens", delivery: "Livraison partout en Tunisie", secure: "Paiement à la livraison" },
} as const;

export type Dictionary = typeof fr;
const dictionaries: Record<Locale, Dictionary> = { fr, ar: fr };
export function t(locale: Locale = DEFAULT_LOCALE): Dictionary {
  return dictionaries[locale];
}
