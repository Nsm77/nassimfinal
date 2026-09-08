"use client";
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckIcon, CloseIcon, InfoIcon, WarningIcon } from "@/components/icons";
import { springSlow, tweenExit } from "@/lib/motion";

type ToastKind = "success" | "info" | "error";
type Toast = { id: number; kind: ToastKind; title: string; description?: string; action?: { label: string; onClick: () => void } };
type Ctx = { toast: (t: Omit<Toast, "id">) => void };
const ToastCtx = createContext<Ctx>({ toast: () => {} });
export const useToast = () => useContext(ToastCtx);

export function ToasterProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Toast[]>([]);
  const dismiss = useCallback((id: number) => setItems((s) => s.filter((t) => t.id !== id)), []);
  const toast = useCallback((t: Omit<Toast, "id">) => {
    const id = Date.now() + Math.random();
    setItems((s) => [...s.slice(-3), { ...t, id }]);
    setTimeout(() => dismiss(id), 4200);
  }, [dismiss]);
  const value = useMemo(() => ({ toast }), [toast]);
  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div aria-live="polite" className="pointer-events-none fixed inset-x-0 bottom-4 z-[70] flex flex-col items-center gap-2 px-4 sm:items-end sm:bottom-6 sm:right-6">
        <AnimatePresence initial={false}>
          {items.map((t) => (
            <motion.div
              key={t.id}
              layout
              initial={{ opacity: 0, y: 16, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1, transition: springSlow }}
              exit={{ opacity: 0, y: 8, transition: tweenExit }}
              className="pointer-events-auto flex w-full max-w-sm items-start gap-3 border border-stone bg-cream px-4 py-3 shadow-float"
              role="status"
            >
              <span className={t.kind === "error" ? "text-error" : t.kind === "info" ? "text-muted" : "text-success"}>
                {t.kind === "error" ? <WarningIcon size={18} /> : t.kind === "info" ? <InfoIcon size={18} /> : <CheckIcon size={18} />}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-ink">{t.title}</p>
                {t.description && <p className="mt-0.5 text-xs text-muted">{t.description}</p>}
                {t.action && (
                  <button onClick={() => { t.action?.onClick(); dismiss(t.id); }} className="mt-2 text-xs uppercase tracking-[0.14em] text-champagne-2 underline-offset-4 hover:underline">
                    {t.action.label}
                  </button>
                )}
              </div>
              <button onClick={() => dismiss(t.id)} aria-label="Fermer" className="-m-1 flex h-8 w-8 items-center justify-center text-muted hover:text-ink">
                <CloseIcon size={14} />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastCtx.Provider>
  );
}
