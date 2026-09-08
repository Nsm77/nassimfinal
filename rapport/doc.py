"""rapport/doc.py — moteur typographique du rapport (ReportLab), lois de langue **exécutables**.

Trois choses sont écrites ici une fois pour toutes, parce qu'elles font la différence entre un
document qui affirme et un document qui prouve :

* la typographie française est **appliquée** au texte (espace insécable fine avant `; : ! ? % »`,
  après `«`), puis vérifiée : `qa.py` repasse la même expression régulière sur le texte extrait du
  PDF rendu. La loi n'existe pas seulement dans l'intention de l'auteur ;
* le choix du glyphe est **mesuré deux fois** (`glyphe_insécable`) : d'abord sur la police embarquée
  (U+202F existe dans DejaVu), ensuite sur le moteur de rendu — et c'est U+00A0 qui gagne, parce que
  ReportLab découpe les lignes sur U+202F comme sur une espace ordinaire. Jamais de tofu (INV-4),
  jamais d'insécable qui ne tient pas ;
* la mise en page tourne en passes : la première calcule la pagination, les suivantes impriment
  les numéros du sommaire et des renvois. Un sommaire faux est un mensonge de cent pages.

La page est découpée en un creux millimétré par figure (`Creux`) ; le texte est posé **avant**
les images (faute connue n° 3 : `chapter` trop tardif), le placage vectoriel intervient après.
"""
from __future__ import annotations

import math
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as _canvas
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus import Image as RLImage

import reportlab.rl_config

reportlab.rl_config.invariant = 1          # déterminisme : aucune horloge dans le PDF (INV-1)

HERE = Path(__file__).resolve().parent
RACINE = HERE.parent
FIGS = HERE / "figs"
AUDIT = RACINE / "audit"
FONTS = Path("/usr/share/fonts/truetype/dejavu")

ENCRE = colors.HexColor("#221A12")          # encre profonde, plus chaude que le brun v13
OR = colors.HexColor("#C9A959")              # champagne
PAPIER = colors.HexColor("#F7F1E4")          # ivoire chaud
SABLE = colors.HexColor("#E3D9C6")
PIERRE = colors.HexColor("#B9AFA0")
ROUILLE = colors.HexColor("#A9563A")
SAUGE = colors.HexColor("#6F7F66")
GRIS = colors.HexColor("#5A5147")
TINTE = colors.HexColor("#EFE7D6")           # fond léger des cadres et diptyques
FILET = colors.HexColor("#D9CDB6")           # hairline : le trait de 0,6 pt qui tient la grille

MARGE = 22 * mm
MARGE_H = 20 * mm
LARGEUR_TEXTE = A4[0] - 2 * MARGE          # 166 mm : la largeur utile des planches
HAUTEUR_TEXTE = A4[1] - 2 * MARGE_H
HAUTEUR_FLUX = HAUTEUR_TEXTE - 6 * mm      # réserve pour le titre courant

NBSP = " "
THIN_NBSP = " "


def glyphe_insécable() -> tuple[str, str]:
    """Choix du glyphe insécable, mesuré deux fois : sur la police, puis sur le moteur de rendu.

    U+202F (insécable fine) est la ponctuation française idéale et DejaVu la possède — le test le
    confirme. Mais le moteur de paragraphes découpe le texte sur tout caractère d'espacement,
    U+202F compris : la fine redevient césurable au rendu, ce qui est exactement la faute que la
    loi cherche à éviter. U+00A0 est insécable dans la police et dans le moteur. Le contrôle de
    langue accepte les deux, parce que ce qui compte est l'absence de césure, pas le numéro de code.
    """
    a_la_police = None
    try:
        from fontTools.ttLib import TTFont as TTF
        a_la_police = 0x202F in TTF(str(FONTS / "DejaVuSans.ttf")).getBestCmap()
    except Exception:
        a_la_police = False
    mesure = ("U+202F présent dans DejaVuSans : "
              f"{'oui' if a_la_police else 'non'} ; rendu forcé en U+00A0 parce que le moteur coupe "
              "sur U+202F (mesuré : les deux points de la page 20 ressortaient en U+0020)")
    return (THIN_NBSP if not a_la_police else NBSP), mesure


INS, RAISON_INSECABLE = glyphe_insécable()

# ──────────────────────────────────── contrôle du RENDU (loi des insécables, version PDF)
PONCTUATION_FR = ";:!?»%"


def lignes_rendues(pdf) -> list[list[tuple[str, str]]]:
    """Lignes du PDF rendu, reconstituées géométriquement : [(page, texte, police), …].

    Le calque texte d'un PDF normalise l'espace insécable en espace ordinaire : une regex posée sur
    `page.get_text()` vérifierait l'extraction, pas le document. On regroupe donc les spans par
    ordonnée et par colonne, comme l'œil du lecteur.
    """
    import pymupdf

    docu = pymupdf.open(str(pdf))
    paquets: dict[tuple[int, int], list[dict]] = {}
    for num, page in enumerate(docu, 1):
        for bloc in page.get_text("dict")["blocks"]:
            for ligne in bloc.get("lines", []):
                for span in ligne["spans"]:
                    if not span["text"]:
                        continue
                    paquets.setdefault((num, round(span["bbox"][1] / 1.6)), []).append(span)
    lignes = []
    for (num, _), spans in sorted(paquets.items()):
        spans.sort(key=lambda sp: sp["bbox"][0])
        lignes.append([dict(page=num, texte=sp["text"], police=sp["font"]) for sp in spans])
    docu.close()
    return lignes


