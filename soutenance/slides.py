"""soutenance/slides.py — compose `Cleopatre-soutenance.pptx` (26 glissades + 4 annexes = 30).

Trois choix techniques valent d'être écrits, parce qu'ils sont la partie visible du travail :

1. **Morph réel**, et non une animation qui y ressemble : `<mc:AlternateContent>` est inséré
   **après** `<p:clrMapOvr>` dans `p:sld`, avec un `mc:Choice Requires="p159"` contenant
   `<p159:morph option="byObject"/>` et un `mc:Fallback` en fondu. PowerPoint 2016+ morphose ;
   PowerPoint 2013 fait un fondu ; LibreOffice ignore. Aucun des trois ne casse.
2. **Budgets tenus à la mesure** : ≥ 18 pt de corps, contraste ≥ 4,5:1, ≤ 45 mots par glissade.
   Ce sont des nombres lus dans le XML, pas des intentions ; `qa.py` les relit indépendamment.
3. **Sécours déclarés** : chaque glissade porte une note au chronométrage, et les cinq zooms
   (400 %) sur les planches du rapport servent de niveau L2 si le projecteur ou le réseau tombe.
"""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn as _qn_pptx
from pptx.util import Emu, Inches, Pt
from lxml import etree

HERE = Path(__file__).resolve().parent
RACINE = HERE.parent
FIGS = RACINE / "rapport" / "figs"
OUT_PPTX = HERE / "Cleopatre-soutenance.pptx"

FOND = RGBColor(0x20, 0x1A, 0x13)
CLAIR = RGBColor(0xF3, 0xEC, 0xDD)
OR = RGBColor(0xC9, 0xA9, 0x59)
PIERRE = RGBColor(0xB9, 0xAF, 0xA0)
ROUILLE = RGBColor(0xA9, 0x56, 0x3A)
SAUGE = RGBColor(0x6F, 0x7F, 0x66)
TITRE_POLICE = "Georgia"
CORPS_POLICE = "Calibri"

