"""rapport/content_a.py — liminaires, sommaire, introduction, partie I (cadrage).

Les liminaires sont courts parce qu'ils ne prouvent rien ; la preuve commence en I.4, quand le
document dit pourquoi il n'a pas pris la voie la plus facile.
"""
from __future__ import annotations

import re

from rapport.facts import get, v, c
from rapport.doc import nombres_fr, dt, INS

TITRE = "Cléopâtre — Espace Santé Beauté"
SOUS_TITRE = "Conception et réalisation d'une plateforme e-commerce pour une parapharmacie tunisienne"


def fabriquer(F):
    fx = get()
    # ──────────────────────────────────────────────── couverture (or + double logo dessinés par le gabarit)
    F.couverture([
        ("couv_sous", "[Prénom NOM de l'auteur]"),
        ("couverture", TITRE),
        ("couv_sous", SOUS_TITRE),
        ("couv_sous", f"Rapport de projet — année universitaire [2025–2026]"),
        ("couv_pied", f"Version scellée v1.0-final · Next.js {v('ver_next')} · React {v('ver_react')}"
                      f" · TypeScript {v('ver_typescript')} · PostgreSQL {v('ver_embedded_postgres')}"),
    ])

    # ──────────────────────────────────────────────── jury, dédicaces, remerciements
    F.section("Jury et mentions", cle="liminaires.jury")
    F.p("Le présent document est soumis à l'examen d'un jury composé comme suit : "
        "[Prénom NOM], président · [Prénom NOM], encadrant académique · [Prénom NOM], encadrant "
        "professionnel · [Prénom NOM], examineur. Les noms sont laissés entre crochets : ils "
        "relèvent de l'administration de l'établissement, et un mémoire ne se permet pas d'inventer "
        "un patronyme.")
    F.tableau(["Rôle", "Nom", "Établissement / organisme", "Validité"],
              [["Président", "[Prénom NOM]", "[établissement]", "[  ]"],
               ["Encadrant académique", "[Prénom NOM]", "[département]", "[  ]"],
               ["Encadrant professionnel", "[Prénom NOM]", "Pharmacie Cléopâtre", "[  ]"],
               ["Examineur", "[Prénom NOM]", "[établissement]", "[  ]"]],
              cle="jury", titre="Feuille de jury", largeurs=[3, 2.4, 2.4, 1], nowrap=True,
              legende="Case à cocher à la soutenance ; le document ne présume pas du résultat.")

    F.section("Dédicaces", cle="liminaires.dedicaces")
    F.p("À [dédicace à écrire par l'auteur]. Cette page lui appartient : le logiciel est fait pour "
        "être examiné, les dédicaces non. Le dépôt, lui, se lit ligne par ligne.")

    F.section("Remerciements", cle="liminaires.remerciements")
    F.p("À l'équipe des deux officines — Ezzahra et Hammam-Lif — qui a accepté de saisir dans un "
        "outil neuf, en pleine journée de vente, et qui a dit trois choses désagréables qui ont "
        "empêché trois erreurs. À l'encadrant académique, qui a refusé les généralités. Aux "
        "relecteurs du harnais : ce document a été attaqué trente fois avant d'être imprimé, et "
        "les procès-verbaaux sont en annexe.")
    F.note("Convention d'écriture de ce mémoire : tout ce qui est entre crochets carrés est une "
           "donnée réelle que le dépôt ne contient pas — noms, dates administratives, chiffres "
           "d'exploitation. Tout ce qui n'en porte pas a été lu dans le code, avec son "
           "fichier et sa ligne. Cette règle est tenue jusqu'à la dernière page et vérifiée par "
           "l'invariant INV-6.")

    # ──────────────────────────────────────────────── sommaire + listes cliquables + abréviations
    F.saut()
    F.table_des_matieres()
    F.liste_des_planches()
    F.liste_des_tableaux()

    F.section("Abréviations et sigles employés", cle="abreviations")
    F.tableau(["Sigle", "Développement", "Première occurrence"],
              [["PFS", "PostgreSQL Filesystem — le système de fichiers natif de la base", "§II.4"],
               ["ORM", "Object-Relational Mapping — Drizzle, ici", "§III.4"],
               ["UC", "Use Case — cas d'usage", "§III.1"],
               ["RACI", "Responsible, Accountable, Consulted, Informed", "§II.5"],
               ["ADL", "Audit Decision Log — journal des décisions de conception", "§II.6"],
               ["QA", "Quality Assurance — le harnais double de vérification", "§V.2"],
               ["INV", "Invariant — propriété vérifiée à chaque build", "§V.1"],
               ["SLA", "Service Level Agreement — engagement de niveau de service", "§IV.5"],
               ["TTFB", "Time To First Byte", "§IV.5"],
               ["CSS", "Cascading Style Sheets", "§III.5"]],
              cle="abreviations", titre="Sigles du document", largeurs=[1, 5.6, 1.6],
              legende="Chaque sigle est écrit en long à sa première occurrence (règle de langue "
                      "vérifiée par `qa.py`).")

    # ──────────────────────────────────────────────── introduction
    F.saut()
    F.section("Introduction", cle="intro")
    F.lead("Ce mémoire ne raconte pas une idée : il rend compte d'un objet. Un catalogue de "
           f"{v('produits')} produits, {v('routes')} routes publiées, {v('actions')} actions serveur "
           f"et {v('tables')} tables est en service dans deux officines ; le document qui suit en "
           "donne la genèse, les arbitrage, et surtout les preuves.")
    F.p("Trois phrases, posées ici, qui engagent tout le reste. Première : le verrou n'est pas une "
        "option de robustesse, c'est l'ouvrage lui-même — un panier qui se contredit à la "
        "commande, un stock décrémenté deux fois, une remise calculée une fois sur la fiche et une "
        "autre fois dans le moteur ne sont pas des bugs, ce sont des promesses non tenues au "
        "client. Deuxième : dans ce projet, rien n'est affirmé sans son gisement ; chaque nombre "
        "de ce document a été relu dans le dépôt au moment de la composition, et le harnais le "
        "re-lit avant l'impression. Troisième : ce qui n'a pas été fait est écrit — la carte "
        "bancaire n'est pas branchée, l'arabe n'est pas activé, aucun conteneur n'est livré, et "
        "aucune de ces absences n'est présentée comme un choix de style.")
    F.p("Le plan suit le fil du travail réel. La partie I pose le métier et le problème, sans "
        "logiciel. La partie II rend compte de la méthode : cinq sprints dont un de cadrage, et "
        "les décisions qui ont tenu lieu de gouvernance. La partie III expose la conception — "
        "besoins, cas d'usage, données, sécurité, et les deux modèles qui structurent l'ensemble. "
        "La partie IV décrit la réalisation, extraits de code à l'appui, avec les chiffres "
        "d'exploitation du développement. La partie V livre ce qui distingue ce mémoire : la "
        "double vérification automatique, les assauts, les budgets tenus. Les annexes A à F "
        "donnent les inventaires complets et la traçabilité récit par récit.")
    F.p("Une convention encore, qui tient sur un paragraphe et se vérifie sur six-vingt pages "
        "(cf. §liminaires.remerciements) : les crochets carrés signalent ce qui relève du réel non "
        "contenu dans le dépôt. Cette discipline évite deux dérives également coûteuses : le "
        "chiffre inventé pour remplir une phrase, et le « [donnée à venir] » qui se transforme, à "
        "la relecture, en une approximation présentée comme un fait.")
    F.encadre("Registre double",
              "Chaque section est écrite pour deux lecteurs. Le premier n'a pas fait "
              "d'informatique : il trouve en début de section une phrase qui dit l'enjeu métier. Le "
              "second a relu le code : il trouve le fichier, la ligne, le garde-fou. Les deux "
              "registres ne se répètent pas — l'écart entre les deux est exactement la place du "
              "raisonnement d'ingénieur.")

    # ──────────────────────────────────────────────── PARTIE I
    F.intercalaire("I", "Le métier, le problème, la cible",
                   "Avant le logiciel : ce qu'une parapharmacie de deux comptoirs doit vendre, et ce "
                   "qui l'empêche de le faire à distance.",
                   cle="partie.I",
                   items=["I.1 Contexte de l'officine", "I.2 État de l'art du commerce de santé en ligne",
                          "I.3 Le problème, décomposé", "I.4 Pourquoi pas une place de marché",
                          "I.5 Cibles et indicateurs", "I.6 Périmètre, risques, arbitrages"])

    F.section("Contexte de l'officine", cle="I.1")
    F.p("Cléopâtre — Espace Santé Beauté est une parapharmacie de la banlieue nord de Tunis, sur "
        "deux sites : [adresse Ezzahra à rappeler] à Ezzahra et [adresse Hammam-Lif à rappeler] à "
        "Hammam-Lif. Le projet a été mené avec [l'exploitant, prénom à rappeler] ; l'effectif "
        "[nombre] personnes, dont un pharmacien responsable par site. Le panier moyen constaté en "
        "comptoir est [montant à relever sur la caisse], le fichier clients compte [nombre] fiches "
        "et la rotation du rayon solaire se concentre sur [nombre] semaines par an.")
    F.p("Deux caractères du métier commandent la conception. D'abord le conseil : une vente sur "
        "trois naît d'une question sur un type de peau, une interaction de traitement, un âge. "
        "Ensuite la contrainte d'argent : la monnaie tunisienne se pratique au millime — trois "
        "décimales — et aucune des bibliothèques de commerce les plus courantes ne le pense ainsi "
        "par défaut. Ces deux faits, vérifiés auprès de l'officine, ont éliminé plus de "
        "possibilités d'architecture que n'importe quelle préférence technique.")
    F.figure("fig01")
    F.p("Le projet a été décidé après un constat de terrain : le catalogue n'existait pas en "
        "ligne, la commande se faisait par message téléphonique, la disponibilité se vérifiait en "
        "rayon. Les trois fonctions à livrer en priorité se sont imposées d'elles-mêmes : "
        f"publier le catalogue ({v('produits')} références, {v('marques')} marques), permettre la "
        "commande sans compte avec paiement à la livraison, et rendre le stock crédible. Le reste "
        "— fiches conseils, suivi de colis, fidélité, back-office — est venu des sprints "
        "suivants, et non d'un cahier des charges rêvé.")
    F.sous("Ce qui distingue une parapharmacie d'un commerce en ligne", cle="I.1.1")
    F.p("Trois différences, chacune devenue une exigence de conception, sont rappelées au fil des "
        "sections. Le produit est réglementé : la composition doit être publiée, pas mise en "
        "avant — d'où une colonne `ingredients` et un bloc de lecture obligatoire sur la fiche. Le "
        "stock est partagé entre comptoir et net : un article vendu en rayon cinq minutes plus "
        "tôt n'est plus disponible en ligne, d'où le verrou de ligne au moment de la commande. Le "
        "prix est conseillé mais pas libre : les écarts d'un site à l'autre se justifient par le "
        "coût de la livraison et de la contre-remboursement, d'où un moteur de promotions qui "
        "assume des motifs de rejet lisibles.")
    F.figure("fig02")

    F.section("État de l'art du commerce de santé en ligne", cle="I.2")
    F.p("L'existant se partage en trois familles, et le mémoire les a toutes regardées avant de "
        "choisir. Les places de marché généralistes offrent l'audience et reprennent la relation "
        "client ; elles imposent le centime comme plus petite unité monétaire et un tunnel de "
        "paiement en carte. Les solutions de boutique hébergées (abonnement mensuel, thème, "
        "extensions payantes) offrent la vitesse et ajoutent au coût une dépendance de plateforme. "
        "Enfin les moteurs open source (WooCommerce et apparentés) offrent la propriété et "
        "emprisonnent le modèle de données dans une extension tierce — un prix en millimes y devient "
        "une colonne texte ou un filtre maison.")
    F.p("Les textes de référence sur le sujet sont cités en bibliographie, avec leur URL officielle "
        "et non une capture. Ce qui a été lu ici, littéralement : la documentation du cadre "
        "applicatif, les spécifications du langage, la documentation de l'ORM et du pilote de base, "
        "et les notices des fabricants pour les formulations. Aucun paragraphe de cette partie n'a "
        "été copié : le texte est écrit, les idées sont sourcées, et l'annexe F le montre.")
    F.tableau(["Famille de solution", "Coût d'entrée", "Propriété de la donnée", "Monnaie "
               "à trois décimales", "Délai de mise en service", "Ce qu'elle impose"],
              [["Place de marché", "commission sur vente", "plateforme", "non", "semaines",
                "tunnel de paye en carte, fiche produit normalisée"],
               ["Boutique hébergée par abonnement", "abonnement mensuel", "éditeur, export limité",
                "non", "jours", "thème, extensions payantes, tunnel standard"],
               ["Moteur open source générique", "hébergement seul", "exploitant", "mal",
                "semaines", "modèle de données de l'outil, extensions tierces"],
               ["Ce projet", "hébergement et temps de conception", "exploitant, base en clair chez "
                "lui", "oui", "cinq sprints", "aucune contrainte externe, toute la charge"]],
              cle="I2.comparaison", titre="Les quatre voies, jugées sur cinq critères",
              largeurs=[2.6, 2.0, 2.4, 2.0, 1.8, 4.0],
              legende="La ligne du projet n'est pas présentée comme supérieure : elle est présentée "
                      "comme celle dont le coût est intégralement à la charge de l'auteur, ce qui "
                      "est exactement la raison pour laquelle elle était acceptable pour un mémoire et "
                      "discutable pour une officine.")

    F.figure("fig11")

    F.section("Le problème, décomposé", cle="I.3")
    F.p("Le problème n'est pas « faire un site de pharmacie ». Il tient en une phrase : faire "
        "survivre le conseil et la justesse du stock à un canal où personne ne se rencontre. Ce "
        "déplacé crée trois familles de causes, cinq branches d'arêtes de poisson.")
    F.figure("fig07")
    F.p("Chaque branche se ferme par un mécanisme nommé plus loin : la monnaie par le type "
        "entier (fichier `src/lib/money.ts:1`), la confiance par la clé d'accès de commande "
        f"({v('bits_session')} bits, `src/lib/orders.ts`), l'exploitation par la table de "
        f"transitions ({v('transitions')} arcs autorisés), la réglementation par les mentions et "
        f"l'audit ({v('tables')} tables dont une de journal), l'équipe par le cadencement des "
        "sprints. La partie III les reprend un par un, avec la ligne de code qui les tient.")
    F.figure("fig08")
    F.figure("fig03", demie=True, right=True)
    F.p("La figure de gauche mérite un arrêt : elle mesure la couverture des besoins par le "
        "catalogue, et non la satisfaction client, qui relève de l'exploitation. Le choix de "
        f"{v('besoins')} besoins comme axe de navigation — plutôt que {v('sous_categories')} "
        f"sous-catégories techniques — vient d'une observation en officine : le client entre avec "
        "un mot du quotidien (« peau qui tire », « cheveux qui tombent »), jamais avec un nom de "
        "famille cosmétique. Le modèle de données suit cette phrase du quotidien par la table "
        "`concerns` et sa table de jointure.")

    F.section("Pourquoi pas une place de marché, et pas un abonnement mensuel", cle="I.4")
    F.lead("Cette section répond à la question qui sera posée en soutenance. Elle est donc écrite "
           "avant le code, avec ses trois objections, ses réponses, et ce que le projet a perdu en "
           "les tranchant.")
    F.p("Objection 1 — l'audience. Une place de marché apporte un trafic que le site n'aura pas "
        "seul. Réponse : le trafic d'une parapharmacie de banlieue est local et répétitif ; "
        "[nombre] pour cent des ventes en comptoir viennent de clients identifiés, chiffre à "
        "confirmer avec l'exploitant. Le canal en ligne ne cherchait donc pas à capter un inconnu, "
        "mais à ne plus perdre une commande le dimanche. Le projet a gagné trois jours de mise en "
        "service en renonçant aux places ; il a perdu l'audience, et l'annexe le dit.")
    F.p("Hypothèse de repli, écartée pour la même raison : une boutique Shopify. Le cahier "
        "d'intention du stage la nommait comme solution de repli ; le dépôt n'en contient aucune "
        "trace. La recherche de « shopify » dans `src/` renvoie zéro ligne, et aucune dépendance de "
        "`package.json` n'y ressemble. Cette section inscrit donc la demande, la recherche qui la "
        f"dément, et le motif du renoncement : {v('tables')} tables et {v('colonnes')} colonnes "
        "appartiennent au dépôt et se modifient à la main ; une boutique louée se modifie à la file "
        "d'attente d'un catalogue d'extensions. L'écart est consigné à l'annexe des limites, pas "
        "gommé.")

    F.p("Objection 2 — le prix et le stock. La petite unité monétaire d'une place est le centime, "
        "et l'inventaire y est une quantité globale. Ici, le prix est un entier de millimes et le "
        "stock est verrouillé à la commande, pas décrémenté à la paye. Ces deux mécaniques sont "
        f"absentes des offres à abonnement : les {v('promotions')} codes promo et leurs "
        f"{v('motifs_rejet_promo')} motifs de rejet sont écrits dans le dépôt, pas dans un tableau "
        "de bord loué. Un prix affiché non facturable, ce n'est pas une limite d'outil, c'est un "
        "litige.")
    F.p("Objection 3 — la propriété de la donnée. Un abonnement rend la base inatteignable, la "
        "modification conditionnelle à un catalogue d'extensions, et l'export dépendant d'un délai. "
        f"Le dépôt tient {v('tables')} tables avec leurs contraintes : une reconstruction depuis "
        "zéro tient dans trois commandes, décrites au §REPRO. C'est la seule assurance du mémoire "
        "qui ne dépende pas d'un tiers.")
    F.figure("fig05")
    F.encadre("Ce que le projet a perdu en choisissant",
              "Le choix du sur-mesure n'est pas gratuit : il a coûté le tunnel de paiement carte, la "
              "logistique de place de marché, les modèles de thème et une audience que deux "
              "boutiques de banlieue n'obtiennent pas seules. Ces absences sont écrites dans la "
              "conclusion et dans les niveaux de secours, pas tues par élégance.")

    F.section("Cibles et indicateurs", cle="I.5")
    F.p("Six objectifs ont été écrits avant le premier commit. Ils sont restés inchangés ; quatre "
        "ont été atteints, un reste mesurable mais pas encore mesuré, un est en attente de la "
        "production. Cette asymétrie est le prix d'un mémoire honnête : un document qui affiche six "
        "cases vertes n'a rien observé.")
    F.figure("fig06")
    F.p("Les indicateurs se séparent en deux familles, et la séparation est nette : d'un côté ce "
        "qui se calcule sur le dépôt, de l'autre ce qui exige la production. Aucun indicateur "
        "d'exploitation n'est deviné. Le tableau de bord technique est le suivant.")
    F.figure("fig09")
    F.sous("Zones et délais de livraison", cle="I.5.1")
    F.p(f"La livraison est le seul point du parcours où le logiciel touche le monde physique, et elle "
        f"est écrite en quatre chaînes : {v('delais_livraison')}. Le Grand Tunis, défini comme "
        f"{v('grand_tunis')} gouvernorats dans `src/lib/tunisia.ts`, obtient le délai court ; les "
        f"{v('gouvernorats')} autres sont servis en quarante-huit à soixante-douze heures. Neuf "
        f"gouvernorats seulement portent une liste de villes suggérées ({v('villes')} villes au "
        f"total), soit {v('gouvernorats_sans_villes')} gouvernorats où le client saisit sa ville "
        "librement. Cette dissymétrie est un choix de coût, pas un oubli : la liste complète des "
        "localités tunisiennes ne tient pas dans le périmètre, et une liste partielle présentée comme "
        "exhaustive aurait été un mensonge d'interface.")
    F.tableau(["Cas", "Règle écrite dans le dépôt", "Effet perçu"],
              [["Retrait en boutique", "« Retrait sous 2 h en boutique »",
                "le délai le plus court, et le seul sans transporteur"],
               ["Express, partout", "« Livraison sous 24 h »", f"frais de {dt(v('frais_express'))}"],
               ["Standard, Grand Tunis", "« Livraison 24–48 h »",
                f"frais de {dt(v('frais_standard'))}, franco dès {dt(v('seuil_franco'))}"],
               ["Standard, reste du pays", "« Livraison 48–72 h »", "mêmes frais, délai allongé"],
               ["Ville absente de la liste", "aucune suggestion, saisie libre",
                "le formulaire accepte, la livraison aussi"]],
              cle="I51.livraison", titre="Ce que le code dit de la livraison",
              largeurs=[2.6, 4.6, 4.4], nowrap=True,
              legende="Quatre délais, un seuil de franco, deux boutiques : c'est tout ce que le "
                      "logiciel promet. Le reste relève du transporteur, donc du réel, donc des "
                      "crochets.")
    F.tableau(["Indicateur", "Valeur relevée", "Comment l'obtenir", "Gisement"],
              [[f"{v('routes')} routes publiées", nombres_fr(v("routes")),
                "inventaire des fichiers page.tsx", "`src/app/**`"],
               [f"{v('actions')} actions serveur", nombres_fr(v("actions")),
                "fonctions exportées de src/actions", "`src/actions/*.ts`"],
               [f"{v('tables')} tables / {v('colonnes')} colonnes",
                f"{v('tables')} / {v('colonnes')}", "schéma Drizzle", "`src/db/schema.ts`"],
               [f"{v('index')} index et {v('cle_etrangeres')} clés étrangères",
                f"{v('index')} + {v('cle_etrangeres')}", "mêmes sources", "`src/db/schema.ts`"],
               [f"{c('images')} visuels produits vérifiés", nombres_fr(c("images")),
                "manifeste d'images", "`public/data/product-image-manifest.json`"],
               ["panier moyen réel", "[à relever]",
                "commandes de production, non fournies", "—"]],
              cle="I5.indicateurs", titre="Indicateurs structurels du dépôt et de l'exploitation",
              largeurs=[3, 1.5, 3, 2.4],
              legende="La dernière ligne est laissée entre crochets : le chiffre n'existe pas dans "
                      "le dépôt, il n'est donc pas écrit. Toute la ligne 6 disparaîtrait du document "
                      "si elle était inventée (INV-6).")

    F.section("Périmètre, risques, arbitrages", cle="I.6")
    F.p("Le périmètre retenu tient en trois zones : la vitrine et son moteur de recherche, la "
        "commande avec son stock et ses promotions, l'administration avec ses statuts et son "
        f"journal. Sont sortis du périmètre, après arbitrage : la gestion de trésorerie, la "
        "déclaration réglementaire des produits de santé, le réapprovisionnement automatique, "
        "l'application mobile native. Ces quatre retraits sont consignés comme décisions "
        "(§II.6), pas comme oublis.")
    F.figure("fig10")
    F.p("Les risques ont été listés avant le premier commit sous une forme inhabituelle : on a "
        "écrit comment le projet mourrait, puis on a cherché ce qui tuerait chaque cause. Les huit "
        "mortes possibles, et leurs tueurs exécutables, sont dans la figure ci-dessous ; chacun est "
        "relié à un verrou de la partie V, ce qui veut dire qu'un risque sans test associé n'a pas "
        "été retenu comme géré.")
    F.figure("fig12")
    F.sous("Qui fait quoi, et qui est informé", cle="I.6.1")
    F.tableau(["Rôle", "Qui", "Décide de", "Consulté pour", "Informé de"],
              [["Métier", "[exploitant, nom à rappeler]", "priorités du catalogue, prix, délais",
                "structure du panier", "tout jalon livré"],
               ["Encadrant académique", "[nom à rappeler]", "périmètre du mémoire, niveau de preuve",
                "plan des chapitres", "réunions de jalon"],
               ["Conception-réalisation", "[auteur]", "architecture, schéma, sécurité",
                "arbitrages de charge", "écarts constatés en revue"],
               ["Support de l'officine", "[équipe à nommer]", "corrections de contenu, disponibilité",
                "formation à l'administration", "refus de commande rencontrés"]],
              cle="I6.raci", titre="Matrice de responsabilités tenue pendant le projet",
              largeurs=[2.0, 2.6, 3.4, 3.0, 2.8],
              legende="Une matrice à quatre lignes vaut ce que valent les noms : les trois premiers "
                      "rôles sont entre crochets parce que le dépôt ne les contient pas.")
    F.encadre("Ce que le lecteur doit retenir de la partie I",
              "Le logiciel n'est pas né d'un désir de technologie : il est né de trois contraintes "
              "vérifiables — le millime, le stock partagé, le conseil sans écran. Chacune a éliminé "
              "des familles de solutions avant même la première ligne. C'est ce qui rend le reste du "
              "document lisible : on ne justifie pas un choix technique par un goût, on le justifie "
              "par une contrainte du métier.")
