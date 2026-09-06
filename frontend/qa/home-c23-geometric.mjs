import { chromium } from "playwright";

const baseUrl = process.env.HOME_QA_BASE ?? "http://localhost:3007";
const viewports = [
  [375, 812],
  [430, 932],
  [768, 1024],
  [1366, 768],
  [1440, 900],
  [1920, 948],
  [1920, 1080],
  [2560, 1440],
];
const jumpOrder = [0.7, 0.18, 0.93, 0.42, 0.05, 1, 0.3, 0.82, 0, 0.56, 0.1];

function almostEqual(left, right, tolerance = 0.025) {
  return Math.abs(left - right) <= tolerance;
}

async function settle(page) {
  await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(resolve)));
}

async function measure(page) {
  return page.evaluate(() => {
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    const stage = document.querySelector(".home-system-chapters");
    const stageIsSticky = stage ? getComputedStyle(stage).position === "sticky" : false;
    const headerRect = document.querySelector(".site-header-inner")?.getBoundingClientRect();
    const sceneData = [...document.querySelectorAll(".home-signal-scene")].map((scene) => {
      const opacity = Number(getComputedStyle(scene).opacity);
      const style = getComputedStyle(scene);
      const safeTop = Number.parseFloat(style.paddingTop) || 0;
      const safeBottom = Number.parseFloat(style.paddingBottom) || 0;
      const heading = scene.querySelector("[data-home-heading]")?.getBoundingClientRect();
      const blocks = [...scene.querySelectorAll("[data-home-primary]")].map((block) => {
        const rect = block.getBoundingClientRect();
        return { left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom };
      });
      return {
        key: scene.dataset.sceneKey,
        opacity,
        safeTop,
        safeBottom,
        heading: heading
          ? { left: heading.left, right: heading.right, top: heading.top, bottom: heading.bottom }
          : null,
        blocks,
      };
    });

    const meaningful = [...document.querySelectorAll(
      "main h1, main h2, main h3, main p, main img, main [data-home-primary], main .home-system-disc, main [data-home-event-card]",
    )].some((element) => {
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      return style.display !== "none"
        && style.visibility !== "hidden"
        && Number(style.opacity) >= 0.08
        && rect.bottom > 0
        && rect.top < viewportHeight
        && rect.right > 0
        && rect.left < viewportWidth;
    });

    const eventRects = [...document.querySelectorAll("[data-home-event-card]")]
      .filter((card) => {
        const rect = card.getBoundingClientRect();
        return rect.bottom > 0 && rect.top < viewportHeight;
      })
      .map((card) => {
        const rect = card.getBoundingClientRect();
        return { left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom };
      });

    return {
      scrollY: window.scrollY,
      overflow: document.documentElement.scrollWidth - viewportWidth,
      stageIsSticky,
      header: headerRect
        ? { top: headerRect.top, bottom: headerRect.bottom, left: headerRect.left, right: headerRect.right }
        : null,
      scenes: sceneData,
      meaningful,
      eventRects,
    };
  });
}

function inspectMeasurement(measurement, viewportHeight, failures) {
  if (measurement.overflow > 1) failures.horizontalOverflow += 1;

  if (measurement.stageIsSticky) {
    const meaningfulScenes = measurement.scenes.filter((scene) => scene.opacity >= 0.15);
    if (measurement.scenes.filter((scene) => scene.opacity >= 0.55).length > 1) {
      failures.dominance += 1;
    }

    for (const scene of meaningfulScenes) {
      if (scene.heading
        && (scene.heading.top < scene.safeTop - 1
          || scene.heading.bottom > viewportHeight - scene.safeBottom + 1)) {
        failures.headingBoundary += 1;
      }
      for (const block of scene.blocks) {
        if (block.top < scene.safeTop - 1 || block.bottom > viewportHeight - scene.safeBottom + 1) {
          failures.primaryBoundary += 1;
        }
        if (measurement.header
          && measurement.header.bottom > 0
          && block.top < measurement.header.bottom + 1) {
          failures.headerCollision += 1;
        }
      }
    }

    for (let left = 0; left < meaningfulScenes.length; left += 1) {
      for (let right = left + 1; right < meaningfulScenes.length; right += 1) {
        for (const leftBlock of meaningfulScenes[left].blocks) {
          for (const rightBlock of meaningfulScenes[right].blocks) {
            const width = Math.min(leftBlock.right, rightBlock.right) - Math.max(leftBlock.left, rightBlock.left);
            const height = Math.min(leftBlock.bottom, rightBlock.bottom) - Math.max(leftBlock.top, rightBlock.top);
            if (width > 2 && height > 2) failures.crossSceneOverlap += 1;
          }
        }
      }
    }
  }

  for (let left = 0; left < measurement.eventRects.length; left += 1) {
    for (let right = left + 1; right < measurement.eventRects.length; right += 1) {
      const a = measurement.eventRects[left];
      const b = measurement.eventRects[right];
      if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2
        && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2) {
        failures.eventCollision += 1;
      }
    }
  }
}

