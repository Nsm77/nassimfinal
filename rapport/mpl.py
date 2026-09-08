"""rapport/mpl.py — style de la maison pour toutes les figures.

Lois appliquées ici (et non promises) :
  * palette encre/or/pierre/sauge/rouille sur papier, **aucun sens porté par la seule couleur**
    (forme + trame + libellé), donc N&B et daltonisme tenus ;
  * chaque figure est sauvée en PDF **et** PNG avec des dimensions identiques (ratios égaux) ;
  * emoji et glyphes bannis refusés à l'écriture (`_assert_glyphs`) ;
  * la figure est dessinée en millimètres : le PDF de sortie a exactement la boîte demandée,
    ce qui rend le placage `merge_transformed_page` sans surprise ;
  * les nombres viennent de `facts.py` — aucune constante de comptage n'est tapée ici.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figs"
MM = 72 / 25.4

# ── palette (contrastes mesurés dans qa.py, pas décoratifs)
PAPIER = "#F5F1E8"
ENCRE = "#2B2620"
OR = "#C9A959"
PIERRE = "#B9AFA0"
SAUGE = "#6F7F66"
ROUILLE = "#A9563A"
SABLE = "#E3D9C6"
NUANCES = [ENCRE, OR, SAUGE, ROUILLE, PIERRE, "#5B6C7C", "#8C6A4F"]
TRAMES = ["", "///", "\\\\", "...", "xxx", "+++", "--"]

_BANNED = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2028\u2029]")


def _assert_glyphs(*texts: str) -> None:
    """Aucun emoji / symbole technique dans les figures : DejaVu les a, mais le print N&B non plus."""
    for t in texts:
        bad = _BANNED.findall(t)
        if bad:
            raise ValueError(f"glyphe bannis dans une figure : {bad!r} dans {t!r}")


def install_style() -> None:
    """DejaVu partout : c'est la seule famille dont le glyphe U+202F est vérifié ici."""
    dejavu = [f for f in font_manager.findSystemFonts() if "DejaVu" in f]
    if not dejavu:
        raise RuntimeError("DejaVu absent : le style de la maison exige cette famille (test U+202F).")
    for f in dejavu:
        font_manager.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 7.6,
        "axes.titlesize": 9.2,
        "axes.labelsize": 7.8,
        "axes.edgecolor": ENCRE,
        "axes.linewidth": 0.6,
        "axes.grid": True,
        "grid.color": PIERRE,
        "grid.linewidth": 0.4,
        "grid.alpha": 0.55,
        "axes.axisbelow": True,
        "figure.facecolor": PAPIER,
        "savefig.facecolor": PAPIER,
        "text.color": ENCRE,
        "axes.labelcolor": ENCRE,
        "xtick.color": ENCRE,
        "ytick.color": ENCRE,
        "legend.frameon": False,
        "savefig.bbox": None,
        "pdf.fonttype": 42,      # TrueType → texte vectoriel sélectionnable dans le PDF
        "svg.fonttype": "none",
        "hatch.linewidth": 0.6,
        "lines.markersize": 5,
    })


install_style()


