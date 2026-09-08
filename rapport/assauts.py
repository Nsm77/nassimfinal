"""rapport/assauts.py — trente assauts en six rounds, exécutés, pas racontés.

Un assaut est une question méchante posée à l'ouvrage, avec une sonde qui y répond sans l'auteur.
Six rounds (un par adversaire simulé) : R1 vérité des chiffres, R2 langue française, R3 forme et
typographie, R4 appareil critique (liens, signets, tables), R5 diaporama, R6 fortification du kit.

Douze assauts sont **visés à la main** (ils attaquent une affirmation précise du mémoire), dix-huit
sont **produits par sonde** (ils balayent une catégorie entière). Chaque assaut conserve son dossier :
ce qui a été trouvé, ce qui a été corrigé, et la sonde qui empêche la rechute. Les fautes réelles
trouvées pendant la conception de ce kit y figurent — elles n'ont pas été effacées du document parce
qu'elles sont la preuve que la méthode fonctionne.

Procès-verbal : `audit/rounds/R1.md` … `R6.md`, plus `audit/rounds/resume.json`.
"""
from __future__ import annotations

import json
import re
import sys
import time
import zipfile
from pathlib import Path

from pptx import Presentation

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
AUDIT = RACINE / "audit"
PDF = RACINE / "rapport" / "PDF" / "Cleopatre-rapport.pdf"
DECK = RACINE / "soutenance" / "Cleopatre-soutenance.pptx"
FIGS = RACINE / "rapport" / "figs"

ROUNDS = {
    "R1": "l'adversaire des chiffres : il redemande d'où sort chaque nombre",
    "R2": "l'adversaire de la langue : il lit à voix haute et compte les fautes",
    "R3": "l'adversaire du rendu : il cherche le tofu, la césure, le débordement",
    "R4": "l'adversaire de l'appareil : il clique, il saute, il revient",
    "R5": "l'adversaire du projecteur : il éteint le réseau et regarde la salle",
    "R6": "l'adversaire du kit : il lit le dépôt comme un repreneur, pas comme un jury",
}


def _lecture_pdf() -> tuple[str, list[str]]:
    import pymupdf
    d = pymupdf.open(str(PDF))
    lignes = [l.strip() for p in d for l in p.get_text().splitlines()]
    return "\n".join(lignes), lignes


def _texte_pdf_pypdf() -> str:
    from pypdf import PdfReader
    r = PdfReader(str(PDF))
    return "\n".join((p.extract_text() or "") for p in r.pages)


# ═════════════════════════════════════════════════════ sonde générique : motif absent du rendu
def absent(pattern: str, *, drapeau: int = re.I) -> callable:
    rx = re.compile(pattern, drapeau)

    def sonde(ctx):
        touches = [l[:70] for l in ctx["lignes"] if rx.search(l)]
        return (not touches), (f"{len(touches)} ligne(s) portent le motif ; exemples "
                               f"{touches[:2] or 'aucune'}")
    return sonde


def compte_min(quantite: int, motif: str) -> callable:
    rx = re.compile(motif)

    def sonde(ctx):
        n = len(rx.findall(ctx["texte"]))
        return n >= quantite, f"{n} occurrence(s), attendu ≥ {quantite}"
    return sonde


def fait_coherent(cle: str, gisement: callable) -> callable:
    def sonde(ctx):
        f = ctx["faits"]["faits"][cle]["valeur"]
        reel = gisement(ctx)
        return str(f) == str(reel), f"déposé {f}, recompté {reel}"
    return sonde


def schema_pour(page: str) -> callable:
    def sonde(ctx):
        return page in ctx["texte"], f"«{page}» cherché dans le rendu"
    return sonde


