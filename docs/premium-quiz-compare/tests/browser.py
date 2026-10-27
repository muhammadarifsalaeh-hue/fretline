"""Real browser acceptance for Premium Quiz/Compare; scoring baselines are immutable."""
from pathlib import Path
from urllib.parse import urlencode,urlparse,parse_qs,urljoin
from playwright.sync_api import sync_playwright,expect
import argparse,json,hashlib,re,traceback
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--engines',nargs='+',default=['chromium','webkit']);p.add_argument('--viewports',nargs='+',default=['desktop','tablet','mobile']);p.add_argument('--cases',nargs='+',default=['quiz-options','quiz-flow','results','compare','responsive','regression']);args=p.parse_args();BASE=args.url.rstrip('/');OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
fixtures=json.loads((ROOT/'docs/premium-quiz-compare/tests/browser-fixtures.json').read_text());records=json.loads((ROOT/'src/data/catalog/reviewedGuitars.json').read_text());rights=json.loads((ROOT/'src/data/catalog/imageRights.json').read_text());art=json.loads((ROOT/'src/data/catalog/projectArtwork.json').read_text())
STEPS={'type':['electric','acoustic','classical','bass','any'],'level':['beginner','intermediate','advanced'],'style':['rock','blues','pop','folk','classical'],'budget':['low','mid','high','premium','flex'],'priority':['light','versatile','premium','value']}
IDS=['yamaha-pacifica-612viifm','yamaha-fg800','yamaha-fg820-12','martin-d-28'];FIFTH='fender-american-professional-ii-stratocaster'
VIEWPORTS={'desktop':(1440,1000),'tablet':(768,1024),'mobile':(390,844)}
def sha(b):return hashlib.sha256(b).hexdigest()
def snapshot():
 return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for folder in ['src','dist/assets'] for p in (ROOT/folder).rglob('*') if p.is_file() and (folder!='src' or p.suffix in ['.js','.jsx','.json','.css'])}
start=snapshot();report={'baseURL':BASE,'checks':[],'consoleErrors':[],'runtimeErrors':[],'failedRequests':[],'networkErrors':[],'screenshots':[],'physicalIPadSafariTested':False,'sourceAndBuildSHA256':start,'note':'Linux WebKit and synthetic touch do not certify native iPad Safari. Generic licensed scene photography is never accepted as a selected guitar model photo.'};ACTIVE=None

def check(name,fn,page):
 global ACTIVE
 ACTIVE=name
 try:
  evidence=fn();report['checks'].append({'case':name,'passed':True,'evidence':evidence});print('PASS',name,flush=True)
 except Exception:
  failure=traceback.format_exc();file=name+'-FAIL.png'
  try:page.screenshot(path=str(OUT/file),full_page=True,animations='disabled')
  except Exception:pass
  report['checks'].append({'case':name,'passed':False,'failure':failure,'url':page.url,'screenshot':file});print('FAIL',name,failure,flush=True)

def go(page,path):
 r=page.goto(BASE+path,wait_until='networkidle');expect(page.locator('main h1')).to_be_visible();page.evaluate('document.fonts.ready');return r

def metrics(page):
 m=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll("main h1").length})');assert m['scrollWidth']<=m['width']+1,m;assert m['h1']==1,m;return m

def no_marketing(page):
 text=page.locator('main').inner_text();assert not re.search(r'\bAI\s*(?:Generated|Edited)|Powered\s+by\s+AI|ออกแบบด้วย\s*AI',text,re.I),text[:400]

def decode_image(im):
 im.scroll_into_view_if_needed();expect(im).to_be_visible();im.evaluate('(i)=>i.decode()');expected_opacity='0.72' if im.evaluate('(i)=>!!i.closest(".pc-hero__photograph") && matchMedia("(max-width:599px)").matches') else '1';expect(im).to_have_css('opacity',expected_opacity);data=im.evaluate('''i=>({src:i.getAttribute('src'),currentSrc:i.currentSrc,width:i.naturalWidth,height:i.naturalHeight,fit:getComputedStyle(i).objectFit,loading:i.loading,clientWidth:i.clientWidth,clientHeight:i.clientHeight})''');assert data['width']>0 and data['height']>0,data;return data

