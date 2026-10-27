"""Actual final UI acceptance; product/chord/score fixtures are not rewritten."""
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright,expect
import argparse,hashlib,importlib.util,json,re,traceback
ROOT=Path(__file__).resolve().parents[3]
DIR=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',required=True,type=Path);p.add_argument('--engines',nargs='+',default=['chromium','webkit']);p.add_argument('--viewports',nargs='+',default=['desktop','landscape','tablet','mobile']);p.add_argument('--cases',nargs='+',default=['home','catalog','layout','practice-library','practice42','camera','fallback']);a=p.parse_args();BASE=a.url.rstrip('/');OUT=a.output;OUT.mkdir(parents=True,exist_ok=True)
SIZES={'desktop':(1440,1000),'landscape':(1194,834),'tablet':(768,1024),'mobile':(390,844),'portrait-edge':(1024,1366)}
records=json.loads((DIR/'catalog-fixture.json').read_text());byid={g['id']:g for g in records}
old_public=json.loads((ROOT/'docs/home-editorial-refinement/tests/catalog-fixture.json').read_text())
expected_featured=['yamaha-pacifica-612viifm','martin-d-28','yamaha-fg820-12']+[g['id'] for g in old_public if g['featured'] and g['id'] not in ['yamaha-pacifica-612viifm','martin-d-28','yamaha-fg820-12']]
spec=importlib.util.spec_from_file_location('practice_probes',DIR/'practice-probes.py');practice=importlib.util.module_from_spec(spec);spec.loader.exec_module(practice)
sha=lambda b:hashlib.sha256(b).hexdigest()
def snapshot():return {str(f.relative_to(ROOT)):sha(f.read_bytes()) for d in ['src','dist'] for f in (ROOT/d).rglob('*') if f.is_file()}
start=snapshot();ACTIVE=None;EXPECTED_WEBGL=False
report={'baseURL':BASE,'checks':[],'consoleErrors':[],'runtimeErrors':[],'networkErrors':[],'failedRequests':[],'expectedInjectedWebGLErrors':[],'screenshots':[],'physicalIPadSafariTested':False,'sourceAndBuildSHA256':start}
def check(name,fn,page):
 global ACTIVE
 ACTIVE=name
 try:
  evidence=fn();unavailable=isinstance(evidence,dict) and evidence.get('notTested',False);report['checks'].append({'case':name,'passed':None if unavailable else True,'outcome':'unavailable-native-webgl2' if unavailable else 'passed','evidence':evidence});print('UNAVAILABLE' if unavailable else 'PASS',name,flush=True)
 except Exception:
  e=traceback.format_exc();f=name+'-FAIL.png'
  try:page.screenshot(path=str(OUT/f),full_page=True,animations='disabled',timeout=60000)
  except Exception:pass
  report['checks'].append({'case':name,'passed':False,'error':e,'url':page.url,'screenshot':f});print('FAIL',name,e,flush=True)
 (OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def attach(page):
 def console(m):
  if m.type!='error':return
  item={'case':ACTIVE,'text':m.text}
  if EXPECTED_WEBGL and 'Error creating WebGL context' in m.text:report['expectedInjectedWebGLErrors'].append(item)
  else:report['consoleErrors'].append(item)
 page.on('console',console);page.on('pageerror',lambda e:report['runtimeErrors'].append({'case':ACTIVE,'text':str(e)}));page.on('requestfailed',lambda r:report['failedRequests'].append({'case':ACTIVE,'url':r.url,'failure':r.failure}));page.on('response',lambda r:report['networkErrors'].append({'case':ACTIVE,'url':r.url,'status':r.status}) if r.status>=400 else None)
def go(page,path='/'):
 page.goto(BASE+path,wait_until='networkidle');page.evaluate('document.fonts.ready');expect(page.locator('main h1')).to_be_visible()
def metrics(page):
 m=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll("main h1").length})');assert m['scrollWidth']<=m['width']+1,m;assert m['h1']==1,m;return m
