"""Real brand-grid and card screenshots; no screenshot styles or image substitution."""
from pathlib import Path
from io import BytesIO
import json
import math
import sys
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'docs/signature-redesign/phase-c/tests'))
from support import OUT,VIEWPORTS,new_page,go,sweep_home,brand_metrics,assert_brands,page_metrics,assert_page,report_template
report=report_template();report['method']='Actual vertical scroll, native lazy loading, decode and font waits. Brand section is cropped from unaltered full-page screenshot pixels. Card screenshot is taken from the real visible card.'
shots=OUT/'after';shots.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height,label in VIEWPORTS:
        context,page=new_page(browser,report,label,width,height)
        try:
            go(page);sweep_home(page)
            metrics=brand_metrics(page);assert_brands(metrics,width);assert_page(page_metrics(page))
            bounds=page.locator('#brands').evaluate('e=>{const r=e.getBoundingClientRect();return {y:r.top+scrollY,height:r.height}}')
            with Image.open(BytesIO(page.screenshot(full_page=True,animations='disabled'))) as png:
                png.crop((0,math.floor(bounds['y']),width,math.ceil(bounds['y']+bounds['height']))).save(shots/f'brands-{label}.png')
            card=page.locator('[data-brand-id=cordoba]');card.scroll_into_view_if_needed();page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');card.screenshot(path=str(shots/f'cordoba-card-{label}.png'),animations='disabled')
            report['checks'].append({'case':label,'passed':True,'brands':metrics,'screenshots':[f'after/brands-{label}.png',f'after/cordoba-card-{label}.png']});print('PASS capture-'+label,flush=True)
        except Exception as e:
            report['checks'].append({'case':label,'passed':False,'error':str(e)});print('FAIL',label,str(e),flush=True)
        finally:context.close()
    browser.close()
report['passed']=all(c['passed'] for c in report['checks']) and not report['consoleErrors'] and not report['runtimeErrors'] and not report['failedRequests']
(OUT/'capture.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
