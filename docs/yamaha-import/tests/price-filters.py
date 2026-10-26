"""Price filter regression for real imported THB values, retaining the old fixture report."""
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json
ROOT=Path(__file__).resolve().parents[3];BASE='http://127.0.0.1:5432'
records=json.loads((ROOT/'src/data/catalog/reviewedGuitars.json').read_text())
expected={k for k,v in records.items() if k.startswith('yamaha-') and isinstance(v.get('price'),int) and v['price']<=30000}
assert len(expected)==17
report={'checks':[],'errors':[],'physicalIPadSafariTested':False}
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) if engine=='chromium' else p.webkit.launch()
  for name,w,h in [('desktop',1440,1000),('tablet',768,1024),('mobile',390,844)]:
   context=browser.new_context(viewport={'width':w,'height':h},has_touch=w<1024);page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else None)
   page.goto(BASE+'/guitars?brand=Yamaha&max=30000',wait_until='networkidle');expect(page.locator('.catalog-result-count')).to_contain_text('17')
   actual=set(page.locator('.catalog-grid article[data-guitar-id]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)'))
   page.locator('.catalog-pagination').get_by_role('button',name='หน้าถัดไป',exact=True).click();expect(page.locator('.catalog-grid article')).to_have_count(8)
   actual.update(page.locator('.catalog-grid article[data-guitar-id]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)'));assert actual==expected
   for query,ids in [('min=15500&max=15500',{'yamaha-fgx800c','yamaha-fsx800c'}),('min=34000&max=34000',{'yamaha-pacifica-612viifm'}),('min=70000',set())]:
    page.goto(BASE+'/guitars?brand=Yamaha&'+query,wait_until='networkidle');expect(page.locator('main h1')).to_be_visible();actual2=set(page.locator('.catalog-grid article[data-guitar-id]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)'));assert actual2==ids,(query,actual2,ids)
   assert 'yamaha-fg800j' not in actual and 'yamaha-fgx830c' not in actual
   report['checks'].append({'engine':engine,'viewport':name,'passed':True,'knownUnder30000':sorted(actual),'boundaries':[15500,34000,70000],'unknownPricesExcluded':True})
   print('PASS',engine,name,'17 confirmed prices and inclusive boundaries',flush=True);context.close()
  browser.close()
report['passed']=len(report['checks'])==6 and not report['errors'];(ROOT/'docs/yamaha-import/tests/price-filters.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise SystemExit(not report['passed'])