def verifier_rendu(pdf) -> dict:
    """Loi des insécables vérifiée sur le rendu. Les spans monospace sont exempts, et le déclarent.

    Une ponctuation française en tête de ligne est une césure interdite ; la même ponctuation dans
    un extrait de code est du code, et le code se recopie tel quel.
    """
    fautes: list[str] = []
    exemptees = 0
    lignes = lignes_rendues(pdf)
    for ln in lignes:
        visibles = [sp for sp in ln if sp["texte"].strip()]
        if not visibles:
            continue
        premier = visibles[0]
        dernier = visibles[-1]
        mono = lambda sp: "mono" in sp["police"].lower()
        if mono(premier) or mono(dernier):
            exemptees += 1
        if premier["texte"].lstrip()[:1] in PONCTUATION_FR and not mono(premier):
            fautes.append(f"p.{premier['page']} : ligne commençant par {premier['texte'][:1]!r} — "
                          f"{premier['texte'].strip()[:48]!r}")
        if dernier["texte"].rstrip().endswith("«") and not mono(dernier):
            fautes.append(f"p.{dernier['page']} : ligne finissant par un guillemet ouvrant")
    return dict(lignes=len(lignes), fautes=fautes, exemptes_mono=exemptees)



# ─────────────────────────────────────────────────── lois de langue (exécutables)
SLOP = [r"dans un monde", r"il est important de", r"il convient de", r"force est de constater",
        r"à l[’']ère du", r"de nos jours", r"jouer un rôle clé", r"s'avère", r"cruciale?",
        r"de pointe", r"solution innovante"]
# Anglicismes de domaine : le mot anglais écrit en toutes lettres dans le texte courant est un refus.
SYNONYMES = {"commande": ["order"], "panier": ["cart"], "produit": ["item"],
             "boutique": ["shop", "store"], "utilisateur": ["user"], "suivi": ["tracking"],
             "mot de passe": ["password"]}
# Mot français licite ailleurs, prohibé quand il tient lieu de terme métier. Vérifié en contexte,
# parce qu'une liste de mots isolés interdirait d'écrire « dans l'ordre » en français correct.
VERBES_COMMANDE = "passer|modifier|annuler|régler|préparer|expédier|livrer|suivre|enregistrer"
DETERMINANTS = "un|une|la|le|mon|votre|son|cet|cette"
SYNONYMES_CONTEXTES = [
    (re.compile(rf"(?:{VERBES_COMMANDE})\s+(?:{DETERMINANTS})\s+ordre\b", re.I),
     "« ordre » au sens de commande : écrire « commande »"),
    (re.compile(r"\bordre\b(?:s)?\s+(?:du client|de la commande|d'expédition|payée|expédiée|annulée)", re.I),
     "« ordre » anglicisé : écrire « commande »"),
]
# Segments de code : entre accents graves, ils sont verbatim (identifiants du dépôt, pas prose).
CODE_INLINE = re.compile(r"`([^`\n]+)`")
ECHAPPE = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}


BALISAGES_AUTORISES = re.compile(
    r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*;)"      # entités déjà écrites
    r"|</?(?:b|i|em|strong|sub|sup|br|c|u)\b[^>]*>"          # emphase
    r"|<(?:font|link)\b[^>]*>"                               # police et lien interne
)


def echapper(texte: str) -> str:
    """Échappe `&`, `<`, `>` d'une prose marquée, en préservant balisage autorisé et entités.

    Deux manières de se tromper, toutes deux rencontrées dans ce dépôt : ne rien échapper (un `<`
    de code casse le paragraphe) ou tout échapper (la loi de langue imprime alors «&lt;b&gt;» au
    lieu de mettre en gras). Le compromis est écrit une fois ici : ce qui n'est ni une entité ni
    une balise de la liste ci-dessus devient du texte littéral.
    """
    paquets: list[str] = []

    def cacher(m):
        paquets.append(m.group(0))
        return f"\x01{len(paquets) - 1}\x01"

    t = BALISAGES_AUTORISES.sub(cacher, texte)
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def liberer(m):
        return paquets[int(m.group(1))]

    return re.sub(r"\x01(\d+)\x01", liberer, t)


def echapper_strict(texte: str) -> str:
    """Échappement intègre du verbatim : dans un extrait de code, `<b>` doit rester `<b>`.

    La loi de langue préserve le balisage de la prose ; un segment monospace n'est pas de la prose.
    """
    return texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def retirer_code(texte: str) -> str:
    """Texte sans les segments `code` : c'est sur ce texte que les lois s'appliquent."""
    return CODE_INLINE.sub(" ", texte)