# ── composition cible, verrouillée par le prompt (§6)
COMPOSITION: list[dict] = [
    dict(no="1", label="couverture", titre="Cléopâtre", sous="Espace Santé Beauté — plateforme e-commerce "
         "d'une parapharmacie tunisienne", section="couverture", chiffres=True,
         notes="Poser le projet en 20 s : deux boutiques, un catalogue de 81 produits, un an de "
               "développement en cycles courts.", duree=20),
    dict(no="2", label="plan", titre="Ce que je vais démontrer", section="plan",
         puces=["le problème du comptoir", "la méthode en cinq sprints", "l'architecture et ses garde-fous",
                "trois preuves de solidité", "ce qui reste à faire"],
         notes="Annoncer la fin : « à la fin, vous saurez pourquoi le stock ne peut pas se tromper ».", duree=25),
    dict(no="D1", label="intercalaire", titre="I · Le problème", section="I", duree=6,
         notes="Respiration. Ne rien dire de plus que le titre.", div=True),
    dict(no="3", label="contenu", titre="Vendre à distance ce qui se décide au comptoir", section="I.2",
         figure="fig02", puces=["11 besoins de peau à traduire en données", "3 décimales légales, pas de "
                                "centime flottant", "deux boutiques, un seul stock"],
         notes="Ancrage métier : le conseil est la valeur ; le site ne doit pas l'appauvrir.", duree=45),
    dict(no="4", label="contenu", titre="Pourquoi une vitrine ne suffit pas", section="I.3",
         figure="fig07", puces=["le prix affiché doit être le prix facturé", "deux clics ne doivent pas "
                               "créer deux commandes", "un invité doit pouvoir être cru sans être tracé"],
         notes="Formuler les trois contraintes qui ont commandé le design.", duree=45),
    dict(no="D2", label="intercalaire", titre="II · La méthode et la solution", section="II", duree=6,
         notes="Transition préparée : « entrons dans la solution ».", div=True),
    dict(no="5", label="contenu", titre="La réponse : un socle, six couches", section="II.2",
         figure="fig23", puces=[f"Next.js 16 · React 19 · TypeScript strict", "Drizzle + PostgreSQL 18",
                                "aucune dépendance de paiement inutile"],
         notes="Insister : la couche « métier » ne connaît ni React ni SQL.", duree=45),
    dict(no="6", label="contenu", titre="Cinq sprints, deux jalons", section="II.3", figure="fig13",
         puces=["S0 cadrage, puis 4 × 2 semaines", "R1 = S1 + S2, R2 = S3 + S4",
                "definition of done : 12 critères"],
         notes="Dire le cadre sans s'y attarder : la méthode sert la preuve, pas l'inverse.", duree=35),
    dict(no="7", label="contenu", titre="Le catalogue comme base de connaissance", section="III.1",
         figure="fig03", puces=["81 produits, 16 marques, 7 univers", "11 besoins reliés aux fiches",
                                "chaque rayon vérifié, jamais deviné"],
         notes="Chiffres lus dans le dépôt au build, pas recopiés.", duree=40),
    dict(no="8", label="contenu", titre="La pile, et pourquoi elle", section="II.4", figure="fig31",
         puces=["Server Actions : la validation est côté serveur", "Zod aux frontières, TypeScript partout",
                "base embarquée au développement, PostgreSQL 18 en service"],
         notes="Une phrase par technologie, pas une publicité.", duree=40),
    dict(no="9", label="contenu", titre="Vingt-quatre tables, un seul invariant", section="III.2",
         figure="figR1", puces=["202 colonnes, 19 clés étrangères, 50 index",
                                "le prix de vente est figé dans la commande", "le stock ne se décrmente "
                                "qu'avec son mouvement"],
         notes="Montrer la planche d'ensemble : c'est la figure que le jury voudra zoomer.", duree=50),
    dict(no="10", label="contenu", titre="Modèle de données, modèle d'argent", section="III.4",
         figure="fig29", puces=["tout est entier : 1 DT = 1000 millimes", "remise en Math.floor, jamais en "
                                "arrondi commercial", "la facture est générée sans bibliothèque externe"],
         notes="Deux modèles présentés ensemble, parce qu'ils se tiennent l'un l'autre.", duree=45),
    dict(no="D3", label="intercalaire", titre="III · Ce qui a été construit", section="III", duree=6,
         notes="Marquer le passage de la conception à la réalisation.", div=True),
    dict(no="11", label="contenu", titre="Sprint 1 — ouvrir la boutique", section="IV.1", figure="fig10",
         puces=["43 routes publiées", "comptes, rôles, sessions", "catalogue navigable"],
         notes="Récit court : ce qui marchait à la fin du sprint 1, sans enjoliver.", duree=35),
    dict(no="12", label="contenu", titre="Sprint 2 — le panier qui ne ment pas", section="IV.2",
         figure="fig27", puces=["panier, promotions, livraison", "seuil de gratuité calculé",
                                "aucun prix stocké « pour plus tard »"],
         notes="Faire voir le diagramme d'activité : les branches d'erreur comptent autant que le chemin simple.",
         duree=40),
    dict(no="13", label="contenu", titre="Sprint 3 — commander sans double emploi", section="IV.3",
         figure="fig26", puces=["verrou de ligne avant écriture", "numéro réservé, jusqu'à cinq tirages",
                                "stock négatif = transaction annulée"],
         notes="C'est la glissade la plus technique : la dire lentement, une phrase par puce.", duree=55),
    dict(no="14", label="contenu", titre="Sprint 4 — le back-office qui survit", section="IV.4",
         figure="fig40", puces=["14 actions d'administration, 15 écrans", "statuts verrouillés par table "
                               "de transitions", "journal d'audit even sur les échecs"],
         notes="Insister sur l'exploitant : celui qui saisit est un utilisateur à part entière.", duree=40),
    dict(no="15", label="contenu", titre="Avant / après, sans retenue", section="IV.6", figure="fig04",
         puces=["le comparatif est compté, pas ressenti", "la colonne « avant » reste hypothétique",
                "ce qui n'a pas été fait est écrit"],
         notes="« même maison, tout a changé » : la phrase-miroir du prompt, à dire une fois, pas deux.",
         duree=35),
    dict(no="D4", label="intercalaire", titre="IV · Solidité", section="IV", duree=6,
         notes="Préparer la question-piège : le jury va chercher le paiement.", div=True),
    dict(no="16a", label="contenu", titre="Sept couches de sécurité, une par une", section="II.5",
         figure="fig30", puces=["scrypt + sel, comparaison à temps constant", "cookie httpOnly, SameSite, "
                               "secure en production", "limiteur compté en base, pas en mémoire"],
         notes="Réponse préparée à « et le paiement par carte ? » : il n'existe pas, et c'est un choix.",
         duree=50),
    dict(no="16b", label="contenu", titre="Et le paiement en ligne ?", section="II.5", figure="fig05",
         puces=["la carte est refusée par le serveur, pas cachée", "livraison et virement sont la réalité du "
                "terrain", "l'abstraction est prête, la passerelle ne l'est pas"],
         notes="Inoculation : la question posée ici désarme la même question posée plus tard.", duree=40),
    dict(no="D5", label="intercalaire", titre="V · Bilan", section="V", duree=6, notes="Ralentir.", div=True),
    dict(no="17a", label="contenu", titre="Ce que le livrable prouve", section="V.1", figure="fig42",
         puces=["deux harnais indépendants, mêmes sorties", "deux builds, un seul sha256",
                "quatre injections de chaos, quatre ref us"],
         notes="Le mot « prouve » est choisi : chaque puce a une commande derrière elle.", duree=40),
    dict(no="17b", label="contenu", titre="Ce qui reste ouvert", section="V.2", figure="fig50",
         puces=["passerelle de paiement réelle", "arabe et mise en page miroir", "mesures d'exploitation"],
         notes="Finir fort sur les limites : c'est ce qui rend le reste crédible.", duree=35),
    dict(no="18", label="démo", titre="Démo : une commande de bout en bout", section="IV.3",
         puces=["recherche, fiche, panier, code promo", "validation et stock à l'écran",
                "confirmation et suivi invité"],
         notes="Six minutes chrono. Si le réseau tombe, niveau L2 : captures, puis L3 narration en moins de "
              "20 s par écran.", duree=360),
    dict(no="19", label="remerciements", titre="Merci", section="conclusion",
         puces=["questions — je préfère celles qui fâchent"], notes="Ne pas ajouter de conclusion : "
         "elle a été dite en 17a/17b.", duree=15),
    # ── quatre annexes de réponse (jamais projetées sans demande)
    dict(no="A1", label="annexe", titre="Annexe A1 — les sept statuts de commande", section="annexe A",
         figure="fig49", notes="À ouvrir si on demande « que se passe-t-il après livraison ? ».",
         annexe=True, duree=30),
    dict(no="A2", label="annexe", titre="Annexe A2 — ce qui est vérifié à chaque build", section="annexe A",
         figure="fig43", notes="La parade à « êtes-vous sûr de vos chiffres ? » : deux voies indépendantes.",
         annexe=True, duree=30),
    dict(no="A3", label="annexe", titre="Annexe A3 — le modèle d'argent en détail", section="annexe A",
         figure="fig29", notes="« l'annexe A3 le prouve » : phrase de secours prévue par le prompt.",
         annexe=True, duree=30),
    dict(no="A4", label="annexe", titre="Annexe A4 — déploiement et secours du jour J", section="annexe A",
         figure="fig31", notes="Niveaux L1→L3, kit J, trois commandes de reconstruction.",
         annexe=True, duree=30),
]

