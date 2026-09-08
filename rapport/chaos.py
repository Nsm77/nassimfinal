"""rapport/chaos.py — §5, quatre environnements dégradés, quatre comportements attendus.

Le principe : ne pas promettre la robustesse, l'éprouver. Quatre états du dépôt sont fabriqués à la
main, la composition est relancée **en processus** (sans régénérer les planches, sinon le chaos
serait réparé avant d'être observé), et le comportement obtenu est confronté à celui qui était écrit
dans le cahier des charges. Toute divergence est rouge.

C1  timbre vectoriel absent, raster présent   → dégradation L2 **comptée**, pas de page blanche.
C2  raster présent mais illisible              → refus, exception, aucun carré vide imprimé.
C3  raster illégitimement énorme (capture 8K) → refus motivé : le poids n'est pas de l'information.
C4  répertoire `rapport/figs` vide             → refus immédiat, message nommant le répertoire.

Chaque état est défait dans un `finally`, et l'assertion de rétablissement fait partie du test.
Procès-verbal : `audit/chaos/resume.json` et `audit/chaos/rapport.md`.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
FIGS = RACINE / "rapport" / "figs"
BOUILLE = Path("/tmp/chaos-base.pdf")
VICTIME = "fig27"          # une planche citée, donc nécessaire à la composition
DEPLACEMENT = Path("/tmp/chaos-deplace.pdf")


def _composer() -> dict:
    from rapport import build
    return build.construire_texte(BOUILLE, max_passes=6)


def _avec_fichiers(mutate: callable, attendre: str):
    """Applique `mutate`, compose, rend le dépôt à son état exact. Retourne (obtenu, message)."""
    backups: dict[Path, bytes | None] = {}
    cibles = mutate(FIGS, backups)          # la mutation range elle-même ce qu'elle touche
    try:
        try:
            obtenu = _composer()
            return "compose", obtenu
        except Exception as exc:            # noqa: BLE001 : le chaos teste précisément les exceptions
            return "refus", f"{type(exc).__name__}: {exc}"
    finally:
        for chemin, contenu in backups.items():
            if contenu is None:
                if chemin.exists():
                    chemin.unlink()
            else:
                chemin.write_bytes(contenu)
        if DEPLACEMENT.exists():
            (FIGS / f"{VICTIME}.pdf").write_bytes(DEPLACEMENT.read_bytes())
            DEPLACEMENT.unlink()
        assert not cibles or all(c.exists() for c in cibles), "rétablissement incomplet"


def c1() -> dict:
    def muter(figs: Path, backups: dict) -> list[Path]:
        timbre = figs / f"{VICTIME}.pdf"
        backups[timbre] = timbre.read_bytes()
        shutil.move(str(timbre), str(DEPLACEMENT))
        return [figs / f"{VICTIME}.png"]
    etat, obtenu = _avec_fichiers(muter, "dégradation déclarée")
    if etat == "compose":
        via = [pl for pl in obtenu["placements"] if pl.get("via_png")]
        conforme = len(via) >= 1
        mesure = f"{len(via)} creux dégradé(s) en raster, aucun creux muet"
    else:
        conforme = False
        mesure = obtenu[:160]
    return dict(id="C1", titre="timbre vectoriel absent", attendu="dégradation L2 comptée",
                obtenu="composition avec via_png déclaré" if etat == "compose" else "refus inattendu",
                conforme=conforme, mesure=mesure)


def c2() -> dict:
    def muter(figs: Path, backups: dict) -> list[Path]:
        png = figs / f"{VICTIME}.png"
        backups[png] = png.read_bytes()
        backups[figs / f"{VICTIME}.pdf"] = (figs / f"{VICTIME}.pdf").read_bytes()
        (figs / f"{VICTIME}.pdf").unlink()
        png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 512 + b"chaos C2 : corps illisible")
        return [png]
    etat, obtenu = _avec_fichiers(muter, "refus")
    refuse = etat == "refus"
    return dict(id="C2", titre="PNG corrompu, timbre absent", attendu="refus avec exception",
                obtenu=obtenu if refuse else "composition sans mot dire",
                conforme=refuse and ("verif" in obtenu.lower() or "image" in obtenu.lower()
                                     or "error" in obtenu.lower()),
                mesure=obtenu[:180])


def c3() -> dict:
    def muter(figs: Path, backups: dict) -> list[Path]:
        import numpy as np
        from PIL import Image
        png = figs / f"{VICTIME}.png"
        backups[png] = png.read_bytes()
        backups[figs / f"{VICTIME}.pdf"] = (figs / f"{VICTIME}.pdf").read_bytes()
        (figs / f"{VICTIME}.pdf").unlink()
        bruit = np.random.default_rng(4).integers(0, 256, size=(4320, 7680, 3), dtype="uint8")
        Image.fromarray(bruit).save(png, format="PNG", compress_level=0)
        return [png]
    etat, obtenu = _avec_fichiers(muter, "refus motivé")
    refuse = etat == "refus"
    taille = (FIGS / f"{VICTIME}.png").stat().st_size if (FIGS / f"{VICTIME}.png").exists() else 0
    return dict(id="C3", titre="raster de substitution en 7680×4320",
                attendu="refus motivé (poids sans information)",
                obtenu=obtenu if refuse else f"composition acceptée pour {taille // 1_048_576} Mo",
                conforme=refuse and "C3" in obtenu, mesure=f"raster pesé {taille // 1024} Ko")


def c4() -> dict:
    dossier = Path("/tmp/chaos-figs")
    if dossier.exists():
        shutil.rmtree(dossier)          # un résidu d'une exécution interrompue ne doit pas tromper

    def muter(figs: Path, backups: dict) -> list[Path]:
        shutil.move(str(figs), str(dossier))
        figs.mkdir(parents=True, exist_ok=True)
        backups[figs / "__sentinelle__"] = None
        return [figs]

    etat, obtenu = _avec_fichiers(muter, "refus immédiat")
    FIGS.rmdir()                         # le répertoire vide recréé par la mutation
    shutil.move(str(dossier), str(FIGS))  # `shutil.move(dir, cible_existante)` imbrique : on cible le nom
    refuse = etat == "refus"
    return dict(id="C4", titre="répertoire rapport/figs vidé",
                attendu="refus immédiat nommant le répertoire",
                obtenu=obtenu if refuse else "composition sur un répertoire vide",
                conforme=refuse and "figs" in obtenu, mesure=obtenu[:160])


CAS = [c1, c2, c3, c4]


def lancer(*, silencieux: bool = False) -> dict:
    t0 = time.time()
    from rapport import mpl
    mpl.import_all()
    lignes = []
    for test in CAS:
        try:
            lignes.append(test())
        except Exception as exc:                            # noqa: BLE001 : un chaos qui casse le harnais
            lignes.append(dict(id=test.__name__.upper(), titre="harnais", attendu="—",
                               obtenu=f"exception du harnais : {type(exc).__name__}: {exc}",
                               conforme=False, mesure="le test lui-même est défaillant"))
    verts = sum(1 for x in lignes if x["conforme"])
    recu = dict(harnais="chaos.py", total=len(CAS), conformes=verts, lignes=lignes,
                secondes=round(time.time() - t0, 1),
                verdict="vert" if verts == len(CAS) else "rouge")
    (RACINE / "audit/chaos").mkdir(parents=True, exist_ok=True)
    (RACINE / "audit/chaos/resume.json").write_text(
        json.dumps(recu, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (RACINE / "audit/chaos/rapport.md").write_text(
        "# Chaos — quatre environnements dégradés\n\n"
        "| Cas | État fabriqué | Attendu | Obtenu | Conforme |\n|---|---|---|---|---|\n"
        + "\n".join(f"| {x['id']} | {x['titre']} | {x['attendu']} | {x['obtenu'][:110]} | "
                    f"{'oui' if x['conforme'] else 'NON'} |" for x in lignes)
        + "\n\nLe dépôt est rétabli après chaque cas ; l'assertion de rétablissement fait partie du "
          "test. Les compositions de ce fichier ne régénèrent pas les planches : sans quoi le chaos "
          "serait réparé avant d'être observé.\n", encoding="utf-8")
    if not silencieux:
        for x in lignes:
            print(f"{x['id']}  {'conforme' if x['conforme'] else 'DIVERGENT'}  {x['obtenu'][:90]}")
        print(f"chaos : {verts}/{len(CAS)} comportements conformes")
    return recu


if __name__ == "__main__":
    sys.exit(0 if lancer()["verdict"] == "vert" else 1)
