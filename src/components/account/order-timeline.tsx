"use client";
import { motion, useReducedMotion } from "framer-motion";
import { CheckIcon } from "@/components/icons";
import { ORDER_FLOW, ORDER_STATUS_LABELS } from "@/lib/order-constants";
import type { OrderStatus } from "@/db/schema";
import { formatDateTime } from "@/lib/utils";
import { EASE_LUXE } from "@/lib/motion";

export function OrderTimeline({ status, events }: { status: OrderStatus; events: { status: OrderStatus; message: string | null; createdAt: Date | string }[] }) {
  const reduce = useReducedMotion();
  const terminal = status === "cancelled" || status === "returned";
  const idx = terminal ? -1 : ORDER_FLOW.indexOf(status);
  return (
    <div>
      {terminal ? <p className="mb-6 inline-flex bg-error-soft px-3 py-1.5 text-xs uppercase tracking-[0.14em] text-error">{ORDER_STATUS_LABELS[status]}</p> : (
        <ol className="grid grid-cols-5 gap-1" aria-label="Progression">
          {ORDER_FLOW.map((s, i) => (
            <li key={s} className="flex flex-col items-center text-center">
              <motion.span initial={reduce ? false : { scale: 0.7, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: i * 0.12, duration: 0.6, ease: EASE_LUXE }} className={`flex h-8 w-8 items-center justify-center border ${i <= idx ? "border-ink bg-ink text-paper" : "border-stone-2 text-muted-2"}`}>{i < idx ? <CheckIcon size={14} /> : <span className="text-[11px]">{i + 1}</span>}</motion.span>
              <span className={`mt-2 text-[10px] uppercase tracking-[0.12em] ${i <= idx ? "text-ink" : "text-muted-2"}`}>{ORDER_STATUS_LABELS[s]}</span>
            </li>
          ))}
        </ol>
      )}
      <ul className="mt-8 space-y-4 border-l border-stone pl-5">
        {events.map((e, i) => (
          <motion.li key={i} initial={reduce ? false : { opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 + i * 0.08, duration: 0.6, ease: EASE_LUXE }} className="relative text-sm">
            <span className="absolute -left-[23px] top-1.5 h-1.5 w-1.5 bg-champagne" />
            <p className="text-ink">{ORDER_STATUS_LABELS[e.status]}{e.message ? <span className="text-muted"> — {e.message}</span> : null}</p>
            <p className="text-xs text-muted-2">{formatDateTime(e.createdAt)}</p>
          </motion.li>
        ))}
      </ul>
    </div>
  );
}
