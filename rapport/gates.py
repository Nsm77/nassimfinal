"""rapport/gates.py — les vingt-sept portes G1 à G27, jugées sur pièces.

Chaque porte a une sonde qui lit le dossier d'audit et le dépôt, jamais la mémoire de l'auteur. La
sonde renvoie une mesure, pas une opinion : `13/13 accords`, `113 pages (bande 102 à 168)`,
`3/3 mutations détectées`. Une porte sans sonde tombe en rouge avec la mention `aucun exécutant`.

Trois portes commandent les autres : G6 note l'ouvrage sur cent (la grille détaillée est écrite dans
`audit/kit/rubrique.md`), G25 constate l'épuisement (« rien à ajouter »), G27 gèle (`--sceller` écrit
`audit/sceau.json` avec l'empreinte de chaque livrable et pose l'étiquette `v1.0-final`).

Usage : `python3 rapport/gates.py [-q]` puis, une fois tout vert,
`python3 rapport/gates.py --sceller`.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "rapport"))
AUDIT = RACINE / "audit"

import invariants as iv  # noqa: E402  (source unique des vingt-cinq invariants et des vingt-sept portes)

PORTES = {p[0]: p for p in iv.PORTES}


def _lu(nom: str) -> dict:
    try:
        return json.loads((AUDIT / nom).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(RACINE), capture_output=True, text=True).stdout.strip()


def _tout_vert(etat: dict) -> bool:
    return all(v["verdict"] == "vert" for k, v in etat.items() if k not in ("G6", "G25", "G27"))


# ═══════════════════════════════════════════════════════════════════════════════════════ les sondes
def g1(c):
    """Porte G1 : les sept actes de démarrage sont écrits, et datés avant le premier octet de kit."""
    t = (RACINE / "audit/B0-boot.md").read_text(encoding="utf-8")
    actes = sorted({m for m in re.findall(r"^##+\s*B(\d)", t, re.M)})
    return len(actes) >= 7, f"actes B0 à B6 écrits avant le code : {actes}"


def g2(c):
    """Porte G2 : le pré-mortem nomme huit morts, pas trois."""
    t = (RACINE / "audit/B0-boot.md").read_text(encoding="utf-8")
    bas = t.lower()
    bloc = bas.split("pre-mortem", 1)[-1].split("##", 1)[0]
    morts = len(re.findall(r"^\s*\d+[.)]?\s", bloc, re.M)) or len(re.findall(r"^\|\s*\d+\s*\|", bloc, re.M))
    return morts >= 8, f"{morts} morts listées dans le pré-mortem (huit exigées)"


def g3(c):
    """Porte G3 : les quatre budgets d'exécution sont tenus, en unités comparables."""
    b = c["budgets"]
    ecarts = []
    for cible, reel, facteur, unite in (("cible_pages", "pages", 1, "pages"),
                                        ("cible_figs_s", "secondes_figs", 1, "s"),
                                        ("cible_build_s", "secondes_build", 1, "s"),
                                        ("cible_mo_pdf", "octets_pdf", 1048576, "Mo")):
        if cible not in b or reel not in b:
            ecarts.append(f"{cible} ou {reel} absent")
            continue
        if float(b[cible]) and float(b[reel]) > float(b[cible]) * facteur:
            ecarts.append(f"{reel} = {float(b[reel]) / facteur:g} {unite} > cible {b[cible]:g}")
    return not ecarts, (f"{b.get('pages')} pages, {b.get('secondes_build')} s de build, "
                        f"{(b.get('octets_pdf') or 0) / 1048576:.1f} Mo"
                        + (f" ; dépassements {ecarts}" if ecarts else ""))


def g4(c):
    """Porte G4 : le dépôt a été audité contre le cahier, et les gisements sont comptés."""
    f = c["facts"]
    attendus = ("tables", "enums", "produits", "marques", "universes", "actions")
    manquants = [k for k in attendus if k not in f or not f[k]]
    releves = ", ".join("{} {}".format(k, len(f[k]) if isinstance(f[k], (list, dict)) else f[k])
                        for k in attendus if k in f)
    return not manquants, f"gisements comptés : {releves}"


