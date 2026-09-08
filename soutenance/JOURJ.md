# Jour J — minute par minute, de T-60 à T+30

Le document se lit à voix basse, une fois, le matin. Tout ce qui doit être décidé est déjà décidé :
le reste est de l'exécution. Durée annoncée du passage : **14 min 30** sur trente glissades, soit
vingt-neuf secondes en moyenne, deux minutes de battement absorbées par les cinq transitions Morph.

## T-60 — la salle
- [ ] Brancher, projeter, **couper le wifi de démo** : le deck doit tenir hors ligne, et le dit.
- [ ] Ratio 16:9 vérifié sur le projecteur, pas sur l'écran du portable (les contrastes changent).
- [ ] Liseuse de notes ouverte sur les trente minutages ; un chronomètre, pas le téléphone.
- [ ] `Cleopatre-soutenance.pptx` copié sur la clé **et** sur le disque local de la salle.
- [ ] Le PDF du rapport, ouvert à la page de la figure 49 : c'est la première question du jury.

## T-40 — le matériel de preuve
- [ ] Dépôt sur deux terminaux : l'application ne dépend d'aucun service extérieur, sauf la base
  embarquée ; `npm ci` a été fait la veille, pas le matin même.
- [ ] Trois chemins de démonstration scriptés, chacun chronométré, chacun avec sa sortie imprimée :
  CHEMIN 1 — catalogue et besoins : entrer par « peau qui tire », sortir avec un panier dont le port est de 7,000 DT (sept mille millimes, le palier standard).
  CHEMIN 2 — commande et stock : deux onglets, un stock à 1, une commande qui passe, une qui est
  refusée avec le motif lisible ; le verrou est montré dans `src/lib/orders.ts`.
  CHEMIN 3 — administration et preuve : le registre des promotions, les huit motifs de refus, la
  facture PDF engendrée, puis le contrôle de langue `python3 rapport/qa.py` qui rend son procès-verbal.
- [ ] Aucun lien réseau dans le paquet : le harnais le vérifie (QA-11, assaut A25).

## T-20 — le corps du texte
- [ ] Les cinq moments où le jury doit applaudir sont écrits, pas espérés. Chacun est dit à voix haute
  une fois, avec sa phrase de clôture :
  - APPLAUDIR 1 (glissade 4, problème) : « Trois-cent-un besoins, deux boutiques, zéro moteur de
    recherche : le client entre par un mot du quotidien, et le catalogue ne lui répondait pas. »
  - APPLAUDIR 2 (glissade 10, modèle) : « Le modèle de données n'a pas été dessiné puis codé : il a
    été lu dans le code, et les vingt-quatre tables du diagramme sont celles du dépôt. »
  - APPLAUDIR 3 (glissade 15, avant/après) : « Ce qui était un tableur partagé tient maintenant en
    une requête avec un verrou. Le gain n'est pas une opinion, c'est une mesure : 0,01 milliseconde
    de règle, un fichier, et zéro client qui voit un stock fantôme. »
  - APPLAUDIR 4 (glissade 17b, bilan) : « Cent treize pages de rapport, soixante et une figures,
    toutes engendrées : aucune capture, aucun copier-coller, deux harnais qui se contredisent
    publiquement et finissent d'accord. »
  - APPLAUDIR 5 (glissade 18, démo) : « Le troisième chemin que je vais montrer est celui que je
    n'ai pas écrit pour la salle : c'est le contrôle qui refuse mon propre rapport quand un chiffre
    diverge. »
- [ ] Les cinq silences (après chaque applaudissement) sont comptés : deux secondes, pas une.
- [ ] Les quatre transitions Morph sont vérifiées à l'écran, pas dans le XML.

## T-5 — la respiration
- [ ] Les trois phrases d'ouverture, apprises ; les trois de clôture, apprises. Le milieu s'explique.
- [ ] Les quatre questions qui font peur, relues dans `soutenance/BANQUE-JURY.md` (Q2, Q7, Q11, Q15).
- [ ] Verre d'eau. Téléphone en avion, montre à la table.

## T+0 à T+14:30 — le passage
- [ ] Glissade 1 sans parler plus de vingt secondes : le titre dit déjà l'objet.
- [ ] Si une démonstration échoue : on la nomme, on passe à la sortie imprimée, on la reprend en
  questions. Une démo muette coûte trois minutes ; une démo nommée coûte dix secondes.
- [ ] À onze minutes : sauter les glissades 9 et 12, jamais la 17 (bilan) ni la 19 (remerciements).
- [ ] Le minutage se lit dans les notes, pas dans la salle.

## T+15 à T+30 — après
- [ ] Remercier le jury debout, range le câble avant de parler : la salle se souvient de l'ordre des gestes.
- [ ] Noter les trois questions qui ont coincé, dans `decisions.md`, à chaud, avant les compliments.
- [ ] Vérifier le scellement : `python3 rapport/gates.py` doit rendre vingt-sept portes vertes, et
  l'étiquette `v1.0-final` doit exister. Si une porte est rouge, on ne promet rien : on corrige.
- [ ] Rendre le dossier `audit/` au tuteur, en même temps que le PDF : c'est lui qui vaut les chiffres.
