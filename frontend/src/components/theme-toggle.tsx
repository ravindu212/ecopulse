"use client";

import { Moon, Sun } from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";
import { useTheme } from "next-themes";
import { useSyncExternalStore } from "react";

type ViewTransitionDocument = Document & { startViewTransition?: (callback: () => void) => { ready: Promise<void> } };

function subscribeToHydration(notify: () => void) {
  const frame = requestAnimationFrame(notify);
  return () => cancelAnimationFrame(frame);
}

export function ThemeToggle() {
  const { resolvedTheme, setTheme, theme } = useTheme();
  const mounted = useSyncExternalStore(subscribeToHydration, () => true, () => false);
  const reduceMotion = useReducedMotion();
  const dark = resolvedTheme === "dark";

  function toggle(event: React.MouseEvent<HTMLButtonElement>) {
    const nextTheme = dark ? "light" : "dark";
    const documentWithTransition = document as ViewTransitionDocument;
    if (reduceMotion || !documentWithTransition.startViewTransition) {
      setTheme(nextTheme);
      return;
    }
    const rect = event.currentTarget.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    const transition = documentWithTransition.startViewTransition(() => setTheme(nextTheme));
    transition.ready.then(() => document.documentElement.animate({ clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] }, { duration: 650, easing: "cubic-bezier(.22,1,.36,1)", pseudoElement: "::view-transition-new(root)" }));
  }

  if (!mounted) return <span className="h-9 w-9" aria-hidden="true" />;
  return <div className="flex items-center gap-1"><motion.button type="button" aria-label={`Switch to ${dark ? "light" : "dark"} theme`} title={`Switch to ${dark ? "light" : "dark"} theme`} onClick={toggle} whileHover={reduceMotion ? undefined : { scale: 1.06 }} whileTap={reduceMotion ? undefined : { scale: 0.94 }} className="grid h-9 w-9 place-items-center rounded-full border border-[var(--border)] bg-[var(--surface)] text-[var(--foreground)] shadow-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--secondary)]"><motion.span animate={reduceMotion ? undefined : { rotate: dark ? 0 : 180, scale: [1, 1.12, 1] }} transition={{ duration: 0.35, ease: "easeOut" }}>{dark ? <Sun size={17} aria-hidden="true" /> : <Moon size={17} aria-hidden="true" />}</motion.span></motion.button><select aria-label="Theme preference" value={theme ?? "system"} onChange={(event) => setTheme(event.target.value)} className="w-20 rounded-md border border-[var(--border)] bg-[var(--surface)] px-1 py-1 text-xs text-[var(--muted)] sm:w-auto sm:px-2"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></div>;
}
