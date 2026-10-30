"""Real local product data and browser interactions; no database writes/mocks.
Run against a frozen production build; hosted Supabase and physical iPad are
separate acceptance checks. This suite intentionally makes no deployment.
"""
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright,expect
import argparse,hashlib,json,re,subprocess,traceback

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--url',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
BASE=args.url.rstrip('/');OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
snapshot_path=ROOT/'.local-preview/signature-experience/catalog-before.json'
if snapshot_path.exists():
 snapshot_text=snapshot_path.read_text()
else:
 # A fresh checkout need not have the ignored audit archive. Read the original
 # project modules through Vite SSR, then verify the same immutable baseline.
 source="""
 import {createServer} from 'vite';
 const server=await createServer({logLevel:'silent',server:{middlewareMode:true,hmr:false},appType:'custom'});
 try {
   const {GUITARS,SAVED_GUITARS_BY_ID}=await server.ssrLoadModule('/src/data/guitars.js');
   const {BRANDS}=await server.ssrLoadModule('/src/data/brands.js');
   const {PRACTICE_CHORDS}=await server.ssrLoadModule('/src/features/practice/data/chords.js');
   process.stdout.write(JSON.stringify({guitars:GUITARS,saved:SAVED_GUITARS_BY_ID,brands:BRANDS,chords:PRACTICE_CHORDS},null,2));
 } finally {await server.close();}
 """
 snapshot_text=subprocess.run(['node','--input-type=module','-e',source],cwd=ROOT,capture_output=True,text=True,check=True).stdout
