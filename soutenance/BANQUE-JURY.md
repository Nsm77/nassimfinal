# Banque du jury — quinze questions, chaque réponse avec sa preuve

Écrite par `python3 rapport/jury.py`. Une preuve non vérifiée fait sortir le script en rouge :
il n'existe pas de carte de complaisance.

## Q1 · chiffres — D'où sortent vos 81 références, 16 marques, 7 univers ?

**Réponse.** Du gisement : le manifeste d'images et les graines de la base. `rapport/facts.py` les compte dans le dépôt, le rapport imprime le compte, et le recomptage par `grep` dans le second harnais tombe sur le même nombre. Rien n'est saisi à la main.

**Relance probable.** Et si je change une ligne du seed, que devient le mémoire ?

**Piège.** Répondre « environ 80 » : le nombre est une clé d'audit, il se vérifie en une seconde.

**Renvoi dans le mémoire.** I.2, annexe C

**Preuve.** audit produits
**Contrôle.** ✓ preuves vérifiées

## Q2 · base — Le schéma ne déclare aucune contrainte CHECK : comment le stock ne devient-il jamais négatif ?

**Réponse.** Par le verrou et le test, pas par la déclaration : la commande s'exécute sous `FOR UPDATE`, la garde est écrite dans `src/lib/orders.ts`, et le rapport dit zéro contrainte au lieu d'en inventer une. C'est consigné comme dette assumée à la section IV.2, avec la raison.

**Relance probable.** Un UPDATE concurrent entre deux transactions, alors ?

**Piège.** Affirmer une contrainte au schéma : le fichier répondrait devant le jury.

**Renvoi dans le mémoire.** IV.2, figure 49

**Preuve.** ligne src/lib/orders.ts  100
**Contrôle.** ✓ preuves vérifiées

## Q3 · base — Combien de tables, et pourquoi ce nombre ?

**Réponse.** Vingt-quatre tables, deux cent deux colonnes, dix enums, cinquante index, dix-neuf clés étrangères. Le nombre vient du périmètre retenu : deux boutiques, un catalogue multi-axes, un tunnel, la fidélité, les retours. Les dictionnaires complets sont en annexe B, générés depuis le schéma.

**Relance probable.** Que avez-vous refusé de modéliser ?

**Piège.** Défendre le nombre sans montrer le dictionnaire : l'annexe B est générée, elle est donc exacte ou le build est rouge.

**Renvoi dans le mémoire.** annexe B

**Preuve.** audit tables
**Contrôle.** ✓ preuves vérifiées

## Q4 · argent — Pourquoi ne pas avoir branché de paiement en ligne ?

**Réponse.** Parce qu'aucune passerelle n'a été contractée pour le stage, et que l'argent ne s'improvise pas : le projet paie à la livraison et le périmètre le dit. La solution de repli nommée par le cahier, une boutique Shopify, n'existe pas dans le dépôt — la recherche dans `src/` renvoie zéro ligne, et le rapport l'écrit au lieu de feindre un connecteur.

**Relance probable.** Le jour où la passerelle existe, combien de temps pour la brancher ?

**Piège.** Répondre « c'était hors périmètre » sans dire ce qui est prêt : le tunnel, l'idempotence et le verrou de stock le sont, la devise non.

**Renvoi dans le mémoire.** I.4, II.5, conclusion

**Preuve.** motif src/actions/checkout.ts idempot
**Contrôle.** ✓ preuves vérifiées

## Q5 · promotions — Huit motifs de refus pour une promotion, c'est beaucoup. Lesquels comptent vraiment ?

**Réponse.** Les huit sont écrits dans le code et listés dans le rapport ; ceux qui tiennent la route sont la date de fenêtre, le cumul interdit, le minimum de panier et l'éligibilité de catégorie. Les autres protègent des cas rares mais coûteux, comme la marque exclue ou le produit déjà en rupture.

**Relance probable.** Un code valable pour deux clients, l'un éligible et l'autre non : lequel gagne ?

**Piège.** Dire « le moteur refuse poliment » : la réponse est dans l'extrait de code, pas dans l'intention.

**Renvoi dans le mémoire.** III.4

**Preuve.** audit promotions
**Contrôle.** ✓ preuves vérifiées

## Q6 · sécurité — Pourquoi scrypt et non bcrypt ou Argon2 ?

**Réponse.** Parce que la bibliothèque standard du serveur l'offre sans dépendance, avec une clé de 64 octets et une comparaison à temps constant. Le choix est tracé dans le code et commenté dans le rapport, y compris ce qu'il coûte : pas de remontée de coût automatique à la reconnexion.

**Relance probable.** Et le vol de cookie ?

**Piège.** Répondre sécurité par le vocabulaire : montrer `timingSafeEqual`, le sel, les attributs du cookie.

**Renvoi dans le mémoire.** II.4

**Preuve.** motif src/lib/auth.ts timingSafeEqual
**Contrôle.** ✓ preuves vérifiées

## Q7 · sécurité — Votre limite de requêtes est en mémoire : que se passe-t-il au deuxième serveur ?

**Réponse.** Rien de bon : le compteur est par processus, donc deux instances doublent le budget réel. C'est écrit dans le rapport comme limite assumée à trois utilisateurs simultanés, avec la sortie (compteur partagé) nommée mais non fabriquée. Le plafond mémoire de cinq mille entrées empêche l'épuisement, pas la fraude.

**Relance probable.** Pourquoi ne pas avoir posé Redis dans le stage ?

**Piège.** Cacher la limite : la loi du kit est de l'écrire, et elle y est.

**Renvoi dans le mémoire.** V.6

**Preuve.** motif src/lib/rate-limit.ts 5000
**Contrôle.** ✓ preuves vérifiées

