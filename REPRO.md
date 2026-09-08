# Reproduction exacte, depuis un clone vierge

Ce document est la recette. Si un pas diverge, l'ouvrage n'est pas recevable : le kit est conçu pour
échouer bruyamment plutôt que de rendre un PDF approximatif.

## 1. Environnement mesuré (celui qui a produit le dépôt)

| outil | version retenue | rôle |
| --- | --- | --- |
| Python | 3.11 | moteur du kit |
| matplotlib | 3.11.1 | soixante et une planches vectorielles |
| reportlab | 5.0.1 | composition du PDF, signets, liens, métadonnées |
| pypdf | 6.18.0 | placage des timbres, lecture des destinations |
| PyMuPDF | 1.28.2 | second harnais : spans, géométrie, outline |
| python-pptx | 1.0.2 | compositeur du diaporama |
| Pillow | 10.x | vérification des rasters de secours (chaos C2) |
| numpy, fonttools, segno | courants | calculs, polices, QR |
| polices | DejaVu (système) | le moteur et le kit doivent partager la même fonte |
| Node / npm | non requis pour le kit | requis pour l'application : `npm ci` puis `npm run dev` |

## 2. Trois commandes, dans cet ordre

```bash
python3 rapport/build.py
python3 soutenance/slides.py
python3 rapport/qa.py
```

Attentes : 113 pages (bande admise 102 à 168), 61 planches dessinées et 61 posées, `via_png` à zéro,
229 liens internes résolus et zéro mort, 233 ancres et 233 signets, quatre mille deux cents lignes
reconstituées sans faute de ponctuation, procès-verbal `qa` en treize lois, code de sortie 0.

## 3. Chaîne de preuve complète

```bash
python3 rapport/qa2.py && python3 rapport/ab.py
python3 rapport/mutation.py && python3 rapport/chaos.py
python3 rapport/assauts.py && python3 rapport/jury.py
python3 rapport/build.py --determinisme
python3 rapport/gates.py
```

Attentes : treize lois en accord entre les deux harnais ; trois mutations attrapées sur trois ; quatre
chaos conformes ; trente assauts tenus ; quinze cartes de jury à preuve vérifiée ; deux rebuilds à la
même empreinte sha256 ; vingt-sept portes vertes, note G6 à quatre-vingt-dix-sept sur cent au minimum.

## 4. Sceller

```bash
python3 rapport/gates.py --sceller    # écrit audit/sceau.json, pose l'étiquette v1.0-final
git add -A && git commit -m "Gel v1.0-final : kit scellé"
git push origin HEAD --follow-tags
```

## 5. Ce qui peut légitimement manquer

`node_modules` n'est pas livré. Sans `npm ci`, `tsc --noEmit`, `next build` et les tests d'application
sont indisponibles : le kit le consigne en **dégradation L1** (`V.6` du rapport, `audit/B0-boot.md`)
au lieu de le taire. Tous les autres contrôles tournent sur les seuls fichiers suivis par git.

Les inconnues du monde réel — dates de soutenance, chiffres d'exploitation, captures d'avant-projet —
restent entre **[crochets]** ou attendent un fichier dans `public/avants/`. Aucune n'est comblée par
une invention : c'est la différence entre un rapport et une maquette.

## 6. Emprunter le kit pour un autre stage

Copier `rapport/` et `soutenance/`, puis : `rapport/facts.py` (vos gisements), `rapport/trace.py`
(votre backlog), `rapport/figs*.py` (vos figures), `rapport/content_a.py` à `content_f.py` (votre
prose), `soutenance/slides.py` (votre minutage). Les lois de langue, les deux harnais, les portes et
les provocations se gardent telles quelles : c'est ce qu'ils vérifient qui change, pas la façon de
vérifier.