def scene_images(page):
 rows=[]
 for im in page.locator('main img').all():
  if im.get_attribute('src') and im.is_visible():
   info=decode_image(im);assert info['fit'] in ['cover','contain'],info;rows.append(info)
 return rows

def shot(page,name):
 scene_images(page);page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/name),full_page=True,animations='disabled');report['screenshots'].append(name)

def select_radio(page,name,value):
 radio=page.locator(f'input[type="radio"][name="{name}"][value="{value}"]');expect(radio).to_have_count(1);radio.locator('..').click();expect(radio).to_be_checked();assert parse_qs(urlparse(page.url).query).get(name)==[value]

def quiz_options(page,engine,viewport):
 go(page,'/find-my-guitar');expect(page.locator('.premium-quiz')).to_be_visible();intro=scene_images(page);assert page.locator('main img').count()>=4,('Hero and three actual editorial image elements required',page.locator('main img').count());assert len(intro)>=1,('A real hero photo must remain visible',len(intro));no_marketing(page);metrics(page);shot(page,f'{engine}-{viewport}-quiz-welcome.png')
 seen={}
 for index,(name,values) in enumerate(STEPS.items(),1):
  go(page,'/find-my-guitar?step='+str(index));expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow',str(index));inputs=page.locator(f'input[type="radio"][name="{name}"]');actual=inputs.evaluate_all('(nodes)=>nodes.map(n=>n.value)');assert actual==values,(name,actual,values)
  expect(page.get_by_role('button',name='ดูผลแนะนำ' if index==5 else 'ถัดไป',exact=True)).to_be_disabled()
  for value in values:select_radio(page,name,value)
  seen[name]=actual;metrics(page)
 return {'allOriginal22OptionValues':seen,'originalCounts':[len(v) for v in seen.values()],'realSceneImageCount':len(intro)}

def assert_results(page,fixture):
 expect(page.locator('.quiz-results-page')).to_be_visible();cards=page.locator('.match-card[data-guitar-id]');expected=fixture['matches'];expect(cards).to_have_count(len(expected));ids=cards.evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)');assert ids==[m['id'] for m in expected],(ids,expected)
 for imatch,match in enumerate(expected):
  card=cards.nth(imatch);expect(card).to_contain_text(match['name']);expect(card.locator('.match-score')).to_contain_text(str(match['score'])+'%');text=card.text_content()
  for reason in match['reasons']:assert reason in text,(match['id'],reason)
  for caveat in match['caveats']:assert caveat in text,(match['id'],caveat)
  if match['price'] is not None:expect(card).to_contain_text('฿'+format(match['price'],','))
 no_marketing(page);metrics(page);return {'ids':ids,'scores':[m['score'] for m in expected],'allBaselineReasonsAndCaveatsRetained':True}

def quiz_flow(page,engine,viewport):
 fixture=fixtures['cases'][0];go(page,'/find-my-guitar');page.get_by_role('button',name='เริ่มค้นหากีตาร์',exact=True).click();expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow','1')
 for index,(name,value) in enumerate(fixture['answers'].items(),1):
  expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow',str(index));select_radio(page,name,value)
  if index==1:shot(page,f'{engine}-{viewport}-quiz-step1.png')
  if index==3:
   page.get_by_role('button',name='ก่อนหน้า',exact=True).click();expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow','2');expect(page.locator('input[name="level"][value="beginner"]')).to_be_checked();page.get_by_role('button',name='ถัดไป',exact=True).click();expect(page.locator('input[name="style"][value="folk"]')).to_be_checked()
  page.get_by_role('button',name='ดูผลแนะนำ' if index==5 else 'ถัดไป',exact=True).click()
 evidence=assert_results(page,fixture);assert 'step' not in parse_qs(urlparse(page.url).query);shot(page,f'{engine}-{viewport}-quiz-results.png')
 page.go_back(wait_until='networkidle');expect(page.locator('input[name="priority"][value="value"]')).to_be_checked();page.get_by_role('button',name='ดูผลแนะนำ',exact=True).click();assert_results(page,fixture)
 page.get_by_role('button',name='แก้ไขคำตอบ',exact=True).click();expect(page.locator('input[name="type"][value="acoustic"]')).to_be_checked();go(page,'/find-my-guitar?'+urlencode(fixture['answers']));page.get_by_role('button',name='ทำแบบสอบถามใหม่',exact=True).click();assert not parse_qs(urlparse(page.url).query);expect(page.get_by_role('button',name='เริ่มค้นหากีตาร์',exact=True)).to_be_visible()
 return {**evidence,'fiveSteps':True,'previousRestoresAnswer':True,'browserBackRestoresAnswer':True,'editAndRetake':True}

