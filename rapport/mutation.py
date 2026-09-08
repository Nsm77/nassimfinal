"""rapport/mutation.py — preuve P3 du §5 : trois fautes injectées, trois fois le refus.

Le principe est celui du test de mutation en génie logiciel : un harnais qui ne rougit jamais ne
mesure rien. Ici, on **casse** volontairement le dépôt de façon réversible, on relance la
composition sur une sortie de brouillon, et on exige (1) un code retour non nul et (2) le message
d'erreur attendu. Si une injection passe, la loi correspondante est décorative et le kit est rouge.

Aucun fichier n'est laissé modifié : chaque mutation est appliquée en mémoire, écrite, puis restaurée
dans un bloc `finally` — y compris sur exception. Le procès-verbal est `audit/mutation/resume.json`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
AUDIT = RACINE / "audit"
BROUILLON = Path("/tmp/mutation-brouillon.pdf")

MUTATIONS = [
    dict(
        id="M1",
        titre="une planche rendue et jamais citée",
        loi="INV-13 — toute plaque est citée exactement une fois",
        fichier="rapport/content_c.py",
        old='    F.figure("fig27")',
        new='    # F.figure("fig27")   # mutation M1 : la citation est retirée',
        attendu="jamais citée",
        explicable="la figure n'est plus appelée : le registre la refuse au lieu de l'imprimer en "
                   "faveur d'un oubli",
    ),
    dict(
        id="M2",
        titre="une espace insécable ôtée avant un point-virgule",
        loi="loi INSÉCABLES du §4, vérifiée sur le rendu",
        fichier="rapport/content_b.py",
        old='"vérifie huit de ces douze critères sans intervention humaine.")',
        new='"vérifie huit de ces douze critères; sans intervention humaine.")',
        attendu="insécable",
        explicable="la césure redevient possible devant la ponctuation haute : le moteur refuse la "
                   "page plutôt que de l'imprimer",
    ),
    dict(
        id="M3",
        titre="un extrait de code dont la ligne citée dépasse la fin du fichier",
        loi="INV-5 — toute citation `fichier:ligne` pointe une ligne qui existe",
        fichier="rapport/content_c.py",
        old='    F.code("src/db/schema.ts", 151, 26,',
        new='    F.code("src/db/schema.ts", 9000, 26,',
        attendu="hors bornes",
        explicable="le 151 devient 9000 : schema.ts n'a pas 9000 lignes, et une référence fausse est "
                   "une contrefaçon de preuve, même quand elle est invisible à l'œil",
    ),
]


def _ecrire(chemin: Path, contenu: str) -> None:
    chemin.write_text(contenu, encoding="utf-8")


def _lancer(args: list[str]) -> tuple[int, str]:
    p = subprocess.run([sys.executable, *args], cwd=str(RACINE), capture_output=True, text=True,
                       timeout=900)
    return p.returncode, (p.stdout + p.stderr)


def injecter(m: dict, *, complet: bool = False) -> dict:
    """Applique la mutation, compose, vérifie le refus, restaure. Retourne la ligne de procès-verbal."""
    chemin = RACINE / m["fichier"]
    original = chemin.read_text(encoding="utf-8")
    if m["old"] not in original:
        return dict(id=m["id"], statut="inapplicable",
                    detail=f"ancre introuvable dans {m['fichier']} — la mutation doit être réécrite "
                           "quand le texte cible change")
    _ecrire(chemin, original.replace(m["old"], m["new"], 1))
    try:
        cmd = ["rapport/build.py"] + ([] if complet else ["--dry-run"])
        if complet:
            cmd += ["--sortie", str(BROUILLON)]
        code, sortie = _lancer(cmd)
    except subprocess.TimeoutExpired:
        code, sortie = -1, "timeout de 900 s : la composition ne meurt pas, elle s'accroche"
    finally:
        _ecrire(chemin, original)
        assert chemin.read_text(encoding="utf-8") == original, f"restauration ratée : {chemin}"
    vu = m["attendu"].lower() in sortie.lower()
    return dict(id=m["id"], titre=m["titre"], loi=m["loi"], refus=code != 0, message_trouvé=vu,
                extrait=" ".join(sortie.strip().splitlines()[-1:])[:220] if sortie.strip() else "",
                explication=m["explicable"], detecte=bool(code != 0 and vu))


def lancer(*, silencieux: bool = False) -> dict:
    t0 = time.time()
    lignes = [injecter(m) for m in MUTATIONS]
    detectes = sum(1 for x in lignes if x.get("detecte"))
    recu = dict(harnais="mutation.py", total=len(lignes), detectes=detectes, lignes=lignes,
                secondes=round(time.time() - t0, 1),
                verdict="vert" if detectes == len(MUTATIONS) else "rouge")
    (AUDIT / "mutation").mkdir(parents=True, exist_ok=True)
    (AUDIT / "mutation/resume.json").write_text(
        json.dumps(recu, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (AUDIT / "mutation/rapport.md").write_text(
        "# Mutation — trois fautes injectées\n\n"
        "| Identifiant | Faute injectée | Loi visée | Build refusé | Message attendu lu |\n"
        "|---|---|---|---|---|\n"
        + "\n".join(f"| {x['id']} | {x.get('titre', '—')} | {x.get('loi', '—')} | "
                    f"{'oui' if x.get('refus') else 'NON'} | {'oui' if x.get('message_trouvé') else 'NON'} |"
                    for x in lignes)
        + "\n\nChaque cellule « NON » est une loi décorative. Le dépôt est restauré ligne à ligne "
          "après chaque essai, et l'assertion de restauration fait partie du test.\n", encoding="utf-8")
    if not silencieux:
        for x in lignes:
            print(f"{x['id']}  {'détectée' if x.get('detecte') else 'NON DÉTECTÉE'}  "
                  f"{x.get('titre') or x.get('statut', 'sans intitulé')}")
        print(f"mutation : {detectes}/{len(MUTATIONS)} fautes injectées refusées par le moteur")
    BROUILLON.unlink(missing_ok=True)
    return recu


if __name__ == "__main__":
    sys.exit(0 if lancer()["verdict"] == "vert" else 1)
