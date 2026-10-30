"""Public navigation, keyboard, motion, responsive composition and attribution checks. No database writes."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import argparse,json,re
parser=argparse.ArgumentParser();parser.add_argument('--url',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
BASE=args.url.rstrip('/');out=args.output;out.mkdir(parents=True,exist_ok=True)
report={'checks':[],'consoleErrors':[],'runtimeErrors':[],'physicalIPadSafariTested':False,'realSupabaseTested':False}
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']) if engine=='chromium' else p.webkit.launch()
  for device,size in [('desktop',(1440,1000)),('landscape',(1194,834)),('portrait',(768,1024)),('mobile',(390,844))]:
   c=b.new_context(viewport={'width':size[0],'height':size[1]},reduced_motion='reduce',has_touch=device!='desktop');page=c.new_page();page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)));page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
   label=engine+'-'+device
   try:
    page.goto(BASE+'/',wait_until='networkidle');expect(page.locator('main h1')).to_be_visible();page.evaluate('document.fonts.ready')
    page.locator('.skip-link').focus();page.keyboard.press('Enter');expect(page.locator('#main-content')).to_be_focused()
    assert page.locator('main>div').evaluate('(e)=>getComputedStyle(e).animationName')=='none'
    if size[0]<1024:
     page.get_by_role('button',name='เปิดเมนู',exact=True).click();expect(page.locator('#mobile-navigation')).to_be_visible();assert page.locator('#mobile-navigation a[href="/admin"]').count()==0
     page.keyboard.press('Escape');expect(page.locator('#mobile-navigation')).not_to_be_visible();expect(page.get_by_role('button',name='เปิดเมนู',exact=True)).to_be_focused()
     page.get_by_role('button',name='เปิดเมนู',exact=True).click();page.locator('#mobile-navigation a[href="/brands"]').click();expect(page).to_have_url(re.compile('/brands$'));expect(page.locator('main h1')).to_be_visible()
     page.goto(BASE+'/',wait_until='networkidle')
    for selector in ['#home-practice','#find','#compare']:page.locator(selector).scroll_into_view_if_needed()
    rects={sel:page.locator(sel).bounding_box() for sel in ['#home-practice','#find','#compare']};a,f,d=[rects[sel] for sel in ['#home-practice','#find','#compare']]
    if size[0]>=1024 and size[0]>size[1]:
     assert a['x']<f['x'] and abs(f['x']-d['x'])<2 and f['y']<d['y'] and abs(a['height']-(d['y']+d['height']-f['y']))<2
    else:assert a['y']<f['y']<d['y'] and abs(a['width']-f['width'])<2
    if engine=='webkit' and device in ['landscape','portrait']:
     target=page.locator('#home-features');target.scroll_into_view_if_needed()
     for image in target.locator('img').all():image.evaluate('(image)=>image.decode()')
     target.screenshot(path=str(out/f'{label}-three-modes.png'),animations='disabled')
    page.goto(BASE+'/image-credits',wait_until='networkidle');expect(page.locator('main h1')).to_be_visible();page.locator('main details').evaluate_all('(nodes)=>nodes.forEach(e=>e.open=true)');text=page.locator('main').inner_text()
    assert not re.search(r'\bAI\b|AI Generated|AI Edited|Made by AI|Powered by AI',text,re.I)
    assert 'สิทธิ์ต้นฉบับและความตรงรุ่นยังไม่ได้รับการยืนยัน' in text
    assert page.locator('#home-photography a').count()>0 and page.locator('#discovery-photography a').count()>0
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    report['checks'].append({'name':label,'passed':True,'evidence':{'keyboardSkipLink':True,'reducedMotion':True,'mobileMenuAndAdminProtection':True,'responsiveThreeModeComposition':True,'originalRightsCreditsPreserved':True,'publicLabelsClean':True}});print('PASS',label,flush=True)
   except Exception as e:
    report['checks'].append({'name':label,'passed':False,'error':str(e)});print('FAIL',label,str(e),flush=True)
   (out/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));c.close()
  b.close()
report['passed']=all(x['passed'] for x in report['checks']) and not report['consoleErrors'] and not report['runtimeErrors'];(out/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('FINAL',report['passed'],len(report['checks']),flush=True);raise SystemExit(not report['passed'])