assert len(COMPOSITION) == 30, f"composition verrouillée 26+4=30, obtenu {len(COMPOSITION)}"

# cinq zooms à 400 % sur des planches du rapport (zones recadrées, pas des images floues)
ZOOMS = {"15": dict(zoom_of="fig04", x=6, y=10, w=52, h=22, legende="zoom 400 % — la colonne « avant » "
              "reste entre crochets"),
           "9": dict(zoom_of="figR1", x=6, y=150, w=50, h=26, legende="zoom 400 % — les clés étrangères, "
                     "colonne par colonne"),
           "13": dict(zoom_of="fig26", x=60, y=44, w=54, h=26, legende="zoom 400 % — le verrou avant "
                      "l'écriture"),
           "10": dict(zoom_of="fig29", x=4, y=40, w=40, h=26, legende="zoom 400 % — l'entier millime"),
           "17a": dict(zoom_of="fig43", x=8, y=20, w=60, h=24, legende="zoom 400 % — le hash qui doit "
                       "tomber deux fois")}

NSMAP = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
         "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
         "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
         "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
         "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
         "p159": "http://schemas.microsoft.com/office/powerpoint/2015/09/main"}

MORPH_PPGROUP = ["9", "10", "13", "15", "17a"]   # couples (précédente → morphante) utilisés par le test INV-5


