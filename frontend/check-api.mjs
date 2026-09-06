import { chromium } from "playwright";

const browser = await chromium.launch({ 
  headless: true, 
  executablePath: "/usr/bin/google-chrome",
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
});
const context = await browser.newContext();
const page = await context.newPage();

const requests = [];
page.on("response", async (response) => {
  const url = response.url();
  if (url.includes("/api/v1/climate")) {
    requests.push({
      url,
      status: response.status(),
      ok: response.ok()
    });
  }
});

await page.setViewportSize({ width: 375, height: 812 });
await page.goto("http://localhost:3456/");
await page.waitForTimeout(3000);

console.log("API requests:", JSON.stringify(requests, null, 2));

const dataStatus = await page.evaluate(() => {
  return {
    hasDataUnavailable: document.querySelectorAll(".climate-unavailable").length,
    hasSeriesPlots: document.querySelectorAll(".home-series").length,
    hasCO2Data: document.querySelector('[data-home-scene="co2"] .home-data-focus') !== null,
    hasTempData: document.querySelector('[data-home-scene="temperature"] .home-data-focus') !== null
  };
});

console.log("Data status:", JSON.stringify(dataStatus, null, 2));
await browser.close();