def appliquer_loi_langue(texte: str) -> str:
    """Insère les insécables hors code, rend le code en monospace, échappe le reste.

    Les autres lois sont des refus, pas des corrections : ce qui doit changer est réécrit par
    l'auteur, pas rafistolé par le moteur.
    """
    segments: list[str] = []

    def cacher(m):
        segments.append(m.group(1))
        return f"\x00{len(segments) - 1}\x00"

    t = CODE_INLINE.sub(cacher, texte)
    t = echapper(t)
    t = re.sub(r"\s([;:!?»])", INS + r"\1", t)
    t = re.sub(rf"(?<=\w){INS}?:(?=\d)", ":", t)          # « fichier.ts:151 » reste copiable
    t = re.sub(r"«\s+", "«" + INS, t)
    t = re.sub(r"\s+»", INS + "»", t)

    def reveler(m):
        return f'<font face="Mono">{echapper_strict(segments[int(m.group(1))])}</font>'

    t = re.sub(r"\x00(\d+)\x00", reveler, t)
    # l'auteur peut écrire l'entité ; le lecteur doit voir le glyphe, jamais le code de l'entité
    return t.replace("&#160;", INS).replace("&nbsp;", INS).replace("&#8239;", INS)
# espace (insécable fine ou classique) exigée avant ces signes ; le motif inverse cherche l'absence
INSSECABLE = re.compile(r"(?<! )(?<!\u00a0) [;:!?»]")

# Ponctuation haute **collée** à un mot : l'espace, même sécable, manque déjà. La loi INSSECABLE
# ci-dessus ne voyait que l'espace ordinaire ; l'assaut M2 de `rapport/mutation.py` a trouvé le trou.
# Exceptions écrites : `:` suivi d'un chiffre (une référence `fichier.ts:151`, une durée `16:9`) et
# `://` d'une URL se recopient tels quels — y mettre une espace casserait l'identifiant ou le lien.
PONCTUATION_COLLÉE = re.compile(r"[\wÀ-ÿ](?::(?!\d)(?!//)|[;!?»])")
PERMETTRE = re.compile(r"permettre de", re.I)





def appliquer_mono(texte: str) -> str:
    """Échappe puis convertit `…` en span monospace, **sans** toucher à la ponctuation française.

    Réservé aux cellules verbatim (identifiants, chemins, valeurs de colonne) : y insérer des
    insécables ou y traduire la ponctuation falsifierait ce qui doit être recopié au caractère.
    """
    segments: list[str] = []

    def cacher(m):
        segments.append(m.group(1))
        return f"\x00{len(segments) - 1}\x00"

    t = CODE_INLINE.sub(cacher, texte)
    t = echapper(t)

    def reveler(m):
        return f'<font face="Mono">{echapper_strict(segments[int(m.group(1))])}</font>'

    return re.sub(r"\x00(\d+)\x00", reveler, t)


def verifier_langue(texte: str) -> list[str]:
    """`[]` = conforme. C'est exactement cette fonction que `qa.py` rejoue sur le texte extrait du PDF."""
    fautes: list[str] = []
    texte = retirer_code(texte)
    bas = texte.lower()
    for motif in SLOP:
        for m in re.finditer(motif, bas):
            extrait = texte[max(0, m.start() - 45):m.end() + 45].replace("\n", " ")
            fautes.append(f"SLOP «{m.group(0)}” : …{extrait}…")
    mots = len(re.findall(r"[\wÀ-ÿ]+", texte)) or 1
    n_permet = len(PERMETTRE.findall(bas))
    if n_permet / mots * 1000 > 3:
        fautes.append(f"«permettre de” sur-représenté : {n_permet} pour {mots} mots")
    for motif, attendu in SYNONYMES_CONTEXTES:
        for m in motif.finditer(texte):
            fautes.append(f"{attendu} : «…{texte[max(0, m.start() - 30):m.end() + 30]}…»")
    # Les entités HTML produites par l'échappement portent un point-virgule de syntaxe, pas de prose :
    # « & » devient « &amp; » et le « ; » final n'a rien à voir avec la ponctuation française. La
    # recherche est donc menée sur un texte où chaque entité est remplacée par des espaces **de même
    # longueur**, pour que les extraits cités à l'auteur restent alignés sur le texte d'origine.
    texte_ponctuation = re.sub(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z]{2,6});",
                              lambda m: " " * (m.end() - m.start()), texte)
    for m in PONCTUATION_COLLÉE.finditer(texte_ponctuation):
        fautes.append(f"ponctuation collée au mot, espace insécable absente avant "
                      f"{texte[m.end() - 1]!r} : «…{texte[max(0, m.start() - 26):m.end() + 8]}…»")
    for m in INSSECABLE.finditer(texte_ponctuation):
        fautes.append(f"insécable absent avant {texte[m.end() - 1]!r} : "
                      f"«…{texte[max(0, m.start() - 28):m.end() + 8]}…»")
    for terme, interdits in SYNONYMES.items():
        for mot in interdits:
            if re.search(rf"(?<![A-Za-zÀ-ÿ]){re.escape(mot)}(?![A-Za-zÀ-ÿ])", bas):
                fautes.append(f"terme à éviter «{mot}” pour «{terme}”")
    return fautes


def nombres_fr(valeur, decimales: int | None = None) -> str:
    """1 234,56 — séparateur de milliers insécable, virgule décimale."""
    if decimales is None:
        decimales = 0 if float(valeur) == int(float(valeur)) else len(str(valeur).split(".")[1])
    s = f"{float(valeur):,.{decimales}f}"
    entier, _, dec = s.partition(".")
    return entier.replace(",", INS) + ("," + dec if dec else "")


