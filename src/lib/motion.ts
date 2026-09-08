import type { Transition, Variants } from "framer-motion";

/** Quiet Confidence — slow, precise, expensive. transform + opacity only. */
export const EASE_LUXE = [0.22, 1, 0.36, 1] as const;
export const EASE_EXIT = [0.55, 0, 1, 0.45] as const;

export const springSlow: Transition = { type: "spring", stiffness: 120, damping: 26, mass: 1 };
export const springCalm: Transition = { type: "spring", stiffness: 180, damping: 30, mass: 0.9 };
export const tweenSlow: Transition = { duration: 0.9, ease: EASE_LUXE };
export const tweenBase: Transition = { duration: 0.6, ease: EASE_LUXE };
export const tweenFast: Transition = { duration: 0.32, ease: EASE_LUXE };
export const tweenExit: Transition = { duration: 0.28, ease: EASE_EXIT };

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: tweenSlow },
};
export const fade: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: tweenBase },
};
export const stagger = (delay = 0.08, delayChildren = 0.05): Variants => ({
  hidden: {},
  show: { transition: { staggerChildren: delay, delayChildren } },
});
export const hoverLift = { y: -3, transition: tweenFast };
export const pageTransition = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: tweenBase },
  exit: { opacity: 0, transition: tweenExit },
};