def decode(im):
 im.scroll_into_view_if_needed();im.evaluate('(i)=>i.decode()');d=im.evaluate('(i)=>({src:i.currentSrc,w:i.naturalWidth,h:i.naturalHeight,fit:getComputedStyle(i).objectFit})');assert d['w']>0 and d['h']>0 and d['fit'] in ['contain','cover'],d;return d
def shot(page,selector,name):
 el=page.locator(selector);expect(el).to_be_visible()
 for im in el.locator('img').all():
  if im.is_visible():decode(im)
 page.locator('.signature-collection-track').evaluate_all('ns=>ns.forEach(n=>n.scrollLeft=0)')
 el.evaluate('e=>scrollBy(0,e.getBoundingClientRect().top-document.querySelector(".site-header").getBoundingClientRect().height-12)')
 page.screenshot(path=str(OUT/name),animations='disabled');report['screenshots'].append(name)
def home(page,engine,size):
 go(page)
 group=page.locator('#home-features');grid=page.locator('#home-features.home-feature-grid,#home-features .home-feature-grid');expect(grid).to_have_count(1)
 assert grid.locator(':scope > *').count()==3
 assert grid.locator(':scope > [data-home-practice-card]').count()==1
 assert grid.locator(':scope > #find').count()==1 and grid.locator(':scope > #compare').count()==1
 assert page.locator('#guitar-modes,[data-home-feature-card="search"],[data-home-feature-card="compare"]').count()==0
 assert page.locator('#find').count()==page.locator('#compare').count()==1
 practice_card=grid.locator('[data-home-practice-card]');expect(practice_card.locator('h2')).to_have_text('โหมดฝึกกีตาร์');expect(practice_card.locator('p')).to_contain_text('ฝึกจับคอร์ดและเรียนรู้ตำแหน่งนิ้ว ตั้งแต่พื้นฐานจนถึงขั้นสูง')
 practice_link=practice_card if practice_card.get_attribute('href') else practice_card.locator('a[href="/practice"]')
 expect(practice_link).to_have_attribute('href','/practice');expect(practice_link).to_contain_text('เริ่มฝึกกีตาร์');practice_photo=decode(practice_card.locator('img'))
 originals=[('find','/find-my-guitar','03 / FIND MY GUITAR','กีตาร์ที่ใช่เริ่มจากตัวคุณ','5 คำถามสั้น ๆ เพื่อค้นหากีตาร์ที่เข้ากับสไตล์ของคุณ','เริ่มค้นหากีตาร์','electric-studio-'),('compare','/compare','04 / SIDE BY SIDE','มองเห็นความต่างก่อนตัดสินใจ','เลือก 2–4 รุ่น แล้ววางรายละเอียดข้างกัน ค่อย ๆ ดูว่าอะไรสำคัญกับการเล่นของคุณ','เริ่มเปรียบเทียบ','quiz-studio-')]
 retained=[]
 for key,href,eyebrow,title,body,action,photo_prefix in originals:
  c=grid.locator('#'+key);expect(c).to_have_class(re.compile('home-editorial--'+key));expect(c.locator('.signature-section-eyebrow')).to_have_text(eyebrow)
  assert c.locator('h2').text_content()==title
  expect(c.locator('.home-editorial-description')).to_have_text(body)
  link=c.locator('.home-editorial-cta');expect(link).to_have_attribute('href',href);expect(link).to_contain_text(action)
  assert link.count()==1 and c.locator('a').count()==1
  bg=link.evaluate('(e)=>getComputedStyle(e).backgroundImage');assert 'linear-gradient' in bg and '237, 202, 128' in bg and '221, 180, 107' in bg,bg
  photo=decode(c.locator('.home-editorial-photo img'));assert photo_prefix in photo['src'],photo
  retained.append({'section':key,'originalEyebrow':eyebrow,'originalTitle':title,'originalBody':body,'originalAction':action,'originalPhoto':photo,'goldCTA':bg})
 cards=[practice_card,grid.locator('#find'),grid.locator('#compare')]
 r=[c.bounding_box() for c in cards];big,search,comp=r;w=page.viewport_size['width'];h=page.viewport_size['height'];stack=w<1024 or (h>w and w<=1366)
 for rect in r:assert rect['width']>=44 and rect['height']>=44
 if not stack:
  assert big['width']>search['width'] and big['height']>search['height']
  assert abs(big['y']-search['y'])<2 and abs(big['y']+big['height']-comp['y']-comp['height'])<2,r
  assert big['x']+big['width']<search['x'] and abs(search['x']-comp['x'])<2,r
 else:assert big['y']+big['height']<=search['y'] and search['y']+search['height']<=comp['y'],r
 assert group.evaluate('(e)=>e.nextElementSibling?.id')=='featured','Featured must immediately follow the three-card group'
 assert page.locator('#featured .guitar-card').evaluate_all('n=>n.map(x=>x.dataset.guitarId)')==expected_featured
 assert page.locator('#featured [role=tab]').count()==4
 assert page.locator('.signature-hero-slide').count()==3
 assert page.locator('.signature-category-card').count()==4
 assert page.locator('.signature-stats-list dd').all_text_contents()==['200','10','4','4']
 assert page.locator('#find input,#find form,#compare table').count()==0
 expect(page.locator('.site-footer a[href="/image-credits"]')).to_have_count(1)
 metrics(page);shot(page,'#home-features',f'{engine}-{size}-home-features.png')
 group.screenshot(path=str(OUT/f'{engine}-{size}-home-features-complete.png'),animations='disabled');report['screenshots'].append(f'{engine}-{size}-home-features-complete.png')
 shot(page,'#featured',f'{engine}-{size}-home.png')
 for key,href,selector in [('practice','/practice','[data-home-practice-card]'),('find','/find-my-guitar','#find .home-editorial-cta'),('compare','/compare','#compare .home-editorial-cta')]:
  go(page);link=page.locator(selector)
  if key=='practice' and not link.get_attribute('href'):link=link.locator('a[href="/practice"]')
  link.click();assert urlparse(page.url).path==href
  if key=='practice':
   expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord','C')
   expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status',re.compile('^(ready|error)$'),timeout=60000)
   if page.locator('[data-practice-status]').get_attribute('data-practice-status')=='ready':expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
  if key=='find':expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow','1');expect(page.locator('input[name="type"]')).to_have_count(5)
  if key=='compare':expect(page.locator('[data-compare-empty-slot]')).to_have_count(4)
  metrics(page)
 return {'routes':['/practice','/find-my-guitar','/compare'],'geometry':'stacked' if stack else 'large-left-two-right','rectangles':r,'originalFindCompareRetained':retained,'practicePhoto':practice_photo,'featuredOriginalIDs':expected_featured,'featuredImmediatelyAfterGroup':True,'actualCountsRetained':True,'all3ImagesDecoded':True}
