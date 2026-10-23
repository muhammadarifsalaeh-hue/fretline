"""Local production diagnostics, not Lighthouse or real-user Core Web Vitals."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import os
OUT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:5203')
report={'method':'Fresh Chromium contexts against local Vite production preview; normal motion, 2-second observation after network idle. No CPU/network throttling. Not Lighthouse, physical Safari or field Core Web Vitals.','runs':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in [(1440,1000),(390,844)]:
        context=browser.new_context(viewport={'width':width,'height':height},has_touch=width<1024)
        page=context.new_page()
        page.add_init_script('''window.phaseCPerf={cls:0,lcp:0};
          new PerformanceObserver(list=>list.getEntries().forEach(e=>{if(!e.hadRecentInput)window.phaseCPerf.cls+=e.value})).observe({type:'layout-shift',buffered:true});
          new PerformanceObserver(list=>list.getEntries().forEach(e=>window.phaseCPerf.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});''')
        page.goto(BASE,wait_until='networkidle');page.evaluate('document.fonts.ready');page.wait_for_timeout(2000)
        result=page.evaluate('''()=>({...window.phaseCPerf,viewport:{width:innerWidth,height:innerHeight},
          domContentLoaded:performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd,
          resourceRequests:performance.getEntriesByType('resource').length,
          transferBytes:performance.getEntriesByType('resource').reduce((sum,e)=>sum+e.transferSize,0),
          overflow:document.documentElement.scrollWidth>innerWidth,
          imageGeometry:[...document.querySelectorAll('#brands img')].every(i=>i.hasAttribute('width')&&i.hasAttribute('height'))})''')
        report['runs'].append(result);print(width,json.dumps(result),flush=True);context.close()
    browser.close()
report['passed']=all(r['cls']<=.1 and not r['overflow'] and r['imageGeometry'] for r in report['runs'])
(OUT/'performance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
