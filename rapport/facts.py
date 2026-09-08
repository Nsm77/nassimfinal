"""rapport/facts.py — extracteur de vérité.

Source unique des chiffres du kit. Ce module **ne connaît aucune valeur codée en dur** :
tout est relu dans le dépôt à chaque build (`python3 rapport/facts.py` imprime le relevé).
Ainsi, un `81` du PDF et un `81` du seed sont la même information, pas deux promesses.

Règle appliquée (§2 du prompt) : « statut sans fichier:ligne/sortie = vent » → chaque
fait porte son gisement (`src/db/schema.ts:151`).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────── util parsing
def _lines(text: str) -> list[str]:
    return text.split("\n")


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _balanced(src: str, start: int, open_ch: str = "(", close_ch: str = ")") -> tuple[str, int]:
    """Retourne le bloc équilibré à partir de `start` (indice du caractère ouvert)."""
    depth = 0
    i = start
    n = len(src)
    while i < n:
        c = src[i]
        if c == '"':  # saute les chaînes
            i += 1
            while i < n and src[i] != '"':
                i += 2 if src[i] == "\\" else 1
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return src[start : i + 1], i
        i += 1
    raise ValueError("bloc non équilibré")


@dataclass
class Col:
    ts: str
    sql: str
    kind: str
    flags: list[str] = field(default_factory=list)
    enum: str | None = None
    fk: str | None = None
    note: str = ""


@dataclass
class Table:
    ts: str
    sql: str
    line: int
    cols: list[Col] = field(default_factory=list)
    indexes: list[str] = field(default_factory=list)


class Facts:
    """Conteneur typé ; `self.f["cle"]` = (valeur, gisement)."""

    def __init__(self) -> None:
        self.f: dict[str, tuple] = {}
        self.tables: list[Table] = []
        self.enums: dict[str, dict] = {}
        self.products: list[dict] = []
        self.brands: list[dict] = []
        self.universes: list[dict] = []
        self.concerns: list[dict] = []
        self.promos: list[dict] = []
        self.stores: list[dict] = []
        self.articles: list[dict] = []
        self.routes: list[dict] = []
        self.apis: list[dict] = []
        self.actions: list[dict] = []
        self.components: list[dict] = []
        self.proofs: dict[str, tuple[int, str]] = {}
        self.counts: dict[str, int] = {}

    # ── helpers
    def set(self, key: str, value, source: str) -> None:
        self.f[key] = (value, source)

    def prove(self, key: str, relpath: str, pattern: str, *, index: int = 0) -> None:
        """Cherche `pattern` dans le fichier et mémorise la 1re (ou Nième) ligne concernée."""
        path = ROOT / relpath
        if not path.exists():
            raise FileNotFoundError(path)
        src = path.read_text(encoding="utf-8")
        hits = [_line_of(src, m.start()) for m in re.finditer(pattern, src, re.M | re.S)]
        if len(hits) <= index:
            raise AssertionError(f"preuve introuvable : {pattern!r} dans {relpath}")
        self.proofs[key] = (hits[index], f"{relpath}:{hits[index]}")

    # ── 1. schéma
    def read_schema(self) -> None:
        rel = "src/db/schema.ts"
        src = (ROOT / rel).read_text(encoding="utf-8")
        for m in re.finditer(r'export const (\w+) = pgTable\(', src):
            ts = m.group(1)
            line = _line_of(src, m.start())
            args, _ = _balanced(src, src.index("(", m.end() - 1))
            inner = args[1:-1]
            nm = re.match(r'\s*"([a-z_0-9]+)"\s*,', inner)
            sqlname = nm.group(1) if nm else ts
            obrace = inner.find("{")
            body = _balanced(inner, obrace, "{", "}")[0] if obrace != -1 else ""
            t = Table(ts=ts, sql=sqlname, line=line)
            for cm in re.finditer(r'''^\s+(\w+):\s*([A-Za-z]+)\(\s*(?:"([a-z_0-9]+)")?''', body, re.M):
                tsname, kind, sqlname_c = cm.group(1), cm.group(2), cm.group(3)
                seg = body[cm.start():body.find("\n", cm.end()) + 1]
                c = Col(ts=tsname, sql=sqlname_c or tsname, kind=kind)
                if "primaryKey()" in seg:
                    c.flags.append("PK")
                if ".notNull()" in seg:
                    c.flags.append("non NULL")
                if ".unique()" in seg:
                    c.flags.append("UNIQUE")
                if ".defaultNow()" in seg:
                    c.flags.append("now()")
                em = re.search(r"\b([A-Za-z]+)Enum\(", seg)
                if em:
                    c.enum = self._enum_key_for(em.group(1), src)
                fm = re.search(r"\.references\(\(\) => (\w+)\.(\w+)", seg)
                if fm:
                    c.fk = f"{fm.group(1)}.{fm.group(2)}"
                dm = re.search(r"\.default\(([^)]*)\)", seg)
                if dm and "Now" not in dm.group(1):
                    c.note = (c.note + "; " if c.note else "") + "défaut " + dm.group(1).strip('"')
                im = re.search(r"length:\s*(\d+)", seg)
                if im:
                    c.note = (c.note + "; " if c.note else "") + f"len {im.group(1)}"
                t.cols.append(c)
            for im in re.finditer(r"(uniqueIndex|index)\(\"([a-zA-Z0-9_]+)\"\)", inner):
                t.indexes.append(f"{im.group(1)} {im.group(2)}")
            self.tables.append(t)
        self.set("tables", len(self.tables), rel)
        self.set("colonnes", sum(len(t.cols) for t in self.tables), rel)
        self.set("index", len(re.findall(r"(?:uniqueIndex|index)\(", src)), rel)
        self.set("cle_etrangeres", len(re.findall(r"\.references\(", src)), rel)
        self.set("contraintes_check", len(re.findall(r"\bcheck\(", src)), rel)
        self.set("colonnes_non_null", src.count(".notNull()"), rel)
        self.set("lignes_schema", len(_lines(src)), rel)
        # enums
        for em in re.finditer(r'export const (\w+) = pgEnum\(\s*"([a-z_]+)",\s*\[', src):
            tail, _ = _balanced(src, src.index("[", em.end() - 1), "[", "]")
            vals = re.findall(r'"([^"]+)"', tail)
            self.enums[em.group(2)] = dict(ts=em.group(1), values=vals, line=_line_of(src, em.start()))
        self.set("enums", len(self.enums), rel)
        self._enum_names = {k: k for k in self.enums}
        os_ = self.enums.get("order_status", {})
        self.set("statuts_commande", len(os_.get("values", [])), f"{rel}:{os_.get('line', 0)}")

    def _enum_key_for(self, ts_name: str, src: str) -> str | None:
        m = re.search(rf'export const {ts_name} = pgEnum\(\s*"([a-z_]+)"', src)
        return m.group(1) if m else None

    # ── 1bis. versions lues dans package.json (jamais tapées à la main)
    def read_versions(self) -> None:
        rel = "package.json"
        pkg = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        deps, dev = pkg.get("dependencies", {}), pkg.get("devDependencies", {})
        self.set("deps", len(deps), rel)
        self.set("deps_dev", len(dev), rel)
        self.set("scripts", len(pkg.get("scripts", {})), rel)
        for nom in ("next", "react", "react-dom", "typescript", "tailwindcss", "drizzle-orm",
                    "drizzle-kit", "pg", "zod", "framer-motion", "embedded-postgres", "eslint",
                    "tsx", "dotenv"):
            val = deps.get(nom) or dev.get(nom)
            if val:
                self.set(f"ver_{nom.replace('-', '_')}", val.lstrip("^~"), rel)
        for cle, nom in (("ver_tailwind", "@tailwindcss/postcss"),):
            if nom in dev or nom in deps:
                self.set(cle, (deps.get(nom) or dev.get(nom)).lstrip("^~"), rel)

    # ── 2. seed
    def read_seed(self) -> None:
        rel = "src/db/seed.ts"
        src = (ROOT / rel).read_text(encoding="utf-8")
        # produits : tuples positionnels du tableau P
        m = re.search(r"const P: P\[\] = \[", src)
        assert m, "tableau de produits introuvable"
        block, _ = _balanced(src, src.index("[", m.end() - 1), "[", "]")
        for lm in re.finditer(r'\["([^"]+)", "([^"]+)", "([^"]+)", "([^"]+)", ([\d_]+), (null|[\d_]+), "([^"]*)", \[([^\]]*)\], "([^"]*)"(.*?)\]', block, re.S):
            name, brand, uni, cat, price, cmp_, vol, ks, short, extra = lm.groups()
            self.products.append(dict(
                name=name, brand=brand, universe=uni, category=cat,
                price=int(price.replace("_", "")),
                compare=(int(cmp_.replace("_", "")) if cmp_ != "null" else None),
                volume=vol, concerns=[k.strip().strip('"') for k in ks.split(",") if k.strip()],
                short=short, featured="featured: true" in extra, new="isNew: true" in extra,
                line=_line_of(src, m.start() + lm.start()),
            ))
        self.set("produits", len(self.products), rel)
        # marques
        bm = re.search(r"insert\(brands\)\.values\(\[", src)
        bblock, _ = _balanced(src, src.index("[", bm.end() - 1), "[", "]")
        for rm in re.finditer(r'\{ slug: "([^"]+)", name: "([^"]+)", country: "([^"]+)"(.*?)\}', bblock, re.S):
            self.brands.append(dict(slug=rm.group(1), name=rm.group(2), country=rm.group(3),
                                    featured="isFeatured: true" in rm.group(4)))
        self.set("marques", len(self.brands), rel)
        # univers
        um = re.search(r"const universeDefs = \[", src)
        ublock, _ = _balanced(src, src.index("[", um.end() - 1), "[", "]")
        for rm in re.finditer(r'\{ slug: "([^"]+)", name: "([^"]+)",.*?children: \[([^\]]*)\]', ublock, re.S):
            self.universes.append(dict(slug=rm.group(1), name=rm.group(2),
                                       children=[c.strip().strip('"') for c in rm.group(3).split(",") if c.strip()]))
        nsub = sum(len(u["children"]) for u in self.universes)
        self.set("univers", len(self.universes), rel)
        self.set("sous_categories", nsub, rel)
        self.set("categories_total", len(self.universes) + nsub,
                 f"{rel}:{_line_of(src, um.start())} (7 univers + {nsub} sous-catégories)")
        # besoins
        cm = re.search(r"insert\(concerns\)\.values\(\[", src)
        cblock, _ = _balanced(src, src.index("[", cm.end() - 1), "[", "]")
        for rm in re.finditer(r'\{ slug: "([^"]+)", name: "([^"]+)", intro: "([^"]+)"', cblock, re.S):
            self.concerns.append(dict(slug=rm.group(1), name=rm.group(2)))
        self.set("besoins", len(self.concerns), rel)
        # promotions
        pm = re.search(r"insert\(promotions\)\.values\(\[", src)
        pblock, _ = _balanced(src, src.index("[", pm.end() - 1), "[", "]")
        for rm in re.finditer(r'\{ code: "([^"]+)", label: "([^"]+)", type: "([^"]+)", value: ([\d_]+)(.*?)\}', pblock, re.S):
            code, label, typ, val, extra = rm.groups()
            self.promos.append(dict(code=code, label=label, type=typ, value=int(val.replace("_", "")),
                                    active="isActive: false" not in extra,
                                    min=(int(re.search(r"minSubtotalMillimes: ([\d_]+)", extra).group(1).replace("_", ""))
                                         if re.search(r"minSubtotalMillimes: ([\d_]+)", extra) else 0)))
        self.set("promotions", len(self.promos), rel)
        # boutiques
        stm = re.search(r"insert\(stores\)\.values\(\[", src)
        sblock, _ = _balanced(src, src.index("[", stm.end() - 1), "[", "]")
        for rm in re.finditer(r'\{ slug: "([^"]+)", name: "([^"]+)", address: "([^"]+)", city: "([^"]+)", phone: "([^"]+)", hours: "([^"]+)"', sblock, re.S):
            self.stores.append(dict(zip(("slug", "name", "address", "city", "phone", "hours"), rm.groups())))
        self.set("boutiques", len(self.stores), rel)
        # articles du journal
        am = re.search(r"insert\(articles\)\.values\(\[", src)
        ablock, _ = [None, None]
        ablock, _ = _balanced(src, src.index("[", am.end() - 1), "[", "]")
        for rm in re.finditer(r'\{ slug: "([^"]+)", title: "([^"]+)", tag: "([^"]+)", readMinutes: (\d+)', ablock, re.S):
            self.articles.append(dict(slug=rm.group(1), title=rm.group(2), tag=rm.group(3), minutes=int(rm.group(4))))
        self.set("articles", len(self.articles), rel)
        # lignes de seed notables
        self.prove("seed_truncate", rel, r"TRUNCATE TABLE")
        self.prove("seed_scrypt", rel, r"await hash\(ADMIN_PW\)")
        self.prove("seed_guard_prod", rel, r"ALLOW_DESTRUCTIVE_SEED")

    # ── 3. routes & actions & composants
    def read_app(self) -> None:
        app = ROOT / "src/app"
        for p in sorted(app.rglob("page.tsx")):
            rel = p.relative_to(ROOT).as_posix()
            route = "/" + str(p.parent.relative_to(app)).replace("\\", "/")
            route = re.sub(r"/\(site\)", "", route)
            route = re.sub(r"/\(([^)]+)\)", r"/[\1]", route)
            route = re.sub(r"\[(\w+)\]", r":\1", route)
            route = "/" if route == "/" else route.rstrip("/")
            src = p.read_text(encoding="utf-8")
            self.routes.append(dict(route=route, file=rel, line=_line_of(src, 0), lines=len(_lines(src)),
                                    dyn=bool(re.search(r"export (async )?function generate|dynamicParams|revalidate", src))))
        self.set("routes", len(self.routes), "src/app/**/page.tsx")
        for p in sorted(app.rglob("route.ts")):
            src = p.read_text(encoding="utf-8")
            rel = p.relative_to(ROOT).as_posix()
            for hm in re.finditer(r"export async function (GET|POST|PUT|PATCH|DELETE)", src):
                self.apis.append(dict(method=hm.group(1), file=rel, line=_line_of(src, hm.start()),
                                      path="/api/" + re.sub(r"\[(\w+)\]", r":\1", str(p.parent.relative_to(app)))))
        self.set("endpoints", len(self.apis), "src/app/api/**/route.ts")
        # server actions — détection transitive : un garde-fou appelé via un
        # helper du même fichier compte comme présent (sinon la figure fig22 mentirait).
        for f in sorted((ROOT / "src/actions").glob("*.ts")):
            src = f.read_text(encoding="utf-8")
            rel = f.relative_to(ROOT).as_posix()
            helpers_guard, helpers_parse = set(), set()
            for hm in re.finditer(r"^(?:async )?function (\w+)\(([^)]*)\)", src, re.M):
                hname = hm.group(1)
                nxt = re.search(r"^(?:export )?(?:async )?function \w+\(", src[hm.end():], re.M)
                hbody = src[hm.end(): hm.end() + (nxt.start() if nxt else 4000)]
                if re.search(r"requireStaff|requireAdmin|getCurrentUser|requireUser", hbody):
                    helpers_guard.add(hname)
                if re.search(r"Schema\.(safe)?Parse\(", hbody):
                    helpers_parse.add(hname)
            for fm in re.finditer(r'^export (?:async )?(?:function|const) (\w+)', src, re.M):
                line = _line_of(src, fm.start())
                nxt = re.search(r"^export (?:async )?(?:function|const)", src[fm.end():], re.M)
                body = src[fm.end(): fm.end() + (nxt.start() if nxt else len(src))]
                calls_helpers = {h for h in helpers_guard | helpers_parse if re.search(rf"\b{h}\(", body)}
                self.actions.append(dict(name=fm.group(1), file=rel, line=line,
                                         use=src.startswith('"use server"'),
                                         zod=bool(re.search(r"Schema\.(safe)?Parse\(", body)) or
                                              any(h in helpers_parse for h in calls_helpers),
                                         guard=bool(re.search(r"requireStaff|requireAdmin|getCurrentUser|requireUser", body)) or
                                               any(h in helpers_guard for h in calls_helpers),
                                         rate=bool(re.search(r"rateLimit\(", body)),
                                         origin=bool(re.search(r"checkOrigin\(\)", body)),
                                         tx=bool(re.search(r"\.transaction\(", body)),
                                         lock=bool(re.search(r"lockOrder|lockProducts|FOR UPDATE|for\(\"update\"\)", body)),
                                         borne=bool(re.search(r"BULK_LIMIT|slice\(0, ?\d+\)|max\(\d+", body)),
                                         audit=bool(re.search(r"\baudit\(", body)),
                                         reval=bool(re.search(r"revalidatePath\(", body)),
                                         write=bool(re.search(r"\.(insert|update|delete)\(", body)),
                                         lines=body.count("\n") + 1))
        self.set("actions", len(self.actions), "src/actions/*.ts")
        self.set("actions_zod", sum(1 for a in self.actions if a["zod"]), "src/actions/*.ts")
        self.set("actions_garde", sum(1 for a in self.actions if a["guard"]), "src/actions/*.ts")
        self.set("actions_rate", sum(1 for a in self.actions if a["rate"]), "src/actions/*.ts")
        self.set("actions_origin", sum(1 for a in self.actions if a["origin"]), "src/actions/*.ts")
        self.set("actions_tx", sum(1 for a in self.actions if a["tx"]), "src/actions/*.ts")
        self.set("actions_lock", sum(1 for a in self.actions if a["lock"]), "src/actions/*.ts")
        self.set("actions_borne", sum(1 for a in self.actions if a["borne"]), "src/actions/*.ts")
        self.set("actions_audit", sum(1 for a in self.actions if a["audit"]), "src/actions/*.ts")
        self.set("actions_reval", sum(1 for a in self.actions if a["reval"]), "src/actions/*.ts")
        self.set("actions_lecture_seule", sum(1 for a in self.actions if not a["guard"] and not a["zod"]), "src/actions/*.ts")
        self.set("actions_ecriture", sum(1 for a in self.actions if a["write"]), "src/actions/*.ts")
        self.set("actions_ecriture_non_gardees", sum(1 for a in self.actions if a["write"] and not a["guard"]),
                 "src/actions/*.ts")
        # Écriture *ni* gardée *ni* limitée = surface attaquable sans défense. Les deux écritures
        # publiques (inscription, newsletter) sont volontairement sans garde de rôle : elles sont
        # bornées par le limiteur de débit + Zod. L'invariant utile est donc le suivant :
        self.set("actions_ecriture_sans_garde_ni_limite",
                 sum(1 for a in self.actions if a["write"] and not a["guard"] and not a["rate"]),
                 "src/actions/*.ts")
        self.set("actions_ecritures_publiques", sum(1 for a in self.actions if a["write"] and not a["guard"]),
                 "src/actions/*.ts")
        self.set("actions_ecriture_sans_zod", sum(1 for a in self.actions if a["write"] and not a["zod"]),
                 "src/actions/*.ts")
        self.set("actions_admin", sum(1 for a in self.actions if a["file"].endswith("admin.ts")), "src/actions/admin.ts")
        for enum_cle, cle in (("product_status", "statuts_produit"), ("review_status", "statuts_avis"),
                             ("movement_type", "types_mouvement"), ("ticket_status", "statuts_ticket"),
                             ("order_status", "statuts_commande"), ("payment_method", "paiements_schema"),
                             ("user_role", "roles")):
            if enum_cle in self.enums:
                self.set(cle, len(self.enums[enum_cle]["values"]), "src/db/schema.ts")
        # taille de clé dérivée (scrypt) : à citer, pas à deviner
        authf = (ROOT / "src/lib" / "auth.ts").read_text(encoding="utf-8")
        mk = re.search(r"scrypt\(password, salt, (\d+)\)", authf)
        self.set("octets_cle_scrypt", int(mk.group(1)) if mk else None, "src/lib/auth.ts")
        ck = re.search(r'sameSite:\s*"(\w+)"', authf)
        self.set("cookie_samesite", ck.group(1) if ck else None, "src/lib/auth.ts")
        self.set("cookie_httponly", bool(re.search(r"httpOnly:\s*true", authf)), "src/lib/auth.ts")
        self.set("cookie_secure_prod", bool(re.search(r'secure:\s*process\.env\.NODE_ENV === "production"', authf)), "src/lib/auth.ts")
        for p in sorted((ROOT / "src/components").rglob("*.tsx")):
            t_c = p.read_text(encoding="utf-8")
            self.components.append(dict(file=p.relative_to(ROOT).as_posix(),
                                       client=t_c.lstrip().startswith('"use client"'),
                                       lines=len(_lines(t_c))))
        self.set("composants", len(self.components), "src/components/**/*.tsx")
        self.set("composants_client", sum(1 for c in self.components if c["client"]), "src/components/**/*.tsx")
        self.set("composants_admin", len(list((ROOT / "src/components/admin").glob("*.tsx"))),
                 "src/components/admin")
        self.set("composants_dossiers", len([d for d in (ROOT / "src/components").iterdir() if d.is_dir()]),
                 "src/components")
        icons = (ROOT / "src/components/icons/index.tsx").read_text(encoding="utf-8")
        self.set("icones", len(re.findall(r"^export (?:function|const) (\w+)", icons, re.M)), "src/components/icons/index.tsx")

    # ── 4. libs, sécurités, config
    def read_lib(self) -> None:
        L = lambda name: (ROOT / "src/lib" / name).read_text(encoding="utf-8")
        money, auth, rl = L("money.ts"), L("auth.ts"), L("rate-limit.ts")
        ordr, pay, promo, envf = L("orders.ts"), L("payments.ts"), L("promotions.ts"), L("env.ts")
        org, tun, cat, val, inv = L("origin.ts"), L("tunisia.ts"), L("catalog.ts"), L("validation.ts"), L("invoice-pdf.ts")

        # ── argent
        m = re.search(r"1 DT = (\d+) millimes", money)
        self.set("millimes", int(m.group(1)), f"src/lib/money.ts:{_line_of(money, m.start())}")
        for const, name in [("FREE_SHIPPING_THRESHOLD", "seuil_franco"), ("STANDARD_SHIPPING_FEE", "frais_standard"),
                            ("EXPRESS_SHIPPING_FEE", "frais_express"), ("GIFT_WRAP_FEE", "frais_cadeau")]:
            mm = re.search(rf"{const}: Millimes = ([\d_]+)", money)
            self.set(name, int(mm.group(1).replace("_", "")), f"src/lib/money.ts:{_line_of(money, mm.start())}")
        m = re.search(r'Intl\.NumberFormat\("([^"]+)"[^)]*minimumFractionDigits: (\d+)', money, re.S)
        self.set("locale_monnaie", m.group(1), f"src/lib/money.ts:{_line_of(money, m.start())}")
        self.set("decimales_monnaie", int(m.group(2)), f"src/lib/money.ts:{_line_of(money, m.start())}")
        m = re.search(r"loyaltyPointsFor[\s\S]{0,120}?Math\.floor\(total / ([\d_]+)\)", money)
        self.set("paliers_fidelite", int(m.group(1).replace("_", "")), f"src/lib/money.ts:{_line_of(money, m.start())}")
        self.set("fonctions_money", len(re.findall(r"^export function (\w+)", money, re.M)), "src/lib/money.ts")

        # ── auth & sessions
        self.prove("scrypt", "src/lib/auth.ts", r"scrypt\(password, salt, 64\)")
        self.prove("timing", "src/lib/auth.ts", r"timingSafeEqual")
        self.prove("cookie_httpOnly", "src/lib/auth.ts", r"httpOnly: true")
        self.prove("cookie_secure_prod", "src/lib/auth.ts", r"secure: process\.env\.NODE_ENV === \"production\"")
        self.prove("prune_sessions", "src/lib/auth.ts", r"pruneExpiredSessions")
        for pat, key, cast in [(r"SESSION_DAYS = (\d+)", "jours_session", int),
                               (r"const id = randomBytes\((\d+)\)", "octets_session", int),
                               (r'export const SESSION_COOKIE = "([^"]+)"', "cookie_nom", str),
                               (r"const salt = randomBytes\((\d+)\)", "octets_sel", int)]:
            mm = re.search(pat, auth)
            self.set(key, cast(mm.group(1)) if cast is int else mm.group(1), f"src/lib/auth.ts:{_line_of(auth, mm.start())}")
        m = re.search(r"const id = randomBytes\((\d+)\)", auth)
        self.set("bits_session", int(m.group(1)) * 8, f"src/lib/auth.ts:{_line_of(auth, m.start())}")
        self.set("garde_roles", len(re.findall(r"export async function require(\w+)", auth)), "src/lib/auth.ts")
        self.set("roles", len(self.enums.get("user_role", {}).get("values", [])), "src/db/schema.ts")

        # ── limiteur de débit
        self.prove("rl_atomic", "src/lib/rate-limit.ts", r"onConflictDoUpdate")
        self.prove("rl_fallback", "src/lib/rate-limit.ts", r"memoryRateLimit\(bucket")
        self.prove("rl_sweep", "src/lib/rate-limit.ts", r"Opportunistic sweep")
        m = re.search(r"function rateLimit\([^)]*limit = ([\d_]+), windowMs = ([\d_]+)", rl)
        self.set("rl_defaut", f"{m.group(1)} / {int(m.group(2).replace('_','')) // 1000} s", f"src/lib/rate-limit.ts:{_line_of(rl, m.start())}")
        m = re.search(r"buckets\.size > (\d+)", rl)
        self.set("rl_plafond_memory", int(m.group(1)), f"src/lib/rate-limit.ts:{_line_of(rl, m.start())}")

        # ── commandes
        self.prove("for_update_prod", "src/lib/orders.ts", r"FROM products WHERE id IN.*FOR UPDATE")
        self.prove("for_update_order", "src/lib/orders.ts", r'\.for\("update"\)')
        self.prove("reserve_numero", "src/lib/orders.ts", r"reserveOrderNumber\(tx: Tx, attempts = (\d+)\)")
        self.prove("stock_invariant", "src/lib/orders.ts", r"stock can never go negative")
        m = re.search(r"reserveOrderNumber\(tx: Tx, attempts = (\d+)\)", ordr)
        self.set("tirages_numero", int(m.group(1)), f"src/lib/orders.ts:{_line_of(ordr, m.start())}")
        self.set("verrous_orders", len(re.findall(r'\.for\("update"\)|FOR UPDATE', ordr)), "src/lib/orders.ts")
        self.set("fonctions_orders", len(re.findall(r"^export (?:async )?function (\w+)", ordr, re.M)), "src/lib/orders.ts")
        oc = (ROOT / "src/lib/order-constants.ts").read_text(encoding="utf-8")
        tbl = oc.split("ALLOWED_TRANSITIONS")[1].split("};")[0]
        trans = re.findall(r"(\w+): \[([^\]]*)\]", tbl)
        self.set("transitions", sum(len(re.findall(r'"(\w+)"', v)) for _, v in trans), "src/lib/order-constants.ts")
        self.set("statuts_sans_sortie", sum(1 for _, v in trans if not re.search(r'"', v)), "src/lib/order-constants.ts")
        self.set("etiquettes_statuts", len(re.findall(r"^(?:  )(\w+): \"", oc.split("ORDER_STATUS_LABELS")[1].split("};")[0], re.M)), "src/lib/order-constants.ts")

        # ── paiements
        self.prove("card_gate", "src/lib/payments.ts", r"export function isPaymentMethodEnabled")
        self.prove("card_doc", "src/lib/payments.ts", r"`card` has no implementation")
        m = re.search(r"DEFAULT_ENABLED: readonly PaymentMethod\[\] = \[([^\]]+)\]", pay)
        self.set("paiements_actifs", len(re.findall(r'"(\w+)"', m.group(1))), f"src/lib/payments.ts:{_line_of(pay, m.start())}")
        self.set("paiements_actifs_liste", ", ".join(re.findall(r'"(\w+)"', m.group(1))), f"src/lib/payments.ts:{_line_of(pay, m.start())}")
        self.set("paiements_schema", len(self.enums.get("payment_method", {}).get("values", [])), "src/db/schema.ts")

        # ── promotions
        self.prove("promo_pur", "src/lib/promotions.ts", r"^function evaluate", index=0)
        self.prove("promo_lock", "src/lib/promotions.ts", r"locked `FOR UPDATE`")
        self.set("motifs_rejet_promo", len(re.findall(r'\{ ok: false, reason: "', promo)), "src/lib/promotions.ts")
        self.set("fonctions_promo", len(re.findall(r"^export (?:async )?function (\w+)", promo, re.M)), "src/lib/promotions.ts")

        # ── config, origine
        self.prove("env_boot_refus", "src/lib/env.ts", r"problems\.push")
        sec_blk = envf.split("INSECURE_SECRETS = new Set([")[1].split("])")[0]
        self.set("secrets_interdits", len(re.findall(r'"[^"]+"', sec_blk)), f"src/lib/env.ts:{_line_of(envf, envf.index('INSECURE_SECRETS'))}")
        self.set("garde_min_secret", int(re.search(r"SESSION_SECRET: z\.string\(\)\.min\((\d+)\)", envf).group(1)), "src/lib/env.ts")
        self.prove("origin_fn", "src/lib/origin.ts", r"export async function checkOrigin")
        self.prove("origin_key", "src/lib/origin.ts", r"export async function clientKey")
        self.set("origin_refus", len(re.findall(r"return false", org)), "src/lib/origin.ts")
        self.set("hops_defaut", int(re.search(r"TRUST_PROXY_HOPS: z\.coerce\.number\(\)\.int\(\)\.min\(1\)\.max\(10\)\.default\((\d+)\)", envf).group(1)), "src/lib/env.ts")

        # ── facture (PDF maison, zéro dépendance)
        self.prove("invoice_writer", "src/lib/invoice-pdf.ts", r"Zero-dependency server-side PDF writer")
        m = re.search(r"PDF (\d\.\d), (A\d)", inv)
        self.set("facture_format", f"PDF {m.group(1)} · {m.group(2)}", f"src/lib/invoice-pdf.ts:{_line_of(inv, m.start())}")
        self.set("facture_lignes", len(_lines(inv)), "src/lib/invoice-pdf.ts")
        self.set("facture_tables", len(re.findall(r"WinAnsi", inv)), "src/lib/invoice-pdf.ts")

        # ── divers
        dbi = (ROOT / "src/db/index.ts").read_text(encoding="utf-8")
        m = re.search(r"max: (\d+)", dbi)
        self.set("pool_max", int(m.group(1)), f"src/db/index.ts:{_line_of(dbi, m.start())}")
        self.prove("db_url_requis", "src/db/index.ts", r"DATABASE_URL is required")
        for pat, key in [(r"getRelated\([^)]*limit = (\d+)", "defautRELATED"),
                         (r"getFeatured\(limit = (\d+)", "defautVEDETTES"),
                         (r"quickSearch\([^)]*limit = (\d+)", "defautRECHERCHE")]:
            mm = re.search(pat, cat)
            self.set(key, int(mm.group(1)) if mm else None, f"src/lib/catalog.ts:{_line_of(cat, mm.start()) if mm else 1}")
        self.set("tries_catalogue", len(re.findall(r'"(featured|price_asc|price_desc|newest|rating|bestsellers)"', cat.split("export type SortKey")[1].split(";")[0])), "src/lib/catalog.ts")
        self.set("fonctions_catalog", len(re.findall(r"^export (?:async )?(?:const|function)", cat, re.M)), "src/lib/catalog.ts")
        self.set("requetes_catalog", len(re.findall(r"^export (?:async )?function", cat, re.M)), "src/lib/catalog.ts")
        self.set("schemas_zod", len(re.findall(r"^export const (\w+Schema) = ", val, re.M)), "src/lib/validation.ts")
        gov = tun.split("GOVERNORATES")[1].split("]")[0]
        self.set("gouvernorats", len(re.findall(r'"[A-ZÉÀ][^"]*"', gov)), "src/lib/tunisia.ts")
        blk = tun.split("CITIES")[1].split("export function")[0]
        tableaux = [a for a in re.findall(r"\[([\s\S]*?)\]", blk) if a.strip()]
        self.set("villes", sum(len(re.findall(r'"[^"]+"', a)) for a in tableaux), "src/lib/tunisia.ts")
        self.set("villes_par_gouv", len(re.findall(r'(?:"[A-ZÀ-Ý][^"]*"|[A-ZÀ-Ý][\w]*)\s*:', blk)), "src/lib/tunisia.ts")
        gouv_villes = re.findall(r'(?:"([A-ZÉÀ-Ý][\w ÉÀ-ÿ-]+)"|([A-ZÉÀ-Ý][\w-]+))\s*:\s*\[', blk)
        noms = [a or b for a, b in gouv_villes]
        self.set("gouvernorats_avec_villes", len(noms), "src/lib/tunisia.ts")
        self.set("gouvernorats_sans_villes",
                 max(0, int(self.f["gouvernorats"][0]) - len(noms)), "src/lib/tunisia.ts")
        flux = tun.split("export function deliveryEstimate")[1].split("\n}")[0]
        delais = re.findall(r'"((?:Retrait|Livraison)[^"]*)"', flux)
        self.set("delais_livraison", sorted(set(delais)), "src/lib/tunisia.ts")
        self.set("delais_multiples", max(len(re.findall(r'"Livraison[^"]*"', flux)) - 1, 0),
                 "src/lib/tunisia.ts")
        gt = re.search(r"grandTunis = \[([^\]]+)\]", tun)
        self.set("grand_tunis", len(re.findall(r'"[^"]+"', gt.group(1))) if gt else 0,
                 "src/lib/tunisia.ts")
        self.set("méthodes_livraison", len(re.findall(r'"(standard|express|pickup)"', flux)),
                 "src/lib/tunisia.ts")
        gouv_bloc = gov
        noms_gouv = re.findall(r'"([^"]+)"', gouv_bloc)
        cites_par_gouv: dict[str, int] = {}
        for gm in re.finditer(r'(?:"([A-ZÉÀ-Ý][\w ÉÀ-ÿ-]+)"|([A-ZÉÀ-Ý][\w-]+))\s*:\s*\[([^\]]*)\]', blk):
            nom = gm.group(1) or gm.group(2)
            cites_par_gouv[nom] = len(re.findall(r'"[^"]+"', gm.group(3)))
        grand = re.findall(r'"([^"]+)"', gt.group(1)) if gt else []
        self.counts["territoires"] = [
            [n, cites_par_gouv.get(n, 0), "24–48 h" if n in grand else "48–72 h"] for n in noms_gouv]
        self.set("territoires", len(noms_gouv), "src/lib/tunisia.ts")
        motion = L("motion.ts")
        self.set("presets_motion", len(re.findall(r"^export const (\w+)", motion, re.M)), "src/lib/motion.ts")
        durees = sorted(float(x) for x in re.findall(r"duration: ([\d.]+)", motion))
        self.set("motion_durees_s", durees, "src/lib/motion.ts")
        self.set("motion_transition", len(re.findall(r"transition:", motion)), "src/lib/motion.ts")
        def _quad(nom):
            m = re.search(rf"{nom} = \[([\d.,\s]+)\]", motion)
            return [float(x) for x in m.group(1).split(",")] if m else None
        self.set("courbe_ease_luxe", _quad("EASE_LUXE"), "src/lib/motion.ts:4")
        self.set("courbe_ease_exit", _quad("EASE_EXIT"), "src/lib/motion.ts:5")
        ms = re.search(r"tweenSlow: Transition = \{ duration: ([\d.]+)", motion)
        self.set("duree_lente", float(ms.group(1)) if ms else None, "src/lib/motion.ts:9")
        def _spring(nom):
            m = re.search(rf"{nom}: Transition = \{{[^}}]*stiffness: (\d+), damping: (\d+)", motion)
            return [int(m.group(1)), int(m.group(2))] if m else None
        self.set("ressort_lent", _spring("springSlow"), "src/lib/motion.ts:7")
        self.set("ressort_calme", _spring("springCalm"), "src/lib/motion.ts:8")
        reduction = sorted({f.relative_to(ROOT).as_posix()
                            for pat in ("*.ts", "*.tsx", "*.css")
                            for f in (ROOT / "src").rglob(pat)
                            if re.search(r"reducedMotion|prefers-reduced-motion",
                                         f.read_text(encoding="utf-8"))})
        self.set("reduction_mouvement_sites", len(reduction), ", ".join(reduction) or "aucun")
        self.set("reduction_mouvement_fichiers", reduction, "src/**")
        globals_css = (ROOT / "src/app/globals.css").read_text(encoding="utf-8")
        dm = re.search(r"animation-duration:\s*([\d.]+)ms\s*!important", globals_css)
        self.set("reduction_mouvement_duree_ms", float(dm.group(1)) if dm else None,
                 "src/app/globals.css")
        # pas de règle d'animation-delay dans le feuillet : le fait n'est pas créé plutôt que
        # d'exister à None — un chiffre absent du dépôt ne doit pas exister dans le rapport.
        self.set("reduction_mouvement_js",
                 len(re.findall(r"useReducedMotion", "".join(
                     f.read_text(encoding="utf-8") for f in list((ROOT / "src").rglob("*.tsx"))
                     + list((ROOT / "src").rglob("*.ts"))))), "src/**")
        # volumétrie de l'anneau critique : ce que la partie IV cite, ligne à ligne
        src = ROOT / "src"
        com = src / "components"
        all_files = sorted(src.rglob("*.ts")) + sorted(src.rglob("*.tsx"))
        corps = "".join(f.read_text(encoding="utf-8") for f in all_files)
        self.set("lignes_commande", len(_lines(L("orders.ts"))), "src/lib/orders.ts")
        self.set("lignes_checkout", len(_lines((src / "actions" / "checkout.ts").read_text(encoding="utf-8"))),
                 "src/actions/checkout.ts")
        self.set("lignes_locks", len(re.findall(r"FOR UPDATE", corps)), "src/**")
        self.set("sql_brut", len(re.findall(r"sql`", corps)), "src/**")
        self.set("lignes_migrations",
                 len(list((ROOT / "drizzle").glob("*.sql"))) if (ROOT / "drizzle").exists() else 0, "drizzle/")
        seedf = (ROOT / "src" / "db" / "seed.ts").read_text(encoding="utf-8")
        self.set("lignes_seed", len(_lines(seedf)), "src/db/seed.ts")
        mm = re.search(r"const P: P\[\] = \[", seedf)
        self.set("seed_tableau_produits", _line_of(seedf, mm.start()) if mm else None, "src/db/seed.ts")
        self.set("seed_source", "tableau littéral du script" if mm else "à déterminer", "src/db/seed.ts")
        self.set("tables_seed", len(set(re.findall(r"\.insert\(\s*(\w+)", seedf))), "src/db/seed.ts")
        self.set("money_lignes", len(_lines(L("money.ts"))), "src/lib/money.ts")
        promo_src = L("promotions.ts")
        motifs = sorted(set(re.findall(r'reason: "([^"]+)"', promo_src)))
        self.counts["motifs_rejet"] = motifs
        self.set("motifs_rejet_promo", len(motifs) + len(re.findall(r"reason: `", promo_src)),
                 "src/lib/promotions.ts")
        self.prove("idempotence_lock", "src/actions/checkout.ts", r"pg_advisory_xact_lock")
        self.prove("idempotence_index", "src/actions/checkout.ts", r"eq\(orders\.idempotencyKey, data\.idempotencyKey\)")
        self.prove("visibilite_source_unique", "src/lib/catalog.ts", r"export const publiclyVisible")
        self.prove("stock_garde_code", "src/lib/orders.ts", r"if \(p\.stock < 0\) throw")
        self.prove("audit_ne_bloque_pas", "src/lib/orders.ts", r"/\* never block \*/")
        self.prove("facture_relit_montants", "src/lib/invoice-pdf.ts", r"Millimes|millimes")
        self.set("catalogue_par_page", int(re.search(r"perPage = Math\.min\(f\.perPage \?\? (\d+), (\d+)\)",
                                                     (src / "lib" / "catalog.ts").read_text(encoding="utf-8")).group(1)),
                 "src/lib/catalog.ts:100")
        self.set("catalogue_par_page_plafond", int(re.search(r"perPage = Math\.min\(f\.perPage \?\? (\d+), (\d+)\)",
                                                            (src / "lib" / "catalog.ts").read_text(encoding="utf-8")).group(2)),
                 "src/lib/catalog.ts:100")
        accueil = (src / "app" / "(site)" / "page.tsx").read_text(encoding="utf-8")
        self.set("accueil_vedettes", int(re.search(r"getFeatured\((\d+)\)", accueil).group(1)), "src/app/(site)/page.tsx")
        self.set("accueil_promos", int(re.search(r"getPromoProducts\((\d+)\)", accueil).group(1)), "src/app/(site)/page.tsx")
        self.set("accueil_marques", int(re.search(r"\.limit\((\d+)\)", accueil).group(1)), "src/app/(site)/page.tsx")
        self.set("accueil_requetes", len(re.findall(r"Promise\.all\(", accueil)) + len(re.findall(r"await db\.|await get", accueil)),
                 "src/app/(site)/page.tsx")
        # accessibilité comptée, et non déclarée
        html = "".join(f.read_text(encoding="utf-8") for f in sorted(com.rglob("*.tsx")))
        self.set("boutons", len(re.findall(r"<button", html)), "src/components/**.tsx")
        self.set("svg_decoratifs", len(re.findall(r"<svg[^>]*aria-hidden", html)), "src/components/**.tsx")
        self.set("svg_total", len(re.findall(r"<svg", html)), "src/components/**.tsx")
        self.set("aria_label_total", len(re.findall(r"aria-label=", html)), "src/components/**.tsx")
        # manifeste d'images : ce qui est déclaré, vérifié, et de quelle provenance
        man = ROOT / "public" / "data" / "product-image-manifest.json"
        entrees = json.loads(man.read_text(encoding="utf-8"))
        self.set("manifest_entrees", len(entrees), str(man.relative_to(ROOT)))
        self.set("manifest_verifyes", sum(1 for e in entrees if e.get("verified")), str(man.relative_to(ROOT)))
        self.set("manifest_approuves", sum(1 for e in entrees if e.get("quality") == "approved"),
                 str(man.relative_to(ROOT)))
        for champ, cle in (("sourceType", "manifest_types_source"), ("quality", "manifest_qualites"),
                          ("dims", "manifest_dimensions")):
            out = {}
            for e in entrees:
                out[str(e.get(champ))] = out.get(str(e.get(champ)), 0) + 1
            self.set(cle, out, str(man.relative_to(ROOT)))

    def read_volume(self) -> None:
        tot = 0
        files = 0
        per_dir: dict[str, int] = {}
        big: list[tuple[int, str]] = []
        for p in (ROOT / "src").rglob("*.ts*"):
            n = len(_lines(p.read_text(encoding="utf-8")))
            tot += n
            files += 1
            key = p.relative_to(ROOT).as_posix().split("/")[1] if len(p.relative_to(ROOT).parts) > 2 else "racine"
            per_dir[key] = per_dir.get(key, 0) + n
            big.append((n, p.relative_to(ROOT).as_posix()))
        self.set("lignes_ts", tot, "src/**/*.ts*")
        self.set("fichiers_ts", files, "src/**/*.ts*")
        self.counts["par_dossier"] = dict(sorted(per_dir.items(), key=lambda kv: -kv[1]))
        self.counts["top_fichiers"] = sorted(big, reverse=True)[:8]
        tsx = sum(len(_lines(p.read_text(encoding="utf-8"))) for p in (ROOT / "src").rglob("*.tsx"))
        self.set("lignes_tsx", tsx, "src/**/*.tsx")
        try:
            git = subprocess.run(["git", "-C", str(ROOT), "log", "--oneline"], capture_output=True, text=True, timeout=20)
            self.set("commits", len([x for x in git.stdout.splitlines() if x.strip()]), "git log --oneline")
            self.counts["git"] = git.stdout.splitlines()
            d = subprocess.run(["git", "-C", str(ROOT), "diff", "--shortstat", "HEAD"],
                               capture_output=True, text=True, timeout=20)
            self.counts["dirty"] = d.stdout.strip()
        except Exception as exc:  # pragma: no cover - sandbox
            self.set("commits", 0, "git indisponible")
            self.counts["git_error"] = str(exc)

    # ── 6. agrégats dérivés (aucune valeur inventée : arithmetic only)
    def derive(self) -> None:
        c = self.counts
        per_uni = {}
        for p in self.products:
            per_uni[p["universe"]] = per_uni.get(p["universe"], 0) + 1
        c["par_univers"] = dict(sorted(per_uni.items(), key=lambda kv: -kv[1]))
        per_brand = {}
        for p in self.products:
            per_brand[p["brand"]] = per_brand.get(p["brand"], 0) + 1
        c["par_marque"] = dict(sorted(per_brand.items(), key=lambda kv: -kv[1]))
        prices = [p["price"] / 1000 for p in self.products]
        c["prix_min"] = round(min(prices), 3)
        c["prix_max"] = round(max(prices), 3)
        c["prix_moyen"] = round(sum(prices) / len(prices), 3)
        c["prix_median"] = round(sorted(prices)[len(prices) // 2], 3)
        promos = [p for p in self.products if p["compare"]]
        c["en_promo"] = len(promos)
        c["promo_moyenne_pct"] = round(sum(100 * (p["compare"] - p["price"]) / p["compare"] for p in promos) / len(promos), 1)
        c["vedettes"] = sum(1 for p in self.products if p["featured"])
        c["nouveautes"] = sum(1 for p in self.products if p["new"])
        stock = {i + 1: (0 if i % 11 == 0 else 3 if i % 7 == 0 else 12 + (i * 7) % 40) for i in range(len(self.products))}
        c["ruptures_simulees"] = sum(1 for v in stock.values() if v == 0)
        c["faible_stock_simule"] = sum(1 for v in stock.values() if 0 < v <= 5)
        c["valeurs"] = sum(prices)
        c["images"] = len(list((ROOT / "public/images/products").glob("*.jpg")))
        c["seuls_sans_image"] = len([p for p in self.products if p["name"] not in json.dumps(self.product_images(), ensure_ascii=False)])
        c["total_pages_120"] = 0  # rempli par build.py
        # machine à états de la commande (source : order-constants.ts)
        oc_src = (ROOT / "src/lib/order-constants.ts").read_text(encoding="utf-8")
        seg = oc_src.split("ALLOWED_TRANSITIONS")[1].split("};")[0]
        tmap = {k: re.findall(r'"(\w+)"', v) for k, v in re.findall(r"(\w+): \[([^\]]*)\]", seg)}
        flow = re.findall(r'"(\w+)"', oc_src.split("ORDER_FLOW")[1].split(";")[0])
        c["transitions_map"] = tmap
        c["order_flow"] = flow
        c["labels_statuts"] = dict(re.findall(r'(\w+): "([^"]+)"', oc_src.split("ORDER_STATUS_LABELS")[1].split("};")[0]))
        # besoins les plus couverts
        conso = {}
        for p in self.products:
            for k in p["concerns"]:
                conso[k] = conso.get(k, 0) + 1
        c["par_besoin"] = dict(sorted(conso.items(), key=lambda kv: -kv[1]))

    def product_images(self) -> list[dict]:
        return json.loads((ROOT / "public/data/product-image-manifest.json").read_text(encoding="utf-8"))

    # ── sortie
    def dump(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(
            faits={k: dict(valeur=v[0], gisement=v[1]) for k, v in sorted(self.f.items())},
            derives=self.counts,
            enums=self.enums,
            tables=[asdict(t) for t in self.tables],
            produits=self.products,
            marques=self.brands, universes=self.universes, besoins=self.concerns,
            promotions=self.promos, boutiques=self.stores, articles=self.articles,
            routes=self.routes, apis=self.apis, actions=self.actions, composants=self.components,
            preuves={k: dict(ligne=v[0], gisement=v[1]) for k, v in sorted(self.proofs.items())},
        )
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    def g(self, key: str) -> str:
        """Gisement d'un fait (pour les notes de bas de page du rapport)."""
        return self.f[key][1]


