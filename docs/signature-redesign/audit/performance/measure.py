'''Production baseline measurements, not Lighthouse scores or Safari results.'''
from pathlib import Path
from playwright.sync_api import sync_playwright
import gzip, json, os, traceback

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = os.environ.get('FRETLINE_AUDIT_URL', 'http://127.0.0.1:5191')
ROUTES = {'home':'/', 'catalog':'/guitars', 'detail':'/guitars/yamaha-pacifica-612viifm',
          'brands':'/brands', 'compare':'/compare?ids=yamaha-pacifica-612viifm,yamaha-fg800',
          'quiz':'/find-my-guitar', 'wishlist':'/wishlist'}
observer = '''window.__baseline={lcp:[],shifts:[],longTasks:[]};
try{new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__baseline.lcp.push({time:e.startTime,size:e.size,element:e.element?.tagName}))).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
try{new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__baseline.shifts.push({time:e.startTime,value:e.value})})).observe({type:'layout-shift',buffered:true})}catch(e){}
try{new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__baseline.longTasks.push({time:e.startTime,duration:e.duration}))).observe({type:'longtask',buffered:true})}catch(e){}'''
report={'baseline':'82fbe9b','browser':'Chromium / Linux, local unthrottled production server',
        'limitations':'Single cold browser-context sample per route/viewport, observed for 2.8s after load; not field Core Web Vitals, Lighthouse, a pass score, physical iPad or Safari.',
        'measurements':[], 'bundles':[], 'errors':[]}
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width,height in [(1440,1000),(390,844)]:
            for name,route in ROUTES.items():
                context=browser.new_context(viewport={'width':width,'height':height})
                context.add_init_script(observer)
                page=context.new_page()
                page.goto(BASE+route,wait_until='networkidle')
                page.wait_for_timeout(2800)
                result=page.evaluate('''()=>({vitals:window.__baseline,
                  navigation:performance.getEntriesByType('navigation').map(n=>({domContentLoaded:n.domContentLoadedEventEnd,load:n.loadEventEnd,transferSize:n.transferSize})),
                  resources:performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,type:r.initiatorType,bytes:r.transferSize,encoded:r.encodedBodySize,duration:r.duration})),
                  title:document.title,description:document.querySelector('meta[name="description"]')?.content,
                  canonical:document.querySelector('link[rel="canonical"]')?.href??null,
                  ogTitle:document.querySelector('meta[property="og:title"]')?.content??null,
                  h1:[...document.querySelectorAll('h1')].map(h=>h.textContent.trim()),
                  brokenImages:[...document.images].filter(i=>i.complete&&i.currentSrc&&i.naturalWidth===0).map(i=>i.currentSrc),
                  overflow:document.documentElement.scrollWidth>innerWidth+1})''')
                shifts=result['vitals']['shifts']; best=0; total=0; start=None; previous=None
                for shift in shifts:
                    now=shift['time']
                    if start is None or now-previous>1000 or now-start>5000:start=now;total=0
                    total+=shift['value'];best=max(best,total);previous=now
                result.update(route=name,width=width,path=route,observedCLS=round(best,5),
                              observedLCPms=round(result['vitals']['lcp'][-1]['time'],1) if result['vitals']['lcp'] else None)
                report['measurements'].append(result)
                print(f'{name} {width}px: LCP={result["observedLCPms"]}ms CLS={result["observedCLS"]}',flush=True)
                context.close()
        browser.close()
    for path in sorted((ROOT/'dist/assets').glob('*')):
        if path.suffix in ['.js','.css']:
            data=path.read_bytes();report['bundles'].append({'file':path.name,'bytes':len(data),'gzipBytes':len(gzip.compress(data))})
    report['completed']=True
except Exception:
    report['completed']=False;report['errors'].append(traceback.format_exc());print(report['errors'][-1],flush=True)
finally:
    (OUT/'baseline.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['completed'] else 1)
