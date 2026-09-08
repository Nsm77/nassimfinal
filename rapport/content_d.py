"""rapport/content_d.py — partie IV : réalisation, sprint par sprint, ce que le dépôt mesure.

Une partie de réalisation sans extraits de code est une plaquette. Les extraits sont pris aux
lignes exactes citées, avec leur fichier ; les chiffres sont relus par `facts.py` à chaque build.
"""
from __future__ import annotations

from rapport.facts import get, v, c
from rapport.doc import nombres_fr, dt
from rapport.mpl import REGISTRE


def fabriquer(F):
    fx = get()
    ms = v("manifest_types_source")
    F.intercalaire("IV", "Réalisation : quatre sprints, deux livraisons",
                   "Ce qui a été écrit, dans quel ordre, avec quels rejets, et ce que le dépôt en "
                   "dit aujourd'hui.",
                   cle="partie.IV",
                   items=["IV.1 S1 — publier le catalogue", "IV.2 S2 — facturer sans se tromper",
                          "IV.3 S3 — exploiter depuis le comptoir", "IV.4 S4 — durcir ce qui doit l'être",
                          "IV.5 Ce que le dépôt mesure", "IV.6 Ce que le projet a dû refuser"])

    F.section("S1 — publier le catalogue", cle="IV.1")
    F.lead("Sprint de publication : le catalogue entre en base, la vitrine devient lisible, et le "
           "stock cesse d'être une rumeur de rayon.")
    F.p(f"Les {v('produits')} produits ne viennent pas d'un export de caisse : ce sont "
        f"{v('produits')} lignes positionnelles d'un tableau littéral, `const P: P[]`, écrit à la "
        f"ligne {v('seed_tableau_produits')} de `src/db/seed.ts` — {v('lignes_seed')} lignes au "
        f"total, qui alimentent {v('tables_seed')} tables dont la jointure des besoins. Le choix "
        "d'un tableau en dur dans le script, plutôt qu'un fichier de données annexe, est "
        "assumé : il rend la préparation impossible à désynchroniser du typage, et l'import reste "
        "idempotent parce qu'il vide et recharge. C'est ce qui interdit l'accident classique du "
        "doublon de marque après trois essais.")
    F.figure("fig33")
    F.p("Le catalogue s'est heurté à un objet du monde réel : les visuels. Le dépôt ne peut pas "
        f"distribuer les photographies des marques ; il distribue un manifeste de "
        f"{v('manifest_entrees')} entrées, une par produit, qui déclare le chemin d'image, la "
        f"provenance et l'état de vérification : {v('manifest_verifyes')} entrées portent "
        f"`verified: true`, {v('manifest_approuves')} sont approuvées après relecture. Les "
        "provenances sont hétérogènes et le mémoire les nomme : "
        f"{ms.get('official-brand')} visuels officiels, {ms.get('verified-retailer')} relevés chez "
        f"un détaillant vérifié, {ms.get('generated-from-real-reference')} générés d'après "
        f"l'emballage réel, {ms.get('cleopatre')} pris en boutique. Un cas particulier est écrit "
        f"dans le fichier : {c('seuls_sans_image')} produits n'ont pas de visuel, et le composant "
        "retombe alors sur l'image d'univers au lieu d'afficher un cadre vide. Rien n'est caché, "
        "rien n'est inventé.")
    F.figure("fig38")
    F.p(f"Le catalogue est construit sur {v('endpoints')} points d'entrée d'API et une recherche "
        "insensible à la casse sur le nom, la marque et la description courte. La pagination est "
        f"calculée côté serveur : {v('catalogue_par_page')} articles par page par défaut, plafonnée "
        f"à {v('catalogue_par_page_plafond')} (`src/lib/catalog.ts:100`), ce qui rend impossible la "
        "page de mille lignes qu'un paramètre malveillant obtiendrait autrement. La visibilité "
        "publique passe par un seul filtre exporté, `publiclyVisible` "
        "(`src/lib/catalog.ts:14`) : le commentaire du fichier dit pourquoi — filtrer à la main à "
        "chaque point d'appel est la façon la plus sure de faire fuiter un produit en brouillon.")
    F.tableau(["Code", "Libellé", "Type", "Valeur", "Actif", "Sous-total minimum"],
              [[pr["code"], pr["label"], pr["type"], str(pr["value"]),
                "oui" if pr["active"] else "non", dt(pr["min"]) if pr["min"] else "—"]
               for pr in fx.promos],
              cle="IV1.promos", titre=f"Les {v('promotions')} codes de promotion du dépôt",
              largeurs=[2.2, 5.4, 1.6, 1.2, 1.0, 2.2], nowrap=True,
              legende="Cinq codes, dont un seul inactif. La colonne « valeur » vaut un pourcentage "
                      "pour un type percent, un montant en millimes pour un type montant fixe : le "
                      "moteur de promotion les traite par une seule fonction pure.")
    F.figure("fig34")
    F.code("src/app/(site)/produit/[slug]/page.tsx", 30, 6,
           commentaire="La fiche produit, au point de rupture : si le slug n'existe pas, `notFound()` "
                       "est appelé par le serveur (ligne 33), et non par un effet de bord en cliente. "
                       "Ce qui frappe à la mauvaise porte obtient une page 404, pas un panier vide.")

    F.section("S2 — facturer sans se tromper", cle="IV.2")
    F.lead("Le sprint qui a le plus écrit et le moins affiché : les trois quarts du code de S2 ne se "
           "voient pas, et c'est le but.")
    F.p("Le parcours de commande tient en quatre étapes (livraison, paye, confirmation, retour) et "
        f"{v('lignes_commande')} lignes dans un seul fichier : `src/lib/orders.ts`. Il contient "
        f"{v('lignes_locks')} verrous de ligne, un tirage de numéro borné à {v('tirages_numero')} "
        f"essais, une clé d'accès de {v('bits_session')} bits, un total recalculé en base ligne par "
        "ligne, et un refus explicite des méthodes de paye non implémentées. Le client ne voit "
        "qu'un résumé ; le serveur, lui, ne croit rien de ce que le navigateur affirme.")
    F.figure("fig35")
    F.p("Le point technique le plus contestable est ce recalcul du total en base : il rend la "
        "commande plus chère en lectures qu'un calcul en mémoire. Ce surcoût est le prix d'une "
        "garantie : le prix affiché dans le navigateur peut être faux (promotion expirée, stock vidé "
        "entre-temps), le prix écrit dans la base ne peut pas être autre chose que le prix vrai au "
        "moment du verrou. La facture, générée après coup, relit ces montants et ne les recalcule "
        "jamais.")
    F.code("src/actions/checkout.ts", 62, 12,
           commentaire="Le contrôle d'idempotence, en deux temps : la clé est d'abord cherchée en "
                       "base (`checkout.ts:57`), puis un verrou advisory transactionnel assis sur "
                       "son empreinte SHA-256 est pris (`:66`). Un double clic, une reprise de "
                       "réseau ou un onglet réveillé produisent la même commande, pas deux. "
                       "L'index unique de la colonne `idempotency_key` sert de dernier rempart si "
                       "deux requêtes traversaient le verrou.")
    F.figure("fig36")

    F.tableau(["Boutique", "Ville", "Adresse publiée", "Horaires"],
              [[st["name"], st["city"], st["address"], st["hours"]] for st in fx.stores],
              cle="IV1.boutiques", titre=f"Les {v('boutiques')} points de vente, tels que le dépôt les déclare",
              largeurs=[2.6, 1.6, 5.0, 4.0], nowrap=True,
              legende="Deux boutiques, deux adresses, deux jeux d'horaires, lus dans le script "
                      "d'ensemencement. Le téléphone figurant à côté dans le dépôt n'est pas "
                      "reproduit ici : un numéro utile au client ne l'est pas au mémoire.")
    F.p("Quatre articles de conseil sont publiés, chacun avec son temps de lecture : "
        + ", ".join(f"« {a['title']} » ({a['minutes']} min)" for a in fx.articles)
        + ". Le temps de lecture est une donnée saisie, pas calculée : "
          f"`{v('articles')}` articles, quatre étiquettes de rayon, et aucune catégorie vide.")
    F.section("S3 — exploiter depuis le comptoir", cle="IV.3")
    F.p(f"L'administration a été écrite en pensant au comptoir, pas au bureau : "
        f"{v('composants_admin')} fichiers de composants, aucun graphique décoratif, trois actions "
        f"par liste, {v('actions_admin')} actions serveur dont {v('actions_garde')} portent une "
        f"garde de rôle et {v('actions_audit')} écrivent dans le journal. Le stock ne se corrige "
        "pas en écrasant une valeur : il se corrige par mouvement, "
        f"{v('types_mouvement')} types enregistrés dans l'enum, ce qui rend le rayon réconciliable "
        "avec la base.")
    F.code("src/lib/orders.ts", 97, 6,
           commentaire="`recordMovement` : le stock est mouvementé, pas posé. La ligne 100 relit la "
                       "valeur après la mise à jour et lève si elle passe sous zéro : « Stock "
                       "insuffisant. ». C'est le code qui tient l'invariant, pas le schéma, et le "
                       "document le dit plutôt que de prêter à la base une vertu qu'elle n'a pas "
                       "reçue.")
    F.figure("fig37")
    F.p("Les promotions sont l'autre moitié du sprint : le back-office voit les "
        f"{v('promotions')} codes, leur plafond d'usage, leur échéance, et surtout leurs motifs de "
        "refus. Un code qui ne s'applique pas renvoie une raison en français, tirée de la table des "
        f"{v('motifs_rejet_promo')} motifs. Le personnel peut répondre au client sans ouvrir le "
        "code, et c'est la seule raison d'exister de cette table.")
    F.figure("fig40")
    F.tableau(["Écran d'administration", "Ce qu'il change", "Journalisé", "Garde"],
              [["produits", f"prix, stock, vedette, statut ({v('statuts_produit')} valeurs)", "oui", "ADMIN"],
               ["commandes", f"statut ({v('transitions')} transitions autorisées)", "oui", "ADMIN"],
               ["promotions", f"{v('promotions')} codes, plafonds, échéances", "oui", "ADMIN"],
               ["articles", "journal de la marque, publication", "oui", "ADMIN"],
               ["boutiques", "deux points de vente, horaires, transporteur", "oui", "ADMIN"],
               ["tickets", f"réponse client, statut ({v('statuts_ticket')} valeurs)", "non", "ADMIN ou SUPPORT"],
               ["avis", f"modération ({v('statuts_avis')} valeurs) et moyenne recalculée", "oui", "ADMIN"]],
              cle="IV3.admin", titre="Ce que l'administration peut vraiment faire",
              largeurs=[3, 5.2, 1.4, 2.0],
              legende="La ligne « tickets » est la seule non journalisée : une réponse n'altère pas "
                      "un montant. Cette exception est un choix assumé, inscrit à l'inventaire des "
                      "dettes (§V.4).")
    F.code("src/actions/admin.ts", 19, 18,
           commentaire="Le changement de statut de commande côté administration "
                       "(`updateOrderStatusAction`). Trois lignes détiennent le sprint : la garde de "
                       "rôle, la récupération de la ligne sous verrou, la demande de transition au "
                       "graphe autorisé. Le reste est de la mise à jour de forme.")

    F.section("S4 — durcir ce qui doit l'être", cle="IV.4")
    F.p("Le dernier sprint n'ajoute aucune fonction. Il ferme trois portes : configuration, limites "
        "de débit, secrets. C'est le sprint le moins visible en démonstration et le seul dont "
        "l'absence aurait été punie en production.")
    F.figure("fig41")
    F.code("src/lib/rate-limit.ts", 5, 10,
           commentaire="L'en-tête du module, qui est aussi sa justification : le compteur vit en "
                       "base pour être partagé entre instances et survivre aux redémarrages, parce "
                       "qu'un cache par processus ne limite rien dès qu'il y a deux ouvriers. Le "
                       f"plafond mémoire de {v('rl_plafond_memory')} compartiments, lui, borne la "
                       "dégradation quand la base est injoignable.")
    F.figure("fig52")
    F.p(f"L'accessibilité a été traitée comme un défaut de conception, pas comme un audit final. Le "
        f"dépôt compte {v('boutons')} éléments interactifs natifs dans les composants, "
        f"{v('aria_label_total')} libellés explicites portés par `aria-label`, et "
        f"{v('svg_decoratifs')} icônes décoratives marquées `aria-hidden` sur {v('svg_total')} "
        "balises `svg` de composants — le solde est porteur de sens et accompagné d'un texte. Les "
        "contrastes de la palette sont mesurés (annexe A) et aucune couleur ne porte une "
        "information seule : un statut se lit par son libellé, sa forme et sa position.")
    F.figure("fig53")
    F.p(f"Le mouvement est réglé par {v('presets_motion')} presets dans un seul fichier, "
        f"{v('motion_transition')} transitions déclarées, de "
        f"{nombres_fr(v('motion_durees_s')[0], decimales=2)} s à "
        f"{nombres_fr(v('motion_durees_s')[-1], decimales=2)} s. La réduction de mouvement demandée "
        "par le système est honorée par une règle CSS globale — un seul fichier, "
        "`src/app/globals.css:161`, qui ramène durée d'animation, durée de transition et leurs "
        f"retards à {nombres_fr(v('reduction_mouvement_duree_ms'), decimales=2)} ms. Ce qu'elle "
        "n'éteint pas : les presets de la bibliothèque de mouvement, pilotés "
        f"en JavaScript, ne consultent pas `useReducedMotion` ({v('reduction_mouvement_js')} "
        "occurrence dans le code). Cette limite est écrite au §V.6, et non gommée de la phrase.")
    F.sous("Inventaire des actions et de leurs garde-fous", cle="IV.4.1")
    F.p("La matrice ci-dessous est le document de sécurité du projet : une ligne par fonction "
        "d'action exportée, une colonne par garde-fou recherché dans le corps de la fonction — "
        "validation de schéma, garde de rôle, limite de débit, vérification d'origine, transaction, "
        "verrou de ligne, borne de saisie, journal d'audit, revalidation de cache, écriture en base. "
        "Elle est générée par `facts.py` et relue par la QA, ce qui la rend plus sure qu'une "
        "prose qui jurerait de la même chose.")
    F.tableau(["Action", "Fichier", "Ligne", "Zod", "Garde", "Débit", "Origine", "Transaction",
               "Verrou", "Borne", "Audit", "Cache", "Écrit", "Lignes"],
              [[a["name"], a["file"].split("/")[-1], str(a["line"]),
                *["oui" if a[k] else "—" for k in ("zod", "guard", "rate", "origin", "tx", "lock",
                                                    "borne", "audit", "reval", "write")],
                str(a["lines"])] for a in fx.actions],
              cle="IV4.actions",
              titre=f"Les {v('actions')} actions serveur, garde-fou par garde-fou",
              largeurs=[3.2, 1.7, 0.8, 0.7, 0.8, 0.7, 0.9, 1.4, 0.8, 0.8, 0.8, 0.8, 1.1, 0.9],
              nowrap=True, cesser=30,
              legende="Trente lignes, quatorze colonnes, aucune case cochée à la main : la détection "
                      "est transitive aux auxiliaires du même fichier, sans quoi trois actions "
                      "paraîtraient non gardées alors qu'elles appellent la garde.")
    F.encadre("Pourquoi S4 n'a pas été fusionné dans S3",
              "Une raison de conduite, pas technique : un sprint de durcissement mélangé à un sprint "
              "de fonctionnalités se termine toujours par « on le fera après ». La séparation a "
              "permis de livrer R2 avec trois portes fermées et de dire, en revue, laquelle restait "
              "ouverte — le chiffrement au repos de la base, hors périmètre, écrit aux limites.")

    F.section("Ce que le dépôt mesure", cle="IV.5")
    F.p("Cette section ne raconte pas, elle relève. Les chiffres ci-dessous sont lus dans le dépôt au "
        "moment de la composition du document ; la même phrase, écrite en janvier, aurait été fausse "
        "de deux lignes.")
    F.tableau(["Grandeur", "Valeur", "Comment elle est obtenue"],
              [["fichiers TypeScript", nombres_fr(v("fichiers_ts")), "dénombrement de src/**"],
               ["lignes totales", nombres_fr(v("lignes_ts")), "somme des lignes non vides"],
               ["dont interface", nombres_fr(v("lignes_tsx")), "fichiers .tsx"],
               ["dont logique", nombres_fr(c("par_dossier")["lib"] + c("par_dossier")["actions"]),
                "src/lib + src/actions"],
               ["dont schéma", nombres_fr(v("lignes_schema")), "src/db/schema.ts"],
               ["requêtes SQL brutes", nombres_fr(v("sql_brut")), "morceaux `sql` typés, comptés"],
               ["verrous de ligne", nombres_fr(v("lignes_locks")), "occurrences de `FOR UPDATE`"],
               ["visuels déclarés / vérifiés",
                f"{v('manifest_entrees')} / {v('manifest_verifyes')}", "manifeste d'images"],
               ["planches du mémoire", nombres_fr(len(REGISTRE)), "registre de la bibliothèque graphique"],
               ["migrations SQL", "aucune", "le schéma est poussé par `drizzle-kit push`"]],
              cle="IV5.volumetrie", titre="Volumétrie relue à la composition", largeurs=[3, 1.8, 5.2],
              legende="La dernière ligne est celle qu'un relecteur technique cherchera : pas de "
                      "dossier de migrations versionnées. Ce n'est pas un oubli mais un choix de "
                      "conduite d'environnement, dit au §V.3 et à l'inventaire des dettes.")
    F.sous("Les fichiers les plus denses du dépôt", cle="IV.5.1")
    F.tableau(["Rang", "Fichier", "Lignes"],
              [[str(i + 1), f, str(n)] for i, (n, f) in enumerate(c("top_fichiers"))],
              cle="IV5.lourds", titre="Les huit fichiers les plus longs", largeurs=[0.8, 8.0, 1.4],
              nowrap=True,
              legende="Un fichier long n'est pas un défaut en soi : `src/db/schema.ts` est long "
                      "parce qu'il est la définition unique du modèle, et c'est ce qui rend le reste "
                      "court. Le signal d'alerte serait un fichier de logique métier long — il "
                      "n'apparaît pas en tête de cette liste.")

    F.figure("fig39")
    F.p("Le cycle de la donnée commerciale est la planche qui résume le mieux ces quatre sprints : "
        "une commande ne meurt pas, elle se transforme en mouvement de stock, en journal, en "
        "facture, parfois en retour. Les six transitions de la figure sont exactement celles que le "
        "schéma autorise ; les deux qui manquent — l'échange standard et l'avoir — sont des "
        "promesses non tenues, écrites comme telles.")
    F.figure("fig04")
    F.p("L'avant / après n'est pas une promesse de conversion : le projet n'a pas de mesure d'avant. "
        "Il montre ce que le canal change dans la charge de travail — la disponibilité devient une "
        "donnée consultable au lieu d'un appel, la composition du panier une liste au lieu d'un "
        "exploit de mémoire, le suivi un écran au lieu d'un message. Les gains de temps ne sont pas "
        "mesurés : [à mesurer après trois mois d'exploitation].")

    F.section("Ce que le projet a dû refuser", cle="IV.6")
    F.p("Quatre refus sont consignés comme décisions, parce qu'ils ont coûté plus que des ajouts. Le "
        "paiement par carte, parce qu'aucune passerelle n'est contractée et que feindre un paiement "
        "est pire que n'en pas avoir. Le multi-entrepôt, parce que deux boutiques ne justifient pas "
        "une table de plus. L'application native, parce que le parcours tient dans un navigateur. "
        "La recherche vectorielle, parce que le catalogue fait "
        f"{v('produits')} lignes et que la base n'a pas d'extension dédiée. Chacun de ces refus a "
        "son paragraphe dans `decisions.md`, avec l'alternative chiffrée qui a été écartée.")
    F.encadre("Charge utile et limites, en une page",
              "Le système tient ce qu'il annonce : un jeu de connexions de "
              f"{v('pool_max')}, une limite de débit par compartiment et par minute, "
              f"{v('catalogue_par_page')} articles par page avec un plafond dur, une clé "
              "d'idempotence unique indexée, un journal d'audit sans purge automatique. Ce qu'il ne "
              "tient pas : le débit en pic, la réplication, le chiffrement au repos, l'arabe en "
              "écriture de droite à gauche. Ces quatre absences sont la carte des travaux à venir, "
              "et elles sont écrites deux fois — ici et dans la conclusion — parce qu'un mémoire qui "
              "ne dit pas ses limites n'a rien mesuré.")
