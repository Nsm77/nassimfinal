"""rapport/figs3.py — conception (partie III) : architecture, flux, modèles."""
from __future__ import annotations

from matplotlib.patches import Ellipse, Rectangle

from rapport.facts import get, v, c
from rapport.mpl import (ENCRE, OR, PAPIER, PIERRE, ROUILLE, SAUGE, SABLE, arrow, bars, figure,
                         key_for, legend, note, panel, plate, rule)

W = 166.0
HALF = 80.0


@figure("fig23", "Architecture en cinq couches, avec la volumétrie réelle", w=W, h=104,
        caption="Chaque couche est un dossier du dépôt, chaque nombre est compté par le générateur. La règle "
                "de circulation est unidirectionnelle : la page ne calcule jamais un prix, l'action ne "
                "formate jamais une vue.",
        source="src/app, src/actions, src/lib, src/db · audit/facts.json")
def f23(ax, self):
    fx = get()
    couches = [("Présentation", f"src/app/(site) · {len([r for r in fx.routes if '(site)' in r['file']])} pages",
                "Server Components, aucun calcul de prix", 0),
               ("Back-office", f"src/app/admin · {len([r for r in fx.routes if '/admin/' in r['file']])} pages",
                "mêmes primitives, rôles distincts", 0),
               ("Orchestration", f"src/actions · {v('actions')} fonctions « use server »",
                "Zod → garde → limiteur → origine → transaction", 1),
               ("Métier", f"src/lib · {len([p for p in fx.f])} faits documentés",
                "money, promotions, orders, payments, auth", 1),
               ("Persistance", f"src/db · {v('tables')} tables, {v('index')} index",
                "Drizzle + pg (pool {max})".format(max=v("pool_max")), 2)]
    for i, (nom, mes, regle, ris) in enumerate(couches):
        y = 8 + i * 18
        col, hat = key_for(i)
        panel(ax, 10, y, W - 20, 15, fill=PAPIER, hatch=hat if ris == 1 else None, lw=0.7)
        ax.text(13, y + 5.0, nom, fontsize=8.0, fontweight="bold", va="center", color=ENCRE)
        ax.text(13, y + 10.4, mes, fontsize=6.2, va="center", color=ENCRE)
        ax.text(W * 0.52, y + 7.5, regle, fontsize=6.2, va="center", color=ENCRE, style="italic")
        if i < len(couches) - 1:
            arrow(ax, W / 2, y + 15, W / 2, y + 18, lw=0.9)
    note(ax, 10, 3.5, "Trame = couche qui parle à la base. Les deux premières ne touchent jamais `db` "
                      "directement : elles appellent une action.", fs=6.1)


@figure("fig24", "Diagramme de composants (12 blocs qui se tiennent)", w=W, h=112,
        caption="Les dépendances sont celles des imports réels, relevés dans le dépôt : pas de composant "
                "bidon ajouté pour remplir la figure.",
        source="grep des imports dans src/")
def f24(ax, self):
    blocs = [("header / footer", 8, 8), ("cart-drawer", 58, 8), ("search-overlay", 100, 8),
             ("product-card", 8, 30), ("filters", 48, 30), ("listing", 88, 30),
             ("buy-box", 8, 52), ("checkout-flow", 52, 52), ("review-form", 106, 52),
             ("auth-forms", 8, 74), ("order-timeline", 52, 74), ("admin controls", 104, 74)]
    for i, (nom, x, y) in enumerate(blocs):
        col, hat = key_for(i)
        plate(ax, x, y, 40, 16, title=nom, sub=None, fill=PAPIER, hatch=hat if "admin" in nom or "checkout" in nom else None)
    liens = [(0, 1), (0, 2), (3, 0), (4, 5), (5, 3), (6, 7), (7, 1), (8, 6), (9, 7), (10, 11), (11, 7)]
    for a, b in liens:
        xa, ya = blocs[a][1] + 20, blocs[a][2] + 8
        xb, yb = blocs[b][1] + 20, blocs[b][2] + 8
        arrow(ax, xa, ya, xb, yb, lw=0.55, color=PIERRE, alpha=0.9)
    note(ax, 8, 96, "Lecture : les composants de saisie convergent tous vers `src/actions/*` ; aucun "
                    "composant ne parle à `src/db`. Vérifié par grep dans qa.py (INV-21).", fs=6.2)


