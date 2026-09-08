"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRightIcon, WarningIcon } from "@/components/icons";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="flex min-h-dvh items-center justify-center bg-noir px-6 text-paper">
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }} className="w-full max-w-lg text-center">
        <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full border border-champagne-3/50 text-champagne-3"><WarningIcon size={24} /></span>
        <p className="eyebrow mt-9 text-champagne-3">Un imprévu est survenu</p>
        <h1 className="mt-4 font-display text-display-md">La boutique reste <em>ouverte</em></h1>
        <p className="mx-auto mt-4 max-w-sm text-sm leading-relaxed text-paper/65">
          Une erreur technique s&apos;est produite sur cette page. Vos données et votre panier sont en sécurité — vous pouvez réessayer, ou reprendre votre parcours.
        </p>
        {error.digest && <p className="mt-6 text-[10px] uppercase tracking-[0.2em] text-paper/35">Référence {error.digest}</p>}
        <div className="mt-9 flex flex-wrap justify-center gap-3">
          <button onClick={reset} className="btn-light">Réessayer</button>
          <Link href="/" className="inline-flex min-h-[52px] items-center gap-2 border border-paper/40 px-8 text-[11px] font-bold uppercase tracking-[0.2em] text-paper transition-colors hover:border-paper hover:bg-paper hover:text-noir">Accueil <ArrowRightIcon size={13} /></Link>
        </div>
      </motion.div>
    </div>
  );
}
