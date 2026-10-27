from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,time,argparse
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:5456');args=parser.parse_args();BASE=args.url.rstrip('/');OUT=Path(__file__).resolve().parent;report={'checks':[],'errors':[],'note':'Focused development-source probe, not physical iPad Safari certification.'}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference');page=c.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
 page.goto(BASE,wait_until='networkidle');rail=page.locator('[data-marquee-viewport]');rail.scroll_into_view_if_needed();page.wait_for_timeout(200)
 assert page.locator('#brands button').count()==0
 assert page.locator('[data-marquee-primary] a').count()==10
 assert page.locator('[data-marquee-clone]').count()==2
 x1=rail.evaluate('(e)=>e.scrollLeft');t=time.monotonic();page.wait_for_timeout(1100);x2=rail.evaluate('(e)=>e.scrollLeft');elapsed=time.monotonic()-t;speed=(x2-x1)/elapsed;assert 20<speed<35,(x1,x2,speed)
 report['checks'].append({'autoSpeedPxPerSecond':speed,'noControlButtons':True,'tenAccessibleBrands':True})
 box=rail.bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+55);before=rail.evaluate('(e)=>e.scrollLeft');page.mouse.down();page.mouse.move(box['x']+box['width']/2-180,box['y']+55,steps=15);page.mouse.up();after=rail.evaluate('(e)=>e.scrollLeft');assert after-before>160,(before,after);assert page.url==BASE+'/'
 page.wait_for_timeout(2100);a=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(700);z=rail.evaluate('(e)=>e.scrollLeft');assert z-a>15,(a,z);report['checks'].append({'mouseDragPixels':after-before,'autoResumedPixels':z-a,'dragDidNotNavigate':True})
 width=page.locator('[data-marquee-primary]').evaluate('(e)=>e.getBoundingClientRect().width');rail.evaluate('(e,w)=>{e.scrollLeft=2*w-3}',width);page.wait_for_timeout(900)
 samples=rail.evaluate('''e=>new Promise(resolve=>{let out=[],n=0;function f(t){out.push({t,x:e.scrollLeft});if(++n<120)requestAnimationFrame(f);else resolve(out)}requestAnimationFrame(f)})''');jumps=[(a,b) for a,b in zip(samples,samples[1:]) if b['x']<a['x']-width/2];assert jumps,samples[-3:]
 phases=[((b['x']-a['x'])%width) for a,b in zip(samples,samples[1:])];assert max(phases)<3, max(phases);report['checks'].append({'wrapsObserved':len(jumps),'maxVisualFrameDelta':max(phases),'groupWidth':width})
 link=page.locator('[data-marquee-primary] a').first;page.keyboard.press('Tab');link.focus();expect(rail).to_have_attribute('data-marquee-motion','keyboard');f=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(250);assert abs(rail.evaluate('(e)=>e.scrollLeft')-f)<=1;page.keyboard.press('Enter');expect(page).to_have_url(BASE+'/guitars?brand=Yamaha');report['checks'].append({'keyboardFocusStopsMovementAndNavigatesBrand':True})
 c.close()
 c=b.new_context(viewport={'width':390,'height':844},has_touch=True,reduced_motion='reduce');page=c.new_page();page.goto(BASE,wait_until='networkidle');rail=page.locator('[data-marquee-viewport]');rail.scroll_into_view_if_needed();expect(rail).to_have_attribute('data-marquee-motion','reduced');assert page.locator('[data-marquee-clone]').first.is_hidden();x=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(500);assert rail.evaluate('(e)=>e.scrollLeft')==x;rail.evaluate('(e)=>e.scrollLeft=700');page.wait_for_timeout(100);assert rail.evaluate('(e)=>e.scrollLeft')==700;report['checks'].append({'reducedMotionNoAutoMovement':True,'uniqueVisibleRow':True,'manualScrollAvailable':True});c.close();b.close()
report['passed']=len(report['checks'])==5 and not report['errors'];(OUT/'brand-dev-probe.json').write_text(json.dumps(report,indent=2));print(report);assert report['passed']
