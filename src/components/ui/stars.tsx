"use client";
import { motion, useReducedMotion } from "framer-motion";
import { StarIcon } from "@/components/icons";

export function Stars({ value, count, size = 13, showCount = true, className = "" }: { value: number; count?: number; size?: number; showCount?: boolean; className?: string }) {
  const reduce = useReducedMotion();
  const v = Math.max(0, Math.min(5, value));
  return (
    <div className={`flex items-center gap-1.5 ${className}`} aria-label={`Note ${v.toFixed(1)} sur 5`}>
      <div className="relative inline-flex text-stone-2" aria-hidden>
        {[0, 1, 2, 3, 4].map((i) => <StarIcon key={i} size={size} filled />)}
        <motion.div
          className="absolute inset-0 flex overflow-hidden text-champagne"
          initial={reduce ? false : { width: 0 }}
          whileInView={{ width: `${(v / 5) * 100}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}
        >
          <div className="flex shrink-0">{[0, 1, 2, 3, 4].map((i) => <StarIcon key={i} size={size} filled />)}</div>
        </motion.div>
      </div>
      {showCount && count != null && <span className="text-xs text-muted">({count})</span>}
    </div>
  );
}

export function StarPicker({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex gap-1" role="radiogroup" aria-label="Votre note">
      {[1, 2, 3, 4, 5].map((i) => (
        <button key={i} type="button" role="radio" aria-checked={value === i} aria-label={`${i} étoile${i > 1 ? "s" : ""}`} onClick={() => onChange(i)} className={`flex h-11 w-11 items-center justify-center transition-colors ${i <= value ? "text-champagne" : "text-stone-2 hover:text-champagne-3"}`}>
          <StarIcon size={22} filled={i <= value} />
        </button>
      ))}
    </div>
  );
}
