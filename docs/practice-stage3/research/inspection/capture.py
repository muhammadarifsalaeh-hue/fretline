from playwright.sync_api import sync_playwright
from pathlib import Path
import json,os
out=Path(os.environ.get('FRETLINE_STAGE3_DIR','/tmp/fretline-stage3-assets'))/'inspection'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
    errors=[]; responses=[]; failedRequests=[]
    page.on('response',lambda r:responses.append({'url':r.url,'status':r.status}))
    page.on('requestfailed',lambda r:failedRequests.append({'url':r.url,'failure':r.failure}))
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    page.goto(os.environ.get('FRETLINE_INSPECTION_URL','http://127.0.0.1:8766/inspection/'))
    page.wait_for_function('window.inspectionReady || window.inspectionError',timeout=60000)
    print(page.evaluate('({ready:window.inspectionReady,error:window.inspectionError})'),flush=True)
    views=[]
    for name in ['front','side','player','context']:
        page.locator('[data-view="'+name+'"]').click()
        page.screenshot(path=str(out/('failed-contact-'+name+'.png')),full_page=True)
        views.append({'view':name,'camera':page.evaluate('window.inspectionCamera')})
    (out/'runtime-vertices.json').write_text(json.dumps(page.evaluate('window.inspectionVertices')))
    (out/'runtime-proof.json').write_text(json.dumps({'browserVersion':browser.version,'views':views,'errors':errors,'responses':responses,'failedRequests':failedRequests,'proof':page.evaluate('window.inspectionProof')},indent=2))
    print('ERRORS',errors)
    browser.close()
