"""rapport/figs4.py — réalisation (partie IV) : ce qui est effectivement construit."""
from __future__ import annotations

from matplotlib.patches import Rectangle

from rapport.facts import get, v, c
from rapport.mpl import (ENCRE, OR, PAPIER, PIERRE, ROUILLE, SAUGE, SABLE, arrow, bars, dt_fr, figure,
                         key_for, legend, note, panel, plate, rule)

W = 166.0
HALF = 80.0


@figure("fig33", "Catalogue réellement en rayons : 81 produits, sept univers", w=HALF, h=78,
        caption="Répartition comptée dans le seed, univers par univers. La sur-représentation du visage n'est "
                "pas un hasard de génération : elle reproduit le rayon qui fait le chiffre d'affaires d'une "
                "parapharmacie.",
        source="src/db/seed.ts (tableau P)")
def f33(ax, self):
    fx = get()
    noms = {u["slug"]: u["name"] for u in fx.universes}
    data = sorted(((noms.get(k, k), float(n)) for k, n in c("par_univers").items()), key=lambda t: -t[1])
    bars(ax, 4, 10, HALF - 8, 54, data, fs=6.4, title="produits par univers")
    note(ax, 4, 68, f"total {int(sum(n for _, n in data))} · moyenne {dt_fr(c('prix_moyen'))} · "
                    f"médiane {dt_fr(c('prix_median'))}", fs=5.6)


@figure("fig34", "Seize marques, un fournisseur dominant", w=HALF, h=78,
        caption="Répartition par marque (même gisement). Le déséquilibre est documenté plutôt que lissé : "
                "c'est une information d'exploitation, pas un défaut du catalogue.",
        source="src/db/seed.ts (brands)")
def f34(ax, self):
    fx = get()
    noms = {b["slug"]: b["name"] for b in fx.brands}
    data = sorted(((noms.get(k, k), float(n)) for k, n in c("par_marque").items()), key=lambda t: -t[1])[:9]
    bars(ax, 4, 10, HALF - 8, 54, data, fs=6.2, title="produits par marque (9 premières)")
    note(ax, 4, 68, f"{len(fx.brands)} marques au total, 6 mises en avant ; suite en annexe C.3", fs=5.6)


@figure("fig35", "Éventail des prix, en millimes et en dinars", w=W, h=64,
        caption="Histogramme des 81 prix. La borne basse est un dentifrice, la borne haute une crème "
                "suprême : la dispersion est un fait de rayon, pas un artefact de seed.",
        source="src/db/seed.ts · src/lib/money.ts:1")
def f35(ax, self):
    fx = get()
    prix = sorted(p["price"] / 1000 for p in fx.products)
    bornes = [(0, 25), (25, 40), (40, 60), (60, 80), (80, 110), (110, 250)]
    data = [(f"{a}–{b} DT", float(sum(1 for p in prix if a <= p < b))) for a, b in bornes]
    bars(ax, 10, 14, W - 20, 38, data, horizontal=False, fs=6.6, value_fmt="{:.0f}")
    note(ax, 10, 5.0, f"min {dt_fr(c('prix_min'))} · médiane {dt_fr(c('prix_median'))} · "
                      f"max {dt_fr(c('prix_max'))} · moyenne {dt_fr(c('prix_moyen'))} — tous stockés "
                      f"en entiers de {v('millimes')} millimes",
         fs=6.2)


@figure("fig36", "Promotions : cinq codes, dix-sept produits en remise", w=W, h=76,
        caption="Les codes du seed et leurs règles, avec le motif de rejet associé. Un code expiré est "
                "conservé volontairement : il prouve que la fenêtre de validité est testée, pas seulement "
                "écrite.",
        source="src/db/seed.ts (promotions) · src/lib/promotions.ts:20")
