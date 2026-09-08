"""rapport/content_c.py — partie III : conception (besoins, cas d'usage, données, modèles).

Cette partie est la plus longue du document parce qu'elle est la seule à pouvoir être fausse sans
qu'on s'en aperçoive à l'usage : un cas d'usage mal écrit ne plante pas, il rend le produit
incohérent. Chaque affirmation y porte son gisement.
"""
from __future__ import annotations

from rapport.facts import get, v, c
from rapport.doc import nombres_fr, dt
from rapport.trace import BACKLOG, EPOPEES


def _tab(fx, nom):
    """Table du schéma, relue par son nom TypeScript (jamais recopiée)."""
    for t in fx.tables:
        if t.ts == nom:
            return t
    raise KeyError(f"table inconnue : {nom}")


def _ncol(fx, nom):
    return len(_tab(fx, nom).cols)


def fabriquer(F):
    fx = get()
    F.intercalaire("III", "Conception : besoins, cas d'usage, modèles",
                   "Vingt-quatre récits, trois acteurs, vingt-quatre tables, deux modèles — écrits "
                   "avant d'être codés, et tenus depuis.",
                   cle="partie.III",
                   items=["III.1 Du besoin métier au cas d'usage", "III.2 Les cas d'usage comme contrats",
                          "III.3 Le modèle de données", "III.4 Le modèle d'argent et de promotion",
                          "III.5 Les processus : commande, stock, retour", "III.6 Architecture et composants",
                          "III.7 Les trente actions, garde-fou par garde-fou",
                          "III.8 Ce qui est stocké, ce qui est calculé"])

    F.section("Du besoin métier au cas d'usage", cle="III.1")
    F.lead("Un besoin métier s'écrit en une phrase que l'exploitant reconnaît. Un cas d'usage "
           "s'écrit en un contrat : qui, quoi, dans quel ordre, et que se passe-t-il quand ça "
           "rate. Cette section montre le passage de l'un à l'autre sur le rayon qui porte le "
           "projet.")
    F.p("Le catalogue est organisé en trois axes qui se croisent sans se confondre : les univers "
        f"({v('univers')}), les catégories ({v('categories_total')} dont {v('sous_categories')} "
        f"sous-catégories) et les besoins ({v('besoins')}). Cette triple entrée n'est pas un "
        "gust : elle correspond aux trois façons dont un client arrive. Le premier sait qu'il "
        "cherche un solaire, le second une marque, le troisième a la peau qui tire. Les requêtes "
        f"de recherche enregistrées ({v('routes')} routes, dont une consacrée à la recherche) "
        "confirment que le troisième cas est le plus fréquent en boutique ; en ligne, il devient "
        "le plus coûteux à rater.")
    F.figure("fig25")
    F.p(f"Trois acteurs, {len(BACKLOG)} buts atteignables. Le visiteur non identifié a le même droit de "
        "lecture que le client : en parapharmacie, une fiche lue sans compte est une visite qui "
        "reviendra. L'équipe, elle, n'a pas un rôle mais deux : l'administration (prix, stock, "
        f"promotions) et le support (tickets, avis, notes), séparés par l'enum `user_role` à "
        f"{v('roles')} valeurs et par la garde d'action, pas par un menu caché.")

    F.sous("Les trois référentiels du catalogue", cle="III.1.1")
    sens = ["le plus gros volume de conseil", "rituel quotidien, récurrence forte",
            "saisonnalité très marquée", "conseil technique, avis déterminants",
            "panier moyen haut, achat de complément", "tolérance et composition surveillées",
            "entrée de gamme, fréquence élevée"]
    uni = sorted(c("par_univers").items(), key=lambda kv: -kv[1])
    F.tableau(["Univers", "Produits", "Ce que ça change en rayon"],
              [[u, str(n), sens[i] if i < len(sens) else "—"] for i, (u, n) in enumerate(uni)],
              cle="III1.univers", titre=f"Les {v('univers')} univers, du plus fourni au plus mince",
              largeurs=[2.6, 1.4, 7.6],
              legende="Le nombre de références n'est pas un jugement de valeur : l'hygiène pèse "
                      "lourd en trafic et léger en marge. La colonne de droite est une lecture "
                      "d'officine, pas une donnée du dépôt.")
    F.tableau(["Marque", "Références"],
              [[m, str(n)] for m, n in sorted(c("par_marque").items(), key=lambda kv: -kv[1])],
              cle="III1.marques", titre=f"Les {v('marques')} marques du catalogue",
              largeurs=[6.0, 1.6], cesser=10,
              legende=f"Seize marques, {v('produits')} références : la tête de liste concentre le "
                      "tiers du catalogue, ce qui explique le poids des filtres de marque dans "
                      "l'interface.")
    F.tableau(["Besoin exprimé", "Produits reliés"],
              [[b, str(n)] for b, n in sorted(c("par_besoin").items(), key=lambda kv: -kv[1])],
              cle="III1.besoins", titre=f"Les {v('besoins')} besoins et leur couverture",
              largeurs=[6.0, 1.6],
              legende="Un produit peut répondre à plusieurs besoins ; la jointure est une table, pas "
                      "un champ, ce qui permet d'ajouter un besoin sans retoucher le catalogue.")

    F.section("Les cas d'usage comme contrats", cle="III.2")
    F.p("Les vingt-quatre récits de l'annexe D sont la matière première de cette section. Chacun "
        "porte : l'acteur, ce qu'il reçoit, ce qu'il rend, le sprint qui le livre, la figure qui "
        "l'illustre, la vérification qui le tient. Le tableau ci-dessous n'en reprend que six, "
        "ceux dont la moindre erreur de contrat aurait coûté le plus cher.")
    rows = []
    for us in BACKLOG:
        if us["id"] in ("US-11", "US-14", "US-15", "US-20", "US-21", "US-13"):
            rows.append([us["id"], us["titre"], us["sprint"],
                         ", ".join(f"`{f}`" for f in us["figures"]),
                         f"`{us['test']}`"])
    F.tableau(["Récit", "But atteignable", "Sprint", "Planches", "Vérification"], rows,
              cle="III2.contrats", titre="Six contrats de cas d'usage, les plus coûteux à rater",
              largeurs=[0.9, 3.2, 0.7, 1.6, 2.4],
              legende="La dernière colonne est une fonction du harnais, pas une promesse : son nom "
                      "peut être cherché dans `qa.py`.")
    F.sous("Index des vingt-quatre contrats", cle="III.2.1")
    F.p("La liste complète, en une table : le récit, son épopée, son titre, le sprint qui l'a livré. "
        "L'annexe D en donne la fiche détaillée ; cette table sert de contrôle visuel — un récit "
        "sans épopée ou sans sprint se voit d'ici.")
    F.tableau(["Récit", "Épopée", "But atteignable", "Sprint", "Section", "Valeur", "Effort"],
              [[u["id"], u["epopee"], u["titre"], u["sprint"], u["section"],
                nombres_fr(u["valeur"], decimales=2), nombres_fr(u["effort"], decimales=2)]
               for u in BACKLOG],
              cle="III2.index", titre=f"Les {len(BACKLOG)} récits du backlog, dans l'ordre de livraison",
              largeurs=[1.1, 1.0, 6.4, 0.9, 1.2, 1.2, 1.2], nowrap=True, cesser=30,
              legende="Valeur et effort sont des estimations déclarées sur une échelle de zéro à un, "
                      "posées au sprint 0 pour ordonner le travail : ce ne sont pas des mesures, et "
                      "le mémoire ne les présente pas comme telles.")

    F.encadre("Ce qu'un contrat interdit",
              "Un cas d'usage sans issue d'erreur est un menu, pas une conception. Les six contrats "
              "ci-dessus ont tous une branche de refus écrite avant le code : rupture de stock, "
              "double clic, numéro de commande indisponible, accès invité non propriétaire, "
              "transition de statut interdite, méthode de paiement refusée. Ces cinq refus sont "
              "des messages en français dans l'application, et cinq assertions dans la QA.")

    F.section("Le modèle de données", cle="III.3")
    F.lead("Vingt-quatre tables. Ce n'est pas beaucoup pour un commerce, c'est trop pour un "
           "mémoire : la planche suivante est donc faite pour être découpée, et les six figures de "
           "domaine qui suivent en sont les découpages assumés.")
    F.figure("figR1")
    F.p("Le schéma se lit en six domaines qui se recouvrent partiellement — c'est voulu, parce que "
        "la session, le limiteur de débit et le journal d'audit appartiennent à la fois au "
        "fonctionnel et à la sûreté de fonctionnement. La table `orders` est la charpente : "
        f"{_ncol(fx, 'orders')} colonnes, dont trois d'identité (numéro, clé d'accès, "
        "idempotence), cinq de montants figés, deux de transporteur, une de contact, et les "
        "timestamps.")
    for cle, titre, propos in [
        ("figX1", "Identité et accès",
         "Trois tables portent l'authentification : l'utilisateur, sa session, ses adresses. La "
         f"suppression de l'utilisateur est en cascade (`onDelete`) sur les adresses et les "
         f"favoris, restrictive sur les commandes : l'historique de vente ne disparaît pas avec un "
         f"compte. Les {_ncol(fx, 'users')} colonnes de `sessions` tiennent dans "
         "quatre champs, dont un jeton de 32 octets en texte et une échéance indexée."),
        ("figX2", "Catalogue",
         "Sept tables : marques, catégories à deux niveaux (l'attribut `is_universe` évite une "
         "table de plus), besoins, produits, la jointure produit-besoin, les articles du journal "
         f"et les boutiques. Le produit est large ({_ncol(fx, 'products')} colonnes) parce qu'il "
         "porte à la fois le commerce (prix, stock, promotion) et le conseil (composition, "
         "utilisation, volume) ; la scinder aurait ajouté une jointure pour un gain nul à cette "
         "échelle."),
        ("figX3", "Ventes",
         "La commande et ses trois satellites : lignes, événements, promotions, mouvements. La "
         "ligne de commande est un relevé, pas une référence : le nom, la marque, le prix unitaire "
         "et le total y sont écrits au moment de la vente, pour que la facture reste vraie quand "
         "le catalogue change."),
        ("figX4", "Engagement",
         "Avis, favoris, points de fidélité, abonnés, tickets. L'avis est le seul objet modéré : "
         "son statut à trois valeurs est une enum, et sa publication déclenche un recalcul de la "
         "moyenne dans la même transaction, sans quoi la fiche afficherait une statistique "
         "orpheline."),
        ("figX5", "Exploitation",
         "Journal d'audit, événements de recherche, événements d'analyse, limiteur. Ces quatre "
         "tables n'ont pas d'interface d'écriture publique : elles se remplissent par les actions, "
         "et leur écriture est volontairement tolérante à l'échec — un journal qui fait échouer "
         "une commande est un journal qui sera désactivé."),
        ("figX6", "Sûreté de fonctionnement",
         "Le même objet relu sous l'angle de la panne : ce qui doit survivre à un redémarrage "
         "(sessions, limiteur), ce qui doit être irrévocable (audit), ce qui doit rester borné "
         "(recherches, tickets), et ce qui est purgeable sans consequence (événements d'analyse)."),
    ]:
        F.figure(cle)
        F.p(propos)
    F.p(f"Les {v('index')} index ne sont pas décoratifs : ils répondent aux requêtes réellement "
        "émises par le catalogue, par l'administration et par le suivi. La recherche plein texte "
        "n'est pas un index dédié mais une recherche insensible à la casse sur trois colonnes, "
        f"complétée par un enregistrement de la requête ({v('endpoints')} points d'entrée API, "
        "dont un de recherche). C'est un choix assumé à cette volumétrie, et il est réversible "
        "sans toucher au schéma.")
    F.code("src/db/schema.ts", 151, 26,
           commentaire="La table `products`, la plus large du schéma. Trois détails valent l'arrêt : "
                       "le prix est un entier non nul (`notNull`) mais sans contrainte `check` — la "
                       "positivité est tenue dans le code, pas dans la base, et le mémoire le dit "
                       "au lieu de le maquiller ; l'image est une chaîne qui peut être nulle, le "
                       "composant retombant alors sur l'image d'univers ; le `slug` est unique et "
                       "indexé, ce qui fait de l'URL l'identité publique du produit.")

    F.section("Le modèle d'argent et le modèle de promotion", cle="III.4")
    F.lead("Deux modèles, une seule discipline : ne jamais laisser deux façons de calculer la même "
           "chose. Le premier évite l'erreur d'arrondi, le second évite l'erreur de contexte.")
    F.p(f"Le schéma ne porte aucune contrainte de vérification : {v('contraintes_check')} `check`, "
        f"en revanche {v('colonnes_non_null')} colonnes sont déclarées non nulles. C'est un choix, "
        "pas un oubli, et il a un coût écrit ici : la non-négativité du stock est tenue par le "
        "code, dans `src/lib/orders.ts:100`, qui relit la valeur après la mise à jour et lève si "
        "elle passe sous zéro — la transaction s'annule donc, mais la base, elle, accepterait un "
        "écrasement fait hors transaction. Un correctif tient dans une migration : il est à "
        "l'inventaire des dettes, §V.6. Le modèle d'argent, lui, est arithmétique. Un montant est un entier de millimes ; le formatage "
        f"passe par la locale {v('locale_monnaie')} avec {v('decimales_monnaie')} décimales "
        "forcées ; la remise en pourcentage est calculée en entier, arrondie à la valeur la plus "
        "proche de zéro, et plafonnée. Le franco se décide sur le sous-total, jamais sur le total : "
        f"le seuil de {dt(v('seuil_franco'))} est évalué avant les frais de port, ce qui évite "
        "qu'une promotion déclenche une gratuité non prévue.")
    F.figure("fig29")
    F.p(f"Le modèle de promotion est une fonction pure avec {v('motifs_rejet_promo')} motifs de "
        "refus, écrits dans `src/lib/promotions.ts`. Cette pureté est la ligne de défense contre le "
        "pire accident du domaine : un prix qui change entre l'affichage et la validation. La "
        "fonction ne connaît ni la requête ni la session ; elle reçoit une promotion et des lignes, "
        "et rend soit un montant, soit une raison.")
    F.tableau(["Refus formulé par le moteur", "Condition qui le déclenche"],
              [[f"« {m} »", ["la date de début est postérieure à maintenant",
                            "le compteur d'usage a atteint le plafond",
                            "la date de fin est antérieure à maintenant",
                            "le code saisi ne correspond à aucune promotion active",
                            "le champ est vide à la validation",
                            "aucune ligne du panier n'appartient à l'univers ciblé",
                            "le client a déjà bénéficié du code"][i] if i < 7 else
                "le sous-total est inférieur au minimum exigé"]
               for i, m in enumerate(c("motifs_rejet") + ["Minimum d'achat (montant calculé)"])],
              cle="III4.motifs", titre=f"Les {v('motifs_rejet_promo')} motifs de refus du moteur",
              largeurs=[6.6, 5.0],
              legende="Les sept premiers textes sont recopiés du source ; le huitième est construit à "
                      "la volée parce qu'il contient le montant du minimum. Un client qui comprend "
                      "pourquoi son code est refusé n'appelle pas le comptoir : c'est la seule "
                      "raison d'être de ce tableau.")
    F.figure("fig28")
    F.code("src/lib/promotions.ts", 20, 27,
           commentaire="La fonction `evaluate`. Sa signature dit l'essentiel : elle ne prend pas "
                       "de `Request`, ne lit pas de cookie, ne formate rien. Le lecteur du mémoire "
                       "peut la tester sur papier, et c'est exactement ce que la QA fait en "
                       "reconstruisant les cas limites.")

    F.section("Les processus : commande, stock, retour", cle="III.5")
    F.lead("Le processus qui vaut le mémoire est celui où trois systèmes de vérité se touchent : "
           "le stock, l'argent et le temps. Les figures suivantes les séparent pour mieux montrer "
           "le point de rencontre.")
    F.figure("fig26")
    F.p("Le tracé ci-dessus est la colonne vertébrale du produit : onze flèches, quatre points "
        "durs, et une règle — aucune écriture avant d'avoir la ligne en main. Le numéro de "
        f"commande est tiré jusqu'à {v('tirages_numero')} fois pour éviter une collision ; la "
        "clé d'accès est un aléa de "
        f"{v('bits_session')} bits ; la facture est générée après coup, pas pendant, pour ne pas "
        "faire dépendre la vente d'un rendu.")
    F.code("src/lib/orders.ts", 78, 20,
           commentaire="Deux auxiliaires de verrouillage. Le premier sélectionne les lignes de "
                       "produit `FOR UPDATE` dans l'ordre des identifiants, ce qui évite "
                       "l'interblocage quand deux commandes touchent les mêmes rayons ; le second "
                       "verrouille la commande avant tout changement de statut, ce qui rend la "
                       "transition idempotente par construction.")
    F.p("La machine à états mérite une planche pour elle seule, parce qu'elle est le lieu où le "
        "droit de rétractation, la logistique et la paye à la livraison se disputent. Sept statuts, "
        f"{v('transitions')} transitions autorisées, {v('statuts_sans_sortie')} puits. La table de "
        "transitions est une donnée du code, pas une convention d'interface : l'administration ne "
        "peut pas « forcer » un statut, elle demande une transition et se voit refuser ce qui n'est "
        "pas écrit.")
    F.figure("fig49")
    F.figure("fig19")
    F.figure("fig27")
    F.p("Les messages de refus ne sont pas écrits deux fois : ils sortent des "
        f"{v('schemas_zod')} schémas de validation de `src/lib/validation.ts`, et l'interface "
        "affiche ce que l'action renvoie. La ligne de preuve est dans "
        "`src/components/checkout/checkout-flow.tsx:68` et `:80`, où le titre du message d'erreur "
        "est `r.error` et la description la première erreur de champ. Un texte d'erreur inventé "
        "côté client est un texte qui ment sur ce que le serveur a refusé.")

    F.section("Architecture et composants", cle="III.6")
    F.lead("Cinq couches, une règle de circulation, et un test d'architecture qui tient en un grep.")
    F.p("La règle : la page ne calcule pas, l'action ne présente pas, le modèle ne connaît pas "
        "HTTP. Elle est facile à écrire et coûteuse à tenir ; elle a coûté la réécriture de deux "
        "composants qui calculaient un total dans le client, et elle a rendu possible la "
        "réimplémentation du moteur de promotion sans toucher une ligne de mise en page.")
    F.figure("fig23")
    F.p(f"Les {v('composants')} composants du dépôt se répartissent en {v('composants_client')} "
        f"interactifs et {v('composants') - v('composants_client')} rendus côté serveur, rangés "
        f"dans {v('composants_dossiers')} dossiers. Ce déséquilibre est un choix : le panier, la "
        "recherche et le tiroir nécessitent de l'immédiateté ; la fiche produit, le catalogue et "
        f"la confirmation n'ont besoin que d'être justes. L'administration tient dans "
        f"{v('composants_admin')} fichiers, parce qu'elle partage un même vocabulaire de table, de "
        "filtre et de ligne d'action : cinq formulaires, une table, une barre de navigation, un "
        "jeu de primitives.")
    F.sous("L'inventaire des composants", cle="III.6.1")
    F.p("Trente-six fichiers de composants, dix dossiers, un compte de lignes par fichier. La "
        "répartition entre rendu serveur et interactif est donnée par la présence de la directive "
        "`use client` en tête de fichier — c'est elle qui décide, pas une convention d'arborescence.")
    F.tableau(["Composant", "Rendu", "Lignes"],
              [[c_["file"].replace("src/components/", ""), "cliente" if c_["client"] else "serveur",
                str(c_["lines"])] for c_ in sorted(fx.components, key=lambda x: -x["lines"])],
              cle="III6.composants", titre=f"Les {v('composants')} composants du dépôt",
              largeurs=[7.0, 1.6, 1.4], nowrap=True, cesser=36,
              legende=f"{v('composants_client')} composants clients sur {v('composants')} : le "
                      "déséquilibre est un choix de conception, pas un oubli d'optimisation. La "
                      "colonne « lignes » est la longueur réelle du fichier, relue au build.")

    F.figure("fig24")
    F.p("Le fichier de connexion à la base est court — vingt lignes, dont une de cache de pool. Sa "
        "première ligne utile est un refus : sans variable d'environnement de connexion, le "
        "processus ne démarre pas. Cette discipline, généralisée à la configuration, est décrite "
        "au §IV.4 ; elle a évité trois mises en production silencieusement broken.")
    F.code("src/lib/env.ts", 8, 12,
           commentaire="Le garde-fou de configuration, avec la liste noire de secrets de "
                       "développement. La logique est simple et féroce : une valeur par défaut sur "
                       "un secret est un trou. En production, une valeur d'exemple fait échouer le "
                       "démarrage.")

    F.section("Les trente actions, garde-fou par garde-fou", cle="III.7")
    F.lead("Cette section est la plus réductible en grief et la plus solide : elle ne décrit pas "
           "des intentions, elle compte des lignes de défense par fonction d'écriture.")
    F.p("Le dépôt expose "
        f"{v('actions')} fonctions d'action : {v('actions_garde')} portent une vérification "
        f"d'identité ou de rôle, {v('actions_zod')} une validation de schéma, {v('actions_rate')} "
        f"une limite de débit, {v('actions_origin')} une vérification d'origine, {v('actions_tx')} "
        f"roulent dans une transaction et {v('actions_lock')} posent un verrou de ligne. Le "
        "tableau de la figure ci-dessous, généré depuis le fichier, montre la répartition réelle — "
        "y compris les cases vides.")
    F.figure("fig22")
    F.p(f"Les cases vides ne sont pas toutes des oublis. La revalidation de cache "
        f"(`revalidatePath`) est présente sur {v('actions_reval')} actions. Côté écriture, "
        f"{v('actions_ecriture')} actions touchent la base, {v('actions_ecritures_publiques')} "
        "n'ont pas de garde de rôle : l'inscription et l'abonnement à la lettre d'information, "
        f"qui sont bornées par le limiteur de débit et par Zod. La statistique qui compte est "
        f"donc {v('actions_ecriture_sans_garde_ni_limite')} : une écriture sans garde et sans "
        "limite. Ce nombre est à zéro, et il est recalculé à chaque build — s'il cesse de l'être, "
        "la figure ci-dessus change de forme avant que le texte ne soit corrigé.")
    F.encadre("Comment vérifier cette section en trente secondes",
              "Ouvrir `src/actions/`, chercher les fonctions exportées, vérifier la première ligne "
              "de chacune. Le compte rendu par la QA donne le même résultat pour un coût humain "
              "nul : c'est la raison pour laquelle il est tenu à jour.")
    F.figure("fig51")

    F.section("Ce qui est stocké, ce qui est calculé", cle="III.8")
    F.p("Un relevé se stocke, une projection se calcule. Le prix payé est un relevé : il ne bouge "
        "plus. La remise affichée est une projection : elle dépend du panier, de l'heure et du "
        "plafond d'usage, et elle doit être recalculée à chaque fois. Le projet a perdu deux jours "
        "à écrire cette distinction dans le code, et les a gagnés en supprimant un bug de facture "
        "qui n'a jamais existé.")
    F.figure("fig32")
    F.p("Trois exceptions à cette règle sont dans le dépôt, et elles sont toutes trois justifiées "
        "par la lecture : les totaux de commande (relevés pour la facture), la moyenne des avis "
        "(recalculée à la modération, mais stockée pour que la grille du catalogue reste lisible "
        "sans jointure d'agrégat), et le stock résiduel (qui est un relevé du dernier mouvement, "
        "jamais une somme calculée à la volée). La colonne de droite de la figure montre que le "
        "projet a compté ses exceptions : elles sont trois, pas trente.")
