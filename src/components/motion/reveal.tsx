"use client";
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";
import { EASE_LUXE } from "@/lib/motion";

export function Reveal({ children, delay = 0, className, y = 18, once = true, as = "div" }: { children: ReactNode; delay?: number; className?: string; y?: number; once?: boolean; as?: "div" | "section" | "li" | "span" | "p" | "h1" | "h2" }) {
  const reduce = useReducedMotion();
  const M = motion[as] as typeof motion.div;
  return (
    <M
      initial={reduce ? false : { opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once, margin: "-10% 0px -10% 0px" }}
      transition={{ duration: 0.9, ease: EASE_LUXE, delay }}
      className={className}
      style={{ willChange: "transform, opacity" }}
    >
      {children}
    </M>
  );
}

export function Stagger({ children, className, delay = 0.08 }: { children: ReactNode; className?: string; delay?: number }) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      initial={reduce ? false : "hidden"}
      whileInView="show"
      viewport={{ once: true, margin: "-8% 0px" }}
      variants={{ hidden: {}, show: { transition: { staggerChildren: delay, delayChildren: 0.05 } } }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
export function StaggerItem({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div variants={{ hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.8, ease: EASE_LUXE } } }} className={className}>
      {children}
    </motion.div>
  );
}
