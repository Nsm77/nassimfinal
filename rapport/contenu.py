"""rapport/contenu.py — le fabricant de flux : contenu → flowables, avec compteurs tenus.

Deux règles structurelles, parce qu'elles tuent deux fautes connues (§9) :

* **la numérotation est calculée** : parties, sections, figures, tableaux, extraits portent des
  compteurs détenus ici. Aucune étiquette n'est tapée à la main — donc aucune dérive possible ;
* **les renvois sont résolus en passes** : `[[R:cle]]` devient « p. N », N lu dans le registre de
  la passe précédente. Un renvoi inconnu lève `RefManquante` : le document se construit complet
  ou ne se construit pas.

Le texte passe par `doc.appliquer_loi_langue` (insécables) puis `doc.verifier_langue` : écrire
« soigné » ne suffit pas, il faut que la regex le dise. Une figure citée qui n'existe pas dans le
registre fait échouer la passe, au même titre qu'un chiffre faux.
"""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, NextPageTemplate, PageBreak, Paragraph, Spacer, Table

from rapport import doc
from rapport.doc import (
    appliquer_mono,
    Creux, Signet, LARGEUR_TEXTE, appliquer_loi_langue, echapper,
                         retirer_code,
                         verifier_langue, nombres_fr, dt, style_tableau, INS)
from rapport.mpl import REGISTRE as FIGURES_REG

RACINE = Path(__file__).resolve().parent.parent
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]


class RefManquante(RuntimeError):
    pass


class LangueRefusee(RuntimeError):
    pass