def ids(page):return page.locator('#catalog-results [data-guitar-id]').evaluate_all('n=>n.map(x=>x.dataset.guitarId)')
def catalog(page,engine,size):
 go(page,'/guitars');expect(page.locator('.catalog-cinematic-photo img')).to_have_count(1);photo=decode(page.locator('.catalog-cinematic-photo img'));assert page.locator('.catalog-data-note').count()==0
 assert len(ids(page))==9
 expect(page.locator('.catalog-result-count')).to_contain_text('200')
 field=page.locator('#catalog-search');field.fill('FG820-12');expect(page.locator('#catalog-results [data-guitar-id]')).to_have_count(1);assert ids(page)==['yamaha-fg820-12'];field.press('Enter');assert parse_qs(urlparse(page.url).query)['q']==['FG820-12'];field.fill('');expect(page.locator('#catalog-results [data-guitar-id]')).to_have_count(9)
 page.locator('.catalog-categories button').last.click();assert parse_qs(urlparse(page.url).query)['type']==['bass'];expect(page.locator('.catalog-result-count')).to_contain_text('17');assert all(byid[x]['category']=='bass' for x in ids(page))
 page.get_by_role('button',name='หน้าถัดไป',exact=True).click();assert parse_qs(urlparse(page.url).query)['page']==['2'];expect(page.locator('#catalog-results [data-guitar-id]')).to_have_count(8);assert all(byid[x]['category']=='bass' for x in ids(page));page.get_by_role('button',name='หน้าก่อนหน้า',exact=True).click()
 go(page,'/guitars');select=page.locator('.catalog-toolbar select');sorts={}
 for direction in ['price-asc','price-desc']:
  select.select_option(direction);assert parse_qs(urlparse(page.url).query)['sort']==[direction]
  expected=sorted(records,key=lambda g:(g['price'] is None,(g['price'] or 0)*(1 if direction=='price-asc' else -1)))[:9]
  assert ids(page)==[g['id'] for g in expected],(direction,ids(page),expected);sorts[direction]=ids(page)
 go(page,'/guitars');drawer=page.viewport_size['width']<1024
 if drawer:
  page.locator('.catalog-filter-trigger').click();panel=page.get_by_role('dialog',name='ตัวกรอง',exact=True);expect(panel).to_be_visible()
 else:panel=page.locator('.catalog-sidebar')
 checkbox=panel.get_by_role('checkbox',name=re.compile('Yamaha'));checkbox.locator('..').click();expect(checkbox).to_be_checked();assert parse_qs(urlparse(page.url).query)['brand']==['Yamaha'];expect(page.locator('.catalog-result-count')).to_contain_text('20')
 upper=panel.get_by_role('slider').nth(1);upper.focus();upper.press('Home')
 for _ in range(10):upper.press('ArrowRight')
 assert parse_qs(urlparse(page.url).query)['max']==['10000']
 if drawer:panel.get_by_role('button',name=re.compile('แสดง.*รุ่น')).click()
 known=[g for g in records if g['brand']=='Yamaha' and g['price'] is not None and g['price']<=10000]
 expect(page.locator('.catalog-result-count')).to_contain_text(str(len(known)));assert all(byid[x]['brand']=='Yamaha' and 0<byid[x]['price']<=10000 for x in ids(page));metrics(page)
 go(page,'/guitars?q=FG820-12');card=page.locator('[data-guitar-id="yamaha-fg820-12"]');expect(card).to_have_count(1);im=card.locator('img');assert im.count()==1;decode(im)
 wish=card.get_by_role('button',name=re.compile('รายการโปรด'));wish.click();expect(wish).to_have_attribute('aria-pressed','true');assert 'yamaha-fg820-12' in page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))');wish.click();expect(wish).to_have_attribute('aria-pressed','false')
 compare=card.locator('.catalog-card-actions button');compare.click();expect(compare).to_have_attribute('aria-pressed','true');assert 'yamaha-fg820-12' in page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))');compare.click();expect(compare).to_have_attribute('aria-pressed','false')
 card.get_by_role('link',name='ดูรายละเอียด',exact=True).click();expect(page).to_have_url(re.compile('/guitars/yamaha-fg820-12$'));expect(page.locator('main h1')).to_contain_text('FG820-12')
 go(page,'/guitars');shot(page,'.catalog-cinematic-hero',f'{engine}-{size}-catalog.png');return {'licensedHeroPhoto':photo,'removedLongNote':True,'actualCatalogCount':200,'search':True,'typeCount':17,'pagination':True,'sorts':sorts,'brandAndRealBudget':len(known),'wishlistCompareDetailActions':True,**metrics(page)}
