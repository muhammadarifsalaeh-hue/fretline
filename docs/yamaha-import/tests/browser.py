"""Actual imported Yamaha data and explicit preview image QA; never a rights approval."""
from pathlib import Path
from urllib.parse import quote,urljoin
from playwright.sync_api import sync_playwright,expect
import argparse,hashlib,json,traceback
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--production',required=True);parser.add_argument('--preview',required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--modes',nargs='+',choices=['production','preview'],default=['production','preview']);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
IDS=['yamaha-fsx830c','yamaha-fsx800c','yamaha-fs800','yamaha-fgx820c','yamaha-fg800m','yamaha-fg820l','yamaha-fs830','yamaha-fg820','yamaha-fgx800c','yamaha-fg840','yamaha-fg850','yamaha-fg800j','yamaha-fg820-12','yamaha-fs850','yamaha-fg830','yamaha-fsx820c','yamaha-fs820','yamaha-fg800']
reviewed=json.loads((ROOT/'src/data/catalog/reviewedGuitars.json').read_text());expected={k:reviewed[k] for k in IDS};inventory=json.loads((ROOT/'docs/yamaha-import/review/image-inventory.json').read_text())
manifest=json.loads((ROOT/'docs/yamaha-import/preview-manifest.json').read_text())
source_by_hash={row['sha256']:row for row in inventory}
uploads={model['guitarId']:[source_by_hash[image['sha256']] for image in model['images']] for model in manifest['models']}
assert len(IDS)==18 and sum(map(len,uploads.values()))==20
rights=json.loads((ROOT/'src/data/catalog/imageRights.json').read_text())['yamaha-fg820-12'][0]
def sha(b):return hashlib.sha256(b).hexdigest()
def snapshot():return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for folder in ['dist/assets','src','scripts/vite'] for p in (ROOT/folder).rglob('*') if p.is_file() and (folder!='src' or p.suffix in ['.js','.jsx','.json','.css'])}
start=snapshot();(args.output/'expected-data.json').write_text(json.dumps(expected,ensure_ascii=False,indent=2)+'\n')
report={'sourceAndBuildSHA256':start,'checks':[],'consoleErrors':[],'runtimeErrors':[],'networkErrors':[],'physicalIPadSafariTested':False,'rightsApprovedByHarness':False,'suppliedArchives':18,'expectedArchiveCount':19,'imageFiles':20,'notes':['Linux WebKit and synthesized touch do not certify native iPad Safari.','Rights-pending supplied images are tested only in explicit local preview, never accepted as licensed production photos.']}
ACTIVE=None

def check(label,fn,page):
 global ACTIVE
 ACTIVE=label
 try:
  detail=fn();report['checks'].append({'case':label,'passed':True,'evidence':detail});print('PASS',label,flush=True)
 except Exception:
  fail=traceback.format_exc();shot=label.replace('/','-')+'-FAIL.png'
  try:page.screenshot(path=str(args.output/shot),full_page=True,animations='disabled')
  except Exception:pass
  report['checks'].append({'case':label,'passed':False,'failure':fail,'url':page.url,'screenshot':shot});print('FAIL',label,fail,flush=True)

def go(page,base,path):
 response=page.goto(base.rstrip('/')+path,wait_until='networkidle');expect(page.locator('main h1')).to_be_visible();page.evaluate('document.fonts.ready');return response

def no_overflow(page):
 result=page.evaluate('({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll("main h1").length})');assert result['scrollWidth']<=result['viewport']+1,result;assert result['h1']==1,result;return result

def image_info(image):
 image.scroll_into_view_if_needed();expect(image).to_be_visible();image.evaluate('(i)=>i.decode()');r=image.evaluate(r'''i=>({src:i.getAttribute('src'),currentSrc:i.currentSrc,width:i.naturalWidth,height:i.naturalHeight,fit:getComputedStyle(i).objectFit,padding:getComputedStyle(i).padding,transform:getComputedStyle(i).transform,frame:(()=>{let e=i;while(e&&!getComputedStyle(e).backgroundColor.match(/rgb\(0, 0, 0\)|rgb\(8, 8, 7\)/))e=e.parentElement;return e?.className})()})''');assert r['width']>0 and r['height']>0 and r['fit']=='contain',r;return r

def price_text(record):return 'ยังไม่มีข้อมูลราคา' if record.get('price') is None else '฿'+format(record['price'],',')