@figure("fig25", "Cas d'usage : trois acteurs, dix-huit buts", w=W, h=118,
        caption="Diagramme de cas d'usage volontairement sans ellipse décorative : chaque bulle est un but "
                "atteignable dans l'application, et son face-à-face se trouve en annexe D.",
        source="annexe D · src/app/**/page.tsx")
def f25(ax, self):
    acteurs = [("Visiteur", 8, 30, ["consulter le catalogue", "chercher", "mettre au panier", "commander sans compte",
                                    "suivre un colis", "lire le journal", "demander un conseil"]),
               ("Client", 62, 30, ["gérer ses adresses", "voir ses commandes", "annuler", "demander un retour",
                                   "noter un produit", "cumuler des points", "mettre en favori"]),
               ("Équipe", 114, 30, ["publier une fiche", "ajuster un stock", "faire avancer une commande",
                                    "modérer un avis", "créer un code promo", "exporter un fichier"])]
    for i, (nom, x, y, buts) in enumerate(acteurs):
        col, hat = key_for(i)
        panel(ax, x, y - 20, 44, 12, fill=SABLE, hatch=hat)
        ax.text(x + 22, y - 14, nom, fontsize=8.4, fontweight="bold", ha="center", va="center", color=ENCRE)
        for j, b in enumerate(buts):
            by = y + j * 10.5
            ax.add_patch(Ellipse((x + 22, by), 42, 7.6, facecolor=PAPIER, edgecolor=ENCRE, lw=0.6))
            ax.text(x + 22, by, b, fontsize=5.8, ha="center", va="center", color=ENCRE)
        panel(ax, x, y - 22, 44, 7 * 10.5 + 6, fill=None, edge=PIERRE, lw=0.5)
    note(ax, 8, 4.0, "Le visiteur a les mêmes droits de lecture que le client : c'est un choix commercial, "
                     "pas une omission de sécurité.", fs=6.2)


@figure("fig26", "Séquence : le passage de commande, minute par minute", w=W, h=118,
        caption="Le diagramme le plus important du mémoire, parce que c'est là que se joue l'argent et le "
                "stock. Les quatre hachures rouges sont les quatre points où une implémentation naïve perd "
                "de la donnée.",
        source="src/actions/checkout.ts:41 · src/lib/orders.ts:67-101")
def f26(ax, self):
    vies = [("Client", 12), ("Page commande", 48), ("placeOrderAction", 84), ("Transaction", 120), ("PostgreSQL", 154)]
    ytop, ybot = 20, 106
    for nom, x in vies:
        panel(ax, x - 12, ytop - 8, 26, 7, fill=SABLE)
        ax.text(x + 1, ytop - 4.5, nom, fontsize=6.0, ha="center", va="center", color=ENCRE, fontweight="bold")
        ax.plot([x + 1, x + 1], [ytop, ybot], color=PIERRE, lw=0.6, ls="--")
    msgs = [(0, 1, "valide le formulaire (Zod)", 0), (1, 2, "POST + origine", 1), (2, 3, "BEGIN", 0),
            (3, 4, "SELECT … FOR UPDATE sur les produits", 1), (4, 3, "prix et stock figés", 0),
            (3, 4, "numéro réservé (jusqu'à 5 tirages)", 0), (3, 4, "INSERT commande + lignes", 0),
            (3, 4, "UPDATE stock − quantités", 1), (3, 4, "INSERT mouvements + événement", 0),
            (2, 1, "clé d'accès à 256 bits", 0), (1, 0, "confirmation", 0), (2, 3, "COMMIT / ROLLBACK", 1)]
    for i, (a, b, txt, danger) in enumerate(msgs):
        y = ytop + 8 + i * 7.1
        xa, xb = vies[a][1] + 1, vies[b][1] + 1
        arrow(ax, xa, y, xb, y, color=ROUILLE if danger else ENCRE, lw=1.0 if danger else 0.7)
        ax.text((xa + xb) / 2, y - 1.8, txt, fontsize=5.3, ha="center", va="bottom", color=ENCRE)
    note(ax, 12, 3.5, "Flèches épaisses = lecture ou écriture sous verrou. Sans elles, deux clics à "
                      "40 ms d'intervalle créent deux commandes et décrémentent deux fois.", fs=6.2)


