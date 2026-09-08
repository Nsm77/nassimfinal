# Confrontation des harnais `qa.py` et `qa2.py`

Verdict : **vert** sur 13 lois, 13 accords, 0 divergence(s), 0.0 s.

| loi | `qa.py` | `qa2.py` |
| --- | --- | --- |
| QA-1 | package.json + texte du PDF, voisinage | spans du PDF + triple de version exact |
| QA-10 | arborescence du kit, motif par motif | grep -rIn du dépôt, .env suivis par git |
| QA-11 | python-pptx, modèle d'objet | zip + regex sur le XML, nom de zone |
| QA-12 | nombresFR sur la source | regex sur les spans du rendu |
| QA-13 | voisinage de caractères dans la ligne | recouvrement d'ordonnées et blanc physique |
| QA-2 | grammaire de `facts.py` (ast) | grep et find dans le dépôt |
| QA-3 | liste des fichiers écrits par le kit | `stat` sur chaque chemin cité |
| QA-4 | regex sur le texte extrait | regex sur les spans non verbatim |
| QA-5 | fenêtre de ±26 caractères autour du mot | fonte du span porteur + ligne de prose déclarée + détection de langue |
| QA-6 | registre de composition | outline PyMuPDF |
| QA-7 | comptage à la composition | destinations d'annotations lues dans le fichier |
| QA-8 | ratios renvoyés par matplotlib | points lus par PyMuPDF contre pixels lus par PIL |
| QA-9 | tables de pictogrammes | plans de code de chaque span |

## Écarts trouvés à la première exécution, et la règle qui a dû être réécrite

1. **la fonte du corps n'est pas Helvetica** — rencontre : qa2 exemptait le verbatim en cherchant « mono » dans une police censée être Times/Helvetica : 0 span de prose trouvé, donc 0 faute déclarée par silence. Règle retenue : le moteur enregistre DejaVu pour le rapport entier ; la discrimination se fait sur « Mono » dans le nom de fonte, et le nombre de spans tenus à part est imprimé

2. **le seau par ordonnée recolle deux cellules** — rencontre : en regroupant les spans par `y` arrondi, la deuxième ligne d'une cellule se retrouvait dans la première de la voisine : sept mots coupés, dix-huit emprunts anglais imaginaires. Règle retenue : une ligne visuelle = un bloc et une ordonnée de ligne, tels que le moteur de texte les donne ; plus de reconstruction à la main

3. **une ligne justifiée écarte les mots de onze points** — rencontre : le critère « écart horizontal > un espace » pour couper une ligne rendait huit « lignes » commençant par « : », donc huit fautes d'insécable introuvables à l'œil. Règle retenue : le blanc ne tranche plus la ligne ; la fonte tranche la nature du texte (verbatim), et la marque d'identifiant est cherchée à ±2 caractères

4. **la région anglaise ne se déduit pas d'un titre** — rencontre : qa.py bornait l'abstract entre deux titres « Abstract » ; le mot reparaît en titre courant et la région se refermait sur rien — la ligne fautive restait dans le champ. Règle retenue : qa2 juge la **langue de la ligne** par ses mots outils, et consigne le nombre de lignes anglaises tenues hors du champ (huit au dernier rendu)

## Verdicts loi par loi

| loi | qa | qa2 | confrontation |
| --- | --- | --- | --- |
| QA-1 | vert | vert | vert |
| QA-10 | vert | vert | vert |
| QA-11 | vert | vert | vert |
| QA-12 | vert | vert | vert |
| QA-13 | vert | vert | vert |
| QA-2 | vert | vert | vert |
| QA-3 | vert | vert | vert |
| QA-4 | vert | vert | vert |
| QA-5 | vert | vert | vert |
| QA-6 | vert | vert | vert |
| QA-7 | vert | vert | vert |
| QA-8 | vert | vert | vert |
| QA-9 | vert | vert | vert |