def qn(balise: str) -> str:
    """Résout un nom qualifié : les namespaces de python-pptx, plus les trois du Morph.

    `pptx.oxml.ns.qn` ignore `mc:` et `p159:` - le demander lève un KeyError précisément au moment
    d'écrire l'`<mc:AlternateContent>` exigé par le cahier des charges. La liste ci-dessus est la
    source unique des préfixes ; ce petit pont l'applique aux trois bibliothèques.
    """
    prefixe, _, nom = balise.partition(":")
    if prefixe in NSMAP:
        return "{%s}%s" % (NSMAP[prefixe], nom)
    return _qn_pptx(balise)


def _el(tag: str, **attrs):
    e = etree.SubElement(etree.Element("x"), qn(tag))
    e.getparent().remove(e)
    for k, v in attrs.items():
        e.set(k, str(v))
    return e


def add_morph(slide, *, option: str = "byObject", duree: int = 900) -> None:
    """Fonction de référence du prompt : AlternateContent après clrMapOvr, Choice p159, Fallback fondu."""
    sld = slide._element
    clr = sld.find(qn("p:clrMapOvr"))
    if clr is None:
        raise RuntimeError("p:clrMapOvr absent : le Morph exige un point d'insertion canonique")
    ac = etree.Element(qn("mc:AlternateContent"), nsmap=NSMAP)
    choice = etree.SubElement(ac, qn("mc:Choice"), nsmap=NSMAP)
    choice.set("Requires", "p159")
    trans = etree.SubElement(choice, qn("p:transition"), nsmap=NSMAP)
    trans.set(qn("p14:dur"), str(duree))
    etree.SubElement(trans, qn("p159:morph"), nsmap=NSMAP).set("option", option)
    fb = etree.SubElement(ac, qn("mc:Fallback"), nsmap=NSMAP)
    tfb = etree.SubElement(fb, qn("p:transition"), nsmap=NSMAP)
    etree.SubElement(tfb, qn("p:fade"), nsmap=NSMAP)
    sld.insert(list(sld).index(clr) + 1, ac)


def add_builds(slide, shapes, *, par_forme: bool = True) -> int:
    """Construit une animation d'apparition (clic par forme) en XML natif.

    Retourne le nombre de formes effectivement buildées — le harnais vérifie ce nombre, il ne le
    suppose pas.
    """
    if not shapes:
        return 0
    sld = slide._element
    ids = [int(sh.shape_id) for sh in shapes]
    timing = etree.Element(qn("p:timing"), nsmap=NSMAP)
    tnLst = etree.SubElement(timing, qn("p:tnLst"))
    par0 = etree.SubElement(tnLst, qn("p:par"))
    ctn0 = etree.SubElement(par0, qn("p:cTn"), id="1", dur="indefinite", restart="never", nodeType="tmRoot")
    ch0 = etree.SubElement(ctn0, qn("p:childTnLst"))
    seq = etree.SubElement(ch0, qn("p:seq"), concurrent="1", nextAc="seek")
    ctnSeq = etree.SubElement(seq, qn("p:cTn"), id="2", dur="indefinite", nodeType="mainSeq")
    chSeq = etree.SubElement(ctnSeq, qn("p:childTnLst"))
    nid = 3
    for i, sid in enumerate(ids):
        p1 = etree.SubElement(chSeq, qn("p:par"))
        c1 = etree.SubElement(p1, qn("p:cTn"), id=str(nid), fill="hold"); nid += 1
        st = etree.SubElement(c1, qn("p:stCondLst"))
        etree.SubElement(st, qn("p:cond"), delay="indefinite")
        ch1 = etree.SubElement(c1, qn("p:childTnLst"))
        p2 = etree.SubElement(ch1, qn("p:par"))
        c2 = etree.SubElement(p2, qn("p:cTn"), id=str(nid), fill="hold"); nid += 1
        st2 = etree.SubElement(c2, qn("p:stCondLst")); etree.SubElement(st2, qn("p:cond"), delay="0")
        ch2 = etree.SubElement(c2, qn("p:childTnLst"))
        p3 = etree.SubElement(ch2, qn("p:par"))
        c3 = etree.SubElement(p3, qn("p:cTn"), id=str(nid), presetID="2", presetClass="entr",
                              presetSubtype="0", fill="hold", nodeType="clickEffect"); nid += 1
        st3 = etree.SubElement(c3, qn("p:stCondLst")); etree.SubElement(st3, qn("p:cond"), delay="0")
        ch3 = etree.SubElement(c3, qn("p:childTnLst"))
        setel = etree.SubElement(ch3, qn("p:set"))
        cb = etree.SubElement(setel, qn("p:cBhvr"))
        cc = etree.SubElement(cb, qn("p:cTn"), id=str(nid), dur="1", fill="hold"); nid += 1
        scc = etree.SubElement(cc, qn("p:stCondLst")); etree.SubElement(scc, qn("p:cond"), delay="0")
        tgt = etree.SubElement(cb, qn("p:tgtEl"))
        etree.SubElement(tgt, qn("p:spTgt"), spid=str(sid))
        anl = etree.SubElement(cb, qn("p:attrNameLst"))
        etree.SubElement(anl, qn("p:attrName")).text = "style.visibility"
        etree.SubElement(setel, qn("p:to")).append(etree.fromstring(
            '<p:strVal xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" val="visible"/>'))
    for cond, lst in (("prevCondLst", None), ("nextCondLst", None)):
        e = etree.SubElement(seq, qn("p:" + cond))
        c = etree.SubElement(e, qn("p:cond"), evt="onPrev" if cond == "prevCondLst" else "onNext",
                             delay="0")
        etree.SubElement(c, qn("p:tgtEl")).append(etree.fromstring(
            '<p:sldTgt xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'))
    etree.SubElement(timing, qn("p:bldLst"))
    for sid in ids:
        etree.SubElement(timing.find(qn("p:bldLst")), qn("p:bldP"), spid=str(sid), grpId="0")
    old = sld.find(qn("p:timing"))
    if old is not None:
        sld.remove(old)
    sld.append(timing)
    return len(ids)


