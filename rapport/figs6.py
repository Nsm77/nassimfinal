"""rapport/figs6.py — planches transversales : code, accessibilité, mouvement, correspondances."""
from __future__ import annotations

import numpy as np
from matplotlib.patches import Rectangle

from rapport.facts import get, v, c
from rapport.mpl import (ENCRE, OR, PAPIER, PIERRE, ROUILLE, SAUGE, SABLE, arrow, bars, figure,
                         key_for, legend, note, panel, plate, rule)

W = 166.0
HALF = 80.0


@figure("fig51", "Anatomie d'une action serveur : les six garde-fous en ordre", w=W, h=118,
        caption="Coupe de `placeOrderAction` (la plus longue des actions du dépôt), annotée. L'ordre des "
                "garde-fous est celui du code réel : limiteur avant parsing, parsing avant base, verrou "
                "avant écriture.",
        source="src/actions/checkout.ts:41")
def f51(ax, self):
    blocs = [("1 · limiteur de débit", "rateLimit(`order:…`) — 5 min", "attaque par rebond évitée"),
             ("2 · origine", "checkOrigin() — sinon refus", "CSRF sur Server Action"),
             ("3 · session", "getCurrentUser() puis propriété", "usurpation d'identifiant"),
             ("4 · validation", "checkoutSchema.safeParse (Zod)", "types, bornes, longueurs"),
             ("5 · transaction", "db.transaction + FOR UPDATE", "double commande, stock négatif"),
             ("6 · après-coup", "revalidatePath + audit + track", "cache périmé, traçabilité")]
    y = 96
    for i, (t, code, contre) in enumerate(blocs):
        col, hat = key_for(i)
        panel(ax, 8, y, (W - 16) * 0.34, 13, fill=PAPIER, lw=0.7, hatch=hat if i == 4 else None)
        ax.text(10.5, y + 6.5, t, fontsize=6.8, fontweight="bold", va="center", color=ENCRE)
        panel(ax, 12 + (W - 16) * 0.34, y, (W - 16) * 0.34, 13, fill=SABLE, lw=0.7)
        ax.text(14 + (W - 16) * 0.34, y + 6.5, code, fontsize=6.0, va="center", color=ENCRE)
        panel(ax, 16 + (W - 16) * 0.68, y, (W - 16) * 0.30, 13, fill=PAPIER, lw=0.7)
        ax.text(18 + (W - 16) * 0.68, y + 6.5, "protège contre : " + contre, fontsize=5.8, va="center", color=ENCRE)
        if i < len(blocs) - 1:
            arrow(ax, 8 + (W - 16) * 0.17, y, 8 + (W - 16) * 0.17, y - 3, lw=0.7)
        y -= 15
    note(ax, 8, 4.0, "Trame = couche où la perte de donnée serait irréversible. C'est la seule ligne du "
                    "fichier qui mérite un verrou de base de données.", fs=6.1)


@figure("fig52", "Accessibilité : ce qui est réellement en place", w=W, h=96,
        caption="Carte des critères d'accessibilité vérifiés dans le code et la maquette, avec la contrepartie "
                "de conception. Les lignes en attente sont conservées telles quelles : rien n'est coché par "
                "gentillesse.",
        source="src/components/** · §IV.4")
def f52(ax, self):
    crit = [("contraste texte courant ≥ 4,5:1", "palette mesurée", "tenu"),
            ("taille de corps ≥ 18 pt (deck)", "10/10/10 mesuré", "tenu"),
            ("sens non porté par la couleur seule", "trame + libellé", "tenu"),
            ("`prefers-reduced-motion` respecté", "src/app/globals.css", "tenu"),
            ("focus visible sur liens et boutons", "globals.css", "tenu"),
            ("alternatives textuelles des visuels", f"{c('images')} visuels", "à reprendre"),
            ("ordre de tabulation du tiroir panier", "composant drawer", "à reprendre"),
            ("lecture d'écran sur les toasts", "aria-live", "partiel")]
    y = 74
    for i, (nom, preuve, etat) in enumerate(crit):
        col, hat = key_for(0 if etat == "tenu" else (2 if etat == "partiel" else 3))
        panel(ax, 6, y, W - 12, 8.4, fill=PAPIER, lw=0.6, hatch=hat if etat != "tenu" else None)
        ax.text(8.6, y + 4.2, nom, fontsize=6.4, va="center", color=ENCRE)
        ax.text(W * 0.60, y + 4.2, preuve, fontsize=5.8, va="center", color=ENCRE, style="italic")
        ax.text(W - 8, y + 4.2, etat, fontsize=6.2, va="center", ha="right", color=ENCRE, fontweight="bold")
        y -= 9.6
    note(ax, 6, 4.0, "Trois cases restent ouvertes à la livraison : elles sont listées dans la conclusion, "
                    "pas dissimulées sous un « conforme » global.", fs=6.1)