baseline=json.loads((ROOT/'docs/signature-experience/safety-baseline.json').read_text())
assert hashlib.sha256(snapshot_text.encode()).hexdigest()==baseline['effectiveDataSHA256'],'Original product/chord baseline differs; inspect data before continuing'
snapshot=json.loads(snapshot_text);BY_ID={g['id']:g for g in snapshot['guitars']};CHORDS={c['id']:c for c in snapshot['chords']}
report={'checks':[],'consoleErrors':[],'runtimeErrors':[],'realSupabaseTested':False,'physicalIPadSafariTested':False,'data':'original project catalog, unchanged source and configuration; no HTTP mocks'}
def check(name,fn,page):
 try:result=fn();report['checks'].append({'name':name,'passed':True,'evidence':result});print('PASS',name,flush=True)
 except Exception:
  error=traceback.format_exc();report['checks'].append({'name':name,'passed':False,'error':error});print('FAIL',name,error,flush=True);page.screenshot(path=str(OUT/(name+'-FAIL.png')),animations='disabled')
 (OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def go(page,path='/'):
 page.goto(BASE+path,wait_until='networkidle');expect(page.locator('main h1')).to_be_visible();page.evaluate('document.fonts.ready')
def screen(page,selector,name):
 target=page.locator(selector);target.scroll_into_view_if_needed()
 for image in target.locator('img').all():
  if image.is_visible():image.evaluate('(image)=>image.decode()')
 target.screenshot(path=str(OUT/name),animations='disabled')
def storage(page,key):return page.evaluate('(key)=>JSON.parse(localStorage.getItem("fretline:"+key)||"[]")',key)

with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']) if engine=='chromium' else p.webkit.launch()
  for device,size in [('desktop',(1440,1000)),('mobile',(390,844))]:
   context=b.new_context(viewport={'width':size[0],'height':size[1]},has_touch=device=='mobile',reduced_motion='reduce');page=context.new_page()
   page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)));page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
   prefix=engine+'-'+device
   def home():
    go(page);expect(page.locator('.signature-hero-slide')).to_have_count(3)
    for category in ['electric','acoustic','classical','bass']:
     card=page.locator('.signature-category-card--'+category);count=sum(g['category']==category for g in BY_ID.values());expect(card).to_contain_text(str(count)+' รุ่น');assert parse_qs(urlparse(card.get_attribute('href')).query)['type']==[category]
    screen(page,'#categories',prefix+'-categories.png');screen(page,'#home-features',prefix+'-three-modes.png')
    for title in ['ยอดนิยม','รุ่นใหม่','ราคาสูง–ต่ำ','ราคาต่ำ–สูง']:
     tab=page.get_by_role('tab',name=title,exact=True);tab.click();expect(tab).to_have_attribute('aria-selected','true');assert page.locator('#featured-models [data-guitar-id]').count()>0
    page.get_by_role('tab',name='ยอดนิยม',exact=True).click();screen(page,'#featured',prefix+'-featured.png')
    track=page.locator('#featured-models');track.evaluate('(element)=>element.scrollLeft=element.scrollWidth');assert track.evaluate('(element)=>element.scrollLeft')>0
    for selector,path in [('#home-practice .home-editorial-cta','/practice'),('#find .home-editorial-cta','/find-my-guitar'),('#compare .home-editorial-cta','/compare')]:assert page.locator(selector).get_attribute('href')==path
    for category in ['electric','acoustic','classical','bass']:
     go(page);page.locator('.signature-category-card--'+category).click();assert parse_qs(urlparse(page.url).query)['type']==[category];expect(page.locator('.catalog-result-count>p').first).to_contain_text(str(sum(g['category']==category for g in BY_ID.values()))+' รุ่น')
    for selector,path in [('#home-practice .home-editorial-cta','/practice'),('#find .home-editorial-cta','/find-my-guitar'),('#compare .home-editorial-cta','/compare')]:
     go(page);page.locator(selector).click();assert urlparse(page.url).path==path;expect(page.locator('main h1')).to_be_visible()
     if path=='/practice':
      expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=60000);expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
    return {'threeOriginalScenes':True,'fourDataDrivenCategories':True,'threeModeDestinations':True,'fourWorkingTabs':True,'horizontalProductScroll':True}
   check(prefix+'-home-and-collections',home,page)
   def brands():
    go(page,'/brands');expect(page.locator('.brand-directory-card')).to_have_count(len(snapshot['brands']))
    for image in page.locator('[data-brand-logo]').all():image.evaluate('(image)=>image.decode()');assert image.evaluate('(image)=>image.naturalWidth')>0
    country=page.locator('.brands-extra-filters');country.locator('summary').click();country.get_by_role('button',name='ญี่ปุ่น',exact=True).click();assert parse_qs(urlparse(page.url).query)['country']==['Japan'];expect(page.locator('.brand-directory-card')).to_have_count(sum(b.get('country')=='Japan' for b in snapshot['brands']));go(page,'/brands')
    page.get_by_role('searchbox',name='ค้นหาแบรนด์',exact=True).fill('Yamaha');expect(page.locator('.brand-directory-card')).to_have_count(1);page.locator('.brand-directory-card').click();assert parse_qs(urlparse(page.url).query)['brand']==['Yamaha']
    expect(page.locator('.catalog-result-count>p').first).to_contain_text('20 รุ่น')
    go(page,'/brands/yamaha');expect(page.locator('.brand-model-grid [data-guitar-id]')).to_have_count(20)
    page.get_by_role('group',name='ประเภทกีตาร์',exact=True).get_by_role('button',name='กีตาร์ไฟฟ้า',exact=True).click();expect(page.locator('.brand-model-grid [data-guitar-id]')).to_have_count(sum(g['brand']=='Yamaha' and g['category']=='electric' for g in BY_ID.values()))
    return {'tenRealBrandMarks':True,'searchAndBrandCatalog':True,'brandDetailCategoryFilter':True}
   check(prefix+'-brands-and-filtering',brands,page)
   def favorites():
    ids=['yamaha-pacifica-612viifm','yamaha-fg820-12']
    for gid in ids:
     go(page,'/guitars?q='+gid);page.locator('[data-guitar-id="'+gid+'"]').get_by_role('button',name=re.compile('^บันทึก.*รายการโปรด')).click()
    go(page,'/wishlist');expect(page.locator('.wishlist-row')).to_have_count(2);assert storage(page,'wishlist')==ids
    page.reload(wait_until='networkidle');expect(page.locator('.wishlist-row')).to_have_count(2);screen(page,'.wishlist-list',prefix+'-favorites.png')
    page.locator('.wishlist-tools .is-gold').click();expect(page.locator('[data-compare-card]')).to_have_count(2)
    go(page,'/wishlist');page.locator('.wishlist-tools button:not(.is-gold)').click();page.get_by_role('alertdialog').get_by_role('button',name='ยกเลิก',exact=True).click();expect(page.locator('.wishlist-row')).to_have_count(2)
    page.locator('.wishlist-row').first.locator('.wishlist-heart').click();expect(page.locator('.wishlist-row')).to_have_count(1)
    page.locator('.wishlist-tools button').click();page.get_by_role('alertdialog').get_by_role('button',name='ยืนยันล้างรายการ',exact=True).click();expect(page.locator('.wishlist-row')).to_have_count(0);assert storage(page,'wishlist')==[]
    return {'saveFromCatalog':True,'persistRefresh':True,'compareSaved':True,'cancelClear':True,'removeAndConfirmClear':True}
   check(prefix+'-personal-collection',favorites,page)
   def gallery():
    gid='yamaha-pacifica-612viifm';go(page,'/guitars/'+gid);images=BY_ID[gid]['gallery'];expect(page.locator('.gallery-thumbnails li')).to_have_count(len(images))
    for index,image in enumerate(images):
     button=page.locator('.gallery-thumbnails button').nth(index);button.click();expect(button).to_have_attribute('aria-current','true');expect(page.locator('.gallery-main img')).to_have_attribute('alt',re.compile(re.escape(BY_ID[gid]['name'])))
    page.get_by_role('button',name='เปิดดูรูปขนาดใหญ่',exact=True).click();dialog=page.locator('.product-lightbox');expect(dialog).to_be_visible();expect(dialog.locator('.lightbox-thumbnails li')).to_have_count(len(images));page.keyboard.press('ArrowRight');page.keyboard.press('Escape');expect(dialog).to_have_count(0)
    page.locator('[role=tablist] button').filter(has_text='สเปก').click();expect(page.locator('#specs')).to_be_visible();expect(page.locator('#specs')).to_contain_text('Seymour Duncan')
    return {'allOriginalImages':len(images),'thumbnails':True,'lightboxKeyboard':True,'specificationsAccessible':True}
   check(prefix+'-full-product-gallery',gallery,page)
   def practice():
    go(page,'/practice');expect(page.locator('[data-practice-chord]')).to_have_count(len(CHORDS));expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=60000);expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
    for gid in ['C','Am','F','Cmaj7','Bm7','Csus4']:
     page.locator('[data-practice-chord="'+gid+'"]').click();expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord',gid)
     actual=page.locator('[data-finger-instruction]').evaluate_all('(nodes)=>nodes.map(node=>[+node.dataset.fingerInstruction,+node.dataset.string,+node.dataset.fret])')
     chord=CHORDS[gid];expected=[[chord['fingers'][i],6-i,fret] for i,fret in enumerate(chord['frets']) if fret is not None and fret>0];assert sorted(actual)==sorted(expected),(gid,actual,expected)
    for button in page.locator('.practice-camera-controls button').all():expect(button).to_be_enabled();button.click()
    page.locator('#practice-chord-search').fill('Am');assert 0<page.locator('[data-practice-chord]').count()<42
    screen(page,'.practice-chord-library',prefix+'-chord-library.png')
    return {'all42Chords':True,'sixVoicingsFingerDataVerified':True,'existing3DLoaded':True,'cameraControls':True,'search':True}
   check(prefix+'-practice-controls-and-finger-data',practice,page)
   context.close()
  context=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference');page=context.new_page()
  def motion():
   go(page);hero=page.locator('[data-hero-slide-index]');before=hero.get_attribute('data-hero-slide-index');page.wait_for_function('(before)=>document.querySelector("[data-hero-slide-index]").dataset.heroSlideIndex!==before',arg=before,timeout=10000)
   rail=page.locator('[data-marquee-viewport]');rail.scroll_into_view_if_needed();start=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(500);moving=rail.evaluate('(e)=>e.scrollLeft');assert start!=moving
   rect=rail.bounding_box();page.mouse.move(rect['x']+rect['width']*.7,rect['y']+rect['height']*.5);page.mouse.down();page.mouse.move(rect['x']+rect['width']*.3,rect['y']+rect['height']*.5,steps=12);dragged=rail.evaluate('(e)=>e.scrollLeft');page.mouse.up();assert dragged!=moving;page.wait_for_timeout(1800);assert rail.evaluate('(e)=>e.scrollLeft')!=dragged
   return {'automaticHero':True,'continuousMarquee':True,'dragAndAutoResume':True}
  check(engine+'-restrained-motion-and-marquee',motion,page);context.close();b.close()
report['passed']=all(c['passed'] for c in report['checks']) and not report['consoleErrors'] and not report['runtimeErrors'];(OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('FINAL',report['passed'],len(report['checks']),flush=True);raise SystemExit(not report['passed'])
