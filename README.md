# Kit de stage — Cleopâtre, parapharmacie en ligne

Ce dépôt contient l'application (Next.js) **et** le kit de restitution : un rapport de stage de cent
treize pages engendré par le code, un diaporama de trente glissades avec Morph réel, deux harnais de
contrôle, un jeu d'assauts, et le dossier `audit/` qui prouve chaque chiffre.

Le kit n'ajoute aucune fonctionnalité à l'application. Il lit le dépôt, dessine, compose, vérifie.
Un chiffre qui n'existe pas dans le code n'existe pas dans le rapport : c'est la loi du projet, et
elle est exécutée par les contrôles, pas décrétée par une préface.

## Objet et prérequis

| ce que c'est | ce qu'il faut pour le refaire |
| --- | --- |
| `rapport/` : moteur Python (ReportLab, matplotlib, pypdf) | Python 3.11, `matplotlib`, `reportlab`, `pypdf`, `PyMuPDF`, `Pillow`, `numpy`, `fonttools`, `segno` |
| `soutenance/` : `slides.py` → un `.pptx` de 16:9 | `python-pptx` |
| figures : 61 planches vectorielles + PNG de secours | polices **DejaVu** (celles du moteur de rendu) |
| `audit/` : procès-verbaux, registres, empreintes | aucune connexion réseau : tout est lu dans le dépôt |

L'application elle-même demande Node 22 et `npm ci` avant `npm run dev`. Le kit de restitution, lui,
ne dépend pas de `node_modules` : il lit les fichiers sources. C'est écrit parce que c'est vrai, et
parce que sans le `npm ci`, le type-check est indisponible (dégradation L1 consignée en `V.6`).

## Reconstruire — trois commandes

```bash
python3 rapport/build.py                 # 61 planches, composition, PDF vectoriel, 30 à 40 s
python3 soutenance/slides.py             # le paquet .pptx, ses cinq morph, ses zooms
python3 rapport/qa.py                    # treize lois, un procès-verbal, code de sortie 1 si rouge
```

Puis, pour la chaîne complète de preuve (une à deux minutes) :

```bash
python3 rapport/qa2.py                   # second harnais : PyMuPDF, géométrie, outils du shell
python3 rapport/ab.py                    # confrontation des deux harnais — divergences = refus
python3 rapport/mutation.py              # trois fautes injectées, trois rejets exigés
python3 rapport/chaos.py                 # quatre provocations : figure absente, PNG corrompu, 8K, figs/ vidé
python3 rapport/assauts.py               # trente assauts en six rounds
python3 rapport/jury.py                  # banque de quinze questions, preuves vérifiées
python3 rapport/gates.py                 # vingt-sept portes, note G6 sur cent
```

## Personnaliser — ce qui est à vous

Les inconnues du monde réel sont entre **[crochets]** : elles ne sont jamais comblées par une
invention. Les trois endroits à traiter avant toute impression :

1. `[crochets]` dans `rapport/content_*.py` — noms du jury, dates de soutenance, chiffres
   d'exploitation à confirmer avec l'exploitant. Cherchez : `grep -rn "\[.*\]" rapport/content_*.py`.
2. `AVANT` / `APRÈS` : le dépôt ne fournit pas les captures d'avant-projet. Le marquage est en place,
   il attend vos images (`public/avants/`, un fichier par glissade concernée).
3. Le **QR** de quatrième de couverture : `rapport/figs6.py` fabrique le code à partir d'un URL à
   saisir ; sans URL, la planche refuse de se dessiner et le build le dit, au lieu de poser un
   gabarit vide.

```bash
python3 rapport/build.py --sortie /tmp/mon-rapport.pdf --dpi 220
python3 rapport/build.py --dry-run        # gabarit complet, aucune planche régénérée
python3 rapport/build.py --determinisme   # deux builds, comparaison d'empreinte
```

## Arborescence

