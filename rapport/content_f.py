"""rapport/content_f.py — annexes A à F, résumés, quatrième de couverture.

Les annexes ne sont pas un fourre-tout : elles sont le gisement. Tout ce qui y figure est produit
par un extracteur (`facts.py`, `trace.py`) et rien n'y est tapé à la main — ce qui permet au
lecteur de rejouer la page qu'il a sous les yeux.
"""
from __future__ import annotations

import json
from pathlib import Path

from rapport.facts import get, v, c
from rapport.mpl import REGISTRE
from rapport.doc import nombres_fr, dt
from rapport.trace import BACKLOG, EPOPEES
from rapport.invariants import INVARIANTS, PORTES, SIALORS, REGLES_STOP, par_famille

import re as _re

VALID = Path(__file__).resolve().parent.parent / "src" / "lib" / "validation.ts"


def _schemas_zod() -> dict[str, int]:
    """Noms des schémas exportés et leur ligne, relus dans le fichier (aucune liste à la main)."""
    texte = VALID.read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for m in _re.finditer(r"^export const (\w+) = ", texte, _re.M):
        out[m.group(1)] = texte.count("\n", 0, m.start()) + 1
    if len(out) != v("schemas_zod"):
        raise RuntimeError(f"{len(out)} schémas trouvés dans {VALID.name}, "
                           f"{v('schemas_zod')} annoncés par facts.py : l'un des deux ment")
    return out


SCHEMAS_ZOD = _schemas_zod()

AUDIT = Path(__file__).resolve().parent.parent / "audit"

# Contrastes calculés depuis les six valeurs du kit, par la formule WCAG 2.x.
PALETTE = {"encre": "2B2620", "or": "C9A959", "papier": "FBF7EF", "sauge": "6F7F63",
           "rouille": "A8503B", "pierre": "CFC4B4", "deck_fond": "201A13", "deck_clair": "F3ECDD"}


