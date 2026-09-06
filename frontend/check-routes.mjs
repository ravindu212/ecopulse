import { chromium } from "playwright";

const browser = await chromium.launch({ 
  headless: true, 
  executablePath: "/usr/bin/google-chrome",
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
});
const context = await browser.newContext();

const routes = [
  "/climate-now/enso",
  "/outlooks",
  "/explore",
  "/indicators",
  "/events",
  "/learn",
  "/sdg",
  "/sdg/13",
  "/sources",
  "/dashboard",
  "/actions",
  "/challenges",
  "/progress",
  "/profile"
];

for (const route of routes) {
  const page = await context.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(`http://localhost:3456${route}`);
  await page.waitForTimeout(1500);
  
  const data = await page.evaluate(() => {
    const docHeight = document.documentElement.scrollHeight;
    const scrollWidth = document.documentElement.scrollWidth;
    const viewportWidth = window.innerWidth;
    const hasHorizontalOverflow = scrollWidth > viewportWidth;
    
    return {
      docHeight,
      scrollWidth,
      viewportWidth,
      hasHorizontalOverflow,
      overflowDiff: scrollWidth - viewportWidth
    };
  });
  
  const status = data.hasHorizontalOverflow ? "OVERFLOW" : "OK";
  console.log(`${route}: ${status} (h:${Math.round(data.docHeight)}, overflow:${data.overflowDiff}px)`);
  await page.close();
}

await browser.close();