def result_fixtures(page):
 rows=[]
 for fixture in fixtures['cases']:
  go(page,'/find-my-guitar?'+urlencode(fixture['answers']));rows.append({'answers':fixture['answers'],**assert_results(page,fixture)})
 return rows

def selected_ids(page):return page.locator('[data-compare-card]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.compareCard)')

def audit_product_images(page,context):
 rows=[]
 for gid in selected_ids(page):
  card=page.locator(f'[data-compare-card="{gid}"]');expect(card).to_contain_text(records[gid]['name']);price=records[gid].get('price')
  if price is not None:expect(card).to_contain_text('฿'+format(price,','))
  images=card.locator('img');available=(rights.get(gid) or [])+(art.get(gid,{}).get('images') or [])
  if not available:assert images.count()==0,(gid,'Never use editorial scene as a missing model photo');rows.append({'id':gid,'honestMissingModelFallback':True});continue
  expect(images).to_have_count(1);info=decode_image(images.first);assert info['fit']=='contain',info;body=context.request.get(urljoin(BASE,info['src'])).body();digest=sha(body);assert digest in {image['sha256'] for image in available},(gid,info['src'],digest);assert not re.search(r'discovery|quiz-hero|compare-hero',info['src']);rows.append({'id':gid,'sha256':digest,**info})
 return rows

