import { chromium } from "playwright";

const browser = await chromium.launch({ 
  headless: true, 
  executablePath: "/usr/bin/google-chrome",
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
});
const context = await browser.newContext();
const page = await context.newPage();

await page.setViewportSize({ width: 375, height: 812 });
await page.goto("http://localhost:3456/login");
await page.waitForTimeout(2000);

const loginData = await page.evaluate(() => {
  const body = document.body;
  const main = document.querySelector('main');
  return {
    bodyBg: getComputedStyle(body).backgroundColor,
    mainMinHeight: getComputedStyle(main).minHeight,
    hasSkipLink: document.querySelector('.skip-link') !== null,
    formElements: document.querySelectorAll('input, button').length
  };
});

console.log("Login page (375px):", JSON.stringify(loginData, null, 2));

await page.close();
await browser.close();