def dt(millimes: int, *, courte: bool = False) -> str:
    v = millimes / 1000
    return nombres_fr(v, decimales=0 if (courte and v == int(v)) else 3) + INS + "DT"


# ──────────────────────────────────────────────────── polices & styles
POLICES = HERE / "polices"

EXIGÉES = {                                    # l'identité v14, nommée par le prompt, pas approchée
    "Newsreader-Regular": "Display", "Newsreader-SemiBold": "Display-SemiBold",
    "Newsreader-Bold": "Display-Bold", "Newsreader-Italic": "Display-Italic",
    "Manrope-Regular": "Texte", "Manrope-Medium": "Texte-Medium",
    "Manrope-SemiBold": "Texte-SemiBold", "Manrope-Bold": "Texte-Bold",
    "Manrope-Italic": "Texte-Italic",
}


def _polices() -> dict:
    """Newsreader (display) + Manrope (texte) si posées ; sinon substitution **écrite**, jamais tue.

    Le bac à sable n'a pas de réseau vers les hébergeurs de fontes : le kit refuse deux mensonges.
    Il ne remplace pas l'identité en silence — `audit/polices.json` dit ce qui tient lieu — et il ne
    prétend pas l'avoir quand elle manque : `CLEOPATRE_FONDS=strict` fait échouer le build tant que
    `rapport/polices/` n'a pas reçu les TTF (`python3 rapport/polices/installer.py`).
    """
    etat = {"exigees": sorted(EXIGÉES), "installees": [], "substitution": None}
    trouve = {nom for nom in EXIGÉES if (POLICES / f"{nom}.ttf").exists()}
    etat["installees"] = sorted(trouve)
    if (POLICES / "OFL-Newsreader.txt").exists():
        etat["licence"] = "SIL Open Font License 1.1 — rapport/polices/"
    if len(trouve) == len(EXIGÉES):
        for nom, logique in EXIGÉES.items():
            pdfmetrics.registerFont(TTFont(logique, str(POLICES / f"{nom}.ttf")))
    else:
        if os.environ.get("CLEOPATRE_FONDS", "").lower() == "strict":
            raise RuntimeError("strict : fontes d'identité absentes — "
                               + ", ".join(sorted(set(EXIGÉES) - trouve)))
        etat["substitution"] = ("DejaVu (système) en attendant rapport/polices/ — "
                                "lancer l'installeur de fontes puis rebuild, sans toucher au texte")
        for logique, source in (("Display", "DejaVuSerif"), ("Display-Bold", "DejaVuSerif-Bold"),
                                ("Display-SemiBold", "DejaVuSerif"), ("Display-Italic", "DejaVuSerif"),
                                ("Texte", "DejaVuSans"), ("Texte-Medium", "DejaVuSans"),
                                ("Texte-SemiBold", "DejaVuSans-Bold"), ("Texte-Bold", "DejaVuSans-Bold"),
                                ("Texte-Italic", "DejaVuSans")):
            pdfmetrics.registerFont(TTFont(logique, str(FONTS / f"{source}.ttf")))
    for base, normal, bold, italic in (("Texte", "Texte", "Texte-Bold", "Texte-Italic"),
                                       ("Display", "Display", "Display-Bold", "Display-Italic")):
        registerFontFamily(base, normal=normal, bold=bold, italic=italic, boldItalic=bold)
    pdfmetrics.registerFont(TTFont("Mono", str(FONTS / "DejaVuSansMono.ttf")))
    pdfmetrics.registerFont(TTFont("Mono-Bold", str(FONTS / "DejaVuSansMono-Bold.ttf")))
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "polices.json").write_text(json.dumps(etat, ensure_ascii=False, indent=1,
                                                   sort_keys=True) + "\n", encoding="utf-8")
    return etat


_INSTALLE = False
etat_polices: dict = {}


def installer_polices() -> None:
    """Point d'entrée du composeur : enregistrement idempotent, état de substitution exposé.

    `styles()` l'appelle avant de composer quoi que ce soit ; les planches matplotlib passent par
    `polices_matplotlib()`. L'état courant ( fontes installées ou substitution ) vit dans
    `doc.etat_polices` et dans `audit/polices.json`, relus par la porte G6 et par `reforge.py`.
    """
    global _INSTALLE, etat_polices
    if _INSTALLE:
        return
    if not FONTS.exists():
        raise RuntimeError(f"polices DejaVu introuvables dans {FONTS} : le rapport refuse de composer "
                           "avec une police non vérifiée pour l'insécable fine")
    etat_polices = _polices()
    _INSTALLE = True


def polices_matplotlib() -> dict:
    """Mêmes fontes, deux moteurs : ce que dessine matplotlib doit être ce que compose ReportLab.

    Renvoie le dictionnaire rcParams à appliquer ; `substitution` traverse le pont, une figure ne doit
    jamais mentir sur la police qu'elle montre au jury.
    """
    installer_polices()
    installees = set(etat_polices.get("installees", []))
    if len(installees) == len(EXIGÉES):
        return {"family": "Manrope", "serif.family": "Newsreader", "display.family": "Manrope",
                "monospace.family": "DejaVu Sans Mono", "substitution": None}
    return {"family": "DejaVu Sans", "serif.family": "DejaVu Serif", "display.family": "DejaVu Sans",
            "monospace.family": "DejaVu Sans Mono", "substitution": etat_polices["substitution"]}


