"""rapport/figs2.py — méthode Scrum, découpage et inventaire des actions (partie II).

Rappel du cadrage réellement utilisé (gisement : annuaire du dépôt + décisions consignées) :
S0 (cadrage) puis quatre sprints de deux semaines, deux livraisons intermédiaires
R1 = S1 + S2, R2 = S3 + S4. Les dates exactes sont entre crochets : elles relèvent du réel
non public et ne sont donc pas inventées.
"""
from __future__ import annotations

from matplotlib.patches import Rectangle

from rapport.facts import get, v, c
from rapport.mpl import (ENCRE, OR, PAPIER, PIERRE, ROUILLE, SAUGE, SABLE, arrow, bars, figure,
                         key_for, legend, note, panel, plate, rule)

W = 166.0
HALF = 80.0


@figure("fig13", "Maille temporelle : S0 puis quatre sprints de deux semaines", w=W, h=66,
        caption="Le découpage retenu n'est pas décoratif : chaque sprint a un objectif de livraison nommé, "
                "et les deux jalons de soutenance intermédiaire (R1 = S1 + S2, R2 = S3 + S4) correspondent "
                "aux deux moitiés du produit. Les dates sont entre crochets faute de relevé officiel.",
        source="decisions.md (ADL-002) · annexe D.0")
def f13(ax, self):
    seq = [("S0", "cadrage, schéma, maquette", 1.0, ["24 tables", "24 récits", "[dates]"]),
           ("S1", "socle : auth, catalogue", 1.0, [f"{v('routes')} routes", "sessions"]),
           ("S2", "panier, commande, argent", 1.0, ["millimes", "FOR UPDATE"]),
           ("S3", "back-office, stock, promos", 1.0, [f"{v('actions')} actions"]),
           ("S4", "dureté : sécurité, PDF, a11y", 1.0, ["scrypt", "facture"])]
    x0, y0 = 8, 18
    wtot = W - 16
    w = wtot / len(seq)
    for i, (nom, obj, _u, livs) in enumerate(seq):
        x = x0 + i * w
        col, hat = key_for(i)
        panel(ax, x, y0, w - 3, 22, fill=PAPIER if i else SABLE, edge=ENCRE, lw=0.7)
        ax.text(x + 2.2, y0 + 4.6, nom, fontsize=8.6, fontweight="bold", color=ENCRE, va="center")
        ax.text(x + 2.2, y0 + 10.0, obj, fontsize=5.9, color=ENCRE, va="center")
        for j, l in enumerate(livs):
            note(ax, x + 2.2, y0 + 14 + j * 2.6, "· " + l, fs=5.3)
        if i < len(seq) - 1:
            arrow(ax, x + w - 3, y0 + 11, x + w, y0 + 11, lw=0.9)
    rule(ax, x0, x0 + wtot, y0 - 4, color=OR, lw=1.6)
    # jalons R1/R2 au-dessus
    for lbl, pos in [("R1 = S1 + S2", 0.5), ("R2 = S3 + S4", 1.5)]:
        cx = x0 + w * (1 + pos)
        arrow(ax, cx, y0 - 5.5, cx, y0 - 2.2, color=ENCRE, lw=0.8, style="-|>")
        ax.text(cx, y0 - 8.0, lbl, fontsize=6.4, ha="center", va="top", color=ENCRE, fontweight="bold")
    note(ax, 8, 4.5, "S0 n'est pas un sprint : c'est la semaine où le schéma et le backlog ont été figés, "
                    "pour que les quatre suivants n'aient plus qu'à être tenus.", fs=6.2)


@figure("fig14", "Rituels tenus, et ce qu'ils ont réellement changé", w=HALF, h=74,
        caption="Quatre rituels, quatre effets mesurables sur le dépôt. Un rituel sans effet consigné a été "
                "supprimé plutôt que maintenu par habitude.",
        source="decisions.md · audit/rounds/")
def f14(ax, self):
    rituels = [("Revue de sprint", "démarrer la démo par le plus laid", "retiré : démo sur script"),
               ("Rétrospective", "1 faute connue ajoutée par sprint", f"{len(get().counts.get('fautes', [])) or 6} fautes en §9"),
               ("Point quotidien", "bloqué > 30 min → ADL", "5 ADL consignées"),
               ("Gel avant scellement", "2 voies indépendantes", "qa.py ≡ qa2.py")]
    for i, (nom, regle, effet) in enumerate(rituels):
        y = 10 + i * 15
        col, hat = key_for(i)
        panel(ax, 4, y, HALF - 8, 13, fill=PAPIER, hatch=hat if i == 3 else None, lw=0.6)
        ax.text(6.5, y + 3.6, nom, fontsize=6.9, fontweight="bold", color=ENCRE, va="center")
        ax.text(6.5, y + 8.2, "· " + regle, fontsize=5.8, color=ENCRE, va="center")
        note(ax, HALF - 12, y + 8.2, "→ " + effet, fs=5.4, ha="right")
    note(ax, 4, 6.0, "gisement : décisions consignées en decisions.md", fs=5.6)