def detail_case(page,context,engine,mode,base,gid,viewport):
 response=go(page,base,'/guitars/'+gid);record=expected[gid];expect(page.locator('.detail-summary h1')).to_have_text(record['name']);expect(page.locator('.detail-price-block')).to_contain_text(price_text(record));assert 'undefined' not in page.locator('.detail-summary').inner_text();metrics=no_overflow(page)
 if record.get('price') is not None:
  note=page.locator('.detail-price-block .price-source-note');expect(note).to_contain_text('Music Arms');expect(note).to_contain_text('2026-10-26')
  if gid in ['yamaha-fg820l','yamaha-fg820-12']:expect(note).to_contain_text('ยกเลิกจำหน่าย')
 main=page.locator('.gallery-main');thumbs=page.locator('.gallery-thumbnails button');observed=[]
 if mode=='production':
  if gid=='yamaha-fg820-12':
   assert thumbs.count()==1;info=image_info(main.locator('img'));body=context.request.get(urljoin(base,info['src'])).body();assert sha(body)==rights['sha256'];observed.append({'registeredPrimary':True,**info})
  else:assert main.locator('img').count()==0;expect(main.locator('.image-placeholder')).to_be_visible()
  assert page.locator('img[src*="__fretline_yamaha"]').count()==0
 else:
  assert 'noindex' in response.headers.get('x-robots-tag','').lower(),response.headers
  count=len(uploads[gid])+(1 if gid=='yamaha-fg820-12' else 0);assert thumbs.count()==count,(gid,thumbs.count(),count)
  if gid=='yamaha-fg820-12':
   first=image_info(main.locator('img'));assert sha(context.request.get(urljoin(base,first['src'])).body())==rights['sha256']
  upload_index=1 if gid=='yamaha-fg820-12' else 0
  for idx,upload in enumerate(uploads[gid]):
   thumbs.nth(idx+upload_index).click();info=image_info(main.locator('img'));assert [info['width'],info['height']]==[upload['width'],upload['height']],(gid,info,upload)
   response_image=context.request.get(urljoin(base,info['src']));assert response_image.status==200;assert sha(response_image.body())==upload['sha256'],(gid,info['src']);assert 'noindex' in response_image.headers.get('x-robots-tag','').lower();observed.append({**info,'sha256':upload['sha256']})
  page.get_by_role('button',name='เปิดดูรูปขนาดใหญ่',exact=True).click();dialog=page.get_by_role('dialog');expect(dialog).to_be_visible();li=image_info(dialog.locator('div.relative img').first);assert li['src']==observed[-1]['src'];page.keyboard.press('Escape');expect(dialog).to_have_count(0)
 page.get_by_role('tab',name='สเปก',exact=True).click();spec=page.locator('.spec-table');expect(spec).to_be_visible()
 for field in ['body','neck','fretboard','pickups','bridge','controls']:
  if record.get('specs',{}).get(field) is not None:expect(spec).to_contain_text(str(record['specs'][field]))
 expect(spec).to_contain_text('ยังไม่ยืนยัน' if record.get('price') is None else price_text(record));assert 'undefined' not in spec.inner_text()
 if viewport=='desktop' and gid in ['yamaha-fsx830c','yamaha-fg820-12','yamaha-fg800'] or viewport!='desktop' and gid in ['yamaha-fsx830c','yamaha-fg800']:
  page.get_by_role('tab').first.click();page.evaluate('scrollTo(0,0)');page.screenshot(path=str(args.output/f'{engine}-{mode}-{viewport}-{gid}.png'),full_page=True,animations='disabled')
 return {'id':gid,'name':record['name'],'expectedPrice':record.get('price'),'displayedPrice':price_text(record),'layout':metrics,'images':observed}

def catalog_case(page,engine,mode,base,viewport):
 go(page,base,'/guitars?brand=Yamaha');expect(page.locator('.catalog-result-count')).to_contain_text('20');ids=[];seen=[]
 for index in range(3):
  if index:page.locator('.catalog-pagination').get_by_role('button',name='หน้าถัดไป',exact=True).click();page.wait_for_load_state('networkidle')
  cards=page.locator('.catalog-grid article[data-guitar-id]');assert cards.count()==(9 if index<2 else 2);ids.extend(cards.evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)'))
  for card in cards.all():
   gid=card.get_attribute('data-guitar-id');assert gid.startswith('yamaha-');
   if gid in expected:expect(card.locator('.catalog-card-price')).to_contain_text(price_text(expected[gid]))
   imgs=card.locator('img')
   if imgs.count():seen.append({'id':gid,**image_info(imgs.first)})
  no_overflow(page)
 assert len(ids)==len(set(ids))==20 and all(k in ids for k in IDS),ids
 if mode=='preview':assert len(seen)==19,(mode,len(seen),seen)
 if mode=='production':assert {r['id'] for r in seen}=={'yamaha-pacifica-612viifm','yamaha-fg820-12'}
 go(page,base,'/guitars?brand=Yamaha');page.locator('#catalog-search').fill('FSX830C');expect(page.locator('.catalog-grid article')).to_have_count(1);expect(page.locator('article[data-guitar-id="yamaha-fsx830c"]')).to_be_visible();no_overflow(page)
 go(page,base,'/guitars?brand=Yamaha');page.screenshot(path=str(args.output/f'{engine}-{mode}-{viewport}-yamaha-catalog.png'),full_page=True,animations='disabled')
 return {'models':ids,'actualRenderedCardImages':seen,'interactiveSearch':'FSX830C returns single stable ID','pagination':[9,9,2]}

