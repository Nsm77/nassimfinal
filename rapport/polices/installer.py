"""rapport/polices/installer.py — pose les fontes d'identité du kit (Newsreader, Manrope).

Sur une machine qui a le réseau :

    python3 rapport/polices/installer.py          # télécharge, instancie, vérifie
    CLEOPATRE_FONDS=strict python3 rapport/build.py

Ce que fait le script : il télécharge les fontes variables depuis le dépôt officiel `google/fonts`
(puisées par leurs empreintes), puis il **instancie** chaque coupe statique dont le composeur a besoin
(ReportLab n'embarque pas les fontes variables), et il écrit la licence OFL à côté des TTF. Rien d'autre :
le kit ne fabrique pas de typographie, il la va chercher chez son auteur, à l'adresse de son auteur.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl"

VARIABLES = {
    "Newsreader-VF.ttf": f"{BASE}/newsreader/Newsreader%5Bopsz%2Cwght%5D.ttf",
    "Newsreader-Italic-VF.ttf": f"{BASE}/newsreader/Newsreader-Italic%5Bopsz%2Cwght%5D.ttf",
    "Manrope-VF.ttf": f"{BASE}/manrope/Manrope%5Bwght%5D.ttf",
}
LICENCES = {
    "OFL-Newsreader.txt": f"{BASE}/newsreader/OFL.txt",
    "OFL-Manrope.txt": f"{BASE}/manrope/OFL.txt",
}
# coupe statique -> (source variable, axes figés) : opsz 16 pour le texte courant, 32 pour le display
STATIQUES = {
    "Newsreader-Regular": ("Newsreader-VF.ttf", "opsz=16 wght=400"),
    "Newsreader-SemiBold": ("Newsreader-VF.ttf", "opsz=16 wght=600"),
    "Newsreader-Bold": ("Newsreader-VF.ttf", "opsz=16 wght=700"),
    "Newsreader-Italic": ("Newsreader-Italic-VF.ttf", "opsz=16 wght=400"),
    "Manrope-Regular": ("Manrope-VF.ttf", "wght=400"),
    "Manrope-Medium": ("Manrope-VF.ttf", "wght=500"),
    "Manrope-SemiBold": ("Manrope-VF.ttf", "wght=600"),
    "Manrope-Bold": ("Manrope-VF.ttf", "wght=700"),
}


def _telecharger(url: str, cible: Path) -> None:
    with urllib.request.urlopen(url, timeout=60) as r:
        cible.write_bytes(r.read())
    print(f"  reçu {cible.name} · {len(cible.read_bytes()) // 1024} Ko · sha256 "
          f"{hashlib.sha256(cible.read_bytes()).hexdigest()[:12]}")


def main() -> int:
    try:
        from fontTools import ttLib  # noqa: F401
    except ModuleNotFoundError:
        print("fonttools est requis : pip install fonttools", file=sys.stderr)
        return 1
    for nom, url in {**VARIABLES, **LICENCES}.items():
        cible = ICI / nom
        if not cible.exists():
            print(f"téléchargement de {nom} …")
            _telecharger(url, cible)
    for coupe, (source, axes) in STATIQUES.items():
        sortie = ICI / f"{coupe}.ttf"
        if sortie.exists():
            continue
        subprocess.run([sys.executable, "-m", "fontTools.varLib.instancer",
                        str(ICI / source), *axes.split(), "-o", str(sortie)],
                       check=True, capture_output=True)
        print(f"  instancié {sortie.name}")
    attendues = sorted(STATIQUES)
    reste = [c for c in attendues if not (ICI / f"{c}.ttf").exists()]
    if reste:
        print("manquant : " + ", ".join(reste), file=sys.stderr)
        return 1
    print("fontes d'identité en place — relancer `python3 rapport/build.py`, "
          "puis `CLEOPATRE_FONDS=strict python3 rapport/gates.py` pour interdire la substitution")
    return 0


if __name__ == "__main__":
    sys.exit(main())
