// Render compact README cards from code and verify their content and interaction.
// npm ci --prefix evals/browser --ignore-scripts
// node evals/browser/render-readme-examples.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {chromium} from 'playwright-core';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const assets=path.join(root,'assets/readme');
const source=path.join(assets,'examples.html');
const legacy=path.join(root,'assets/showcase/showcase.html');
const temporary=await fs.mkdtemp(path.join(os.tmpdir(),'clear-output-readme-'));
const browser=await chromium.launch(process.env.CLEAR_OUTPUT_BROWSER
 ? {headless:true,executablePath:process.env.CLEAR_OUTPUT_BROWSER}
 : {headless:true,channel:'chrome'});
const page=await browser.newPage({viewport:{width:1000,height:1100},deviceScaleFactor:2,reducedMotion:'reduce'});
const report={kind:'readme-example-render-checks',date:new Date().toISOString().slice(0,10),browser:browser.version(),
 disclosure:'Authored presentation examples, not a measured model A/B test. The first three scenarios are fictional.',
 source_sha256:createHash('sha256').update(await fs.readFile(source)).digest('hex'),
 original_showcase_sha256:createHash('sha256').update(await fs.readFile(legacy)).digest('hex'),
 preserved_original_examples:[],images:[],animations:[],interaction_states:[],page_errors:[],network_attempts:[]};
