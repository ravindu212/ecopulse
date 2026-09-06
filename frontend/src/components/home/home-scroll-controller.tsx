"use client";

import { useEffect } from "react";

function clamp(value: number) {
  return Math.min(1, Math.max(0, value));
}

function ease(progress: number) {
  const value = clamp(progress);
  return value * value * (3 - 2 * value);
}

export function getScenePresentation(progress: number, index: number, count: number) {
  const position = progress * count - index;
  const local = clamp(position);
  const entering = index === 0 ? 1 : ease((position + 0.08) / 0.2);
  const exitStart = index === count - 1 ? 0.88 : 0.72;
  const exiting = ease((local - exitStart) / (1 - exitStart));
  const opacity = clamp(entering * (1 - exiting));

  return {
    local,
    opacity,
    translateY: (1 - entering) * 28 - exiting * 28,
    scale: 1 - (1 - opacity) * 0.006,
    isDominant: opacity >= 0.55,
  };
}

export default function HomeScrollController() {
  useEffect(() => {
    const root = document.querySelector<HTMLElement>("[data-home-observatory]");
    if (!root) return;

    const scenes = Array.from(root.querySelectorAll<HTMLElement>("[data-home-scene]"));
    const journey = root.querySelector<HTMLElement>("[data-system-journey]");
    const journeyScenes = journey
      ? Array.from(journey.querySelectorAll<HTMLElement>("[data-home-scene]"))
      : [];
    const hero = root.querySelector<HTMLElement>("[data-home-hero]");
    const header = root.querySelector<HTMLElement>(".site-header-inner");
    const reducedQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const pointerQuery = window.matchMedia("(hover: hover) and (pointer: fine)");
    const stageQuery = window.matchMedia("(min-width: 75rem) and (min-height: 52rem)");
    let frame = 0;
    let disposed = false;

    const update = () => {
      frame = 0;
      const viewport = window.innerHeight;
      const reduced = reducedQuery.matches;
      root.dataset.motion = reduced ? "reduced" : "full";
      if (header) root.style.setProperty("--home-header-height", `${header.offsetHeight}px`);

      scenes.forEach((scene) => {
        const bounds = scene.getBoundingClientRect();
        const progress = reduced ? 1 : clamp((viewport * 0.78 - bounds.top) / (bounds.height + viewport * 0.28));
        scene.style.setProperty("--scene-progress", progress.toFixed(4));
      });

      if (hero) {
        const bounds = hero.getBoundingClientRect();
        const scrollRange = Math.max(1, bounds.height - viewport);
        const heroProgress = reduced || !stageQuery.matches ? 0 : clamp(-bounds.top / scrollRange);
        hero.style.setProperty("--hero-progress", heroProgress.toFixed(4));
      }

      if (journey) {
        const bounds = journey.getBoundingClientRect();
        const cinematic = !reduced && stageQuery.matches;
        const journeyProgress = cinematic ? clamp(-bounds.top / Math.max(1, bounds.height - viewport)) : 0;
        journey.style.setProperty("--journey-progress", journeyProgress.toFixed(4));

        if (!cinematic) {
          journeyScenes.forEach((scene) => {
            scene.style.setProperty("--scene-progress", "1");
            scene.style.setProperty("--scene-opacity", "1");
            scene.style.setProperty("--scene-translate", "0px");
            scene.style.setProperty("--scene-scale", "1");
            scene.dataset.phase = "linear";
            scene.removeAttribute("aria-hidden");
            scene.inert = false;
          });
          const focal = journeyScenes.find((scene) => {
            const sceneBounds = scene.getBoundingClientRect();
            return sceneBounds.top <= viewport * 0.55 && sceneBounds.bottom >= viewport * 0.45;
          });
          journey.dataset.activeScene = focal?.dataset.sceneKey ?? "co2";
          return;
        }

        const activeIndex = Math.min(
          journeyScenes.length - 1,
          Math.floor(journeyProgress * journeyScenes.length),
        );
        journeyScenes.forEach((scene, index) => {
          const presentation = getScenePresentation(journeyProgress, index, journeyScenes.length);
          scene.style.setProperty("--scene-progress", presentation.local.toFixed(4));
          scene.style.setProperty("--scene-opacity", presentation.opacity.toFixed(4));
          scene.style.setProperty("--scene-translate", `${presentation.translateY.toFixed(2)}px`);
          scene.style.setProperty("--scene-scale", presentation.scale.toFixed(4));
          scene.dataset.phase = presentation.isDominant ? "dominant" : "transition";
          scene.setAttribute("aria-hidden", presentation.opacity < 0.01 ? "true" : "false");
          scene.inert = presentation.opacity < 0.01;

        });
        journey.dataset.activeScene = journeyScenes[activeIndex]?.dataset.sceneKey ?? "co2";
      }
    };

    const requestUpdate = () => {
      if (!disposed && !frame) frame = window.requestAnimationFrame(update);
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

    const resizeObserver = new ResizeObserver(requestUpdate);
    resizeObserver.observe(root);
    scenes.forEach((scene) => resizeObserver.observe(scene));

    update();
    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate);
    window.addEventListener("orientationchange", requestUpdate);
    window.addEventListener("pageshow", requestUpdate);
    window.addEventListener("load", requestUpdate);
    window.addEventListener("pointermove", handlePointer, { passive: true });
    document.addEventListener("visibilitychange", handleVisibility);
    reducedQuery.addEventListener("change", requestUpdate);
    stageQuery.addEventListener("change", requestUpdate);
    void document.fonts?.ready.then(requestUpdate);

    return () => {
      disposed = true;
      if (frame) window.cancelAnimationFrame(frame);
      resizeObserver.disconnect();
      window.removeEventListener("scroll", requestUpdate);
      window.removeEventListener("resize", requestUpdate);
      window.removeEventListener("orientationchange", requestUpdate);
      window.removeEventListener("pageshow", requestUpdate);
      window.removeEventListener("load", requestUpdate);
      window.removeEventListener("pointermove", handlePointer);
      document.removeEventListener("visibilitychange", handleVisibility);
      reducedQuery.removeEventListener("change", requestUpdate);
      stageQuery.removeEventListener("change", requestUpdate);
    };
  }, []);

  return null;
}