def styles() -> dict[str, ParagraphStyle]:
    installer_polices()
    S: dict[str, ParagraphStyle] = {}
    S["couverture"] = ParagraphStyle("couverture", fontName="Display", fontSize=34, leading=38,
                                     textColor=ENCRE, alignment=TA_CENTER)
    S["couv_sous"] = ParagraphStyle("couv_sous", fontName="Texte", fontSize=12, leading=17,
                                    textColor=GRIS, alignment=TA_CENTER)
    S["couv_pied"] = ParagraphStyle("couv_pied", fontName="Texte", fontSize=9, leading=13,
                                    textColor=GRIS, alignment=TA_CENTER)
    S["interc"] = ParagraphStyle("interc", fontName="Display", fontSize=30, leading=33.5,
                                 textColor=colors.HexColor("#F5F1E8"), alignment=TA_LEFT, spaceBefore=6)
    S["interc_num"] = ParagraphStyle("interc_num", fontName="Display", fontSize=92, leading=94,
                                     textColor=OR, spaceAfter=1)
    S["interc_note"] = ParagraphStyle("interc_note", fontName="Texte", fontSize=9.2, leading=13.5,
                                      textColor=PIERRE, alignment=TA_LEFT)
    S["h1"] = ParagraphStyle("h1", fontName="Display", fontSize=19.5, leading=23.2, textColor=ENCRE,
                             spaceBefore=12, spaceAfter=6, keepWithNext=1)
    S["h2"] = ParagraphStyle("h2", fontName="Display", fontSize=14.6, leading=18.2, textColor=ENCRE,
                             spaceBefore=9, spaceAfter=4, keepWithNext=1)
    S["h3"] = ParagraphStyle("h3", fontName="Texte-Bold", fontSize=9.8, leading=12.6, textColor=GRIS,
                             spaceBefore=7, spaceAfter=3, keepWithNext=1)
    S["corps"] = ParagraphStyle("corps", fontName="Texte", fontSize=9.6, leading=14.1, textColor=ENCRE,
                                alignment=TA_JUSTIFY, spaceAfter=5.0)
    S["chapeau"] = ParagraphStyle("chapeau", fontName="Texte", fontSize=10.0, leading=14.6,
                                  textColor=GRIS, alignment=TA_JUSTIFY, spaceAfter=7)
    S["liste"] = ParagraphStyle("liste", fontName="Texte", fontSize=9.4, leading=13.4, textColor=ENCRE,
                                alignment=TA_LEFT, leftIndent=9.5, spaceAfter=2.4)
    S["note"] = ParagraphStyle("note", fontName="Texte", fontSize=7.7, leading=10.6, textColor=GRIS,
                               alignment=TA_LEFT, spaceBefore=2.2, spaceAfter=5.4)
    S["legende"] = ParagraphStyle("legende", fontName="Texte", fontSize=7.5, leading=10.1,
                                  textColor=GRIS, alignment=TA_JUSTIFY, spaceBefore=1.8, spaceAfter=7)
    S["table_mono"] = ParagraphStyle("table_mono", fontName="Mono", fontSize=6.3, leading=8.0,
                                      textColor=ENCRE, spaceBefore=0.6, spaceAfter=0.6)
    S["code"] = ParagraphStyle("code", fontName="Mono", fontSize=6.7, leading=8.9, textColor=ENCRE,
                               backColor=SABLE, borderPadding=5, spaceAfter=6)
    S["table"] = ParagraphStyle("table", fontName="Texte", fontSize=7.1, leading=9.0, textColor=ENCRE)
    S["table_h"] = ParagraphStyle("table_h", fontName="Texte-Bold", fontSize=7.1, leading=9.0,
                                  textColor=ENCRE)
    S["toc"] = ParagraphStyle("toc", fontName="Texte", fontSize=9.1, leading=13.2, textColor=ENCRE)
    return S


# ──────────────────────────────────────────────────── flowables maison
PLACEMENTS: list[dict] = []


def reinitialiser_placements() -> None:
    PLACEMENTS.clear()


