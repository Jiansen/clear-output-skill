// Usage: node evals/browser/check-interactive.mjs HTML_FILE OUTPUT_DIRECTORY
// Install the optional dependencies in this directory first. Requires Chrome.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright-core';

const html = path.resolve(process.argv[2] || 'examples/retry-backoff.html');
const output = path.resolve(process.argv[3] || 'evals/local/interactive');
await fs.mkdir(output, {recursive: true});
const browser = await chromium.launch(process.env.CLEAR_OUTPUT_BROWSER
  ? {headless: true, executablePath: process.env.CLEAR_OUTPUT_BROWSER}
  : {headless: true, channel: 'chrome'});
const report = {browser: browser.version(), playwright: '1.65.0', states: [], page_errors: [], network_attempts: []};
try {
  const page = await browser.newPage({viewport: {width: 1280, height: 950}, reducedMotion: 'reduce'});
  page.on('pageerror', error => report.page_errors.push(error.message));
  await page.route(/^https?:\/\//, route => {
    report.network_attempts.push(route.request().url());
    return route.abort();
  });
  await page.goto(pathToFileURL(html).href);
  const base = page.getByLabel('Base delay', {exact: true});
  const retries = page.getByLabel('Retries', {exact: true});
  assert.equal(await page.locator('html').getAttribute('lang'), 'en');
  assert.equal(await base.inputValue(), '1');
  assert.equal(await retries.inputValue(), '3');
  assert.equal(await page.locator('#total-wait').innerText(), '7');
  assert.equal(await page.locator('#total-attempts').innerText(), '4');
  await page.screenshot({path: path.join(output, 'desktop-default.png'), fullPage: true});

  // Independent closed-form oracle; verify DOM values, not the artifact's helper.
  for (let step = 0; step < 6; step += 1) {
    await base.press('Home');
    for (let n = 0; n < step; n += 1) await base.press('ArrowRight');
    const delay = 0.5 + step * 0.5;
    assert.equal(Number(await base.inputValue()), delay);
    for (let count = 0; count <= 5; count += 1) {
      await retries.press('Home');
      for (let n = 0; n < count; n += 1) await retries.press('ArrowRight');
      const total = delay * (2 ** count - 1);
      assert.equal(Number(await page.locator('#total-wait').innerText()), total);
      assert.equal(Number(await page.locator('#total-attempts').innerText()), count + 1);
      const actualWaits = await page.locator('#wait-rows .wait-number').allTextContents();
      assert.deepEqual(actualWaits.map(Number.parseFloat), Array.from({length: count}, (_, k) => delay * 2 ** k));
      const actualCumulative = await page.locator('#wait-rows tr td:last-child').allTextContents();
      assert.deepEqual(actualCumulative.map(Number.parseFloat), Array.from({length: count}, (_, k) => delay * (2 ** (k + 1) - 1)));
      assert.equal(await page.locator('#empty-state').isVisible(), count === 0);
      report.states.push({base_delay: delay, retries: count, total_wait: total, total_attempts: count + 1, passed: true});
    }
  }
  await page.screenshot({path: path.join(output, 'desktop-maximum.png'), fullPage: true});

  await base.focus();
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'retry-count');
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'reset');
  await page.keyboard.press('Enter');
  assert.equal(await page.locator('#total-wait').innerText(), '7');
  report.keyboard_navigation_and_reset = true;

  await base.press('Home');
  const box = await base.boundingBox();
  await page.mouse.click(box.x + box.width * 0.75, box.y + box.height / 2);
  const mouseValue = Number(await base.inputValue());
  assert.ok(mouseValue > 0.5);
  assert.equal(Number(await page.locator('#total-wait').innerText()), mouseValue * 7);
  report.mouse_control_updates_output = true;

  await page.getByRole('button', {name: 'Reset to 1 s · 3 retries'}).click();
  await page.setViewportSize({width: 390, height: 844});
  const fits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
  assert.ok(fits, 'Mobile page overflows horizontally');
  await page.screenshot({path: path.join(output, 'mobile-default.png'), fullPage: true});
  report.mobile_no_horizontal_overflow = true;
  assert.deepEqual(report.page_errors, []);
  assert.deepEqual(report.network_attempts, []);
  report.ok = true;
} catch (error) {
  report.ok = false;
  report.failure = error.message;
} finally {
  await browser.close();
}
await fs.writeFile(path.join(output, 'interactive-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({...report, states: `${report.states.length} parameter combinations checked`}, null, 2));
if (!report.ok) process.exitCode = 1;
