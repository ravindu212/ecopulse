import { chromium } from "playwright";

const BASE = "http://localhost:3456";
const VIEWPORTS = [
  { name: "375", width: 375, height: 812 },
  { name: "768", width: 768, height: 1024 },
  { name: "1440", width: 1440, height: 900 },
  { name: "1920", width: 1920, height: 1080 },
];

const PAGES = [
  { path: "/", name: "home" },
  { path: "/climate-now", name: "climate-now" },
];

const THEMES = [
  { name: "dark", set: async () => {} },
  { name: "light", set: async (page) => {
    await page.evaluate(() => document.documentElement.setAttribute("data-theme", "light"));
    await page.waitForTimeout(600);
  }},
];

async function capture() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
  });
  const context = await browser.newContext();

  for (const pageDef of PAGES) {
    for (const vp of VIEWPORTS) {
      for (const theme of THEMES) {
        const page = await context.newPage();
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE}${pageDef.path}`);
        await page.waitForTimeout(2000);
        
        await page.evaluate(() => {
          const style = document.createElement("style");
          style.textContent = `* { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }`;
          document.head.appendChild(style);
        });
        
        await theme.set(page);
        await page.waitForTimeout(800);
        
        const filePath = `/tmp/screenshots/${pageDef.name}-${vp.name}-${theme.name}.png`;
        await page.screenshot({ path: filePath, fullPage: true });
        console.log(`Captured ${filePath}`);
        await page.close();
      }
    }
  }

  await browser.close();
}

await capture();