# ── géométrie en millimètres
def canvas(w_mm: float, h_mm: float, *, dpi: int = 300):
    fig = plt.figure(figsize=(w_mm / 25.4, h_mm / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_mm)
    ax.set_ylim(0, h_mm)
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_facecolor(PAPIER)
    fig.patch.set_facecolor(PAPIER)
    return fig, ax


def panel(ax, x, y, w, h, *, fill=PAPIER, edge=ENCRE, lw=0.8, r=2.2, hatch=None, alpha=1.0):
    """Boîte dont l'emprise fait **exactement** w×h mm (pad=0) : le placage millimétré du §5 ne peut
    alors ni déborder ni laisser de blanc — c'est ce qu'assert `rapport/build.py` (grille)."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                linewidth=lw, edgecolor=edge, facecolor=(fill or "none"),
                                hatch=hatch, alpha=alpha, mutation_aspect=1))


def plate(ax, x, y, w, h, *, title=None, sub=None, fill=SABLE, edge=ENCRE, hatch=None, lw=0.7, fs=7.4):
    """Bloc étiqueté : la trame + le libellé portent le sens, jamais la couleur seule."""
    panel(ax, x, y, w, h, fill=fill, edge=edge, hatch=hatch, lw=lw)
    cy = y + h / 2
    if title:
        _assert_glyphs(title)
        ax.text(x + 2.6, cy - (2.0 if sub else 0), title, ha="left", va="center",
                fontsize=fs, color=ENCRE, fontweight="bold")
    if sub:
        _assert_glyphs(sub)
        ax.text(x + 2.6, cy + 2.4, sub, ha="left", va="center", fontsize=fs - 1.0, color=ENCRE, alpha=0.82)


def arrow(ax, x1, y1, x2, y2, *, color=ENCRE, lw=0.9, style="-|>", rad=0.0, ls="-", alpha=1.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                 arrowprops=dict(arrowstyle=style, color=color, lw=lw, linestyle=ls,
                                 alpha=alpha, shrinkA=1.5, shrinkB=1.5,
                                 connectionstyle=f"arc3,rad={rad}"))


def dt_fr(valeur: float, decimales: int = 3) -> str:
    """Montant en dinars à la française pour une figure : virgule, zéros superflus retirés.

    Les figures ne passent pas par le moteur de prose du rapport ; sans cet appel, elles imprimeraient
    « 64.019 DT ». Les trois décimales sont gardées dès qu'elles disent quelque chose, et 14,9 DT
    n'est pas arrondi à 15 : le chiffre du dépôt reste le chiffre du document.
    """
    texte = f"{float(valeur):.{decimales}f}".rstrip("0").rstrip(".")
    entier, _, dec = texte.partition(".")
    entier_fmt = f"{int(entier):,d}".replace(",", "\u202f")
    return (f"{entier_fmt},{dec}\u202fDT" if dec else f"{entier_fmt}\u202fDT")


def note(ax, x, y, text, *, fs=6.4, ha="left", color=ENCRE, style="italic", weight="normal"):
    _assert_glyphs(text)
    ax.text(x, y, text, fontsize=fs, ha=ha, va="top", color=color, style=style, fontweight=weight, zorder=6)


def title_of(ax, x, y, main, sub=None, *, fs=11.0):
    _assert_glyphs(main, *( [sub] if sub else [] ))
    ax.text(x, y, main, fontsize=fs, fontweight="bold", color=ENCRE, ha="left", va="center")
    if sub:
        ax.text(x, y + 5.0, sub, fontsize=fs - 3.4, color=ENCRE, alpha=0.8, ha="left", va="center")


def rule(ax, x1, x2, y, *, color=OR, lw=1.4):
    ax.plot([x1, x2], [y, y], color=color, lw=lw, solid_capstyle="butt", zorder=5)


def key_for(i: int) -> tuple[str, str]:
    """(couleur, trame) — la paire garantit forme+trame+libellé, jamais la couleur seule."""
    return NUANCES[i % len(NUANCES)], TRAMES[i % len(TRAMES)]


def bars(ax, x, y, w, h, data: list[tuple[str, float]], *, horizontal=True, unit="", fs=7.0,
         value_fmt="{:.0f}", title=None, palette=None, show_values=True):
    """Barres dessinées à la main (pas d'axes matplotlib) → contrôle typographique total."""
    if not data:
        raise ValueError("bars() sans données")
    n = len(data)
    vmax = max(abs(v) for _, v in data) or 1
    if title:
        _assert_glyphs(title)
        ax.text(x, y - 2.4, title, fontsize=fs + 0.8, fontweight="bold", va="bottom", ha="left", color=ENCRE)
    if horizontal:
        bh = h / n
        lab_w = w * 0.30
        for i, (lab, v) in enumerate(data):
            _assert_glyphs(lab)
            yy = y + i * bh + bh * 0.16
            col, hat = (palette[i % len(palette)], None) if palette else key_for(i)
            ax.text(x, yy + bh * 0.34, lab, fontsize=fs, va="center", ha="left", color=ENCRE)
            bw = (w - lab_w - 16) * (abs(v) / vmax)
            ax.add_patch(Rectangle((x + lab_w, yy), max(bw, 0.4), bh * 0.68, facecolor=col,
                                   edgecolor=ENCRE, lw=0.5, hatch=hat))
            if show_values:
                _assert_glyphs(str(v))
                ax.text(x + lab_w + bw + 1.6, yy + bh * 0.34, value_fmt.format(v) + unit,
                        fontsize=fs - 0.4, va="center", ha="left", color=ENCRE)
    else:
        bw = w / n
        for i, (lab, v) in enumerate(data):
            col, hat = key_for(i)
            hh = (h - 8) * (abs(v) / vmax)
            ax.add_patch(Rectangle((x + i * bw + bw * 0.18, y + h - hh), bw * 0.64, hh,
                                   facecolor=col, edgecolor=ENCRE, lw=0.5, hatch=hat))
            _assert_glyphs(lab, str(v))
            ax.text(x + i * bw + bw / 2, y + h + 1.6, lab, fontsize=fs - 1.0, ha="center", va="top",
                    color=ENCRE, rotation=0)
            ax.text(x + i * bw + bw / 2, y + h - hh - 2.4, value_fmt.format(v), fontsize=fs - 0.8,
                    ha="center", va="bottom", color=ENCRE)


def legend(ax, x, y, entries: list[str], *, fs=6.6, per_row=None, dx=34.0, dy=4.6):
    n = per_row or len(entries)
    for i, e in enumerate(entries):
        col, hat = key_for(i)
        cx, cy = x + (i % n) * dx, y + (i // n) * dy
        ax.add_patch(Rectangle((cx, cy), 3.6, 2.6, facecolor=col, edgecolor=ENCRE, lw=0.5, hatch=hat))
        _assert_glyphs(e)
        ax.text(cx + 4.8, cy + 1.3, e, fontsize=fs, va="center", ha="left", color=ENCRE)


def grid_dots(ax, x, y, w, h, *, step=5.0, color=PIERRE):
    for gx in range(int(x), int(x + w), int(step)):
        for gy in range(int(y), int(y + h), int(step)):
            ax.plot(gx, gy, ".", color=color, ms=0.7, alpha=0.5)


# ── registre
@dataclass
class Figure:
    id: str
    title: str
    width_mm: float
    height_mm: float
    draw: object = None
    caption: str = ""
    source: str = ""      # gisement du fait principal (fichier:ligne)
    kind: str = "figure"
    tags: list[str] = field(default_factory=list)

    def save(self, out: Path, *, dpi: int = 300) -> dict:
        fig, ax = canvas(self.width_mm, self.height_mm, dpi=dpi)
        self.draw(ax, self)
        # Filet général : **tout** texte présent dans la figure est audité, y compris celui écrit
        # par un ax.text direct qui contournerait les helpers. Un emoji = build rouge.
        _assert_glyphs(self.title, self.caption, self.source,
                       *(t.get_text() for t in ax.texts))
        base = out / self.id
        fig.savefig(base.with_suffix(".pdf"))
        fig.savefig(base.with_suffix(".png"), dpi=dpi)
        import matplotlib.pyplot as plt
        plt.close(fig)
        from pypdf import PdfReader
        from PIL import Image
        r = PdfReader(str(base.with_suffix(".pdf")))
        box = r.pages[0].mediabox
        pw, ph = float(box.width) / MM, float(box.height) / MM
        with Image.open(base.with_suffix(".png")) as im:
            png_ratio = im.width / im.height
        ratio = self.width_mm / self.height_mm
        # ASSERT : ratios identiques (prompt §5) — sinon le placage mm déformerait.
        assert abs(pw - self.width_mm) < 0.6, f"{self.id}: boîte PDF {pw:.2f} ≠ {self.width_mm:.2f} mm"
        assert abs(ph - self.height_mm) < 0.6, f"{self.id}: boîte PDF {ph:.2f} ≠ {self.height_mm:.2f} mm"
        assert abs(png_ratio - ratio) < 0.02, f"{self.id}: ratio PNG {png_ratio:.4f} ≠ PDF {ratio:.4f}"
        return dict(id=self.id, mm=[round(pw, 2), round(ph, 2)], png_ratio=round(png_ratio, 4),
                    pdf_ratio=round(pw / ph, 4), octets_pdf=base.with_suffix('.pdf').stat().st_size,
                    octets_png=base.with_suffix('.png').stat().st_size)


REGISTRE: dict[str, Figure] = {}


def figure(id_, titre, *, w=170.0, h=92.0, caption="", source="", tags=()):
    def deco(fn):
        if id_ in REGISTRE:
            raise ValueError(f"figure dupliquée : {id_}")
        REGISTRE[id_] = Figure(id=id_, title=titre, width_mm=w, height_mm=h, draw=fn,
                               caption=caption, source=source, tags=list(tags))
        return fn
    return deco


def register(id_: str, titre: str, draw, *, w: float = 170.0, h: float = 92.0,
             caption: str = "", source: str = "", tags=()) -> None:
    """Enregistrement impératif (complément du décorateur `figure`)."""
    if id_ in REGISTRE:
        raise ValueError(f"figure dupliquée : {id_}")
    REGISTRE[id_] = Figure(id=id_, title=titre, width_mm=w, height_mm=h, draw=draw,
                           caption=caption, source=source, tags=list(tags))


def build_all(only: set[str] | None = None, out: Path = FIGS, *, dpi: int = 300) -> dict:
    """Dessine (ou redessine) les figures et écrit figs/manifeste.json."""
    out.mkdir(parents=True, exist_ok=True)
    ids = [k for k in sorted(REGISTRE) if only is None or k in only]
    if not ids:
        raise RuntimeError("registre de figures vide : aucun module figs chargé ?")
    infos = {}
    for k in ids:
        infos[k] = REGISTRE[k].save(out, dpi=dpi)
    (out / "manifeste.json").write_text(json.dumps(infos, ensure_ascii=False, indent=1, sort_keys=True),
                                        encoding="utf-8")
    return infos


def import_all() -> None:
    """Charge tous les modules de planches présents (figref.py, figs1.py … figsN.py).

    La découverte est dynamique : ajouter une planche = ajouter un fichier, sans rien énumérer
    ailleurs. C'est ce qui rend l'oubli de plaque visible (le manifeste serait incomplet) plutôt
    que silencieux.
    """
    import importlib
    pkg = __package__ if __package__ not in (None, "") else ROOT_PKG
    mods = sorted(x.stem for x in HERE.glob("fig*.py"))
    if not mods:
        raise RuntimeError("aucun module de planches trouvé à côté de mpl.py")
    for mod in mods:
        importlib.import_module(f"{pkg}.{mod}")


ROOT_PKG = "rapport"