def compare_case(page,mode,base,ids):
 go(page,base,'/compare?ids='+','.join(ids));expect(page.locator('[data-compare-remove]')).to_have_count(len(ids));table=page.get_by_role('table');expect(table).to_be_visible()
 for gid in ids:expect(table).to_contain_text(expected[gid]['name']);expect(table).to_contain_text(price_text(expected[gid]))
 images=page.locator('.compare-table-scroll img');
 if mode=='preview':assert images.count()==len(ids)
 for im in images.all():image_info(im)
 no_overflow(page);return {'ids':ids,'prices':{k:expected[k].get('price') for k in ids},'images':images.count()}

def wishlist_case(page,mode,base):
 gid='yamaha-fg800';go(page,base,'/guitars/'+gid);button=page.locator('.detail-actions button').nth(1);button.click();expect(button).to_have_attribute('aria-pressed','true');go(page,base,'/wishlist');expect(page.locator('.wishlist-row')).to_have_count(1);expect(page.locator('.wishlist-row')).to_contain_text(price_text(expected[gid]));page.reload(wait_until='networkidle');expect(page.locator('.wishlist-row')).to_have_count(1);assert page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))')==[gid]
 if mode=='preview':image_info(page.locator('.wishlist-image img'))
 return {'stableId':gid,'reloadPersisted':True}

def quiz_case(page,mode,base):
 go(page,base,'/find-my-guitar?type=acoustic&level=beginner&style=folk&budget=low&priority=value');expect(page.locator('.quiz-results-page')).to_be_visible();cards=page.locator('.match-card');assert cards.count()>0;ids=cards.evaluate_all('(rows)=>rows.map(r=>r.dataset.guitarId)');assert 'yamaha-fg800' in ids,ids
 card=page.locator('.match-card[data-guitar-id="yamaha-fg800"]');expect(card).to_contain_text(price_text(expected['yamaha-fg800']));
 if mode=='preview':image_info(card.locator('img'))
 no_overflow(page);return {'rankedIds':ids,'sameFG800DataAndPreview':True}

with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  browser=None
  try:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) if engine=='chromium' else p.webkit.launch()
   for mode,base in [('production',args.production),('preview',args.preview)]:
    if mode not in args.modes:continue
    for label,w,h in [('desktop',1440,1000),('tablet',768,1024),('mobile',390,844)]:
     context=browser.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion='reduce',locale='th-TH');page=context.new_page()
     page.on('pageerror',lambda e:report['runtimeErrors'].append({'case':ACTIVE,'text':str(e)}));page.on('console',lambda m:report['consoleErrors'].append({'case':ACTIVE,'text':m.text}) if m.type=='error' else None);page.on('requestfailed',lambda r:report['networkErrors'].append({'case':ACTIVE,'url':r.url,'error':r.failure}));page.on('response',lambda r:report['networkErrors'].append({'case':ACTIVE,'url':r.url,'status':r.status}) if r.status>=400 else None)
     check(f'{engine}-{mode}-{label}-catalog',lambda:catalog_case(page,engine,mode,base,label),page)
     for gid in IDS:check(f'{engine}-{mode}-{label}-{gid}',lambda gid=gid:detail_case(page,context,engine,mode,base,gid,label),page)
     for index in range(0,18,4) if label=='desktop' else [0]:
      selected=IDS[index:index+4];selected=selected if len(selected)>=2 else IDS[-2:];check(f'{engine}-{mode}-{label}-compare-{index}',lambda selected=selected:compare_case(page,mode,base,selected),page)
     check(f'{engine}-{mode}-{label}-wishlist',lambda:wishlist_case(page,mode,base),page)
     check(f'{engine}-{mode}-{label}-quiz',lambda:quiz_case(page,mode,base),page)
     context.close()
   report.setdefault('browserVersions',{})[engine]=browser.version
  except Exception:report.setdefault('harnessFailures',[]).append({'engine':engine,'error':traceback.format_exc()})
  finally:
   if browser:browser.close()
report['sourceAndBuildUnchangedDuringRun']=start==snapshot();report['passed']=bool(report['checks']) and all(c['passed'] for c in report['checks']) and report['sourceAndBuildUnchangedDuringRun'] and not any(report[k] for k in ['consoleErrors','runtimeErrors','networkErrors']) and not report.get('harnessFailures')
(args.output/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('RESULT',report['passed'],sum(c['passed'] for c in report['checks']),len(report['checks']),flush=True);raise SystemExit(not report['passed'])
