"""Real browser diagnostics for /brands. No app/data edits or hidden image substitution."""
from collections import Counter
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import os
import re
import sys
import unicodedata

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(os.environ.get('FRETLINE_QA_OUTPUT_DIR', str(Path(__file__).resolve().parents[1]))).resolve()
OUT.mkdir(parents=True, exist_ok=True)
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:5304').rstrip('/')
ENGINE = os.environ.get('FRETLINE_QA_ENGINE', 'chromium')
assert ENGINE in {'chromium', 'webkit'}, ENGINE
VIEWPORTS = [(1440,1000,'desktop'),(1024,768,'tablet-landscape'),(768,1024,'tablet'),(390,844,'mobile'),(320,740,'small-mobile')]
os.environ.setdefault('FRETLINE_QA_OUTPUT_DIR', str(OUT))
sys.path.insert(0, str(ROOT/'docs/signature-redesign/phase-c/tests'))
from support import catalogue_records

RECORDS = catalogue_records()
BY_ID = {r['id']: r for r in RECORDS}
BRAND_COUNTS = Counter(r['brand'] for r in RECORDS)
def brand_id(name):
    return ''.join(c for c in unicodedata.normalize('NFD', name).lower() if not unicodedata.combining(c))
BRAND_NAMES = {brand_id(name): name for name in BRAND_COUNTS}

def report_template():
    return {'baseURL':BASE,'engine':ENGINE,'checks':[], 'consoleErrors':[], 'runtimeErrors':[], 'failedRequests':[], 'badResponses':[],
            'expectedFaultErrors':[], 'injectedImageFaults':[],
            'limitations':['WebKit on Linux is engine coverage, not physical Safari on iPad.','Viewport/touch emulation does not reproduce every iPad GPU, OS or network condition.']}

def launch(p, report):
    if ENGINE == 'chromium':
        browser = p.chromium.launch(executable_path=os.environ.get('FRETLINE_CHROMIUM','/usr/bin/chromium'), args=['--no-sandbox'])
    else:
        browser = p.webkit.launch()
    report['browserVersion'] = browser.version
    return browser

def image_target(url, kind='all'):
    name = urlparse(url).path.rsplit('/',1)[-1]
    identity = next((key for key in BRAND_NAMES if re.match(re.escape(key)+r'[-.]', name)), None)
    if not identity: return False
    photo = bool(re.search(r'\.webp$', name))
    logo = bool(re.search(r'\.(svg|png)$', name))
    return (kind == 'photo' and photo) or (kind == 'logo' and logo) or (kind == 'all' and (photo or logo))

def new_page(browser, report, case, width=1440, height=1000, fault_kind=None):
    context = browser.new_context(viewport={'width':width,'height':height}, has_touch=width<=1024, reduced_motion='reduce', locale='th-TH')
    page = context.new_page()
    def expected(url='', text=''):
        return bool(fault_kind and (image_target(url, fault_kind) or (not url and any(s in text.lower() for s in ['load resource','load image','decode image','failed to fetch']))))
    def console(message):
        if message.type != 'error': return
        row={'case':case,'text':message.text,'location':message.location}
        (report['expectedFaultErrors'] if expected(message.location.get('url',''),message.text) else report['consoleErrors']).append(row)
    def failed(request):
        row={'case':case,'url':request.url,'failure':request.failure}
        (report['expectedFaultErrors'] if expected(request.url) else report['failedRequests']).append(row)
    def response(result):
        if result.status < 400: return
        row={'case':case,'url':result.url,'status':result.status}
        (report['expectedFaultErrors'] if expected(result.url) else report['badResponses']).append(row)
    page.on('console',console)
    page.on('pageerror',lambda error:report['runtimeErrors'].append({'case':case,'text':str(error)}))
    page.on('requestfailed',failed)
    page.on('response',response)
    return context,page

def go(page, route='/brands'):
    page.goto(BASE+route,wait_until='networkidle')
    page.locator('#main-content h1').wait_for(state='visible')
    page.evaluate('document.fonts.ready')

def settle(page):
    page.evaluate('''async()=>{await document.fonts.ready;await Promise.all([...document.images].filter(i=>i.complete&&i.naturalWidth>0).map(i=>i.decode().catch(()=>{})));await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame)}''')

def sweep(page):
    height=page.evaluate('document.documentElement.scrollHeight')
    for top in range(0,int(height)+400,400):
        page.evaluate('(top)=>window.scrollTo({top,behavior:"instant"})',top)
        page.wait_for_timeout(90)
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    page.wait_for_timeout(150)
    settle(page)

def wait_artwork(page):
    """Wait for real native requests after sweeping; never force loading/source values."""
    page.wait_for_function('''()=>[...document.querySelectorAll('.brands-page [data-brand-photo],.brands-page [data-brand-logo]')].every(i=>i.complete)''',timeout=20000)
    settle(page)

