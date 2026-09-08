"""rapport/invariants.py — la table des vingt-cinq invariants, source unique.

Chaque invariant est écrit avec la commande ou la fonction qui le vérifie. Ce fichier est lu par
trois consommateurs : l'annexe E du rapport (qui l'imprime), `rapport/gates.py` (qui évalue les
vingt-sept portes) et `qa.py`/`qa2.py` (qui vérifient que le PDF contient bien la liste complète).
Un invariant sans exécutant est refusé à l'import : c'est la règle « statut sans preuve = vent »,
appliquée au document lui-même.
"""
from __future__ import annotations

import re

# (clé, titre, énoncé vérifiable, famille, exécutant, preuve attendue dans audit/)
INVARIANTS: list[dict] = [
    dict(cle="INV-1", nom="Demi-carré typographique",
         enonce="Aucun bloc de texte ne dépasse la largeur utile (166 mm) et aucune ligne isolée ne "
                "termine une page : la grille est vérifiée sur le PDF, pas sur le brouillon.",
         famille="forme", executant="qa.py:check_grille", preuve="audit/qa.json"),
    dict(cle="INV-2", nom="Vectoriel sauf preuve du contraire",
         enonce="Toute planche est posée depuis son timbre PDF ; un PNG n'est collé que si le vectoriel "
                "est absent, et la dégradation est déclarée à la page.",
         famille="forme", executant="rapport/build.py:placer", preuve="audit/placements.json"),
    dict(cle="INV-3", nom="Place mesurée au millimètre",
         enonce="Chaque plaque occupe exactement la boîte réservée par le moteur de mise en page ; "
                "l'écart mesuré après placage est inférieur à 0,1 mm.",
         famille="forme", executant="qa.py:check_placements", preuve="audit/placements.json"),
    dict(cle="INV-4", nom="Zéro dégradation silencieuse",
         enonce="Toute perte de qualité (PNG, sous-échantillonnage, repli de police) écrit une ligne "
                "dans l'audit et une ligne dans le document.",
         famille="preuve", executant="qa.py:check_degradations", preuve="audit/dernier-build.json"),
    dict(cle="INV-5", nom="Chiffre greffé",
         enonce="Aucun nombre du document n'est tapé à la main : tous viennent de `audit/facts.json`, "
                "qui est recalculé avant chaque build.",
         famille="verite", executant="qa.py:check_chiffres", preuve="audit/facts.json"),
    dict(cle="INV-6", nom="Crochet = réel absent",
         enonce="Toute donnée du monde réel non contenue dans le dépôt est entre crochets, et "
                "l'inverse est vrai : rien entre crochets n'est une donnée du dépôt.",
         famille="verite", executant="qa.py:check_crochets", preuve="audit/qa.json"),
    dict(cle="INV-7", nom="Zéro copié-collé",
         enonce="Aucune phrase du document n'est reprise d'un README du dépôt ; les extraits de code "
                "sont cités avec leur fichier et leurs lignes exactes.",
         famille="verite", executant="qa.py:check_copies", preuve="audit/qa.json"),
    dict(cle="INV-8", nom="Slop à zéro",
         enonce="La liste des tournures creuses est exécutée : occurrence trouvée = refus de "
                "composer, pas un avertissement.",
         famille="langue", executant="rapport/doc.py:verifier_langue", preuve="audit/langue.json"),
    dict(cle="INV-9", nom="Synonymes interdits",
         enonce="Les anglicismes de domaine sont refusés dans la prose ; les identifiants du dépôt, "
                "en monospace, sont exemptés et cette exemption est comptée.",
         famille="langue", executant="rapport/doc.py:verifier_langue", preuve="audit/langue.json"),
    dict(cle="INV-10", nom="Insécables tenues",
         enonce="Aucun ` ; : ! ? »` sans espace insécable devant, dans le texte extrait du PDF, hors "
                "span monospace.",
         famille="langue", executant="qa2.py:check_insecables", preuve="audit/qa2.json"),
    dict(cle="INV-11", nom="Nombres à la française",
         enonce="Les nombres sont écrits avec la virgule décimale et l'espace des milliers ; les "
                "montants en dinars à trois décimales.",
         famille="langue", executant="rapport/doc.py:nombres_fr", preuve="audit/qa.json"),
    dict(cle="INV-12", nom="Inoculation trois sur trois",
         enonce="Les trois sujets pièges (place de marché, paiement, charge) sont traités chacun à "
                "la place convenue, et non enfouis.",
         famille="verite", executant="qa.py:check_inoculation", preuve="audit/qa.json"),
    dict(cle="INV-13", nom="Une plaque, un appel",
         enonce="Toute figure du registre est citée exactement une fois, et toute citation pointe une "
                "plaque du registre.",
         famille="preuve", executant="rapport/build.py:construire", preuve="audit/dernier-build.json"),
    dict(cle="INV-14", nom="Ancres réelles",
         enonce="Chaque lien du sommaire et des listes a une destination posée dans le PDF ; un renvoi "
                "sans ancre arrête la composition.",
         famille="preuve", executant="rapport/build.py:resoudre_liens", preuve="audit/liens.json"),
    dict(cle="INV-15", nom="Signets trois niveaux",
         enonce="Le PDF porte un signet par partie, section et objet numéroté, triés par page.",
         famille="forme", executant="rapport/build.py:placer", preuve="audit/signets.json"),
    dict(cle="INV-16", nom="Métadonnées et horodatage figés",
         enonce="Titre, auteur, sujet, mots-clés, producteur sont posés ; les dates du fichier sont "
                "figées pour que le déterminisme soit possible.",
         famille="preuve", executant="rapport/build.py:placer", preuve="audit/dernier-build.json"),
    dict(cle="INV-17", nom="Déterminisme par l'empreinte",
         enonce="Deux builds consécutifs du même dépôt produisent le même SHA-256, sinon le PDF n'est "
                "pas écrit.",
         famille="preuve", executant="rapport/build.py:determinisme", preuve="audit/determinisme.txt"),
    dict(cle="INV-18", nom="Rapport noir et blanc",
         enonce="Aucune information n'est portée par la couleur seule : retirée la couleur, l'objet "
                "reste lisible (forme, libellé, position).",
         famille="forme", executant="qa.py:check_nb", preuve="audit/qa.json"),
    dict(cle="INV-19", nom="Daltonisme",
         enonce="Les paires rouge/vert du document sont distinguées par une marque de forme en plus de "
                "la teinte.",
         famille="forme", executant="qa.py:check_formes", preuve="audit/qa.json"),
    dict(cle="INV-20", nom="Budgets tenus, pas négociés",
         enonce="Poids du PDF, du diaporama, durées de build, de figures et de QA sont mesurés et "
                "inférieurs aux seuils du cahier des charges.",
         famille="preuve", executant="rapport/gates.py:check_budgets", preuve="audit/budgets.json"),
    dict(cle="INV-21", nom="Double harnais convergent",
         enonce="`qa.py` et `qa2.py`, implémentés indépendamment, rendent le même verdict ; leur "
                "différence est imprimée, pas moyennée.",
         famille="preuve", executant="rapport/ab.py:comparer", preuve="audit/ab/harnais.json"),
    dict(cle="INV-22", nom="Chaos conduit",
         enonce="Les quatre injections de panne produisent le comportement exigé : refus, message, "
                "code de sortie non nul.",
         famille="preuve", executant="rapport/chaos.py:lancer", preuve="audit/chaos/C1.json"),
    dict(cle="INV-23", nom="Mutation du contrôle",
         enonce="Trois sabotages du harnais sont détectés trois fois ; un contrôle qui reste vert est "
                "une faute du kit.",
         famille="preuve", executant="rapport/mutation.py:lancer", preuve="audit/mutation/M1.json"),
    dict(cle="INV-24", nom="Diaporama sans lien invérifié",
         enonce="Aucune URL n'est posée dans le deck si elle n'a pas été ouverte ; les QR et renvois "
                "sont marqués comme à confirmer quand ils ne l'ont pas été.",
         famille="verite", executant="soutenance/slides.py:fabriquer", preuve="audit/qa2.json"),
    dict(cle="INV-25", nom="Secrets à zéro",
         enonce="Aucune valeur sensible n'est committée : la recherche de motifs (clés, mots de passe, "
                "URL de connexion avec identifiant) rend 0 occurrence dans le kit.",
         famille="verite", executant="qa.py:check_secrets", preuve="audit/qa.json"),
]