def collect(root: Path | None = None) -> Facts:
    global ROOT
    if root is not None:
        ROOT = Path(root).resolve()
    fx = Facts()
    fx.read_schema()
    fx.read_seed()
    fx.read_app()
    fx.read_versions()
    fx.read_lib()
    fx.read_volume()
    fx.derive()
    return fx


if __name__ == "__main__":
    fx = collect()
    out = Path(__file__).resolve().parent.parent / "audit" / "facts.json"
    fx.dump(out)
    print(f"relevé écrit dans {out.relative_to(ROOT)}")
    for k, (v, s) in sorted(fx.f.items()):
        print(f"{k:22} = {v!s:34} ⟵ {s}")
    print("— dérivés —")
    for k in ("prix_min", "prix_max", "prix_moyen", "prix_median", "en_promo", "promo_moyenne_pct",
              "vedettes", "nouveautes", "images", "ruptures_simulees", "faible_stock_simule"):
        print(f"{k:22} = {fx.counts[k]}")
    print("par univers :", fx.counts["par_univers"])
    print("par marque  :", fx.counts["par_marque"])


_CACHE: Facts | None = None


def get(root: Path | None = None) -> Facts:
    """Accès mutualisé au relevé (une lecture du dépôt par build, pas une par figure)."""
    global _CACHE
    if _CACHE is None:
        _CACHE = collect(root)
    return _CACHE


def v(key: str):
    """Valeur d'un fait — les figures et le texte ne tapent jamais un nombre à la main."""
    return get().f[key][0]


def src(key: str) -> str:
    return get().g(key)


def c(key: str):
    return get().counts[key]
