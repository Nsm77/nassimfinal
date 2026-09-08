import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/ui/primitives";
export const metadata: Metadata = { title: "Conditions générales de vente" };
const S = [
  ["1. Objet", "Les présentes conditions régissent les ventes réalisées sur le site para-cleopatre.tn par Cléopâtre — Espace Santé Beauté, Ezzahra, Tunisie."],
  ["2. Prix", "Les prix sont exprimés en dinars tunisiens (DT) toutes taxes comprises. Les frais de livraison sont indiqués avant validation de la commande."],
  ["3. Commande", "Toute commande vaut acceptation des présentes conditions. Cléopâtre se réserve le droit d'annuler une commande en cas d'indisponibilité ou de suspicion de fraude, avec remboursement intégral."],
  ["4. Paiement", "Paiement à la livraison en espèces, virement bancaire, ou carte cadeau. Le paiement par carte sera proposé prochainement."],
  ["5. Livraison", "Délais indicatifs de 24 à 72 h ouvrées selon le gouvernorat. Le client vérifie l'état du colis à la réception."],
  ["6. Rétractation & retours", "Le client dispose de 7 jours à compter de la réception pour retourner un produit non ouvert, dans son emballage d'origine. Les frais de retour restent à sa charge sauf erreur de notre part."],
  ["7. Garantie", "Tous les produits sont authentiques et proviennent des circuits officiels de distribution. En cas de défaut, contactez-nous sous 48 h."],
  ["8. Données personnelles", "Voir notre politique de confidentialité."],
];
export default function CGVPage() {
  return (<div className="container-lux py-10 lg:py-14"><Breadcrumbs items={[{ label: "CGV" }]} /><header className="mt-6 mb-12 max-w-2xl"><h1 className="font-display text-display-lg text-ink">Conditions générales de vente</h1></header><div className="mx-auto max-w-2xl space-y-8">{S.map(([t, b]) => <section key={t}><h2 className="text-[15px] text-ink">{t}</h2><p className="mt-2 text-sm leading-relaxed text-charcoal">{b}</p></section>)}</div></div>);
}