def layout(page,engine,size):
 paths=['/','/guitars','/find-my-guitar','/find-my-guitar?step=3','/compare?ids=','/compare?ids=yamaha-fg820-12,martin-d-28','/practice'];rows=[]
 for path in paths:
  go(page,path);rows.append({'route':path,**metrics(page)})
  if path=='/find-my-guitar':assert page.locator('.quiz-hero-actions,.quiz-bottom-note,.quiz-editorial-credit').count()==0;expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow','1')
  if path=='/compare?ids=':assert page.locator('.pc-empty-state,.pc-data-note').count()==0;expect(page.locator('[data-compare-empty-slot]')).to_have_count(4)
  if path=='/practice':
   assert page.locator('.practice-intro-aside,.practice-keyboard-hint,.practice-preview-note').count()==0
   expect(page.locator('[data-practice-chord]')).to_have_count(42)
   expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status',re.compile('^(ready|error)$'),timeout=60000)
   if page.locator('[data-practice-status]').get_attribute('data-practice-status')=='ready':expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
   for forbidden in ['กำลังโหลดโมเดลมือ','YOUR PRACTICE SPACE','THE ART OF YOUR NEXT CHORD']:
    assert forbidden not in page.locator('main').inner_text(),forbidden
  if path=='/find-my-guitar':
   page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'{engine}-{size}-quiz-top.png'),animations='disabled');report['screenshots'].append(f'{engine}-{size}-quiz-top.png')
  if path=='/compare?ids=yamaha-fg820-12,martin-d-28':shot(page,'.pc-workspace',f'{engine}-{size}-compare-selected.png')
  for key,sel in [('quiz-question','.quiz-studio-panel'),('compare-empty','.pc-workspace'),('practice','.practice-studio')]:
   if (key=='quiz-question' and path=='/find-my-guitar') or (key=='compare-empty' and path=='/compare?ids=') or (key=='practice' and path=='/practice'):
    shot(page,sel,f'{engine}-{size}-{key}.png')
 return rows
