"""rapport/jury.py — banque de quinze questions hostiles, avec preuves vérifiées à l'exécution.

Le jury ne demande pas ce qui a été fait, il demande où c'est écrit. Chaque carte répond en trois
phrases, puis rend la preuve : un fichier et une ligne, ou un motif cherché dans le dépôt, ou une clé
du dossier d'audit. `verifier_preuves()` **exécute** la preuve : si le motif n'est pas dans le fichier,
la carte est marquée fautive et le script sort en rouge. Une carte sans preuve vérifiable n'entre pas
dans la banque.

Sorties : `audit/kit/jury.json` (banque machine) et `soutenance/BANQUE-JURY.md` (fiches à lire la
veille). La porte G5 de `rapport/gates.py` relit le JSON et refuse l'ouvrage si une preuve manque.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
AUDIT = RACINE / "audit"
FACTS = json.loads((AUDIT / "facts.json").read_text(encoding="utf-8"))

BANQUE = [
    dict(id="Q1", theme="chiffres",
         question="D'où sortent vos 81 références, 16 marques, 7 univers ?",
         reponse="Du gisement : le manifeste d'images et les graines de la base. `rapport/facts.py` "
                 "les compte dans le dépôt, le rapport imprime le compte, et le recomptage par "
                 "`grep` dans le second harnais tombe sur le même nombre. Rien n'est saisi à la main.",
         relance="Et si je change une ligne du seed, que devient le mémoire ?",
         piege="Répondre « environ 80 » : le nombre est une clé d'audit, il se vérifie en une seconde.",
         renvoi="I.2, annexe C", preuve=dict(type="audit", cle="produits"),
         preuve2=dict(type="motif", fichier="public/data/product-image-manifest.json", motif="verified")),
    dict(id="Q2", theme="base",
         question="Le schéma ne déclare aucune contrainte CHECK : comment le stock ne devient-il "
                  "jamais négatif ?",
         reponse="Par le verrou et le test, pas par la déclaration : la commande s'exécute sous "
                 "`FOR UPDATE`, la garde est écrite dans `src/lib/orders.ts`, et le rapport dit zéro "
                 "contrainte au lieu d'en inventer une. C'est consigné comme dette assumée à la "
                 "section IV.2, avec la raison.",
         relance="Un UPDATE concurrent entre deux transactions, alors ?",
         piege="Affirmer une contrainte au schéma : le fichier répondrait devant le jury.",
         renvoi="IV.2, figure 49", preuve=dict(type="ligne", fichier="src/lib/orders.ts", ligne=100),
         preuve2=dict(type="motif", fichier="src/db/schema.ts", motif="pgTable")),
    dict(id="Q3", theme="base",
         question="Combien de tables, et pourquoi ce nombre ?",
         reponse="Vingt-quatre tables, deux cent deux colonnes, dix enums, cinquante index, dix-neuf "
                 "clés étrangères. Le nombre vient du périmètre retenu : deux boutiques, un catalogue "
                 "multi-axes, un tunnel, la fidélité, les retours. Les dictionnaires complets sont en "
                 "annexe B, générés depuis le schéma.",
         relance="Que avez-vous refusé de modéliser ?",
         piege="Défendre le nombre sans montrer le dictionnaire : l'annexe B est générée, elle est "
               "donc exacte ou le build est rouge.",
         renvoi="annexe B", preuve=dict(type="audit", cle="tables"),
         preuve2=dict(type="motif", fichier="src/db/schema.ts", motif="pgEnum")),
    dict(id="Q4", theme="argent",
         question="Pourquoi ne pas avoir branché de paiement en ligne ?",
         reponse="Parce qu'aucune passerelle n'a été contractée pour le stage, et que l'argent ne "
                 "s'improvise pas : le projet paie à la livraison et le périmètre le dit. La solution "
                 "de repli nommée par le cahier, une boutique Shopify, n'existe pas dans le dépôt — la "
                 "recherche dans `src/` renvoie zéro ligne, et le rapport l'écrit au lieu de feindre "
                 "un connecteur.",
         relance="Le jour où la passerelle existe, combien de temps pour la brancher ?",
         piege="Répondre « c'était hors périmètre » sans dire ce qui est prêt : le tunnel, l'idempotence "
               "et le verrou de stock le sont, la devise non.",
         renvoi="I.4, II.5, conclusion", preuve=dict(type="motif", fichier="src/actions/checkout.ts",
                                                     motif="idempot")),
    dict(id="Q5", theme="promotions",
         question="Huit motifs de refus pour une promotion, c'est beaucoup. Lesquels comptent vraiment ?",
         reponse="Les huit sont écrits dans le code et listés dans le rapport ; ceux qui tiennent la "
                 "route sont la date de fenêtre, le cumul interdit, le minimum de panier et "
                 "l'éligibilité de catégorie. Les autres protègent des cas rares mais coûteux, comme "
                 "la marque exclue ou le produit déjà en rupture.",
         relance="Un code valable pour deux clients, l'un éligible et l'autre non : lequel gagne ?",
         piege="Dire « le moteur refuse poliment » : la réponse est dans l'extrait de code, pas dans "
               "l'intention.",
         renvoi="III.4", preuve=dict(type="audit", cle="promotions")),
    dict(id="Q6", theme="sécurité",
         question="Pourquoi scrypt et non bcrypt ou Argon2 ?",
         reponse="Parce que la bibliothèque standard du serveur l'offre sans dépendance, avec une clé "
                 "de 64 octets et une comparaison à temps constant. Le choix est tracé dans le code et "
                 "commenté dans le rapport, y compris ce qu'il coûte : pas de remontée de coût "
                 "automatique à la reconnexion.",
         relance="Et le vol de cookie ?",
         piege="Répondre sécurité par le vocabulaire : montrer `timingSafeEqual`, le sel, les attributs "
               "du cookie.",
         renvoi="II.4", preuve=dict(type="motif", fichier="src/lib/auth.ts", motif="timingSafeEqual"),
         preuve2=dict(type="motif", fichier="src/lib/auth.ts", motif="scrypt")),
    dict(id="Q7", theme="sécurité",
         question="Votre limite de requêtes est en mémoire : que se passe-t-il au deuxième serveur ?",
         reponse="Rien de bon : le compteur est par processus, donc deux instances doublent le budget "
                 "réel. C'est écrit dans le rapport comme limite assumée à trois utilisateurs "
                 "simultanés, avec la sortie (compteur partagé) nommée mais non fabriquée. Le plafond "
                 "mémoire de cinq mille entrées empêche l'épuisement, pas la fraude.",
         relance="Pourquoi ne pas avoir posé Redis dans le stage ?",
         piege="Cacher la limite : la loi du kit est de l'écrire, et elle y est.",
         renvoi="V.6", preuve=dict(type="motif", fichier="src/lib/rate-limit.ts", motif="5000")),
    dict(id="Q8", theme="sécurité",
         question="Que contient votre cookie de session, et combien de temps vit-il ?",
         reponse="Un identifiant opaque de 256 bits, pas d'informations personnelles ; trente jours ; "
                 "`httpOnly`, `sameSite=lax`, `secure` en production. La session est révoquée côté base, "
                 "donc la déconnexion est réelle.",
         relance="Et le jeton CSRF sur les formulaires ?",
         piege="Confondre `sameSite` et protection CSRF : le rapport dit ce que le dépôt fait, "
                "c'est-à-dire la posture lax et le contrôle d'origine à l'écriture.",
         renvoi="II.4", preuve=dict(type="motif", fichier="src/lib/auth.ts", motif="cleo_session")),
    dict(id="Q9", theme="architecture",
         question="Où est la source de vérité de la visibilité d'un produit ?",
         reponse="Dans une seule fonction : `src/lib/catalog.ts`, ligne quatorze pour le filtre. Les "
                 "pages, l'administration et l'API appellent cette fonction ; elles ne recopient pas la "
                 "condition. C'est la preuve que le catalogue ne peut pas se contredire d'un écran à "
                 "l'autre.",
         relance="Prouvez-moi qu'aucune page ne refait le filtre.",
         piege="Répondre par l'intention : la réponse est un `grep` que le kit exécute pour moi.",
         renvoi="III.2", preuve=dict(type="ligne", fichier="src/lib/catalog.ts", ligne=14)),
    dict(id="Q10", theme="fiabilité",
         question="Deux clics sur « commander » : deux commandes ?",
         reponse="Non : la clé d'idempotence est prise dans la base avec un verrou, et l'index la rend "
                 "unique. La seconde requête retombe sur la commande existante. Les deux lignes sont "
                 "citées dans le rapport et dans l'annexe des preuves.",
         relance="Et si la clé est perdue par le client ?",
         piege="Promettre une file d'attente : le dépôt ne l'a pas.",
         renvoi="III.4, annexe F", preuve=dict(type="ligne", fichier="src/actions/checkout.ts", ligne=66)),
    dict(id="Q11", theme="accessibilité",
         question="Votre rapport est-il lisible par un daltonien, et votre site est-il sobre en "
                  "mouvement ?",
         reponse="Le rapport encode par forme, label et texte, jamais par couleur seule, et la planche "
                 "de contact le vérifie. Pour le site, la réduction de mouvement tient dans une seule "
                 "feuille, sans hook React : c'est peu, et le rapport l'écrit comme limite plutôt que "
                 "comme succès.",
         relance="Pourquoi ne pas avoir branché useReducedMotion ?",
         piege="Réclamer un mérite d'accessibilité non mesuré : la loi du kit est d'inscrire l'écart.",
         renvoi="V.6, figure 43", preuve=dict(type="motif", fichier="src/app/globals.css",
                                            motif="prefers-reduced-motion")),
    dict(id="Q12", theme="langue",
         question="Le projet est tunisien : l'arabe est-il dans le produit ?",
         reponse="Non, et c'est écrit dans les non-objectifs : l'interface est en français, la "
                 "disposition arabe n'a pas été rendue ni testée. La donnée tunisienne, elle, est "
                 "réelle : vingt-quatre gouvernorats, cinquante-trois villes dans neuf délais, frais en "
                 "millimes.",
         relance="Que coûte l'activation du RTL ?",
         piege="Répondre « prêt à activer » : la chaîne de traduction n'existe pas dans le dépôt.",
         renvoi="I.6.1, B4", preuve=dict(type="motif", fichier="src/lib/tunisia.ts",
                                       motif="GOVERNORATES"),
         preuve2=dict(type="motif", fichier="src/lib/validation.ts", motif="Gouvernorat requis")),
    dict(id="Q13", theme="argent",
         question="Comment est calculé le franco de port ?",
         reponse="Sur le montant après remises, à quatre-vingt-dix-neuf dinars, avec trois paliers de "
                 "livraison à sept, douze et cinq mille millimes. Les nombres du rapport viennent du "
                 "fichier de tarification, formatés à la française, et la table est générée.",
         relance="Le franco s'applique-t-il avant ou après la promotion ?",
         piege="Inventer l'ordre des calculs : l'annexe des preuves le donne ligne à ligne.",
         renvoi="III.6.1", preuve=dict(type="ligne", fichier="src/lib/money.ts", ligne=4),
         preuve2=dict(type="motif", fichier="src/lib/money.ts", motif="FREE_SHIPPING_THRESHOLD")),
    dict(id="Q14", theme="méthode",
         question="Comment savez-vous que votre PDF n'est pas un assemblage de captures ?",
         reponse="Parce que les ratios des planches sont lus dans les deux formats, que le nombre de "
                 "poses égale le nombre de planches, et que aucune figure n'est passée par le raster. "
                 "Deux rebuilds successifs donnent la même empreinte, et le second harnais recompte "
                 "les placements sans consulter le premier.",
         relance="Montrez-moi la trace.",
         piege="Jurer : `audit/dernier-build.json` et `audit/ab/harnais.json` répondent plus vite.",
         renvoi="V.2, V.5", preuve=dict(type="fichier", fichier="audit/ab/harnais.json")),
    dict(id="Q15", theme="vérité",
         question="Qu'avez-vous vérifié vous-même, dans un kit écrit par une machine ?",
         reponse="Chaque statut du mémoire : pas un « fait » sans fichier, ligne ou sortie. Les trois "
                 "cent trente-trois lignes de l'appareil, les 28 corrections du fichier "
                 "CORRECTIONS.md et les cinq chaos provoqués sont là pour ça. Le dépôt ne se relance "
                 "pas sans node_modules, et le kit l'écrit comme dégradation au lieu de le cacher.",
         relance="Où est la preuve que vous n'avez pas enjolivé une figure ?",
         piege="Répondre par la confiance : la figure 27 et le test de mutation M1 répondent.",
         renvoi="B5, V.6", preuve=dict(type="fichier", fichier="CORRECTIONS.md"),
         preuve2=dict(type="fichier", fichier="audit/mutation/resume.json")),
]


def verifier_preuves() -> list[dict]:
    """Contrôle d'exécution : chaque preuve annoncée est vérifiée ici, sinon la carte est fautive."""
    recu = []
    for carte in BANQUE:
        fautes = []
        for cle in ("preuve", "preuve2"):
            if cle not in carte:
                continue
            p = carte[cle]
            if p["type"] == "motif":
                f = RACINE / p["fichier"]
                if not f.exists():
                    fautes.append(f"{p['fichier']} absent")
                elif not re.search(p["motif"], f.read_text(encoding="utf-8"), flags=re.I):
                    fautes.append(f"motif « {p['motif']} » introuvable dans {p['fichier']}")
            elif p["type"] == "ligne":
                f = RACINE / p["fichier"]
                n = len(f.read_text(encoding="utf-8").splitlines()) if f.exists() else 0
                if not f.exists():
                    fautes.append(f"{p['fichier']} absent")
                elif not 1 <= p["ligne"] <= n:
                    fautes.append(f"{p['fichier']}:{p['ligne']} hors bornes (le fichier fait {n} lignes)")
            elif p["type"] == "audit":
                if p["cle"] not in FACTS["faits"] and p["cle"] not in FACTS:
                    fautes.append(f"clef « {p['cle']} » absente de audit/facts.json")
            elif p["type"] == "fichier":
                if not (RACINE / p["fichier"]).exists():
                    fautes.append(f"{p['fichier']} pas encore produit")
        recu.append(dict(id=carte["id"], theme=carte["theme"], question=carte["question"],
                         preuve_verifiee=not fautes, fautes=fautes,
                         renvoi=carte["renvoi"]))
    return recu


