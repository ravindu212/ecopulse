"use client";

import { useEffect } from "react";

function clamp(value: number) {
  return Math.min(1, Math.max(0, value));
}

export default function HomeScrollController() {
  useEffect(() => {
    const root = document.querySelector<HTMLElement>("[data-home-observatory]");
    if (!root) return;

    const scenes = Array.from(root.querySelectorAll<HTMLElement>("[data-home-scene]"));
    const journey = root.querySelector<HTMLElement>("[data-system-journey]");
    const reducedQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const pointerQuery = window.matchMedia("(hover: hover) and (pointer: fine)");
    let frame = 0;

    const update = () => {
      frame = 0;
      const viewport = window.innerHeight;
      const reduced = reducedQuery.matches;
      root.dataset.motion = reduced ? "reduced" : "full";

      scenes.forEach((scene) => {
        const bounds = scene.getBoundingClientRect();
        const progress = reduced ? 1 : clamp((viewport * 0.78 - bounds.top) / (bounds.height + viewport * 0.28));
        scene.style.setProperty("--scene-progress", progress.toFixed(4));
        scene.dataset.active = progress > 0.12 && progress < 0.92 ? "true" : "false";
      });

      if (journey) {
        const bounds = journey.getBoundingClientRect();
        const journeyProgress = reduced ? 1 : clamp(-bounds.top / Math.max(1, bounds.height - viewport));
        journey.style.setProperty("--journey-progress", journeyProgress.toFixed(4));
        const focal = scenes.find((scene) => {
          const bounds = scene.getBoundingClientRect();
          return bounds.top <= viewport * 0.55 && bounds.bottom >= viewport * 0.45;
        });
        journey.dataset.activeScene = focal?.dataset.sceneKey ?? "co2";
      }
    };

    const requestUpdate = () => {
      if (!frame) frame = window.requestAnimationFrame(update);
    };

    const handlePointer = (event: PointerEvent) => {
      if (!pointerQuery.matches || reducedQuery.matches) return;
      root.style.setProperty("--pointer-x", `${((event.clientX / window.innerWidth) - 0.5).toFixed(3)}`);
      root.style.setProperty("--pointer-y", `${((event.clientY / window.innerHeight) - 0.5).toFixed(3)}`);
    };

    const handleVisibility = () => {
      root.dataset.paused = document.hidden ? "true" : "false";
      requestUpdate();
    };

    update();
    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate);
    window.addEventListener("pointermove", handlePointer, { passive: true });
    document.addEventListener("visibilitychange", handleVisibility);
    reducedQuery.addEventListener("change", requestUpdate);

    return () => {
      if (frame) window.cancelAnimationFrame(frame);
      window.removeEventListener("scroll", requestUpdate);
      window.removeEventListener("resize", requestUpdate);
      window.removeEventListener("pointermove", handlePointer);
      document.removeEventListener("visibilitychange", handleVisibility);
      reducedQuery.removeEventListener("change", requestUpdate);
    };
  }, []);

  return null;
}