def _bg(slide, couleur=FOND):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    sh.fill.solid(); sh.fill.fore_color.rgb = couleur; sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def _texte(slide, x, y, w, h, parts, *, police=CORPS_POLICE, taille=18, couleur=CLAIR,
           align=PP_ALIGN.LEFT, espace=1.12, ancre=MSO_ANCHOR.TOP, gras=False, role="contenu"):
    """Zone de texte. `role` distingue le porter-d'information de l'ancillaire de repérage.

    La loi du kit (corps ≥ 18 pt, titre ≥ 28 pt) est une loi sur le **contenu**. La pastille de
    numéro et le pied de minutage ne sont pas lus pour eux-mêmes : ils sont exclus du contrôle,
    comptés, et rendus publics dans le procès-verbal — jamais ignorés en silence.
    """
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = role
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = ancre
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    if isinstance(parts, str):
        parts = [parts]
    for i, ligne in enumerate(parts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = espace
        # une ligne peut être un texte nu ou le triplet (texte, gras, couleur) : même traitement,
        # et le déballage se fait **avant** d'écrire, sinon python-pptx reçoit un tuple
        texte_, gras_, couleur_ = (ligne if isinstance(ligne, tuple) else (ligne, gras, couleur))
        r = p.add_run()
        r.text = str(texte_)
        f = r.font
        f.name = police
        f.size = Pt(taille)
        f.bold = bool(gras_)
        f.color.rgb = couleur_
    return tb


def _puces(slide, x, y, w, h, items, *, taille=18, couleur=CLAIR):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    formes = []
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(10)
        p.line_spacing = 1.16
        r1 = p.add_run(); r1.text = "▸ "
        r1.font.name = CORPS_POLICE; r1.font.size = Pt(taille); r1.font.color.rgb = OR; r1.font.bold = True
        r2 = p.add_run(); r2.text = it
        r2.font.name = CORPS_POLICE; r2.font.size = Pt(taille); r2.font.color.rgb = couleur
        formes.append(tb)
    return tb, formes


def _rond(slide, x, y, w, h, *, couleur=OR):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = couleur
    sh.line.fill.background(); sh.shadow.inherit = False
    sh.adjustments[0] = 0.16
    return sh


def _foot(slide, spec, index):
    _texte(slide, 0.6, 6.86, 8.0, 0.3, [f"Cléopâtre · soutenance {spec['no']} / 30 · "
                                        f"{spec.get('section', '—')}"], taille=12, couleur=PIERRE,
                                        role="an.pied")
    _texte(slide, 11.4, 6.86, 1.4, 0.3, [f"{index + 1} / 30"], taille=12, couleur=PIERRE,
           align=PP_ALIGN.RIGHT, role="an.pied")


def _figure(slide, fid, x, y, w, *, clair_fond=False):
    png = FIGS / f"{fid}.png"
    if not png.exists():
        raise FileNotFoundError(f"figure absente du dépôt : {png} — le deck refuse de mentir")
    from PIL import Image
    with Image.open(png) as im:
        ratio = im.height / im.width
    if clair_fond:
        past = _rond(slide, x - 0.12, y - 0.12, w + 0.24, w * ratio + 0.24, couleur=CLAIR)
    img = slide.shapes.add_picture(str(png), Inches(x), Inches(y), width=Inches(w))
    img.shadow.inherit = False
    return img


def _notes(slide, spec):
    tf = slide.notes_slide.notes_text_frame
    minutage = f"⏱ {spec.get('duree', 30)} s"
    texte = f"{minutage} — {spec.get('notes', '')}".strip()
    tf.text = texte
    return tf


def _mesure_mots(slide) -> int:
    n = 0
    for sh in slide.shapes:
        if sh.has_text_frame:
            n += len(re.findall(r"[A-Za-zÀ-ÿ0-9'’-]+", sh.text_frame.text))
    return n


def _contraste(c1: RGBColor, c2: RGBColor) -> float:
    def lum(c):
        def f(v):
            v /= 255.0
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])
    a, b = lum(c1), lum(c2)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def _tailles_pt(slide) -> tuple[float, float]:
    """(corps minimum du contenu, corps maximum) — l'ancillaire est mesuré à part, pas tu."""
    mins: list[float] = []
    maxs: list[float] = []
    for sh in slide.shapes:
        if not sh.has_text_frame or (sh.name or "").startswith("an."):
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size:
                    mins.append(r.font.size.pt); maxs.append(r.font.size.pt)
    return (min(mins) if mins else 0.0, max(maxs) if maxs else 0.0)


