import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowRightIcon, ChevronRightIcon, MinusIcon, PlusIcon } from "@/components/icons";
import { cn } from "@/lib/utils";

/* ── Section heading — editorial, numbered, restraint ─────────── */
export function SectionHeading({
  eyebrow, title, description, action, align = "left", className, index, italic,
}: {
  eyebrow?: string; title: string; description?: string;
  action?: { href: string; label: string }; align?: "left" | "center";
  className?: string; index?: string; italic?: boolean;
}) {
  return (
    <div className={cn("flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between", align === "center" && "sm:flex-col sm:items-center sm:text-center", className)}>
      <div className={cn("max-w-2xl", align === "center" && "flex flex-col items-center")}>
        <p className="eyebrow mb-5 flex items-center gap-3">
          {index && <span className="font-display text-base italic text-champagne-2">{index}</span>}
          {eyebrow}
        </p>
        <h2 className={cn("font-display text-display-md text-ink", italic && "italic")}>{title}</h2>
        {description && <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-muted">{description}</p>}
      </div>
      {action && (
        <Link href={action.href} className="btn-ghost shrink-0">
          {action.label} <ArrowRightIcon size={14} />
        </Link>
      )}
    </div>
  );
}

/* ── Breadcrumbs ──────────────────────────────────────────────── */
export function Breadcrumbs({ items, light }: { items: { href?: string; label: string }[]; light?: boolean }) {
  return (
    <nav aria-label="Fil d'Ariane" className={cn("text-[11px] uppercase tracking-[0.18em]", light ? "text-paper/70" : "text-muted")}>
      <ol className="flex flex-wrap items-center gap-2">
        <li><Link href="/" className={cn("transition-colors hover:text-champagne", light ? "hover:text-paper" : "hover:text-ink")}>Accueil</Link></li>
        {items.map((it, i) => (
          <li key={i} className="flex items-center gap-2">
            <ChevronRightIcon size={10} className={light ? "text-paper/40" : "text-sand-2"} />
            {it.href ? (
              <Link href={it.href} className={cn("transition-colors hover:text-champagne", light ? "hover:text-paper" : "hover:text-ink")}>{it.label}</Link>
            ) : (
              <span className={light ? "text-paper/90" : "text-ink"} aria-current="page">{it.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

/* ── Empty state — editorial, with a reason ───────────────────── */
export function EmptyState({ icon, title, description, action, tone = "light" }: { icon: ReactNode; title: string; description?: string; action?: { href: string; label: string }; tone?: "light" | "dark" }) {
  const dark = tone === "dark";
  return (
    <div className={cn("flex flex-col items-center px-6 py-24 text-center", dark ? "bg-noir text-paper" : "border border-stone-2/60 bg-cream")}>
      <span className={cn("flex h-16 w-16 items-center justify-center", dark ? "border border-paper/25" : "border border-stone-2", "text-champagne")}>{icon}</span>
      <h3 className={cn("mt-7 font-display text-display-sm", dark ? "text-paper" : "text-ink")}>{title}</h3>
      {description && <p className={cn("mt-2 max-w-sm text-sm", dark ? "text-paper/70" : "text-muted")}>{description}</p>}
      {action && (
        <Link href={action.href} className={cn("mt-9", dark ? "btn-light" : "btn-secondary")}>{action.label}</Link>
      )}
    </div>
  );
}

/* ── Badge — small, flat, typographic ─────────────────────────── */
export function Badge({ children, tone = "neutral", className }: { children: ReactNode; tone?: "neutral" | "accent" | "success" | "warning" | "error" | "ink" | "outline"; className?: string }) {
  const tones: Record<string, string> = {
    neutral: "bg-stone/70 text-charcoal",
    accent: "bg-champagne-soft text-champagne-2",
    success: "bg-success-soft text-success",
    warning: "bg-warning-soft text-warning",
    error: "bg-error-soft text-error",
    ink: "bg-ink text-paper",
    outline: "border border-current",
  };
  return <span className={cn("inline-flex items-center px-2 py-1 text-[9px] font-bold uppercase tracking-[0.18em]", tones[tone], className)}>{children}</span>;
}

/* ── Quantity stepper ─────────────────────────────────────────── */
export function QtyStepper({ value, onChange, max = 20, min = 1, size = "md" }: { value: number; onChange: (v: number) => void; max?: number; min?: number; size?: "sm" | "md" }) {
  const h = size === "sm" ? "h-10" : "h-12";
  const w = size === "sm" ? "w-9" : "w-11";
  return (
    <div className={cn("inline-flex items-center border border-stone-2 bg-cream", h)} role="group" aria-label="Quantité">
      <button type="button" onClick={() => onChange(value - 1)} disabled={value <= min} aria-label="Diminuer la quantité" className={cn("flex items-center justify-center text-ink transition-opacity hover:opacity-60 disabled:opacity-25", w, h)}><MinusIcon size={13} /></button>
      <span className="min-w-9 text-center text-sm tabular-nums text-ink" aria-live="polite">{value}</span>
      <button type="button" onClick={() => onChange(value + 1)} disabled={value >= max} aria-label="Augmenter la quantité" className={cn("flex items-center justify-center text-ink transition-opacity hover:opacity-60 disabled:opacity-25", w, h)}><PlusIcon size={13} /></button>
    </div>
  );
}

/* ── Checkout steps ───────────────────────────────────────────── */
export function Steps({ steps, current }: { steps: string[]; current: number }) {
  return (
    <ol className="flex items-center gap-2" aria-label="Étapes de commande">
      {steps.map((s, i) => {
        const done = i < current, active = i === current;
        return (
          <li key={s} className="flex flex-1 items-center gap-2">
            <span className={cn("flex h-8 w-8 shrink-0 items-center justify-center border text-[11px] tabular-nums transition-all duration-500",
              done ? "border-ink bg-ink text-paper" : active ? "border-champagne bg-champagne-soft text-champagne-2" : "border-stone-2 text-muted-2")}
              aria-current={active ? "step" : undefined}>{done ? "✓" : i + 1}</span>
            <span className={cn("hidden text-[10px] font-semibold uppercase tracking-[0.18em] sm:block", active ? "text-ink" : "text-muted-2")}>{s}</span>
            {i < steps.length - 1 && <span className={cn("h-px flex-1 transition-colors duration-700", done ? "bg-champagne" : "bg-stone-2/60")} />}
          </li>
        );
      })}
    </ol>
  );
}

/* ── Form field with label / hint / error ─────────────────────── */
export function Field({ label, error, children, hint, htmlFor }: { label: string; error?: string; children: ReactNode; hint?: string; htmlFor?: string }) {
  return (
    <label className="block text-left" htmlFor={htmlFor}>
      <span className="mb-2 block text-[10px] font-semibold uppercase tracking-[0.18em] text-muted">{label}</span>
      {children}
      {hint && !error && <span className="mt-1.5 block text-xs text-muted-2">{hint}</span>}
      {error && <span className="mt-1.5 block text-xs font-medium text-error" role="alert">{error}</span>}
    </label>
  );
}

/* ── Product grid skeleton ────────────────────────────────────── */
export function ProductGridSkeleton({ n = 8 }: { n?: number }) {
  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-10 md:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: n }).map((_, i) => (
        <div key={i}>
          <div className="skeleton aspect-square" />
          <div className="skeleton mt-5 h-2.5 w-1/3" />
          <div className="skeleton mt-2.5 h-4 w-4/5" />
          <div className="skeleton mt-3.5 h-4 w-1/4" />
        </div>
      ))}
    </div>
  );
}