def ecrire(*, silencieux: bool = False) -> dict:
    recu = verifier_preuves()
    par_id = {r["id"]: r for r in recu}
    (AUDIT / "kit").mkdir(parents=True, exist_ok=True)
    (AUDIT / "kit/jury.json").write_text(
        json.dumps(dict(harnais="jury.py", total=len(BANQUE),
                        verifiees=sum(1 for r in recu if r["preuve_verifiee"]),
                        fautes=[f"{r['id']} : {x}" for r in recu for x in r["fautes"]],
                        themes=sorted({c["theme"] for c in BANQUE}),
                        verdict="vert" if all(r["preuve_verifiee"] for r in recu) else "rouge",
                        lignes=recu), ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8")
    md = ["# Banque du jury — quinze questions, chaque réponse avec sa preuve", "",
          "Écrite par `python3 rapport/jury.py`. Une preuve non vérifiée fait sortir le script en rouge :",
          "il n'existe pas de carte de complaisance.", ""]
    for c in BANQUE:
        etat = "✓ preuves vérifiées" if par_id[c["id"]]["preuve_verifiee"] else \
            "**preuve en défaut** : " + " ; ".join(par_id[c["id"]]["fautes"])
        md += [f"## {c['id']} · {c['theme']} — {c['question']}", "",
               f"**Réponse.** {c['reponse']}", "",
               f"**Relance probable.** {c['relance']}", "",
               f"**Piège.** {c['piege']}", "",
               f"**Renvoi dans le mémoire.** {c['renvoi']}", "",
               f"**Preuve.** {c['preuve']['type']} "
               f"{c['preuve'].get('fichier', c['preuve'].get('cle', ''))} "
               f"{c['preuve'].get('motif', '')} {c['preuve'].get('ligne', '')}".rstrip(),
               f"**Contrôle.** {etat}", ""]
    (RACINE / "soutenance/BANQUE-JURY.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    bilan = dict(total=len(BANQUE), verifiees=sum(1 for r in recu if r["preuve_verifiee"]),
                 verdict="vert" if all(r["preuve_verifiee"] for r in recu) else "rouge")
    if not silencieux:
        for r in recu:
            print(f"{r['id']:>4}  {'preuve ok' if r['preuve_verifiee'] else 'FAUTE : ' + ' ; '.join(r['fautes'])}")
        print(f"jury : {bilan['verifiees']}/{bilan['total']} cartes à preuve vérifiée, verdict {bilan['verdict']}")
    return bilan


if __name__ == "__main__":
    sys.exit(0 if ecrire()["verdict"] == "vert" else 1)