def compare_case(page,context,engine,viewport):
 go(page,'/compare?ids=');expect(page.locator('.premium-compare')).to_be_visible();expect(page.locator('[data-compare-remove]')).to_have_count(0);expect(page.locator('[data-compare-empty-slot]')).to_have_count(4);expect(page.get_by_role('button',name='แชร์ลิงก์',exact=True)).to_be_disabled();expect(page.get_by_role('button',name='ล้างการเปรียบเทียบ',exact=True)).to_be_disabled();scene=scene_images(page);assert scene, 'Real atmospheric scene file required';no_marketing(page);metrics(page);shot(page,f'{engine}-{viewport}-compare-empty.png')
 page.get_by_role('button',name='เพิ่มกีตาร์',exact=True).first.click();dialog=page.get_by_role('dialog',name='เพิ่มกีตาร์',exact=True);expect(dialog).to_be_visible();search=dialog.get_by_role('searchbox');expect(search).to_be_focused();page.keyboard.press('Tab');assert page.evaluate('document.activeElement.closest("[role=dialog]")!==null');page.keyboard.press('Escape');expect(dialog).to_have_count(0)
 page.get_by_role('button',name='เพิ่มกีตาร์',exact=True).first.click();dialog=page.get_by_role('dialog',name='เพิ่มกีตาร์',exact=True);search=dialog.get_by_role('searchbox')
 for gid in IDS:
  search.fill(records[gid]['name']);row=dialog.locator('.picker-model-row').filter(has=page.get_by_text(records[gid]['name'],exact=True));expect(row).to_have_count(1);row.click();expect(row).to_have_attribute('aria-pressed','true')
 search.fill(records[FIFTH]['name']);row=dialog.locator('.picker-model-row').filter(has=page.get_by_text(records[FIFTH]['name'],exact=True));expect(row).to_be_disabled();dialog.get_by_role('button',name='เสร็จสิ้น',exact=True).click();expect(dialog).to_have_count(0);expect(page.locator('[data-compare-remove]')).to_have_count(4);assert selected_ids(page)==IDS;expect(page.locator('[data-compare-empty-slot]')).to_have_count(0);expect(page.get_by_role('button',name='ครบ 4 รุ่นแล้ว',exact=True)).to_be_disabled();assert page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))')==IDS
 evidence=audit_product_images(page,context);tabs=page.locator('[data-compare-category]');assert tabs.count()==6;category_rows={}
 for key in ['main','sound','materials','hardware','dimensions','all']:
  tab=page.locator(f'[data-compare-category="{key}"]');tab.click();expect(tab).to_have_attribute('aria-selected','true');table=page.get_by_role('table');expect(table).to_be_visible();keys=table.locator('[data-compare-row]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.compareRow)');assert keys,(key,'Functional category must expose real rows');category_rows[key]=keys;metrics(page)
 assert len(category_rows['all'])>=len(category_rows['main']);assert category_rows['sound']!=category_rows['materials']
 page.locator('[data-compare-category="main"]').focus();page.keyboard.press('ArrowRight');expect(page.locator('[data-compare-category="sound"]')).to_have_attribute('aria-selected','true');page.keyboard.press('End');expect(page.locator('[data-compare-category="all"]')).to_have_attribute('aria-selected','true');page.keyboard.press('Home');expect(page.locator('[data-compare-category="main"]')).to_have_attribute('aria-selected','true')
 differences=page.get_by_role('switch',name='แสดงเฉพาะส่วนที่ต่างกัน',exact=True);differences.click();expect(differences).to_have_attribute('aria-checked','true');differences.click();expect(differences).to_have_attribute('aria-checked','false');samples=page.get_by_role('switch',name='แสดงข้อมูลตัวอย่าง',exact=True);samples.click();expect(samples).to_have_attribute('aria-checked','true');samples.click();expect(samples).to_have_attribute('aria-checked','false')
 if viewport!='desktop':
  region=page.locator('.compare-table-scroll');before=region.evaluate('(e)=>({left:e.scrollLeft,width:e.clientWidth,scroll:e.scrollWidth})');region.evaluate('(e)=>{e.scrollLeft=e.scrollWidth}');after=region.evaluate('(e)=>e.scrollLeft');assert before['scroll']>before['width'] and after>0,(before,after);region.evaluate('(e)=>e.scrollLeft=0')
 page.get_by_role('button',name='แชร์ลิงก์',exact=True).click();link=page.locator('.share-link-control input');expect(link).to_be_visible();shared=link.input_value();assert parse_qs(urlparse(shared).query)['ids'][0].split(',')==IDS;expect(link).to_be_focused();shot(page,f'{engine}-{viewport}-compare-four.png')
 first=page.locator('[data-compare-remove="'+IDS[0]+'"]');first.click();expect(page.locator('[data-compare-remove]')).to_have_count(3);assert selected_ids(page)==IDS[1:];metrics(page);shot(page,f'{engine}-{viewport}-compare-three.png');page.go_back(wait_until='networkidle');expect(page.locator('[data-compare-remove]')).to_have_count(4);assert selected_ids(page)==IDS;page.go_forward(wait_until='networkidle');expect(page.locator('[data-compare-remove]')).to_have_count(3);page.reload(wait_until='networkidle');assert selected_ids(page)==IDS[1:]
 page.get_by_role('button',name='ล้างการเปรียบเทียบ',exact=True).click();confirm=page.get_by_role('alertdialog');expect(confirm).to_be_visible();confirm.get_by_role('button',name='ยกเลิก',exact=True).click();expect(confirm).to_have_count(0);expect(page.locator('[data-compare-remove]')).to_have_count(3)
 page.get_by_role('button',name='ล้างการเปรียบเทียบ',exact=True).click();confirm=page.get_by_role('alertdialog');confirm.get_by_role('button',name='ยืนยันล้างรายการ',exact=True).click();expect(confirm).to_have_count(0);expect(page.locator('[data-compare-remove]')).to_have_count(0);assert page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))')==[]
 go(page,'/compare?ids='+','.join(IDS+[FIFTH,IDS[0],'made-up-model']));expect(page.locator('[data-compare-remove]')).to_have_count(4);assert selected_ids(page)==IDS;no_marketing(page);metrics(page)
 return {'actualModelPhotos':evidence,'all6FunctionalCategories':category_rows,'addFourAndFifthDisabled':True,'shareFallbackURL':shared,'removeBackForwardReloadClearCancelConfirm':True,'keyboardModalAndTabs':True}

