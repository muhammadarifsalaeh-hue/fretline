"""Capture actual Phase C before/after at six widths. Root supplies the server.

No altered screenshot DOM/CSS, network mocks or product substitutions. Native
scroll/decode waits reveal real content. Brands are cropped from full-page pixels.
"""
from PIL import Image
from playwright.sync_api import sync_playwright
import json
import math
import os
import traceback
from polish_support import (OUT,CAPTURE_VIEWPORTS,new_page,go,sweep_home,page_metrics,
                            brand_metrics,assert_page,assert_brand_layout,
                            homepage_geometry,report_template)

STAGE=os.environ.get('FRETLINE_QA_STAGE','after')
assert STAGE in {'before','after'},STAGE
SHOTS=OUT/STAGE
SHOTS.mkdir(parents=True,exist_ok=True)
REPORT=report_template()
REPORT['stage']=STAGE
REPORT['method']='Actual application, native scrolling, loaded/decoded source images and local fonts. No screenshot-only DOM/style changes. Brands crops use the actual full-page screenshot pixels.'
REPORT['limitations']=['Chromium/Linux viewport and touch emulation, not physical iPad/Safari.','Geometry does not establish visual similarity or exact subject crop; manual reference review remains necessary.']
selected=set(filter(None,os.environ.get('FRETLINE_QA_VIEWPORTS','').split(',')))
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('FRETLINE_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        for width,height,label in CAPTURE_VIEWPORTS:
            if selected and label not in selected:continue
            context,page=new_page(browser,REPORT,'capture-'+STAGE+'-'+label,width,height)
            try:
                go(page);sweep_home(page)
                metrics=page_metrics(page);brands=brand_metrics(page)
                assert_page(metrics);layout=assert_brand_layout(brands,width,STAGE)
                composition=homepage_geometry(page)
                bounds=page.locator('#brands').evaluate('e=>{const r=e.getBoundingClientRect();return {x:r.left+scrollX,y:r.top+scrollY,width:r.width,height:r.height}}')
                page.evaluate('document.activeElement?.blur()')
                viewport=SHOTS/f'home-{label}.png';full=SHOTS/f'home-{label}-full.png';brandshot=SHOTS/f'brands-{label}.png'
                page.screenshot(path=str(viewport),animations='disabled')
                page.screenshot(path=str(full),full_page=True,animations='disabled')
                with Image.open(full) as image:
                    scale=image.width/width
                    image.crop((math.floor(bounds['x']*scale),math.floor(bounds['y']*scale),
                                min(image.width,math.ceil((bounds['x']+bounds['width'])*scale)),
                                min(image.height,math.ceil((bounds['y']+bounds['height'])*scale)))).save(brandshot)
                REPORT['checks'].append({'case':label,'passed':True,'page':metrics,'brands':brands,
                                         'layout':layout,'composition':composition,'brandsDocumentBounds':bounds,
                                         'screenshots':[str(x.relative_to(OUT)) for x in [viewport,full,brandshot]]})
                print('PASS capture-'+STAGE+'-'+label,flush=True)
            except Exception:
                failure=traceback.format_exc();REPORT['checks'].append({'case':label,'passed':False,'failure':failure});print('FAIL '+label+'\n'+failure,flush=True)
            finally:context.close()
        browser.close()
except Exception:REPORT['harnessFailure']=traceback.format_exc()
finally:
    REPORT['passed']=bool(REPORT['checks']) and all(c['passed'] for c in REPORT['checks']) and not REPORT.get('harnessFailure') and not REPORT['consoleErrors'] and not REPORT['runtimeErrors'] and not REPORT['failedRequests']
    (OUT/f'capture-{STAGE}.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if REPORT['passed'] else 1)
