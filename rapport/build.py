"""rapport/build.py — constructeur unique du rapport PDF.

Enchaînement (dans cet ordre, parce que l'ordre est une correction de faute connue — §9) :

1. `mpl.build_all()` : les 61 planches en PDF **et** PNG vectoriels, ratios assertés identiques ;
2. passes de texte jusqu'à stabilisation de la pagination : le sommaire, la liste des planches et
   chaque renvoi `[[R:cle]]` impriment le numéro de page **de la page courante du build**, jamais
   un copier-coller de la veille ;
3. placage `merge_transformed_page` en millimètres, `y = PH − (y + hh)·MM`, échelle déduite de la
   `mediabox` du timbre ;
4. résolution des liens internes (GoTo nommés → GoTo directs), signets sur trois niveaux,
   métadonnées ;
5. autocontrôles (toute figure citée est posée, aucune boîte hors page, aucun chevauchement,
   aucune légende manquante) puis budgets §7.

`--dry-run` imprime la grille sans écrire le PDF final ; `--determinisme` construit deux fois et
compare les sha256 (INV-1). Toute anomalie lève une exception : le build refuse, il n'avertit pas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import re
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from pypdf import PdfReader, PdfWriter                                    # noqa: E402
from pypdf.generic import ArrayObject, DictionaryObject, NameObject       # noqa: E402

from rapport import doc                                                    # noqa: E402
from rapport.doc import A4                                                 # noqa: E402

MM = 72 / 25.4
PAGE_H_MM = A4[1] / MM
PAGE_W_MM = A4[0] / MM
DOSSIER = RACINE / "rapport"
PDF_REPERTOIRE = DOSSIER / "PDF"
BASE = PDF_REPERTOIRE / "base.pdf"
FINAL = PDF_REPERTOIRE / "Cleopatre-rapport.pdf"
AUDIT = RACINE / "audit"
FIGEE = "D:20260101000000+00'00'"        # horodatage figé : sans lui, pas de déterminisme possible


def cites_enregistrees(txt: dict) -> int:
    """Nombre de citations de planches déclarées par le contenu (contrôle croisé de l'audit)."""
    return sum(1 for k in txt["cles"] if k.startswith("fig."))
MODULES_CONTENU = ["content_a", "content_b", "content_c", "content_d", "content_e", "content_f"]

# budgets §7 (seuils, pas des intentions)
BUDGET_MO_PDF = 30.0
BUDGET_PAGES = 120          # cible §2 du prompt
PAGE_PLANCHER = 102        # en dessous, le document s'est effondré
PAGE_PLAFOND = 168         # au-dessus, il gonfle et ne se lit plus
BUDGET_BUILD_S = 600.0
BUDGET_FIGS_S = 300.0


def hachier(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ─────────────────────────────────────────────────────────── figures
def figures(*, dpi: int = 300, only: set[str] | None = None) -> dict:
    from rapport import mpl
    mpl.import_all()
    t0 = time.time()
    infos = mpl.build_all(only=only, dpi=dpi)
    secondes = time.time() - t0
    if secondes > BUDGET_FIGS_S:
        raise RuntimeError(f"figures : {secondes:.0f} s > budget {BUDGET_FIGS_S:.0f} s (§7) — "
                           "profiler le tracé, ne pas réduire la qualité")
    return dict(infos=infos, secondes=round(secondes, 2))


# ─────────────────────────────────────────────────────────── texte (passes)
def doc_build(fab, sortie: Path) -> tuple[int, dict]:
    """Une passe complète de mise en page : renvoie (nombre de pages, ancres → page)."""
    reg = doc.Registre()
    gabarit = doc.Toile(sortie, reg,
                        author="[Prénom NOM de l'auteur]",
                        subject="Rapport de projet — plateforme e-commerce Cléopâtre",
                        creator="rapport/build.py (dépôt nassimfinal)",
                        keywords="parapharmacie, Next.js, PostgreSQL, e-commerce, Tunisie, mémoire")
    gabarit.build(fab.flux)
    return len(PdfReader(str(sortie)).pages), dict(reg.pages_signets)


def construire_texte(sortie: Path, *, max_passes: int = 6) -> dict:
    from rapport.contenu import Fab
    import importlib
    modules = [importlib.import_module(f"rapport.{m}") for m in MODULES_CONTENU]
    pages: dict[str, dict] = {}
    hist: list[dict] = []
    placements: list[dict] = []
    fab = None
    for passe in range(1, max_passes + 1):
        doc.reinitialiser_placements()
        fab = Fab(pages=pages)
        for m in modules:
            m.fabriquer(fab)
        fab.materialiser()
        fab.autoverif()
        n_pages, nouveau = doc_build(fab, sortie)
        instable = passe == 1 or any(pages.get(cle, {}).get("page") != info["page"]
                                    for cle, info in nouveau.items())
        hist.append(dict(passe=passe, ancres=len(nouveau), pages=n_pages))
        placements = list(doc.PLACEMENTS)
        pages = nouveau
        if not instable:
            break
    else:
        raise RuntimeError(f"la pagination ne se stabilise pas en {max_passes} passes : {hist}")
    from rapport.mpl import REGISTRE          # le registre est rempli par figures(), avant la texte
    citees = {k[4:] for k in fab.cles if k.startswith("fig.")}
    orphelines = sorted(set(REGISTRE) - citees)
    if orphelines and not getattr(fab, "tolere_orphelines", False):
        raise RuntimeError(f"{len(orphelines)} planche(s) dessinée(s) et jamais citée(s) : "
                           f"{orphelines[:6]} — soit les appeler dans le texte, soit retirer le dessin "
                           "(rasoir §2 : une figure que personne ne cite est du travail caché)")
    return dict(pages=pages, placements=placements, hist=hist,
                compteurs=dict(figures=fab.n_fig, tableaux=fab.n_tab, extraits=fab.n_code,
                               pages=n_pages),
                cles=dict(fab.cles), langue=dict(verifiees=fab.verifiees, exemptees=fab.exemptees))


# ─────────────────────────────────────────────────────────── placage
def placer(base: Path, placements: list[dict], sortie: Path, *, pages_signets: dict) -> dict:
    """Fusion des timbres vectoriels dans la base, aux coordonnées relevées à la pose."""
    lecteur = PdfReader(str(base))
    escreveur = PdfWriter()
    for p in lecteur.pages:
        escreveur.add_page(p)
    figs = DOSSIER / "figs"
    poses = png_degrades = 0
    par_page: dict[int, list] = {}
    for pl in placements:
        par_page.setdefault(pl["page"], []).append(pl)
        if pl.get("via_png"):
            png_degrades += 1            # collé par ReportLab en niveau L2 déclaré : pas de placage
            continue
        timbre = figs / f"{pl['fid']}.pdf"
        if not timbre.exists():
            raise FileNotFoundError(f"chaos C1 : placement déclaré mais timbre absent — {timbre}")
        st = PdfReader(str(timbre)).pages[0]
        natif_w, natif_h = float(st.mediabox.width), float(st.mediabox.height)
        if natif_w <= 0 or natif_h <= 0:
            raise RuntimeError(f"{pl['fid']} : mediabox dégénérée ({natif_w}×{natif_h})")
        ratio_timbre = natif_w / natif_h
        ratio_creux = pl["w_mm"] / pl["h_mm"]
        if abs(ratio_timbre - ratio_creux) > 0.02:
            raise RuntimeError(f"{pl['fid']} : ratio du creux {ratio_creux:.4f} ≠ ratio du timbre "
                               f"{ratio_timbre:.4f} — déformation refusée")
        if pl["x_mm"] < 18 or pl["x_mm"] + pl["w_mm"] > PAGE_W_MM - 18:
            raise RuntimeError(f"{pl['fid']} : hors marges latérales (x={pl['x_mm']},"
                               f" w={pl['w_mm']}, page={PAGE_W_MM:.1f})")
        if pl["y_mm"] < 16 or pl["y_mm"] + pl["h_mm"] > PAGE_H_MM - 15:
            raise RuntimeError(f"{pl['fid']} : hors zone imprimable (y={pl['y_mm']}, h={pl['h_mm']})")
        s = (pl["w_mm"] * MM) / natif_w
        escreveur.pages[pl["page"]].merge_transformed_page(
            st, (s, 0, 0, s, pl["x_mm"] * MM, PAGE_H_MM * MM - (pl["y_mm"] + pl["h_mm"]) * MM))
        poses += 1
    chevauchements = []
    for pg, lst in par_page.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                a, b = lst[i], lst[j]
                if (a["x_mm"] < b["x_mm"] + b["w_mm"] - 0.5 and b["x_mm"] < a["x_mm"] + a["w_mm"] - 0.5
                        and a["y_mm"] < b["y_mm"] + b["h_mm"] - 0.5
                        and b["y_mm"] < a["y_mm"] + a["h_mm"] - 0.5):
                    chevauchements.append(dict(page=pg + 1, a=a["fid"], b=b["fid"]))
    if chevauchements:
        raise RuntimeError(f"chevauchement de plaques : {chevauchements[:3]}")
    # signets sur trois niveaux (les ancres portent leur niveau) — reconstruction explicite
    parents: dict[int, object] = {}
    for cle, info in sorted(pages_signets.items(), key=lambda kv: (kv[1]["page"], kv[1]["niveau"],
                                                                   kv[0])):
        niveau = int(info.get("niveau", 1))
        titre = re.sub(r"\s+", " ", info["titre"]).strip()
        index = min(max(info["page"] - 1, 0), len(escreveur.pages) - 1)
        parent = parents.get(niveau - 1) if niveau > 1 else None
        try:
            parents[niveau] = escreveur.add_outline_item(titre, index, parent=parent)
        except Exception:
            parents[niveau] = escreveur.add_outline_item(titre, index)
    escreveur.add_metadata({
        "/Title": "Cléopâtre — Espace Santé Beauté : rapport de projet",
        "/Author": "[Prénom NOM de l'auteur]",
        "/Subject": "Plateforme e-commerce d'une parapharmacie tunisienne (Ezzahra · Hammam-Lif)",
        "/Keywords": "parapharmacie, e-commerce, Next.js, PostgreSQL, Drizzle, Tunisie, "
                     "mémoire de fin d'études",
        "/Creator": "rapport/build.py — dépôt nassimfinal",
        "/Producer": "ReportLab (texte) + pypdf (placements millimétrés)",
        "/CreationDate": "D:20260101000000+00'00'",
        "/ModDate": "D:20260101000000+00'00'"})
    sortie.parent.mkdir(parents=True, exist_ok=True)
    with open(sortie, "wb") as fh:
        escreveur.write(fh)
    return dict(poses=poses, via_png=png_degrades, chevauchements=0,
                signets=len(pages_signets))


# ─────────────────────────────────────────────────────────── liens internes
def resoudre_liens(pdf: Path, registre: dict[str, dict]) -> dict:
    """Contrôle des liens internes : chaque annotation doit atterrir sur une page qui porte une ancre.

    ReportLab émet déjà des destinations directes (`/Dest` sur l'annotation) quand la cible est
    connue à la composition, et des destinations nommées quand elle passe par le dictionnaire de
    destinations. Le placage pypdf conservant les premières mais pas toujours les secondes, la
    fonction normalise tout en destinations directes, puis vérifie la cible. Un lien mort n'est pas
    un avertissement : c'est une faute d'ouvrage, et le build s'arrête.
    """
    w = PdfWriter(clone_from=pdf)
    pages_ancre = {max(int(info["page"]) - 1, 0) for info in registre.values()}
    # Après placage, `/Dest` est un tableau brut [page, /Fit] et non un objet Destination : la page
    # cible se reconnaît par identité d'objet, ce qui est exact et indépendant du nom de la clé.
    index_par_objet = {id(pg): k for k, pg in enumerate(w.pages)}
    total = directs = nommes = 0
    morts: list[str] = []
    for i, page in enumerate(w.pages):
        for a in (page.get("/Annots") or []):
            ob = a.get_object()
            if ob.get("/Subtype") != "/Link":
                continue
            total += 1
            acte = ob.get("/A")
            if acte is not None and "/D" in acte and acte.get("/S") in (None, "/GoTo"):
                d = acte["/D"]
                if isinstance(d, (ArrayObject, list)) and d:
                    ob[NameObject("/Dest")] = d
                    del ob[NameObject("/A")]
                else:
                    cle = str(d)
                    if cle in registre:
                        idx = min(max(int(registre[cle]["page"]) - 1, 0), len(w.pages) - 1)
                        ob[NameObject("/Dest")] = ArrayObject(
                            [w.pages[idx].indirect_ref, NameObject("/Fit")])
                        del ob[NameObject("/A")]
                        nommes += 1
                    else:
                        morts.append(f"p.{i + 1} : destination nommée inconnue {cle!r}")
                        continue
            elif acte is not None:
                # lien externe (URL) : hors contrôle interne, compté séparément
                continue
            if "/Dest" not in ob:
                morts.append(f"p.{i + 1} : annotation de lien sans destination")
                continue
            dest = ob["/Dest"]
            if isinstance(dest, (ArrayObject, list)):
                dest = dest[0] if dest else None
            ref = dest.get_object() if hasattr(dest, "get_object") else dest
            idx = index_par_objet.get(id(ref))
            if idx is None:
                try:
                    idx = w.get_destination_page_number(ob)
                except Exception as exc:                  # noqa: BLE001 - message lisible exigé
                    morts.append(f"p.{i + 1} : destination illisible ({exc})")
                    continue
            directs += 1
            if idx not in pages_ancre:
                morts.append(f"p.{i + 1} → p.{idx + 1} : la page cible ne porte aucune ancre posée")
    with open(pdf, "wb") as fh:
        w.write(fh)
    return dict(liens=total, resolus=directs, nommes_resolus=nommes, morts=morts)


# ─────────────────────────────────────────────────────────── orchestration
def construire(*, sortie: Path = FINAL, dry_run: bool = False, dpi: int = 300) -> dict:
    t0 = time.time()
    PDF_REPERTOIRE.mkdir(parents=True, exist_ok=True)
    if dry_run:
        infos = figures(dpi=150)
        txt = construire_texte(BASE, max_passes=6)
        grille = "\n".join(
            f"p{pl['page'] + 1:>3}  {pl['fid']:<8} x={pl['x_mm']:>7} y={pl['y_mm']:>7} "
            f"w={pl['w_mm']:>6} h={pl['h_mm']:>6}"
            for pl in sorted(txt["placements"], key=lambda z: (z["page"], z["y_mm"])))
        print(f"[dry-run] {len(infos['infos'])} planches · {len(txt['placements'])} creux · "
              f"{txt['hist'][-1]['pages']} pages\n{grille}")
        return dict(dry_run=True, pages=txt["hist"][-1]["pages"], planches=len(infos["infos"]))
    infos = figures(dpi=dpi)
    txt = construire_texte(BASE)
    plac = placer(BASE, txt["placements"], sortie, pages_signets=txt["pages"])
    liens = resoudre_liens(sortie, txt["pages"])
    if liens["morts"]:
        raise RuntimeError(f"{len(liens['morts'])} lien(s) interne(s) mort(s) dans le PDF :\n  "
                           + "\n  ".join(liens["morts"][:8]))
    if not liens["liens"]:
        raise RuntimeError("aucun lien interne dans un document qui annonce un sommaire cliquable")
    r = PdfReader(str(sortie))
    n_pages = len(r.pages)
    citees = {k[4:] for k in txt["cles"] if k.startswith("fig.")}
    posees = {pl["fid"] for pl in txt["placements"]}
    if citees - posees:
        raise RuntimeError(f"figures citées sans placement : {sorted(citees - posees)}")
    if posees - citees:
        raise RuntimeError(f"plaques posées sans référence déclarée : {sorted(posees - citees)}")
    # INV-13 est contrôlé dans construire_texte (donc aussi en dry-run) : le contrôle d'orphelinage
    # n'a rien à faire dans la seule voie du PDF, un brouillon doit déjà le refuser.
    if citees - set(infos["infos"]):
        raise RuntimeError(f"plaque citée sans rendu : {sorted(citees - set(infos['infos']))}")
    if not (PAGE_PLANCHER <= n_pages <= PAGE_PLAFOND):
        raise RuntimeError(f"pagination hors cible : {n_pages} pages (attendu entre {PAGE_PLANCHER} et "
                           f"{PAGE_PLAFOND}, cible {BUDGET_PAGES}) — le rasoir §2 n'est pas une "
                           "suggestion, et un effondrement de mise en page est une panne")
    secondes = time.time() - t0
    octets = sortie.stat().st_size
    if octets > BUDGET_MO_PDF * 1024 * 1024:
        raise RuntimeError(f"budget §7 dépassé : {octets / 1e6:.1f} Mo > {BUDGET_MO_PDF} Mo")
    if secondes > BUDGET_BUILD_S:
        raise RuntimeError(f"budget §7 dépassé : build {secondes:.0f} s > {BUDGET_BUILD_S:.0f} s")
    mesures = dict(pages=n_pages, planches=len(infos["infos"]), creux=len(txt["placements"]),
                   poses=plac["poses"], via_png=plac["via_png"], octets_pdf=octets,
                   secondes_build=round(secondes, 1), secondes_figs=infos["secondes"],
                   liens=liens["liens"], liens_resolus=liens["resolus"], morts=liens["morts"],
                   signets=len(txt["pages"]), sha256=hachier(sortie),
                   compteurs=txt["compteurs"], passes=txt["hist"])
    AUDIT.mkdir(exist_ok=True)
    (AUDIT / "dernier-build.json").write_text(json.dumps(mesures, ensure_ascii=False, indent=1,
                                                         sort_keys=True) + "\n", encoding="utf-8")
    (AUDIT / "placements.json").write_text(json.dumps(txt["placements"], ensure_ascii=False, indent=1)
                                           + "\n", encoding="utf-8")
    (AUDIT / "liens.json").write_text(json.dumps(dict(liens, ancres=len(txt["pages"]),
                                                       cites=cites_enregistrees(txt),
                                                       horodatage=FIGEE), ensure_ascii=False, indent=1,
                                                     sort_keys=True) + "\n", encoding="utf-8")
    rendu = doc.verifier_rendu(sortie) if sortie.exists() else dict(lignes=0, fautes=[], exemptes_mono=0)
    if rendu["fautes"]:
        raise RuntimeError("loi des insécables violée sur le rendu :\n  "
                           + "\n  ".join(rendu["fautes"][:6]))
    (AUDIT / "langue-rendu.json").write_text(
        json.dumps(rendu, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (AUDIT / "langue.json").write_text(json.dumps(txt["langue"], ensure_ascii=False, indent=1,
                                                  sort_keys=True) + "\n", encoding="utf-8")
    (AUDIT / "signets.json").write_text(json.dumps(txt["pages"], ensure_ascii=False, indent=1,
                                                   sort_keys=True) + "\n", encoding="utf-8")
    # budgets.json = le fichier que lisent les planches de preuve (fig43, fig48). Il est fusionné,
    # jamais écravi : les clés du diaporama et de la QA sont posées par rapport/gates.py.
    bp = AUDIT / "budgets.json"
    ancien = json.loads(bp.read_text(encoding="utf-8")) if bp.exists() else {}
    det = AUDIT / "determinisme.txt"
    identique = "[à mesurer]"
    if det.exists():
        # booléen au registre, pas de chaîne : la porte G26 exige `true` et le PDF ne doit rien imprimer
        identique = "IDENTIQUES" in det.read_text(encoding="utf-8")
    budgets = dict(ancien)
    budgets.update(dict(pages=n_pages, figures=len(infos["infos"]), octets_pdf=octets,
                        secondes_build=round(secondes, 1), secondes_figs=infos["secondes"],
                        sha256_identique=identique, empreinte=mesures["sha256"],
                        cible_pages=BUDGET_PAGES, cible_mo_pdf=BUDGET_MO_PDF,
                        cible_build_s=BUDGET_BUILD_S, cible_figs_s=BUDGET_FIGS_S))
    bp.write_text(json.dumps(budgets, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                  encoding="utf-8")
    return mesures


def determinisme() -> dict:
    """Deux builds sur registre gelé : le seul écart possible est l'ouvrage, pas l'horloge.

    Le rapport imprime les durées du build précédent, lues dans `audit/`. Sans gel, le build A écrit le
    registre que le build B lit : les deux empreintes diffèrent d'un dixième de seconde, et
    l'invariant de déterminisme est violé pour une raison qui n'a rien d'un défaut du document.
    """
    gel = Path("/tmp/registre-determinisme")
    if gel.exists():
        shutil.rmtree(gel)
    gel.mkdir()
    registe = [p for p in AUDIT.glob("*.json")]
    for p in registe:
        shutil.copy2(p, gel / p.name)

    def _retablir():
        for p in gel.iterdir():
            shutil.copy2(p, AUDIT / p.name)

    a = construire(sortie=PDF_REPERTOIRE / "det-a.pdf")
    _retablir()
    b = construire(sortie=PDF_REPERTOIRE / "det-b.pdf")
    _retablir()
    ha = hachier(PDF_REPERTOIRE / "det-a.pdf")
    hb = hachier(PDF_REPERTOIRE / "det-b.pdf")
    (AUDIT / "determinisme.txt").write_text(
        "build A : " + ha + "\nbuild B : " + hb + "\nrésultat : "
        + ("IDENTIQUES" if ha == hb else "DIFFÉRENTS") + "\n"
        + f"pages : {a['pages']} / {b['pages']} · planches : {a['planches']} / {b['planches']}\n",
        encoding="utf-8")
    bp = AUDIT / "budgets.json"
    budgets = json.loads(bp.read_text(encoding="utf-8")) if bp.exists() else {}
    budgets["sha256_identique"] = (ha == hb)
    budgets["empreintes_determinisme"] = dict(a=ha, b=hb)
    bp.write_text(json.dumps(budgets, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                  encoding="utf-8")
    if ha != hb:
        raise RuntimeError("INV-1 violé : deux builds, deux empreintes\n" + ha + "\n" + hb)
    return dict(sha_a=ha, sha_b=hb, identique=True, pages=a["pages"], planches=a["planches"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="construit le rapport PDF (figures + texte + placage)")
    ap.add_argument("--dry-run", action="store_true", help="grille de placage, sans PDF final")
    ap.add_argument("--determinisme", action="store_true", help="deux builds, comparaison des sha256")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--sortie", type=Path, default=FINAL)
    a = ap.parse_args()
    out = determinisme() if a.determinisme else construire(sortie=a.sortie, dry_run=a.dry_run, dpi=a.dpi)
    print(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