def clipboard_success(page):
 page.context.grant_permissions(['clipboard-read','clipboard-write']);go(page,'/compare?ids='+','.join(IDS[:2]));page.get_by_role('button',name='แชร์ลิงก์',exact=True).click();value=page.evaluate('navigator.clipboard.readText()');assert parse_qs(urlparse(value).query)['ids'][0].split(',')==IDS[:2];assert page.locator('.share-link-control input').count()==0
 return {'actualBrowserClipboardURL':value,'fallbackNotNeeded':True}

def responsive_case(page):
 rows=[]
 for w,h in [(320,740),(1024,768),(834,1194),(1194,834)]:
  page.set_viewport_size({'width':w,'height':h})
  for path in ['/find-my-guitar','/find-my-guitar?step=3','/compare?ids='+','.join(IDS)]:
   go(page,path);rows.append({'url':path,**metrics(page)})
 return rows

def regression_case(page):
 rows=[]
 for path in ['/','/brands','/guitars?brand=Yamaha','/guitars/yamaha-fg820-12','/wishlist']:
  go(page,path);rows.append({'url':path,**metrics(page)})
 return rows

with sync_playwright() as p:
 for engine in args.engines:
  browser=None
  try:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) if engine=='chromium' else p.webkit.launch()
   report.setdefault('browserVersions',{})[engine]=browser.version
   for viewport in args.viewports:
    w,h=VIEWPORTS[viewport];context=browser.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion='reduce');context.add_init_script('''Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new Error('Test clipboard denied')}}});''');page=context.new_page()
    page.on('console',lambda m:report['consoleErrors'].append({'case':ACTIVE,'text':m.text}) if m.type=='error' else None);page.on('pageerror',lambda e:report['runtimeErrors'].append({'case':ACTIVE,'text':str(e)}));page.on('requestfailed',lambda r:report['failedRequests'].append({'case':ACTIVE,'url':r.url,'failure':r.failure}));page.on('response',lambda r:report['networkErrors'].append({'case':ACTIVE,'url':r.url,'status':r.status}) if r.status>=400 else None)
    if 'quiz-options' in args.cases:check(f'{engine}-{viewport}-quiz-options',lambda:quiz_options(page,engine,viewport),page)
    if 'quiz-flow' in args.cases:check(f'{engine}-{viewport}-quiz-flow',lambda:quiz_flow(page,engine,viewport),page)
    if 'results' in args.cases and viewport=='desktop':check(f'{engine}-{viewport}-six-result-fixtures',lambda:result_fixtures(page),page)
    if 'compare' in args.cases:check(f'{engine}-{viewport}-compare-interactions',lambda:compare_case(page,context,engine,viewport),page)
    if 'responsive' in args.cases and viewport=='desktop':check(f'{engine}-{viewport}-responsive-320-ipad-landscape',lambda:responsive_case(page),page)
    if 'regression' in args.cases and viewport=='desktop':check(f'{engine}-{viewport}-untouched-page-regressions',lambda:regression_case(page),page)
    context.close()
   if engine=='chromium' and 'compare' in args.cases:
    clipboard_context=browser.new_context(viewport={'width':1440,'height':1000},permissions=['clipboard-read','clipboard-write']);clipboard_page=clipboard_context.new_page();check('chromium-actual-clipboard-success',lambda:clipboard_success(clipboard_page),clipboard_page);clipboard_context.close()
  except Exception:report.setdefault('harnessFailures',[]).append({'engine':engine,'error':traceback.format_exc()});print('HARNESSFAIL',engine,report['harnessFailures'][-1]['error'],flush=True)
  finally:
   if browser:browser.close()
report['sourceAndBuildUnchangedDuringRun']=start==snapshot();report['passed']=bool(report['checks']) and all(c['passed'] for c in report['checks']) and report['sourceAndBuildUnchangedDuringRun'] and not any(report.get(k) for k in ['consoleErrors','runtimeErrors','failedRequests','networkErrors','harnessFailures']);(OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('RESULT',report['passed'],sum(c['passed'] for c in report['checks']),len(report['checks']),flush=True);raise SystemExit(not report['passed'])