@dataclass
class Creux(Flowable):
    """Creux millimétré réservé à une planche, comblé en fin de build par `merge_transformed_page`.

    Le timbre vectoriel (`figs/<id>.pdf`) est la voie normale. S'il manque alors que le PNG existe,
    le creux est rempli sur place en PNG — dégradation L2 **déclarée** (`via_png=True`), reprise en
    rouge par la QA. Si les deux manquent, la construction est refusée : exception, pas page vide
    (§5 ; chaos C1 et C4).
    """
    fid: str
    w_mm: float
    h_mm: float
    legende: str = ""
    styles: dict = field(default_factory=dict, repr=False)
    via_png: bool = False

    def __post_init__(self):
        if (FIGS / f"{self.fid}.pdf").exists():
            return
        png = FIGS / f"{self.fid}.png"
        if not png.exists():
            raise FileNotFoundError(f"plaque {self.fid} : ni timbre vectoriel ni PNG dans {FIGS} "
                                    "— construction refusée")
        octets = png.stat().st_size
        if octets > 8 * 1024 * 1024:
            raise RuntimeError(f"chaos C3 : {self.fid} ne fournit qu'un raster de "
                               f"{octets // 1_048_576} Mo. Une capture 8K ne remplace pas un vecteur : "
                               "elle pèse le document sans ajouter une ligne d'information. Réduire la "
                               "source ou réécrire la planche en matplotlib.")
        from PIL import Image
        with Image.open(png) as im:          # chaos C2 : un PNG illisible doit faire mourir le build
            im.verify()
        self.via_png = True

    def _hauteur_legende(self) -> float:
        if not self.legende:
            return 0.0
        st = self.styles.get("legende")
        if st is None:
            return 12.0
        brut = re.sub(r"<[^>]+>", "", self.legende)
        largeur_pt = self.w_mm * mm
        lignes = max(1, math.ceil(pdfmetrics.stringWidth(brut, st.fontName, st.fontSize)
                                  / max(largeur_pt - 6, 1)))
        return lignes * st.leading + 2.6

    def wrap(self, aw, ah):
        self._w = min(self.w_mm * mm, aw)
        self._h = self.h_mm * mm + self._hauteur_legende()
        if self._h > HAUTEUR_FLUX:
            raise RuntimeError(f"plaque {self.fid} : {self._h / mm:.1f} mm de haut, la page utile fait "
                               f"{HAUTEUR_FLUX / mm:.1f} mm — réduire la planche, pas la légende")
        return (self._w, self._h)

    def draw(self):
        c = self.canv
        h_leg = self._hauteur_legende()
        if self.via_png:
            c.drawImage(str(FIGS / f"{self.fid}.png"), 0, h_leg, width=self._w, height=self.h_mm * mm,
                        mask="auto")
        else:
            c.setStrokeColor(PIERRE)
            c.setLineWidth(0.3)
            c.setDash(1.3, 1.7)
            c.rect(0, h_leg, self._w, self.h_mm * mm, stroke=1, fill=0)   # la grille reste visible au brouillon
            c.setDash()
        if self.legende:
            p = Paragraph(self.legende, self.styles["legende"])
            p.wrapOn(c, self._w, 260)
            p.drawOn(c, 0, 1.0)

    def drawOn(self, canv, x, y, _sW=0):
        """Enregistre le placement en millimètres, origine haut-gauche — la monnaie du placage."""
        super().drawOn(canv, x, y, _sW)
        bas_image = y + self._hauteur_legende()
        haut_image = bas_image + self.h_mm * mm
        PLACEMENTS.append(dict(
            fid=self.fid, page=canv.getPageNumber() - 1,          # 0-based : exigence du placage
            x_mm=round(x / mm, 4), y_mm=round((A4[1] - haut_image) / mm, 4),
            w_mm=round(self._w / mm, 4), h_mm=round(self.h_mm, 4),
            via_png=bool(self.via_png), legende_h=round(self._hauteur_legende() / mm, 3),
        ))


class Signet(Flowable):
    """Ancre nommée (sommaire cliquable, renvois) + entrée de plan, sur trois niveaux."""

    def __init__(self, cle: str, titre: str, niveau: int = 1):
        self.cle, self.titre, self.niveau = cle, titre, niveau
        self.width = self.height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        self.canv.bookmarkPage(self.cle)
        if self.titre:
            try:
                self.canv.addOutlineEntry(self.titre, self.cle, level=max(0, self.niveau - 1),
                                          closed=False)
            except Exception:
                pass


class Registre:
    """Collecte ancres et creux pendant la mise en page (sert au sommaire, au placage, à l'audit)."""

    def __init__(self):
        self.pages_signets: dict[str, dict] = {}
        self.creux: dict[str, dict] = {}

    def ancre(self, cle: str, titre: str, niveau: int, page: int) -> None:
        self.pages_signets[cle] = dict(page=page, titre=titre, niveau=niveau)