PORTES: list[dict] = [
    # (porte, intitulé, invariants qui la tiennent, preuve écrite)
    ("G1", "Démarrage : sept actes écrits avant le code", ["INV-5", "INV-7"], "audit/B0-boot.md"),
    ("G2", "Pré-mortem de huit morts", ["INV-12"], "audit/B0-boot.md"),
    ("G3", "Plan et budget chiffrés tenus", ["INV-20"], "audit/budgets.json"),
    ("G4", "Audit du dépôt contre le cahier", ["INV-5", "INV-6"], "audit/facts.json"),
    ("G5", "Banque de quinze questions de jury", ["INV-12"], "audit/kit/jury.json"),
    ("G6", "Grille de notation auto-appliquée", ["INV-8", "INV-11"], "audit/kit/rubrique.md"),
    ("G7", "Pare-feu de périmètre et non-objectifs", ["INV-6"], "audit/B0-boot.md"),
    ("G8", "Rapport composé entre le plancher et le plafond de pages, tout vectoriel",
     ["INV-1", "INV-2", "INV-3", "INV-4"],
     "audit/dernier-build.json"),
    ("G9", "Zéro copié-collé", ["INV-7"], "audit/qa.json"),
    ("G10", "Lois de langue exécutées", ["INV-8", "INV-9", "INV-10"], "audit/langue.json"),
    ("G11", "Inoculation trois sur trois", ["INV-12"], "audit/qa.json"),
    ("G12", "Registre de figures complet", ["INV-13"], "audit/dernier-build.json"),
    ("G13", "Sommaire et listes cliquables", ["INV-14", "INV-15"], "audit/liens.json"),
    ("G14", "Accessibilité et non-couleur", ["INV-18", "INV-19"], "audit/qa.json"),
    ("G15", "Cinq applaudissements scriptés", ["INV-24"], "soutenance/JOURJ.md"),
    ("G16", "Diaporama de trente glissades", ["INV-24"], "soutenance/Cleopatre-soutenance.pptx"),
    ("G17", "Morph réel dans le fichier", ["INV-24"], "audit/qa2.json"),
    ("G18", "Cinq zooms de détail", ["INV-3"], "audit/qa2.json"),
    ("G19", "Minutage à quatorze minutes trente", ["INV-20"], "soutenance/JOURJ.md"),
    ("G20", "Dix dix dix mesurés", ["INV-20"], "audit/qa2.json"),
    ("G21", "Démo en trois chemins, zéro réseau", ["INV-6"], "soutenance/JOURJ.md"),
    ("G22", "Harnais double convergent", ["INV-21"], "audit/ab/harnais.json"),
    ("G23", "Quatre chaos conduits", ["INV-22"], "audit/chaos/resume.json"),
    ("G24", "Trois mutations détectées", ["INV-23"], "audit/mutation/resume.json"),
    ("G25", "Épuisement signé", ["INV-7", "INV-17"], "audit/RIEN-A-AJOUTER.md"),
    ("G26", "Kit et war-room livrés", ["INV-25"], "soutenance/JOURJ.md"),
    ("G27", "Gel scellé et étiquette poussée", ["INV-16", "INV-17"], "audit/sceau.json"),
]

