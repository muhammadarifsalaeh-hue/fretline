from pathlib import Path
import argparse
from playwright.sync_api import sync_playwright,expect
import json
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:5456');args=parser.parse_args();BASE=args.url.rstrip('/');report={'physicalIPadSafariTested':False,'engine':'Chromium CDP trusted touch input on Linux','errors':[]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=b.new_context(viewport={'width':768,'height':1024},has_touch=True,reduced_motion='no-preference');page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.goto(BASE,wait_until='networkidle');rail=page.locator('[data-marquee-viewport]');rail.evaluate('(e)=>e.scrollIntoView({block:"center"})');page.wait_for_timeout(200);bounds=rail.bounding_box();w=page.locator('[data-marquee-primary]').evaluate('(e)=>e.getBoundingClientRect().width');x1=rail.evaluate('(e)=>e.scrollLeft');cdp=context.new_cdp_session(page);y=bounds['y']+55;left=bounds['x']+bounds['width']*.8;assert page.evaluate('([x,y])=>Boolean(document.elementFromPoint(x,y)?.closest("[data-marquee-viewport]"))',[left,y]);right=bounds['x']+bounds['width']*.25
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':left,'y':y}]})
 for i in range(1,13):
  cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':left+(right-left)*i/12,'y':y}]});page.wait_for_timeout(24)
 page.wait_for_timeout(350);held1=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(1600);held2=rail.evaluate('(e)=>e.scrollLeft');assert abs(held2-held1)<=1,(held1,held2);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});page.wait_for_timeout(100);x2=rail.evaluate('(e)=>e.scrollLeft');delta=(x2-x1)%w;assert delta>250,(x1,x2,delta);assert page.url==BASE+'/'
 page.wait_for_timeout(3300);expect(rail).to_have_attribute('data-marquee-motion','auto');x3=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(750);x4=rail.evaluate('(e)=>e.scrollLeft');resume=(x4-x3)%w;assert 15<resume<30,(x3,x4,resume);assert page.evaluate('document.documentElement.scrollWidth')==768
 report.update({'nativeTouchSwipePixels':delta,'heldFingerStopsAutoMovement1600ms':True,'autoResumedPixelsOver750ms':resume,'swipeDidNotNavigate':True,'noHorizontalPageOverflow':True,'passed':not report['errors']});context.close();b.close()
Path(__file__).resolve().parent.joinpath('brand-dev-touch.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
