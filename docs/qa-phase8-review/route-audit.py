"""Open every active guitar detail in a browser and check identity/runtime health."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import csv,json,os,time
OUT=Path(__file__).parent
ROOT=OUT.parent.parent
BASE=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:5189')
records=list(csv.DictReader((ROOT/'docs/qa-phase7/catalog-200.csv').open(encoding='utf-8-sig')))
report={'routes':[],'page_errors':[],'console_errors':[],'failed_requests':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
 page.on('console',lambda m:report['console_errors'].append(m.text) if m.type=='error' else None)
 page.on('requestfailed',lambda r:report['failed_requests'].append({'url':r.url,'error':r.failure}))
 for i,g in enumerate(records):
  response=page.goto(BASE+'/guitars/'+g['id'],wait_until='load')
  expect(page.locator('.detail-summary h1')).to_have_text(g['model'])
  expect(page.locator('.detail-summary')).to_contain_text(g['brand'])
  report['routes'].append({'id':g['id'],'brand':g['brand'],'passed':response.status==200 and page.locator('.archive-notice').count()==0})
  if i%25==0:print(f'{i+1}/200 details opened',flush=True)
 report['passed']=len(report['routes'])==200 and all(r['passed'] for r in report['routes']) and not any(report[k] for k in ['page_errors','console_errors','failed_requests'])
 browser.close()
(OUT/'detail-route-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('passed',report['passed'],flush=True)
raise SystemExit(0 if report['passed'] else 1)
