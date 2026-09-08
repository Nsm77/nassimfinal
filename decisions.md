# Journal des décisions

Une décision par entrée : le problème, ce qui a été choisi, ce que ça coûte. Les renvois `fichier:ligne`
sont vérifiés par le kit (`rapport/qa.py`, lois QA-1 et QA-3). Les décisions non prises — celles qui
appartiennent à l'exploitant ou au jury — portent un [crochet].

## D1. Le kit est écrit en Python, pas en TypeScript
- **Problème.** Un mémoire sur une application Next.js peut se relancer depuis l'application elle-même.
- **Décision.** Non : le rapport est engendré par des scripts Python lisibles par un correcteur sans
  outillage de build. `rapport/facts.py` lit le dépôt (TypeScript) comme une base de faits.
- **Coût.** Deux piles à maintenir, et un extracteur à écrire pour chaque famille de chiffres.

## D2. Un seul extracteur de faits, aucune saisie à la main
- **Problème.** Un nombre recopié vieillit mal et ne se prouve pas.
- **Décision.** Tout nombre passe par `rapport/facts.py` → `audit/facts.json`, et le rendu est contrôlé
  contre le fichier source (`qa.py` QA-1, QA-2 ; `qa2.py` recompte par `grep` et `find`).
- **Coût.** Un build de plus à chaque changement de périmètre ; desregex à réécrire quand le code bouge.

## D3. Zéro contrainte CHECK revendiquée là où le schéma n'en a pas
- **Problème.** Le premier jet affirmait que « la contrainte tient le stock » : le dépôt ne déclare
  aucune contrainte `check`.
- **Décision.** Le rapport dit zéro et montre la garde réelle : verrou `FOR UPDATE` et test en code,
  `src/lib/orders.ts:100-101`. La figure est corrigée à l'extracteur, pas adoucie à la légende.
- **Coût.** Une section de limites plus longue, une question de jury en plus (Q2 de la banque).

## D4. Les planches sont des objets vectoriels posés, pas des captures
- **Problème.** Une capture 8K fait joli et ne prouve rien ; elle pèse, elle pixellise à l'impression.
- **Décision.** Chaque planche est dessinée en code, sauvée en `.pdf` **et** en `.png` aux mêmes ratios ;
  `pypdf.merge_transformed_page` la pose aux dimensions voulues. Le PNG ne sert que de secours, et
  seulement si la planche n'est citée nulle part — sinon exception (`rapport/build.py:placer()`).
- **Coût.** Soixante et une fonctions de dessin, un registre de citations à tenir (INV-13).

## D5. Deux harnais, pas un seul qui se donne raison
- **Problème.** Un contrôle écrit par le même auteur que le moteur a ses angles morts.
- **Décision.** `qa.py` lit la source et le texte ; `qa2.py` lit la géométrie des spans, les polices,
  et recompte dans le dépôt par outils du shell. `ab.py` confronte les deux verdicts loi par loi et
  refuse l'ouvrage sur divergence. Les quatre écarts trouvés sont écrits dans `audit/ab/harnais.md`.
- **Coût.** Dix-sept secondes de contrôle, quatre règles de méthode à réécrire une par une.

## D6. La loi de langue est exécutée, pas corrigée à la main
- **Problème.** Slop, emprunts anglais, ponctuation collée : cent treize pages ne se relisent pas deux fois.
- **Décision.** Cinq lois dans `rapport/doc.py` (SLOP, SYNONYMES, CODE_INLINE, INSÉCABLE,
  PONCTUATION_COLLÉE), appliquées au rendu (`verifier_rendu`, `verifier_langue`). Le verbatim est
  exempté **par la fonte**, la région anglaise par sa langue, et chaque exemption est comptée au
  procès-verbal.
- **Coût.** Trois cent cinquante lignes de code de contrôle, et l'obligation de réécrire une phrase au
  lieu de la défendre.

## D7. Les inconnues restent entre crochets
- **Problème.** Un mémoire de stage fourmille de chiffres que l'exploitant seul détient.
- **Décision.** `[crochets]` obligatoires, marque `AVANT` pour l'image manquante, et aucun gabarit
  muet : le QR de quatrième de couverture refuse de se dessiner sans URL.
- **Coût.** Le document est moins « fini » qu'un document qui ment. C'est le but.

## D8. L'application n'est pas modifiée pour le kit
- **Problème.** Un rapport qui a besoin d'une route d'export pour ses figures contamine le livrable.
- **Décision.** Aucune fonctionnalité nouvelle. Le kit lit les fichiers ; `node_modules` absent ne
  bloque que le type-check, consigné comme dégradation L1.
- **Coût.** Le kit doit savoir lire du TypeScript sans compiler — d'où `facts.py`.

## D9. Le scellement est un ordre, pas une intention
- **Problème.** Sceller avant d'avoir écrit le bloc de fin produit un sceau faux.
- **Décision.** Gel du contenu → calcul des empreintes → `audit/sceau.json` → commit unique →
  étiquette `v1.0-final`. L'empreinte scellée est celle du PDF final, pas celle du commit.
- **Coût.** Une porte (G27) qui refuse de sceller tant qu'une porte est rouge — cf. `rapport/gates.py`.

## D10. Réduire le mouvement : mesurer, pas promettre
- **Problème.** Le site déclare une préférence système que le code n'exploite qu'à moitié.
- **Décision.** Le rapport imprime la mesure : une règle dans `src/app/globals.css:161`, zéro occurrence
  de `useReducedMotion`. La limite est écrite en `V.6` au lieu d'être couverte par une figure.
- **Coût.** Une figure de moins en apparence « réussie ».

## D11. Le téléphone des boutiques ne sort pas du dépôt
- **Problème.** Le seed contient un numéro réel ; le lire en soutenance n'est pas un problème,
  l'imprimer sur cent treize pages en est un.
- **Décision.** Le champ n'est pas reproduit dans le PDF, et la légende le dit.
- **Coût.** Un lecteur curieux demandera pourquoi : la réponse tient en une ligne.