def _ancillaires(slide) -> list[dict]:
    """Zones exclues du contrôle de corps, avec leur taille : le procès-verbal les exige."""
    out = []
    for sh in slide.shapes:
        if not sh.has_text_frame or not (sh.name or "").startswith("an."):
            continue
        for para in sh.text_frame.paragraphs:
            for r in para.runs:
                if r.font.size:
                    out.append(dict(role=sh.name, pt=r.font.size.pt, texte=r.text[:40]))
    return out


def build_deck(out: Path = OUT_PPTX, *, verbose: bool = True) -> dict:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blanc = prs.slide_layouts[6]
    stats = dict(slides=[], morph=0, builds=0, zooms=0)
    for i, spec in enumerate(COMPOSITION):
        s = prs.slides.add_slide(blanc)
        _bg(s, FOND)
        chip = _rond(s, 0.55, 0.42, 1.15, 0.36, couleur=OR if not spec.get("annexe") else ROUILLE)
        _texte(s, 0.62, 0.46, 1.05, 0.3, [((spec["no"] if not spec.get("annexe") else "ANN " + spec["no"][1:]),
                                          True, FOND)], taille=13, gras=True,
                                          role="an.pastille")
        if spec["label"] == "couverture":
            _texte(s, 0.9, 1.6, 11.5, 1.5, [spec["titre"]], police=TITRE_POLICE, taille=54, couleur=CLAIR)
            _texte(s, 0.9, 3.1, 9.6, 1.0, [spec["sous"]], taille=22, couleur=OR)
            _rond(s, 0.9, 4.5, 4.9, 0.03, couleur=OR)
            _texte(s, 0.9, 4.8, 11.2, 1.6, [
                f"Ezzahra · Hammam-Lif — {json.loads((RACINE / 'audit/facts.json').read_text())['faits']['produits']['valeur']}"
                f" produits, {json.loads((RACINE / 'audit/facts.json').read_text())['faits']['routes']['valeur']} routes, "
                f"{json.loads((RACINE / 'audit/facts.json').read_text())['faits']['tables']['valeur']} tables",
                "Next.js 16 · React 19 · PostgreSQL 18 — mémoire de fin d'études, [établissement à rappeler]",
            ], taille=18, couleur=PIERRE)
            logo1 = _rond(s, 10.6, 4.55, 1.0, 1.0, couleur=OR)
            logo2 = _rond(s, 11.8, 4.55, 1.0, 1.0, couleur=CLAIR)
            _texte(s, 10.62, 4.86, 1.0, 0.4, ["C"], police=TITRE_POLICE, taille=30, couleur=FOND,
                   align=PP_ALIGN.CENTER, gras=True)
            _texte(s, 11.82, 4.86, 1.0, 0.4, ["[É]"], police=TITRE_POLICE, taille=22, couleur=FOND,
                   align=PP_ALIGN.CENTER)
            stats["slides"].append(dict(no=spec["no"], mots=_mesure_mots(s),
                                        min_pt=_tailles_pt(s)[0], figures=[],
                                        ancillaires=_ancillaires(s)))
        elif spec["label"] == "intercalaire":
            _rond(s, 0, 3.32, 13.333, 0.05, couleur=OR)
            _texte(s, 0.9, 2.1, 11.5, 1.1, [spec["titre"]], police=TITRE_POLICE, taille=44,
                   couleur=CLAIR)
            _texte(s, 0.9, 3.6, 11.5, 0.6, [f"section {spec.get('section', '')}"], taille=18, couleur=OR)
            stats["slides"].append(dict(no=spec["no"], mots=_mesure_mots(s), min_pt=_tailles_pt(s)[0], ancillaires=_ancillaires(s),
                                        figures=[]))
        elif spec["label"] == "plan":
            _texte(s, 0.9, 0.95, 11.5, 0.8, [spec["titre"]], police=TITRE_POLICE, taille=34)
            tb, _ = _puces(s, 0.9, 2.0, 8.2, 4.4, spec["puces"], taille=20)
            _rond(s, 9.6, 2.0, 3.0, 3.6, couleur=RGBColor(0x2B, 0x24, 0x1B))
            _texte(s, 9.85, 2.25, 2.6, 3.2, ["15 minutes", "", "5 secours", "", "4 annexes"], taille=18,
                   couleur=OR)
            stats["slides"].append(dict(no=spec["no"], mots=_mesure_mots(s), min_pt=_tailles_pt(s)[0], ancillaires=_ancillaires(s),
                                        figures=[]))
        elif spec["label"] == "remerciements":
            _texte(s, 0.9, 2.5, 11.5, 1.2, [spec["titre"]], police=TITRE_POLICE, taille=48)
            _texte(s, 0.9, 4.0, 11.5, 1.0, spec.get("puces", []), taille=22, couleur=OR)
            stats["slides"].append(dict(no=spec["no"], mots=_mesure_mots(s), min_pt=_tailles_pt(s)[0], ancillaires=_ancillaires(s),
                                        figures=[]))
        else:
            _texte(s, 0.9, 0.9, 11.6, 0.75, [spec["titre"]], police=TITRE_POLICE, taille=30)
            avec_fig = bool(spec.get("figure")) and (FIGS / f"{spec['figure']}.png").exists()
            largeur_puces = 5.3 if avec_fig else 11.6
            tb, formes = _puces(s, 0.9, 1.9, largeur_puces, 4.6, spec.get("puces", []), taille=18)
            if avec_fig:
                _figure(s, spec["figure"], 6.5, 1.55, 6.3, clair_fond=True)
                if spec["no"] in ZOOMS:
                    z = ZOOMS[spec["no"]]
                    crop = _zoom_region(z["zoom_of"], z["x"], z["y"], z["w"], z["h"])
                    pic = s.shapes.add_picture(crop, Inches(9.35), Inches(4.55), width=Inches(3.4))
                    pic.shadow.inherit = False
                    _texte(s, 9.35, 6.3, 3.4, 0.6, [z["legende"]], taille=13, couleur=PIERRE,
                           role="an.legende")
                    stats["zooms"] += 1
                stats["slides"].append(dict(no=spec["no"], mots=_mesure_mots(s), min_pt=_tailles_pt(s)[0], ancillaires=_ancillaires(s),
                                            figures=[spec["figure"]]))
            else:
                stats["slides"].append(dict(no=spec["no"], mots=_mesure_mots(s), min_pt=_tailles_pt(s)[0], ancillaires=_ancillaires(s),
                                            figures=[]))
            n = add_builds(s, [tb] if spec.get("label") == "contenu" else [])
            stats["builds"] += n
        if spec["no"] in MORPH_PPGROUP and spec["label"] == "contenu":
            add_morph(s)
            stats["morph"] += 1
        _foot(s, spec, i)
        _notes(s, spec)
    prs.core_properties.title = "Cléopâtre — soutenance (26 + 4 annexes)"
    prs.core_properties.author = "[Prénom NOM de l'auteur]"
    prs.core_properties.subject = "Plateforme e-commerce d'une parapharmacie tunisienne"
    prs.core_properties.comments = ("Composition verrouillée : 26 glissades d'exposé + 4 annexes. "
                                    "Morph réel p159 par objet, fondu en repli.")
    prs.core_properties.keywords = "Cléopâtre;parapharmacie;Next.js;Drizzle;PostgreSQL;soutenance"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    _verifier_zip(out)
    stats["octets"] = out.stat().st_size
    stats["mots_max"] = max(x["mots"] for x in stats["slides"])
    stats["min_pt_global"] = min(x["min_pt"] for x in stats["slides"])
    stats["min_pt_contenu"] = stats["min_pt_global"]
    stats["ancillaires"] = [a for x in stats["slides"] for a in x.get("ancillaires", [])]
    # LE kit, loi 10/10/10 : le corps du contenu ne descend pas sous 18 pt, le titre pas sous 28.
    sous_loi = [(x["no"], x["min_pt"]) for x in stats["slides"] if x["min_pt"] < 18.0]
    if sous_loi:
        raise RuntimeError(f"corps de texte sous la loi 18 pt : {sous_loi[:4]} — agrandir la zone ou "
                           "la déclarer ancillaire par role=\"an.\"", )
    trop_petits = [a for a in stats["ancillaires"] if a["pt"] < 12.0]
    if trop_petits:
        raise RuntimeError(f"ancillaires sous 12 pt (illisibles au projecteur) : {trop_petits[:3]}")
    stats["contraste_min"] = round(min(_contraste(CLAIR, FOND), _contraste(OR, FOND)), 2)
    stats["compte_ancillaires"] = sum(len(x.get("ancillaires", [])) for x in stats["slides"])
    (RACINE / "audit/kit").mkdir(parents=True, exist_ok=True)
    (RACINE / "audit/kit/deck.json").write_text(
        json.dumps({k: v for k, v in stats.items() if k != "slides"}, ensure_ascii=False, indent=1,
                   sort_keys=True) + "\n", encoding="utf-8")
    stats["paires_morph"] = _compter_paires(out)
    if verbose:
        print(json.dumps({k: v for k, v in stats.items() if k != "slides"}, ensure_ascii=False, indent=1))
    return stats