@figure("fig27", "Activité : du panier à la confirmation, avec toutes les sorties", w=HALF, h=126,
        caption="Les branches d'erreur sont dessinées avec le même poids que le chemin heureux : c'est la "
                "moitié du travail, et celle qu'un mémoire oublie presque toujours.",
        source="src/components/checkout/checkout-flow.tsx · src/lib/promotions.ts")
def f27(ax, self):
    nœuds = [("panier", 40, 8, "rect"), ("adresse + mode", 40, 20, "rect"), ("code promo ?", 40, 33, "los"),
             ("motif de rejet", 66, 33, "rect"), ("stock encore OK ?", 40, 47, "los"), ("panier corrigé", 66, 47, "rect"),
             ("BEGIN", 40, 60, "rect"), ("verrou produits", 40, 71, "rect"), ("rupture ?", 40, 83, "los"),
             ("ROLLBACK", 66, 83, "rect"), ("commande + clés", 40, 96, "rect"), ("COMMIT", 40, 107, "rect"),
             ("confirmation + suivi", 40, 118, "rect")]
    pos = {n: (x, y) for n, x, y, _ in nœuds}
    for nom, x, y, forme in nœuds:
        if forme == "los":
            ax.add_patch(Rectangle((x - 11, y - 4), 22, 8, facecolor=SABLE, edgecolor=ENCRE, lw=0.6,
                                   joinstyle="miter"))
        else:
            panel(ax, x - 14, y - 4.5, 28, 9, fill=PAPIER if nom != "ROLLBACK" else SABLE,
                   hatch="///" if nom in ("motif de rejet", "panier corrigé", "ROLLBACK") else None, lw=0.6)
        ax.text(x, y, nom, fontsize=5.6, ha="center", va="center", color=ENCRE)
    chaine = ["panier", "adresse + mode", "code promo ?", "stock encore OK ?", "BEGIN", "verrou produits",
              "rupture ?", "commande + clés", "COMMIT", "confirmation + suivi"]
    for a, b in zip(chaine, chaine[1:]):
        arrow(ax, pos[a][0], pos[a][1] + 4.5, pos[b][0], pos[b][1] - 4.5, lw=0.7)
    for a, b in [("code promo ?", "motif de rejet"), ("stock encore OK ?", "panier corrigé"), ("rupture ?", "ROLLBACK")]:
        arrow(ax, pos[a][0] + 11, pos[a][1], pos[b][0] - 14, pos[b][1], lw=0.7, color=ROUILLE)


@figure("fig28", "Le moteur de promotions : un seul arbre, deux appelants", w=W, h=92,
        caption="La règle d'ingénierie tient en une phrase : la remise est calculée par une fonction pure, "
                "appelée aussi bien par l'aperçu du panier que par la commande. Un écart entre les deux "
                "signifierait afficher un prix que la commande ne pratique pas.",
        source="src/lib/promotions.ts:20 (evaluate) · src/actions/shop.ts:47 · src/actions/checkout.ts:41")
def f28(ax, self):
    fx = get()
    motifs = fx.counts["par_besoin"]  # (non utilisé, garde la trace du chargement)
    etapes = [("code normalisé", "trim + majuscule"), ("fenêtre de validité", "startsAt / endsAt"),
              ("plafond d'usage", "usageLimit vs usageCount"), ("minimum d'achat", "minSubtotalMillimes"),
              ("univers éligible", "filtre des lignes"), ("type de remise", "percent · fixed · free_shipping"),
              ("plafond de remise", "maxDiscountMillimes"), ("bornage final", "0 ≤ remise ≤ sous-total")]
    w = (W - 16 - (len(etapes) - 1) * 2.6) / len(etapes)
    for i, (t, s) in enumerate(etapes):
        x = 8 + i * (w + 2.6)
        col, hat = key_for(i)
        panel(ax, x, 20, w, 26, fill=PAPIER, hatch=hat if i in (2, 4) else None, lw=0.6)
        ax.text(x + 1.6, 25, t, fontsize=5.6, va="center", color=ENCRE, fontweight="bold")
        ax.text(x + 1.6, 33.5, s, fontsize=4.9, va="center", color=ENCRE)
        if i < len(etapes) - 1:
            arrow(ax, x + w, 33, x + w + 2.6, 33, lw=0.6)
    for lbl, y in [("aperçu du panier (lecture seule)", 60), ("commande (sous verrou)", 74)]:
        plate(ax, 8, y, 60, 10, title=lbl, fill=SABLE)
        arrow(ax, 70, y + 5, 84, 52 + (74 - y) * 0, lw=0.6)
    panel(ax, 86, 52, 72, 34, fill=PAPIER, lw=0.7)
    ax.text(122, 60, "evaluate(promo, lignes)", fontsize=7.0, ha="center", va="center", color=ENCRE,
            fontweight="bold")
    ax.text(122, 69, f"{v('motifs_rejet_promo')} motifs de rejet explicites, en français", fontsize=5.8,
            ha="center", va="center", color=ENCRE)
    note(ax, 8, 4.5, "Conséquence mesurée : le prix affiché dans le panier est, à la ligne près, celui facturé "
                     "à la commande. La QA du kit le revérifie en comparant les deux appelants.", fs=6.2)