def metrics(page):
    return page.locator('.brands-page').evaluate(r'''root=>{
      const rect=e=>{if(!e)return null;const b=e.getBoundingClientRect();return {x:b.left+scrollX,y:b.top+scrollY,width:b.width,height:b.height,left:b.left,top:b.top,right:b.right,bottom:b.bottom}};
      const style=e=>{const s=getComputedStyle(e);return {display:s.display,visibility:s.visibility,opacity:s.opacity,position:s.position,zIndex:s.zIndex,overflow:s.overflow,aspectRatio:s.aspectRatio,minHeight:s.minHeight,height:s.height,filter:s.filter,transform:s.transform,animation:s.animationName}};
      const hidden=e=>{for(let n=e;n&&n.nodeType===1;n=n.parentElement){const s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return true;}return false;};
      const status=(a,name)=>a.getAttribute(name)||a.querySelector('['+name+']')?.getAttribute(name)||null;
      const image=i=>({src:i.currentSrc||i.src,complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,rect:rect(i),style:style(i),hidden:hidden(i)});
      const grid=root.querySelector('.brand-directory-grid');
      return {viewport:{width:innerWidth,height:innerHeight},userAgent:navigator.userAgent,aspectRatioSupported:CSS.supports('aspect-ratio','1 / 1'),scrollWidth:document.documentElement.scrollWidth,grid:rect(grid),columns:grid?getComputedStyle(grid).gridTemplateColumns:null,
        cards:[...root.querySelectorAll('.brand-directory-card[data-brand-id]')].map(a=>({id:a.dataset.brandId,href:a.getAttribute('href'),label:a.getAttribute('aria-label'),text:a.innerText,rect:rect(a),style:style(a),hidden:hidden(a),
          photoStatus:status(a,'data-photo-status'),logoStatus:status(a,'data-logo-status'),
          photos:[...a.querySelectorAll('[data-brand-photo]')].map(image),logos:[...a.querySelectorAll('[data-brand-logo]')].map(image),
          fallbacks:[...a.querySelectorAll('[data-brand-fallback]')].map(e=>({text:e.innerText,rect:rect(e),hidden:hidden(e),style:style(e)})),
          photoFallbacks:[...a.querySelectorAll('[data-brand-photo-fallback],[data-photo-fallback]')].map(e=>({text:e.innerText,rect:rect(e),hidden:hidden(e)})),
          count:a.querySelector('[data-brand-count],.brand-card-count')?.innerText,mark:rect(a.querySelector('[data-brand-mark],.brand-card-mark')),
          before:{content:getComputedStyle(a,'::before').content,paddingTop:getComputedStyle(a,'::before').paddingTop,display:getComputedStyle(a,'::before').display}}))};
    }''')

def assert_layout(data, normal=True):
    assert len(RECORDS)==len(BY_ID)==200 and len(BRAND_COUNTS)==10 and set(BRAND_COUNTS.values())=={20}
    assert len(data['cards'])==10 and {c['id'] for c in data['cards']}==set(BRAND_NAMES), data
    assert data['scrollWidth']<=data['viewport']['width']+1, data
    for c in data['cards']:
        assert c['rect']['height']>150 and c['rect']['width']>100 and not c['hidden'],c
        assert BRAND_NAMES[c['id']] in c['label'] and re.search(r'\b20\b',c['count'] or ''),c
        url=urlparse(c['href']);assert url.path=='/guitars' and parse_qs(url.query).get('brand')==[BRAND_NAMES[c['id']]],c
        if normal:
            assert len(c['photos'])==1,c
            p=c['photos'][0];assert p['complete'] and min(p['naturalWidth'],p['naturalHeight'])>0 and not p['hidden'],c
            assert image_target(p['src'],'photo') and re.search(r'/'+c['id']+r'[-.]',urlparse(p['src']).path),c
            if c['id']=='cordoba':
                assert any(f['text']==BRAND_NAMES[c['id']] and not f['hidden'] for f in c['fallbacks']),c
            else:
                assert len(c['logos'])==1,c
                i=c['logos'][0];assert i['complete'] and min(i['naturalWidth'],i['naturalHeight'])>0 and not i['hidden'],c
                assert re.search(r'/'+c['id']+r'[-.]',urlparse(i['src']).path),c
    return {'models':200,'brands':10,'modelsPerBrand':20,'minCardHeight':min(c['rect']['height'] for c in data['cards']),'normalArtwork':normal}

def pixel_evidence(page, name):
    """Read actual card pixels after native scroll, not generated reference imagery."""
    rows=[]
    for card in page.locator('.brand-directory-card[data-brand-id]').all():
        page.evaluate('(y)=>window.scrollTo({top:y-120,behavior:"instant"})',card.evaluate('e=>e.getBoundingClientRect().top+scrollY'))
        settle(page)
        capture=card.screenshot(animations='allow')
        image=Image.open(BytesIO(capture)).convert('RGB')
        mark=card.locator('[data-brand-mark],.brand-card-mark').first
        a,b=card.bounding_box(),mark.bounding_box()
        region=image.crop((max(0,int(b['x']-a['x'])),max(0,int(b['y']-a['y'])),min(image.width,int(b['x']-a['x']+b['width']+1)),min(image.height,int(b['y']-a['y']+b['height']+1))))
        whites=sum(1 for p in region.getdata() if min(p)>210)
        palette=len(image.resize((64,64)).getcolors(4096) or [])
        row={'id':card.get_attribute('data-brand-id'),'cardPixels':[image.width,image.height],'markBrightPixels':whites,'cardSampleColors':palette}
        if whites<=10:
            failure=OUT/'failures'/f'{name}-{row["id"]}-paint.png';failure.parent.mkdir(exist_ok=True);failure.write_bytes(capture);row['failureScreenshot']=str(failure.relative_to(OUT))
        assert whites>10,row
        rows.append(row)
    return {'method':'Actual locator screenshots after native scroll; bright mark pixels support painted identity, not photographic source authenticity. Manual reference review is still required.','cards':rows}

def finish(report, filename):
    report['passed']=bool(report['checks']) and all(c['passed'] for c in report['checks']) and not report.get('harnessFailure') and not any(report[k] for k in ['consoleErrors','runtimeErrors','failedRequests','badResponses'])
    (OUT/filename).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report['passed']
