"""rapport/ab.py — confrontation des deux harnais : le même serment, deux machines.

`qa.py` lit le texte (pypdf + voisinage dans les fichiers écrits) ; `qa2.py` lit le rendu (PyMuPDF,
géométrie des spans, polices) et recompte l'application avec des outils du shell. Cette confrontation
ne demande pas « êtes-vous d'accord ? » : elle **mesure** l'écart, loi par loi, et refuse l'ouvrage
tant qu'un désaccord reste ouvert.

Un accord obtenu en écrivant le second harnais *après* le premier ne vaut rien : les quatre écarts
trouvés à la première exécution de `qa2.py` sont consignés ci-dessous et dans
`audit/ab/harnais.md`, avec la règle qui a dû être réécrite.

Sorties : `audit/ab/harnais.json`, `audit/ab/harnais.md`. Code de sortie 1 si divergence.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
AUDIT = RACINE / "audit"

METHODES = {
    "QA-1": ("package.json + texte du PDF, voisinage", "spans du PDF + triple de version exact"),
    "QA-2": ("grammaire de `facts.py` (ast)", "grep et find dans le dépôt"),
    "QA-3": ("liste des fichiers écrits par le kit", "`stat` sur chaque chemin cité"),
    "QA-4": ("regex sur le texte extrait", "regex sur les spans non verbatim"),
    "QA-5": ("fenêtre de ±26 caractères autour du mot", "fonte du span porteur + ligne de prose "
             "déclarée + détection de langue"),
    "QA-6": ("registre de composition", "outline PyMuPDF"),
    "QA-7": ("comptage à la composition", "destinations d'annotations lues dans le fichier"),
    "QA-8": ("ratios renvoyés par matplotlib", "points lus par PyMuPDF contre pixels lus par PIL"),
    "QA-9": ("tables de pictogrammes", "plans de code de chaque span"),
    "QA-10": ("arborescence du kit, motif par motif", "grep -rIn du dépôt, .env suivis par git"),
    "QA-11": ("python-pptx, modèle d'objet", "zip + regex sur le XML, nom de zone"),
    "QA-12": ("nombresFR sur la source", "regex sur les spans du rendu"),
    "QA-13": ("voisinage de caractères dans la ligne", "recouvrement d'ordonnées et blanc physique"),
}

ECARTS_INSTRUITS = [
    dict(titre="la fonte du corps n'est pas Helvetica",
         rencontre="qa2 exemptait le verbatim en cherchant « mono » dans une police censée être "
                   "Times/Helvetica : 0 span de prose trouvé, donc 0 faute déclarée par silence.",
         regle="le moteur enregistre DejaVu pour le rapport entier ; la discrimination se fait sur "
               "« Mono » dans le nom de fonte, et le nombre de spans tenus à part est imprimé"),
    dict(titre="le seau par ordonnée recolle deux cellules",
         rencontre="en regroupant les spans par `y` arrondi, la deuxième ligne d'une cellule se "
                   "retrouvait dans la première de la voisine : sept mots coupés, dix-huit emprunts "
                   "anglais imaginaires.",
         regle="une ligne visuelle = un bloc et une ordonnée de ligne, tels que le moteur de texte les "
               "donne ; plus de reconstruction à la main"),
    dict(titre="une ligne justifiée écarte les mots de onze points",
         rencontre="le critère « écart horizontal > un espace » pour couper une ligne rendait huit "
                   "« lignes » commençant par « : », donc huit fautes d'insécable introuvables à l'œil.",
         regle="le blanc ne tranche plus la ligne ; la fonte tranche la nature du texte (verbatim), et "
               "la marque d'identifiant est cherchée à ±2 caractères"),
    dict(titre="la région anglaise ne se déduit pas d'un titre",
         rencontre="qa.py bornait l'abstract entre deux titres « Abstract » ; le mot reparaît en titre "
                   "courant et la région se refermait sur rien — la ligne fautive restait dans le champ.",
         regle="qa2 juge la **langue de la ligne** par ses mots outils, et consigne le nombre de lignes "
               "anglaises tenues hors du champ (huit au dernier rendu)"),
]


def _lu(nom: str) -> dict:
    return json.loads((AUDIT / nom).read_text(encoding="utf-8"))


def confronter(*, silencieux: bool = False) -> dict:
    t0 = time.time()
    a, b = _lu("qa.json"), _lu("qa2.json")
    par_a = {c["code"]: c for c in a["controles"]}
    par_b = {c["code"]: c for c in b["controles"]}
    codes = sorted(set(par_a) | set(par_b))
    lignes, divergences = [], []
    for code in codes:
        ca, cb = par_a.get(code), par_b.get(code)
        if ca is None or cb is None:
            divergences.append(f"{code} : un seul harnais la juge")
            verdict = "divergent"
        elif ca["verdict"] != cb["verdict"]:
            divergences.append(f"{code} : qa={ca['verdict']} contre qa2={cb['verdict']}")
            verdict = "divergent"
        else:
            verdict = ca["verdict"]
        lignes.append(dict(code=code, verdict=verdict, qa_verdict=(ca or {}).get("verdict"),
                           qa2_verdict=(cb or {}).get("verdict"),
                           qa=dict(mesure=ca.get("mesure"), detail=str(ca.get("detail", ""))[:220])
                           if ca else None,
                           qa2=dict(mesure=cb.get("mesure"), detail=str(cb.get("detail", ""))[:220])
                           if cb else None,
                           methodes=METHODES.get(code, ("?", "?"))))
    recu = dict(harnais="ab.py", lois=len(codes),
                accord=sum(1 for l in lignes if l["verdict"] in ("vert",)),
                divergences=divergences, verdict="vert" if not divergences else "rouge",
                secondes=round(time.time() - t0, 2),
                note="l'accord porte sur le verdict de chaque loi ; les mesures diffèrent par nature "
                     "(le premier harnais compte des fichiers, le second des spans) et c'est voulu")
    (AUDIT / "ab").mkdir(parents=True, exist_ok=True)
    (AUDIT / "ab/harnais.json").write_text(
        json.dumps(dict(recu, lignes=lignes, ecarts_instruits=ECARTS_INSTRUITS), ensure_ascii=False,
                   indent=1, sort_keys=True) + "\n", encoding="utf-8")
    md = ["# Confrontation des harnais `qa.py` et `qa2.py`", "",
          f"Verdict : **{recu['verdict']}** sur {len(codes)} lois, {recu['accord']} accords, "
          f"{len(divergences)} divergence(s), {recu['secondes']} s.", "",
          "| loi | `qa.py` | `qa2.py` |", "| --- | --- | --- |"]
    for code in codes:
        l = next(x for x in lignes if x["code"] == code)
        md.append(f"| {code} | {METHODES[code][0]} | {METHODES[code][1]} |")
    md += ["", "## Écarts trouvés à la première exécution, et la règle qui a dû être réécrite", ""]
    for i, e in enumerate(ECARTS_INSTRUITS, 1):
        md += [f"{i}. **{e['titre']}** — rencontre : {e['rencontre']} Règle retenue : {e['regle']}", ""]
    md += ["## Verdicts loi par loi", "", "| loi | qa | qa2 | confrontation |", "| --- | --- | --- | --- |"]
    for l in lignes:
        md.append(f"| {l['code']} | {l['qa_verdict'] or '—'} | {l['qa2_verdict'] or '—'} | "
                  f"{l['verdict']} |")
    if divergences:
        md += ["", "## Divergences ouvertes", ""] + [f"- {d}" for d in divergences]
    (AUDIT / "ab/harnais.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    if not silencieux:
        for l in lignes:
            marque = "accord" if l["verdict"] != "divergent" else "DIVERGENT"
            print(f"{l['code']:>6}  {marque:>10}  qa {l['qa']['mesure'] if l['qa'] else '—'} / "
                  f"qa2 {l['qa2']['mesure'] if l['qa2'] else '—'}")
        print(f"ab : {recu['accord']}/{len(codes)} accords, {len(divergences)} divergence(s), "
              f"{recu['secondes']} s")
    return recu


if __name__ == "__main__":
    sys.exit(0 if confronter(silencieux="-q" in sys.argv)["verdict"] == "vert" else 1)
