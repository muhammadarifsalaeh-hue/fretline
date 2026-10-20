"""Deliberately inject loading, chunk-failure and photo-failure conditions.
Errors in this isolated test are expected, not normal-flow console regressions.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,os
OUT=Path(__file__).parent
BASE=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:4188')
r={'checks':[],'expected_fault_console':[],'expected_fault_page_errors':[]}
def check(name,condition=True):
 r['checks'].append({'name':name,'passed':bool(condition)});print(name,bool(condition),flush=True);assert condition,name
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce')
 page=context.new_page()
 page.on('console',lambda m:r['expected_fault_console'].append(m.text) if m.type=='error' else None)
 page.on('pageerror',lambda e:r['expected_fault_page_errors'].append(str(e)))
 pending=[]
 page.route('**/assets/CatalogPage-*.js',lambda route:pending.append(route))
 page.goto(BASE+'/guitars',wait_until='domcontentloaded')
 expect(page.get_by_role('status',name='กำลังโหลดข้อมูลกีตาร์…',exact=True)).to_be_visible()
 check('Lazy Catalog exposes a labelled loading state')
 page.screenshot(path=str(OUT/'loading-mobile.png'),animations='disabled')
 for route in pending:route.abort()
 expect(page.get_by_role('heading',name='โหลดหน้านี้ไม่สำเร็จ',exact=True)).to_be_visible()
 check('Failed route chunk displays the recoverable error boundary')
 page.screenshot(path=str(OUT/'error-mobile.png'),animations='disabled')
 page.unroute('**/assets/CatalogPage-*.js')
 page.get_by_role('button',name='ลองใหม่',exact=True).click()
 expect(page.locator('.catalog-grid article')).to_have_count(9)
 check('Retry reload recovers after the chunk becomes available')
 page.goto(BASE+'/guitars?q=does-not-exist-zz-999999',wait_until='networkidle')
 expect(page.locator('.catalog-grid article')).to_have_count(0)
 expect(page.locator('main')).to_contain_text('ไม่พบ')
 page.screenshot(path=str(OUT/'empty-mobile.png'),animations='disabled')
 check('An unmatched query has an honest empty state')
 page.route('**/assets/01-front-*.webp',lambda route:route.abort())
 page.goto(BASE+'/guitars/yamaha-fg820-12',wait_until='networkidle')
 expect(page.locator('.gallery-main .image-placeholder')).to_be_visible()
 check('Failed licensed photo falls back to this model’s labelled illustration','FG820-12' in page.locator('.gallery-main .image-placeholder').get_attribute('aria-label'))
 page.screenshot(path=str(OUT/'image-fallback-mobile.png'),animations='disabled')
 page.unroute('**/assets/01-front-*.webp')
 page.goto(BASE+'/brands/unknown-brand-123',wait_until='networkidle')
 expect(page.get_by_role('heading',name='ไม่พบแบรนด์นี้',level=1,exact=True)).to_be_visible()
 check('Unknown brand link exposes the existing recovery page')
 r['passed']=all(c['passed'] for c in r['checks']);browser.close()
(OUT/'states-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
