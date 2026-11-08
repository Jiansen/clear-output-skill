// Rebuild the editorial images and verify the working preview.
// npm ci --prefix evals/browser --ignore-scripts
// node evals/browser/render-showcase.mjs
// Requires Chrome and ffmpeg. Uses no network resources while rendering.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {chromium} from 'playwright-core';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const assetRoot=path.join(root,'assets/showcase');
const source=path.join(assetRoot,'showcase.html');
const temporary=await fs.mkdtemp(path.join(os.tmpdir(),'clear-output-showcase-'));
const browser=await chromium.launch(process.env.CLEAR_OUTPUT_BROWSER
  ? {headless:true,executablePath:process.env.CLEAR_OUTPUT_BROWSER}
  : {headless:true,channel:'chrome'});
const report={
  kind:'editorial-showcase-render-checks',
  date:new Date().toISOString().slice(0,10),
  disclosure:'Illustrative before/after compositions, not raw model outputs or evidence of a measured skill advantage.',
  browser:browser.version(),
  source_sha256:createHash('sha256').update(await fs.readFile(source)).digest('hex'),
  images:[], animations:[], interaction_states:[], page_errors:[], network_attempts:[]
};
const dimensions={landscape:{width:1600,height:1000},portrait:{width:1080,height:1350}};
const page=await browser.newPage({deviceScaleFactor:1,reducedMotion:'reduce'});
page.on('pageerror',error=>report.page_errors.push(error.message));
await page.route(/^https?:\/\//,route=>{
  report.network_attempts.push(route.request().url());
  return route.abort();
});
async function open(language,example,format='landscape',exportMode=true) {
  await page.setViewportSize(dimensions[format]);
  const url=pathToFileURL(source);
  url.search=new URLSearchParams({lang:language,case:example,format,export:exportMode?'1':'0'}).toString();
  await page.goto(url.href);
  await page.evaluate(()=>document.fonts.ready);
  assert.equal(await page.locator('html').getAttribute('lang'),language==='zh'?'zh-CN':'en');
}
async function checkLayout() {
  const problems=await page.evaluate(()=>{
    const issues=[];
    const poster=document.querySelector('.poster').getBoundingClientRect();
    for(const el of document.querySelectorAll('.poster .panel,.poster header,.poster footer,.poster .brand-row')) {
      const b=el.getBoundingClientRect();
      if(b.left<poster.left-1||b.top<poster.top-1||b.right>poster.right+1||b.bottom>poster.bottom+1) issues.push(`${el.className||el.tagName}: outside poster`);
      if(el.scrollHeight>el.clientHeight+2||el.scrollWidth>el.clientWidth+2) issues.push(`${el.className||el.tagName}: content overflow`);
    }
    // Text nodes can overflow without changing a fixed SVG view box.
    for(const text of document.querySelectorAll('svg text')) {
      const box=text.getBBox(), view=text.ownerSVGElement.viewBox.baseVal;
      if(box.x<view.x||box.y<view.y||box.x+box.width>view.width||box.y+box.height>view.height) issues.push(`SVG label clipped: ${text.textContent}`);
    }
    const panels=[...document.querySelectorAll('.panel')].map(el=>el.getBoundingClientRect());
    if(panels[0].bottom>panels[1].top+2 && panels[0].right>panels[1].left+2) issues.push('Comparison panels overlap');
    return issues;
  });
  assert.deepEqual(problems,[]);
}
async function setState(base,retries) {
  const baseInput=page.locator('#base'), retryInput=page.locator('#retries');
  await baseInput.press('Home');
  for(let i=0;i<(base-0.5)/0.5;i++) await baseInput.press('ArrowRight');
  await retryInput.press('Home');
  for(let i=0;i<retries;i++) await retryInput.press('ArrowRight');
  assert.equal(Number(await baseInput.inputValue()),base);
  assert.equal(Number(await retryInput.inputValue()),retries);
  assert.equal(Number(await page.locator('#total').innerText()),base*(2**retries-1));
  assert.equal(Number(await page.locator('#attempts').innerText()),retries+1);
  assert.deepEqual((await page.locator('.bar-row .value').allTextContents()).map(parseFloat),Array.from({length:retries},(_,k)=>base*2**k));
  assert.equal(await page.locator('.zero').count(),retries===0?1:0);
}
try {
  for(const language of ['en','zh']) {
    for(const example of ['release','debugging','retry']) {
      for(const format of ['landscape','portrait']) {
        await open(language,example,format);
        await checkLayout();
        const file=`${example}-${language}-${format}.png`;
        await page.locator('.poster').screenshot({path:path.join(assetRoot,file),animations:'disabled'});
        report.images.push({file,...dimensions[format],layout:'passed'});
      }
    }
    await open(language,'retry');
    for(let step=0;step<6;step++) {
      for(let retries=0;retries<=5;retries++) {
        const base=0.5+step*0.5;
        await setState(base,retries);
        await checkLayout();
        report.interaction_states.push({language,base_delay_s:base,retries,total_wait_s:base*(2**retries-1),attempts:retries+1,passed:true});
      }
    }
    // Check the maximum-row layout in the narrower export as well.
    await open(language,'retry','portrait');
    await setState(3,5);
    await checkLayout();

    await open(language,'retry');
    await page.locator('#base').focus();
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(()=>document.activeElement.id),'retries');
    await page.locator('#base').press('Home');
    const box=await page.locator('#base').boundingBox();
    await page.mouse.click(box.x+box.width*.75,box.y+box.height/2);
    const mouseBase=Number(await page.locator('#base').inputValue());
    assert.ok(mouseBase>0.5);
    assert.equal(Number(await page.locator('#total').innerText()),mouseBase*7);
    report.keyboard_and_mouse_controls=true;

    const frameDir=path.join(temporary,language);
    await fs.mkdir(frameDir);
    const states=[[1,3],[2,3],[2,4],[2,0],[1,3]];
    for(const [i,[base,retries]] of states.entries()) {
      await setState(base,retries);
      await page.locator('#retries').blur();
      await page.locator('.poster').screenshot({path:path.join(frameDir,`frame-${i}.png`),animations:'disabled'});
    }
    const file=`retry-${language}.gif`;
    execFileSync('ffmpeg',['-y','-loglevel','error','-framerate','1/2','-i',path.join(frameDir,'frame-%d.png'),'-filter_complex','fps=1/2,scale=1200:-1:flags=lanczos,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0',path.join(assetRoot,file)]);
    report.animations.push({file,width:1200,height:750,seconds:10,source:'Actual rendered page states changed through keyboard controls; screenshots assembled into GIF.',states:states.map(([base,retries])=>({base_delay_s:base,retries,total_wait_s:base*(2**retries-1)}))});
  }
  await open('en','release','landscape',false);
  await page.setViewportSize({width:390,height:844});
  await page.locator('#language').selectOption('zh');
  await page.locator('#case').selectOption('retry');
  await page.locator('#format').selectOption('portrait');
  assert.equal(await page.locator('h1').innerText(),'多重试一次，会多等多久？');
  await setState(1,3);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile preview overflows horizontally');
  report.preview_navigation_and_mobile_fit=true;
  assert.deepEqual(report.page_errors,[]);
  assert.deepEqual(report.network_attempts,[]);
  report.ok=true;
} catch(error) {
  report.ok=false;
  report.failure=error.stack;
} finally {
  await browser.close();
  await fs.rm(temporary,{recursive:true,force:true});
}
await fs.writeFile(path.join(assetRoot,'render-checks.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,interaction_states:`${report.interaction_states.length} parameter states checked`},null,2));
if(!report.ok) process.exitCode=1;