# SI / ALORS du §7 : dix règles de conduite, chacune avec son garde-fou
SIALORS: list[tuple[str, str, str]] = [
    ("SI une mesure manque", "ALORS le document écrit « à mesurer »", "jamais une valeur voisine",
     "qa.py:check_placeholders"),
    ("SI une plaque est absente", "ALORS le build refuse de démarrer", "et nomme la plaque",
     "rapport/doc.py:Creux"),
    ("SI un PNG remplace un vectoriel", "ALORS la dégradation est imprimée à la page",
     "et consignée dans l'audit", "qa.py:check_degradations"),
    ("SI un chiffre du texte diverge du dépôt", "ALORS la QA rougit", "et le build est repris",
     "qa.py:check_chiffres"),
    ("SI une tournure creuse apparaît", "ALORS la composition lève", "et l'auteur réécrit",
     "rapport/doc.py:verifier_langue"),
    ("SI un lien n'a pas d'ancre", "ALORS la composition lève", "et non un avertissement",
     "rapport/contenu.py:autoverif"),
    ("SI un build dépasse son budget", "ALORS la réduction convenue s'applique",
     "et le nouveau temps est consigné", "rapport/build.py:construire"),
    ("SI les deux harnais diffèrent", "ALORS la QA rougit", "et la divergence est publiée",
     "rapport/ab.py:comparer"),
    ("SI une donnée réelle manque", "ALORS elle reste entre crochets", "et n'est pas devinée",
     "qa.py:check_crochets"),
    ("SI un secret est committé", "ALORS la QA échoue", "et le scellement est refusé",
     "qa.py:check_secrets"),
]

REGLES_STOP: list[tuple[str, str]] = [
    ("Un invariant sans exécutant", "porte non évaluée : gel refusé"),
    ("Deux harnais en désaccord", "round d'assaut supplémentaire, pas de mise en page corrective"),
    ("Trois signaux d'alerte cumulés", "arrêt du cycle, réécriture de la section fautive"),
    ("Dépassement de budget non résolu", "le livrable est livré avec le dépassement écrit, jamais "
                                         "amorti en silence"),
]


def par_famille() -> dict[str, int]:
    out: dict[str, int] = {}
    for inv in INVARIANTS:
        out[inv["famille"]] = out.get(inv["famille"], 0) + 1
    return out


def autoverifier() -> None:
    """Contrôle interne du fichier : pas de doublon, pas d'exécutant manquant, portes closes."""
    vus = [i["cle"] for i in INVARIANTS]
    if len(vus) != 25 or len(set(vus)) != 25:
        raise AssertionError(f"{len(vus)} invariants déclarés, attendu 25 sans doublon")
    for i in INVARIANTS:
        if not re.match(r"^[\w./-]+:\w+$", i["executant"]):
            raise AssertionError(f"{i['cle']} : exécutant mal formé ({i['executant']})")
        if not i["preuve"].startswith("audit/"):
            raise AssertionError(f"{i['cle']} : la preuve doit être un fichier d'audit")
    cles = set(vus)
    for porte, _, invs, preuve in PORTES:
        if not preuve.startswith("audit/") and not preuve.endswith((".pptx", ".md")):
            raise AssertionError(f"{porte} : preuve non fichier")
        for x in invs:
            if x not in cles:
                raise AssertionError(f"{porte} référence {x}, invariant inexistant")
    couvertes = {x for _, _, invs, _ in PORTES for x in invs}
    if cles - couvertes:
        raise AssertionError("invariants sans porte : " + ", ".join(sorted(cles - couvertes)))
    if len(PORTES) != 27:
        raise AssertionError(f"{len(PORTES)} portes, attendu 27")


autoverifier()
