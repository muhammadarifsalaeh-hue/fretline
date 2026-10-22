'''Render the proposal document, not the application After state.'''
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

OUT=Path(__file__).resolve().parent
report={'note':'Proposal only; tokens are not imported into the application.','views':[],'errors':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(reduced_motion='reduce')
    page.on('pageerror',lambda e:report['errors'].append(str(e)))
    for width,height,name in [(1440,1100,'desktop'),(768,1024,'tablet'),(390,844,'mobile')]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto('http://127.0.0.1:5192/docs/signature-redesign/proposals/design-system.html',wait_until='networkidle')
        page.evaluate('document.fonts.ready');page.locator('img').evaluate('(i)=>i.decode()')
        filename='design-system-'+name+'.png'
        page.screenshot(path=str(OUT/filename),full_page=True,animations='disabled')
        report['views'].append({'viewport':width,'overflow':page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),'screenshot':filename})
    browser.close()
(OUT/'preview-check.json').write_text(json.dumps(report,indent=2)+'\n')
assert not report['errors'] and not any(v['overflow'] for v in report['views'])
print('Proposal captured at1440/768/390 with no page overflow or runtime errors.')