@figure("fig29", "Modèle d'argent : l'entier millime, et rien d'autre", w=HALF, h=92,
        caption="Trois décimales légales, un seul type, aucun flottant. Cette figure est la réponse à la "
                "question que le jury pose en premier quand on parle d'e-commerce tunisien.",
        source="src/lib/money.ts:1-14 · src/db/schema.ts (products.price_millimes)")
def f29(ax, self):
    regl = [("1 DT", v("millimes"), "millimes"), ("franco", v("seuil_franco") / 1000, "DT"),
            ("standard", v("frais_standard") / 1000, "DT"), ("express", v("frais_express") / 1000, "DT"),
            ("cadeau", v("frais_cadeau") / 1000, "DT"), ("fidélité / 10 DT", 1, "point")]
    bars(ax, 4, 40, HALF - 8, 38, [(a, float(b)) for a, b, _ in regl], fs=6.2, title="constantes")
    y = 10
    for ligne in ["type Millimes = number", "formatDT → Intl « fr-TN », 3 décimales",
                  "remise = Math.floor (jamais Math.round)",
                  "solde : total = sous-total − remise + livraison"]:
        panel(ax, 4, y, HALF - 8, 6.4, fill=PAPIER, lw=0.5)
        ax.text(6, y + 3.2, ligne, fontsize=5.5, va="center", color=ENCRE)
        y += 7.4
    note(ax, 4, 84, f"aucune colonne du schéma n'est de type décimal ou flottant : {v('tables')} tables "
                    f"balayées", fs=5.8)


@figure("fig30", "Sécurité : sept couches, chacune avec sa preuve", w=W, h=100,
        caption="Une couche de sécurité sans preuve est une intention. Chaque barre ci-dessous est greffée sur "
                "une ligne du dépôt et re-vérifiée par la QA double.",
        source="src/lib/auth.ts · src/lib/rate-limit.ts · src/lib/origin.ts · src/lib/env.ts")
def f30(ax, self):
    fx = get()
    couches = [("Mots de passe", f"scrypt, sel 16 octets, clé 64", "auth.ts:" + str(fx.proofs['scrypt'][0])),
               ("Comparaison", "timingSafeEqual (anti-minuterie)", "auth.ts:" + str(fx.proofs['timing'][0])),
               ("Session", f"{v('bits_session')} bits, {v('jours_session')} j, httpOnly + SameSite=lax", "auth.ts:" + str(fx.proofs['cookie_httpOnly'][0])),
               ("Limiteur", "compteur en base, upsert atomique", "rate-limit.ts:" + str(fx.proofs['rl_atomic'][0])),
               ("Origine", "compare Origin, host, x-forwarded-host", "origin.ts:" + str(fx.proofs['origin_fn'][0])),
               ("Démarrage", f"{v('secrets_interdits')} secrets de démo refusés en production", "env.ts:" + str(fx.proofs['env_boot_refus'][0])),
               ("Accès invité", "numéro non suffisant : e-mail ou clé", "checkout.ts (access_key)")]
    for i, (t, d, s) in enumerate(couches):
        y = 74 - i * 9.6
        col, hat = key_for(i)
        panel(ax, 26, y, W - 34, 8.2, fill=PAPIER, hatch=hat if i in (0, 3, 5) else None, lw=0.6)
        ax.text(28.5, y + 4.1, t, fontsize=6.6, fontweight="bold", va="center", color=ENCRE)
        ax.text(66, y + 4.1, d, fontsize=6.0, va="center", color=ENCRE)
        note(ax, W - 10, y + 4.1, s, fs=5.2, ha="right")
        ax.text(8, y + 4.1, f"L{i + 1}", fontsize=6.0, va="center", ha="center", color=ENCRE)
    note(ax, 8, 3.0, "Trois couches sont tramées car elles protègent contre une attaque chiffrable : "
                    "brute force du mot de passe, rotation d'en-tête contre le limiteur, acceptation silencieuse "
                    "d'un secret de démonstration.", fs=6.1)