## Q8 · sécurité — Que contient votre cookie de session, et combien de temps vit-il ?

**Réponse.** Un identifiant opaque de 256 bits, pas d'informations personnelles ; trente jours ; `httpOnly`, `sameSite=lax`, `secure` en production. La session est révoquée côté base, donc la déconnexion est réelle.

**Relance probable.** Et le jeton CSRF sur les formulaires ?

**Piège.** Confondre `sameSite` et protection CSRF : le rapport dit ce que le dépôt fait, c'est-à-dire la posture lax et le contrôle d'origine à l'écriture.

**Renvoi dans le mémoire.** II.4

**Preuve.** motif src/lib/auth.ts cleo_session
**Contrôle.** ✓ preuves vérifiées

## Q9 · architecture — Où est la source de vérité de la visibilité d'un produit ?

**Réponse.** Dans une seule fonction : `src/lib/catalog.ts`, ligne quatorze pour le filtre. Les pages, l'administration et l'API appellent cette fonction ; elles ne recopient pas la condition. C'est la preuve que le catalogue ne peut pas se contredire d'un écran à l'autre.

**Relance probable.** Prouvez-moi qu'aucune page ne refait le filtre.

**Piège.** Répondre par l'intention : la réponse est un `grep` que le kit exécute pour moi.

**Renvoi dans le mémoire.** III.2

**Preuve.** ligne src/lib/catalog.ts  14
**Contrôle.** ✓ preuves vérifiées

## Q10 · fiabilité — Deux clics sur « commander » : deux commandes ?

**Réponse.** Non : la clé d'idempotence est prise dans la base avec un verrou, et l'index la rend unique. La seconde requête retombe sur la commande existante. Les deux lignes sont citées dans le rapport et dans l'annexe des preuves.

**Relance probable.** Et si la clé est perdue par le client ?

**Piège.** Promettre une file d'attente : le dépôt ne l'a pas.

**Renvoi dans le mémoire.** III.4, annexe F

**Preuve.** ligne src/actions/checkout.ts  66
**Contrôle.** ✓ preuves vérifiées

## Q11 · accessibilité — Votre rapport est-il lisible par un daltonien, et votre site est-il sobre en mouvement ?

**Réponse.** Le rapport encode par forme, label et texte, jamais par couleur seule, et la planche de contact le vérifie. Pour le site, la réduction de mouvement tient dans une seule feuille, sans hook React : c'est peu, et le rapport l'écrit comme limite plutôt que comme succès.

**Relance probable.** Pourquoi ne pas avoir branché useReducedMotion ?

**Piège.** Réclamer un mérite d'accessibilité non mesuré : la loi du kit est d'inscrire l'écart.

**Renvoi dans le mémoire.** V.6, figure 43

**Preuve.** motif src/app/globals.css prefers-reduced-motion
**Contrôle.** ✓ preuves vérifiées

## Q12 · langue — Le projet est tunisien : l'arabe est-il dans le produit ?

**Réponse.** Non, et c'est écrit dans les non-objectifs : l'interface est en français, la disposition arabe n'a pas été rendue ni testée. La donnée tunisienne, elle, est réelle : vingt-quatre gouvernorats, cinquante-trois villes dans neuf délais, frais en millimes.

**Relance probable.** Que coûte l'activation du RTL ?

**Piège.** Répondre « prêt à activer » : la chaîne de traduction n'existe pas dans le dépôt.

**Renvoi dans le mémoire.** I.6.1, B4

**Preuve.** motif src/lib/tunisia.ts GOVERNORATES
**Contrôle.** ✓ preuves vérifiées

## Q13 · argent — Comment est calculé le franco de port ?

**Réponse.** Sur le montant après remises, à quatre-vingt-dix-neuf dinars, avec trois paliers de livraison à sept, douze et cinq mille millimes. Les nombres du rapport viennent du fichier de tarification, formatés à la française, et la table est générée.

**Relance probable.** Le franco s'applique-t-il avant ou après la promotion ?

**Piège.** Inventer l'ordre des calculs : l'annexe des preuves le donne ligne à ligne.

**Renvoi dans le mémoire.** III.6.1

**Preuve.** ligne src/lib/money.ts  4
**Contrôle.** ✓ preuves vérifiées

## Q14 · méthode — Comment savez-vous que votre PDF n'est pas un assemblage de captures ?

**Réponse.** Parce que les ratios des planches sont lus dans les deux formats, que le nombre de poses égale le nombre de planches, et que aucune figure n'est passée par le raster. Deux rebuilds successifs donnent la même empreinte, et le second harnais recompte les placements sans consulter le premier.

**Relance probable.** Montrez-moi la trace.

**Piège.** Jurer : `audit/dernier-build.json` et `audit/ab/harnais.json` répondent plus vite.

**Renvoi dans le mémoire.** V.2, V.5

**Preuve.** fichier audit/ab/harnais.json
**Contrôle.** ✓ preuves vérifiées

## Q15 · vérité — Qu'avez-vous vérifié vous-même, dans un kit écrit par une machine ?

**Réponse.** Chaque statut du mémoire : pas un « fait » sans fichier, ligne ou sortie. Les trois cent trente-trois lignes de l'appareil, les 28 corrections du fichier CORRECTIONS.md et les cinq chaos provoqués sont là pour ça. Le dépôt ne se relance pas sans node_modules, et le kit l'écrit comme dégradation au lieu de le cacher.

**Relance probable.** Où est la preuve que vous n'avez pas enjolivé une figure ?

**Piège.** Répondre par la confiance : la figure 27 et le test de mutation M1 répondent.

**Renvoi dans le mémoire.** B5, V.6

**Preuve.** fichier CORRECTIONS.md
**Contrôle.** ✓ preuves vérifiées