@figure("fig53", "Le mouvement est une donnée du projet, pas un goût", w=W, h=76,
        caption="Les courbes sont tracées depuis les valeurs réelles de `src/lib/motion.ts` : une seule "
                "bézier d'entrée, une de sortie, et des ressorts amortis. Conséquence : aucune animation ne "
                "translate autre chose que transform et opacity.",
        source="src/lib/motion.ts:4-12")
def f53(ax, self):
    fx = get()
    luxe = fx.f["courbe_ease_luxe"][0]
    exit_ = fx.f["courbe_ease_exit"][0]
    x = np.linspace(0, 1, 240)

    def bez(p1, p2, p3, p4):
        t = x[:, None]
        p0 = np.array([0.0, 0.0])
        c1, c2 = np.array([p1, p2]), np.array([p3, p4])
        p1v = np.array([1.0, 1.0])
        u = 1 - t
        return (u ** 3)[:, None] * p0 + 3 * (u ** 2)[:, None] * t * c1 + 3 * u[:, None] * (t ** 2) * c2 + (t ** 3)[:, None] * p1v

    ax.add_patch(Rectangle((22, 14), 56, 48, facecolor=PAPIER, edgecolor=PIERRE, lw=0.6))
    for (courbe, nom, style) in [(luxe, f"EASE_LUXE {luxe}", "-"), (exit_, f"EASE_EXIT {exit_}", "--")]:
        pts = bez(*courbe)
        ax.plot(22 + pts[:, 0] * 56, 14 + pts[:, 1] * 48, style, color=ENCRE, lw=1.1)
    ax.text(24, 58, "progression du déplacement", fontsize=6.2, color=ENCRE)
    ax.text(74, 12, "temps", fontsize=6.2, color=ENCRE, ha="right")
    legend(ax, 24, 8.5, ["entrée (ressort lent)", "sortie (freinée)"], dx=44, fs=5.8)
    plate(ax, 88, 14, 70, 48, title="règles tenues", fill=SABLE)
    for i, l in enumerate([f"{v('presets_motion')} presets partagés (ressorts, fondus, escaliers)",
                           f"durée de référence {v('duree_lente')} s pour une apparition",
                           f"ressort : raideur {v('ressort_lent')[0]}, amortissement {v('ressort_lent')[1]}",
                           "transform + opacity uniquement (pas de layout shift)",
                           f"réduction de mouvement honorée ({v('reduction_mouvement_sites')} site(s) "
                           "déclaratifs dans src/"]):
        note(ax, 90.5, 22 + i * 6.6, "· " + l, fs=5.8)
    note(ax, 22, 68, "Une interface « premium » ne se prouve pas par l'adjectif : elle se prouve par une "
                    "courbe partagée partout et un unique point de définition.", fs=6.2)


@figure("fig54", "Correspondance rapport ↔ deck : 30 glissades, zéro orpheline", w=W, h=88,
        caption="Chaque glissade renvoie à une section du document et, le cas échéant, à une planche. C'est "
                "la figure qui rend le secours possible : si le projecteur tombe, on sait quelle page lire.",
        source="soutenance/slides.py · annexe F")
def f54(ax, self):
    from soutenance.slides import COMPOSITION
    fx = get()
    n = len(COMPOSITION)
    cols = 6
    rows = (n + cols - 1) // cols
    cw, ch = (W - 12) / cols, 12.6
    for i, slide in enumerate(COMPOSITION):
        x = 6 + (i % cols) * cw
        y = 8 + (rows - 1 - (i // cols)) * ch
        col, hat = key_for(0 if not slide.get("annexe") else 4)
        panel(ax, x, y, cw - 2.5, ch - 2.5, fill=PAPIER, hatch=hat, lw=0.55)
        ax.text(x + 1.6, y + 3.0, f"{slide['no']}", fontsize=6.6, fontweight="bold", color=ENCRE, va="center")
        ax.text(x + 1.6, y + 7.6, slide["titre"][:24], fontsize=5.1, color=ENCRE, va="center")
        note(ax, x + 1.6, y + ch - 4.6, "§ " + str(slide.get("section", "—")), fs=4.6)
    note(ax, 6, 3.0, f"{n} glissades composées : {sum(1 for s in COMPOSITION if not s.get('annexe'))} pour "
                     f"l'exposé, {sum(1 for s in COMPOSITION if s.get('annexe'))} en annexe de réponse ; "
                     f"les renvois de figures sont vérifiés par qa2.py.", fs=6.1)