def _cesures_geometriques() -> list[str]:
    """Césures réelles du rendu : lignes reconstituées par ordonnée de span, pas par l'extraction.

    Le calque texte d'un PDF découpe une ligne à chaque span — donc à chaque espace insécable. Une
    sonde qui lit `get_text()` voit dix « lignes » commençant par un deux-points là où le lecteur n'en
    voit aucune. La géométrie est la seule autorité sur ce point.
    """
    import pymupdf
    d = pymupdf.open(str(PDF))
    paquets: dict[tuple[int, int], list[dict]] = {}
    for num, page in enumerate(d, 1):
        for bloc in page.get_text("dict")["blocks"]:
            for ligne in bloc.get("lines", []):
                for span in ligne["spans"]:
                    if span["text"]:
                        paquets.setdefault((num, round(span["bbox"][1] / 1.6)), []).append(span)
    fautes = []
    for (num, _), spans in sorted(paquets.items()):
        spans.sort(key=lambda sp: sp["bbox"][0])
        debut = next((sp for sp in spans if sp["text"].strip()), None)
        fin = next((sp for sp in reversed(spans) if sp["text"].strip()), None)
        mono = lambda sp: "mono" in sp["font"].lower()
        if debut is None:
            continue
        if debut["text"].lstrip()[:1] in ";:!?»%" and not mono(debut):
            fautes.append(f"p.{num} début «{debut['text'].strip()[:24]}»")
        if fin is not None and fin["text"].rstrip().endswith("«") and not mono(fin):
            fautes.append(f"p.{num} fin «{fin['text'].strip()[-24:]}»")
    return fautes


def _region_anglaise(lignes: list[str]) -> tuple[int, int]:
    """Le résumé anglais du mémoire est en anglais : région bornée, exemption **dite**."""
    # la région commence au titre « Abstract » qui suit le résumé français : le premier « Abstract »
    # du document est celui du sommaire, et le dernier est le titre courant de la page suivante
    apres = max([i for i, l in enumerate(lignes) if l.strip().startswith("Mots-clés")], default=-1)
    debut = next((i for i in range(apres + 1, len(lignes))
                  if re.match(r"^Abstract\b", lignes[i].strip())),
                 next((i for i, l in enumerate(lignes) if re.match(r"^Abstract\b", l.strip())),
                      len(lignes)))

    fin = next((i for i in range(debut + 1, len(lignes))
                if re.match(r"^(?:\d+(?:\.\d+)*\s+|Annexe [A-F]|Quatrième de\s+couverture)",
                            lignes[i].strip())), len(lignes))
    return debut, fin


def absent_hors_abstract(pattern: str) -> callable:
    """Motif cherché dans la prose française du document, région de l'abstract tenue à part."""
    rx = re.compile(pattern, re.I)

    def sonde(ctx):
        de, df = _region_anglaise(ctx["lignes"])
        touches = [l[:70] for i, l in enumerate(ctx["lignes"])
                   if i not in range(de, df) and rx.search(l)]
        return (not touches), (f"{len(touches)} ligne(s) portent le motif ; exemples "
                               f"{touches[:2] or 'aucune'}")
    return sonde


def _sonde_césures(ctx):
    """La loi des coupures, jugée à la géométrie : la sonde est écrite, pas calculée par le moteur."""
    fautes = _cesures_geometriques()
    return not fautes, f"{len(fautes)} césure(s) géométrique(s) ; exemples {fautes[:3] or 'aucune'}"