async function auditViewport(page, width, height, theme) {
  await page.setViewportSize({ width, height });
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
  await page.evaluate((nextTheme) => document.documentElement.setAttribute("data-theme", nextTheme), theme);
  await settle(page);

  const maxScroll = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
  const steps = Math.max(220, Math.ceil(maxScroll / 50));
  const positions = Array.from({ length: steps + 1 }, (_, index) => Math.round(maxScroll * index / steps));
  const failures = {
    headingBoundary: 0,
    primaryBoundary: 0,
    crossSceneOverlap: 0,
    dominance: 0,
    headerCollision: 0,
    horizontalOverflow: 0,
    eventCollision: 0,
    deadZone: 0,
    reverseMismatch: 0,
    jumpMismatch: 0,
  };
  const forward = new Map();
  let emptyStart = null;

  for (const position of positions) {
    await page.evaluate((scrollPosition) => scrollTo(0, scrollPosition), position);
    await settle(page);
    const measurement = await measure(page);
    inspectMeasurement(measurement, height, failures);
    forward.set(position, measurement.scenes.map((scene) => scene.opacity));

    if (!measurement.meaningful && emptyStart === null) emptyStart = position;
    if (measurement.meaningful && emptyStart !== null) {
      if (position - emptyStart > height * 0.65) failures.deadZone += 1;
      emptyStart = null;
    }
  }
  if (emptyStart !== null && maxScroll - emptyStart > height * 0.65) failures.deadZone += 1;

  for (const position of [...positions].reverse()) {
    await page.evaluate((scrollPosition) => scrollTo(0, scrollPosition), position);
    await settle(page);
    const measurement = await measure(page);
    inspectMeasurement(measurement, height, failures);
    const expected = forward.get(position) ?? [];
    if (measurement.scenes.some((scene, index) => !almostEqual(scene.opacity, expected[index] ?? 0))) {
      failures.reverseMismatch += 1;
    }
  }

  for (const fraction of jumpOrder) {
    const position = Math.round(maxScroll * fraction);
    await page.evaluate((scrollPosition) => scrollTo(0, scrollPosition), position);
    await settle(page);
    const measurement = await measure(page);
    inspectMeasurement(measurement, height, failures);
    const closest = positions.reduce((best, candidate) => (
      Math.abs(candidate - position) < Math.abs(best - position) ? candidate : best
    ));
    const expected = forward.get(closest) ?? [];
    if (measurement.scenes.some((scene, index) => !almostEqual(scene.opacity, expected[index] ?? 0, 0.04))) {
      failures.jumpMismatch += 1;
    }
  }

  return {
    viewport: `${width}x${height}`,
    theme,
    forwardSamples: positions.length,
    reverseSamples: positions.length,
    jumpSamples: jumpOrder.length,
    failures,
  };
}

const browser = await chromium.connectOverCDP("http://127.0.0.1:9224");
const context = browser.contexts()[0];
const page = await context.newPage();
const results = [];

for (const [width, height] of viewports) {
  results.push(await auditViewport(page, width, height, "dark"));
}
results.push(await auditViewport(page, 1920, 948, "light"));

console.log(JSON.stringify(results, null, 2));
await browser.close();
