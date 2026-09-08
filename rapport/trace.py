"""rapport/trace.py — le squelette de traçabilité (annexe D + annexe F + figures 16/17/21 + deck).

C'est **la** source unique de la chaîne US → sprint → section → figures → vérification → glissade.
Aucune des deux moitiés du harnais (qa.py, qa2.py) ne compte les récits à la main : elles lisent ce
fichier et vérifient, pour chaque ligne, que le fichier cité existe et que le symbole cité s'y trouve.
Un trou dans la table = build rouge (c'est le mécanisme qui remplace la promesse « 0 trou »).
"""
from __future__ import annotations

EPOPEES = {
    "E1": "Identité & accès",
    "E2": "Catalogue & découverte",
    "E3": "Commande & argent",
    "E4": "Exploitation (back-office)",
    "E5": "Confiance & après-vente",
    "E6": "Livrable & preuve",
}

# valeur / effort : estimations de travail déclarées (0..1), pas des mesures.
BACKLOG: list[dict] = [
    dict(id="US-01", epopee="E1", titre="Créer un compte client", sprint="S1",
         regoit="e-mail, mot de passe, nom, téléphone", rend="session ouverte, 0 point de fidélité",
         valeur=0.62, effort=0.34, section="III.2", figures=["fig22", "fig26"],
         fichiers=["src/actions/auth.ts", "src/lib/validation.ts"], symboles=["registerAction", "registerSchema"],
         test="qa.py:check_action_guarded", slide="11"),
    dict(id="US-02", epopee="E1", titre="Se connecter et sortir", sprint="S1",
         regoit="identifiants", rend="cookie de session httpOnly",
         valeur=0.9, effort=0.30, section="II.4", figures=["fig30", "fig22"],
         fichiers=["src/lib/auth.ts", "src/actions/auth.ts"], symboles=["createSession", "loginAction"],
         test="qa.py:check_session_cookie_flags", slide="16a"),
    dict(id="US-03", epopee="E1", titre="Modifier son profil et son mot de passe", sprint="S2",
         regoit="nom, téléphone, ancien mot de passe", rend="hash recalculé, sessions conservées",
         valeur=0.48, effort=0.32, section="III.5", figures=["fig30"],
         fichiers=["src/actions/auth.ts", "src/lib/auth.ts"], symboles=["updateProfileAction", "hashPassword"],
         test="qa.py:check_scrypt_params", slide="16b"),
    dict(id="US-04", epopee="E1", titre="Gérer ses adresses de livraison", sprint="S2",
         regoit="adresse + gouvernorat", rend="adresse par défaut unique",
         valeur=0.44, effort=0.36, section="III.5", figures=["fig29", "fig22"],
         fichiers=["src/actions/auth.ts", "src/lib/tunisia.ts"], symboles=["saveAddressAction", "GOVERNORATES"],
         test="qa.py:check_governorates", slide="11"),
    dict(id="US-05", epopee="E2", titre="Parcourir le catalogue par univers", sprint="S1",
         regoit="slug d'univers", rend="grille paginée, facettes",
         valeur=0.86, effort=0.28, section="III.1", figures=["fig10", "fig33"],
         fichiers=["src/app/(site)/univers/[slug]/page.tsx", "src/lib/catalog.ts"],
         symboles=["listProducts", "getUniverses"], test="qa.py:check_univers_counts", slide="11"),
    dict(id="US-06", epopee="E2", titre="Chercher un produit", sprint="S2",
         regoit="requête texte", rend="produits + pages, événement de recherche",
         valeur=0.7, effort=0.45, section="III.3", figures=["fig22", "fig53"],
         fichiers=["src/app/api/search/route.ts", "src/lib/catalog.ts"], symboles=["quickSearch"],
         test="qa.py:check_search_events_table", slide="11"),
    dict(id="US-07", epopee="E2", titre="Voir une fiche produit complète", sprint="S1",
         regoit="slug produit", rend="prix, stock, avis, routine, composition",
         valeur=0.92, effort=0.4, section="III.1", figures=["figR1", "fig26"],
         fichiers=["src/app/(site)/produit/[slug]/page.tsx", "src/db/schema.ts"],
         symboles=["products", "getProductBySlug"], test="qa.py:check_product_columns", slide="12"),
    dict(id="US-08", epopee="E2", titre="Filtrer par besoin de peau", sprint="S3",
         regoit="11 besoins", rend="sélection croisée univers × besoin",
         valeur=0.58, effort=0.5, section="III.1", figures=["fig03", "fig34"],
         fichiers=["src/db/seed.ts", "src/components/catalog/filters.tsx"], symboles=["concerns"],
         test="qa.py:check_concerns_coverage", slide="12"),
    dict(id="US-09", epopee="E2", titre="Découvrir les marques et leur histoire", sprint="S3",
         regoit="16 marques", rend="pages marque + vitrine",
         valeur=0.4, effort=0.25, section="III.1", figures=["fig34", "fig10"],
         fichiers=["src/app/(site)/marques/page.tsx", "src/db/seed.ts"], symboles=["brands"],
         test="qa.py:check_brands_count", slide="12"),
    dict(id="US-10", epopee="E3", titre="Ajouter au panier sans compte", sprint="S2",
         regoit="produit, quantité", rend="panier persistant, total en millimes",
         valeur=0.95, effort=0.35, section="III.4", figures=["fig27", "fig29"],
         fichiers=["src/components/cart/cart-provider.tsx", "src/lib/money.ts"], symboles=["formatDT"],
         test="qa.py:check_money_integer", slide="13"),
    dict(id="US-11", epopee="E3", titre="Passer commande sans casser le stock", sprint="S2",
         regoit="panier + adresse + mode de paiement", rend="commande, mouvements, événement",
         valeur=1.0, effort=0.72, section="III.4", figures=["fig26", "fig49", "fig22"],
         fichiers=["src/actions/checkout.ts", "src/lib/orders.ts"], symboles=["placeOrderAction", "lockProducts"],
         test="qa.py:check_for_update", slide="13"),
    dict(id="US-12", epopee="E3", titre="Appliquer un code promo", sprint="S3",
         regoit="code", rend="remise ou franco, motifs de rejet explicites",
         valeur=0.66, effort=0.55, section="III.6", figures=["fig28", "fig36"],
         fichiers=["src/lib/promotions.ts", "src/actions/shop.ts"], symboles=["evaluatePromo", "validatePromoAction"],
         test="qa.py:check_promo_reasons", slide="14"),
    dict(id="US-13", epopee="E3", titre="Payer à la livraison ou par virement", sprint="S2",
         regoit="méthode parmi les autorisées", rend="commande créée, statut de paiement en attente",
         valeur=0.8, effort=0.3, section="II.5", figures=["fig30", "fig05"],
         fichiers=["src/lib/payments.ts", "src/lib/validation.ts"], symboles=["enabledPaymentMethods", "checkoutSchema"],
         test="qa.py:check_payment_gate", slide="16a"),
    dict(id="US-14", epopee="E3", titre="Ne pas commander deux fois par erreur", sprint="S4",
         regoit="double clic, recharge", rend="clé d'idempotence, une seule commande",
         valeur=0.78, effort=0.42, section="IV.2", figures=["fig26", "fig47"],
         fichiers=["src/actions/checkout.ts", "src/lib/orders.ts"], symboles=["placeOrderAction", "reserveOrderNumber"],
         test="qa.py:check_idempotence", slide="16b"),
    dict(id="US-15", epopee="E5", titre="Suivre son colis sans compte", sprint="S3",
         regoit="numéro + e-mail (ou clé d'accès)", rend="chronologie des événements",
         valeur=0.72, effort=0.38, section="III.7", figures=["fig49", "fig10"],
         fichiers=["src/app/(site)/suivi/page.tsx", "src/db/schema.ts"], symboles=["orderEvents"],
         test="qa.py:check_guest_access_key", slide="15"),
    dict(id="US-16", epopee="E5", titre="Annuler tant que c'est possible", sprint="S3",
         regoit="commande", rend="statut annulé, stock rendu, points inversés",
         valeur=0.64, effort=0.48, section="III.7", figures=["fig49", "fig27"],
         fichiers=["src/actions/checkout.ts", "src/lib/orders.ts"], symboles=["cancelOrderAction", "restockOrder"],
         test="qa.py:check_restock_symetry", slide="15"),
    dict(id="US-17", epopee="E5", titre="Demander un retour après livraison", sprint="S4",
         regoit="motif", rend="événement horodaté, aucune double demande",
         valeur=0.5, effort=0.4, section="III.7", figures=["fig49"],
         fichiers=["src/actions/checkout.ts"], symboles=["requestReturnAction"],
         test="qa.py:check_transition_table", slide="15"),
    dict(id="US-18", epopee="E5", titre="Laisser un avis modéré", sprint="S4",
         regoit="note, titre, texte", rend="avis en attente puis moyenne recalculée",
         valeur=0.55, effort=0.44, section="IV.4", figures=["fig28", "fig22"],
         fichiers=["src/actions/shop.ts", "src/actions/admin.ts"], symboles=["submitReviewAction", "moderateReviewAction"],
         test="qa.py:check_review_aggregation", slide="14"),
    dict(id="US-19", epopee="E4", titre="Gérer le catalogue depuis l'administration", sprint="S3",
         regoit="formulaire produit", rend="produit + associations + images",
         valeur=0.82, effort=0.6, section="IV.1", figures=["fig40", "fig22"],
         fichiers=["src/actions/admin.ts", "src/components/admin/product-form.tsx"],
         symboles=["saveProductAction", "productSchema"], test="qa.py:check_admin_guards", slide="17a"),
    dict(id="US-20", epopee="E4", titre="Ajuster un stock avec journal", sprint="S3",
         regoit="delta, motif", rend="mouvement + stock après, jamais négatif",
         valeur=0.76, effort=0.45, section="IV.1", figures=["fig37", "fig29"],
         fichiers=["src/actions/admin.ts", "src/lib/orders.ts"], symboles=["adjustStockAction", "recordMovement"],
         test="qa.py:check_stock_invariant", slide="17a"),
    dict(id="US-21", epopee="E4", titre="Faire avancer une commande d'un clic", sprint="S3",
         regoit="nouveau statut", rend="transition validée, événement, revalidation cache",
         valeur=0.88, effort=0.5, section="IV.1", figures=["fig49", "fig22"],
         fichiers=["src/actions/admin.ts", "src/lib/order-constants.ts"],
         symboles=["updateOrderStatusAction", "ALLOWED_TRANSITIONS"], test="qa.py:check_transition_table", slide="17b"),
    dict(id="US-22", epopee="E4", titre="Répondre au support et exporter", sprint="S4",
         regoit="ticket, plage de commandes", rend="réponse, CSV, journal d'audit",
         valeur=0.46, effort=0.52, section="IV.3", figures=["fig40"],
         fichiers=["src/actions/admin.ts", "src/app/api/admin/export/[kind]/route.ts"],
         symboles=["replyTicketAction"], test="qa.py:check_export_route_guarded", slide="17b"),
    dict(id="US-23", epopee="E6", titre="Produire un rapport reproductible", sprint="S4",
         regoit="dépôt", rend="PDF vectoriel + annexe F pleine",
         valeur=0.7, effort=0.6, section="IV.5", figures=["fig42", "fig43", "fig44"],
         fichiers=["rapport/build.py", "rapport/doc.py"], symboles=["build"],
         test="qa.py:check_annexe_f_complete", slide="18"),
    dict(id="US-24", epopee="E6", titre="Tenir la soutenance sans réseau", sprint="S4",
         regoit="30 glissades", rend="kit J, secours L1→L3",
         valeur=0.68, effort=0.35, section="IV.6", figures=["fig45", "fig46"],
         fichiers=["soutenance/slides.py", "audit/kit/JOURJ.md"], symboles=["build_deck"],
         test="qa2.py:check_morph_count", slide="18"),
]


def sprint_stats() -> dict:
    out: dict[str, dict] = {}
    for us in BACKLOG:
        d = out.setdefault(us["sprint"], dict(recits=0, fichiers=set(), epopees=set()))
        d["recits"] += 1
        d["fichiers"].update(us["fichiers"])
        d["epopees"].add(us["epopee"])
    for k, d in out.items():
        d["fichiers"] = sorted(d["fichiers"])
        d["epopees"] = sorted(d["epopees"])
    return out


def figure_usage() -> dict[str, list[str]]:
    """figure → récits qui l'appellent (sert à prouver qu'aucune planche n'est orpheline)."""
    out: dict[str, list[str]] = {}
    for us in BACKLOG:
        for f in us["figures"]:
            out.setdefault(f, []).append(us["id"])
    return out


if __name__ == "__main__":
    print(f"{len(BACKLOG)} récits · {len(EPOPEES)} épopées")
    for s, d in sorted(sprint_stats().items()):
        print(f"  {s}: {d['recits']} récits, {len(d['fichiers'])} fichiers, épopées {','.join(d['epopees'])}")
