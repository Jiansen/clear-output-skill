// Usage: node evals/browser/render-diagrams.mjs REPOSITORY OUTPUT_DIRECTORY
// Install the optional dependencies in this directory first. Requires Chrome.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {chromium} from 'playwright-core';

const require = createRequire(import.meta.url);
const repo = path.resolve(process.argv[2] || '.');
const output = path.resolve(process.argv[3] || 'evals/local/diagrams');
await fs.mkdir(output, {recursive: true});
const browser = await chromium.launch(process.env.CLEAR_OUTPUT_BROWSER
  ? {headless: true, executablePath: process.env.CLEAR_OUTPUT_BROWSER}
  : {headless: true, channel: 'chrome'});
const report = {browser: browser.version(), mermaid: '12.3.0', theme: 'neutral', plot_palette: '#087b65', diagrams: []};

try {
  for (const condition of ['previous', 'current']) {
    const data = JSON.parse(await fs.readFile(path.join(repo, 'evals/forms', condition + '.json'), 'utf8'));
    for (const row of data.responses) {
      let index = 0;
      for (const match of row.response.matchAll(/```mermaid\s*\n([\s\S]*?)```/g)) {
        index += 1;
        const name = `${condition}-${row.id}-${index}`;
        const page = await browser.newPage({viewport: {width: 1280, height: 900}, deviceScaleFactor: 1});
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        await page.route(/^https?:\/\//, route => route.abort());
        await page.setContent('<html><body style="margin:0;padding:24px;background:white"></body></html>');
        const mermaidPath = path.join(path.dirname(require.resolve('mermaid')), 'mermaid.min.js');
        await page.addScriptTag({path: mermaidPath});
        try {
          const svg = await page.evaluate(async source => {
            mermaid.initialize({startOnLoad: false, securityLevel: 'strict', theme: 'neutral', fontFamily: 'Arial, PingFang SC, sans-serif', themeVariables: {xyChart: {plotColorPalette: '#087b65'}}});
            const result = await mermaid.render('diagram', source);
            document.body.innerHTML = result.svg;
            return result.svg;
          }, match[1]);
          await fs.writeFile(path.join(output, name + '.svg'), svg);
          const box = await page.locator('svg').boundingBox();
          if (!box || box.width < 1 || box.height < 1) throw new Error('No visible diagram');
          await page.locator('svg').screenshot({path: path.join(output, name + '.png')});
          report.diagrams.push({condition, case_id: row.id, index, rendered: true, width: box.width, height: box.height, errors});
        } catch (error) {
          report.diagrams.push({condition, case_id: row.id, index, rendered: false, error: error.message, errors});
        }
        await page.close();
      }
    }
  }
} finally {
  await browser.close();
}
report.ok = report.diagrams.length > 0 && report.diagrams.every(item => item.rendered && item.errors.length === 0);
await fs.writeFile(path.join(output, 'render-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
if (!report.ok) process.exitCode = 1;
