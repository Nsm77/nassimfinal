"use client";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useCallback, useEffect, useState, useTransition } from "react";
import { CloseIcon, FilterIcon, SortIcon } from "@/components/icons";
import { formatDTShort } from "@/lib/money";
import type { SortKey } from "@/lib/catalog";
import { tweenExit } from "@/lib/motion";

export type Facets = { brands: { slug: string; name: string; n: number }[]; concerns: { slug: string; name: string; n: number }[]; priceMin: number; priceMax: number };
const SORTS: { v: SortKey; l: string }[] = [
  { v: "featured", l: "Notre sélection" }, { v: "bestsellers", l: "Meilleures ventes" }, { v: "newest", l: "Nouveautés" },
  { v: "price_asc", l: "Prix croissant" }, { v: "price_desc", l: "Prix décroissant" }, { v: "rating", l: "Mieux notés" },
];

export function useFilterParams() {
  const sp = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [pending, start] = useTransition();
  const update = useCallback((mut: (p: URLSearchParams) => void) => {
    const p = new URLSearchParams(sp.toString());
    mut(p); p.delete("page");
    start(() => router.replace(`${pathname}${p.toString() ? `?${p}` : ""}`, { scroll: false }));
  }, [sp, router, pathname]);
  const toggleMulti = (key: string, v: string) => update((p) => {
    const cur = new Set((p.get(key) ?? "").split(",").filter(Boolean));
    if (cur.has(v)) cur.delete(v); else cur.add(v);
    if (cur.size) p.set(key, [...cur].join(",")); else p.delete(key);
  });
  const set = (key: string, v: string | null) => update((p) => (v ? p.set(key, v) : p.delete(key)));
  const clearAll = () => start(() => router.replace(pathname, { scroll: false }));
  const has = (key: string, v: string) => (sp.get(key) ?? "").split(",").includes(v);
  const activeCount = ["brands", "concerns", "min", "max", "stock", "promo", "rating"].filter((k) => sp.get(k)).length;
  return { sp, toggleMulti, set, clearAll, has, activeCount, pending };
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <details open className="group border-b border-stone py-4">
      <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between text-xs uppercase tracking-[0.16em] text-ink">{title}<span className="text-muted transition-transform duration-500 group-open:rotate-45"><span className="block text-lg leading-none">+</span></span></summary>
      <div className="pt-3">{children}</div>
    </details>
  );
}
function Check({ checked, onChange, label, count }: { checked: boolean; onChange: () => void; label: string; count?: number }) {
  return (
    <label className="flex min-h-10 cursor-pointer items-center gap-3 text-sm text-charcoal hover:text-ink">
      <input type="checkbox" checked={checked} onChange={onChange} className="h-4 w-4 shrink-0 accent-ink" />
      <span className="flex-1">{label}</span>{count != null && <span className="text-xs text-muted-2">{count}</span>}
    </label>
  );
}

