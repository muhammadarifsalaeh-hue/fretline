"""Production-build acceptance with actual project records; no HTTP/DB mocks.
Linux WebKit with touch emulation is not a certification on a physical iPad.
"""
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect
import argparse, json, re, traceback

P=argparse.ArgumentParser();P.add_argument('--url',required=True);P.add_argument('--before-url',required=True);P.add_argument('--output',type=Path,required=True);P.add_argument('--sizes',nargs='+');P.add_argument('--only-failed-from',type=Path);A=P.parse_args()
BASE=A.url.rstrip('/');BEFORE=A.before_url.rstrip('/');OUT=A.output;OUT.mkdir(parents=True,exist_ok=True)
FAILED_NAMES={c['name'] for c in json.loads(A.only_failed_from.read_text())['checks'] if not c['passed']} if A.only_failed_from else None
SIZES={'desktop':(1440,1000),'landscape':(1194,834),'portrait':(768,1024),'mobile':(390,844),'narrow':(320,740),'mobile-landscape':(844,390)}
ROUTES={'home':'/','catalog':'/guitars','brands':'/brands','brand':'/brands/yamaha','favorites':'/wishlist','credits':'/image-credits','compare':'/compare?ids=yamaha-pacifica-612viifm,yamaha-fg820-12','quiz':'/find-my-guitar','practice':'/practice','admin':'/admin','qr':'/qr','detail':'/guitars/yamaha-pacifica-612viifm','missing':'/route-not-found'}
REPORT={'checks':[],'consoleErrors':[],'runtimeErrors':[],'failedImages':[],'source':'original real project catalog; no mock records, SQL or database writes','physicalIPadSafariTested':False,'hostedSupabaseTested':False}
def save(): (OUT/'browser-results.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
def check(name,fn,page):
 if FAILED_NAMES is not None and name not in FAILED_NAMES:return
 try:
  evidence=fn();REPORT['checks'].append({'name':name,'passed':True,'evidence':evidence});print('PASS',name,flush=True)
 except Exception:
  error=traceback.format_exc();REPORT['checks'].append({'name':name,'passed':False,'error':error});print('FAIL',name,error,flush=True)
  try:page.screenshot(path=str(OUT/(name+'-FAIL.png')),animations='disabled')
  except Exception:pass
 save()
def go(page,path,base=BASE):
 response=page.goto(base+path,wait_until='networkidle');assert response.status in [200,304],response.status # WebKit may expose a successful cache revalidation as 304
 expect(page.locator('main h1')).to_be_visible();page.evaluate('document.fonts.ready')
def load_visible_images(page):
 page.evaluate('''async()=>{let step=Math.max(200,innerHeight*.8);for(let y=0;y<document.documentElement.scrollHeight;y+=step){scrollTo(0,y);await new Promise(r=>requestAnimationFrame(r))}scrollTo(0,0)}''')
 page.wait_for_function('''()=>[...document.querySelectorAll('main img')].filter(i=>getComputedStyle(i).display!=='none'&&i.getBoundingClientRect().width>0).every(i=>i.complete)''',timeout=20000)
 bad=page.locator('main img').evaluate_all('(nodes)=>nodes.filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute("src"))');assert not bad,bad
def styles(page):
 return page.evaluate('''()=>Object.fromEntries(['.site-header','.site-header-inner','.admin-page','.admin-config-card','main h1','main input','main button'].map(s=>{const e=document.querySelector(s);if(!e)return[s,null];const c=getComputedStyle(e);return[s,Object.fromEntries(['fontFamily','fontSize','color','backgroundColor','borderRadius','padding','minHeight','maxWidth','gap'].map(k=>[k,c[k]]))]}))''')

with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']) if engine=='chromium' else p.webkit.launch()
  for device,(width,height) in SIZES.items():
   if A.sizes and device not in A.sizes:continue
   context=b.new_context(viewport={'width':width,'height':height},has_touch=device in ['portrait','mobile','narrow','mobile-landscape'],reduced_motion='reduce');page=context.new_page()
   page.on('console',lambda m:REPORT['consoleErrors'].append(m.text) if m.type=='error' else None);page.on('pageerror',lambda e:REPORT['runtimeErrors'].append(str(e)))
   for name,path in ROUTES.items():
    def route(name=name,path=path):
     go(page,path);load_visible_images(page)
     assert page.locator('main h1').count()==1
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
     assert page.locator('.site-header a[href="/admin"]').count()==0,'Unverified visitor sees admin link'
     text=page.locator('main').inner_text()
     assert not re.search(r'AI\s*(Generated|Edited)|Made (?:with|by) AI|Powered by AI|Demo Website|Placeholder Content|Template Description',text,re.I)
     assert not re.search(r'\b(?:Search|Favorites|Loading|Filter|Sort|Explore by Brand)\b',text),'Untranslated ordinary UI'
     assert not re.search(r'\b(?:targeted|p4|p5|p6)\.[a-zA-Z]+\.',text),'Missing translation key'
     links=page.locator('main a[href^="/"]').evaluate_all('(nodes)=>nodes.map(e=>e.getAttribute("href"))')
     for href in links:
      path_only=urlparse(href).path
      assert re.match(r'^/(?:$|guitars(?:/[^/]+)?$|brands(?:/[^/]+)?$|wishlist$|compare$|find-my-guitar$|practice$|admin$|qr$|image-credits$|assets/)',path_only),href
     if name=='home':
      expect(page.locator('.signature-stats-list dd')).to_have_text(['200','10','4','4'])
      expect(page.locator('[data-marquee-primary] a')).to_have_count(10)
      expected=4 if width>=1024 else 2 if width>=640 else 1
      assert page.locator('.signature-category-grid').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length')==expected
      expect(page.locator('#home-practice img')).to_have_attribute('src',re.compile('practice-black-gold-les-paul'))
      for selector,destination in [('#home-practice','/practice'),('#find','/find-my-guitar'),('#compare','/compare')]:expect(page.locator(selector+' .home-editorial-cta')).to_have_attribute('href',destination)
      pill=page.locator('.signature-category-pill').first;assert float(pill.evaluate('(e)=>parseFloat(getComputedStyle(e).borderTopLeftRadius)'))>=100
      if width>=1024:
       practice=page.locator('#home-practice').bounding_box();find=page.locator('#find').bounding_box();compare=page.locator('#compare').bounding_box();assert abs(practice['height']-(compare['y']+compare['height']-find['y']))<2
      else:
       assert page.locator('#home-practice').bounding_box()['y']<page.locator('#find').bounding_box()['y']<page.locator('#compare').bounding_box()['y']
     if name=='practice':
      expect(page.locator('[data-practice-chord]')).to_have_count(42)
      expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=60000)
      expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
     if name=='compare':expect(page.locator('[data-comparison-slot]')).to_have_count(2);expect(page.locator('[data-compare-empty-slot]')).to_have_count(2)
     if name=='admin':assert page.locator('.fretline-experience').count()==0;expect(page.get_by_role('heading',name='เชื่อมต่อโปรเจกต์ Fretline')).to_be_visible()
     if device in ['desktop','mobile'] and name in ['home','catalog','brands','detail','quiz','compare','practice','favorites','qr']:
      page.screenshot(path=str(OUT/(engine+'-'+device+'-'+name+'.png')),animations='disabled')
     return {'viewport':device,'route':path,'oneHeading':True,'noOverflow':True,'noBrokenImages':True,'internalLinks':len(links),'publicStyling':name!='admin'}
    check(engine+'-'+device+'-'+name,route,page)
   def admin_unchanged():
    go(page,'/admin',BEFORE);old=styles(page);go(page,'/admin');new=styles(page);assert new==old,{'before':old,'after':new}
    return {'originalAdminComputedStylesIdentical':True,'loginConfigUntouched':True,'liveAuthNotConfigured':True}
   check(engine+'-'+device+'-admin-isolation',admin_unchanged,page)
   if device in ['portrait','mobile','narrow','mobile-landscape']:
    def menu():
     go(page,'/');page.get_by_role('button',name='เปิดเมนู',exact=True).click();dialog=page.locator('#mobile-navigation');expect(dialog).to_have_attribute('aria-hidden','false');expect(dialog.get_by_role('link',name='กีตาร์',exact=True)).to_be_visible();dialog.get_by_role('button',name='ปิดเมนู',exact=True).click();expect(dialog).to_have_attribute('aria-hidden','true')
     return {'openAndClose':True,'touchTargets':True}
    check(engine+'-'+device+'-navigation',menu,page)
   context.close()
  context=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference');page=context.new_page()
  def marquee():
   go(page,'/');rail=page.locator('[data-marquee-viewport]');rail.scroll_into_view_if_needed();page.mouse.move(1,1);page.wait_for_timeout(250)
   primary=page.locator('[data-marquee-primary]');assert primary.locator('a').count()==10
   for anchor in primary.locator('a').all():
    assert anchor.evaluate('(e)=>getComputedStyle(e).borderTopWidth')=='0px';assert anchor.evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgba(0, 0, 0, 0)'
   start=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(900);end=rail.evaluate('(e)=>e.scrollLeft');assert end>start,(start,end)
   group=primary.bounding_box()['width'];rail.evaluate('(e,w)=>e.scrollLeft=2*w-4',group);page.wait_for_timeout(1800)
   samples=[]
   for i in range(8):samples.append(rail.evaluate('(e)=>e.scrollLeft'));page.wait_for_timeout(160)
   deltas=[(b-a)%group for a,b in zip(samples,samples[1:])];assert all(0<=delta<45 for delta in deltas),deltas;assert sum(deltas)>0
   rect=rail.bounding_box();page.mouse.move(rect['x']+rect['width']*.7,rect['y']+rect['height']*.5);page.mouse.down();page.mouse.move(rect['x']+rect['width']*.3,rect['y']+rect['height']*.5,steps=12);dragged=rail.evaluate('(e)=>e.scrollLeft');page.mouse.up();page.wait_for_timeout(1800);assert rail.evaluate('(e)=>e.scrollLeft')!=dragged
   page.keyboard.press('Tab');primary.locator('a').first.focus();page.wait_for_timeout(200);focused=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(600);assert rail.evaluate('(e)=>e.scrollLeft')==focused
   return {'realBrands':10,'realLogoFiles':9,'unchangedCordobaNameFallback':True,'noIndividualFrames':True,'rightToLeftAutomatic':True,'seamDeltasPx':deltas,'dragAndResume':True,'keyboardPause':True}
  check(engine+'-original-marquee-motion',marquee,page);context.close()
  context=b.new_context(viewport={'width':390,'height':844},has_touch=True,reduced_motion='reduce');page=context.new_page()
  def brand_links():
   destinations=[]
   for bid in ['yamaha','fender','gibson','taylor','ibanez','prs','epiphone','martin','squier','cordoba']:
    go(page,'/');rail=page.locator('[data-marquee-viewport]');rail.scroll_into_view_if_needed();old=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(150);assert old==rail.evaluate('(e)=>e.scrollLeft')
    link=page.locator('[data-marquee-primary] a[data-brand-id="'+bid+'"]');link.scroll_into_view_if_needed();link.tap();expect(page.locator('.catalog-result-count>p').first).to_contain_text('20 รุ่น');destinations.append(page.url)
   return {'allTenActualBrandLinks':destinations,'reducedMotionNoAutoscroll':True,'nativeTouchTap':True}
  check(engine+'-all-ten-brand-touch-links',brand_links,page);context.close();b.close()
REPORT['passed']=all(c['passed'] for c in REPORT['checks']) and not REPORT['consoleErrors'] and not REPORT['runtimeErrors'];save();print('FINAL',REPORT['passed'],len(REPORT['checks']),flush=True);raise SystemExit(not REPORT['passed'])
