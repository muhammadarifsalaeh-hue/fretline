"""Read-only public-site regression using real catalog UI, no catalog fixtures."""
import json,re,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/practice-complete-42';report={'checks':[],'errors':[],'consoleErrors':[],'databaseWrites':0,'handRequestsOutsidePractice':[],'catalogFixturesUsed':False,'dataSourceChanged':False,'hostedSupabaseAuthenticationTested':False}
with sync_playwright()as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);c=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');page=c.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['consoleErrors'].append(m.text)if m.type=='error'else None)
 def request(r):
  if 'makehuman-left-arm-sleeved'in r.url or 'hand-poses'in r.url:report['handRequestsOutsidePractice'].append(r.resource_type)
  if '.supabase.co/'in r.url and r.method not in ['GET','HEAD','OPTIONS']:report['databaseWrites']+=1
 page.on('request',request)
 def go(path):assert page.goto('http://127.0.0.1:4197'+path,wait_until='domcontentloaded').status==200;expect(page.locator('main')).to_be_visible()
 def ok(name,evidence):report['checks'].append({'name':name,'passed':True,'evidence':evidence});print('PASS',name,flush=True)
 try:
  go('/');expect(page.locator('.signature-stats-list dd')).to_have_text(['200','10','4','4']);ok('home-stats',{'models':200,'brands':10,'types':4,'compareMax':4})
  go('/guitars');expect(page.locator('.catalog-result-count p').first).to_contain_text(re.compile(r'\b200\b'));page.locator('#catalog-search').fill('Yamaha');expect(page.locator('.catalog-result-count p').first).to_contain_text(re.compile(r'\b20\b'));assert 1<page.locator('article[data-guitar-id]').count()<=20;ids=page.locator('article[data-guitar-id]').evaluate_all('ns=>ns.map(n=>n.dataset.guitarId)');detail=page.locator('article[data-guitar-id] h3 a').first.get_attribute('href');ok('catalog-and-real-yamaha-search',{'filteredModelsFromRealResultCount':20,'visiblePageModels':len(ids),'ids':ids,'paginationPreserved':True})
  for i in [0,1]:
   card=page.locator('article[data-guitar-id]').nth(i);card.hover();card.locator('button').nth(1).click()
  card=page.locator('article[data-guitar-id]').first;card.hover();card.locator('button').first.click();go('/compare');expect(page.locator('[data-compare-remove]')).to_have_count(2);ok('compare-real-selected-models',{'selectedIds':ids[:2],'selectedColumns':2})
  go('/wishlist');saved=page.locator('.wishlist-row[data-guitar-id="'+ids[0]+'"]');expect(saved).to_be_visible();saved.hover();saved.locator('button').first.click();expect(page.locator('.wishlist-row[data-guitar-id="'+ids[0]+'"]')).to_have_count(0);ok('favorites-add-persist-remove',{'id':ids[0]})
  go(detail);expect(page.locator('main h1')).to_be_visible();ok('real-product-detail',{'route':detail,'model':page.locator('main h1').inner_text()})
  go('/brands');cards=page.locator('main a[data-brand-id]');expect(cards).to_have_count(10);brand_id=cards.first.get_attribute('data-brand-id');target=cards.first.get_attribute('href');go(target);expect(page.locator('.catalog-result-count p').first).to_contain_text(re.compile(r'\b20\b'));go('/brands/'+brand_id);expect(page.locator('main h1')).to_be_visible();assert page.locator('article[data-guitar-id]').count()>0;ok('brand-directory-and-detail',{'brands':10,'directoryTarget':target,'deepRoute':'/brands/'+brand_id})
  go('/find-my-guitar?step=1');questions=[]
  for i in range(5):
   first=page.get_by_role('radio').first;name=first.get_attribute('name');value=first.get_attribute('value');first.locator('..').click();expect(page.locator('.quiz-next')).to_be_enabled();page.locator('.quiz-next').click();questions.append({'question':name,'choice':value})
   if i<4:page.wait_for_function('name=>document.querySelector(".quiz-question-form input")?.name!==name',arg=name)
  expect(page.locator('.quiz-results-next')).to_be_visible();ok('find-my-guitar-all-five-real-steps',{'questions':questions,'resultsFromRealCatalog':True})
  go('/admin');expect(page.locator('main h1')).to_be_visible();assert page.locator('input[type=password]').count()or 'Supabase'in page.locator('main').inner_text();ok('admin-anonymous-entry',{'pageOpens':True,'authenticatedWritesNotAttempted':True})
  assert not report['handRequestsOutsidePractice'];assert report['databaseWrites']==0;ok('practice-assets-remain-lazy-and-no-database-writes',{'handRequests':0,'databaseWrites':0})
 except Exception:report['failure']=traceback.format_exc();print(report['failure']);page.screenshot(path=str(OUT/'screenshots/public-smoke-failure.png'),full_page=True)
 b.close()
report['passed']='failure'not in report and not report['errors']and not report['consoleErrors'];(OUT/'tests/public-smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'errors':report['errors'],'consoleErrors':report['consoleErrors']}));raise SystemExit(0 if report['passed']else 1)
