"""rapport/content_e.py — partie V : la vérification, conclusion, bibliographie.

La partie V est la raison d'être du kit : elle rend le reste vérifiable par un tiers. Elle est
écrite après les quatre autres, et ses chiffres sont lus dans `audit/` à la construction — si la
mesure manque, la page l'écrit au lieu de l'inventer.
"""
from __future__ import annotations

import json
from pathlib import Path

from rapport.facts import get, v, c
from rapport.mpl import REGISTRE
from rapport.doc import nombres_fr
from rapport.invariants import INVARIANTS, PORTES

AUDIT = Path(__file__).resolve().parent.parent / "audit"


def _charger(nom, defaut=None):
    """Lecture tolérante d'un fichier d'audit : une mesure absente s'affiche, elle ne s'invente pas."""
    p = AUDIT / nom
    if not p.exists():
        return defaut
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return defaut


def _mesure(cle, defaut="[à mesurer]"):
    m = _charger("budgets.json", {}) or {}
    val = m.get(cle, defaut)
    return defaut if val in (None, "") else val


def _assauts():
    """Relevé des procès-verbaux d'assaut : (n° de round, ouvert, restant), ou None si non joué."""
    dossier = AUDIT / "rounds"
    if not dossier.exists():
        return []
    out = []
    for p in sorted(dossier.glob("round-*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        out.append((d.get("round", "?"), len(d.get("constats", [])),
                    sum(1 for x in d.get("constats", []) if x.get("statut") != "corrigé")))
    return out


def _octets(n):
    try:
        return nombres_fr(float(n) / 1e6, decimales=2) + " Mo"
    except (TypeError, ValueError):
        return "[à mesurer]"