def _luminance(hexa: str) -> float:
    def canal(x):
        x = x / 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexa[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def _rapport(a: str, b: str) -> str:
    la, lb = _luminance(PALETTE[a]), _luminance(PALETTE[b])
    hi, lo = max(la, lb), min(la, lb)
    return nombres_fr((hi + 0.05) / (lo + 0.05), decimales=2) + " : 1"


def _relations() -> int:
    return sum(len(u["figures"]) + len(u["fichiers"]) + len(u["symboles"]) + 4 for u in BACKLOG)


def fabriquer(F):
    fx = get()
    F.intercalaire("Annexes", "Le gisement : six inventaires complets",
                   "A Repères de forme · B Le modèle table par table · C Catalogue et routes · "
                   "D Les vingt-quatre récits · E Protocoles et commandes · F Traçabilité.",
                   cle="annexes",
                   items=["Annexe A — Repères de forme, palette, accessibilité",
                          "Annexe B — Le modèle de données, table par table",
                          "Annexe C — Catalogue, parcours, inventaire des routes",
                          "Annexe D — Les vingt-quatre récits du backlog",
                          "Annexe E — Protocoles de vérification et commandes",
                          "Annexe F — Traçabilité : récit, section, figure, preuve"])

    # ──────────────────────────────────────────────── annexe A
    F.section("Annexe A — Repères de forme, palette, accessibilité", cle="annexe.A")
    F.p("Cette annexe existe parce qu'un document qui parle de contraste se doit de montrer les "
        "siens. Les valeurs ci-dessous sont celles employées par le kit — rapport, diaporama, "
        "figures — et les rapports sont calculés à la composition par la formule de luminance "
        "relative, non repris d'une fiche de palette.")
    F.tableau(["Premier plan", "Fond", "Emploi", "Rapport mesuré"],
              [["Encre #2B2620", "Papier #FBF7EF", "texte courant du rapport", _rapport("encre", "papier")],
               ["Or #C9A959", "Encre #2B2620", "filets et titres d'intercalaire", _rapport("or", "encre")],
               ["Or #C9A959", "Papier #FBF7EF", "accent réservé aux filets, jamais au texte",
                _rapport("or", "papier")],
               ["Sauge #6F7F63", "Papier #FBF7EF", "état « disponible »", _rapport("sauge", "papier")],
               ["Rouille #A8503B", "Papier #FBF7EF", "état « rupture »", _rapport("rouille", "papier")],
               ["Clair #F3ECDD", "Fond #201A13", "diaporama de soutenance", _rapport("deck_clair", "deck_fond")]],
              cle="annexeA.contrastes", titre="Contrastes mesurés du kit", largeurs=[2.6, 2.4, 4.2, 1.8],
              legende="Un accent réservé aux filets n'est pas une promesse d'accessibilité : c'est "
                      "la mention de son usage. La ligne or / papier est volontairement conservée "
                      "avec son rapport faible, parce qu'elle ne sert pas à porter du texte.")
    F.p("Deux règles complètent la palette. Aucune information n'est portée par la couleur seule : "
        "un état de stock s'écrit avec son mot, sa forme et sa position. Aucun pictogramme n'est "
        f"employé sans libellé : les {v('icones')} icônes du dépôt sont chacune accompagnées d'un "
        "texte ou marquées décoratives.")
    F.p(f"Planche de contact : les {len(REGISTRE)} figures du document, reproduites en vignettes sur "
        "une page unique, sont fournies en `audit/planche-contact.png`. Cet objet n'est pas une "
        "coquetterie : il permet de vérifier en dix secondes qu'aucune planche n'est vide, tronquée "
        "ou répétée, et il est régénéré à chaque build.")

    F.sous("Glossaire des termes du projet", cle="annexeA.glossaire")
    F.p("Les termes ci-dessous sont ceux que le jury rencontrera dans les parties I à IV. Ils sont "
        "donnés dans l'ordre du document, avec le mot employé par le code quand il diffère — parce "
        "qu'un mot qui change entre la fiche et la base est une source de litige.")
    F.tableau(["Terme du mémoire", "Mot du code", "Sens retenu ici"],
              [["commande", "orders", "l'engagement d'achat, du panier validé à la livraison"],
               ["panier", "cart", "la sélection non encore validée, sans effet sur le stock"],
               ["client", "users + role", "le compte, pas la personne physique"],
               ["équipe", "role ADMIN ou SUPPORT", "qui peut écrire quoi dans l'administration"],
               ["millime", "priceMillimes", "le tiers du dinar, seule unité de stockage du prix"],
               ["remise", "promotions", "le code, avec son plafond d'usage et son échéance"],
               ["franco", "FREE_SHIPPING_THRESHOLD", "le seuil qui rend la livraison gratuite"],
               ["mouvement", "inventoryMovements",
                "toute entrée, sortie, ajustement, vente ou retour"],
               ["verrou", "FOR UPDATE", "la ligne saisie avant lecture, pour que deux ventes ne "
                                         "croient pas la même disponibilité"],
               ["clé d'accès", "accessKey", "ce qui permet de suivre une commande sans compte"],
               ["journal", "auditLogs", "la trace de ce que l'administration a changé"],
               ["univers", "categories.isUniverse", "la porte d'entrée large du catalogue"],
               ["besoin", "concerns", "le motif de venue du client, en langage courant"],
               ["vedette", "isFeatured", "la mise en avant éditoriale, pas un paiement de marque"],
               ["retour", "returned", "le statut puits de la machine à états"],
               ["retrait", "pickup", "le seul délai mesuré en heures du catalogue"]],
              cle="annexeA.glossaire", titre="Glossaire croisé mémoire et code",
              largeurs=[3.0, 3.4, 5.2], nowrap=True,
              legende="Seize termes, pas trente : un glossaire qui répète le dictionnaire de données "
                      "ne sert qu'à allonger le document.")

    F.sous("Territoire couvert par la livraison", cle="annexeA.territoire")
    F.p(f"Les {v('gouvernorats')} gouvernorats tunisiens sont tous déclarés dans le dépôt ; seuls "
        f"{v('gouvernorats_avec_villes')} portent une liste de villes suggérées. Le délai, lui, est "
        f"calculé sur une seule règle : {v('grand_tunis')} gouvernorats du Grand Tunis en vingt-"
        "quarante-huit heures, le reste en quarante-huit-soixante-douze, avec une option express à "
        "vingt-quatre heures partout et un retrait en deux heures en boutique.")
    F.tableau(["Gouvernorat", "Villes suggérées", "Délai standard"],
              [[n, str(nb), delai] for n, nb, delai in c("territoires")],
              cle="annexeA.territoire_liste", titre="Le territoire, gouvernorat par gouvernorat",
              largeurs=[4.0, 2.4, 3.2], nowrap=True, cesser=24,
              legende="Zéro gouvernorat absent, vingt-quatre lignes : la table est produite depuis "
                      "`src/lib/tunisia.ts`, et une ligne en moins dans le code en enlève une ici.")

    # ──────────────────────────────────────────────── annexe B
    F.section("Annexe B — Le modèle de données, table par table", cle="annexe.B")
    F.p(f"Cet inventaire est produit en relisant `src/db/schema.ts` : pour chaque table, le nom "
        "sql, la ligne de déclaration, le nombre de colonnes, le nombre d'index, les clés "
        "étrangères et les colonnes obligatoires. Aucun commentaire n'est ajouté, aucune ligne "
        "n'est retirée : la table soit exister, soit ne pas exister.")
    lignes = []
    for t in fx.tables:
        fk = sum(1 for col in t.cols if getattr(col, "fk", None))
        nn = sum(1 for col in t.cols if "non NULL" in getattr(col, "flags", []))
        lignes.append([t.sql, str(t.line), str(len(t.cols)), str(len(t.indexes)), str(fk), str(nn)])
    F.tableau(["Table", "Ligne", "Colonnes", "Index", "Clés étrangères", "Obligatoires"], lignes,
              cle="annexeB.tables", titre=f"Les {v('tables')} tables, telles qu'écrites",
              largeurs=[3.0, 1.0, 1.5, 1.0, 1.9, 1.8], nowrap=True,
              legende=f"Totaux relus : {v('tables')} tables, {v('colonnes')} colonnes, {v('index')} index, "
                      f"{v('cle_etrangeres')} clés étrangères, {v('colonnes_non_null')} colonnes "
                      f"obligatoires, {v('contraintes_check')} contrainte de vérification. Cette "
                      "dernière valeur est à zéro, et la conséquence est écrite §III.4 : les "
                      "bornes de valeur sont tenues par le code, pas par la base.")
    F.p(f"Les {v('enums')} types énumérés méritent leur propre tableau, parce qu'ils sont la partie "
        "du modèle la plus souvent sous-estimée en relecture : un statut non borné est un statut qui "
        "dérive. Les valeurs sont recopiées depuis le schéma à la composition — une valeur ajoutée "
        "dans le code apparaît ici au build suivant, et nulle part ailleurs.")
    F.tableau(["Type énuméré", "Valeurs", "Nombre", "Ligne"],
              [[cle, ", ".join(d["values"]), str(len(d["values"])), str(d.get("line", "—"))]
               for cle, d in sorted(fx.enums.items())],
              cle="annexeB.enums", titre="Les dix enums du schéma", largeurs=[2.4, 6.6, 1.0, 1.2],
              nowrap=True,
              legende="Colonne « ligne » : la ligne de déclaration dans `src/db/schema.ts`, relue par "
                      "`facts.py`.")
    F.p("Le dictionnaire de données suit : une ligne par colonne, avec son type, ses contraintes et "
        "le type énuméré éventuel. Il est produit en relisant le schéma, ce qui le rend plus exact "
        "qu'un tableau recopié d'une documentation — et surtout, il change tout seul quand le schéma "
        "bouge.")
    F.sous("Dictionnaire des colonnes", cle="annexeB.dico")
    lignes_cols = []
    for t in fx.tables:
        for col in t.cols:
            drapeaux = ", ".join(getattr(col, "flags", [])) or "—"
            lignes_cols.append([t.sql, col.ts, col.kind, drapeaux,
                                getattr(col, "enum", None) or "—", getattr(col, "fk", None) or "—"])
    F.tableau(["Table", "Colonne", "Type", "Contraintes", "Enum", "Référence"], lignes_cols,
              cle="annexeB.colonnes", titre=f"Les {v('colonnes')} colonnes du modèle, une par ligne",
              largeurs=[2.4, 3.0, 1.4, 2.6, 2.0, 2.4], nowrap=True, cesser=46,
              legende="Le tableau est découpé en portions de quarante-six lignes avec répétition de "
                      "l'en-tête, pour qu'aucune ligne ne soit tronquée ni coupée au milieu.")

    F.sous("Inventaire des index", cle="annexeB.index")
    F.p(f"Les {v('index')} index du schéma, table par table, dans l'ordre de déclaration. Un index "
        "sans requête qui le consomme est du poids à l'écriture ; un chemin d'accès manquant est une "
        "requête qui lit toute la table. Cette liste est le lieu où le lecteur peut trancher la "
        "question lui-même.")
    lignes_idx = []
    for t in fx.tables:
        for ix in t.indexes:
            lignes_idx.append([t.sql, ix.split(" ")[0], ix.split(" ", 1)[1]])
    F.tableau(["Table", "Nature", "Nom"], lignes_idx, cle="annexeB.index_liste",
              titre=f"Les {v('index')} index déclarés", largeurs=[3.0, 2.0, 6.0], nowrap=True, cesser=40,
              legende=f"{len(lignes_idx)} lignes, {sum(1 for t in fx.tables if t.indexes)} tables "
                      "indexées. La nature distingue `uniqueIndex` de `index` : le premier porte une "
                      "contrainte d'unicité, le second seulement une vitesse.")

    F.p("Quatre tables sont le siège des garde-fous cités en partie III, et leurs noms méritent "
        "d'être écrits une fois : `orders` (numéro unique, clé d'accès, clé d'idempotence "
        "unique, montants figés), `order_items` (relevé de prix, pas référence), `stock_movements` "
        "(journal du stock, jamais écrasé) et `audit_logs` (append-only, aucune interface de "
        "suppression). Le détail est dans l'inventaire ci-dessus ; la raison est aux §III.3 et "
        "§III.5.")

    F.sous("L'échelle typographique du document", cle="annexeA.echelle")
    ECHELLE = [
        ("Couverture — titre", "DejaVuSerif", "26 / 30", "or sur encre"),
        ("Intercalaire — numéro", "DejaVuSerif-Bold", "34 / 36", "or"),
        ("Intercalaire — titre", "DejaVuSerif", "17 / 21", "papier"),
        ("Titre de section", "DejaVuSerif-Bold", "13,5 / 16", "encre"),
        ("Sous-titre", "DejaVuSerif-Bold", "10,8 / 13", "encre"),
        ("Chapeau", "DejaVu", "9,4 / 13,4", "encre, retrait gauche"),
        ("Corps", "DejaVu", "9,1 / 12,8", "encre, justifié"),
        ("Liste", "DejaVu", "8,9 / 12,4", "puce or"),
        ("Légende de planche", "DejaVu", "7,6 / 10,2", "gris"),
        ("Tableau", "DejaVu", "7,1 / 9,2", "encre"),
        ("Extrait de code", "DejaVuSansMono", "6,7 / 8,9", "fond papier, filet"),
        ("Sommaire", "DejaVu", "8,3 / 11,4", "lien cliquable"),
    ]
    F.tableau(["Emploi", "Famille", "Corps / interlignage (pt)", "Particularité"],
              [[a, b_, c_, d] for a, b_, c_, d in ECHELLE],
              cle="annexeA.echelle_liste", titre="L'échelle employée par le moteur de composition",
              largeurs=[3.6, 2.6, 2.6, 4.0],
              legende="Une seule famille serif pour les titres, une sans-serif pour le corps, une "
                      "monospace pour le code : trois polices, pas une de plus, parce que chaque "
                      "police embarquée pèse sur le budget de poids du fichier.")

    F.p("Trois mesures ont été nécessaires pour écrire ce qui précède, et elles contredisent trois "
        "idées reçues dans ce dépôt. La première : l'espace insécable fine (U+202F), que DejaVu "
        "possède et que l'usage français recommande, est traitée par le moteur de paragraphes comme "
        "une espace ordinaire — la césure revient. Le rendu utilise donc U+00A0, et le contrôle "
        "accepte les deux, parce que ce qui est en jeu est l'absence de césure, pas le numéro de "
        "caractère. La seconde : le calque texte d'un PDF normalise l'insécable en espace, si bien "
        "qu'une expression régulière posée sur le texte extrait ne voit rien ; la loi est donc "
        "vérifiée sur les lignes reconstituées géométriquement, span par span, avec exemption "
        "déclarée pour les spans monospace. La troisième : échapper le texte « pour protéger le "
        "lecteur du balisage » détruit la mise en forme de l'auteur ; l'échappement préserve "
        "exactement la liste des balises d'emphase, et le verbatim passe par un échappement strict.")

    # ──────────────────────────────────────────────── annexe C
    F.section("Annexe C — Catalogue, parcours, inventaire des routes", cle="annexe.C")
    F.p("Le catalogue en chiffres, calculés depuis le script d'ensemencement — ce qui veut dire que "
        "ce que le client verra est ce qui est écrit ici, et non ce qu'un export a déclaré un jour.")
    F.tableau(["Grandeur", "Valeur", "Détail"],
              [["produits", nombres_fr(v("produits")), f"{v('marques')} marques, {v('univers')} univers"],
               ["prix le plus bas", dt(c("prix_min")), "le plus petit montant du catalogue"],
               ["prix le plus haut", dt(c("prix_max")), "le plus grand montant du catalogue"],
               ["prix courant", dt(c("prix_median")), "médiane, pas moyenne — le catalogue est asymétrique"],
               ["en promotion", nombres_fr(c("en_promo")), f"remise moyenne {c('promo_moyenne_pct')} %"],
               ["sans visuel", nombres_fr(c("seuls_sans_image")), "retombée sur l'image d'univers"],
               ["en rupture à la préparation", nombres_fr(c("ruptures_simulees")),
                "état du fichier de référence, pas un état de stock réel"],
               ["faible stock à la préparation", nombres_fr(c("faible_stock_simule")), "même réserve"],
               ["répartition par univers", ", ".join(f"{k} {n}" for k, n in c("par_univers").items()),
                "le visage pèse le tiers du catalogue"],
               ["cinq premières marques", ", ".join(f"{k} {n}" for k, n in list(c("par_marque").items())[:5]),
                f"sur {v('marques')} marques"]],
              cle="annexeC.catalogue", titre="Le catalogue, mesuré", largeurs=[3.0, 4.2, 3.8],
              legende="Les montants sont des entiers de millimes dans la base et sont formatés ici en "
                      "dinars tunisiens à trois décimales, sans arrondi intermédiaire. Les deux "
                      "lignes de stock sont un état du fichier de référence : le stock réel appartient "
                      "à l'officine, et le document ne l'invente pas.")
    F.p("L'inventaire des pages ferme la question « qu'est-ce qui est publié ? ». La liste est "
        "produite en parcourant `src/app`, avec le fichier source de chaque route ; elle inclut les "
        "pages d'information, qui ne sont pas des pages de commerce.")
    routes = [[r["route"], r["file"], "dynamique" if r["dyn"] else "statique"] for r in fx.routes]
    F.tableau(["Route", "Fichier", "Rendu"], routes, cle="annexeC.routes",
              titre=f"Les {v('routes')} pages, route par route", largeurs=[3.4, 6.6, 1.6], nowrap=True,
              legende="La colonne « rendu » distingue une page dont les données viennent de la base à "
                      "chaque visite d'une page figée à la construction. Chaque ligne se vérifie en "
                      "ouvrant le fichier cité.")
    api = [[a["method"], a["path"], a["file"]] for a in fx.apis]
    F.tableau(["Méthode", "Chemin", "Fichier"], api, cle="annexeC.api",
              titre=f"Les {v('endpoints')} points d'entrée de l'API", largeurs=[1.4, 4.0, 6.0],
              nowrap=True,
              legende="Cinq points d'entrée pour un site qui n'a pas d'application mobile : la "
                      "surface exposée est volontairement petite.")

    F.p("Le catalogue intégral, tel que le script d'ensemencement l'écrit. Cette liste est le "
        "contrôle le plus brut du mémoire : elle compare, produit par produit, ce que le fichier de "
        "référence annonce et ce que la base reçoit.")
    F.sous("Catalogue complet", cle="annexeC.catalogue_complet")
    prod = []
    for p_ in fx.products:
        prod.append([p_["name"], p_["brand"], p_["universe"], p_["category"],
                     nombres_fr(p_["price"] / 1000, decimales=3), "oui" if p_["compare"] else "non",
                     "oui" if p_["featured"] else "non"])
    F.tableau(["Produit", "Marque", "Univers", "Rayon", "Prix (DT)", "En promo", "Vedette"], prod,
              cle="annexeC.produits", titre=f"Les {v('produits')} références du catalogue",
              largeurs=[4.6, 2.0, 1.6, 2.6, 1.4, 1.2, 1.0], nowrap=True, cesser=44,
              legende="Sept colonnes, quatre-vingt-une lignes, zéro produit inventé : la liste est "
                      "celle que `src/db/seed.ts` insère, lue ligne à ligne.")

    F.sous("Le plan de rayon complet", cle="annexeC.rayons")
    F.p(f"Sept univers, {v('sous_categories')} sous-rayons déclarés dans le script "
        f"d'ensemencement, {v('categories_total')} lignes de catégorie au total dans la base (les "
        "univers sont stockés dans la même table, marqués par l'attribut `isUniverse`). Le plan est "
        "donné tel quel : c'est lui qui décide de la profondeur de la navigation.")
    F.tableau(["Univers", "Sous-rayons"],
              [[u["name"], ", ".join(u.get("children", [])) or "—"] for u in fx.universes],
              cle="annexeC.rayons_liste", titre="Le plan de rayon, univers par univers",
              largeurs=[2.4, 9.2], nowrap=True,
              legende="Un univers sans sous-rayon reste navigable : la table est une arborescence, "
                      "pas une obligation de profondeur.")

    # ──────────────────────────────────────────────── annexe D
    F.section("Annexe D — Les vingt-quatre récits du backlog", cle="annexe.D")
    F.p("Le backlog intégral, tel qu'il a été écrit en S0 et tel qu'il a été tenu. Vingt-quatre "
        "récits, six épopées, et pour chacun ce qu'il reçoit, ce qu'il rend, le sprint qui l'a "
        "livré, la section du mémoire qui en traite, la planche qui l'illustre, le fichier qui le "
        "réalise et la vérification qui le tient. Les deux colonnes d'estimation sont déclaratives "
        "(échelle 0 à 1) : elles servent à ordonner le travail, pas à rendre un compte d'heures.")
    for us in BACKLOG:
        F.sous(f"{us['id']} — {us['titre']}", cle=f"annexe.D.{us['id']}")
        F.tableau(["Champ", "Contenu"],
                  [["Épopée", f"{us['epopee']} · {EPOPEES.get(us['epopee'], '—')}"],
                   ["Sprint", us["sprint"]],
                   ["Reçoit", us["regoit"]],
                   ["Rend", us["rend"]],
                   ["Valeur estimée", f"{nombres_fr(us['valeur'], decimales=2)} (échelle déclarée 0–1)"],
                   ["Effort estimé", f"{nombres_fr(us['effort'], decimales=2)} (même échelle)"],
                   ["Section du mémoire", us["section"]],
                   ["Planches", ", ".join(f"`{f}`" for f in us["figures"]) or "—"],
                   ["Fichiers", ", ".join(f"`{f}`" for f in us["fichiers"])],
                   ["Symboles", ", ".join(f"`{s}`" for s in us["symboles"])],
                   ["Vérification", f"`{us['test']}`"],
                   ["Glissade du diaporama", us["slide"]]],
                  cle=f"annexeD.{us['id']}", titre=f"Fiche {us['id']}", largeurs=[2.4, 9.2],
                  legende="Fiche produite par `rapport/trace.py` ; le harnais vérifie que chaque "
                          "fichier et chaque symbole citées existent.")
    F.p(f"Répartition, calculée sur ces vingt-quatre lignes : {len(EPOPEES)} épopées, "
        f"{len(set(u['sprint'] for u in BACKLOG))} sprints utilisés, "
        f"{sum(1 for u in BACKLOG if not u['fichiers'])} récit sans fichier de réalisation. Ce "
        "dernier nombre est le seul que le lecteur a intérêt à vérifier : un récit sans gisement est "
        "une intention, et le document n'en publie pas.")

    # ──────────────────────────────────────────────── annexe E
    F.section("Annexe E — Protocoles de vérification et commandes", cle="annexe.E")
    F.p("Cette annexe donne à lire les commandes exactes et ce qu'elles écrivent. Elle redouble "
        "`REPRO.md` par dessein : le lecteur du PDF ne doit pas avoir à ouvrir le dépôt pour savoir "
        "quoi taper.")
    F.tableau(["Commande", "Ce qu'elle fait", "Sortie attendue", "Budget"],
              [["python3 rapport/facts.py", "relit le dépôt, écrit audit/facts.json",
                f"{len(fx.f)} faits, {len(fx.tables)} tables", "< 5 s"],
               ["python3 rapport/build.py --dry-run", "planches, texte, grille de placage sans PDF",
                "creux et cotes, page par page", "< 30 s"],
               ["python3 rapport/build.py", "compose, place, scelle le PDF",
                "rapport/PDF/Cleopatre-rapport.pdf", "< 10 min"],
               ["python3 rapport/build.py --determinisme", "deux builds, empreintes comparées",
                "audit/determinisme.txt", "< 2 × 10 min"],
               ["python3 qa.py", "premier harnais, lecture par `pypdf`", "zéro défaut, sortie 0",
                "< 3 min"],
               ["python3 qa2.py", "second harnais, implémentation indépendante",
                "accord avec qa.py", "< 3 min"],
               ["python3 jury.py", "questions du jury, réponses, renvois", "audit/kit/questions.md",
                "< 10 s"]],
              cle="annexeE.commandes", titre="Les sept commandes du kit", largeurs=[3.6, 3.8, 3.0, 1.2],
              nowrap=True,
              legende="Les durées sont des budgets, pas des promesses : mesurées à chaque build et "
                      "consignées dans `audit/budgets.json`.")
    F.sous("Les vingt-cinq invariants et leur exécutant", cle="annexeE.invariants")
    F.p("La table est générée depuis `rapport/invariants.py`, qui refuse l'import si un invariant "
        "n'a pas d'exécutant ou si un invariant n'est couvert par aucune porte. Elle donne à lire, "
        "pour chaque propriété, la commande qui la contrôle et le fichier d'audit où sa trace est "
        "posée.")
    F.tableau(["Clé", "Nom", "Énoncé vérifiable", "Famille", "Exécutant", "Preuve"],
              [[i["cle"], i["nom"], i["enonce"], i["famille"], f"`{i['executant']}`",
                f"`{i['preuve']}`"] for i in INVARIANTS],
              cle="annexeE.inv", titre="Les vingt-cinq invariants du kit",
              largeurs=[0.9, 2.2, 5.6, 1.0, 2.6, 2.4], cesser=22,
              legende="Familles : vérité (ce qui est affirmé vient du dépôt), forme (le rendu tient "
                      "ses cotes), langue (les lois sont exécutées), preuve (le contrôle est "
                      "contrôlé). Un invariant sans exécutant rend le fichier importable en erreur.")
    F.sous("Dix règles de conduite SI/ALORS", cle="annexeE.sialors")
    F.tableau(["Si", "Alors", "Et", "Garde-fou"],
              [[a, b_, c_, f"`{d}`"] for a, b_, c_, d in SIALORS],
              cle="annexeE.si_alors", titre="Les dix règles SI/ALORS du §7",
              largeurs=[2.6, 3.4, 3.4, 2.4],
              legende="Ces dix règles sont ce qui remplace la bonne volonté : chacune a un exécutant "
                      "dans le dépôt, et l'exécutant refuse la composition au lieu de la commenter.")
    F.sous("Les schémas de validation des frontières", cle="annexeE.zod")
    F.p(f"{v('schemas_zod')} schémas de validation bornent les saisies du dépôt ; "
        f"{v('actions_zod')} des {v('actions')} actions en appellent un, directement ou par "
        "l'intermédiaire d'un auxiliaire du même fichier. Le contrôle n'est pas une question de "
        "goût : la surface d'écriture publique est exactement la différence des deux nombres.")
    F.tableau(["Schéma exporté", "Ligne"],
              [[s, str(l)] for s, l in sorted(SCHEMAS_ZOD.items(), key=lambda kv: kv[1])],
              cle="annexeE.zod_liste", titre=f"Les {v('schemas_zod')} schémas, avec leur ligne de définition",
              largeurs=[7.0, 1.6], nowrap=True,
              legende="Noms lus dans `src/lib/validation.ts`. Un schéma sans usage serait visible "
                      "ici et dans la matrice des actions du §IV.5 — c'est la comparaison des deux "
                      "listes qui est intéressante.")

    F.sous("Règles d'arrêt", cle="annexeE.stop")
    F.liste([f"{situation} — {consequence}" for situation, consequence in REGLES_STOP])

    F.p("Ce que la vérification refuse, en trois exemples pris dans le code du harnais : un chiffre "
        "du document qui ne correspond plus au dépôt, une figure citée sans plaque, un espace "
        "insécable manquant avant une ponctuation haute. Dans les trois cas le résultat est un échec "
        "et un message, jamais un avertissement. Le refus est ce qui distingue un harnais d'un "
        "compteur.")

    # ──────────────────────────────────────────────── annexe F
    F.section("Annexe F — Traçabilité : récit, section, figure, preuve", cle="annexe.F")
    F.p("La table de traçabilité est l'objet qui autorise à écrire que ce document n'a pas été "
        "fabriqué à l'envers. Elle relie, pour chaque récit, la section du mémoire qui en traite, la "
        "plaque qui l'illustre, le fichier qui le réalise et la vérification qui le tient. Elle est "
        "produite par `rapport/trace.py` et recoupée à la construction : une ligne sans section, ou "
        "une section sans ligne, arrête le build.")
    F.tableau(["Récit", "Section", "Planches", "Fichiers", "Symboles", "Vérification"],
              [[u["id"], u["section"], ", ".join(u["figures"]) or "—",
                ", ".join(f.split("/")[-1] for f in u["fichiers"]), ", ".join(u["symboles"]),
                u["test"].split(":")[-1]]
               for u in BACKLOG],
              cle="annexeF.trace", titre="Traçabilité des vingt-quatre récits",
              largeurs=[1.0, 1.0, 1.8, 3.0, 2.8, 2.2], nowrap=True,
              legende=f"{_relations()} relations dans les deux sens, {len(BACKLOG)} récits, "
                      f"{len({f for u in BACKLOG for f in u['figures']})} plaques appelées. Le compte "
                      "est recalculé à chaque composition : une relation rompue empêche l'impression.")
    F.figure("fig54")
    F.sous("Correspondance avec le diaporama", cle="annexeF.deck")
    F.p("Le diaporama de soutenance n'est pas un résumé du mémoire : il en est la seconde "
        "implémentation. Chaque glissade renvoie à une section, et chaque section utile au mémoire a "
        "au moins une glissade. La table est générée depuis le même fichier que les deux objets, ce "
        "qui rend le désaccord impossible sans échec de build.")
    F.tableau(["Récit", "Section", "Glissade", "Planches communes"],
              [[u["id"], u["section"], u["slide"], ", ".join(f"`{f}`" for f in u["figures"]) or "—"]
               for u in BACKLOG],
              cle="annexeF.deck", titre="Récit par récit : section de texte et glissade",
              largeurs=[1.2, 1.4, 1.4, 7.6], nowrap=True, cesser=32,
              legende=f"{len(BACKLOG)} récits, {len({u['slide'] for u in BACKLOG})} glissades "
                      "dédiées. Une glissade sans récit porté est une diapositive décorative : le "
                      "harnais la refuse.")

    F.encadre("Comment vérifier ce document en une soirée",
              "Reprendre trois lignes au hasard de l'annexe F, ouvrir les fichiers cités, comparer. "
              "Puis lancer les trois commandes du §REPRO et comparer l'empreinte du PDF avec celle "
              "de `audit/determinisme.txt`. Si les deux correspondent, ce mémoire est reproductible. "
              "Si elles diffèrent, il ne l'est pas, et le reste de la lecture n'a plus d'objet.")

    # ──────────────────────────────────────────────── résumés
    # le dos du document sort de la numérotation : « VI.9 Quatrième de couverture » serait un
    # numéro que le plan du mémoire ne contient pas
    F.hors_numerotation()
    F.saut()
    F.section("Résumé", cle="resume.fr")
    F.p("Ce mémoire rend compte de la conception et de la réalisation d'une plateforme de commerce "
        f"en ligne pour une parapharmacie tunisienne à deux comptoirs. L'application couvre un "
        f"catalogue de {v('produits')} références, la recherche multi-axes, le panier, la commande "
        "avec paiement à la livraison, l'administration des statuts, la facturation et un journal "
        f"d'audit ; elle tient sur {v('tables')} tables, {v('actions')} fonctions d'action et "
        f"{v('routes')} pages, dans un cadre unique côté serveur. Trois contraintes du métier ont "
        "commandé l'architecture : une monnaie à trois décimales, un stock partagé entre le rayon "
        "et le net, et l'absence d'intermédiaire humain dans la vente à distance. Le document "
        "s'impose en outre une discipline de preuve : chaque chiffre est relu dans le dépôt au "
        "moment de la composition, deux harnais indépendants contrôlent le rendu, et ce qui n'a pas "
        "été réalisé est écrit. Les limites — pas de passerelle bancaire, arabe non activé, "
        "exploitabilité non mesurée — y sont traitées comme des résultats, non comme des réserves.")
    F.p("Mots-clés : commerce électronique, parapharmacie, TypeScript, PostgreSQL, verrouillage de "
        "ligne, accessibilité, vérification automatique, traçabilité.")

    F.section("Abstract", cle="resume.en")
    F.p("This report documents the design and implementation of an e-commerce platform for a "
        f"Tunisian parapharmacy running two counters. The application covers a catalogue of "
        f"{v('produits')} items, multi-axis discovery, cart, ordering with cash on delivery, "
        f"back-office status management, invoicing and an audit journal; it rests on {v('tables')} "
        f"tables, {v('actions')} server functions and {v('routes')} pages within a single "
        "server-side framework. Three business constraints drove the architecture: a currency with "
        "three decimal digits, stock shared between the sales floor and the web channel, and the "
        "absence of a human intermediary in remote sales. The document also imposes an evidentiary "
        "discipline: every figure is re-read from the repository at composition time, two "
        "independent harnesses check the rendered output, and what was not implemented is stated as "
        "such. The limitations — no payment gateway, Arabic not enabled, no production measurement — "
        "are reported as results rather than as reservations.", langue="en")
    F.p("Keywords: e-commerce, parapharmacy, TypeScript, PostgreSQL, row-level locking, "
        "accessibility, automated verification, traceability.", langue="en")

    # ──────────────────────────────────────────────── quatrième de couverture
    F.saut()
    F.section("Quatrième de couverture", cle="quatrieme")
    F.couverture([
        ("couv_sous", "Ce document ne demande pas d'être cru."),
        ("couverture", "Trois commandes, et il est rejouable."),
        ("couv_sous", f"{len(REGISTRE)} planches vectorielles · {v('tables')} tables relues · "
                      f"{v('actions')} actions auditées · 30 glissades · 25 invariants · 27 portes"),
        ("couv_pied", "python3 rapport/build.py && python3 qa.py && python3 qa2.py"),
    ])
    F.p("Ce mémoire décrit un objet vérifiable plutôt qu'une performance. Il montre comment trois "
        "contraintes de métier — une monnaie à trois décimales, un stock partagé entre le comptoir "
        "et le net, un conseil qui ne peut pas passer par un écran — ont produit une architecture, "
        "et comment cette architecture a été tenue sous le contrôle d'un harnais qui refuse "
        "d'imprimer une affirmation fausse.")
    F.p("Il s'adresse à trois lecteurs. À l'enseignant qui cherche la méthode : les parties II et V "
        "donnent les décisions, les rejets et les preuves. Au praticien qui cherche le métier : les "
        "parties I et III disent ce qu'une parapharmacie en ligne doit refuser pour rester "
        "crédible. À l'étudiant qui cherche un chemin : le dépôt est complet, les commandes sont au "
        "nombre de trois, et chaque chiffre de ce document a été relu pour lui.")
    F.p("Ce qui n'a pas été fait est écrit : pas de passerelle bancaire, pas d'arabe activé, pas de "
        "conteneur, pas de mesure d'exploitation, pas de migrations versionnées. Ces absences sont "
        "le travail de celles et ceux qui reprendront l'objet — et la garantie donnée au lecteur que "
        "ce qu'il lit n'a pas été enjolivé.")
    F.note("Étiquette de version : v1.0-final, scellée à la date du dernier build consigné dans "
           "`audit/dernier-build.json`, après évaluation des vingt-sept portes et mention signée "
           "« rien à ajouter ». Ce qui viendrait après relèverait d'un nouveau cycle, non d'un "
           "correcteur.")