```
rapport/
  build.py          ordonnance : modules de contenu, passes, placement, signets, métadonnées
  doc.py            styles, palette, lois de langue, gardes de Creux (chaos C2 et C3)
  contenu.py        Fab : section, paragraphe, tableau, figure, code, encadré
  content_a..f.py   la prose, les six annexes, les inventaires engendrés
  facts.py          extracteur unique des chiffres : source → audit/facts.json
  trace.py          les vingt-quatre récits du backlog, avec fichiers et symboles
  figs1..6.py       soixante et une planches écrites en code ; figref.py les référence
  mpl.py            helpers de figure, registres, garde anti-pictogramme
  invariants.py     vingt-cinq invariants, vingt-sept portes, dix lignes SI/ALORS, autocontrôle
  qa.py  qa2.py     deux harnais ; ab.py les confronte
  mutation.py      injecte trois fautes, exige trois rejets
  chaos.py         provoque quatre pannes, exige quatre comportements
  assauts.py  jury.py  gates.py
  PDF/Cleopatre-rapport.pdf   figs/ (61 PDF + 61 PNG)
soutenance/
  slides.py  Cleopatre-soutenance.pptx  zooms/  JOURJ.md  BANQUE-JURY.md
audit/
  dernier-build.json  facts.json  langue.json  langue-rendu.json  liens.json  signets.json
  qa.json  qa2.json  ab/  rounds/  mutation/  chaos/  kit/  gates.json  gates.md  sceau.json
```

## Dépannage

### Le build refuse une figure : « ne fournit qu'un raster de … Mo »
Vous avez déposé une capture d'écran à la place d'une planche. Le moteur la refuse au-delà d'un
budget de huit mégaoctets (garde de `rapport/doc.py`, provocée par `chaos.py`, cas C3). Redessinez la
planche en code, ou réduisez la capture à la taille d'impression.

### « ni timbre vectoriel ni PNG dans rapport/figs »
`rapport/figs/` est vide ou incomplet. Relancez `python3 rapport/build.py --dry-run` puis sans
`--dry-run` : le secours raster n'est accepté **que** pour une figure que le rapport ne cite pas.

### Une légende ou un titre casse à l'impression avec un petit carré
Un pictogramme s'est glissé dans un texte. `_assert_glyphs` de `rapport/mpl.py` le chasse au tracé :
le message nomme la planche et le caractère. Le kit interdit emoji et symboles dans les figures.

### « ponctuation collée » ou « insécable manquante » au contrôle de langue
La loi est typographique : pas d'espace avant une virgule, une insécable avant un point-virgule. La
faute est dans la phrase, pas dans le moteur — corrigez le texte de `content_*.py`. Si vous citez du
code, entourez l'identifiant de backticks : le verbatim est exempté, et le nombre de lignes exemptées
est imprimé au procès-verbal.

### `qa.py` sort en rouge sur « chemins cités introuvables »
Le rapport cite un fichier que le dépôt ne contient pas encore (ou plus). Deux issues, jamais la
troisième : écrire le fichier, ou réécrire la phrase. Les adoucir le contrôle est proscrit par
`decisions.md`.

### `npm ci` échoue, `tsc --noEmit` est indisponible
Le dépôt livré ne contient pas `node_modules`. Le kit s'exécute quand même (il lit les sources) ; la
limite est consignée comme dégradation L1 en `V.6` et dans `REPRO.md`, avec la commande à relancer
quand le réseau redevient disponible.

### Le PDF change d'octets entre deux builds
Comparez avec `python3 rapport/build.py --determinisme`. Un horodatage figé (`D:20260101000000+00'00'`)
est posé exprès ; si l'empreinte diverge malgré tout, la cause est une figure non déterministe
(tri, dictionnaire, aléa) : `audit/dernier-build.json` garde l'empreinte du dernier build pour
l'écart.

## Ce que le kit ne fait pas

Pas de vidéo, pas de CMYK, pas de rendu arabe, pas de données réelles d'exploitation, pas de fonds.
Ces absences sont des choix écrits dans `audit/B0-boot.md`, pas des oublis.