class CadreCapture(Flowable):
    """Le cadre éditorial 16:9 en attente de capture — pas une boîte grise de formulaire.

    Il revendique sa place sur la page, tient exactement le ratio promis, et s'efface dès qu'un fichier
    `public/avants/<cle>.png` existe : alors l'image est posée **sans déformation**, et le contrôle du
    ratio refuse une capture qui ne tiendrait pas dans le cadre promis. Aucun gabarit inventé, aucune
    capture fabriquée.
    """

    SAUT_SOUS = 8.4 * mm

    def __init__(self, cle: str, etiquette: str, note: str = ""):
        super().__init__()
        self.cle, self.etiquette, self.note = cle, etiquette, note
        self.image = RACINE / "public" / "avants" / f"{cle}.png"
        self.largeur = 0.0

    def wrap(self, aw, ah):
        self.largeur = aw
        return aw, aw * 9 / 16 + self.SAUT_SOUS

    def draw(self):
        c = self.canv
        h = self.largeur * 9 / 16
        if self.image.exists():
            from PIL import Image as _Im
            with _Im.open(self.image) as im:
                w0, h0 = im.size
            if abs(w0 / h0 - 16 / 9) > 0.03:
                raise RuntimeError(f"chaos d'insertion : {self.image.name} fait un ratio de "
                                   f"{w0 / h0:.3f}, le cadre promet 16:9 (±3 %). Recadrer la capture, "
                                   f"ne pas tordre l'image.")
            c.saveState()
            c.clipPath(c.beginPath().roundRect(0, self.SAUT_SOUS, self.largeur, h, 2.2 * mm),
                       stroke=0, fill=0)
            c.drawImage(str(self.image), 0, self.SAUT_SOUS, width=self.largeur, height=h,
                        preserveAspectRatio=True, anchor="c", mask="auto")
            c.restoreState()
            c.setStrokeColor(FILET); c.setLineWidth(0.6)
            c.roundRect(0, self.SAUT_SOUS, self.largeur, h, 2.2 * mm, stroke=1, fill=0)
            return
        c.setFillColor(TINTE)
        c.roundRect(0, self.SAUT_SOUS, self.largeur, h, 2.2 * mm, stroke=0, fill=1)
        c.setStrokeColor(FILET); c.setLineWidth(0.6)
        c.roundRect(0, self.SAUT_SOUS, self.largeur, h, 2.2 * mm, stroke=1, fill=0)
        c.setFillColor(PIERRE)
        for x, y in ((3.4 * mm, self.SAUT_SOUS + 3.4 * mm), (self.largeur - 3.4 * mm, self.SAUT_SOUS + 3.4 * mm),
                     (3.4 * mm, self.SAUT_SOUS + h - 3.4 * mm), (self.largeur - 3.4 * mm, self.SAUT_SOUS + h - 3.4 * mm)):
            c.circle(x, y, 0.7 * mm, stroke=0, fill=1)
        c.setFillColor(GRIS)
        c.setFont("Display", 13.5)
        c.drawCentredString(self.largeur / 2, self.SAUT_SOUS + h / 2 + 4.4, self.etiquette)
        c.setFont("Texte-Medium", 7.2)
        c.drawCentredString(self.largeur / 2, self.SAUT_SOUS + h / 2 - 9.4,
                            "CAPTURE À INSÉRER — 16 : 9" + (f" — {self.note}" if self.note else ""))


