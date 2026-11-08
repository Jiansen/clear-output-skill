// Run after building and serving dist/site: node evals/browser/check-site.mjs [URL]
import {chromium} from 'playwright-core';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
const url=process.argv[2]||'http://127.0.0.1:8766/';
const output=path.resolve('dist/site-checks');await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-http2']});
const report={url,layouts:[],clipboard:[],errors:[],externalRequests:[]};
try{
 const context=await browser.newContext({viewport:{width:1200,height:900},reducedMotion:'reduce'});
 await context.grantPermissions(['clipboard-read','clipboard-write'],{origin:new URL(url).origin});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
 page.on('request',r=>{if(new URL(r.url()).origin!==new URL(url).origin)report.externalRequests.push(r.url());});
 for(const language of ['en','zh']){
  await page.goto(url+'?lang='+language,{waitUntil:'domcontentloaded'});
  assert.equal(await page.locator('html').getAttribute('lang'),language==='zh'?'zh-CN':'en');
  assert.equal(await page.locator('h1').count(),1);
  assert.equal(await page.locator('.card').count(),6);
  assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'),'https://jiansen.github.io/clear-output-skill/');
  for(const [base,n,total,attempts] of [[1,3,7,4],[2,4,30,5],[3,0,0,1]]){
   await page.locator('#base').fill(String(base));await page.locator('#retries').fill(String(n));
   assert.equal(await page.locator('#total').innerText(),String(total));
   assert.equal(await page.locator('#attempts').innerText(),String(attempts));
  }
  await page.locator('#copy-install').click();
  assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),'npx skills add Jiansen/clear-output-skill --skill clear-output');
  for(const agent of ['codex','claude-code','cursor']){
   await page.locator('#prompt-agent').selectOption(agent);await page.locator('#copy-prompt').click();
   const prompt=await page.evaluate(()=>navigator.clipboard.readText());
   assert.ok(prompt.startsWith(agent==='codex'?'$clear-output ':'/clear-output '));
   assert.ok(prompt.includes(language==='zh'?'预算仍未确定':'budget is still undecided'));
   report.clipboard.push({language,agent,passed:true});
  }
  for(const width of [1200,390,320]){
   await page.setViewportSize({width,height:900});await page.evaluate(()=>scrollTo(0,0));
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal overflow at '+width);
   const invalid=await page.locator('a[href^="#"]').evaluateAll(links=>links.filter(a=>!document.getElementById(a.getAttribute('href').slice(1))).map(a=>a.href));
   assert.deepEqual(invalid,[]);
   await page.screenshot({path:path.join(output,language+'-'+width+'.png')});
   report.layouts.push({language,width,passed:true});
  }
 }
 await page.locator('#language').selectOption('en');assert.equal(await page.locator('html').getAttribute('lang'),'en');
 assert.equal(new URL(page.url()).searchParams.get('lang'),'en');
 await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{value:{writeText:async()=>{throw new Error('Clipboard denied');}}}));
 await page.locator('#copy-install').click();assert.match(await page.locator('#copy-status').innerText(),/Select and copy/);
 report.clipboardFallback=true;assert.deepEqual(report.errors,[]);assert.deepEqual(report.externalRequests,[]);report.ok=true;
}catch(error){report.ok=false;report.error=error.stack;process.exitCode=1;}
finally{await browser.close();}
await fs.writeFile(path.join(output,'checks.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