with sync_playwright() as p:
 for engine in a.engines:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']) if engine=='chromium' else p.webkit.launch()
  report.setdefault('browserVersions',{})[engine]=browser.version
  for size in a.viewports:
   w,h=SIZES[size];context=browser.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion='reduce');page=context.new_page();attach(page)
   if 'home' in a.cases:check(f'{engine}-{size}-home-restored-three-card-group',lambda:home(page,engine,size),page)
   if 'catalog' in a.cases:check(f'{engine}-{size}-catalog-interactions',lambda:catalog(page,engine,size),page)
   if 'layout' in a.cases:check(f'{engine}-{size}-all-pages-layout',lambda:layout(page,engine,size),page)
   if 'practice-library' in a.cases:check(f'{engine}-{size}-practice-library-navigation',lambda:practice.practice_filters_navigation(page,BASE,engine),page)
   if size=='desktop':
    if 'practice42' in a.cases:check(f'{engine}-practice-all42-accuracy',lambda:practice.practice_all_chords(page,BASE,engine,OUT),page)
    if 'camera' in a.cases:check(f'{engine}-practice-camera-controls',lambda:practice.practice_camera(page,BASE,engine,OUT),page)
   context.close()
  if 'fallback' in a.cases:
   EXPECTED_WEBGL=True;context=browser.new_context(viewport={'width':390,'height':844},has_touch=True,reduced_motion='reduce');page=context.new_page();attach(page);check(f'{engine}-practice-injected-webgl-fallback',lambda:practice.practice_webgl_fallback(page,BASE,engine,OUT),page);context.close();EXPECTED_WEBGL=False
  browser.close()
report['sourceAndBuildUnchangedDuringRun']=snapshot()==start
report['passed']=all(c['passed'] is not False for c in report['checks']) and report['sourceAndBuildUnchangedDuringRun'] and not any(report[k] for k in ['consoleErrors','runtimeErrors','networkErrors','failedRequests'])
(OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('FINAL',sum(c['passed'] is True for c in report['checks']),'/',len(report['checks']),report['passed'],flush=True)
raise SystemExit(0 if report['passed'] else 1)
