#!/usr/bin/env node
// Dev-only browser checks; the static website does not load Playwright.
// Install playwright@1.64.0 outside this repository and expose it via NODE_PATH.
// Usage: node scripts/browser_compatibility.cjs [base-url] [artifact-directory]
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const playwright = require('playwright');

const ROUTES = ['/', '/towing-shawano-wi/', '/towing-bonduel-wi/', '/towing-pulaski-wi/'];
const WIDTHS = [320, 375, 1440];
const ENGINES = ['chromium', 'firefox', 'webkit'];
const baseURL = new URL(process.argv[2] || 'http://127.0.0.1:4173');
const artifactDir = path.resolve(process.argv[3] || path.join(os.tmpdir(), 'lucky7-browser-compatibility'));
assert(['http:', 'https:'].includes(baseURL.protocol), 'Base URL must use HTTP or HTTPS');

async function checkCallAccess(page) {
  const numbers = await page.locator('a[href^="tel:"]').evaluateAll(links =>
    links.map(link => link.getAttribute('href').replace(/\D/g, '')));
  assert(numbers.length && numbers.every(number => /^(1)?7158538513$/.test(number)), 'Incorrect phone link');
  for (const fraction of [0, 0.5, 1]) {
    await page.evaluate(value => scrollTo({top: document.body.scrollHeight * value, behavior: 'instant'}), fraction);
    // Poll the observable result rather than sleeping for a guessed animation duration.
    await page.waitForFunction(() => [...document.querySelectorAll('a[href^="tel:"]')].some(link => {
      const r = link.getBoundingClientRect();
      const s = getComputedStyle(link);
      return r.width >= 44 && r.height >= 44 && r.left >= -0.5 && r.right <= innerWidth + 0.5 &&
        r.top >= 0 && r.bottom <= innerHeight && s.visibility !== 'hidden' && s.opacity !== '0';
    }));
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      `Horizontal overflow at scroll fraction ${fraction}`);
  }
  assert(await page.locator('.phone-plate').evaluateAll(plates => plates.every(plate => {
    const r = plate.getBoundingClientRect();
    return r.left >= -0.5 && r.right <= innerWidth + 0.5 && plate.scrollWidth <= plate.clientWidth;
  })), 'Phone plate or phone text is clipped');
}

async function checkFAQs(page) {
  const details = page.locator('details');
  const count = await details.count();
  assert(count > 0, 'No FAQ disclosures found');
  for (let i = 0; i < count; i++) {
    const item = details.nth(i);
    await item.locator('summary').focus();
    await page.keyboard.press('Enter');
    assert(await item.evaluate(el => el.open), `FAQ ${i + 1} did not open with Enter`);
    await page.keyboard.press('Enter');
    assert(await item.evaluate(el => !el.open), `FAQ ${i + 1} did not close with Enter`);
  }
  return count;
}

async function checkAssets(page) {
  // Trigger native lazy loading before checking every image, including below the fold.
  await page.locator('img').evaluateAll(images => images.forEach(img => { img.loading = 'eager'; }));
  await page.waitForFunction(() => [...document.images].every(img => img.complete));
  assert.deepEqual(await page.locator('img').evaluateAll(images =>
    images.filter(img => !img.naturalWidth).map(img => img.currentSrc)), [], 'Broken images');
  // Returning document.fonts.ready can hang in Firefox with JavaScript disabled.
  // Poll load state with a bounded timer, independent of background paint frames.
  await page.waitForFunction(() => document.fonts.status === 'loaded', null, {polling: 100});
  assert.deepEqual(await page.evaluate(() => [...document.fonts].filter(font => font.status === 'error')
    .map(font => font.family)), [], 'Failed fonts');
}

async function checkNavigation(page) {
  await page.evaluate(() => scrollTo({top: 0, behavior: 'instant'}));
  const menu = page.locator('.menu-btn');
  const mobile = await menu.isVisible();
  if (mobile) {
    await menu.click();
    assert.equal(await menu.getAttribute('aria-expanded'), 'true', 'Menu did not open');
    await page.keyboard.press('Escape');
    assert.equal(await menu.getAttribute('aria-expanded'), 'false', 'Escape did not close menu');
    assert(await menu.evaluate(el => document.activeElement === el), 'Escape did not return menu focus');
    await menu.click();
  }
  const serviceLink = page.locator('#site-nav a').filter({hasText: 'Services'}).first();
  const destination = new URL(await serviceLink.getAttribute('href'), page.url()).href;
  await serviceLink.click();
  await page.waitForURL(destination);
  await page.waitForFunction(() => {
    const section = document.querySelector('#services');
    const r = section?.getBoundingClientRect();
    return r && r.top >= 0 && r.top < innerHeight && r.bottom > 0;
  });
  if (mobile) assert.equal(await page.locator('.menu-btn').getAttribute('aria-expanded'), 'false', 'Anchor did not close menu');
}

