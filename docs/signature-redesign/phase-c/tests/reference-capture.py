"""Additional actual render at the supplied reference's 1280px width."""
from PIL import Image
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import math
from support import OUT, new_page, go, sweep_home, brand_metrics, assert_brands, report_template
report=report_template()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context,page=new_page(browser,report,'reference-desktop',1280,1000)
    go(page);sweep_home(page)
    metrics=brand_metrics(page);assert_brands(metrics,1280)
    bounds=page.locator('#brands').evaluate('e=>{const r=e.getBoundingClientRect();return {y:r.top+scrollY,height:r.height}}')
    full=OUT/'after/home-reference-desktop-full.png'
    page.screenshot(path=str(full),full_page=True,animations='disabled')
    with Image.open(full) as image:
        image.crop((0,math.floor(bounds['y']),1280,math.ceil(bounds['y']+bounds['height']))).save(OUT/'after/brands-reference-desktop.png')
    report['checks'].append({'case':'reference-desktop','passed':True,'brands':metrics,'bounds':bounds})
    context.close();browser.close()
report['passed']=not report['consoleErrors'] and not report['runtimeErrors'] and not report['failedRequests']
(OUT/'reference-capture.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