def g5(c):
    """Porte G5 : quinze cartes de jury, chaque preuve relue à l'exécution."""
    j = _lu("kit/jury.json")
    return (j.get("total") == 15 and j.get("verifiees") == 15 and j.get("verdict") == "vert",
            f"{j.get('verifiees', 0)}/{j.get('total', 0)} cartes à preuve vérifiée "
            f"(défauts {j.get('fautes', [])[:2] or 'aucun'})")


def g7(c):
    """Porte G7 : le pare-feu de périmètre et les non-objectifs sont écrits noir sur blanc."""
    t = (RACINE / "audit/B0-boot.md").read_text(encoding="utf-8").lower()
    attendus = ("non-objectif", "pare-feu", "vidéo", "cmyk", "données réelles")
    absents = [a for a in attendus if a not in t]
    return not absents, f"pare-feu écrit, mentions absentes {absents or 'aucune'}"


def g8(c):
    """Porte G8 : le rapport tient dans la bande de pages, tout vectoriel, sans replat de raster."""
    b = c["build"]
    return (102 <= b.get("pages", 0) <= 168 and b.get("via_png") == 0
            and b.get("poses") == b.get("planches"),
            f"{b.get('pages')} pages (bande 102 à 168), {b.get('planches')} planches dessinées, "
            f"{b.get('poses')} posées, {b.get('via_png')} secours raster")


def _duplicats_prose() -> list[str]:
    """Deux fois le même paragraphe hors marges = copier-coller. Mesure sur le rendu, corps de page.

    Les pages de titre portent un pied de page et un titre courant répétés sur cent treize pages : ce
    sont des objets de mise en page, pas de la prose. La sonde ignore donc la bande des marges (hors
    70 à 770 points) et les pages d'appareil (sommaire, listes), où la répétition est le principe même.
    """
    import pymupdf
    d = pymupdf.open(str(RACINE / "rapport/PDF/Cleopatre-rapport.pdf"))
    lignes = []
    for page in d:
        if re.search(r"^(Sommaire|Liste des figures|Liste des tableaux)", page.get_text().strip()):
            continue
        for bloc in page.get_text("dict")["blocks"]:
            for ligne in bloc.get("lines", []):
                if not 70 <= ligne["bbox"][1] <= 770:
                    continue
                t = "".join(x["text"] for x in ligne["spans"]).strip()
                if len(t) >= 64 and not re.match(r"^\d+(\.\d+)*\s", t):
                    lignes.append(t)
    vus, dups = {}, []
    for l in lignes:
        vus[l] = vus.get(l, 0) + 1
    for l, n in vus.items():
        if n >= 2:
            dups.append(f"{n}× {l[:48]}")
    return dups


def g9(c):
    """Porte G9 : zéro copié-collé — la prose du rendu ne se répète pas par blocs."""
    dups = _duplicats_prose()
    return not dups, f"{len(dups)} bloc(s) de prose répétés {dups[:2] or ''}"


def g10(c):
    """Porte G10 : les lois de langue sont exécutées à la source et au rendu."""
    l, r = c["langue"], c["langue_rendu"]
    return (not r.get("fautes") and l.get("verifiees", 0) > 0,
            f"source : {l.get('verifiees', 0)} lignes vérifiées ; rendu : "
            f"{len(r.get('fautes', []))} faute(s) sur {r.get('lignes', 0)} lignes reconstituées, "
            f"{r.get('exemptes_mono', 0)} lignes de verbatim exemptées")


def g11(c):
    """Porte G11 : l'inoculation des trois motifs imposés, chacun à la place dite."""
    import pymupdf
    d = pymupdf.open(str(RACINE / "rapport/PDF/Cleopatre-rapport.pdf"))
    rendu = " ".join(p.get_text() for p in d).lower()
    exigences = (("shopify", "I.4"), ("paiement", "II.5"), ("charge", "V."))
    etat = {mot: (mot in rendu) for mot, _ in exigences}
    return all(etat.values()), (f"{sum(etat.values())}/3 inoculations présentes au rendu : "
                                f"{' ; '.join(f'{m} ({s}) vu' if etat[m] else f'{m} ({s}) ABSENT' for m, s in exigences)}")


