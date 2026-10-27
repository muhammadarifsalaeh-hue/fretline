"""Diagnose native wheel completion without crediting later autoplay pixels."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json

OUT=Path(__file__).resolve().parent/'webkit-wheel-trace.json'
report=[]
with sync_playwright() as p:
 b=p.webkit.launch()
 for label,w,h in [('desktop',1440,1000),('tablet',768,1024),('mobile',390,844)]:
  c=b.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion='no-preference');page=c.new_page();page.goto('http://127.0.0.1:5451/',wait_until='networkidle');page.evaluate('document.fonts.ready')
  rail=page.locator('[data-marquee-viewport]');rail.evaluate('(e)=>e.scrollIntoView({block:"center"})');page.wait_for_timeout(200);expect(rail).to_have_attribute('data-marquee-motion','auto');rb=rail.bounding_box();x=rb['x']+min(rb['width']*.7,500);y=rb['y']+rb['height']/2
  page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-125,y,steps=12);page.mouse.up();page.wait_for_timeout(1800);expect(rail).to_have_attribute('data-marquee-motion','auto')
  page.mouse.move(x,y)
  rail.evaluate('''e=>{window.__wheelTrace=[];const read=kind=>__wheelTrace.push({kind,t:performance.now(),left:e.scrollLeft,mode:e.dataset.marqueeMotion});window.__wheelRead=read;e.addEventListener('wheel',()=>read('wheel'),{passive:true});e.addEventListener('scroll',()=>read('scroll'),{passive:true});read('before');}''')
  page.mouse.wheel(180,0)
  for i in range(12):
   page.wait_for_timeout(150);rail.evaluate('(e)=>__wheelRead("sample")')
  rows=page.evaluate('__wheelTrace');report.append({'viewport':label,'samples':rows});print(label,rows[0],rows[-1],flush=True);c.close()
 b.close()
OUT.write_text(json.dumps(report,indent=2)+'\n')