export function FilterPanel({ facets, hideConcerns = false, hideBrands = false }: { facets: Facets; hideConcerns?: boolean; hideBrands?: boolean }) {
  const f = useFilterParams();
  /*
   * `min`/`max` hold the draft value while typing; the URL is the committed value.
   * When the URL changes (e.g. « Tout effacer ») the draft is re-synced during
   * render — React's documented "adjusting state when a prop changes" pattern,
   * which avoids the cascading render an effect-based reset would cause.
   */
  const urlMin = f.sp.get("min") ?? "";
  const urlMax = f.sp.get("max") ?? "";
  const [min, setMin] = useState(urlMin);
  const [max, setMax] = useState(urlMax);
  const [synced, setSynced] = useState(`${urlMin}\u0000${urlMax}`);
  const current = `${urlMin}\u0000${urlMax}`;
  if (current !== synced) { setSynced(current); setMin(urlMin); setMax(urlMax); }
  return (
    <div className={f.pending ? "opacity-60 transition-opacity" : "transition-opacity"}>
      <div className="flex items-center justify-between border-b border-stone pb-3">
        <span className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-ink"><FilterIcon size={14} /> Filtres {f.activeCount > 0 && <span className="bg-ink px-1.5 py-0.5 text-[10px] text-paper">{f.activeCount}</span>}</span>
        {f.activeCount > 0 && <button onClick={f.clearAll} className="min-h-11 text-xs text-muted underline-offset-4 hover:text-ink hover:underline">Tout effacer</button>}
      </div>
      <Section title="Disponibilité">
        <Check checked={f.sp.get("stock") === "1"} onChange={() => f.set("stock", f.sp.get("stock") === "1" ? null : "1")} label="En stock uniquement" />
        <Check checked={f.sp.get("promo") === "1"} onChange={() => f.set("promo", f.sp.get("promo") === "1" ? null : "1")} label="En promotion" />
      </Section>
      {!hideBrands && facets.brands.length > 0 && (
        <Section title="Marques"><div className="max-h-64 space-y-0.5 overflow-y-auto pr-1">{facets.brands.map((b) => <Check key={b.slug} checked={f.has("brands", b.slug)} onChange={() => f.toggleMulti("brands", b.slug)} label={b.name} count={b.n} />)}</div></Section>
      )}
      {!hideConcerns && facets.concerns.length > 0 && (
        <Section title="Besoins"><div className="space-y-0.5">{facets.concerns.map((c) => <Check key={c.slug} checked={f.has("concerns", c.slug)} onChange={() => f.toggleMulti("concerns", c.slug)} label={c.name} count={c.n} />)}</div></Section>
      )}
      <Section title="Prix">
        <p className="mb-2 text-xs text-muted-2">De {formatDTShort(facets.priceMin)} à {formatDTShort(facets.priceMax)}</p>
        <form onSubmit={(e) => { e.preventDefault(); f.set("min", min ? String(Math.round(Number(min) * 1000)) : null); f.set("max", max ? String(Math.round(Number(max) * 1000)) : null); }} className="flex items-center gap-2">
          <input inputMode="decimal" value={min ? String(Number(min) / (min.length > 4 ? 1000 : 1)) : ""} onChange={(e) => setMin(e.target.value)} placeholder="Min" aria-label="Prix minimum (DT)" className="field h-11 min-h-0 px-3 text-sm" />
          <span className="text-muted-2">–</span>
          <input inputMode="decimal" value={max ? String(Number(max) / (max.length > 4 ? 1000 : 1)) : ""} onChange={(e) => setMax(e.target.value)} placeholder="Max" aria-label="Prix maximum (DT)" className="field h-11 min-h-0 px-3 text-sm" />
          <button className="btn-secondary h-11 min-h-0 px-3 text-[11px]">OK</button>
        </form>
      </Section>
      <Section title="Note minimale">
        <div className="flex gap-2">{[4, 3].map((r) => <button key={r} onClick={() => f.set("rating", f.sp.get("rating") === String(r) ? null : String(r))} className={`min-h-11 border px-3 text-xs ${f.sp.get("rating") === String(r) ? "border-ink bg-ink text-paper" : "border-stone-2 text-charcoal hover:border-ink"}`}>{r}★ et +</button>)}</div>
      </Section>
    </div>
  );
}

export function SortSelect() {
  const f = useFilterParams();
  return (
    <label className="flex items-center gap-2 text-xs text-muted">
      <SortIcon size={14} /><span className="hidden sm:inline">Trier :</span>
      <select value={(f.sp.get("sort") as SortKey) ?? "featured"} onChange={(e) => f.set("sort", e.target.value === "featured" ? null : e.target.value)} className="min-h-11 bg-transparent text-sm text-ink focus:outline-none" aria-label="Trier par">
        {SORTS.map((s) => <option key={s.v} value={s.v}>{s.l}</option>)}
      </select>
    </label>
  );
}

export function MobileFilters(props: { facets: Facets; hideConcerns?: boolean; hideBrands?: boolean }) {
  const [open, setOpen] = useState(false);
  const f = useFilterParams();
  const reduce = useReducedMotion();
  useEffect(() => { document.body.style.overflow = open ? "hidden" : ""; return () => { document.body.style.overflow = ""; }; }, [open]);
  return (
    <>
      <button onClick={() => setOpen(true)} className="flex min-h-11 items-center gap-2 border border-stone-2 px-4 text-xs uppercase tracking-[0.14em] text-ink lg:hidden"><FilterIcon size={14} /> Filtres {f.activeCount > 0 && `(${f.activeCount})`}</button>
      <AnimatePresence>
        {open && (
          <>
            <motion.button aria-label="Fermer" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setOpen(false)} className="fixed inset-0 z-50 bg-ink/30 backdrop-blur-sm lg:hidden" />
            <motion.div role="dialog" aria-modal="true" aria-label="Filtres" initial={reduce ? false : { y: "100%" }} animate={{ y: 0 }} exit={{ y: "100%", transition: tweenExit }} transition={{ type: "spring", stiffness: 180, damping: 30 }} className="fixed inset-x-0 bottom-0 z-[60] flex max-h-[88dvh] flex-col bg-paper lg:hidden">
              <div className="flex h-14 items-center justify-between border-b border-stone px-5"><span className="text-sm text-ink">Filtres</span><button onClick={() => setOpen(false)} aria-label="Fermer" className="flex h-11 w-11 items-center justify-center"><CloseIcon /></button></div>
              <div className="flex-1 overflow-y-auto px-5 pb-4"><FilterPanel {...props} /></div>
              <div className="border-t border-stone p-4"><button onClick={() => setOpen(false)} className="btn-primary w-full">Voir les résultats</button></div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