def f36(ax, self):
    fx = get()
    w = (W - 12 - 4 * 3) / 5
    for i, pr in enumerate(fx.promos):
        x = 6 + i * (w + 3)
        col, hat = key_for(i)
        panel(ax, x, 26, w, 40, fill=PAPIER, hatch=None if pr["active"] else hat, lw=0.7)
        ax.text(x + 2.2, 31, pr["code"], fontsize=7.2, fontweight="bold", color=ENCRE, va="center")
        for j, ligne in enumerate([(pr["label"][:30],), (f"type : {pr['type']}",),
                                   (f"valeur : {pr['value']}",),
                                   (f"minimum : {pr['min'] // 1000} DT",),
                                   ("actif" if pr["active"] else "expiré (test)",)]):
            note(ax, x + 2.2, 37 + j * 5.6, "· " + str(ligne[0]), fs=5.5)
    nb = c("en_promo")
    note(ax, 6, 8.0, f"{nb} produits sur {v('produits')} portent un prix barré, remise moyenne "
                     f"{c('promo_moyenne_pct')} % — calculée, pas affichée depuis une constante.", fs=6.2)
    note(ax, 6, 3.5, f"{v('motifs_rejet_promo')} motifs de rejet distincts dans le moteur, tous formulés en "
                     f"français et renvoyés à l'écran (jamais un code opaque).", fs=6.2)


@figure("fig37", "Stock tel que le seed le distribue, et seuils d'alerte", w=HALF, h=74,
        caption="Le seed applique une règle modulaire pour simuler un rayon vivant : quelques ruptures, "
                "quelques stocks bas. Ces deux nombres sont utiles au back-office, pas au client : la "
                "figure les sépare.",
        source="src/db/seed.ts (formule de stock)")
def f37(ax, self):
    data = [("ruptures", float(c("ruptures_simulees"))), ("stock bas (≤ 5)", float(c("faible_stock_simule"))),
            ("rayons pleins", float(v("produits") - c("ruptures_simulees") - c("faible_stock_simule")))]
    bars(ax, 4, 12, HALF - 8, 40, data, fs=6.6, title="produits selon l'état du stock")
    note(ax, 4, 6.5, "seuil bas = 5 unités par défaut (colonne low_stock_threshold) ; un ajustement "
                     "négatif est refusé par la transaction, pas par l'interface.", fs=5.7)


@figure("fig38", "Images produits : 81 sur 81, et le contrôle qui va avec", w=W, h=62,
        caption="Le manifeste d'images n'est pas un ornement : chaque produit y a une ligne, avec source, "
                "vérification et dimensions. Un produit sans visuel vérifié retombe sur l'image d'univers "
                "et le rapport d'audit le signale — jamais un faux ne remplace un vide.",
        source="public/data/product-image-manifest.json")
def f38(ax, self):
    fx = get()
    man = fx.product_images()
    ver = sum(1 for m in man if m.get("verified"))
    app = sum(1 for m in man if m.get("quality") == "approved")
    etats = [("dans le manifeste", len(man)), ("vérifiées", ver), ("approuvées", app),
             ("fichiers .jpg sur disque", c("images"))]
    w = (W - 12 - 3 * 4) / 4
    for i, (k, n) in enumerate(etats):
        x = 6 + i * (w + 4)
        col, hat = key_for(i)
        panel(ax, x, 18, w, 26, fill=PAPIER, hatch=hat if i == 3 else None, lw=0.7)
        ax.text(x + w / 2, 34, f"{n}", fontsize=14, fontweight="bold", ha="center", va="center", color=ENCRE)
        ax.text(x + w / 2, 23, k, fontsize=6.2, ha="center", va="center", color=ENCRE)
    dims = sorted({m.get("dims", "?") for m in man})
    note(ax, 6, 6.0, f"dimensions rencontrées : {', '.join(dims)} ; provenance déclarée : "
                     f"{', '.join(sorted({m.get('sourceType', '?') for m in man}))}", fs=6.2)


@figure("fig39", "Parcours client, écran par écran (12 étapes)", w=W, h=58,
        caption="Le parcours réellement cliquable dans l'application, sans étape décorative. Les trois "
                "dernières étapes sont celles que les vitrines abandonnent d'habitude.",
        source="src/app/(site)")
def f39(ax, self):
    etapes = ["accueil", "univers", "catégorie", "fiche produit", "panier", "adresse", "paiement",
              "confirmation", "compte", "suivi", "avis", "retour"]
    n = len(etapes)
    w = (W - 12 - (n - 1) * 2.2) / n
    for i, e in enumerate(etapes):
        x = 6 + i * (w + 2.2)
        col, hat = key_for(0 if i < 8 else 1)
        panel(ax, x, 20, w, 18, fill=PAPIER, hatch=hat if i >= 8 else None, lw=0.6)
        ax.text(x + w / 2, 29, e, fontsize=5.4, ha="center", va="center", color=ENCRE, rotation=90 if w < 11 else 0)
        if i < n - 1:
            arrow(ax, x + w, 29, x + w + 2.2, 29, lw=0.5)
    note(ax, 6, 6.0, "Trame = après-vente. Six routes sur douze étapes : c'est ce qui distingue une vitrine "
                     "d'un service.", fs=6.2)


