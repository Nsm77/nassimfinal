"""rapport/figref.py — figR1 et figX1…figX6 : les 24 tables, dessinées depuis le schéma.

Ces six planches et la planche d'ensemble sont le gisement visuel de l'annexe B : elles ne sont pas
redessinées à la main, elles sont **composées** à partir de `facts.tables` (colonnes, contraintes,
index, clés étrangères). Si le schéma change, la planche change et le build refuse toute table
qui ne serait couverte par aucun domaine : c'est le mécanisme qui remplace la promesse « à jour ».
"""
from __future__ import annotations

from matplotlib.patches import Rectangle

from rapport.facts import get, v
from rapport.mpl import (ENCRE, OR, PAPIER, PIERRE, ROUILLE, SAUGE, SABLE, arrow, figure,
                         key_for, note, panel, plate, register, rule)

W = 166.0
NCOL_R1 = 4
LIGNE_H = 2.55      # hauteur d'une ligne de colonne, en mm
ENTETE_H = 5.2


# Noms TS (tels qu'ils apparaissent dans src/db/schema.ts) — vérifiés à l'import, sinon build refusé.
DOMAINES = {
    "X1 · Identité & accès": ["users", "sessions", "addresses"],
    "X2 · Catalogue": ["brands", "categories", "concerns", "products", "productConcerns", "articles", "stores"],
    "X3 · Ventes": ["orders", "orderItems", "orderEvents", "promotions", "inventoryMovements"],
    "X4 · Engagement": ["reviews", "wishlistItems", "loyaltyTransactions", "newsletterSubscribers", "supportTickets"],
    "X5 · Exploitation": ["auditLogs", "searchEvents", "analyticsEvents", "rateLimits"],
    "X6 · Sûreté de fonctionnement": ["sessions", "rateLimits", "auditLogs", "inventoryMovements"],
}


def _hauteur_boite(t, max_cols: int) -> float:
    n = len(t.cols)
    n_shown = min(n, max_cols)
    h = ENTETE_H + 1.6 + n_shown * LIGNE_H + 1.6
    if n > n_shown:
        h += 2.4
    if t.indexes:
        h += 2.6
    return h


def _layout_r1(max_cols: int = 10) -> tuple[list, float]:
    """Prépare la planche **avant** de la dessiner : la hauteur du PDF en découle, donc rien ne déborde."""
    fx = get()
    tables = [t for t in fx.tables]
    largeur = (W - 12 - (NCOL_R1 - 1) * 4) / NCOL_R1
    colonnes = [[] for _ in range(NCOL_R1)]
    ys = [0.0] * NCOL_R1
    i = 0
    while i < len(tables):
        c = i % NCOL_R1
        colonnes[c].append((tables[i], ys[c]))
        ys[c] += _hauteur_boite(tables[i], max_cols) + 3.0
        i += 1
    return colonnes, max(ys)


def _boite_table(ax, t, x, y, w, *, max_cols=99, fs=4.6, show_idx=True):
    n_col = len(t.cols)
    n_shown = min(n_col, max_cols)
    box_h = _hauteur_boite(t, max_cols)
    panel(ax, x, y, w, box_h, fill=PAPIER, lw=0.55)
    ax.add_patch(Rectangle((x, y), w, ENTETE_H, facecolor=SABLE, edgecolor=ENCRE, lw=0.55))
    ax.text(x + 1.8, y + ENTETE_H / 2, t.sql, fontsize=fs + 1.1, va="center", ha="left", color=ENCRE,
            fontweight="bold")
    ax.text(x + w - 1.8, y + ENTETE_H / 2, f"{n_col}", fontsize=fs - 0.2, va="center", ha="right", color=ENCRE,
            style="italic")
    yy = y + ENTETE_H + 1.8
    for col in t.cols[:n_shown]:
        marque = "◆" if "PK" in col.flags else ("◇" if col.fk else ("●" if "non NULL" in col.flags else "○"))
        texte = f"{marque} {col.sql} : {col.kind}"
        extras = []
        if col.enum:
            extras.append("« " + col.enum + " »")
        if col.fk:
            extras.append("→ " + col.fk.split(".")[0])
        if any("UNIQUE" in f for f in col.flags):
            extras.append("uniq")
        if extras:
            texte += "  (" + ", ".join(extras) + ")"
        ax.text(x + 1.8, yy, texte[:94], fontsize=fs, va="center", color=ENCRE)
        yy += LIGNE_H
    if n_col > n_shown:
        note(ax, x + 1.8, yy, f"… {n_col - n_shown} autres colonnes en annexe B", fs=fs - 0.4)
        yy += 2.4
    if show_idx and t.indexes:
        note(ax, x + 1.8, yy + 0.4, f"index : {len(t.indexes)} · gisement src/db/schema.ts:{t.line}", fs=fs - 0.6)
    return box_h


