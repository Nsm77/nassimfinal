# B0 — Boot, sept actes écrits avant tout code

Objet : produire le kit de soutenance (rapport PDF vectoriel, deck PPTX à Morph, harnais QA,
war-room) d'un projet réel déjà implémenté : **Cléopâtre — Espace Santé Beauté**, plateforme
e-commerce de parapharmacie (Ezzahra · Hammam-Lif), Next.js 16 / React 19 / TypeScript strict /
Tailwind v4 / Drizzle + PostgreSQL 18 / Zod / Server Actions.

## B0 — Auto-audit du prompt v13 (contradictions, angles morts, hypothèses signées)

| # | Constat | Nature | Traitement retenu (signé) |
|---|---------|--------|---------------------------|
| 1 | §2 réclame « PG18 · Docker » mais le dépôt ne contient **aucun Dockerfile** ; la base locale est servie par `embedded-postgres@18.4.0-beta.17` (package.json devDependencies). | contradiction prompt/réel | Le rapport documente la **réalité** (PostgreSQL 18 embarqué, pilote `pg`, pool max 10 — `src/db/index.ts:13`) et **déclare** la conteneurisation comme hors périmètre, consignée en ADL. Aucune figure « Docker » inventée. |
| 2 | §2 annonce « 24 tables » ; le README du dépôt en annonce 23. | contradiction interne au dépôt | Vérifié par analyse du schéma : `grep -c pgTable src/db/schema.ts` → **24**. Le README est corrigé (l'erreur venait du README, pas du code). |
| 3 | §4 impose « ~120 p. » ; B4 interdit le remplissage. | tension objectif/moyen | La page cible est un **effet de bord** du contenu (50 figures, 24 tables détaillées, catalogue 81 lignes, annexe F complète). Aucune ligne de remplissage ; si le rendu fait 112 pages, le kit déclare 112. |
| 4 | §2 réclame des « tests » (traçabilité F : US→…→test) alors que l'application n'a **aucune suite de tests unitaires** (aucun fichier `*.test.ts` dans le dépôt). | angle mort | Le test de référence = le harnais QA du kit (`qa.py`/`qa2.py` : 100 % des chiffres du PDF re-greffés sur le code) + les 3 commandes de rebuild + protocoles manuels d'annexe E. Limitation déclarée, chiffrée, en §IV.6 et en ADL. |
| 5 | §5 « Exception = refus » et §7 « STOP : vérité > esthétique » se contredisent sur un timbre manquant. | ambiguïté | Règle appliquée : timbre vectoriel absent → repli **déclaré** sur le PNG (le §5 l'écrit explicitement) ; toute **autre** anomalie (figure absente, `figs/` vide, PNG corrompu) → exception et exit 1. |
| 6 | §1 « convergence 0 finding » et §9 « fautes connues vivante » : un 0 figé serait un mensonge dès qu'on touche au livrable. | angle mort | Les 30 attaques et les rounds sont **exécutés** (`rapport/assauts.py`) et non racontés ; la convergence est datée et reproductible ; le dernier round utile avant scellement fait foi. |
| 7 | §11 exige une ligne `commit · tag v1.0-final · sha256` dans le bloc de fin, donc un commit **après** le scellement du manifeste. | ordre circulaire | Ordre réel : gel du contenu → calcul du manifeste + sha256 → écriture du bloc de fin **dans** `audit/SCESCELLEMENT`… → commit unique → tag. Le sha256 affiché est celui du PDF final, pas celui du commit. |
| 8 | Hypothèses signées : le lecteur-cible est un jury tunisien de fin d'études (licence/génie logiciel) ; le dépôt est le produit ; le PDF est lu à l'écran **et** imprimé N&B. | hypothèses | Acceptées et rappelées en §I.1 ; elles contraignent : double registre, print/N&B, daltonisme (forme+label), pas de couleur seule. |

## B1 — Pre-mortem : huit morts possibles, huit tueurs

Le projet est mort dans 12 mois. Pourquoi ? (→ chaque risque a son tueur exécuté, §12 du prompt, prouvé en `audit/gates.md`.)

1. **Le build ne passe pas hors de ma machine** → tue par « effet de seuil du correcteur ». *Tueur* : G3/G8 — trois commandes, Python pur, `qa.py` et `qa2.py` exit 0 sur un clone propre, consigné dans `REPRO.md`.
2. **Un chiffre du rapport est faux** (ex. « 81 produits » alors que le seed en a 79). *Tueur* : INV-2/INV-6 — **aucun nombre n'est tapé à la main** : `rapport/facts.py` parse le dépôt à chaque build, `qa.py` re-extrait le texte du PDF et re-giffe chaque valeur contre le code source.
3. **Les figures sautent une page ou sont floues à l'impression.** *Tueur* : G1/G10 + §5 — chaque figure est sauvée en PDF **et** PNG aux mêmes proportions, l'assemblage est en millimètres avec assert sur la boîte, zoom 400 % vérifié, `pixel-diff` sur 7 pages.
4. **Le Morph du deck ne passe pas sur le projecteur.** *Tueur* : G4/§6 — `AlternateContent` + `<mc:Fallback>` fondu, vérifié par `grep p159:morph == N` (INV-5) et drill « PPTX vieux → fondu vérifié, et on le dit ».
5. **Le jury pose la question du paiement par carte / du hors-scope.** *Tueur* : G5 — banque de 15 questions amorcée + `jury.py` 5+5+5, réponses avec preuve `fichier:ligne`.
6. **La démo réseau tombe le jour J.** *Tueur* : G8/§7 — kit J `L1 live → L2 captures → L3 narration <20 s`, `backup.pdf`, `JOURJ.md`.
7. **Le texte est mou : phrases creuses, anglicismes, « innovant ».** *Tueur* : G17 — loi SLOP/SYNONYMES/INSÉCABLES **exécutable** (regex + occurrence = rewrite), appliquée à l'écriture et re-vérifiée sur le PDF rendu.
8. **Le dépôt contient un secret** (mot de passe réel, URL de prod). *Tueur* : G26 — scan secrets du diff et de l'arbo (0 finding), `.gitignore` verrouillé, secrets de démo documentés comme tels et seulement comme tels.

## B2 — Plan et budget (enveloppes consommées, pas intentions)

| Poste | Enveloppe | Ce qu'elle achète |
|-------|-----------|--------------------|
| Rapport (PDF ~120 p.) | 38 % | 50 figures vectorielles, 4 parties + 6 annexes, annexe F traçable 24/24, lois de langue |
| PPTX (26 + 4 annexes) | 16 % | Morph réel, builds, 5 zooms, notes minutées ≈ 15 min |
| QA / assauts | 22 % | `qa.py` ≡ `qa2.py`, 30 attaques exécutées, mutation 3/3, chaos 4/4, 27 gates |
| Vernis | 8 % | couverture or + double logo, intercalaires, print/N&B, daltonisme, métadonnées, signets |
| Kit + war-room | 8 % | `REPRO.md`, `JOURJ.md`, `REPEATS.md`, `CORRECTIONS.md`, banque, kit J |
| Sceau + post | 8 % | manifeste + sha256, tag, passation, ADL |

Contrainte dure mesurée : PDF ≤ 30 Mo · PPTX ≤ 15 Mo · build rapport ≤ 10 min · figures ≤ 5 min · QA ≤ 3 min.

## B3 — Audit du prompt §8 + §9

- §8 (25 invariants) : tous ont un *comment-prouver* exécutable, sauf INV-25 (épuisement) qui est un acte signé → journal de tentatives `audit/epuisement.md`, et INV-11 (« casier 27 scellements ») qui devient 27 preuves `audit/gates/Gnn.txt`. Aucun invariant « à la tête du client » : 25 lignes, 25 commandes, 25 sorties.
- §9 (fautes connues) : la liste est augmentée de trois fautes *réellement* observables ici — (a) compter les tables avec `grep -c "pgTable"` **ou** le README, pas les deux ; (b) placer les figures en points au lieu de millimètres ; (c) supposer que ReportLab et matplotlib partagent les mêmes espaces insécables. Parade : `facts.py` unique, placements en mm avec assert, glyphe testé par `fontTools` **et** par largeur de signe ReportLab.

## B4 — Pare-feu et NON-OBJECTIFS

Zéro remplissage · zéro fonctionnalité inventée · zéro donnée falsifiée · zéro dégradation silencieuse · pas de vidéo · pas de CMYK · pas de RTL (perspective seulement) · pas de fonds perdus · pas de données réelles (chiffres d'affaires, clientèle, noms réels) — **tout ce qui relève du réel non public est entre [crochets]**.
Ajout hors-scope = entrée dans `decisions.md` (ADL) **et** accord explicite du souverain. Sont donc *refusés* sans ADL : générateur de site, i18n arabe effective, PDF/X, animations CSS dans le deck, OCR des captures, « IA qui rédige le rapport ».

## B5 — Serment

Je n'écrirai dans ce kit aucune phrase que le dépôt ne peut pas prouver. Je préfère une page de moins et un zéro de plus. Chaque fois que le réel manque, j'écris un crochet, pas un chiffre. Chaque fois qu'un contrôle échoue, il échoue à l'écran, pas dans mon résumé.

## B6 — Horizons shippables

- **H1 (livrable minimal sincère)** : build unique, PDF complet mais figures basiques, deck sans Morph, `qa.py` vert.
- **H2 (niveau visé, atteint)** : 50 figures vectorielles + assemblage mm, Morph réel + fallback, `qa.py ≡ qa2.py`, 30 attaques exécutées, 27 gates, kit J.
- **H3 (lubies à ne pas financer ici)** : version anglaise du rapport, thème N&B dédié avec planches séparées, export DOCX pour l'école, vidéo de démo, RTL arabe. Déclarées, non commencées.

## B7 — Dégradation déclarée L0→L3 (et ce qui est interdit)

| Niveau | Contenu | État |
|--------|---------|------|
| **L0** | PDF vectoriel complet + PPTX Morph + harnais double + kit J + 27 preuves | **visé et mesuré** |
| L1 | PDF vectoriel + PPTX sans Morph (fondu), kit J réduit à `backup.pdf` | autorisé si budget figures dépassé |
| L2 | PDF à figures PNG 300 ppp, deck en images, pas d'annexe A/B/C | autorisé seulement si matplotlib indisponible |
| L3 | Texte seul | **interdit** |

Interdits absolus (aucune dégradation ne les autorise) : enlever une figure déjà citée, tronquer l'annexe F, remplacer un chiffre par une estimation, maquiller un échec de gate en « à faire », écrire « testé » sans sortie.
