import type { ReactNode } from "react";
import { ORDER_STATUS_LABELS } from "@/lib/order-constants";
import type { OrderStatus } from "@/db/schema";
import { cn } from "@/lib/utils";

/* ── Page shell ───────────────────────────────────────────────── */
export function AdminPage({ title, sub, action, children, eyebrow }: { title: string; sub?: string; action?: ReactNode; children: ReactNode; eyebrow?: string }) {
  return (
    <div>
      <div className="mb-7 flex flex-wrap items-end justify-between gap-4 border-b border-admin-border pb-6">
        <div>
          {eyebrow && <p className="mb-2 text-[9px] font-bold uppercase tracking-[0.24em] text-admin-gold">{eyebrow}</p>}
          <h1 className="font-display text-display-sm tracking-tight text-admin-text">{title}</h1>
          {sub && <p className="mt-1.5 text-[13px] text-admin-muted">{sub}</p>}
        </div>
        {action && <div className="flex flex-wrap items-center gap-2">{action}</div>}
      </div>
      {children}
    </div>
  );
}

export function Panel({ children, className, title, action }: { children: ReactNode; className?: string; title?: string; action?: ReactNode }) {
  return (
    <div className={cn("border border-admin-border bg-admin-panel", className)}>
      {title && (
        <div className="flex items-center justify-between gap-4 border-b border-admin-border px-5 py-3.5">
          <h2 className="text-[10px] font-bold uppercase tracking-[0.2em] text-admin-muted">{title}</h2>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}

/* ── Data table — dense but legible ───────────────────────────── */
export function Table({ head, children, minWidth = "min-w-[720px]" }: { head: string[]; children: ReactNode; minWidth?: string }) {
  return (
    <div className="overflow-x-auto border border-admin-border bg-admin-panel">
      <table className={cn("w-full border-collapse text-[13px]", minWidth)}>
        <thead>
          <tr className="border-b border-admin-border text-left text-[9px] font-bold uppercase tracking-[0.18em] text-admin-muted">
            {head.map((h) => <th key={h} className="px-4 py-3 font-bold">{h}</th>)}
          </tr>
        </thead>
        <tbody className="divide-y divide-admin-border">{children}</tbody>
      </table>
    </div>
  );
}

/* ── Status badge ─────────────────────────────────────────────── */
const tones: Record<OrderStatus, string> = {
  pending: "bg-warning-soft text-warning", confirmed: "bg-champagne-soft text-champagne-2", preparing: "bg-champagne-soft text-champagne-2",
  shipped: "bg-stone text-charcoal", delivered: "bg-success-soft text-success", cancelled: "bg-error-soft text-error", returned: "bg-error-soft text-error",
};
export function StatusBadge({ s, className }: { s: OrderStatus; className?: string }) {
  return <span className={cn("inline-flex whitespace-nowrap px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.16em]", tones[s], className)}>{ORDER_STATUS_LABELS[s]}</span>;
}

/* ── KPIs — editorial, not dashboard-y ────────────────────────── */
export function KPI({ label, value, sub, tone = "text-admin-text" }: { label: string; value: string; sub?: string; tone?: string }) {
  return (
    <div className="relative overflow-hidden border border-admin-border bg-admin-panel px-5 py-6">
      <span aria-hidden className="absolute inset-x-0 top-0 h-px bg-admin-gold/40" />
      <p className="text-[9px] font-bold uppercase tracking-[0.22em] text-admin-muted">{label}</p>
      <p className={cn("mt-3 font-display text-[2rem] leading-none tracking-tight", tone)}>{value}</p>
      {sub && <p className="mt-2 text-xs text-admin-muted">{sub}</p>}
    </div>
  );
}

/* ── Inputs ───────────────────────────────────────────────────── */
export const afield = "w-full min-h-11 border border-admin-border bg-admin-bg px-3.5 py-2 text-sm text-admin-text placeholder:text-admin-muted focus:border-admin-gold focus:outline-none focus:ring-1 focus:ring-admin-gold/30 transition-colors";
export const abtn = "inline-flex min-h-11 items-center justify-center gap-2 bg-admin-gold px-4 text-[11px] font-bold uppercase tracking-[0.16em] text-noir transition-colors hover:bg-admin-text disabled:opacity-40";
export const abtnGhost = "inline-flex min-h-11 items-center justify-center gap-2 border border-admin-border px-4 text-[11px] font-bold uppercase tracking-[0.16em] text-admin-text transition-colors hover:border-admin-gold hover:text-admin-gold disabled:opacity-40";
export const abtnDanger = "inline-flex min-h-11 items-center justify-center gap-2 border border-error px-4 text-[11px] font-bold uppercase tracking-[0.16em] text-error transition-colors hover:bg-error hover:text-admin-text disabled:opacity-40";

export function AField({ label, children, error, hint }: { label: string; children: ReactNode; error?: string; hint?: string }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[9px] font-bold uppercase tracking-[0.18em] text-admin-muted">{label}</span>
      {children}
      {hint && !error && <span className="mt-1 block text-[11px] text-admin-muted">{hint}</span>}
      {error && <span className="mt-1 block text-[11px] text-error" role="alert">{error}</span>}
    </label>
  );
}

export function SectionLabel({ children, className }: { children: ReactNode; className?: string }) {
  return <h2 className={cn("mb-3 text-[10px] font-bold uppercase tracking-[0.2em] text-admin-muted", className)}>{children}</h2>;
}