page.on('pageerror',error=>report.page_errors.push(error.message));
await page.route(/^https?:\/\//,route=>{report.network_attempts.push(route.request().url());return route.abort();});

async function open(language,exportMode=true) {
 const url=pathToFileURL(source);url.search=new URLSearchParams({lang:language,export:exportMode?'1':'0'}).toString();
 await page.goto(url.href);await page.evaluate(()=>document.fonts.ready);
 assert.equal(await page.locator('html').getAttribute('lang'),language==='zh'?'zh-CN':'en');
}
async function layout() {
 const problems=await page.evaluate(()=>{
  const errors=[];
  for(const card of document.querySelectorAll('.card')) {
   const outer=card.getBoundingClientRect();
   for(const el of card.querySelectorAll('h2,.before,.after,.source,table,.evidence,.explorer,.survey-stat,.flow')) {
    const b=el.getBoundingClientRect();
    if(b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1)errors.push(card.id+': '+el.className+' outside card');
    if(el.scrollWidth>el.clientWidth+2||el.scrollHeight>el.clientHeight+2)errors.push(card.id+': '+el.className+' content overflow');
   }
  }
  for(const el of document.querySelectorAll('svg text')) {
   const b=el.getBBox(),v=el.ownerSVGElement.viewBox.baseVal;
   if(b.x<v.x||b.y<v.y||b.x+b.width>v.width||b.y+b.height>v.height)errors.push('Clipped SVG text: '+el.textContent);
  }
  return errors;
 });
 assert.deepEqual(problems,[]);
}
async function setRetry(base,retries) {
 await page.locator('#base').fill(String(base));
 await page.locator('#retries').fill(String(retries));
 assert.equal(Number(await page.locator('#total').innerText()),base*(2**retries-1));
 assert.equal(Number(await page.locator('#attempts').innerText()),retries+1);
 assert.deepEqual((await page.locator('.bar-row .value').allTextContents()).map(parseFloat),Array.from({length:retries},(_,i)=>base*2**i));
 assert.equal(await page.locator('.zero').count(),retries===0?1:0);
}
try {
 await page.goto(pathToFileURL(legacy).href);
 const original=await page.evaluate(()=>COPY);
 for(const language of ['en','zh']) {
  await open(language);
  const current=await page.evaluate(()=>COPY);
  for(const name of ['release','debugging','retry']) {
   const item=current[language].cases.find(item=>item.id===name);
   for(const field of ['title','before','form'])assert.equal(item[field],original[language].cases[name][field]);
   report.preserved_original_examples.push({language,example:name,title_source_and_form_unchanged:true});
  }
  assert.deepEqual(current[language].flow,original[language].flow);
  assert.deepEqual(current[language].evidence,original[language].evidence);
  for(const [key,value]of Object.entries(current[language].retry))assert.equal(value,original[language].retry[key]);

  // Independent checks against the fictional briefs and the existing release rule.
  assert.deepEqual(await page.locator('#choices tbody td').allTextContents(),['US$60','US$40',current[language].choice.two,current[language].choice.three,'0','1']);
  assert.deepEqual(await page.locator('#meeting tbody td:first-child').allTextContents(),['Maya','Leo']);
  assert.equal(await page.locator('#meeting tbody tr:nth-child(2) td:last-child').innerText(),current[language].meeting.confirmed);
  assert.equal(await page.locator('#reading .dot').count(),30);
  assert.equal(await page.locator('#reading .dot.filled').count(),18);
  assert.ok((await page.locator('#reading .survey-caption').innerText()).includes((18/30*100)+'%'));
  assert.deepEqual(await page.locator('[data-edge]').evaluateAll(elements=>elements.map(e=>e.dataset.edge).sort()),
   ['build-tests','build-scan','tests-pass-join','scan-pass-join','tests-fail-stop','scan-fail-stop','join-deploy'].sort());
  await layout();
  for(const name of ['choices','meeting','reading','release','debugging','retry']) {
   const card=page.locator('#'+name),box=await card.boundingBox();
   const file=`${name}-${language}.png`;
   await card.screenshot({path:path.join(assets,file),animations:'disabled'});
   report.images.push({file,css_width:box.width,css_height:box.height,device_scale:2,layout:'passed'});
  }
  for(let i=1;i<=6;i++)for(let retries=0;retries<=5;retries++) {
   await setRetry(i/2,retries);await layout();
   report.interaction_states.push({language,base_delay_s:i/2,retries,total_wait_s:i/2*(2**retries-1),attempts:retries+1});
  }
  await page.locator('#base').focus();await page.keyboard.press('Home');await page.keyboard.press('ArrowRight');
  assert.equal(Number(await page.locator('#base').inputValue()),1);
  await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'retries');
  await page.keyboard.press('Home');await page.keyboard.press('ArrowRight');
  assert.equal(Number(await page.locator('#total').innerText()),1);
  const frames=path.join(temporary,language);await fs.mkdir(frames);
  const states=[[1,3],[2,3],[2,4],[2,0],[1,3]];
  const sizes=[];
  for(const [index,[base,retries]]of states.entries()) {
   await setRetry(base,retries);await page.locator('#retries').blur();
   const box=await page.locator('#retry').boundingBox();sizes.push(Math.ceil(box.height));
   await page.locator('#retry').screenshot({path:path.join(frames,`frame-${index}.png`),animations:'disabled'});
  }
  assert.equal(new Set(sizes).size,1,'GIF frames must have a stable layout');
  const file=`retry-${language}.gif`;
  execFileSync('ffmpeg',['-y','-loglevel','error','-framerate','1/2','-i',path.join(frames,'frame-%d.png'),'-filter_complex','fps=1/2,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0',path.join(assets,file)]);
  report.animations.push({file,seconds:10,states,source:'Actual HTML states captured after changing real controls; playback speed is not retry timing.'});
 }
 await open('en',false);await page.setViewportSize({width:390,height:844});
 await page.locator('#language').selectOption('zh');await layout();await setRetry(3,5);await layout();
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile page has horizontal overflow');
 assert.equal(await page.locator('.card').count(),6);
 report.responsive_html_and_language_switch=true;
 assert.deepEqual(report.page_errors,[]);assert.deepEqual(report.network_attempts,[]);
 report.ok=true;
} catch(error) {report.ok=false;report.failure=error.stack;}
finally {await browser.close();await fs.rm(temporary,{recursive:true,force:true});}
await fs.writeFile(path.join(assets,'render-checks.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,interaction_states:report.interaction_states.length+' states checked'},null,2));
if(!report.ok)process.exitCode=1;
