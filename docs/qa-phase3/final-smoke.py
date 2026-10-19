from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import json,os
OUTPUT=Path(__file__).resolve().parent
BASE=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:4173')
report={'checks':[],'page_errors':[],'console_errors':[]}
def check(name,value=True):
 report['checks'].append({'name':name,'passed':bool(value)});assert value,name
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN','/usr/bin/chromium'),args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1100})
 page.on('pageerror',lambda error:report['page_errors'].append(str(error)))
 page.on('console',lambda message:report['console_errors'].append(message.text) if message.type=='error' else None)
 page.goto(BASE+'/guitars/yamaha-fg830#specs',wait_until='networkidle')
 expect(page.get_by_role('tab',name='สเปก',exact=True)).to_have_attribute('aria-selected','true')
 expect(page.get_by_role('table')).to_be_visible();check('Existing #specs deep link opens specifications')
 check('Specifications anchor scrolls under navigation',page.locator('#specs').evaluate('(el)=>el.getBoundingClientRect().top')>=79)
 page.get_by_role('tab',name='รีวิว',exact=True).click();expect(page.get_by_text('ยังไม่มีรีวิวที่ตรวจสอบแล้ว',exact=True)).to_be_visible()
 check('Tabs remain interactive after a deep link')
 page.reload(wait_until='networkidle');expect(page.get_by_role('table')).to_be_visible();check('Specs deep link survives reload')
 for kind,path in [('catalog','/guitars'),('detail','/guitars/yamaha-fg830')]:
  for label,width,height in [('desktop',1440,1100),('tablet',768,1024),('mobile',390,844)]:
   page.set_viewport_size({'width':width,'height':height});page.goto(BASE+path,wait_until='networkidle')
   page.screenshot(path=str(OUTPUT/f'{kind}-{label}.png'),animations='disabled')
   if label=='desktop':
    if kind=='detail':page.get_by_role('tab',name='สเปก',exact=True).click()
    page.screenshot(path=str(OUTPUT/f'{kind}-desktop-full.png'),full_page=True,animations='disabled')
 check('Final build has no page or console errors',not report['page_errors'] and not report['console_errors'])
 browser.close()
report['passed']=True
(OUTPUT/'final-smoke-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