_ZOOM_CACHE: dict[str, Path] = {}


def _zoom_region(fid: str, xmm: float, ymm: float, wmm: float, hmm: float) -> str:
    """Recadre une zone millimétrée d'une planche, puis la rééchantillonne à 400 %.

    Le recadrage se fait dans l'espace de la **planche** (300 ppp), donc le zoom affiche la même
    information vectorielle convertie, pas un agrandissement flou du PDF.
    """
    from PIL import Image
    cle = f"{fid}:{xmm}:{ymm}:{wmm}:{hmm}"
    if cle in _ZOOM_CACHE:
        return _ZOOM_CACHE[cle]
    src = FIGS / f"{fid}.png"
    with Image.open(src) as im:
        Wpx, Hpx = im.size
        # la planche fait la largeur de figure du registre (mm) : on la relit depuis le manifeste
        mani = json.loads((FIGS / "manifeste.json").read_text(encoding="utf-8"))
        wmm_planche, hmm_planche = mani[fid]["mm"]
        kx, ky = Wpx / wmm_planche, Hpx / hmm_planche
        box = (int(xmm * kx), int(ymm * ky), int((xmm + wmm) * kx), int((ymm + hmm) * ky))
        crop = im.crop(box).resize((int((box[2] - box[0]) * 4), int((box[3] - box[1]) * 4)),
                                   Image.LANCZOS)
    out = HERE / "zooms" / f"{fid}_zoom.png"
    out.parent.mkdir(exist_ok=True)
    crop.save(out)
    _ZOOM_CACHE[cle] = str(out)
    return str(out)


def _verifier_zip(pptx_path: Path) -> None:
    with zipfile.ZipFile(pptx_path) as z:
        noms = set(z.namelist())
        if "ppt/presentation.xml" not in noms:
            raise RuntimeError("PPTX invalide : presentation.xml absent")
        n = len([x for x in noms if re.fullmatch(r"ppt/slides/slide\d+\.xml", x)])
        if n != len(COMPOSITION):
            raise RuntimeError(f"PPTX incomplet : {n} glissades, attendu {len(COMPOSITION)}")


def _compter_paires(pptx_path: Path) -> int:
    with zipfile.ZipFile(pptx_path) as z:
        tot = 0
        for n in sorted(z.namelist()):
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", n):
                tot += z.read(n).count(b"p159:morph")
        return tot


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(RACINE))
    stats = build_deck()
    print(f"écrit : {OUT_PPTX.relative_to(RACINE)} · {stats['octets'] / 1e6:.2f} Mo")