def _choisir_max_cols() -> int:
    """Le nombre de colonnes affichées est **calculé** pour tenir sur la page, pas décrété.

    Hauteur utile = 297 mm de page − 2 × 20 mm de marge − 22 mm réservés à la légende
    = 235 mm. Au-delà, on réduit l'extrait de chaque boîte (le reste part en annexe B).
    """
    for mc in range(10, 3, -1):
        _, h = _layout_r1(mc)
        if h + BANDEAU_R1 + 14 <= 235:
            return mc
    raise RuntimeError("figR1 impossible à tenir sur une page : réduire le nombre de colonnes affichées")


BANDEAU_R1 = 26.0
_MAX_COLS_R1 = _choisir_max_cols()
_COLONNES_R1, _HAUTEUR_R1 = _layout_r1(_MAX_COLS_R1)


@figure("figR1", "Les 24 tables du schéma, d'un seul regard", w=W,
        h=_HAUTEUR_R1 + BANDEAU_R1 + 14,
        caption="Planche de référence du mémoire : chaque boîte est une table de `src/db/schema.ts`, chaque "
                "ligne une colonne, chaque marque un rôle (◆ clé primaire, ◇ clé étrangère, ● non NULL, ○ "
                "NULL autorisé). Les compteurs du bandeau sont lus dans le même fichier que les boîtes.",
        source="src/db/schema.ts")
def fr1(ax, self):
    fx = get()
    xw = (W - 12 - (NCOL_R1 - 1) * 4) / NCOL_R1
    for ci, colonne in enumerate(_COLONNES_R1):
        y = 6.0
        for t, _ in colonne:
            h = _boite_table(ax, t, 6 + ci * (xw + 4), y, xw, max_cols=_MAX_COLS_R1, fs=4.5)
            y += h + 3.0
    bas = 6.0 + _HAUTEUR_R1 + 3
    panel(ax, 6, bas, W - 12, BANDEAU_R1 - 4, fill=SABLE, lw=0.7)
    compteurs = [("tables", v("tables")), ("colonnes", v("colonnes")), ("index", v("index")),
                 ("clés étrangères", v("cle_etrangeres")), ("enums", v("enums")),
                 ("statuts de commande", v("statuts_commande"))]
    for i, (k, val) in enumerate(compteurs):
        x = 10 + i * ((W - 20) / len(compteurs))
        ax.text(x, bas + 13, f"{val}", fontsize=11.5, fontweight="bold", color=ENCRE, va="center")
        ax.text(x, bas + 6, k, fontsize=5.8, color=ENCRE, va="center")
    note(ax, 6, bas + BANDEAU_R1 + 1.5,
         "Lecture recommandée : zoom 400 % — le texte reste du texte (TrueType incorporé), donc la planche "
         "est sélectionnable dans le PDF et nette sur papier.", fs=6.1)


def _domaine(ax, self, cle: str, max_cols: int = 14):
    fx = get()
    tables = {t.ts: t for t in fx.tables}
    noms = DOMAINES[cle]
    n = len(noms)
    wcol = (W - 12 - (n - 1) * 4) / n
    for i, key in enumerate(noms):
        t = tables[key]
        x = 6 + i * (wcol + 4)
        h = _boite_table(ax, t, x, 14, wcol, max_cols=max_cols, fs=4.4)
        note(ax, x + 1.8, 14 + h + 1.4, f"{len(t.cols)} colonnes · schema.ts:{t.line}", fs=4.6)
        if i < n - 1:
            tb = tables[noms[i + 1]]
            lie = any(c.fk and c.fk.split(".")[0] in (noms[i + 1],) for c in tb.cols) or \
                  any(c.fk and c.fk.split(".")[0] == key for c in tb.cols)
            if lie:
                arrow(ax, x + wcol, 20, x + wcol + 4, 20, lw=0.8, color=OR, rad=0.15)


def _verrou_domaines() -> None:
    connus = {t.ts for t in get().tables}
    inconnus = sorted({n for lst in DOMAINES.values() for n in lst} - connus)
    if inconnus:
        raise RuntimeError(f"domaines de figref hors schéma : {inconnus}")
    couverts = {n for k, lst in DOMAINES.items() if not k.startswith("X6") for n in lst}
    if connus - couverts:
        raise RuntimeError(f"tables non couvertes par un domaine : {sorted(connus - couverts)}")


def _make(cle: str, n: int):
    def _fn(ax, self):
        _domaine(ax, self, cle, max_cols=14)
        note(ax, 6, self.height_mm - 6.0,
             f"domaine {cle} · {n} tables · flèche dorée = clé étrangère entrante depuis la boîte voisine",
             fs=6.1)
    return _fn


_verrou_domaines()
for _cle in DOMAINES:
    _n = len(DOMAINES[_cle])
    register("fig" + _cle.split(" ")[0], f"Détail {_cle.split(' · ')[0]} — {_cle.split(' · ')[1]}",
             _make(_cle, _n), w=W, h=112, source="src/db/schema.ts",
             caption=f"Zoom du domaine {_cle.split(' · ')[0]} : {_n} colonnes retenues à l'échelle du chapitre ; la "
                     f"liste intégrale, sans troncature, est reportée en annexe B pour le domaine {_cle.split(' · ')[0]}.")