async function checkPage(browser, engine, route, width, mode) {
  const options = {viewport: {width, height: 812}};
  if (mode === 'no-js') options.javaScriptEnabled = false;
  if (mode === 'reduced-motion') options.reducedMotion = 'reduce';
  const context = await browser.newContext(options);
  const page = await context.newPage();
  page.setDefaultTimeout(30000);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  page.on('requestfailed', request => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
  page.on('response', response => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`); });
  const result = {engine, version: browser.version(), route, width, mode};
  try {
    const response = await page.goto(new URL(route, baseURL).href, {waitUntil: 'load'});
    assert.equal(response.status(), 200, 'Page response is not successful');
    await page.waitForFunction(() => document.fonts.status === 'loaded', null, {polling: 100});
    assert.equal(await page.locator('h1').count(), 1, 'Expected one main heading');
    assert(await page.locator('h1').isVisible(), 'Main heading is hidden');
    await page.keyboard.press('Tab');
    // macOS WebKit follows the system keyboard preference. With the default
    // preference, Option-Tab includes links; plain Tab only includes controls.
    // Do not change the user's global preference to run this check.
    if (engine === 'webkit' && process.platform === 'darwin' &&
        !await page.locator('.skip-link').evaluate(el => document.activeElement === el)) {
      // The first Tab can scroll to a control and trigger lazy image requests.
      // Finish them before this deliberate reload rather than hiding failures.
      await checkAssets(page);
      await page.goto(new URL(route, baseURL).href, {waitUntil: 'load'});
      await page.keyboard.press('Alt+Tab');
    }
    assert(await page.locator('.skip-link').evaluate(el => document.activeElement === el), 'Skip link is not first keyboard stop');
    await page.keyboard.press('Enter');
    await page.waitForURL(url => url.hash === '#main');
    await checkCallAccess(page);
    result.faqs = await checkFAQs(page);
    await checkAssets(page);
    if (mode === 'normal') await checkNavigation(page);
    if (mode !== 'normal') {
      assert(await page.locator('.reveal').evaluateAll(elements => elements.every(el =>
        getComputedStyle(el).opacity !== '0')), 'Fallback content is hidden');
    }
    if (mode === 'no-js') assert(!await page.evaluate(() => document.documentElement.classList.contains('js')), 'JavaScript was not disabled');
    if (mode === 'reduced-motion') {
      assert(await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches), 'Reduced motion was not applied');
      // Header state transitions may be finishing after keyboard scrolling; ongoing
      // decorative animation must stop, without guessing a fixed settling delay.
      await page.waitForFunction(() => document.getAnimations().length === 0);
    }
    assert.deepEqual(errors, [], 'Browser or asset errors');
    result.status = 'PASS';
  } catch (error) {
    result.status = 'FAIL';
    result.error = error.stack || String(error);
    result.browserErrors = errors;
    const filename = `${engine}-${route.replaceAll('/', '') || 'home'}-${width}-${mode}.png`;
    await page.screenshot({path: path.join(artifactDir, filename), fullPage: true}).catch(screenshotError => {
      result.screenshotError = String(screenshotError);
    });
  } finally {
    await context.close();
  }
  console.log(`${result.status} ${engine} ${route} ${width}px ${mode}${result.error ? `\n${result.error}` : ''}`);
  return result;
}

async function main() {
  await fs.mkdir(artifactDir, {recursive: true});
  const results = [];
  for (const engine of ENGINES) {
    const browser = await playwright[engine].launch();
    try {
      for (const width of WIDTHS) for (const route of ROUTES) {
        results.push(await checkPage(browser, engine, route, width, 'normal'));
      }
      for (const mode of ['no-js', 'reduced-motion']) for (const route of ROUTES) {
        results.push(await checkPage(browser, engine, route, 375, mode));
      }
    } finally {
      await browser.close();
    }
  }
  const report = {baseURL: baseURL.href, playwright: require('playwright/package.json').version, results};
  await fs.writeFile(path.join(artifactDir, 'results.json'), JSON.stringify(report, null, 2) + '\n');
  const failed = results.filter(result => result.status === 'FAIL');
  console.log(`${results.length - failed.length}/${results.length} browser cases passed. Report: ${artifactDir}`);
  if (failed.length) process.exitCode = 1;
}

main().catch(error => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