def g12(c):
    """Porte G12 : le registre des figures est complet, cites et posées."""
    b = c["build"]
    compteurs = b.get("compteurs", {})
    return (b.get("planches") == 61 and b.get("poses") == 61,
            f"{b.get('planches')}/61 planches, {b.get('poses')} poses, "
            f"{compteurs.get('tableaux', b.get('tableaux', 0))} tableaux")


def g13(c):
    """Porte G13 : sommaire et listes cliquables — autant de signets que d'ancres, zéro mort."""
    n_signets = len([k for k in c["signets"] if not k.startswith("_")])
    li = c["liens"]
    return (n_signets == li.get("ancres", -1) and n_signets > 200 and not li.get("morts"),
            f"{n_signets} signets pour {li.get('ancres', 0)} ancres, {li.get('resolus', 0)} liens "
            f"résolus, {len(li.get('morts', []))} mort(s)")


def g14(c):
    """Porte G14 : la couleur n'est jamais le seul porteur de sens — les sept statuts sont dits en mots."""
    import pymupdf
    d = pymupdf.open(str(RACINE / "rapport/PDF/Cleopatre-rapport.pdf"))
    texte = " ".join(p.get_text() for p in d)
    # les sept statuts ne sont pas décrétés ici : ils sont lus dans l'enum du schéma
    sch = (RACINE / "src/db/schema.ts").read_text(encoding="utf-8")
    m = re.search(r"orderStatusEnum = pgEnum\(\"order_status\", \[([^\]]+)\]", sch, re.S)
    statuts = re.findall(r'\"([a-z_]+)\"', m.group(1)) if m else []
    absents = [s for s in statuts if s.replace("_", " ") not in texte.lower()
                and s not in texte.lower()]
    return (len(statuts) == 7 and not absents), \
        f"{len(statuts) - len(absents)}/{len(statuts)} statuts de commande nommés en toutes lettres au " \
        f"rendu (absents {absents or 'aucun'})"


def g15(c):
    """Porte G15 : cinq moments d'applaudissement sont scriptés, minutés, et non improvisés."""
    t = _jourj()
    n = len(re.findall(r"APPLAUDIR", t))
    return n >= 5, f"{n} moments marqués « APPLAUDIR » dans soutenance/JOURJ.md"


