# Chaos — quatre environnements dégradés

| Cas | État fabriqué | Attendu | Obtenu | Conforme |
|---|---|---|---|---|
| C1 | timbre vectoriel absent | dégradation L2 comptée | composition avec via_png déclaré | oui |
| C2 | PNG corrompu, timbre absent | refus avec exception | UnidentifiedImageError: cannot identify image file '/home/user/nassimfinal/rapport/figs/fig27.png' | oui |
| C3 | raster de substitution en 7680×4320 | refus motivé (poids sans information) | RuntimeError: chaos C3 : fig27 ne fournit qu'un raster de 94 Mo. Une capture 8K ne remplace pas un vecteur : e | oui |
| C4 | répertoire rapport/figs vidé | refus immédiat nommant le répertoire | FileNotFoundError: plaque fig01 : ni timbre vectoriel ni PNG dans /home/user/nassimfinal/rapport/figs — constr | oui |

Le dépôt est rétabli après chaque cas ; l'assertion de rétablissement fait partie du test. Les compositions de ce fichier ne régénèrent pas les planches : sans quoi le chaos serait réparé avant d'être observé.