class Toile(BaseDocTemplate):
    """Gabarit : couverture, intercalaires, pages courantes avec titre courant et filet doré."""

    def __init__(self, chemin: Path, registre: Registre, **kw):
        kw.setdefault("title", "Cléopâtre — Espace Santé Beauté : rapport de projet")
        kw.setdefault("creator", "rapport/build.py — dépôt nassimfinal")
        super().__init__(str(chemin), pagesize=A4, leftMargin=MARGE, rightMargin=MARGE,
                         topMargin=MARGE_H, bottomMargin=MARGE_H, **kw)
        self.registre = registre
        self._titre_courant = ""
        self._roman_courant = ""

    def _cadres(self):
        corps = Frame(MARGE, MARGE_H, LARGEUR_TEXTE, HAUTEUR_FLUX, id="corps",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        couv = Frame(MARGE, MARGE_H, LARGEUR_TEXTE, HAUTEUR_TEXTE, id="couv",
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        interc = Frame(MARGE, MARGE_H, LARGEUR_TEXTE, HAUTEUR_TEXTE, id="interc",
                       leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        return corps, couv, interc

    def build(self, flux, **kw):
        corps, couv, interc = self._cadres()
        self.addPageTemplates([
            PageTemplate(id="couverture", frames=[couv], onPage=self._dessiner_couverture),
            PageTemplate(id="intercalaire", frames=[interc], onPage=self._dessiner_intercalaire),
            PageTemplate(id="corps", frames=[corps], onPage=self._dessiner_corps),
        ])
        super().build(flux, **kw)

    # ── décors de page ------------------------------------------------
    def _dessiner_couverture(self, c: _canvas.Canvas, doc):
        c.saveState()
        c.setFillColor(ENCRE)
        c.rect(0, A4[1] - 9 * mm, A4[0], 9 * mm, stroke=0, fill=1)
        c.setFillColor(OR)
        c.rect(0, A4[1] - 9.9 * mm, A4[0], 0.9 * mm, stroke=0, fill=1)
        c.rect(0, 6.4 * mm, A4[0], 0.5 * mm, stroke=0, fill=1)
        c.setFillColor(PAPIER)
        c.setFont("Texte-Bold", 7.8)
        c.drawString(MARGE, A4[1] - 6.1 * mm, "CLÉOPÂTRE — ESPACE SANTÉ BEAUTÉ")
        c.drawRightString(A4[0] - MARGE, A4[1] - 6.1 * mm, "RAPPORT DE PROJET")
        c.setFillColor(GRIS)
        c.setFont("Texte", 7.2)
        c.drawCentredString(A4[0] / 2, 9.4 * mm,
                            "Document engendré par le dépôt : chaque chiffre est relu dans le code à la "
                            "construction (annexe F).")
        # ── double logo : marque du produit (vectorielle) + emplacement établissement [à poser]
        cx, cy, r0 = A4[0] / 2 - 13 * mm, A4[1] / 2 + 30 * mm, 7.4 * mm
        c.setStrokeColor(OR); c.setLineWidth(0.9)
        c.circle(cx, cy, r0, stroke=1, fill=0)
        c.setLineWidth(0.35)
        c.circle(cx, cy, r0 - 1.5 * mm, stroke=1, fill=0)
        c.setFillColor(OR)
        c.setFont("Display-Bold", 13)
        c.drawCentredString(cx, cy - 4.6, "C")
        c.setFillColor(GRIS)          # PAPIER sur PAPIER : la légende était invisible à l'impression
        c.setFont("Texte", 5.4)
        c.drawCentredString(cx, cy - r0 - 3.2 * mm, "ESPACE SANTÉ BEAUTÉ")
        c2 = A4[0] / 2 + 13 * mm
        c.setStrokeColor(PIERRE); c.setLineWidth(0.7)
        c.roundRect(c2 - r0, cy - r0, 2 * r0, 2 * r0, 1.6 * mm, stroke=1, fill=0)
        # le cadre fait la taille du monogramme : le texte long est posé sous le cadre, pas dedans,
        # et la police est réduite jusqu'à tenir — un gabarit qui déborde est un gabarit qui ment
        _largeur_utile = 2 * r0 - 4
        _corps = 6.2
        while _corps > 4.2 and c.stringWidth("[logo]", "Texte", _corps) > _largeur_utile:
            _corps -= 0.2
        c.setFillColor(GRIS); c.setFont("Texte", _corps)
        c.drawCentredString(c2, cy - 2, "[logo]")
        c.setFont("Texte", 5.4)
        c.drawCentredString(c2, cy - r0 - 3.2 * mm, "[établissement]")
        c.restoreState()

    def _dessiner_intercalaire(self, c: _canvas.Canvas, doc):
        c.saveState()
        c.setFillColor(ENCRE)
        c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        c.setFillColor(OR)
        c.rect(MARGE, A4[1] - 24 * mm, 44 * mm, 0.7 * mm, stroke=0, fill=1)
        c.rect(A4[0] - MARGE - 26 * mm, 14 * mm, 26 * mm, 0.4 * mm, stroke=0, fill=1)
        c.setFillColor(PIERRE)
        c.setFont("Texte", 7.4)
        c.drawString(MARGE, 16.5 * mm, "Cléopâtre — rapport de projet")
        c.setFillColor(PAPIER)
        c.drawRightString(A4[0] - MARGE, 16.5 * mm, f"page {c.getPageNumber()}")
        if getattr(doc, "_roman_courant", ""):
            c.setFillColor(OR)
            c.setFont("Texte-Bold", 8)
            c.drawRightString(A4[0] - MARGE, A4[1] - 24.5 * mm, doc._roman_courant)
        c.restoreState()

    def _dessiner_corps(self, c: _canvas.Canvas, doc):
        c.saveState()
        c.setFont("Texte", 7.1)
        c.setFillColor(GRIS)
        c.drawString(MARGE, A4[1] - 12.4 * mm, "Cléopâtre — rapport de projet")
        titre = getattr(doc, "_titre_courant", "")
        if titre:
            c.drawRightString(A4[0] - MARGE, A4[1] - 12.4 * mm, titre[:96])
        c.setStrokeColor(PIERRE)
        c.setLineWidth(0.35)
        c.line(MARGE, A4[1] - 13.8 * mm, A4[0] - MARGE, A4[1] - 13.8 * mm)
        c.setFillColor(OR)
        c.rect(MARGE, 13.4 * mm, 15 * mm, 0.45 * mm, stroke=0, fill=1)
        c.setFillColor(GRIS)
        c.setFont("Texte", 7.4)
        c.drawString(MARGE, 10.8 * mm, "Rapport de projet — [établissement à rappeler]")
        c.setFont("Texte-Bold", 8.2)
        c.setFillColor(ENCRE)
        c.drawRightString(A4[0] - MARGE, 10.6 * mm, str(c.getPageNumber()))
        c.restoreState()

    # ── relève --------------------------------------------------------
    def afterFlowable(self, fl):
        page = self.page
        if isinstance(fl, Signet):
            if fl.titre:
                self.registre.ancre(fl.cle, fl.titre, fl.niveau, page)
            if fl.niveau <= 2:
                self._titre_courant = fl.titre
            elif fl.niveau == 0:
                self._roman_courant = fl.titre
        elif isinstance(fl, Creux):
            self.registre.creux[fl.fid] = dict(page=page, via_png=fl.via_png)


# ──────────────────────────────────────────────────── helpers de tableau
def style_tableau(n_lignes: int, *, zebra: bool = True) -> TableStyle:
    cmds = [("BACKGROUND", (0, 0), (-1, 0), SABLE),
            ("LINEBELOW", (0, 0), (-1, 0), 0.7, ENCRE),
            ("GRID", (0, 0), (-1, -1), 0.26, PIERRE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3.6), ("RIGHTPADDING", (0, 0), (-1, -1), 3.6),
            ("TOPPADDING", (0, 0), (-1, -1), 2.4), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4)]
    if zebra:
        for i in range(1, n_lignes):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), colors.Color(0.96, 0.94, 0.89)))
    return TableStyle(cmds)
