import {chromium} from 'playwright';
import fs from 'node:fs';
const errors=[];
const browser=await chromium.launch({executablePath:'/home/dev/.local/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8776/',{waitUntil:'networkidle'});
await page.waitForTimeout(2000);
await page.screenshot({path:'tests/desktop.png',fullPage:true});
const desktopOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
await page.getByRole('tab',{name:'Reference',exact:true}).click();await page.waitForTimeout(500);
const referenceLoaded=await page.locator('#hero').evaluate(i=>i.complete&&i.naturalWidth>0);
await page.getByRole('tab',{name:'Eevee render',exact:true}).click();
const status=await page.evaluate(async()=>await(await fetch('status.json')).json());
let webgl=null;
if(status.files?.glb){
 await page.getByRole('tab',{name:'Orbit 3D',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#three canvas')&&!document.querySelector('#empty').checkVisibility(),{},{timeout:120000});
 await page.waitForTimeout(2000);await page.screenshot({path:'tests/orbit.png',fullPage:false,timeout:120000});
 webgl=await page.locator('#three canvas').evaluate(c=>({width:c.width,height:c.height}));
 await page.getByRole('button',{name:'Auto-rotate',exact:true}).click();await page.waitForTimeout(500);await page.getByRole('button',{name:'Stop rotation',exact:true}).click();
 await page.getByRole('button',{name:'Reset view',exact:true}).click();
}
await page.setViewportSize({width:390,height:844});await page.getByRole('tab',{name:'Eevee render',exact:true}).click();await page.waitForTimeout(500);await page.screenshot({path:'tests/mobile.png',fullPage:true});
const mobileOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
const report={desktopOverflow,mobileOverflow,referenceLoaded,webgl,errors,checked:new Date().toISOString()};fs.writeFileSync('tests/browser-report.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
if(errors.length||desktopOverflow||mobileOverflow||!referenceLoaded)process.exitCode=1;