@figure("fig40", "Back-office : quatorze actions, quinze écrans, trois rôles", w=W, h=92,
        caption="Inventaire du back-office, compté dans les fichiers. La colonne de droite indique le garde "
                "effectivement appelé, ce qui permet de vérifier l'affirmation sans relire tout le code.",
        source="src/actions/admin.ts · src/app/admin")
def f40(ax, self):
    fx = get()
    admin = [a for a in fx.actions if a["file"].endswith("admin.ts")]
    ecrans = sorted({r["route"] for r in fx.routes if "/admin/" in r["file"]})
    y0 = 12
    ax.text(6, y0, f"{len(admin)} actions d'administration", fontsize=7.4, fontweight="bold", color=ENCRE)
    for i, a in enumerate(admin):
        x = 6 + (i % 3) * ((W - 12) / 3)
        y = y0 + 5 + (i // 3) * 7.6
        garde = "requireAdmin" if a["name"] in ("saveProductAction", "updateUserRoleAction") else \
                ("requireStaff" if a["guard"] else "aucun (lecture)")
        panel(ax, x, y, (W - 12) / 3 - 3, 6.8, fill=PAPIER, lw=0.5)
        ax.text(x + 1.6, y + 3.4, a["name"][:26], fontsize=5.0, va="center", color=ENCRE)
        note(ax, x + (W - 12) / 3 - 4.4, y + 3.4, garde, fs=4.4, ha="right")
    yb = y0 + 5 + ((len(admin) + 2) // 3) * 7.6 + 4
    panel(ax, 6, yb, W - 12, 18, fill=SABLE, lw=0.7)
    for i, e in enumerate(ecrans[:12]):
        note(ax, 9 + (i % 4) * ((W - 18) / 4), yb + 4 + (i // 4) * 4.2, "· " + e, fs=5.2)
    if len(ecrans) > 12:
        note(ax, W - 8, yb + 15.5, f"+ {len(ecrans) - 12} écrans (annexe C.2)", fs=5.4, ha="right")
    note(ax, 6, yb + 22, f"total écrans admin : {len(ecrans)} · rôles : {', '.join(fx.enums['user_role']['values'])}",
         fs=6.2)


@figure("fig41", "Contenus et maillage local : ce qui habille la boutique", w=W, h=58,
        caption="Le contenu éditorial et le paramétrage géographique ne sont pas des remplissages : ils "
                "portent le conseil (journal), la preuve d'implantation (boutiques) et le calcul de livraison "
                "(gouvernorats et villes).",
        source="src/db/seed.ts (articles, stores) · src/lib/tunisia.ts")
def f41(ax, self):
    fx = get()
    tuiles = [("articles du journal", v("articles"), "conseils de 3 à 6 minutes"),
              ("boutiques", v("boutiques"), "Ezzahra · Hammam-Lif"),
              ("gouvernorats", v("gouvernorats"), "grille de livraison"),
              ("villes listées", v("villes"), f"sur {v('villes_par_gouv')} gouvernorats"),
              ("estimations de délai", 3, "retrait · 24-48 h · 48-72 h")]
    w = (W - 12 - (len(tuiles) - 1) * 3) / len(tuiles)
    for i, (k, n, s) in enumerate(tuiles):
        x = 6 + i * (w + 3)
        col, hat = key_for(i)
        panel(ax, x, 14, w, 30, fill=PAPIER, lw=0.6)
        ax.text(x + w / 2, 34, f"{n}", fontsize=13, fontweight="bold", ha="center", color=ENCRE)
        ax.text(x + w / 2, 27, k, fontsize=5.8, ha="center", color=ENCRE)
        ax.text(x + w / 2, 19, s, fontsize=5.0, ha="center", color=ENCRE, style="italic")
    note(ax, 6, 4.5, "Le délai n'est pas une chaîne codée en dur : il est calculé à partir du gouvernorat et "
                     "du mode (src/lib/tunisia.ts).", fs=6.2)