class Fab:
    """Fabrique le flux du document et détient les compteurs. `pages` = registre de la passe précédente."""

    def __init__(self, pages: dict[str, dict] | None = None):
        self.flux: list = []
        self._marques: list[dict] = []
        self.exemptees: list[dict] = []
        self.verifiees = 0
        self.ancres: set[str] = set()
        self.liens_orphelins: list[str] = []
        self.styles = doc.styles()
        self.pages = pages or {}
        self.cles: dict[str, str] = {}
        self.figures_citees: dict[str, str] = {}
        self.tableaux: dict[str, str] = {}
        self.extraits: list[str] = []
        self.n_partie = 0
        self.n_section = 0
        self.n_sous = 0
        self.n_fig = 0
        self.n_tab = 0
        self.n_code = 0
        self.en_annexe = ""
        self.mode = "corps"

    # ── mécanique interne --------------------------------------------
    def _legal(self, texte: str, *, tolerer: bool = False) -> str:
        """Loi de langue : contrôle du rendu, exemption du code, insertion des insécables.

        Le contrôle porte sur le texte converti, sans ses spans monospace : ce qui doit être
        conforme est ce qui est imprimé, et `user_role` n'est pas le mot anglais « user ».
        """
        # La loi s'évalue sur le texte **après** mise en forme : c'est le rendu qui doit être
        # conforme, et le moteur insère les insécables. Les spans monospace (code verbatim) sont
        # retirés avant contrôle — `src/db/schema.ts:151` n'est pas de la prose.
        self.verifiees += 1
        converti = appliquer_loi_langue(texte)
        nu = re.sub(r'<font face="Mono">.*?</font>', " ", converti, flags=re.S)
        nu = retirer_code(re.sub(r"<[^>]+>", "", nu))
        fautes = [] if tolerer else verifier_langue(nu)
        if fautes:
            raise LangueRefusee(" ; ".join(fautes[:3]))
        # la correction, pas seulement le contrôle : le texte rendu porte les insécables et les
        # spans monospace produits par le moteur. Rendre `texte` brut serait imprimer un brouillon.
        return self._refs(converti)

    def _refs(self, texte: str) -> str:
        def remplace(m):
            cle = m.group(1)
            if cle not in self.cles:
                raise RefManquante(f"renvoi [[R:{cle}]] : clé jamais déclarée par le contenu")
            info = self.pages.get(cle)
            if info is None:
                # première passe : le numéro n'existe pas encore, on réserve la place au pixel près
                return f"{INS}p.{INS}—{INS}"
            if cle not in self.ancres:
                self.liens_orphelins.append(cle)
                num = str(info["page"])
                return f"{INS}p.{INS}{num}{INS}"
            return (f'<link href="#{cle}" color="#5A5147">{INS}p.{INS}{info["page"]}{INS}'
                    "</link>")
        return re.sub(r"\s*\[\[R:([A-Za-z0-9_.:-]+)\]\]", remplace, texte)

    def _numerote(self) -> str:
        if self.en_annexe:
            return (f"{self.en_annexe}" if self.n_section == 0
                    else f"{self.en_annexe}.{self.n_section}")
        return f"{self.n_partie}.{self.n_section}"

    def _pousser(self, *objets):
        self.flux.extend(objets)

    def _ancre(self, cle: str, titre: str, *, niveau: int = 3):
        """Pose le signet et declare l'ancre : un lien sans destination est un lien mort d'avance."""
        self.ancres.add(cle)
        return Signet(cle, re.sub(r"<[^>]+>", "", titre), niveau=niveau)

    @staticmethod
    def _nu(texte: str) -> str:
        """Titre d'appareil en texte nu : balises retirées, entités décodées, insécable U+202f gardée.

        Le signet et l'en-tête courant sont dessinés hors paragraphe (canvas) : ils ne décodent ni
        balise ni entité. Un libellé qui affiche «&#160;» est une faute de rendu, pas une nuance.
        """
        t = re.sub(r"<[^>]+>", "", texte)
        for ent, val in (("&#160;", "\u202f"), ("&nbsp;", "\u202f"), ("&#8239;", "\u202f"),
                         ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')):
            t = t.replace(ent, val)
        return re.sub(r"\s+", " ", t).strip()

    def _lien(self, cle: str, nom: str):
        """Libelle cliquable si l'ancre existe, sinon texte simple — jamais un lien brise."""
        nom = echapper(self._nu(nom))
        if cle in self.ancres:
            return '<link href="#' + cle + '" color="#2B2620">' + nom + "</link>"
        self.liens_orphelins.append(cle)
        return nom

    def _marquer(self, espece: str, **options):
        """Place un marqueur d'appareil (sommaire, listes). L'appareil est composé à la fin de la
        passe, quand les compteurs et les numéros de page sont connus — jamais avant."""
        self._marques.append(dict(espece=espece, options=options, index=len(self.flux)))
        self.flux.append(Spacer(1, 0.1))

    # ── structure ------------------------------------------------------
    def saut(self):
        self._pousser(PageBreak())

    def toise(self, h_mm: float = 3.0):
        self._pousser(Spacer(1, h_mm * mm))

    def couverture(self, blocs: list[tuple[str, str]]):
        self._pousser(NextPageTemplate("couverture"))
        self._pousser(Spacer(1, 26 * mm))
        for style, texte in blocs:
            self._pousser(Paragraph(appliquer_loi_langue(texte), self.styles[style]))
            self._pousser(Spacer(1, 3.0 * mm))
        self._pousser(PageBreak())

    def intercalaire(self, roman: str, titre: str, accroche: str, *, cle: str, items: list[str] | None = None):
        """Page-bandeau. Le compteur de parties est **dérivé** du numéro romain : pas de désaccord."""
        self.n_partie = ROMAN.index(roman) + 1 if roman in ROMAN else self.n_partie + 1
        self.n_section = self.n_sous = 0
        self.cles[cle] = f"{roman} — {titre}"
        self._pousser(NextPageTemplate("intercalaire"))
        self._pousser(Spacer(1, 74 * mm))
        self.ancres.add(cle)
        s0 = Signet(cle, f"{roman} · {titre}", niveau=0)
        self._pousser(s0)
        self._pousser(Paragraph(roman, self.styles["interc_num"]))
        self._pousser(Paragraph(appliquer_loi_langue(titre), self.styles["interc"]))
        self._pousser(Spacer(1, 5 * mm))
        self._pousser(Paragraph(appliquer_loi_langue(accroche), self.styles["interc_note"]))
        if items:
            self._pousser(Spacer(1, 8 * mm))
            for it in items:
                self._pousser(Paragraph(f'<font color="#C9A959">—</font>{INS}{self._legal(it)}',
                                        self.styles["interc_note"]))
        self._pousser(NextPageTemplate("corps"))
        self._pousser(PageBreak())

    def section(self, titre: str, *, cle: str, niveau: int = 1):
        if niveau == 1:
            if not self.en_annexe:
                self.n_section += 1
            self.n_sous = 0
        elif niveau == 2:
            self.n_sous += 1
        # liminaires (n_partie == 0, hors annexe) : pas de numéro — un «0.1» en tête de dédicaces
        # serait une faute de rédaction, pas un style
        prefix = self._numerote() if (niveau <= 2 and (self.n_partie or self.en_annexe)) else ""
        titre_legal = self._legal(titre)
        complet = f"{prefix}\u202f{titre_legal}" if prefix else titre_legal
        nu = self._nu(f"{prefix} {titre}".strip()) if prefix else self._nu(titre)
        self.cles[cle] = nu
        style = {1: "h1", 2: "h2", 3: "h3"}[niveau]
        if niveau == 1:
            self._pousser(Spacer(1, 2 * mm))
        self.ancres.add(cle)
        self._pousser(Signet(cle, nu, niveau=min(niveau, 3)))
        self._pousser(KeepTogether([Paragraph(complet, self.styles[style])]))

    def sous(self, titre: str, *, cle: str):
        self.section(titre, cle=cle, niveau=2)

    def paragraphe(self, titre: str, *, cle: str):
        self.section(titre, cle=cle, niveau=3)

    def hors_numerotation(self) -> None:
        """Sort des parties et des annexes : le dos du document ne se numérote pas « VI.9 ».

        Résumés et quatrième de couverture viennent après la dernière annexe. Sans cet appel, ils
        héritent du compteur de la sixième partie et le mémoire affiche une section qui n'existe
        nulle part dans le plan. La commande est passée par le contenu, pas par le moteur : la
        structure du document reste lisible dans le fichier qui l'écrit.
        """
        self.n_partie = 0
        self.en_annexe = ""
        self.n_section = self.n_sous = 0

    def annexe(self, lettre: str, titre: str, accroche: str, *, cle: str | None = None):
        self.en_annexe = lettre
        self.n_section = self.n_sous = 0
        self._pousser(NextPageTemplate("intercalaire"))
        self._pousser(Spacer(1, 74 * mm))
        cle = cle or f"annexe.{lettre}"
        self.cles[cle] = f"Annexe {lettre} — {titre}"
        self._pousser(Signet(cle, f"Annexe {lettre} · {titre}", niveau=0))
        self._pousser(Paragraph(f"ANNEXE {lettre}", self.styles["interc_num"]))
        self._pousser(Paragraph(appliquer_loi_langue(titre), self.styles["interc"]))
        self._pousser(Spacer(1, 5 * mm))
        self._pousser(Paragraph(appliquer_loi_langue(accroche), self.styles["interc_note"]))
        self._pousser(NextPageTemplate("corps"))
        self._pousser(PageBreak())

    # ── texte ----------------------------------------------------------
    def lead(self, texte: str, *, langue: str = "fr"):
        if langue != "fr":
            self.exemptees.append(dict(langue=langue, raison="abstract-bilingue",
                                       debut=re.sub(r"\s+", " ", texte)[:60], mots=len(texte.split())))
            self._pousser(Paragraph(echapper(texte), self.styles["chapeau"]))
            return
        self._pousser(Paragraph(self._legal(texte), self.styles["chapeau"]))

    def p(self, *paragraphes: str, tolerer: bool = False, langue: str = "fr"):
        """Paragraphe de corps. `langue="en"` suspend les lois de langue française et **le déclare**.

        Un texte écrit dans une autre langue n'échappe pas au contrôle : il est consigné comme
        exempté, avec sa raison, dans `audit/langue.json`, et le harnais vérifie que le nombre de
        paragraphes exemptés correspond à ce que le PDF contient entre les titres concernés.
        """
        for t in paragraphes:
            if langue != "fr":
                self.exemptees.append(dict(langue=langue, raison="abstract-bilingue",
                                           debut=re.sub(r"\s+", " ", t)[:60], mots=len(t.split())))
                self._pousser(Paragraph(echapper(t), self.styles["corps"]))
                continue
            self._pousser(Paragraph(self._legal(t, tolerer=tolerer), self.styles["corps"]))

    def liste(self, items: list[str], *, numerotee: bool = False):
        for i, it in enumerate(items, 1):
            puce = f"{i}." if numerotee else "—"
            self._pousser(Paragraph(f'<font color="#C9A959">{puce}</font>{INS}{self._legal(it)}',
                                    self.styles["liste"]))

    def note(self, texte: str):
        self._pousser(Paragraph(f'<font color="#5A5147">{self._legal(texte)}</font>',
                                self.styles["note"]))

    def encadre(self, titre: str, texte: str, *, teinte=doc.OR):
        inner = [Paragraph(appliquer_loi_langue(f"<b>{titre}</b>"), self.styles["h3"]),
                 Paragraph(self._legal(texte), self.styles["corps"])]
        t = Table([[inner]], colWidths=[LARGEUR_TEXTE])
        t.setStyle(doc.TableStyle([("BACKGROUND", (0, 0), (-1, -1), doc.PAPIER),
                                   ("BOX", (0, 0), (-1, -1), 0.7, teinte),
                                   ("LINEBEFORE", (0, 0), (0, -1), 2.4, teinte),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 7),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                                   ("TOPPADDING", (0, 0), (-1, -1), 5.5),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5)]))
        self._pousser(Spacer(1, 2.4 * mm), t, Spacer(1, 3.0 * mm))

    # ── figures, tableaux, code ----------------------------------------
    def figure(self, fid: str, *, legende: str | None = None, saut: float = 0.0, demie: bool = False,
                right: bool = False):
        if fid in self.figures_citees:
            raise RuntimeError(f"plaque {fid} citée deux fois : le document compterait deux figures "
                               "pour une seule planche — supprimer le second appel")
        if fid not in FIGURES_REG:
            raise RuntimeError(f"figure citée mais inexistante : {fid} — le rapport refuse de promettre "
                               "une plaque que le dépôt ne produit pas")
        f = FIGURES_REG[fid]
        self.n_fig += 1
        demi = f.width_mm < 100 or demie
        if demi and f.width_mm >= 100:
            raise RuntimeError(f"{fid} est une pleine plaque : ne pas forcer demie=True")
        largeur = (LARGEUR_TEXTE / mm) if not demi else 80.0
        echelle = largeur / f.width_mm
        hauteur = f.height_mm * echelle
        texte_legende = legende if legende is not None else (
            f"{f.title}. {f.caption}" + (f" Gisement : {f.source}." if f.source else ""))
        entete = f'<b>Figure&#160;{self.n_fig}</b>&#160;—&#160;'
        self.figures_citees[fid] = f"Figure {self.n_fig} — {f.title}"
        cle = f"fig.{fid}"
        self.cles[cle] = f"Figure {self.n_fig} — {f.title}"
        creux = Creux(fid, largeur, hauteur,
                      legende=appliquer_loi_langue(entete + texte_legende), styles=self.styles)
        blocs = ([Spacer(1, saut * mm)] if saut else []) + [self._ancre(cle, self.cles[cle]), creux]
        if right and demi:
            blocs = [Spacer(1, LARGEUR_TEXTE - 80 * mm)] + blocs
        self._pousser(KeepTogether(blocs))
        return cle

    def code(self, fichier: str, debut: int, n: int, *, titre: str = "", commentaire: str = ""):
        """Cite des lignes **réelles** du dépôt, avec leur numéro de ligne. Aucune réécriture."""
        chemin = RACINE / fichier
        if not chemin.exists():
            raise RuntimeError(f"source citée introuvable : {fichier}")
        lignes = chemin.read_text(encoding="utf-8").splitlines()
        if debut < 1 or debut - 1 + n > len(lignes):
            raise RuntimeError(f"extrait hors bornes : {fichier}:{debut}+{n} "
                               f"(le fichier fait {len(lignes)} lignes)")
        extrait = lignes[debut - 1: debut - 1 + n]
        self.n_code += 1
        entete = titre or f"{fichier}:{debut}–{debut + n - 1}"
        corps = []
        for i, ln in enumerate(extrait):
            nu = debut + i
            texte = (ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                     .replace(" ", "\u00a0"))
            corps.append(f'<font color="#5A5147">{nu:>4}</font>{INS}{texte or chr(160)}')
        blocs = [Paragraph(appliquer_loi_langue(f"<b>Extrait {self.n_code}</b>&#160;—&#160;{entete}"),
                          self.styles["h3"]),
                 Paragraph("\n".join(corps), self.styles["code"])]
        if commentaire:
            blocs.append(Paragraph(self._legal(commentaire), self.styles["note"]))
        self._pousser(KeepTogether(blocs))
        self.extraits.append(f"{fichier}:{debut}-{debut + n - 1}")
        self.cles[f"code.{fichier}.{debut}"] = f"Extrait {self.n_code} — {entete}"

    def tableau(self, entetes: list[str], lignes: list[list[str]], *, titre: str, cle: str,
                largeurs: list[float] | None = None, legende: str = "", cesser: int | None = None,
                nowrap: bool = False, taille: float = 7.1):
        self.n_tab += 1
        entetes = [appliquer_loi_langue(h) for h in entetes]
        ent = [Paragraph(f"<b>{h}</b>", self.styles["table_h"]) for h in entetes]
        corps = []
        for ln in lignes:
            ligne = []
            for cel in ln:
                cel = str(cel)
                cel = self._legal(cel) if not nowrap else appliquer_mono(cel)
                style = "table_mono" if nowrap else "table"
                ligne.append(Paragraph(cel, self.styles[style]))
            corps.append(ligne)
        data = [ent] + corps
        cols = ([LARGEUR_TEXTE * (x / sum(largeurs)) for x in largeurs] if largeurs
                else [LARGEUR_TEXTE / len(entetes)] * len(entetes))
        morceaus = []
        depart = 0
        while True:
            fin = len(corps) if cesser is None else min(depart + cesser, len(corps))
            part = [ent] + corps[depart:fin]
            t = Table(part, colWidths=cols, repeatRows=1)
            t.setStyle(style_tableau(len(part)))
            nom = f'<b>Tableau&#160;{self.n_tab}</b>&#160;—&#160;{appliquer_loi_langue(titre)}'
            if legende:
                nom += f'. {appliquer_loi_langue(legende)}'
            if depart == 0:
                nom += "" if cesser is None or fin >= len(corps) else " (suite ci-après)"
            else:
                nom = f'<i>suite du tableau {self.n_tab}</i>'
            morceaus.append(KeepTogether([Paragraph(nom, self.styles["legende"]), t]))
            depart = fin
            if depart >= len(corps):
                break
        nom_tab = f"Tableau {self.n_tab} — {titre}"
        if cle:
            self.cles["tab." + cle] = nom_tab
            self.tableaux[cle] = nom_tab
            morceaus.insert(0, self._ancre("tab." + cle, nom_tab))
        self._pousser(*morceaus, Spacer(1, 2.6 * mm))

    # ── sommaires et listes (cliquables, construits depuis le registre) ─
    # ── appareil (sommaire et listes) : composé APRÈS le contenu, inséré aux marqueurs ──
    def table_des_matieres(self, *, titre: str = "Sommaire", cle: str = "sommaire"):
        self._marquer("toc", titre=titre, cle=cle)

    def liste_des_planches(self, *, cle: str = "liste.figures"):
        self._marquer("figlist", titre="Liste des planches", cle=cle)

    def liste_des_tableaux(self, *, cle: str = "liste.tableaux"):
        self._marquer("tablist", titre="Liste des tableaux", cle=cle)

    def _titre_appareil(self, cle: str, titre: str):
        """Un titre d'appareil n'est pas numéroté : il n'appartient à aucune partie."""
        self.cles[cle] = titre
        return [Signet(cle, titre, niveau=0),
                Paragraph(appliquer_loi_langue(titre), self.styles["h1"])]

    def _ligne_appareil(self, cle: str, nom: str):
        info = self.pages.get(cle, {})
        return [Paragraph(self._lien(cle, nom), self.styles["toc"]),
                Paragraph(str(info.get("page", "—")), self.styles["toc"])]

    def _table_appareil(self, lignes):
        t = Table(lignes, colWidths=[LARGEUR_TEXTE - 16, 16])
        t.setStyle(doc.TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 1.3),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 1.3),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                                   ("ALIGN", (1, 0), (1, -1), "RIGHT")]))
        return t

    def _generer(self, espece: str, **opt):
        if espece == "toc":
            blocs = self._titre_appareil(opt["cle"], opt["titre"])
            entrees = [(c, nom) for c, nom in self.cles.items()
                       if not c.startswith(("fig.", "tab.", "code."))
                       and c not in ("sommaire", "liste.figures", "liste.tableaux", "abreviations")]
            lignes = [self._ligne_appareil(c, nom) for c, nom in entrees]
            blocs += [self._table_appareil(lignes), PageBreak()]
            return blocs
        if espece == "figlist":
            if not self.figures_citees:
                raise RuntimeError("aucune figure citée : la liste serait fausse plutôt que vide")
            blocs = self._titre_appareil(opt["cle"], opt["titre"])
            rangs = sorted(self.figures_citees.items(),
                           key=lambda kv: int(re.search(r"(\d+)", kv[1].split("—")[0]).group()))
            lignes = [self._ligne_appareil(f"fig.{fid}", nom) for fid, nom in rangs]
            blocs += [self._table_appareil(lignes), PageBreak()]
            return blocs
        if espece == "tablist":
            if not self.tableaux:
                raise RuntimeError("aucun tableau construit")
            blocs = self._titre_appareil(opt["cle"], opt["titre"])
            lignes = [self._ligne_appareil(f"tab.{c}", nom) for c, nom in self.tableaux.items()]
            blocs += [self._table_appareil(lignes), PageBreak()]
            return blocs
        raise RuntimeError(f"espèce d'appareil inconnue : {espece}")

    def materialiser(self) -> None:
        """Remplace les marqueurs par l'appareil réel, et refuse un appareil plus gros qu'une page vide."""
        if not self._marques:
            raise RuntimeError("aucun marqueur d'appareil : le document n'aurait ni sommaire ni listes")
        flux = []
        par_index = {m["index"]: m for m in self._marques}
        for i, b in enumerate(self.flux):
            if i in par_index:
                flux.pop()                     # l'espace fantôme du marqueur
                flux.extend(self._generer(par_index[i]["espece"], **par_index[i]["options"]))
            else:
                flux.append(b)
        self.flux = flux

    # ── autocontrôle interne (appelé par build.py) --------------------
    def autoverif(self) -> None:
        lags = []
        for fid in self.figures_citees:
            if fid not in FIGURES_REG:
                lags.append(f"figure déclarée puis retirée du registre : {fid}")
        for cle in list(self.cles):
            if cle.startswith("fig.") and cle[4:] not in self.figures_citees:
                lags.append(f"clé de figure sans citation effective : {cle}")
        if self.liens_orphelins:
            vus = sorted(set(self.liens_orphelins))
            lags.append(str(len(vus)) + " renvoi(s) sans ancre posée : " + ", ".join(vus[:6]))
        if lags:
            raise RuntimeError(" ; ".join(lags))


def numeroter_section(fab: Fab) -> str:      # utilitaire exposé pour les annexes
    return fab._numerote()