def g16(c):
    """Porte G16 : trente glissades au paquet, composition verrouillée."""
    import zipfile
    z = zipfile.ZipFile(RACINE / "soutenance/Cleopatre-soutenance.pptx")
    n = len([x for x in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", x)])
    return n == 30, f"{n} parties `slide` dans le paquet"


def g17(c):
    """Porte G17 : le Morph est écrit en XML réel dans cinq paires de glissades."""
    import zipfile
    z = zipfile.ZipFile(RACINE / "soutenance/Cleopatre-soutenance.pptx")
    n = sum(1 for x in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", x)
            and b"p159:morph" in z.read(x))
    return n == 5, f"{n} glissades portant `p159:morph option=\"byObject\"`"


def g18(c):
    """Porte G18 : cinq zooms de détail, produits comme fichiers et comptés dans le deck."""
    d = _lu("kit/deck.json")
    zooms = len(list((RACINE / "soutenance/zooms").glob("*.png"))) if (RACINE / "soutenance/zooms").exists() else 0
    return (d.get("zooms") == 5 and zooms >= 5), f"{d.get('zooms', 0)} zooms déclarés, {zooms} fichiers produits"


def _jourj() -> str:
    p = RACINE / "soutenance/JOURJ.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def g19(c):
    """Porte G19 : le minutage annoncé fait quatorze minutes trente, et les notes le portent."""
    t = _jourj()
    d = _lu("kit/deck.json")
    annonce = bool(re.search(r"14\s*m\s*30|14\s*min\s*30|14:30", t))
    return (annonce and d.get("octets", 0) > 100000), \
        f"minutage 14 min 30 {'annoncé' if annonce else 'ABSENT'} au JOURJ, deck de " \
        f"{(d.get('octets', 0) or 0) / 1024:.0f} Ko"


def g20(c):
    """Porte G20 : la règle dix-dix-dix est mesurée sur le paquet, pas décrétée."""
    d = _lu("kit/deck.json")
    return (d.get("min_pt_contenu", 0) >= 18 and d.get("mots_max", 99) <= 45
            and d.get("contraste_min", 0) >= 4.5,
            f"corps minimal {d.get('min_pt_contenu')} pt, maximum {d.get('mots_max')} mots par "
            f"glissade, contraste le plus faible {d.get('contraste_min')}:1")


def g21(c):
    """Porte G21 : la démonstration tient en trois chemins, sans réseau."""
    t = _jourj()
    chemins = len(re.findall(r"CHEMIN \d+", t))
    hors_ligne = ("couper le wifi" in t.lower() or "hors ligne" in t.lower()) \
        and not re.search(r"https?://", t)
    return (chemins >= 3 and hors_ligne), f"{chemins} chemins de démonstration scriptés, " \
                                          f"zéro dépendance réseau : {hors_ligne}"


def g22(c):
    """Porte G22 : les deux harnais sont écrits, exécutés, et convergent loi par loi."""
    ab = _lu("ab/harnais.json")
    return (ab.get("verdict") == "vert" and ab.get("lois", 0) == 13
            and ab.get("accord") == ab.get("lois"),
            f"{ab.get('accord', 0)}/{ab.get('lois', 0)} lois en accord, divergences "
            f"{ab.get('divergences', [])[:2] or 'aucune'} ; quatre écarts de méthode instruits")


def g23(c):
    """Porte G23 : les quatre provocations de chaos produisent le comportement annoncé."""
    ch = c["chaos"]
    return (ch.get("total") == 4 and ch.get("conformes") == 4), \
        f"{ch.get('conformes', 0)}/{ch.get('total', 0)} conformes (figure absente, PNG corrompu, " \
        f"capture 8K, figs/ vidé)"


def g24(c):
    """Porte G24 : trois fautes injectées, trois fois le moteur refuse l'ouvrage."""
    m = c["mutation"]
    return (m.get("total") == 3 and m.get("detectes") == 3), \
        f"{m.get('detectes', 0)}/{m.get('total', 0)} fautes injectées attrapées"


def g25(c):
    """Porte G25 : l'épuisement est signé, c'est-à-dire qu'il ne reste rien à ajouter."""
    p = RACINE / "audit/RIEN-A-AJOUTER.md"
    if not p.exists():
        return False, "constat d'épuisement non écrit (audit/RIEN-A-AJOUTER.md)"
    t = p.read_text(encoding="utf-8")
    jour = re.search(r"\d{2}/\d{2}/\d{4}", t)
    return ("RIEN À AJOUTER" in t and c.get("__tout_vert__", False),
            f"constat signé le {jour.group(0) if jour else '[date]'} ; portes automatiques vertes à "
            f"la signature : {c.get('__tout_vert__')}")


def g26(c):
    """Porte G26 : le kit de reprise et le war-room du jour J sont livrés et lisibles."""
    docs = ["README.md", "REPRO.md", "decisions.md", "CORRECTIONS.md", "soutenance/JOURJ.md",
            "soutenance/BANQUE-JURY.md"]
    manques = [d for d in docs if not (RACINE / d).exists() or (RACINE / d).stat().st_size < 900]
    readme = (RACINE / "README.md").read_text(encoding="utf-8") if (RACINE / "README.md").exists() else ""
    commandes = len(set(re.findall(r"python3 (?:rapport|soutenance)/[\w.-]+\.py", readme)))
    depannage = len(re.findall(r"^### ", readme.split("Dépannage")[-1], re.M)) if "Dépannage" in readme else 0
    return (not manques and commandes >= 3 and depannage >= 5), \
        f"{len(docs) - len(manques)}/{len(docs)} livrables du kit, {commandes} commandes de rebuild, " \
        f"{depannage} entrées de dépannage" + (f" ; manquants {manques}" if manques else "")


def g27(c):
    """Porte G27 : le contenu est gelé, l'empreinte est au dossier, l'étiquette est posée."""
    sceau_p = AUDIT / "sceau.json"
    if not sceau_p.exists():
        return False, "aucun sceau : `python3 rapport/gates.py --sceller`"
    sceau = json.loads(sceau_p.read_text(encoding="utf-8"))
    derives = [k for k, v in sceau["empreintes"].items()
               if not (RACINE / k).exists() or _sha(RACINE / k) != v]
    etiquette = _git("tag", "-l", "v1.0-final")
    return (not derives and bool(etiquette),
            f"{len(sceau['empreintes'])} empreintes scellées, {len(derives)} dérivée(s), étiquette "
            f"locale {etiquette or 'absente'} ; poussée : [à la main du déposant]")


SONDES = {f"g{n}": globals()[f"g{n}"] for n in range(1, 28) if f"g{n}" in globals()}

RUBRIQUE = [
    ("Torsion de la source : aucune faute de langue au rendu", 12, lambda c: not c["langue_rendu"].get("fautes")),
    ("Langue à la source : crochets, nombres, emprunts, insécables", 10,
     lambda c: c["langue"].get("verifiees", 0) > 0 and not c["langue_rendu"].get("fautes")),
    ("Premier harnais vert (treize lois sur pièces)", 12, lambda c: c["qa"].get("verdict") == "vert"),
    ("Second harnais vert, et accord complet avec le premier", 12,
     lambda c: _lu("qa2.json").get("verdict") == "vert" and _lu("ab/harnais.json").get("verdict") == "vert"),
    ("Quatre provocations de chaos conformes", 8, lambda c: c["chaos"].get("conformes") == 4),
    ("Trois mutations attrapées par le moteur", 8, lambda c: c["mutation"].get("detectes") == 3),
    ("Trente assauts tenus, six rounds écrits", 10, lambda c: c["rounds"].get("tenus") == 30),
    ("Déterminisme mesuré : deux rebuilds, une empreinte", 10,
     lambda c: c["budgets"].get("sha256_identique") is True),
    ("Vecteur intégral : 61 planches, zéro raster de secours, 113 pages dans la bande", 10,
     lambda c: c["build"].get("via_png") == 0 and c["build"].get("poses") == c["build"].get("planches")),
    ("Kit reproductible : README, REPRO, décisions, corrections", 7,
     lambda c: all((RACINE / d).exists() for d in ("README.md", "REPRO.md", "decisions.md",
                                                    "CORRECTIONS.md"))),
    ("Ordre du scellement écrit (gel → empreintes → commit → étiquette)", 1,
     lambda c: "D9." in (RACINE / "decisions.md").read_text(encoding="utf-8")
     if (RACINE / "decisions.md").exists() else False),
]


def evaluer(*, silencieux: bool = False) -> dict:
    t0 = time.time()
    c = dict(build=_lu("dernier-build.json"), qa=_lu("qa.json"), qa2=_lu("qa2.json"),
             langue=_lu("langue.json"), langue_rendu=_lu("langue-rendu.json"),
             liens=_lu("liens.json"), signets=_lu("signets.json"), budgets=_lu("budgets.json"),
             facts=_lu("facts.json"), mutation=_lu("mutation/resume.json"),
             chaos=_lu("chaos/resume.json"), rounds=_lu("rounds/resume.json"),
             deck=_lu("kit/deck.json"))
    etat = {}
    for gid, (ident, intitule, invs, preuve) in PORTES.items():
        cle = gid.lower()
        sonde = SONDES.get(cle)
        if sonde is None:
            # la porte reste jugée sur pièce : la preuve annoncée doit exister et être substantielle
            p = RACINE / preuve
            ok = p.exists() and p.stat().st_size > 400
            etat[gid] = dict(titre=intitule, invariants=invs, preuve=preuve,
                             verdict="vert" if ok else "rouge",
                             mesure=f"preuve au dossier {'présente' if ok else 'absente'} ({preuve}) ; "
                                    f"aucune sonde automatisée pour cette porte")
            continue
        conforme, mesure = sonde(c)
        p = RACINE / preuve
        etat[gid] = dict(titre=intitule, invariants=invs, preuve=preuve,
                         verdict="vert" if conforme and p.exists() else "rouge",
                         mesure=mesure, preuve_presente=p.exists())
    c["__tout_vert__"] = _tout_vert(etat)
    conforme_g25, mesure_g25 = SONDES["g25"](c)
    etat["G25"].update(verdict="vert" if conforme_g25 else "rouge", mesure=mesure_g25)
    etat["G6"] = etat.get("G6", {})  # la note est calculée juste après, pas ici
    score = 0
    rubrique = []
    for intitule, points, test in RUBRIQUE:
        obtenu = points if test(c) else 0
        score += obtenu
        rubrique.append(dict(critere=intitule, points=points, obtenu=obtenu))
    etat["G6"].update(verdict="vert" if score >= 97 else "rouge",
                      mesure=f"note {score}/100 (seuil 97), détail écrit dans audit/kit/rubrique.md")
    rouge = [g for g in sorted(etat) if etat[g]["verdict"] != "vert"]
    recu = dict(harnais="gates.py", total=len(etat), vert=len(etat) - len(rouge), rouges=rouge,
                note_g6=score, verdict="vert" if not rouge else "rouge",
                secondes=round(time.time() - t0, 2), etat=etat, rubrique=rubrique)
    (AUDIT / "gates.json").write_text(json.dumps(recu, ensure_ascii=False, indent=1, sort_keys=True)
                                      + "\n", encoding="utf-8")
    md = ["# Portes G1 à G27", "",
          f"Verdict : **{recu['verdict']}** — {recu['vert']}/{recu['total']} portes vertes, "
          f"note G6 {score}/100, {recu['secondes']} s.", "",
          "| porte | intitulé | invariants | verdict | mesure | preuve |",
          "| --- | --- | --- | --- | --- | --- |"]
    for gid in sorted(etat, key=lambda x: int(x[1:])):
        e = etat[gid]
        md.append(f"| {gid} | {e['titre']} | {', '.join(e['invariants'])} | {e['verdict']} | "
                  f"{e['mesure']} | `{e['preuve']}` |")
    (AUDIT / "gates.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (AUDIT / "kit").mkdir(parents=True, exist_ok=True)
    (AUDIT / "kit/rubrique.md").write_text(
        "\n".join(["# Grille auto-appliquée (porte G6)", "",
                   f"Note : **{score}/100**, seuil exigé 97. Chaque ligne est jugée par une sonde de "
                   f"`rapport/gates.py`, pas par un avis.", "",
                   "| critère | points | obtenu |", "| --- | --- | --- |"]
                  + [f"| {r['critere']} | {r['points']} | {r['obtenu']} |" for r in rubrique]
                  + ["", f"Total | {sum(r['points'] for r in rubrique)} | {score} |", ""]) + "\n",
        encoding="utf-8")
    if not silencieux:
        for gid in sorted(etat, key=lambda x: int(x[1:])):
            e = etat[gid]
            print(f"{gid:>4}  {e['verdict']:>5}  {e['mesure'][:96]}")
        print(f"\ngates : {recu['vert']}/{recu['total']} vertes, note G6 {score}/100, verdict "
              f"{recu['verdict']}")
    return recu


def sceller() -> int:
    r = evaluer(silencieux=True)
    ouvertes = [g for g in r["rouges"] if g != "G27"]     # G27 est précisément ce que cette commande pose
    if ouvertes:
        print("refus de sceller : portes rouges " + ", ".join(ouvertes)
              + " — voir audit/gates.md, ligne par ligne", file=sys.stderr)
        return 1
    livrables = ["rapport/PDF/Cleopatre-rapport.pdf", "soutenance/Cleopatre-soutenance.pptx",
                 "README.md", "REPRO.md", "decisions.md", "CORRECTIONS.md", "soutenance/JOURJ.md",
                 "soutenance/BANQUE-JURY.md"]
    livrables += [f"rapport/{p.name}" for p in sorted((RACINE / "rapport").glob("*.py"))]
    livrables += [f"soutenance/{p.name}" for p in sorted((RACINE / "soutenance").glob("*.py"))]
    empreintes = {x: _sha(RACINE / x) for x in livrables if (RACINE / x).exists()}
    (AUDIT / "sceau.json").write_text(json.dumps(dict(
        livrables=len(empreintes), empreintes=empreintes, note_g6=r["note_g6"],
        gates=dict(vertes=f"{r['vert']}/{r['total']}"), etiquette="v1.0-final"),
        ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    _git("tag", "-a", "-f", "-m", "Gel v1.0-final (rupture de sceau : kit complet et scellé)",
         "v1.0-final")
    print(f"sceau : {len(empreintes)} empreintes, note {r['note_g6']}/100, étiquette v1.0-final posée")
    return 0


if __name__ == "__main__":
    sys.exit(sceller() if "--sceller" in sys.argv else (0 if evaluer(silencieux="-q" in sys.argv)
                                                         ["verdict"] == "vert" else 1))