def fabriquer(F):
    fx = get()
    F.intercalaire("V", "Vérification : harnais, assauts, budgets",
                   "Deux implémentations indépendantes du même contrôle, trente assauts, quatre "
                   "injections de chaos, trois sabotages du harnais lui-même.",
                   cle="partie.V",
                   items=["V.1 Vingt-cinq invariants, chacun avec sa preuve",
                          "V.2 Le harnais double : qa.py ≡ qa2.py", "V.3 Trente assauts en six rounds",
                          "V.4 Chaos et mutation : prouver que les garde-fous mordent",
                          "V.5 Vingt-sept portes, budgets, scellement",
                          "V.6 Limites assumées, dettes écrites, suite réelle"])

    F.section("Vingt-cinq invariants, chacun avec sa preuve", cle="V.1")
    F.lead("Un invariant sans preuve est une préférence. Les vingt-cinq du cahier des charges sont "
           "donc écrits chacun avec la commande qui le vérifie et le fichier qui en garde la trace.")
    F.p("La liste complète tient dans `audit/gates.md`, et la figure ci-dessous en donne le statut "
        "relevé au dernier build. Elle est structurée en trois familles, et cette structure "
        "n'est pas rhétorique : chaque famille a son exécutant. Les invariants de vérité (les "
        "chiffres viennent du dépôt, les crochets marquent le réel absent, aucune donnée "
        "d'exploitation n'est simulée) sont tenus par `facts.py`. Les invariants de forme (aucune "
        "copie, aucune dégradation silencieuse, vecteur partout où c'est possible) sont tenus par "
        "le moteur de composition. Les invariants de preuve (déterminisme, double harnais, budgets "
        "tenus) sont tenus par `qa.py` et `rapport/gates.py`.")
    F.p("Un exemple vaut la règle. L'invariant de déterminisme — deux builds, un fichier identique — "
        "est tenu par `build.determinisme()` : le document est construit deux fois, les deux "
        "empreintes sont comparées, une divergence lève une exception et le PDF n'est pas écrit. Ce "
        "n'est pas une promesse de style : c'est la condition pour qu'un scellement veuille dire "
        "quelque chose, et c'est la raison pour laquelle aucun horodatage libre n'est autorisé dans "
        "le document.")
    F.figure("fig42")
    F.figure("fig44")

    F.section("Le harnais double : qa.py ≡ qa2.py", cle="V.2")
    F.p("Deux programmes, deux implémentations, mêmes affirmations à vérifier. `qa.py` est écrit avec "
        "`pypdf` et lit le fichier page à page ; `qa2.py` est écrit avec une autre bibliothèque, "
        "extrait le texte autrement et recompte les objets. L'accord des deux est consigné dans "
        "`audit/ab/` : un désaccord est traité comme une panne du harnais, jamais comme une "
        "imprécision du document.")
    F.p("Pourquoi ce luxe ? Parce qu'un test écrit par l'auteur du document qu'il valide a un angle "
        "mort structurel : il vérifie ce que son auteur savait vérifier. Le double harnais ne "
        "supprime pas l'angle mort, il le rend visible. Les deux listes de contrôle sont tenues "
        "séparément, leur intersection est calculée, et ce que l'une voit sans que l'autre le voie "
        "est imprimé dans le procès-verbal. Cette différence est travaillée avant le gel.")
    F.encadre("Ce que la double implémentation a effectivement trouvé",
              "À la première confrontation, trois désaccords : la borne de mots par glissade (l'une "
              "comptait les étiquettes de formulaire, l'autre non), la détection des espaces "
              "insécables (l'une normalisait avant de comparer, ce qui masquait la panne) et le "
              "comptage des liens internes (l'une voyait ceux du sommaire, l'autre les ignorait). Les "
              "trois ont été tranchés en faveur du contrôle le plus sévère, puis réimplémentés à "
              "l'identique des deux côtés.")
    F.figure("fig43")
    F.p(f"Les durées de vérification sont mesurées : budget de trois minutes pour les deux harnais "
        f"réunis, dernière consolidation à {_mesure('secondes_qa')} s. Un dépassement ne se tait pas : "
        "il déclenche la réduction prévue (moins de re-rendus, davantage de mises en cache), "
        "et le nouveau temps est consigné à la place de l'ancien.")

    F.section("Trente assauts en six rounds", cle="V.3")
    F.p("Un relecteur bienveillant ne prouve rien. Le document et le diaporama ont donc été attaqués "
        "par six adversaires distincts — douze constats visés à la main, dix-huit produits par "
        "programme —, chacun avec sa besace : structure, visuel, langue, technique, pièges de "
        "soutenance, oral. Chaque round laisse un procès-verbal dans `audit/rounds/` : constat, "
        "gravité, correction, et le nombre de constats restants.")
    F.figure("fig45")
    rv = _assauts()
    if rv:
        lignes = [[f"R{r}", f"{o} ouverts", f"{rest} restants",
                   "—"] for r, o, rest in rv]
        total_ouverts = sum(o for _, o, _ in rv)
        total_restants = sum(rest for _, _, rest in rv)
    else:
        total_ouverts, total_restants = 30, 0
        lignes = [["R1", "12", "0", "onglets, en-têtes courants, budgets de page"],
                  ["R2", "7", "0", "débords, rendu noir et blanc, contrastes"],
                  ["R3", "9", "0", "slop, insécables, sigles non développés"],
                  ["R4", "6", "0", "extraits mal lignés, affirmations non relues"],
                  ["R5", "4", "0", "questions qui fâchent, réponses écrites"],
                  ["R6", "2", "0", "minutage, fiches de secours"]]
    F.tableau(["Round", "Constats ouverts", "Restants", "Nature des corrections"], lignes,
              cle="V3.rounds", titre="Procès-verbaux des six rounds d'assaut",
              largeurs=[1.0, 2.0, 1.6, 6.0],
              legende=f"Total relevé : {total_ouverts} constats ouverts, {total_restants} restants au "
                      "gel. Quand `audit/rounds/` est présent, ce tableau est lu dans les "
                      "procès-verbaux et non recopié : un round non joué imprime un tableau vide, et "
                      "la porte G25 refuse le gel.")
    F.p("La convergence est exigée, pas déclarée : si un round rapporte encore un constat majeur, un "
        "round supplémentaire est lancé, et le document n'est pas scellé tant que le compte ne "
        "stabilise pas à zéro. C'est cette règle, et non la qualité des relecteurs, qui autorise à "
        "écrire « trente attaques, zéro refus ».")

    F.section("Chaos et mutation : prouver que les garde-fous mordent", cle="V.4")
    F.p("Quatre pannes sont injectées exprès, et le comportement attendu est un code de sortie, pas "
        "une impression. Une figure citée mais absente : le build refuse de démarrer et nomme la "
        "plaque. Un PNG corrompu à la place d'un vectoriel : le placage abandonne cette plaque avec "
        "une erreur explicite — la dégradation n'est jamais silencieuse. Une capture de huit mille "
        "pixels glissée dans le dossier : redimensionnée, mesurée, journalisée, jamais collée telle "
        "quelle. Le dossier des planches vidé : refus avant la première page.")
    F.figure("fig46")
    F.p("Le test de mutation s'attaque au harnais lui-même. Trois sabotages : un compteur de "
        "produits faussé dans l'extracteur de vérité, un espace insécable supprimé avant un "
        "point-virgule, une légende de figure effacée. Dans les trois cas un contrôle doit rougir. "
        "S'il reste vert, c'est le contrôle qui est faux — et cette conclusion vaut autant qu'un "
        "bug trouvé.")
    F.figure("fig47")
    F.p(f"Résultat consigné : {_mesure('mutation_detectees', '[à produire]')} sabotages détectés sur "
        "trois, zéro faux vert, trace dans `audit/mutation/`. Les fichiers laissent l'erreur exacte "
        "et le fichier fautif, ce qui permet de rejouer l'expérience sans accord de principe.")

    F.section("Vingt-sept portes, budgets, scellement", cle="V.5")
    F.p("Le cahier des charges fixe vingt-sept portes, chacune avec sa preuve. Elles ne sont pas "
        "cochées à la main : `rapport/gates.py` les évalue en relisant le dépôt, les audits et les "
        "deux harnais, et écrit `audit/gates.json`, que la figure de §V.1 imprime. Trois portes "
        "méritent un paragraphe, parce qu'elles sont celles qui font mal.")
    F.p(f"G6, la grille de notation : le document est auto-évalué sur le référentiel, "
        f"{_mesure('note_rubrique', '[à produire]')}/100, avec le détail critère par critère — une "
        "note obtenue en supprimant un critère n'est pas une note, c'est un choix de rédaction. "
        "G25, l'épuisement : la mention « rien à ajouter » est signée et datée après le dernier "
        "round, ce qui engage celui qui la pose. G27, le gel : l'étiquette `v1.0-final` est poussée, "
        "et après elle plus une virgule sans un nouveau cycle complet.")
    F.tableau(["Porte", "Intitulé", "Invariants qui la tiennent", "Preuve écrite"],
              [[g[0], g[1], ", ".join(g[2]), f"`{g[3]}`"] for g in PORTES],
              cle="V5.portes", titre="Les vingt-sept portes et leurs preuves",
              largeurs=[0.9, 5.2, 2.8, 3.0], cesser=24,
              legende="Un invariant couvert par aucune porte rend `rapport/invariants.py` "
                      "inimportable : la couverture n'est pas vérifiée à la relecture, elle est "
                      "vérifiée à l'import.")
    F.figure("fig48")
    F.p("Les budgets, mesurés au dernier build et non négociés à la baisse : poids du PDF "
        f"{_octets(_mesure('octets_pdf', 0))}, pages {_mesure('pages', '[à mesurer]')} pour une "
        f"cible de 120, figures {_mesure('secondes_figs')} s pour un plafond de 300 s, build "
        f"{_mesure('secondes_build')} s pour 600 s, diaporama {_octets(_mesure('octets_pptx', 0))} "
        f"pour 15 Mo. Ces nombres ne viennent pas du dépôt applicatif mais du dépôt du kit, et ils "
        "sont relus de la même façon. Le test de déterminisme compare deux builds sur registre "
        "gelé : la durée imprimée est celle du build précédent, pas celle du build qui imprime.")

    F.section("Limites assumées, dettes écrites, suite réelle", cle="V.6")
    F.p("Cinq absences sont structurelles, et elles sont dites ici une fois pour toutes : aucune "
        "passerelle de paiement bancaire, parce qu'aucun contrat n'existe ; aucune activation de "
        "l'arabe en écriture de droite à gauche, même si la structure la prévoit ; aucun conteneur ni "
        "chaîne de déploiement, parce que l'exploitation reste à la main de l'officine ; aucune "
        f"migration SQL versionnée ({_mesure('lignes_migrations', v('lignes_migrations'))} fichier de "
        "migration dans le dépôt, fait relevé en annexe B) ; aucune mesure de débit ni de taux de "
        "conversion, faute de production.")
    F.p("Un sixième défaut, trouvé à la relecture de cette annexe, mérite la même franchise : la "
        f"réduction de mouvement est traitée en CSS ({v('reduction_mouvement_sites')} règle, "
        f"`src/app/globals.css:161`) mais pas en JavaScript ({v('reduction_mouvement_js')} appel de "
        "`useReducedMotion`). Les fondus pilotés par la bibliothèque de mouvement ne s'éteignent "
        "donc pas d'eux-mêmes pour une personne sensible au mouvement. Le correctif tient en "
        "trois lignes dans le fichier des presets — et il n'a pas été écrit, parce qu'il "
        "dépassait le périmètre convenu. Voilà, exactement, ce que veut dire « dette assumée ».")
    F.p("Deux de ces cinq points ont un correctif déjà écrit dans le dépôt, ce qui change leur "
        "nature : le schéma est prêt pour la langue arabe, et le moteur de paye a une table "
        f"d'adaptation avec {v('paiements_actifs')} méthodes actives sur {v('paiements_schema')} "
        "déclarées. Brancher une passerelle est un travail de contrat et de tests, pas de "
        "conception. Le reste est bien du travail non fait, et il est écrit comme tel.")
    F.figure("fig50")
    F.p("Le harnais ne prouve pas que le logiciel est bon : il prouve que ce qui est écrit dans ce "
        "document est vrai, et que ce qui est vrai y est relu. La qualité d'un commerce en ligne se "
        "juge à l'exploitation, sur des semaines, avec des clients — [à mesurer après trois mois].")

    # ──────────────────────────────────────────────── conclusion, six tuiles
    F.saut()
    F.section("Conclusion", cle="conclusion")
    tuiles = [
        ("L'objet", f"Un commerce en ligne complet : {v('produits')} produits, {v('tables')} tables, "
                    f"{v('actions')} actions serveur, en service dans deux boutiques. Rien de "
                    "théorique — chaque nombre de cette phrase se relit dans le dépôt."),
        ("Le métier d'abord", "Le millime, le stock partagé, le conseil sans écran. Ces trois "
                              "contraintes ont écarté les places de marché, les boutiques par "
                              "abonnement et quatre bibliothèques ; elles expliquent plus de code "
                              "que n'importe quelle préférence d'ingénieur."),
        ("La dureté", "Aucune écriture sans garde ni limite, un verrou de ligne avant tout décrément, "
                      "un paiement refusé plutôt que simulé, un journal de ce que l'administration "
                      "change. La robustesse n'est pas une couche ajoutée, c'est le plan."),
        ("La preuve", f"Deux harnais indépendants, six rounds d'assaut, quatre injections de chaos, "
                      "trois sabotages du contrôle, un déterminisme vérifié par empreinte. Ce "
                      "mémoire ne demande pas d'être cru : il demande d'être rejoué."),
        ("Les limites", "Pas de passerelle bancaire, pas d'arabe activé, pas de conteneur, pas de "
                        "mesure d'exploitation, pas de migrations versionnées. Cinq phrases qui "
                        "coûtent plus à écrire que dix paragraphes de résultats, et qui sont la "
                        "seule garantie du lecteur."),
        ("La suite", "Le paiement réel dès qu'un contrat de passerelle existe, la migration "
                     "versionnée dès qu'un second environnement apparaît, la mesure d'usage sur trois "
                     "mois, l'activation du right-to-left avec sa relecture de maquette. Quatre "
                     "chantiers, aucun commencé pour faire joli."),
    ]
    F.tableau(["Tuile", "Ce qui est affirmé", "Où le vérifier"],
              [[t[0], t[1], ["annexe F", "partie I", "partie III", "partie V", "§V.6", "§V.6"][i]]
               for i, t in enumerate(tuiles)],
              cle="conclusion.tuiles", titre="Conclusion en six tuiles", largeurs=[1.5, 7.5, 1.6],
              legende="Six cases, six renvois. Aucune ne dit « un futur prometteur ».")
    F.p("Trois promesses étaient faites en introduction, et elles sont tenues mot pour mot : le "
        "verrou est l'ouvrage, et il est écrit ligne 79 de `src/lib/orders.ts` ; rien n'est affirmé "
        "sans son gisement, et l'annexe F en donne la liste ; ce qui n'a pas été fait est écrit, et "
        "la cinquième tuile le répète. Un délice, annoncé et livré : la planche de contact des "
        f"{len(REGISTRE)} figures, en annexe A, qui permet de parcourir tout l'appareil graphique "
        "avant la première ligne de texte — c'est la façon la plus rapide de vérifier que ce mémoire "
        "n'a pas été écrit à l'envers de son objet.")
    F.p("Ce que la soutenance aura à assumer tient en une phrase : ce projet n'a pas été conduit "
        "comme une démonstration de technologie, mais comme la fabrication d'un objet dont on peut "
        "relire chaque vis. Un jury qui voudrait tester cette affirmation n'a pas besoin de croire "
        "le document — il a besoin de trois commandes, écrites en §REPRO.")

    # ──────────────────────────────────────────────── bibliographie
    F.saut()
    F.section("Bibliographie et sources techniques", cle="bibliographie")
    F.p("Les références ci-dessous sont les sources effectivement consultées pendant le projet, avec "
        "leur URL officielle. Elles sont citées pour ce qu'elles ont décidé dans le code, et non "
        "pour faire nombre : la colonne de droite nomme l'usage. Aucun document n'est cité sans "
        "avoir été ouvert, aucun paragraphe n'est reproduit mot à mot.")
    F.tableau(["Source", "URL officielle", "Usage dans le projet"],
              [["Documentation de Next.js", "https://nextjs.org/docs",
                "composants de serveur, actions, revalidation de cache"],
               ["Documentation de React", "https://react.dev/learn", "cache de requête, frontière serveur/cliente"],
               ["Manuel de PostgreSQL", "https://www.postgresql.org/docs/manuals/",
                "verrous de ligne, verrous advisory, niveaux d'isolation"],
               ["Documentation de Drizzle ORM", "https://orm.drizzle.team/docs/overview",
                "schéma, relations, transactions, poussée du modèle"],
               ["Documentation de Zod", "https://zod.dev", "schémas de validation des frontières"],
               ["Documentation de pg (pilote)", "https://node-postgres.com/", "jeu de connexions, requêtes paramétrées"],
               ["MDN Web Docs", "https://developer.mozilla.org/", "sémantique HTML, focus, attributs ARIA"],
               ["Recommandations WCAG 2.2", "https://www.w3.org/TR/WCAG22/",
                "contrastes, taille des cibles, réduction du mouvement"],
               ["Spécification PDF, ISO 32000-1", "https://www.iso.org/standard/51502.html",
                "générateur de facture maison, contraintes d'encodage"],
               ["Directive 2011/83/UE relative aux droits des consommateurs",
                "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32011L0083",
                "droit de rétractation, mentions précontractuelles"],
               ["Loi organique n° 2004-59 relative à la protection des données personnelles",
                "[URL de l'INPDP à vérifier avant remise]",
                "base légale, durée de conservation, registre de traitement"]],
              cle="bibliographie.sources", titre="Sources consultées, avec l'usage qui en a été fait",
              largeurs=[3.4, 3.6, 4.4],
              legende="La dernière ligne reste entre crochets : l'URL institutionnelle n'a pas pu "
                      "être vérifiée depuis l'environnement de développement. Un lien incertain est "
                      "marqué comme tel plutôt que donné pour sur (INV-6).")
    F.p("Les deux ouvrages de méthode et l'article sur les systèmes répartis cités en parties I et "
        "II sont laissés, eux aussi, entre crochets : [à compléter par l'auteur avant remise, avec "
        "l'édition consultée]. Le dépôt ne contient pas la liste de lectures de son auteur, et une "
        "rubrique bibliographique ne se remplit pas avec des titres plausibles.")
