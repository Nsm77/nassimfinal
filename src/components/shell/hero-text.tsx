"use client";
import { motion, useReducedMotion } from "framer-motion";
import { EASE_LUXE } from "@/lib/motion";

/** Entrance — 01. Cinematic typographic entry to the maison. */
export function HeroText() {
  const reduce = useReducedMotion();
  const base = reduce ? {} : { y: "104%", opacity: 0 };
  return (
    <div>
      <motion.p
        initial={reduce ? false : { opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: EASE_LUXE, delay: 0.05 }}
        className="rule-label mb-8"
      >
        Espace Santé Beauté · Ezzahra &amp; Hammam-Lif
      </motion.p>
      <h1 className="font-display text-display-xl leading-[0.95] tracking-[-0.02em] text-ink">
        {[
          { t: "La beauté" },
          { t: "se soigne", i: true, accent: true },
          { t: "avec justesse.", i: true },
        ].map((l, i) => (
          <span key={l.t} className="block overflow-hidden pb-[0.06em]">
            <motion.span
              initial={base}
              animate={reduce ? {} : { y: 0, opacity: 1 }}
              transition={{ duration: 1.15, ease: EASE_LUXE, delay: 0.18 + i * 0.11 }}
              className={`block ${l.accent ? "text-champagne-2" : ""} ${l.i ? "italic" : ""}`}
              style={{ willChange: "transform, opacity" }}
            >
              {l.t}
            </motion.span>
          </span>
        ))}
      </h1>
      <motion.p
        initial={reduce ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.05, ease: EASE_LUXE, delay: 0.68 }}
        className="mt-8 max-w-lg text-[15px] leading-[1.8] text-muted sm:text-base"
      >
        Dermo-cosmétique, solaire, cheveux et compléments — une sélection resserrée de produits
        <em className="text-charcoal"> authentiques et utiles</em>, conseillée par nos pharmaciens et livrée partout en Tunisie.
      </motion.p>
    </div>
  );
}
