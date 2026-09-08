# Portes G1 à G27

Verdict : **vert** — 27/27 portes vertes, note G6 100/100, 1.4 s.

| porte | intitulé | invariants | verdict | mesure | preuve |
| --- | --- | --- | --- | --- | --- |
| G1 | Démarrage : sept actes écrits avant le code | INV-5, INV-7 | vert | actes B0 à B6 écrits avant le code : ['0', '1', '2', '3', '4', '5', '6', '7'] | `audit/B0-boot.md` |
| G2 | Pré-mortem de huit morts | INV-12 | vert | 8 morts listées dans le pré-mortem (huit exigées) | `audit/B0-boot.md` |
| G3 | Plan et budget chiffrés tenus | INV-20 | vert | 113 pages, 36.9 s de build, 3.9 Mo | `audit/budgets.json` |
| G4 | Audit du dépôt contre le cahier | INV-5, INV-6 | vert | gisements comptés : tables 24, enums 10, produits 81, marques 16, universes 7, actions 30 | `audit/facts.json` |
| G5 | Banque de quinze questions de jury | INV-12 | vert | 15/15 cartes à preuve vérifiée (défauts aucun) | `audit/kit/jury.json` |
| G6 | Grille de notation auto-appliquée | INV-8, INV-11 | vert | note 100/100 (seuil 97), détail écrit dans audit/kit/rubrique.md | `audit/kit/rubrique.md` |
| G7 | Pare-feu de périmètre et non-objectifs | INV-6 | vert | pare-feu écrit, mentions absentes aucune | `audit/B0-boot.md` |
| G8 | Rapport composé entre le plancher et le plafond de pages, tout vectoriel | INV-1, INV-2, INV-3, INV-4 | vert | 113 pages (bande 102 à 168), 61 planches dessinées, 61 posées, 0 secours raster | `audit/dernier-build.json` |
| G9 | Zéro copié-collé | INV-7 | vert | 0 bloc(s) de prose répétés  | `audit/qa.json` |
| G10 | Lois de langue exécutées | INV-8, INV-9, INV-10 | vert | source : 1772 lignes vérifiées ; rendu : 0 faute(s) sur 4203 lignes reconstituées, 1064 lignes de verbatim exemptées | `audit/langue.json` |
| G11 | Inoculation trois sur trois | INV-12 | vert | 3/3 inoculations présentes au rendu : shopify (I.4) vu ; paiement (II.5) vu ; charge (V.) vu | `audit/qa.json` |
| G12 | Registre de figures complet | INV-13 | vert | 61/61 planches, 61 poses, 70 tableaux | `audit/dernier-build.json` |
| G13 | Sommaire et listes cliquables | INV-14, INV-15 | vert | 233 signets pour 233 ancres, 229 liens résolus, 0 mort(s) | `audit/liens.json` |
| G14 | Accessibilité et non-couleur | INV-18, INV-19 | vert | 7/7 statuts de commande nommés en toutes lettres au rendu (absents aucun) | `audit/qa.json` |
| G15 | Cinq applaudissements scriptés | INV-24 | vert | 5 moments marqués « APPLAUDIR » dans soutenance/JOURJ.md | `soutenance/JOURJ.md` |
| G16 | Diaporama de trente glissades | INV-24 | vert | 30 parties `slide` dans le paquet | `soutenance/Cleopatre-soutenance.pptx` |
| G17 | Morph réel dans le fichier | INV-24 | vert | 5 glissades portant `p159:morph option="byObject"` | `audit/qa2.json` |
| G18 | Cinq zooms de détail | INV-3 | vert | 5 zooms déclarés, 5 fichiers produits | `audit/qa2.json` |
| G19 | Minutage à quatorze minutes trente | INV-20 | vert | minutage 14 min 30 annoncé au JOURJ, deck de 3806 Ko | `soutenance/JOURJ.md` |
| G20 | Dix dix dix mesurés | INV-20 | vert | corps minimal 18.0 pt, maximum 38 mots par glissade, contraste le plus faible 7.63:1 | `audit/qa2.json` |
| G21 | Démo en trois chemins, zéro réseau | INV-6 | vert | 3 chemins de démonstration scriptés, zéro dépendance réseau : True | `soutenance/JOURJ.md` |
| G22 | Harnais double convergent | INV-21 | vert | 13/13 lois en accord, divergences aucune ; quatre écarts de méthode instruits | `audit/ab/harnais.json` |
| G23 | Quatre chaos conduits | INV-22 | vert | 4/4 conformes (figure absente, PNG corrompu, capture 8K, figs/ vidé) | `audit/chaos/resume.json` |
| G24 | Trois mutations détectées | INV-23 | vert | 3/3 fautes injectées attrapées | `audit/mutation/resume.json` |
| G25 | Épuisement signé | INV-7, INV-17 | vert | constat signé le 08/09/2026 ; portes automatiques vertes à la signature : True | `audit/RIEN-A-AJOUTER.md` |
| G26 | Kit et war-room livrés | INV-25 | vert | 6/6 livrables du kit, 10 commandes de rebuild, 7 entrées de dépannage | `soutenance/JOURJ.md` |
| G27 | Gel scellé et étiquette poussée | INV-16, INV-17 | vert | 37 empreintes scellées, 0 dérivée(s), étiquette locale v1.0-final ; poussée : [à la main du déposant] | `audit/sceau.json` |
