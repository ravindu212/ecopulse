"use client";

import { motion, type Variants, useReducedMotion } from "framer-motion";
import { usePathname } from "next/navigation";
import { type ReactNode } from "react";

export const fadeUp: Variants = { hidden: { opacity: 0, y: 18 }, visible: { opacity: 1, y: 0, transition: { duration: 0.48, ease: "easeOut" } } };
export const fadeIn: Variants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { duration: 0.32, ease: "easeOut" } } };
export const scaleIn: Variants = { hidden: { opacity: 0, scale: 0.98 }, visible: { opacity: 1, scale: 1, transition: { duration: 0.35, ease: "easeOut" } } };
export const slideFromLeft: Variants = { hidden: { opacity: 0, x: -18 }, visible: { opacity: 1, x: 0, transition: { duration: 0.4, ease: "easeOut" } } };
export const slideFromRight: Variants = { hidden: { opacity: 0, x: 18 }, visible: { opacity: 1, x: 0, transition: { duration: 0.4, ease: "easeOut" } } };
export const staggerContainer: Variants = { hidden: {}, visible: { transition: { staggerChildren: 0.09, delayChildren: 0.06 } } };
export const staggerItem = fadeUp;

export function MotionSection({ children, className = "" }: { children: ReactNode; className?: string }) {
  const reduceMotion = useReducedMotion();
  return <motion.div className={className} variants={reduceMotion ? undefined : fadeUp} initial={false} animate="visible">{children}</motion.div>;
}

export function MotionList({ children, className = "" }: { children: ReactNode; className?: string }) {
  const reduceMotion = useReducedMotion();
  return <motion.div className={className} variants={reduceMotion ? undefined : staggerContainer} initial={false} animate="visible">{children}</motion.div>;
}

export function PageMotion({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const reduceMotion = useReducedMotion();

  return <motion.div id="page-content" tabIndex={-1} key={pathname} data-page-motion variants={reduceMotion ? undefined : fadeIn} initial={false} animate="visible">{children}</motion.div>;
}