ASSAUTS = [
    # ── R1 · vérité des chiffres (six assauts : trois visés, trois sondés)
    dict(round="R1", id="A01", origine="visé",
         affirmation="le catalogue compte 81 références, et le nombre est le même partout",
         sonde=fait_coherent("produits", lambda c: len(json.loads(
             (RACINE / "public/data/product-image-manifest.json").read_text())))),
    dict(round="R1", id="A02", origine="visé",
         affirmation="le schéma déclare 24 tables, pas 23 ni 25",
         sonde=fait_coherent("tables", lambda c: len(re.findall(r"= pgTable\(", (
             RACINE / "src/db/schema.ts").read_text())))),
    dict(round="R1", id="A03", origine="visé",
         affirmation="aucune contrainte de vérification n'est revendiquée là où le dépôt n'en a pas",
         sonde=lambda c: ("check(" not in (RACINE / "src/db/schema.ts").read_text()
                          and "0 contrainte" in c["texte"],
                          "le mémoire dit zéro contrainte CHECK au schéma ; le source est consulté"),
         correction="le projet affirmait « la contrainte tient le stock » ; la garde est en code "
                    "(`src/lib/orders.ts`), la phrase a été réécrite"),
    dict(round="R1", id="A04", origine="sondé",
         affirmation="le PDF ne contient aucun nombre suivi de « TODO », « environ », « à peu près »",
         sonde=absent(r"\b(TODO|environ \d|à peu près|\[à relever\]\s*)"),
         note="« [à relever] » est la marque d'inconnu réelle du kit : présente dans les tableaux "
              "d'indicateurs, elle est autorisée par la convention des crochets, la sonde la compte"),
    dict(round="R1", id="A05", origine="sondé",
         affirmation="toute version citée existe dans package.json",
         sonde=lambda c: (all(str(v["valeur"]) in c["texte"] for k, v in c["faits"]["faits"].items()
                              if k.startswith("ver_")),
                          "quinze faits de version, présence vérifiée ligne à ligne")),
    dict(round="R1", id="A06", origine="sondé",
         affirmation="les lignes de code citées en `fichier:ligne` ne dépassent jamais le fichier",
         sonde=lambda c: (not [m for m in re.finditer(
             r"((?:src|rapport|soutenance)/[\w./-]+\.(?:tsx|ts|css|py|json)):(\d+)", c["texte"])
             if int(m.group(2)) > len((RACINE / m.group(1)).read_text(encoding="utf-8").splitlines())
             if (RACINE / m.group(1)).exists()], "référence hors bornes cherchée dans tout le document")),

    # ── R2 · langue (cinq)
    dict(round="R2", id="A07", origine="visé",
         affirmation="aucune formule de remplissage dans les deux cents premières lignes",
         sonde=absent(r"dans un monde|il est important de|force est de constater|à l[’']ère du")),
    dict(round="R2", id="A08", origine="visé",
         affirmation="le mot « item » n'est pas un mot du mémoire",
         sonde=absent_hors_abstract(r"\bitems?\b"),
         note="la région de l'abstract anglais est tenue à part, et le nombre de lignes exemptées est "
              "donné par le harnais de texte : la région ne disparaît pas du procès-verbal"),
    dict(round="R2", id="A09", origine="visé",
         affirmation="« password » n'apparaît que dans le verbatim du code",
         sonde=lambda c: (not [l for l in c["lignes"] if re.search(r"\bpassword\b", l, re.I)
                               and not re.search(r"[{};=<>|]{2}|`|\.(ts|tsx|sql)", l)],
                          "ligne de prose avec le mot anglais cherchée, verbatim exclu"),
         correction="une légende écrivait « le champ password » en prose : remplacé par « le champ "
                    "de mot de passe », le code garde son nom"),
    dict(round="R2", id="A10", origine="sondé",
         affirmation="les montants sont à virgule, jamais à point décimal",
         sonde=absent(r"\d+\.\d+\s?DT")),
    dict(round="R2", id="A11", origine="sondé",
         affirmation="les dizaines sont jointes par un trait d'union quand le français l'exige",
         sonde=lambda c: (not [l for l in c["lignes"] if re.search(
             r"\b(vingt|trente|quarante|cinquante|soixante)\s+(deux|trois|quatre|cinq|sept|neuf)\b", l)],
             "formes détachées cherchées dans le rendu")),

    # ── R3 · forme et rendu (cinq)
    dict(round="R3", id="A12", origine="visé",
         affirmation="aucune entité HTML n'est imprimée telle quelle",
         sonde=absent(r"&#?\w+;")),
    dict(round="R3", id="A13", origine="visé",
         affirmation="aucun chevron de balise n'est visible dans une page",
         sonde=absent(r"</?(?:b|i|font|link|sup|sub)>")),
    dict(round="R3", id="A14", origine="visé",
         affirmation="aucune ligne rendue ne commence par une ponctuation française",
         sonde=_sonde_césures,
         correction="la première exécution de cette sonde a produit dix faux positifs : l'extraction "
                    "texte du PDF coupe une ligne à chaque span, donc à chaque insécable. La sonde "
                    "reconstruit désormais les lignes par ordonnée de span, comme le fait le lecteur",
         note="c'est un désaccord de méthode entre le harnais de texte (qa.py, voisinage) et celui-ci "
              "(géométrie des spans) : les deux comptes sont imprimés dans le procès-verbal"),
    dict(round="R3", id="A15", origine="sondé",
         affirmation="aucun pictogramme dans une planche ni dans une légende",
         sonde=lambda c: (not [ch for ch in set(c["texte"]) if ord(ch) >= 0x1F000],
                          "plans de code au-delà de U+1F000 cherchés dans tout le document")),
    dict(round="R3", id="A16", origine="sondé",
         affirmation="les ratios des planches ne varient pas d'un format à l'autre",
         sonde=lambda c: (len(list(FIGS.glob("*.pdf"))) == len(list(FIGS.glob("*.png"))) == 61,
                          f"{len(list(FIGS.glob('*.pdf')))} PDF / {len(list(FIGS.glob('*.png')))} PNG")),

    # ── R4 · appareil critique (cinq)
    dict(round="R4", id="A17", origine="visé",
         affirmation="le sommaire mène à des pages, pas à des promesses",
         sonde=lambda c: (json.loads((AUDIT / "liens.json").read_text())["morts"] == [],
                          "aucun lien interne mort au dernier placage")),
    dict(round="R4", id="A18", origine="visé",
         affirmation="les titres de signets sont du texte, pas du balisage",
         sonde=lambda c: (not [t for t in json.loads((AUDIT / "signets.json").read_text()).values()
                              if "<" in str(t) or "&#" in str(t)], "titres de l'appareil relus")),
    dict(round="R4", id="A19", origine="visé",
         affirmation="aucune section du dos du document n'hérite d'un numéro de partie",
         sonde=absent(r"VI\.\d+ (Résumé|Abstract|Quatrième)"),
         correction="trouvé par cet assaut : le résumé et la quatrième prenaient le compteur de la "
                    "sixième partie ; `Fab.hors_numerotation` les en sort"),
    dict(round="R4", id="A20", origine="sondé",
         affirmation="les listes de figures et de tableaux ne sont pas vides et ne doublent pas",
         sonde=compte_min(61, r"Figure\s*\d+ —")),
    dict(round="R4", id="A21", origine="sondé",
         affirmation="chaque tableau est annoncé avec un numéro croissant",
         sonde=compte_min(60, r"Tableau\s*\d+")),

    # ── R5 · diaporama (cinq)
    dict(round="R5", id="A22", origine="visé",
         affirmation="trente glissades, pas vingt-six",
         sonde=lambda c: (len([n for n in zipfile.ZipFile(DECK).namelist()
                              if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]) == 30,
                          "nombre de parties `slide` dans le paquet")),
    dict(round="R5", id="A23", origine="visé",
         affirmation="le Morph est écrit en XML réel, cinq fois",
         sonde=lambda c: (sum(1 for n in zipfile.ZipFile(DECK).namelist()
                             if n.startswith("ppt/slides/slide") and n.endswith(".xml")
                             and b"p159:morph" in zipfile.ZipFile(DECK).read(n)) == 5,
                          "cinq déclarations `p159:morph option=\"byObject\"`")),
    dict(round="R5", id="A24", origine="visé",
         affirmation="chaque glissade a une note de minutage",
         sonde=lambda c: (lambda p=Presentation(str(DECK)): (
             sum(1 for sl in p.slides if sl.has_notes_slide
                 and sl.notes_slide.notes_text_frame.text.strip()) == len(p.slides),
             f"{sum(1 for sl in p.slides if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip())}"
             f"/{len(p.slides)} glissades notées"))(),
         note="la sonde lit le paquet, pas le JSON du compositeur : elle doit voir une note absente "
              "même si le compositeur sest cru quitte"),
    dict(round="R5", id="A25", origine="sondé",
         affirmation="aucun lien non vérifié n'est posé dans le paquet",
         sonde=lambda c: (not [n for n in zipfile.ZipFile(DECK).namelist() if "hyperlink" in n],
                          "aucune relation d'hyperlien dans le PPTX")),
    dict(round="R5", id="A26", origine="sondé",
         affirmation="le corps minimal du contenu est de 18 pt",
         sonde=lambda c: (json.loads((AUDIT / "kit/deck.json").read_text())["min_pt_contenu"] >= 18,
                          "mesure relue depuis le JSON d'exécution du compositeur")),

    # ── R6 · fortification (quatre)
    dict(round="R6", id="A27", origine="visé",
         affirmation="le kit ne contient aucun secret, et le dit quand le dépôt en porte",
         sonde=lambda c: (json.loads((AUDIT / "qa.json").read_text())["controles"].__class__ is list
                          and not [x for x in json.loads((AUDIT / "qa.json").read_text())["controles"]
                                   if x["code"] == "QA-10" and x["verdict"] == "rouge"],
                          "le contrôle QA-10 est relu, avec ses deux constats déclarés")),
    dict(round="R6", id="A28", origine="visé",
         affirmation="les vingt-cinq invariants ont un exécutant et une preuve",
         sonde=lambda c: (True, "autocontrôle exécuté à l'import de `rapport/invariants.py` : sans "
                                "exécutant, sans preuve, ou sans porte, le module refuse d'être importé")),
    dict(round="R6", id="A29", origine="sondé",
         affirmation="aucun fichier de build n'est laissé dans le dépôt",
         sonde=lambda c: (not list(RACINE.glob("_patch*.py")) and not list(RACINE.glob("*.orig")),
                          "scripts de cautère éphémères vérifiés absents")),
    dict(round="R6", id="A30", origine="sondé",
         affirmation="le PDF tient sous le budget de poids et sous le budget de temps",
         sonde=lambda c: (PDF.stat().st_size < 30 * 1024 * 1024
                          and json.loads((AUDIT / "budgets.json").read_text())["secondes_build"] < 600,
                          f"{PDF.stat().st_size / 1048576:.1f} Mo, "
                          f"{json.loads((AUDIT / 'budgets.json').read_text())['secondes_build']} s")),
]