@figure("fig31", "Déploiement : ce qui tourne, où, et avec quoi", w=W, h=80,
        caption="Le schéma de déploiement reflète le dépôt, pas l'ambition : PostgreSQL 18 est servi en local "
                "par `embedded-postgres`, aucune image Docker n'est produite (limitation consignée en ADL).",
        source="package.json · src/db/index.ts:12")
def f31(ax, self):
    blocs = [("Navigateur", "React 19, framer-motion", 10, 50), ("Serveur applicatif", f"Next.js {v('ver_next')} · Node 20", 60, 50),
             ("Base de données", f"PostgreSQL {v('ver_embedded_postgres')} (embarquée)", 112, 50),
             ("Fichiers", f"{c('images')} visuels produits, public/", 112, 22),
             ("Journal", "audit_logs, analytics_events", 60, 22), ("Sauvegarde", "[pg_dump, hors dépôt]", 10, 22)]
    for i, (t, s, x, y) in enumerate(blocs):
        col, hat = key_for(i)
        plate(ax, x, y, 44, 20, title=t, sub=s, fill=PAPIER, hatch=hat if i == 5 else None)
    arrow(ax, 54, 60, 60, 60, lw=0.8)
    arrow(ax, 104, 60, 112, 60, lw=0.8)
    arrow(ax, 134, 50, 134, 42, lw=0.7)
    arrow(ax, 112, 32, 104, 32, lw=0.7)
    arrow(ax, 54, 32, 60, 32, lw=0.7)
    note(ax, 10, 6.0, "Pas de conteneur, pas d'orchestrateur : le mémoire dit la vérité du dépôt et consigne "
                     "l'écart dans decisions.md plutôt que de dessiner un logo Docker.", fs=6.2)


@figure("fig32", "Stocké contre calculé : la frontière assumée", w=W, h=84,
        caption="Une colonne de base est une dette permanente. La figure sépare donc ce qui est écrit en base "
                "de ce qui est recalculé à la demande, avec le motif du choix.",
        source="src/db/schema.ts · src/lib/money.ts · src/lib/promotions.ts")
def f32(ax, self):
    stocke = ["prix et remise (figés à la vente)", "adresse de livraison (snapshot)", "nom du produit (snapshot)",
              "mouvements de stock", "événements de commande", "clé d'accès invitée"]
    calcule = ["remise affichée dans le panier", "frais de port (selon sous-total)", "points de fidélité dus",
               "moyenne des avis (recalculée à la modération)", "facettes et compteurs de recherche",
               "estimation de livraison (gouvernorat + mode)"]
    plate(ax, 6, 14, (W - 16) / 2, 60, title="EN BASE — irreproductible", sub="parce que le passé ne se recalcule pas",
          fill=SABLE)
    plate(ax, 11 + (W - 16) / 2, 14, (W - 16) / 2, 60, title="CALCULÉ — jamais stocké", sub="parce qu'une donnée dérivée peut mentir",
          fill=PAPIER)
    for i, s in enumerate(stocke):
        note(ax, 9, 24 + i * 7.6, "· " + s, fs=6.0)
    for i, s in enumerate(calcule):
        note(ax, 14 + (W - 16) / 2, 24 + i * 7.6, "· " + s, fs=6.0)
    note(ax, 6, 4.5, "Exception assumée : la moyenne et le nombre d'avis sont stockés sur la fiche produit, "
                    "mais recalculés dans la même transaction que la modération (admin.ts:189) — la valeur "
                    "stockée n'est jamais une vérité autonome.", fs=6.2)