@figure("fig15", "Definition of Done — douze critères, tous vérifiables", w=W, h=58,
        caption="Un récit n'est terminé que si les douze cases sont cochées par une commande ou un grep, pas "
                "par une impression. C'est cette liste qui a rendu le gel du document possible.",
        source="audit/gates.md · qa.py")
def f15(ax, self):
    crit = [("récit traçable (annexe F)", "figs/F"), ("code typé sans `any`", "tsc"),
            ("montants en millimes", "money.ts"), ("verrou de ligne posé", "orders.ts"),
            ("GARDÉ si écriture", "actions"), ("idempotence testée", "checkout"),
            ("message d'erreur FR", "api.ts"), ("empty/error rendu", "UI"),
            ("N&B + daltonisme", "qa.py"), ("zéro emoji", "qa.py"),
            ("figure légendée", "figs/manifeste"), ("QA double verte", "qa ≡ qa2")]
    n = len(crit)
    w = (W - 12 - (n // 2) * 3) / (n // 2)
    for i, (nom, preuve) in enumerate(crit):
        x = 6 + (i % (n // 2)) * (w + 3)
        y = 30 if i < n // 2 else 10
        col, hat = key_for(i)
        panel(ax, x, y, w, 17, fill=PAPIER, lw=0.6)
        ax.add_patch(Rectangle((x + 1.6, y + 2.0), 3.2, 3.2, facecolor=PAPIER, edgecolor=ENCRE,
                               lw=0.5, hatch="xxx"))
        ax.text(x + 6.6, y + 3.2, nom, fontsize=5.6, color=ENCRE, va="center")
        note(ax, x + 1.6, y + 8.0, "vérif : " + preuve, fs=5.0)
    note(ax, 6, 4.5, "Deux critères sont structurellement impossibles à tricher : la QA double (deux codes "
                    "différents, mêmes sorties) et la traçabilité (trou = build rouge).", fs=6.2)


@figure("fig16", "Backlog : 24 récits regroupés en 6 épopées", w=W, h=70,
        caption="Le backlog n'a pas été écrit pour le mémoire puis implanté : les 24 récits listés en annexe D "
                "correspondent à des fichiers du dépôt. La figure montre la répartition et le sprint porteur.",
        source="annexe D · src/actions, src/app")
def f16(ax, self):
    from rapport.trace import BACKLOG
    epis = {}
    for us in BACKLOG:
        epis.setdefault(us["epopee"], []).append(us)
    n = len(epis)
    w = (W - 12 - (n - 1) * 3) / n
    for i, (nom, lst) in enumerate(epis.items()):
        x = 6 + i * (w + 3)
        col, hat = key_for(i)
        panel(ax, x, 14, w, 42, fill=PAPIER, hatch=hat, lw=0.7)
        ax.text(x + 2.2, 17.5, nom, fontsize=6.4, fontweight="bold", color=ENCRE, va="top")
        ax.text(x + 2.2, 22.5, f"{len(lst)} récits", fontsize=5.8, color=ENCRE, va="top")
        for j, us in enumerate(lst):
            note(ax, x + 2.2, 27 + j * 3.0, f"{us['id']} · {us['titre'][:26]}", fs=4.9)
        note(ax, x + 2.2, 10.5, "sprint : " + "/".join(sorted({u["sprint"] for u in lst})), fs=5.2)
    note(ax, 6, 4.5, f"Total : {len(BACKLOG)} récits, tous reliés à un fichier du dépôt et à une "
                     f"vérification (annexe F).", fs=6.2)


@figure("fig17", "Charge par sprint, en récits et en fichiers touchés", w=HALF, h=72,
        caption="La charge acceptée par sprint, comptée en récits (annexe D) et en fichiers du dépôt marqués "
                "comme touchés par ce lot. Un sprint surchargé aurait été coupé, pas étiré.",
        source="annexe D · rapport/trace.py")
def f17(ax, self):
    from rapport.trace import BACKLOG
    par = {}
    for us in BACKLOG:
        par.setdefault(us["sprint"], [0, 0])
        par[us["sprint"]][0] += 1
        par[us["sprint"]][1] += len(us["fichiers"])
    data = [(k, float(v[0])) for k, v in sorted(par.items())]
    bars(ax, 4, 12, HALF - 8, 26, data, fs=6.2, title="récits par sprint")
    data2 = [(k, float(v[1])) for k, v in sorted(par.items())]
    bars(ax, 4, 46, HALF - 8, 20, data2, fs=6.2, title="fichiers touchés")
    note(ax, 4, 68, "R1 = S1+S2, R2 = S3+S4 : les deux jalons portent chacun la moitié du produit.", fs=5.7)


@figure("fig18", "Qui fait quoi : RACI des six jalons", w=W, h=52,
        caption="Un mémoire mené par une seule personne n'échappe pas à la question : qui valide ? Le RACI "
                "nomme l'encadrant, l'exploitant et le soutenant sur chaque jalon. Les initiales sont "
                "[à compléter] par l'auteur, pas par le générateur.",
        source="decisions.md")
def f18(ax, self):
    jalons = ["gel du périmètre", "schéma + seed", "checkout + argent", "back-office", "dureté sécurité", "kit + scellement"]
    act = ["développeur", "exploitant", "encadrant", "jury"]
    mat = [("A", "I", "R", "I"), ("R", "C", "A", "I"), ("R", "A", "C", "I"), ("R", "C", "I", "I"),
           ("R", "I", "A", "C"), ("R", "I", "A", "A")]
    x0, y0 = 40, 12
    cw = (W - x0 - 6) / len(jalons)
    for j, nom in enumerate(jalons):
        ax.text(x0 + j * cw + cw / 2, y0 + 2, nom, fontsize=5.6, rotation=32, ha="left", va="bottom", color=ENCRE)
    for i, role in enumerate(act):
        y = y0 + 20 + i * 7
        ax.text(x0 - 2, y, role, fontsize=6.4, ha="right", va="center", color=ENCRE, fontweight="bold")
        for j in range(len(jalons)):
            col, hat = key_for("RACI".index(mat[j][i]))
            panel(ax, x0 + j * cw + 1, y - 3, cw - 2, 6, fill=PAPIER, lw=0.5)
            ax.text(x0 + j * cw + cw / 2, y, mat[j][i], fontsize=6.2, ha="center", va="center", color=ENCRE)
    legend(ax, x0, y0 + 48, ["R : réalisateur", "A : approbateur", "C : consulté", "I : informé"], dx=38, fs=5.6)


@figure("fig19", "Flux de valeur d'une commande, du clic au comptoir", w=W, h=56,
        caption="Le temps de traversée n'est pas mesuré ici : il dépend de la production. La figure ne montre "
                "donc que les états traversés par la donnée, avec ce qui est automatique et ce qui est humain.",
        source="src/lib/order-constants.ts · src/actions/admin.ts:19")
def f19(ax, self):
    etapes = [("clic « Commander »", "auto"), ("vérification stock", "auto"), ("numéro réservé", "auto"),
              ("événement d'état", "auto"), ("préparation", "humain"), ("transporteur", "humain"),
              ("livré + payé", "humain"), ("points de fidélité", "auto")]
    n = len(etapes)
    w = (W - 12 - (n - 1) * 3) / n
    for i, (t, qui) in enumerate(etapes):
        x = 6 + i * (w + 3)
        col, hat = key_for(0 if qui == "auto" else 1)
        panel(ax, x, 16, w, 22, fill=PAPIER, hatch=None if qui == "auto" else hat, lw=0.7)
        ax.text(x + 2, 22.5, t, fontsize=5.5, color=ENCRE, va="center")
        note(ax, x + 2, 30.0, qui, fs=5.2)
        if i < n - 1:
            arrow(ax, x + w, 27, x + w + 3, 27, lw=0.7)
    note(ax, 6, 6.5, "Trame = intervention humaine. Quatre maillons sur huit restent humains : c'est le "
                    "résultat honnête d'un commerce à deux comptoirs, pas une lacune du logiciel.", fs=6.1)


@figure("fig20", "Changements de périmètre consignés (ADL)", w=HALF, h=64,
        caption="Aucun ajout n'a été fait en silence : chaque écart de périmètre porte une entrée "
                "ADL (accord, décision, lie du changement) dans `decisions.md`. Le nombre affiché est compté dans "
                "le fichier, pas déclaré.",
        source="decisions.md")
def f20(ax, self):
    import re
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "decisions.md"
    n = 0
    lignes: list[str] = []
    if p.exists():
        lignes = [l for l in p.read_text(encoding="utf-8").splitlines() if re.match(r"^### ADL-\d+", l)]
    n = len(lignes)
    data = [(l.split("—", 1)[-1].strip()[:34] if "—" in l else l[4:38], 1.0) for l in lignes[:6]] or \
           [("decisions.md à écrire", 1.0)]
    bars(ax, 4, 14, HALF - 8, 34, data, fs=6.0, title="entrées ADL", value_fmt="{:.0f}", unit="")
    note(ax, 4, 6.0, f"{n} entrée(s) ADL comptée(s) dans decisions.md", fs=6.0)


@figure("fig21", "Valeur × effort : ce qui a été fait en premier", w=W, h=74,
        caption="Les 24 récits placés selon la valeur métier perçue et l'effort estimé au sprint 0. Les "
                "coordonnées sont des estimations de travail (déclarées comme telles), pas des mesures ; "
                "l'ordre qu'elles imposent, lui, est vérifiable dans la chronologie des commits.",
        source="annexe D · git log")
def f21(ax, self):
    from rapport.trace import BACKLOG
    x0, y0, w, h = 16, 16, W - 30, 48
    ax.add_patch(__import__("matplotlib").patches.Rectangle((x0, y0), w, h, facecolor=PAPIER,
                                                            edgecolor=PIERRE, lw=0.7))
    ax.plot([x0, x0 + w], [y0 + h / 2, y0 + h / 2], color=PIERRE, lw=0.5, ls="--")
    ax.plot([x0 + w / 2, x0 + w / 2], [y0, y0 + h], color=PIERRE, lw=0.5, ls="--")
    for us in BACKLOG:
        cx = x0 + w * us["effort"]
        cy = y0 + h * (1 - us["valeur"])
        col, hat = key_for({"S1": 0, "S2": 1, "S3": 2, "S4": 3, "S0": 4}.get(us["sprint"], 5))
        ax.add_patch(__import__("matplotlib").patches.RegularPolygon((cx, cy), 4, radius=2.4,
                                                                      orientation=0.78, facecolor=col,
                                                                      edgecolor=ENCRE, lw=0.6, hatch=hat or None))
        ax.text(cx + 3.2, cy, us["id"], fontsize=5.0, va="center", color=ENCRE)
    ax.text(x0, y0 - 4, "effort estimé →", fontsize=6.0, color=ENCRE)
    ax.text(x0 - 3, y0 + h, "← valeur", fontsize=6.0, color=ENCRE, rotation=90, va="top", ha="right")
    legend(ax, x0 + w - 60, y0 + h + 3, ["S1", "S2", "S3", "S4"], dx=13, fs=5.6)
    note(ax, 6, 4.5, "Quadrant haut-gauche (valeur forte, effort faible) : traité au sprint 1. Quadrant "
                    "bas-droit : consigné hors périmètre avec accord.", fs=6.0)


@figure("fig22", "Les 30 actions serveur et leurs garde-fous", w=W, h=148,
        caption="C'est la figure de vérité de la partie II : chaque ligne est une fonction exportée de "
                "`src/actions/*.ts`, chaque colonne un garde-fou grepé dans son corps. Une case vide n'est "
                "pas un oubli de mise en forme : c'est une décision assumée (lecture seule) ou une dette.",
        source="src/actions/{auth,shop,checkout,admin}.ts")
def f22(ax, self):
    fx = get()
    actes = fx.actions
    cols = [("zod", "zod"), ("garde", "guard"), ("rate", "rate"), ("orig.", "origin"),
            ("txn", "tx"), ("verrou", "lock"), ("lignes", "lines")]
    x0, ytop = 44, 136
    rh = 3.5
    ncol = len(cols)
    cw = (W - x0 - 6) / ncol
    for j, (nom, _) in enumerate(cols):
        ax.text(x0 + j * cw + cw / 2, ytop + 2.5, nom, fontsize=6.0, ha="center", va="bottom",
                color=ENCRE, fontweight="bold")
    cur_file = None
    for i, a in enumerate(actes):
        y = ytop - i * rh
        if a["file"] != cur_file:
            cur_file = a["file"]
            ax.text(4, y + rh / 2, cur_file.replace("src/actions/", ""), fontsize=5.6,
                    color=OR, fontweight="bold", va="center")
        ax.text(x0 - 2, y + rh / 2, a["name"], fontsize=4.9, ha="right", va="center", color=ENCRE)
        for j, (_, key) in enumerate(cols):
            cx = x0 + j * cw
            if key == "lines":
                ax.text(cx + cw / 2, y + rh / 2, str(a["lines"]), fontsize=4.6, ha="center",
                        va="center", color=ENCRE, alpha=0.8)
            else:
                ok = bool(a[key])
                ax.add_patch(__import__("matplotlib").patches.Rectangle(
                    (cx + cw * 0.3, y + rh * 0.18), cw * 0.4, rh * 0.64,
                    facecolor=PAPIER if ok else PIERRE, edgecolor=ENCRE, lw=0.4,
                    hatch="///" if not ok else None, alpha=1.0 if ok else 0.7))
    note(ax, 4, 3.0, f"{len(actes)} actions · {v('actions_zod')} avec validation Zod · "
                     f"{v('actions_rate')} avec limiteur de débit · {v('actions_tx')} dans une transaction. "
                     f"Case claire = présent ; case tramée = absent.", fs=6.0)