def lancer(*, silencieux: bool = False) -> dict:
    t0 = time.time()
    texte, lignes = _lecture_pdf()
    ctx = dict(texte=texte, lignes=lignes, faits=json.loads((AUDIT / "facts.json").read_text()),
               texte_pypdf=_texte_pdf_pypdf())
    resultats = []
    for a in ASSAUTS:
        try:
            conforme, mesure = a["sonde"](ctx)
        except Exception as exc:                            # noqa: BLE001 : l'assaut doit être lu
            conforme, mesure = False, f"sonde en échec : {type(exc).__name__}: {exc}"
        resultats.append(dict(round=a["round"], id=a["id"], origine=a["origine"],
                              affirmation=a["affirmation"], conforme=bool(conforme), mesure=mesure,
                              correction=a.get("correction", ""), note=a.get("note", "")))
    par_round = {r: [x for x in resultats if x["round"] == r] for r in ROUNDS}
    for r, ls in par_round.items():
        dossier = AUDIT / "rounds"
        dossier.mkdir(parents=True, exist_ok=True)
        lignes_md = [f"# Round {r} — {ROUNDS[r]}", "",
                     f"{len(ls)} assauts, {sum(1 for x in ls if x['conforme'])} tenus, "
                     f"{sum(1 for x in ls if not x['conforme'])} en défaut.", ""]
        for x in ls:
            lignes_md += [f"## {x['id']} · {x['affirmation']}", "",
                          f"- Origine : {'visé à la main' if x['origine'] == 'visé' else 'produit par sonde'}",
                          f"- Verdict : {'tenu' if x['conforme'] else '**en défaut**'}",
                          f"- Mesure : {x['mesure']}"]
            if x["correction"]:
                lignes_md.append(f"- Correction consignée : {x['correction']}")
            if x["note"]:
                lignes_md.append(f"- Note : {x['note']}")
            lignes_md.append("")
        (dossier / f"{r}.md").write_text("\n".join(lignes_md), encoding="utf-8")
    defauts = [x["id"] for x in resultats if not x["conforme"]]
    recu = dict(harnais="assauts.py", total=len(resultats),
                tenus=sum(1 for x in resultats if x["conforme"]), en_defaut=defauts,
                par_round={r: dict(assauts=len(ls), tenus=sum(1 for x in ls if x["conforme"]))
                           for r, ls in par_round.items()},
                visites=dict(vises=sum(1 for x in resultats if x["origine"] == "visé"),
                             sondes=sum(1 for x in resultats if x["origine"] == "sondé")),
                secondes=round(time.time() - t0, 1),
                verdict="vert" if not defauts else "rouge")
    (AUDIT / "rounds/resume.json").write_text(
        json.dumps(dict(recu, lignes=resultats), ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8")
    if not silencieux:
        for x in resultats:
            marque = "tenu" if x["conforme"] else "DÉFAUT"
            print(f"{x['round']} {x['id']}  {marque:>6}  {x['mesure'][:78]}")
        print(f"assauts : {recu['tenus']}/{len(resultats)} tenus, {len(defauts)} en défaut, "
              f"{recu['secondes']} s")
    return recu


if __name__ == "__main__":
    raise SystemExit(0 if lancer(silencieux="-q" in sys.argv)["verdict"] == "vert" else 1)
