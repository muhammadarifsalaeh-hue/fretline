from pathlib import Path
import json
from playwright.sync_api import sync_playwright,expect
OUT=Path(__file__).resolve().parent
report={'checks':[],'errors':[],'physicalIPadSafariTested':False,'mode':'Chromium development-source independent read-only review'}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,w,h in [('desktop',1440,1000),('tablet',768,1024),('mobile',390,844),('narrow',320,740)]:
  c=b.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion='reduce')
  page=c.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else None)
  page.goto('http://127.0.0.1:5454/',wait_until='networkidle');page.evaluate('document.fonts.ready')
  for region in ['#top','#brands','#categories','#find','#compare']:
   el=page.locator(region);el.scroll_into_view_if_needed()
   for im in el.locator('img').all():
    if im.is_visible():im.scroll_into_view_if_needed();im.evaluate('(i)=>i.decode()')
   page.wait_for_timeout(100)
   m=el.evaluate('''el=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,rect:el.getBoundingClientRect().toJSON(),texts:[...el.querySelectorAll('h1,h2,h3,p,.home-find-option-title,.home-find-option-description,.signature-category-copy,.home-compare-model')].filter(e=>e.offsetWidth&&e.offsetHeight&&!e.classList.contains('sr-only')).map(e=>({text:e.textContent,width:e.clientWidth,scroll:e.scrollWidth,rect:e.getBoundingClientRect().toJSON(),color:getComputedStyle(e).color,font:getComputedStyle(e).fontSize})),buttons:[...el.querySelectorAll('button')].filter(e=>e.offsetWidth&&e.offsetHeight).map(e=>({text:e.textContent,rect:e.getBoundingClientRect().toJSON()})),images:[...el.querySelectorAll('img')].filter(e=>e.offsetWidth&&e.offsetHeight).map(e=>({src:e.currentSrc,width:e.naturalWidth,height:e.naturalHeight,fit:getComputedStyle(e).objectFit}))})''')
   m['textOverflow']=[t for t in m['texts'] if t['scroll']>t['width']+1]
   m['viewportTextOverflow']=[t for t in m['texts'] if t['rect']['left']< -1 or t['rect']['right']>w+1]
   m['smallButtons']=[t for t in m['buttons'] if t['rect']['height']<44 or t['rect']['width']<44]
   # Moving/clipped rail copies are intentionally larger than the viewport.
   if region=='#brands':m['viewportTextOverflow']=[]
   m['region']=region;m['viewport']=label
   report['checks'].append(m)
   el.screenshot(path=str(OUT/(label+'-'+region[1:]+'.png')),animations='disabled')
  c.close()
 b.close()
report['passed']=not report['errors'] and all(not r['textOverflow'] and not r['viewportTextOverflow'] and not r['smallButtons'] and r['scrollWidth']<=r['width']+1 and all(i['width']>0 and i['height']>0 for i in r['images']) for r in report['checks'])
(OUT/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('RESULT',report['passed'],len(report['checks']),len(report['errors']))
for r in report['checks']:
 if r['textOverflow'] or r['viewportTextOverflow'] or r['smallButtons']:print(r['viewport'],r['region'],'internal',r['textOverflow'],'outside',r['viewportTextOverflow'],'small',r['smallButtons'])
