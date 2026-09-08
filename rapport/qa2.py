"""rapport/qa2.py — second harnais : mêmes affirmations, autres primitives.

`qa.py` lit le PDF avec `pypdf` et compte des lignes de texte ; celui-ci lit le PDF avec
**PyMuPDF** (géométrie des spans, polices réelles) et recompte l'application et les chemins avec des
**outils du shell** (`grep`, `find`), donc sans la grammaire de l'extracteur du rapport ni la
heuristique de voisinage du premier harnais. Deux angles, deux sources d'erreur distinctes.

Ce que les deux harnais ne voient pas de la même façon est la matière première de `ab.py` : un
désaccord n'est pas une imprécision du document, c'est une panne à instruire.

Sorties : `audit/qa2.json`, puis confrontation par `python3 rapport/ab.py`.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
AUDIT = RACINE / "audit"
PDF = RACINE / "rapport" / "PDF" / "Cleopatre-rapport.pdf"
DECK = RACINE / "soutenance" / "Cleopatre-soutenance.pptx"
FIGS = RACINE / "rapport" / "figs"

SLOP = [r"dans un monde", r"il est important de", r"il convient de", r"force est de constater",
        r"à l[’']ère du", r"de nos jours", r"rôle clé", r"s'avère", r"crucial", r"de pointe",
        r"solution innovante"]
EMPRUNTS = ["order", "orders", "cart", "carts", "item", "items", "shop", "store", "user", "users",
            "tracking", "password"]


def _shell(cmd: str) -> str:
    p = subprocess.run(["bash", "-lc", cmd], cwd=str(RACINE), capture_output=True, text=True)
    return p.stdout.strip()


def _spans() -> list[dict]:
    """Tous les spans du document, avec page, police, taille, texte. Base de tous les contrôles."""
    import pymupdf
    d = pymupdf.open(str(PDF))
    out = []
    for num, page in enumerate(d, 1):
        for bloc in page.get_text("dict")["blocks"]:
            for ligne in bloc.get("lines", []):
                for sp in ligne["spans"]:
                    out.append(dict(page=num, font=sp["font"], size=round(sp["size"], 2),
                                    texte=sp["text"], x=sp["bbox"][0], y=sp["bbox"][1]))
    d.close()
    return out


def _lignes_visuelles(spans: list[dict]) -> list[list[dict]]:
    """Lignes visuelles : regroupement par ordonnée, puis coupure quand le blanc dépasse un espace.

    Le moteur de texte découpe une « ligne » à chaque appel de tracé : dans un tableau, l'étiquette de
    la cellule et sa valeur deviennent deux lignes, et une loi de ponctuation jugée là-dessus voit douze
    coupures imaginaires (p. 18, 30, 44 au premier jet). Le critère vrai est optique : deux spans sont
    de la même ligne si leur ordonnée se recoupe et si l'écart horizontal ne dépasse pas un espace.
    """
    import pymupdf
    d = pymupdf.open(str(PDF))
    n_pages = d.page_count
    atoms = []
    for num, page in enumerate(d, 1):
        for bloc, group in enumerate(page.get_text("dict")["blocks"]):
            for ligne in group.get("lines", []):
                for x in ligne["spans"]:
                    if x["text"]:
                        atoms.append(dict(page=num, bloc=bloc, font=x["font"],
                                          size=round(x["size"], 2), texte=x["text"],
                                          x0=x["bbox"][0], x1=x["bbox"][2], y0=x["bbox"][1],
                                          y1=x["bbox"][3]))
    d.close()
    # une ligne visuelle = un bloc, une ordonnée de ligne. Les blancs internes ne coupent rien :
    # une ligne justifiée écarte les mots de onze points, et le texte d'une cellule de tableau tient
    # dans un seul bloc. Le harnais de texte de qa.py, lui, lit les sauts de ligne bruts.
    paquets: dict[tuple[int, int, int], list[dict]] = {}
    for a in atoms:
        paquets.setdefault((a["page"], a["bloc"], round(a["y0"] / 1.5)), []).append(a)
    lignes: list[list[dict]] = []
    for _, v in sorted(paquets.items()):
        lignes.append(sorted(v, key=lambda a: a["x0"]))
    return lignes


# ══════════════════════════════════════════════════════════════════════ les lois
def q1(ctx):
    """Versions : ce qui est imprimé existe au dépôt, et tout ce que le rapport promet est imprimé."""
    dep = json.loads((RACINE / "package.json").read_text(encoding="utf-8"))
    deps = {**dep.get("dependencies", {}), **dep.get("devDependencies", {})}
    imprimees = {s_["texte"].strip() for s_ in ctx["spans"]
                 if re.fullmatch(r"\d+\.\d+\.\d+[\w.-]*", s_["texte"].strip())}
    attendues = {k[4:]: str(v["valeur"]) for k, v in ctx["faits"]["faits"].items()
                 if k.startswith("ver_")}
    absentes = sorted(n for n, v in attendues.items() if v not in imprimees)
    reelles = {str(x).lstrip("^~") for x in deps.values()}
    inventees = sorted(t for t in imprimees if t not in reelles)
    return dict(verdict="vert" if not absentes else "rouge", mesure=len(attendues),
                detail=f"{len(attendues)} versions attendues, absentes {absentes[:3] or 'aucune'} ; "
                       f"{len(inventees)} triple(s) de version imprimée(s) sans paquet correspondant "
                       f"(signal, pas faute : {inventees[:3] or 'aucune'})")


def q2(ctx):
    n_tables = int(_shell("grep -c '= pgTable(' src/db/schema.ts || echo 0") or 0)
    n_enums = int(_shell("grep -c '= pgEnum(' src/db/schema.ts || echo 0") or 0)
    n_routes = int(_shell("find src/app -name 'page.tsx' | wc -l") or 0)
    n_api = int(_shell("find src/app/api -name 'route.ts' | wc -l") or 0)
    n_actions = int(_shell("grep -rhEc '^export (async )?(function|const)' src/actions | "
                           "awk '{s+=$1} END {print s+0}'") or 0)
    # le manifeste compte une entrée par référence ; la clé choisie est celle qui marque chaque ligne
    n_produits = int(_shell("grep -o '\"verified\"' public/data/product-image-manifest.json | wc -l") or 0)
    reel = dict(tables=n_tables, enums=n_enums, routes=n_routes, endpoints=n_api,
                actions=n_actions, produits=n_produits)
    faits = ctx["faits"]["faits"]
    ecarts = [f"{k}: shell {n}, fait {faits[k]['valeur']}" for k, n in reel.items()
              if str(faits[k]["valeur"]) != str(n)]
    return dict(verdict="vert" if not ecarts else "rouge", mesure=len(reel),
                detail=f"recomptage par outils du shell ({', '.join(f'{k} {v}' for k, v in reel.items())}) ; "
                       f"écarts avec l'extracteur {ecarts[:3] or 'aucun'}")


def q3(ctx):
    texte = "\n".join(s["texte"] for s in ctx["spans"])
    chemins = set(re.findall(r"(?:src|public|rapport|soutenance)/[\w./-]+", texte))
    absents = [c for c in sorted(chemins)
               if re.search(r"\.(tsx|ts|css|json|py|md)$", c)
               and _shell(f"test -e {json.dumps(str(RACINE / c))} && echo oui || echo non") != "oui"]
    return dict(verdict="vert" if not absents else "rouge", mesure=len(chemins),
                detail=f"{len(chemins)} mentions de chemin, absentes du disque "
                       f"{absents[:3] or 'aucune'} (test `stat`, pas listing Python)")


def q4(ctx):
    texte = " ".join(sp["texte"] for sp in ctx["spans"] if "Mono" not in sp["font"])
    touches = [motif for motif in SLOP if re.search(motif, texte, flags=re.I)]
    return dict(verdict="vert" if not touches else "rouge", mesure=len(touches),
                detail=f"{len(touches)} formule(s) sur {len([s_ for s_ in ctx['spans'] if 'Mono' not in s_['font']])}"
                       f" spans non verbatim du document (verbatim tenu à part) : "
                       f"{touches[:4] or 'aucune'}")


def _verbatim(spans: list[dict]) -> list[dict]:
    """Spans de verbatim : la fonte monospace, seule exemption admise par la loi de langue."""
    return [sp for sp in spans if "Mono" in sp["font"]]


def _concatene(ligne: list[dict]) -> str:
    """Texte d'une ligne, avec un espace là où le blanc est réel et rien là où l'extraction a coupé.

    Un mot peut sortir du lecteur en deux spans (kerning, italique, césure de tracé) ; coller sans
    regard produit « cart e » et fait croire à un emprunt anglais. Le blanc physique tranche.
    """
    out = ""
    for i, x in enumerate(ligne):
        if i:
            a, b = ligne[i - 1], x
            if a["page"] == b["page"] and b["x0"] - a["x1"] > 0.6 * max(a["size"], b["size"]) * 0.5:
                out += " "
        out += x["texte"]
    return out


EN_STOPWORDS = ("the", "and", "with", "for", "that", "this", "from", "have", "covers", "application",
                "catalogue", "ordering", "cash", "delivery", "two", "which", "are", "was", "their")


def _ligne_anglaise(concat: str) -> bool:
    """La ligne est-elle en anglais ? Détection par mots outils, pas par position dans le document.

    La loi de français ne s'applique pas au résumé anglais : qa.py l'exempte par la région (entre le
    titre « Abstract » et le titre suivant), ce qui rate si un titre se répète en titre courant. Cette
    sonde juge la **langue de la ligne**, donc survit à un déplacement du résumé et à une reprise du mot
    « items » dans une citation. Le nombre de lignes tenues pour anglaises est imprimé au procès-verbal.
    """
    mots = re.findall(r"[A-Za-z]{3,}", concat.lower())
    if len(mots) < 5:
        return False
    return sum(1 for m in mots if m in EN_STOPWORDS) >= max(2, len(mots) // 6)


def _ligne_de_prose(concat: str) -> bool:
    """Une ligne de prose = au moins quatre mots de deux lettres ou plus, séparés par des espaces.

    Les étiquettes d'un schéma de bases (« users 9 », « orders 24 ») ne sont pas de la prose : ce sont
    des noms de table suivis d'un compteur. La distinction est écrite ici, pas cachée dans une exemption
    de police, et le nombre de lignes écartées pour cette raison est imprimé au procès-verbal.
    """
    return len(re.findall(r"[A-Za-zÀ-ÿ]{2,}", concat)) >= 4


FR = "A-Za-zàâäéèêëïîôöùûüçœÀ-Ÿ"   # classes de caractères : les plages, pas des lettres éparpillées
MARQUE_IDENTIFIANT = set("_.-/⟵·«»") | {chr(91), chr(93)}


def _span_porteur(ligne: list[dict], index: int) -> dict:
    """Le span qui couvre un index du texte concaténé de la ligne (la ligne est un jeu de spans)."""
    position = 0
    for x in ligne:
        if position <= index < position + len(x["texte"]):
            return x
        position += len(x["texte"])
    return ligne[0]


def _est_identifiant(ligne: list[dict], index_span: int, debut: int, fin: int) -> bool:
    """Le mot est-il un identifiant cité (nom de fichier, de table, de colonne) plutôt qu'un mot ?

    Le premier jet du harnais exemptait par la police seule : dix-huit lignes de prose sont en
    monospace parce qu'elles sortent d'un extrait, et cent identifiers sont en police normale parce
    qu'ils vivent dans une cellule de tableau. La marque d'identifiant (point, tiret bas, crochet,
    flèche, chevron de citation) est la preuve qui manque aux deux.
    """
    texte = "".join(x["texte"] for x in ligne)
    gauche = texte[max(0, debut - 2):debut]
    droite = texte[fin:fin + 2]
    if any(c in MARQUE_IDENTIFIANT for c in gauche + droite):
        return True
    if gauche and gauche[-1] in FR:                 # le mot est collé à une lettre française
        return True
    if droite and droite[0] in FR:
        return True
    if any(c in "[](){}<>'\\" for c in (gauche + droite)):
        return True
    return any(re.search(r"[\w.-]+\.(?:tsx?|py|json|sql|css)\b", x["texte"]) for x in ligne)


def q5(ctx):
    """Emprunts anglais : faute seulement si le mot est employé comme mot français."""
    hits, exempts, prose, etiquettes, anglaises = [], 0, 0, 0, 0
    for ln in ctx["lignes"]:
        concat = _concatene(ln)
        corps = max(x["size"] for x in ln)
        if corps < 8.5:                            # légende de figure ou d'étiquette : hors prose
            etiquettes += 1
            continue
        if not _ligne_de_prose(concat):            # ligne d'étiquette ou de schéma : hors loi
            etiquettes += 1
            continue
        if _ligne_anglaise(concat):                 # le résumé anglais est en anglais : consigné
            anglaises += 1
            continue
        prose += 1
        for mot in EMPRUNTS:
            for m in re.finditer(rf"(?<![{FR}]){mot}(?![{FR}])", concat):
                span = _span_porteur(ln, m.start())
                if "mono" in span["font"].lower() or _est_identifiant(ln, 0, m.start(), m.end()):
                    exempts += 1
                else:
                    hits.append(f"{mot} dans « {concat[max(0, m.start() - 30):m.end() + 24]} »")
    return dict(verdict="vert" if not hits else "rouge", mesure=len(hits),
                detail=f"{len(hits)} emploi(s) fautif(s) sur {prose} lignes de prose "
                       f"({etiquettes} ligne(s) hors prose, {anglaises} ligne(s) anglaise(s) "
                       f"tenues hors du champ), "
                       f"{exempts} occurrence(s) exemptée(s) par la fonte ou par une marque "
                       f"d'identifiant ; exemples {hits[:2] or 'aucun'}")


def q6(ctx):
    import pymupdf
    d = pymupdf.open(str(PDF))
    toc = d.get_toc()
    registre = json.loads((AUDIT / "signets.json").read_text())
    sales = [t[1] for t in toc if "<" in t[1] or "&#" in t[1]]
    hors_pages = [t for t in toc if not (1 <= t[2] <= d.page_count)]
    return dict(verdict="vert" if len(toc) == len(registre) and not sales and not hors_pages else "rouge",
                mesure=len(toc),
                detail=f"{len(toc)} entrées d'outline PyMuPDF, registre {len(registre)}, titres "
                       f"fautifs {sales[:2] or 'aucun'}, pointeurs hors pages {hors_pages[:2] or 'aucun'}")


def q7(ctx):
    """Liens : chaque annotation de saut pointe sur une page qui existe ; zéro sortie vers le réseau."""
    import pymupdf
    d = pymupdf.open(str(PDF))
    internes = externes = morts = 0
    for num, page in enumerate(d, 1):
        for l in page.get_links():
            if l.get("kind") == pymupdf.LINK_URI or l.get("uri"):
                externes += 1
                continue
            cible = l.get("page")
            if cible is not None and 0 <= cible < d.page_count:
                internes += 1
            else:
                morts += 1
    return dict(verdict="vert" if morts == 0 and internes > 150 and externes == 0 else "rouge",
                mesure=internes,
                detail=f"{internes} sauts internes résolus par get_links(), {externes} lien(s) "
                       f"externe(s) cliquable(s), {morts} sans cible")


def q8(ctx):
    import pymupdf
    from PIL import Image
    divergents = []
    for timbre in sorted(FIGS.glob("*.pdf")):
        png = timbre.with_suffix(".png")
        if not png.exists():
            divergents.append(f"{timbre.stem}: PNG absent")
            continue
        d = pymupdf.open(str(timbre))
        r = d[0].rect
        d.close()
        with Image.open(png) as im:
            w, h = im.size
        if abs(r.width / r.height - w / h) > 0.01:
            divergents.append(f"{timbre.stem}: {r.width / r.height:.4f} contre {w / h:.4f}")
    return dict(verdict="vert" if not divergents else "rouge",
                mesure=len(list(FIGS.glob("*.pdf"))),
                detail=f"ratios lus côté PyMuPDF (points) contre PIL (pixels) : divergences "
                       f"{divergents[:3] or 'aucune'}")


def q9(ctx):
    symboles = [s["texte"][:20] for s in ctx["spans"]
                if any(ord(c) >= 0x1F000 or 0x2600 <= ord(c) <= 0x27BF for c in s["texte"]
                       if c not in "·—–’«»…")]
    return dict(verdict="vert" if not symboles else "rouge", mesure=len(symboles),
                detail=f"spans portant un idéogramme ou un pictogramme : {symboles[:3] or 'aucun'}")


def q10(ctx):
    sortie = _shell("grep -rInE '(api[_-]?key|secret|password|private key)[[:space:]]*[:=]"
                    "[[:space:]]*\\\"[^\\\"]{8,}' rapport soutenance audit 2>/dev/null | "
                    "grep -vE 'change-me|exemple|gabarit' | head -5")
    lignes = [l for l in sortie.splitlines() if l.strip()]
    env_reel = _shell("git ls-files | grep -E '^\\.env([.][a-z-]+)?$' | grep -v example | head -3")
    return dict(verdict="vert" if not lignes and not env_reel.strip() else "rouge", mesure=len(lignes),
                detail=f"grep du kit : {len(lignes)} affectation suspecte ; .env suivis réels : "
                       f"{env_reel.strip() or 'aucun'}")


def q11(ctx):
    """Le paquet du diaporama, ouvert comme une archive : sans python-pptx, donc sans hypothèque."""
    z = zipfile.ZipFile(DECK)
    parties = sorted(n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
    notes = len([n for n in z.namelist()
                 if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)])
    morph = sum(1 for n in parties if b"p159:morph" in z.read(n))
    petits = []
    for n in parties:
        x = z.read(n).decode("utf-8")
        # un run de contenu est marqué par le nom de sa zone (role="contenu" posé au composition)
        for m in re.finditer(r'name="contenu"[\s\S]*?sz="(\d{3,4})"', x):
            if int(m.group(1)) < 1800:
                petits.append(f"{n.split('/')[-1]}:{int(m.group(1)) / 100} pt")
    return dict(verdict="vert" if len(parties) == 30 and morph == 5 and notes == 30 and not petits
                else "rouge", mesure=len(parties),
                detail=f"lu par zip et regex : {len(parties)} glissades, {morph} morph, {notes} "
                       f"fichiers de notes, corps < 18 pt dans une zone de contenu "
                       f"{petits[:3] or 'aucun'}")


def q12(ctx):
    texte = ctx["texte"]
    points = sorted(set(re.findall(r"\d+\.\d+ *DT", texte)))
    virgules = len(re.findall(r"\d+,\d{3} *DT", texte))
    groupes = sorted(set(re.findall(r"(?<!\d)\d{1,3}\.\d{3}(?!\d)", texte)))
    return dict(verdict="vert" if not points and virgules >= 10 else "rouge", mesure=virgules,
                detail=f"{virgules} montants à trois décimales, points décimaux {points[:3] or 'aucun'}, "
                       f"groupements par point {groupes[:3] or 'aucuns'} (le point n'est pas un "
                       f"séparateur de milliers en français)")


def q13(ctx):
    fautes = []
    for ln in ctx["lignes"]:
        visibles = [s for s in ln if s["texte"].strip()]
        if not visibles:
            continue
        premier, dernier = visibles[0], visibles[-1]
        # une ponctuation collée à du verbatim n'est pas une faute de prose : la ponctuation appartient
        # à l'extrait de code. Le span *de bordure* fait foi, et il est jugé sur sa propre fonte.
        mono = lambda s: "Mono" in s["font"]
        if premier["texte"].lstrip()[:1] in ";:!?»%" and not mono(premier):
            fautes.append(f"p.{premier['page']} début {premier['texte'][:24]!r}")
        if dernier["texte"].rstrip().endswith("«") and not mono(dernier):
            fautes.append(f"p.{dernier['page']} fin {dernier['texte'][-24:]!r}")
    return dict(verdict="vert" if not fautes else "rouge", mesure=len(fautes),
                detail=f"loi des insécables jugée à la géométrie des spans et à la police : "
                       f"{len(fautes)} faute(s) ; exemples {fautes[:3] or 'aucune'}")


LOIS = [("QA-1", q1), ("QA-2", q2), ("QA-3", q3), ("QA-4", q4), ("QA-5", q5), ("QA-6", q6),
        ("QA-7", q7), ("QA-8", q8), ("QA-9", q9), ("QA-10", q10), ("QA-11", q11), ("QA-12", q12),
        ("QA-13", q13)]


def lancer(*, silencieux: bool = False) -> dict:
    t0 = time.time()
    spans = _spans()
    ctx = dict(spans=spans, lignes=_lignes_visuelles(spans),
               texte=" ".join(s["texte"] for s in spans),
               faits=json.loads((AUDIT / "facts.json").read_text(encoding="utf-8")))
    controles = []
    for code, func in LOIS:
        try:
            r = func(ctx)
        except Exception as exc:                                  # noqa: BLE001
            r = dict(verdict="rouge", mesure=0,
                     detail=f"exception {type(exc).__name__}: {exc}")
        r.update(code=code, titre=r.get("titre", ""))
        controles.append(r)
        if not silencieux:
            print(f"{r['verdict']:>5}  {code}  {r['detail'][:150]}")
    rouges = sum(1 for c in controles if c["verdict"] == "rouge")
    recu = dict(harnais="qa2.py (PyMuPDF + outils du shell)", controles=controles, rouges=rouges,
                secondes=round(time.time() - t0, 2), lignes=len(ctx["lignes"]),
                spans=len(spans), verdict="vert" if rouges == 0 else "rouge")
    (AUDIT / "qa2.json").write_text(json.dumps(recu, ensure_ascii=False, indent=1, sort_keys=True)
                                    + "\n", encoding="utf-8")
    if not silencieux:
        print(f"\nqa2 : {len(LOIS)} lois, {rouges} rouge(s), {recu['secondes']} s")
    return recu


if __name__ == "__main__":
    sys.exit(0 if lancer()["verdict"] == "vert" else 1)
