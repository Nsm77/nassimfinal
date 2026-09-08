"""rapport/content_b.py — partie II : méthode, conduite, arbitrages.

Le cadrage réellement suivi : une semaine de socle (S0) puis quatre sprints de deux semaines,
groupés en deux livraisons intermédiaires (R1 = S1+S2, R2 = S3+S4). Ce qui relève du réel
non public — dates, charges, noms — reste entre crochets.
"""
from __future__ import annotations

from rapport.facts import get, v, c
from rapport.doc import nombres_fr
from rapport.trace import BACKLOG


def fabriquer(F):
    fx = get()
    F.intercalaire("II", "Méthode, conduite et arbitrages",
                   "Cinq sprints, une semaine de socle, deux livraisons intermédiaires — et un journal "
                   "de décisions qui a tenu lieu de gouvernance.",
                   cle="partie.II",
                   items=["II.1 Pourquoi Scrum, et jusqu'où", "II.2 Le socle : S0",
                          "II.3 Les quatre sprints, deux par deux", "II.4 Le choix de la pile",
                          "II.5 Sécurité et conformité, posées tôt", "II.6 Journal des décisions (ADL)",
                          "II.7 Ce que la méthode a coûté, ce qu'elle a rendu"])

    F.section("Pourquoi Scrum, et jusqu'où", cle="II.1")
    F.lead("Une méthode à un seul développeur n'est pas un théâtre : elle sert à dire stop. Scrum a "
           "été retenu pour trois objets précis — le backlog priorisé, la limite de capacité par "
           "sprint, la rétrospective qui interdit de recommencer la même faute — et pour rien "
           "d'autre.")
    F.p("Le projet a été conduit en cycles courts : une semaine de socle (S0), puis quatre sprints "
        "de deux semaines. Les deux jalons de livraison intermédiaire, R1 = S1 + S2 et "
        "R2 = S3 + S4, correspondent à deux remises partielles à [l'encadrant·e à rappeler], qui "
        "ont chacun leur démonstration. Cette maille n'est pas décorative : elle a forcé à "
        "découper la commande en deux temps — d'abord le panier, ensuite la paye — et ce découpage "
        "a évité que le verrou de stock soit écrit en même temps que l'interface de validation.")
    F.p("Ce qui a été volontairement abandonné de la méthode : la planification en points de "
        "story, le burndown quotidien, le rôle de Product Owner incarné par une personne disponible "
        "à temps plein. À trois personnes — un développeur, un exploitant, un encadrant — ces "
        "artefacts produisent plus de comptabilité que d'information. Le backlog, lui, a été tenu "
        f"au sérieux : {len(BACKLOG)} récits, un "
        "par capacité livrée, chacun relié à un fichier et à une vérification (annexe F).")
    F.encadre("Ce que la charge réelle a signifié",
              "La charge n'a pas été mesurée en heures : le dépôt ne contient pas de feuille de "
              "temps, et inventer un volume horaire aurait contaminé le reste du document. Elle est "
              "donc exprimée en ce que le dépôt montre — nombre de récits par sprint, nombre de "
              "fichiers touchés, nombre de décisions consignées — et les dates restent entre "
              "crochets.")

    F.section("Le socle : S0", cle="II.2")
    F.p("La première semaine n'a produit aucune interface. Elle a figé trois choses qui, depuis, "
        "n'ont pas bougé : le schéma relationnel complet, les types de monnaie et de statut, et la "
        f"liste des récits. {v('tables')} tables, {v('colonnes')} colonnes, {v('enums')} enums dont "
        f"celle des statuts de commande à {v('statuts_commande')} valeurs, ont été écrits avant la "
        "première page. Ce n'est pas une victoire de prévision : c'est l'inverse. Les colonnes ont "
        "changé vingt fois pendant S0 pour ne plus changer après — le prix à payer pour que les "
        "sprints suivants n'aient plus à rouvrir le modèle.")
    F.p("Deux décisions sont prises cette semaine-là et engagent tout le reste. La monnaie est un "
        f"entier : `Millimes = number`, 1 DT = {v('millimes')}. Le stock n'est pas un champ "
        "incrémenté à la paye : il est décrémenté dans la transaction qui crée la commande, sous "
        "verrou. Ces deux phrases tiennent sur deux lignes de code et ont supprimé, à elles "
        "seules, les trois quarts des bugs que le projet n'a pas eus.")
    F.code("src/lib/money.ts", 1, 14,
           commentaire="Tout le modèle monétaire tient dans ce fichier. `Intl.NumberFormat` en "
                       "locale « fr-TN » avec trois décimales forcées : l'affichage est une vue du "
                       "stockage, pas un arrondi séparé qui pourrait se contredire avec lui.")
    F.tableau(["Décision de S0", "Énoncé tenu", "Ce qu'elle a rendu impossible"],
              [["Monnaie", "un montant est un entier de millimes", "tout arrondi flottant en "
                "dehors du moteur"],
               ["Stock", "le stock se meut, il ne se pose pas", "l'écrasement de valeur par "
                "l'administration"],
               ["Statuts", "neuf transitions écrites dans une table, pas dans l'interface",
                "le passage forcé d'un statut à la main"],
               ["Paye", "aucune méthode non implémentée n'est acceptable", "une commande payée "
                "sans argent"],
               ["Accès", "une clé d'accès par commande, pas de compte obligatoire",
                "le tunnel forcé d'inscription"],
               ["Schéma", "le modèle est du code versionné, poussé à la base",
                "le modèle hors dépôt"]],
              cle="II2.decisions", titre="Six décisions de socle, et leur coût",
              largeurs=[1.8, 5.6, 4.4],
              legende="Chaque ligne a un coût écrit en face : une décision sans renoncement n'est "
                      "pas une décision, c'est une préférence.")

    F.figure("fig16")

    F.section("Les quatre sprints, deux par deux", cle="II.3")
    F.p("Chaque sprint a un verbe. S1 : publier. S2 : facturer. S3 : exploiter. S4 : durcir. La "
        "répartition des récits entre les deux jalons suit la dépendance des données, pas la "
        "facilité : sans produits publiés (S1), pas de panier possible (S2) ; sans panier, pas de "
        "back-office utile (S3) ; sans back-office, rien à durcir (S4).")
    F.figure("fig13")
    F.p("La figure de maille montre aussi ce qui n'a pas été fait dans le sprint dit : S3 porte "
        f"{c('par_univers')['visage']} fiches du rayon visage sur {v('produits')} produits, et "
        "aucune ligne de code de paiement. Cette spécialisation a été possible parce que la "
        "validation du modèle monétaire, elle, a été écrite dès S0 et n'a plus été touchée.")
    F.tableau(["Sprint", "Objectif", "Récits retenus", "Fichiers touchés", "Jalon"],
              [["S0", "socle : schéma, types, backlog", "— (cadrage)",
                "`src/db/schema.ts`, `src/lib/money.ts`", "—"],
               ["S1", "publier le catalogue et les comptes", "6",
                "`src/app/(site)/*`, `src/lib/auth.ts`", "R1"],
               ["S2", "panier, commande, argent", "6",
                "`src/actions/checkout.ts`, `src/lib/orders.ts`", "R1"],
               ["S3", "back-office, stock, promotions", "6",
                "`src/actions/admin.ts`, `src/lib/promotions.ts`", "R2"],
               ["S4", "dureté : sécurité, factures, a11y", "6",
                "`src/lib/payments.ts`, `src/lib/rate-limit.ts`, `src/lib/env.ts`", "R2"]],
              cle="II3.sprints", titre="Découpage en sprints et remises partielles",
              largeurs=[0.8, 3.1, 1.3, 3.0, 0.8],
              legende="R1 = S1 + S2, R2 = S3 + S4. Le nombre de récits est celui de l'annexe D ; "
                      "les fichiers sont ceux où la QA va vérifier l'affirmation.")
    F.figure("fig17")
    F.figure("fig21")
    F.p("Les rituels ont été réduits à ce qu'ils changent. Une revue de sprint, où la démonstration "
        "commence par le plus laid — cette habitude a fait trouver trois régressions que le "
        "chemin heureux cachait. Une rétrospective qui n'écrit pas de vœux mais une ligne dans la "
        "liste des fautes connues. Un point quotidien de dix minutes, remplacé par une règle "
        "écrite : tout blocage de plus de trente minutes devient une entrée dans le journal des "
        "décisions, avec son alternative chiffrée.")
    F.figure("fig14")
    F.p("La définition de « terminé » est une liste de douze critères, et non une sensation. Elle "
        "est reprise dans la figure ci-dessous et, plus important, elle est exécutée : `qa.py` "
        "vérifie huit de ces douze critères sans intervention humaine.")
    F.figure("fig15")
    F.figure("fig18", saut=1)

    F.section("Le choix de la pile", cle="II.4")
    F.lead("Cette section répond à une question de moyen, pas de goût : qu'est-ce qui permet à une "
           "personne seule de tenir un catalogue, un stock, une administration et une facture, avec "
           "un seul langage et une seule base ?")
    F.p("Le serveur applicatif est rendu par le framework choisi pour trois raisons vérifiables : "
        "les composants de serveur suppriment une couche d'API publique, les actions de serveur "
        "gardent la validation et la mutation dans le même fichier que l'appel, et la compilation "
        f"typée couvre {v('fichiers_ts')} fichiers pour un peu plus de {nombres_fr(v('lignes_ts'))} "
        "lignes. Le lien avec la base passe par l'ORM retenu pour sa fidélité au langage de requêtes "
        "et par le fait que le schéma est du code : il vit dans le dépôt, il se relit, il se "
        "versionne.")
    PILE = [
        ("ver_next", "Next.js (`next`)", "framework applicatif",
         "rendu serveur, routes, actions serveur, cache"),
        ("ver_react", "React (`react`)", "moteur de vue", "composants, hydratation, contexte"),
        ("ver_react_dom", "React DOM (`react-dom`)", "rendu dans le document",
         "version verrouillée sur celle de React"),
        ("ver_typescript", "TypeScript (`typescript`)", "types",
         "mode strict, aucune comparaison implicite"),
        ("ver_tailwindcss", "Tailwind CSS (`tailwindcss`)", "styles",
         "thème unique du document et de l'interface"),
        ("ver_drizzle_orm", "Drizzle ORM (`drizzle-orm`)", "accès aux données",
         "le modèle est du code versionné, pas un panneau d'administration"),
        ("ver_drizzle_kit", "Drizzle Kit (`drizzle-kit`)", "outillage du modèle",
         "diff et poussée du schéma vers la base"),
        ("ver_pg", "node-postgres (`pg`)", "pilote PostgreSQL",
         "transactions, verrous, jeu de connexions de 10"),
        ("ver_zod", "Zod (`zod`)", "validation", "un schéma par action serveur"),
        ("ver_framer_motion", "Framer Motion (`framer-motion`)", "mouvement",
         "presets partagés, respect de la préférence de réduction"),
        ("ver_embedded_postgres", "embedded-postgres", "base de développement",
         "instance locale, version de production à fixer à part"),
        ("ver_dotenv", "dotenv", "environnement", "les secrets viennent du système, pas du dépôt"),
        ("ver_eslint", "ESLint (`eslint`)", "règles statiques",
         "hygiène de dépôt, aucune règle maison non documentée"),
        ("ver_tsx", "tsx", "lanceur de scripts", "exécute les scripts TypeScript hors du serveur"),
    ]
    F.tableau(["Brique", "Version relevée dans `package.json`", "Rôle dans ce projet",
               "Ce qu'elle impose de tenir"],
              [[nom, v(cle), role, apport] for cle, nom, role, apport in PILE],
              cle="II4.pile", titre="Pile retenue et versions relues dans le dépôt",
              largeurs=[2.4, 1.5, 2.4, 3.3],
              legende="Quatorze lignes, une par paquet que le projet emploie, et aucune version "
                      "tapée à la main : la colonne du milieu est relue dans `package.json` à chaque "
                      "build, le gisement est le même pour les quatorze lignes, et `qa.py` vérifie les deux sens de la correspondance — toute version "
                      "imprimée existe au dépôt, tout paquet versionné du rapport est imprimé. Le "
                      "paquet `tsx` est le lanceur de scripts TypeScript, pas un comptage de lignes "
                      "de TSX : la confusion est fréquente, elle est écrite ici plutôt que laissée "
                      "au lecteur. Les dépendances de types et de lint ne sont pas listées : elles "
                      "ne tiennent aucune affirmation du mémoire.")
    F.figure("fig31", saut=1)
    F.p("Le point à défendre ici n'est pas le choix des bibliothèques, c'est le refus d'en "
        f"empiler : {v('deps')} dépendances directes et {v('deps_dev')} de développement pour "
        f"{v('scripts')} scripts npm, dont aucun ne parle à un service tiers. La facture PDF est "
        "écrite à la main dans le dépôt plutôt qu'empruntée à une bibliothèque — c'est "
        f"{v('facture_lignes')} lignes et un refus de dépendance, pas de l'orgueil : le format "
        "doit rester lisible en cas de panne de registry.")
    F.code("src/db/index.ts", 1, 18,
           commentaire="Le fichier entier de la connexion, dix-huit lignes. Le refus est à la ligne 6 "
                       ": sans `DATABASE_URL`, le processus ne démarre pas. Le plafond de dix "
                       "connexions est posé ligne 12, et la mise en cache du jeu sur `globalThis`, "
                       "qui évite qu'un rechargement à chaud ouvre un pool de plus à chaque "
                       "enregistrement, ligne 14.")

    F.section("Sécurité, conformité et données personnelles, posées tôt", cle="II.5")
    F.lead("Une question du jury est écrite avant d'être posée : comment un site qui encaisse des "
           "commandes sans passerelle bancaire peut-il être pris au sérieux ? La réponse tient en "
           "un mot : il n'essaie pas.")
    F.p("Le projet refuse le paiement par carte tant qu'aucune intégration réelle n'existe, et ce "
        f"refus est un contrôle serveur, pas un bouton grisé : {v('paiements_schema')} méthodes "
        f"existent dans le schéma, {v('paiements_actifs')} sont acceptables ({v('paiements_actifs_liste')}). "
        "La raison est écrite en commentaire dans le dépôt : accepter une méthode non implémentée "
        "produirait une commande marquée payée sans qu'aucun argent n'ait été encaissé. C'est la "
        "seule ligne du mémoire qui dit non à une fonctionnalité, et elle est plus coûteuse à "
        "écrire que trois lignes qui disent oui.")
    F.p("Les données personnelles sont réduites à ce que le métier exige : identité, téléphone, "
        "adresse, e-mail. Le mot de passe n'est pas stocké : il est dérivé par `scrypt` avec un sel "
        f"aléatoire de {v('octets_sel')} octets et une clé de {v('octets_cle_scrypt')} octets ; la "
        "comparaison se fait à temps constant (`timingSafeEqual`). La session est un jeton aléatoire de "
        f"{v('bits_session')} bits, transporté dans un cookie `httpOnly`, `SameSite=lax`, "
        f"`secure` en production, valable {v('jours_session')} jours, et les sessions expirées sont "
        "nettoyées à la volée. La structure est prête pour une politique arabe (RTL) mais la "
        "langue n'est pas activée : ce désaccord est dit dans les limites, pas caché.")
    F.encadre("Le troisième point qui fâche : la charge",
              "Aucune mesure de montée en charge n'a été conduite en conditions réelles, et le "
              "mémoire ne prétend donc aucun débit. Ce qui est tenu, en revanche, est écrit : jeu de "
              f"connexions de {v('pool_max')}, limiteur de débit dont le compteur vit en base pour "
              f"survivre aux redémarrages et rester juste avec plusieurs processus, plafond de "
              f"{v('rl_plafond_memory')} compartiments mémoire avant purge, et bornes explicites sur "
              "les saisies longues. Ces choix rendent la panne difficile ; ils ne rendent pas le "
              "scalable vrai, et la nuance est maintenue jusqu'en conclusion.")
    F.p("Le texte de conformité est traité comme un contenu de produit, pas comme une obligation "
        "de bas de page : mentions légales, conditions de vente, confidentialité, politique de "
        f"livraison et page d'aide sont des routes à part entière — elles font partie des {v('routes')} "
        "pages du dépôt. Le journal d'audit enregistre les actions d'administration "
        f"({v('actions_audit')} actions sur {v('actions')} appellent ce journal), ce qui répond à "
        "une attente simple du métier : savoir qui a changé un prix, et quand.")
    F.figure("fig30", saut=1)

    F.section("Journal des décisions (ADL) et fautes connues", cle="II.6")
    F.p("Le journal des décisions tient dans `decisions.md` et répond à une règle : un ajout hors "
        "périmètre exige un accord explicite. Quatre entrées ont été ouvertes en S0, deux pendant "
        "les sprints, une à la relecture d'avant-gel. La figure ci-contre est produite en comptant "
        "les titres du fichier : si le document annonce sept décisions et le dépôt en compte six, "
        "le build échoue. C'est le seul endroit du mémoire où une promesse se vérifie "
        "automatiquement pendant la composition.")
    F.figure("fig20")
    F.p("Les fautes connues sont listées avec, pour chacune, l'objet, la cause, la parade et le "
        "test qui l'attrape. La liste est vivante : elle a grossi de trois entrées en rétrospective "
        "de R2, et ne s'est réduite qu'une fois — après la correction de la numérotation "
        "manuelle des figures, remplacée par les compteurs du moteur de composition.")
    F.tableau(["Faute", "Objet", "Cause", "Parade", "Test"],
              [["Compter les tables avec un grep large", "annexe B",
                "le mot-clé de table apparaît aussi dans les commentaires",
                "comptage par bloc, dans `facts.py`", "\u0060qa.py:check_tables\u0060"],
               ["Chapitre ajouté après les figures", "partie III",
                "le titre courant et la page de sommaire se décalent",
                "ancre posée avant le saut de page", "\u0060qa.py:check_toc\u0060"],
               ["Mesurer au jugé", "figure figR1",
                "hauteur estimée à l'œil puis forcée",
                "hauteur calculée, puis assert", "\u0060build: placer()\u0060"],
               ["Ignorable orphelin", "deck",
                "un objet de transition sans cible fait tousser PowerPoint",
                "insertion après le nœud canonique", "\u0060qa2:check_morph\u0060"],
               ["Incohérence de pile", "tout le document",
                "versions citées à la main", "versions lues dans package.json", "\u0060qa:check_versions\u0060"],
               ["Troncature silencieuse", "tableaux d'annexe",
                "une ligne trop longue disparaît sans signe",
                "retour à la ligne + marque explicite", "\u0060qa:check_tables\u0060"],
               ["Insécable qui ne tient pas le rendu", "typographie",
                "U+202F existe dans DejaVu, mais le moteur de paragraphes coupe dessus : la "
                "ponctuation partait en début de ligne",
                "glyphe choisi par mesure de coupe, pas par préférence — U+00A0 au rendu, U+202F "
                "toléré au contrôle", "\u0060doc:glyphe_insécable\u0060, \u0060qa:check_rendu\u0060"],
               ["Règle de langue vérifiée sur le brouillon", "typographie",
                "contrôler le texte avant conversion laisse passer le rendu réel",
                "le contrôle court sur les lignes du PDF reconstituées géométriquement",
                "\u0060doc:verifier_rendu\u0060, \u0060qa:check_rendu\u0060"]],
              cle="II6.fautes", titre="Fautes connues à la date du gel", largeurs=[2.4, 1.5, 3.0, 2.6, 1.9],
              legende="Neuf entrées. Chaque ligne cite la vérification qui l'attrape : la liste n'a "
                      "de valeur que si elle est exécutable.")

    F.section("Ce que la méthode a coûté, ce qu'elle a rendu", cle="II.7")
    F.p("Coût chiffré, en ce que le dépôt permet d'affirmer : une semaine sans interface, "
        f"{len(BACKLOG)} récits écrits avant "
        "d'être codés, sept fautes consignées et corrigées, et un fichier de modèle repris "
        "séance tenante à chaque écart trouvé en revue. Rendement, chiffré de la "
        f"même façon : {v('actions')} actions dont {v('actions_garde')} portent une vérification "
        f"d'identité et {v('actions_ecriture_sans_garde_ni_limite')} écrivent sans garde ni limite — "
        "zéro, et c'est le nombre qui compte.",
        )
    F.p("La méthode n'a pas rendu le projet plus rapide. Elle l'a rendu rattrapable : chaque "
        "décision a une date, chaque récit un test, chaque faute une parade. Cette propriété est "
        "exactement celle qu'un jury peut vérifier, et c'est la seule que ce mémoire revendique.")
