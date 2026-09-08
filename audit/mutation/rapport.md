# Mutation — trois fautes injectées

| Identifiant | Faute injectée | Loi visée | Build refusé | Message attendu lu |
|---|---|---|---|---|
| M1 | une planche rendue et jamais citée | INV-13 — toute plaque est citée exactement une fois | oui | oui |
| M2 | une espace insécable ôtée avant un point-virgule | loi INSÉCABLES du §4, vérifiée sur le rendu | oui | oui |
| M3 | un extrait de code dont la ligne citée dépasse la fin du fichier | INV-5 — toute citation `fichier:ligne` pointe une ligne qui existe | oui | oui |

Chaque cellule « NON » est une loi décorative. Le dépôt est restauré ligne à ligne après chaque essai, et l'assertion de restauration fait partie du test.
