"""Production-browser acceptance for Home redesign; no mock model data.

Chromium CDP can dispatch real browser touch gestures. Linux WebKit here exposes
no native touch-drag API; its wheel/mouse/native scroll and pointer lifecycle are
covered, never presented as physical iPad Safari certification.
"""
from pathlib import Path
from urllib.parse import urlparse,parse_qs,urljoin
from playwright.sync_api import sync_playwright,expect
import argparse,json,hashlib,traceback,time,re
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--engines',nargs='+',default=['chromium','webkit']);p.add_argument('--viewports',nargs='+',default=['desktop','tablet','mobile']);p.add_argument('--cases',nargs='+',default=['composition','quiz','compare','reduced','carousel','routes']);args=p.parse_args();BASE=args.url.rstrip('/');OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
VIEWPORTS={'desktop':(1440,1000),'tablet':(768,1024),'mobile':(390,844)}
STEPS={'type':['electric','acoustic','classical','bass','any'],'level':['beginner','intermediate','advanced'],'style':['rock','blues','pop','folk','classical'],'budget':['low','mid','high','premium','flex'],'priority':['light','versatile','premium','value']}
fixture=json.loads((ROOT/'docs/premium-quiz-compare/tests/browser-fixtures.json').read_text())['cases'][0]
records=json.loads((ROOT/'src/data/catalog/reviewedGuitars.json').read_text());rights=json.loads((ROOT/'src/data/catalog/imageRights.json').read_text());art=json.loads((ROOT/'src/data/catalog/projectArtwork.json').read_text())
DEFAULT=['yamaha-fg820-12','martin-d-28'];EXTRAS=['yamaha-pacifica-612viifm','yamaha-fg800']
def sha(b):return hashlib.sha256(b).hexdigest()
def snapshot():return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for folder in ['src','dist/assets'] for p in (ROOT/folder).rglob('*') if p.is_file()}
start=snapshot();ACTIVE=None
report={'baseURL':BASE,'checks':[],'consoleErrors':[],'runtimeErrors':[],'networkErrors':[],'failedRequests':[],'physicalIPadSafariTested':False,'nativeWebKitTouchDragAvailable':False,'sourceAndBuildSHA256':start,'screenshots':[]}
def check(name,fn,page):
 global ACTIVE
 ACTIVE=name
 try:r=fn();report['checks'].append({'case':name,'passed':True,'evidence':r});print('PASS',name,flush=True)
 except Exception:
  error=traceback.format_exc();file=name+'-FAIL.png'
  try:page.screenshot(path=str(OUT/file),full_page=True,animations='disabled')
  except Exception:pass
  report['checks'].append({'case':name,'passed':False,'error':error,'url':page.url,'screenshot':file});print('FAIL',name,error,flush=True)
def go(page,path='/'):
 page.goto(BASE+path,wait_until='networkidle');page.evaluate('document.fonts.ready');expect(page.locator('main h1')).to_be_visible()
def metrics(page):
 r=page.evaluate('({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll("main h1").length})');assert r['scrollWidth']<=r['viewport']+1,r;assert r['h1']==1,r;return r
def decode(im):
 im.scroll_into_view_if_needed();im.evaluate('(i)=>i.decode()');r=im.evaluate('(i)=>({src:i.getAttribute("src"),currentSrc:i.currentSrc,width:i.naturalWidth,height:i.naturalHeight,fit:getComputedStyle(i).objectFit,loading:i.loading})');assert r['width']>0 and r['height']>0,r;assert r['fit'] in ['contain','cover'],r;return r
def shot_region(page,selector,name):
 el=page.locator(selector);el.scroll_into_view_if_needed()
 for im in el.locator('img').all():
  if im.is_visible():decode(im)
 page.wait_for_timeout(120);el.screenshot(path=str(OUT/name),animations='disabled');report['screenshots'].append(name)
def model_photos(page,context):
 evidence=[]
 for card in page.locator('[data-home-compare-model]').all():
  gid=card.get_attribute('data-home-compare-model');expect(card).to_contain_text(records[gid]['name']);registered=(rights.get(gid) or [])+(art.get(gid,{}).get('images') or []);images=card.locator('img')
  if not registered:
   assert images.count()==0,(gid,'Never substitute generic photograph for an unknown model');evidence.append({'id':gid,'honestMissingModelFallback':True});continue
  expect(images).to_have_count(1);info=decode(images.first);expect(images.first).to_have_css('opacity','1');assert info['fit']=='contain',info;response=context.request.get(urljoin(BASE,info['src']));assert response.status==200;digest=sha(response.body());assert digest in {x['sha256'] for x in registered},(gid,digest);evidence.append({'id':gid,'sha256':digest,**info})
 return evidence
def composition(page,context,engine,viewport):
 go(page);assert page.evaluate('scrollY')<30,'Home must not auto-scroll to inline Quiz';metrics(page)
 photos={}
 for selector in ['.signature-hero-visual','.home-find-photograph','.home-compare-scene__photo']:
  node=page.locator(selector)
  if node.count() and node.locator('img').count():photos[selector]=[decode(im) for im in node.locator('img').all()]
 assert all(k in photos for k in ['.signature-hero-visual','.home-find-photograph','.home-compare-scene__photo']),photos
 assert page.locator('.signature-category-card').count()==4
 for card in page.locator('.signature-category-card').all():
  expect(card.locator('img')).to_have_count(1);decode(card.locator('img'));expect(card.locator('img')).to_have_css('opacity','1')
 for kind in ['electric','acoustic','classical','bass']:
  option=page.locator('[data-home-quiz-option="'+kind+'"]');expect(option).to_have_count(1);expect(option.locator('img')).to_have_count(1);photos[kind]=decode(option.locator('img'))
 expect(page.locator('.home-find-statistics')).to_contain_text('200');expect(page.locator('.home-find-statistics')).to_contain_text('10');expect(page.locator('.home-find-statistics')).to_contain_text('4')
 assert not re.search(r'AI\s*Generated|Powered\s+by\s+AI|ออกแบบด้วย\s*AI',page.locator('main').inner_text(),re.I)
 sources=model_photos(page,context);assert [x['id'] for x in sources]==DEFAULT
 for name,selector in [('brands','#brands'),('quiz','#find'),('compare','#compare')]:shot_region(page,selector,f'{engine}-{viewport}-{name}.png')
 page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'{engine}-{viewport}-homepage.png'),full_page=True,animations='disabled');report['screenshots'].append(f'{engine}-{viewport}-homepage.png')
 resources=page.evaluate('performance.getEntriesByType("resource").map(r=>new URL(r.name).pathname)');assert not any('practice-three' in r or r.endswith('.glb') for r in resources),resources
 return {'realEditorialImages':photos,'modelBoundPhotos':sources,'no3DLoaded':True,**metrics(page)}
def inline_quiz(page,engine,viewport):
 go(page);page.locator('[data-home-quiz-start]').click();expect(page.locator('.home-find-live-question h3')).to_be_focused();seen={}
 for index,(field,values) in enumerate(STEPS.items(),1):
  expect(page.locator('[data-home-quiz-panel] [role=progressbar]')).to_have_attribute('aria-valuenow',str(index));radios=page.locator('input[name="home-quiz-'+field+'"]');assert radios.evaluate_all('(nodes)=>nodes.map(n=>n.value)')==values
  expect(page.locator('.home-find-next')).to_be_disabled()
  for value in values:
   radio=page.locator('input[name="home-quiz-'+field+'"][value="'+value+'"]');radio.locator('..').click();expect(radio).to_be_checked()
  value=fixture['answers'][field];page.locator('input[name="home-quiz-'+field+'"][value="'+value+'"]').locator('..').click();seen[field]=values
  if index==3:
   page.locator('.home-find-previous').click();expect(page.locator('input[name=home-quiz-level][value=beginner]')).to_be_checked();page.locator('.home-find-next').click();expect(page.locator('input[name=home-quiz-style][value=folk]')).to_be_checked()
  page.locator('.home-find-next').click()
 expect(page.locator('.quiz-results-page')).to_be_visible();query=parse_qs(urlparse(page.url).query);assert {k:v[0] for k,v in query.items()}==fixture['answers'];cards=page.locator('.match-card[data-guitar-id]');assert cards.evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)')==[m['id'] for m in fixture['matches']]
 for i,m in enumerate(fixture['matches']):
  card=cards.nth(i);expect(card.locator('.match-score')).to_contain_text(str(m['score'])+'%')
  for reason in m['reasons']:expect(card).to_contain_text(reason)
  for caveat in m['caveats']:expect(card).to_contain_text(caveat)
 shot_region(page,'.quiz-results-page',f'{engine}-{viewport}-inline-quiz-results.png');metrics(page)
 return {'allOriginal22Options':seen,'fiveSteps':True,'previousPreservesAnswers':True,'originalResultsIDs':[m['id'] for m in fixture['matches']],'scoresReasonsCaveatsUnchanged':True}
def compare_ids(page):return page.locator('[data-home-compare-model]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.homeCompareModel)')
def comparison(page,context,engine,viewport):
 go(page);expect(page.locator('#compare [role=switch]')).to_have_attribute('aria-checked','true');assert compare_ids(page)==DEFAULT
 assert page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))')==[],'Demo pair must not silently alter selection'
 page.locator('#compare [role=switch]').click();expect(page.locator('#compare [role=switch]')).to_have_attribute('aria-checked','false');keys=page.locator('[data-home-compare-row]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.homeCompareRow)');assert keys==['neck','body','fretboard','pickups','scale','frets','weight','price'],keys
 for gid in DEFAULT:
  for key in ['neck','body','fretboard','pickups']:
   expect(page.locator('[data-home-compare-row="'+key+'"] [data-home-compare-value="'+gid+'"]').first).to_have_text(records[gid]['specs'][key])
 expect(page.locator('[data-home-compare-row=price] [data-home-compare-value="yamaha-fg820-12"]')).to_contain_text('฿16,500');expect(page.locator('[data-home-compare-row=frets] [data-home-compare-value="martin-d-28"]')).to_have_text('20');weight=page.locator('[data-home-compare-row=weight]');assert not re.search(r'\d',weight.inner_text()),'Unknown weights must never be invented'
 page.locator('[data-home-compare-expand]').click();expect(page.locator('[data-home-compare-panel]')).to_be_visible();expect(page.locator('[data-home-compare-panel] [role=table]')).to_be_visible();page.locator('[data-home-compare-expand]').click();expect(page.locator('[data-home-compare-panel]')).to_be_hidden()
 page.locator('.home-compare-page-link').click();expect(page.locator('.premium-compare')).to_be_visible();assert parse_qs(urlparse(page.url).query)['ids'][0].split(',')==DEFAULT
 page.get_by_role('button',name='เพิ่มกีตาร์',exact=True).first.click();dialog=page.get_by_role('dialog',name='เพิ่มกีตาร์',exact=True);search=dialog.get_by_role('searchbox')
 for gid in EXTRAS:
  search.fill(records[gid]['name']);row=dialog.locator('.picker-model-row').filter(has=page.get_by_text(records[gid]['name'],exact=True));expect(row).to_have_count(1);row.click();expect(row).to_have_attribute('aria-pressed','true')
 dialog.get_by_role('button',name='เสร็จสิ้น',exact=True).click();expect(page.locator('[data-compare-remove]')).to_have_count(4)
 page.locator('.site-header a[href="/"]').first.click();expect(page.locator('.signature-home')).to_be_visible();assert compare_ids(page)==DEFAULT+EXTRAS;photos=model_photos(page,context)
 page.locator('[data-home-compare-remove="'+DEFAULT[0]+'"]').click();assert compare_ids(page)==[DEFAULT[1]]+EXTRAS;expect(page.locator('[data-home-compare-remove]')).to_have_count(3)
 page.locator('[data-home-compare-expand]').click();expect(page.locator('[data-home-compare-panel] [data-compare-remove]')).to_have_count(3);page.locator('[data-home-compare-panel] [data-compare-remove="'+DEFAULT[1]+'"]').click();expect(page.locator('[data-home-compare-panel] [data-compare-remove]')).to_have_count(2);assert compare_ids(page)==EXTRAS
 page.locator('[data-home-compare-remove="'+EXTRAS[0]+'"]').click();assert compare_ids(page)==DEFAULT;assert page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))')==[EXTRAS[1]];metrics(page)
 return {'actualCatalogRows':keys,'allOriginalSelectionFunctions':True,'modelBoundImages':photos,'defaultPairDoesNotMutateContext':True,'fourThreeTwoAndFallbackOne':True}
def reduced(page):
 go(page);rail=page.locator('[data-marquee-viewport]');rail.evaluate('(e)=>e.scrollIntoView({block:"center"})');expect(rail).to_have_attribute('data-marquee-motion','reduced');a=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(350);assert abs(rail.evaluate('(e)=>e.scrollLeft')-a)<=1
 assert rail.locator('[data-marquee-clone]:visible').count()==0;assert page.locator('#brands button').count()==0;first=rail.locator('[data-marquee-primary] a').last;page.keyboard.press('Tab');first.focus();expect(first).to_be_focused();bounds=first.bounding_box();rb=rail.bounding_box();assert bounds['x']>=rb['x']-1 and bounds['x']+bounds['width']<=rb['x']+rb['width']+1,(bounds,rb)
 radio=page.locator('input[name=home-quiz-type][value=electric]');radio.focus();page.keyboard.press('Space');expect(radio).to_be_checked();focus=radio.locator('..').locator('.home-find-option-focus');assert focus.evaluate('(e)=>getComputedStyle(e).outlineStyle')!='none';metrics(page)
 return {'staticAutomaticMotion':True,'clonesHidden':True,'lastKeyboardBrandFullyVisible':True,'nativeQuizRadioKeyboardFocus':True}
def carousel(page,context,engine,viewport):
 go(page);rail=page.locator('[data-marquee-viewport]');rail.evaluate('(e)=>e.scrollIntoView({block:"center"})');page.wait_for_timeout(200);expect(rail).to_have_attribute('data-marquee-motion','auto');assert page.locator('#brands button').count()==0;assert not page.locator('#brands [data-marquee-prev],#brands [data-marquee-next],#brands [data-marquee-pause]').count();assert rail.evaluate('(e)=>getComputedStyle(e).scrollbarWidth')=='none'
 groups=rail.locator('.signature-marquee-group');assert groups.count()==3
 identities=groups.evaluate_all('(nodes)=>nodes.map(n=>[...n.querySelectorAll("a")].map(a=>({id:a.dataset.brandId,href:a.getAttribute("href"),image:a.querySelector("img")?.getAttribute("src")||null})))');assert identities[0]==identities[1]==identities[2];assert len(identities[1])==10
 W=rail.locator('[data-marquee-primary]').evaluate('(e)=>e.getBoundingClientRect().width')
 # A main-thread read between WebKit's delayed startup frames can observe a
 # stale native position. Sample position and time together after a real frame,
 # keeping the 30px/sec target and tightening the earlier broad tolerance.
 sample='(e)=>new Promise(resolve=>requestAnimationFrame(t=>resolve({left:e.scrollLeft,frameTime:t,observedTime:performance.now()})))'
 before_sample=rail.evaluate(sample);page.wait_for_timeout(800);after_sample=rail.evaluate(sample)
 before=before_sample['left'];after=after_sample['left'];delta=(after-before)%W;elapsed=after_sample['frameTime']-before_sample['frameTime'];assert elapsed>0,(before_sample,after_sample)
 pixels_per_second=delta*1000/elapsed;assert 27<=pixels_per_second<=33,(before_sample,after_sample,pixels_per_second)
 rb=rail.bounding_box();x=rb['x']+min(rb['width']*.7,500);y=rb['y']+rb['height']/2;page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-125,y,steps=12);expect(rail).to_have_attribute('data-marquee-dragging','true');dragged=rail.evaluate('(e)=>e.scrollLeft');page.mouse.up();assert page.url==BASE+'/'
 assert (dragged-after)%W>70,(after,dragged);page.wait_for_timeout(1800);expect(rail).to_have_attribute('data-marquee-motion','auto');resumed=rail.evaluate('(e)=>e.scrollLeft');assert (resumed-dragged)%W>8,(dragged,resumed)
 assert page.evaluate('([x,y])=>Boolean(document.elementFromPoint(x,y)?.closest("[data-marquee-viewport]"))',[x,y]),'Gesture must hit rail rather than fixed navigation'
 native_touch=False;wheel_evidence=None;touch_note='Mouse drag plus browser horizontal wheel; native touch drag is unavailable in Linux WebKit automation.'
 if engine=='chromium' and viewport!='desktop':
  session=context.new_cdp_session(page);rb=rail.bounding_box();tx=rb['x']+rb['width']*.8;ty=rb['y']+rb['height']/2;before_touch=rail.evaluate('(e)=>e.scrollLeft');session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':tx,'y':ty,'id':1}]})
  for i in range(1,9):session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':tx-i*16,'y':ty,'id':1}]});time.sleep(.025)
  held=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(1250);still_held=rail.evaluate('(e)=>e.scrollLeft');assert abs(still_held-held)<=2,('Autoplay must not resume while a native touch remains down',held,still_held);expect(rail).to_have_attribute('data-marquee-motion','manual');session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});page.wait_for_timeout(300);after_touch=rail.evaluate('(e)=>e.scrollLeft');assert (after_touch-before_touch)%W>45,(before_touch,after_touch);native_touch=True;touch_note='Chromium native browser touch gesture dispatched via CDP; this is not a physical iPad.'
  page.wait_for_timeout(1800);expect(rail).to_have_attribute('data-marquee-motion','auto');session.detach()
 else:
  # Native wheel scrolling is asynchronous in WebKit. Keep the original >70px
  # movement requirement, but observe the actual trusted input lifecycle rather
  # than assume a 200ms IPC wait includes delivery and scrolling. Autoplay is
  # explicitly forbidden from supplying any pixels needed for a pass.
  page.mouse.move(x,y)
  rail.evaluate('''e=>new Promise(resolve=>requestAnimationFrame(t=>{
    window.__homeWheelProbe={before:{frameTime:t,time:performance.now(),left:e.scrollLeft},event:null,samples:[],seenManual:false,outcome:null};
    e.addEventListener('wheel',event=>{const p=__homeWheelProbe,now=performance.now();
      p.event={time:now,leftAtDelivery:e.scrollLeft,deltaX:event.deltaX,deltaY:event.deltaY,trusted:event.isTrusted};
      p.maximumPreEventAutoPixels=Math.max(0,now-p.before.frameTime)*30/1000;
    },{once:true,passive:true});resolve(__homeWheelProbe.before)}))''')
  page.mouse.wheel(180,0)
  page.wait_for_function('''([e,width])=>{const p=__homeWheelProbe;if(!p.event)return false;
    const delta=((e.scrollLeft-p.before.left)%width+width)%width,mode=e.dataset.marqueeMotion;
    const minimumNativePixels=Math.max(0,delta-p.maximumPreEventAutoPixels);
    p.samples.push({time:performance.now(),left:e.scrollLeft,totalDelta:delta,minimumNativePixels,mode});
    if(mode==='manual')p.seenManual=true;
    if(p.event.trusted&&mode==='manual'&&minimumNativePixels>70){p.outcome='native-movement-passed';return true}
    if(p.seenManual&&mode==='auto'){p.outcome='autoplay-resumed-before-native-movement';return true}
    return false}''',arg=[rail.element_handle(),W],timeout=2000)
  wheel_evidence=page.evaluate('__homeWheelProbe');assert wheel_evidence['outcome']=='native-movement-passed',wheel_evidence
  page.wait_for_timeout(1800);expect(rail).to_have_attribute('data-marquee-motion','auto')
 rail.evaluate('(e)=>{const w=e.querySelector("[data-marquee-primary]").getBoundingClientRect().width;e.scrollLeft=2*w-2}');page.wait_for_timeout(50)
 frames=rail.evaluate('''async(e)=>{const samples=[];for(let i=0;i<135;i++){await new Promise(requestAnimationFrame);const r=e.getBoundingClientRect();const links=[...e.querySelectorAll("a")].map(a=>a.getBoundingClientRect()).filter(a=>a.right>r.left&&a.left<r.right);samples.push({left:e.scrollLeft,covered:links.length>0&&Math.min(...links.map(a=>a.left))<=r.left+1&&Math.max(...links.map(a=>a.right))>=r.right-1});}return samples}''')
 jumps=[b['left']-a['left'] for a,b in zip(frames,frames[1:])];assert any(d<-W/2 for d in jumps),('No actual loop boundary crossed',min(jumps),W);normalized=[d+W if d<-W/2 else d-W if d>W/2 else d for d in jumps];assert min(normalized)>=-1 and max(normalized)<=3,(min(normalized),max(normalized));assert all(f['covered'] for f in frames),'Loop must not expose blank rail'
 return {'automaticMotion':{'targetPixelsPerSecond':30,'allowedPixelsPerSecond':[27,33],'measuredPixelsPerSecond':pixels_per_second,'pixels':delta,'elapsedMs':elapsed,'nominalWaitMs':800,'before':before_sample,'after':after_sample},'nativeWheel':wheel_evidence,'measuredGroupWidth':W,'actualLoopCrossed':True,'maximumNormalizedFrameDelta':max(normalized),'noBlankFrames':True,'mouseDragAndResume':True,'nativeChromiumTouchGesture':native_touch,'nativeTouchHoldChecked':native_touch,'touchLimit':touch_note,'allThreeCopiesIdentical':True,'realStandaloneLogoFiles':sum(bool(i['image']) for i in identities[1]),'typographicFallbackBrands':[i['id'] for i in identities[1] if not i['image']],'noControlsOrScrollbar':True}
def routes(page):
 go(page);rail=page.locator('[data-marquee-viewport]');actual=[]
 for link in rail.locator('[data-marquee-primary] a').all():
  name=link.get_attribute('data-brand-id');href=link.get_attribute('href');assert href.startswith('/guitars?brand=');actual.append((name,href))
 assert len({name for name,href in actual})==10
 for name,href in actual:
  go(page);link=page.locator('[data-marquee-primary] a[data-brand-id="'+name+'"]');link.focus();link.press('Enter');expect(page).to_have_url(BASE+href);expect(page.locator('main h1')).to_be_visible()
 for w,h in [(320,740),(834,1194),(1024,768),(1194,834)]:
  page.set_viewport_size({'width':w,'height':h});go(page);metrics(page)
  for selector in ['#find','#compare']:page.locator(selector).scroll_into_view_if_needed();metrics(page)
 return {'allTenBrandLinksActuallyNavigated':actual,'additionalWidths':[320,834,1024,1194]}
with sync_playwright() as p:
 for engine in args.engines:
  browser=None
  try:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) if engine=='chromium' else p.webkit.launch();report.setdefault('browserVersions',{})[engine]=browser.version
   for viewport in args.viewports:
    w,h=VIEWPORTS[viewport]
    for mode in ['reduce','no-preference']:
     context=browser.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion=mode);page=context.new_page();page.on('console',lambda m:report['consoleErrors'].append({'case':ACTIVE,'text':m.text}) if m.type=='error' else None);page.on('pageerror',lambda e:report['runtimeErrors'].append({'case':ACTIVE,'text':str(e)}));page.on('requestfailed',lambda r:report['failedRequests'].append({'case':ACTIVE,'url':r.url,'failure':r.failure}));page.on('response',lambda r:report['networkErrors'].append({'case':ACTIVE,'url':r.url,'status':r.status}) if r.status>=400 else None)
     if mode=='reduce':
      if 'composition' in args.cases:check(f'{engine}-{viewport}-composition',lambda:composition(page,context,engine,viewport),page)
      if 'quiz' in args.cases:check(f'{engine}-{viewport}-inline-quiz',lambda:inline_quiz(page,engine,viewport),page)
      if 'compare' in args.cases:check(f'{engine}-{viewport}-comparison',lambda:comparison(page,context,engine,viewport),page)
      if 'reduced' in args.cases:check(f'{engine}-{viewport}-reduced-and-keyboard',lambda:reduced(page),page)
      if 'routes' in args.cases and viewport=='desktop':check(f'{engine}-{viewport}-brand-routes-and-responsive',lambda:routes(page),page)
     elif 'carousel' in args.cases:check(f'{engine}-{viewport}-carousel-motion-input-loop',lambda:carousel(page,context,engine,viewport),page)
     context.close()
  except Exception:report.setdefault('harnessErrors',[]).append({'engine':engine,'error':traceback.format_exc()});print('HARNESSFAIL',engine,report['harnessErrors'][-1]['error'],flush=True)
  finally:
   if browser:browser.close()
report['sourceAndBuildUnchangedDuringRun']=start==snapshot();report['passed']=bool(report['checks']) and all(x['passed'] for x in report['checks']) and report['sourceAndBuildUnchangedDuringRun'] and not any(report.get(key) for key in ['consoleErrors','runtimeErrors','networkErrors','failedRequests','harnessErrors']);(OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('RESULT',report['passed'],sum(x['passed'] for x in report['checks']),len(report['checks']),flush=True);raise SystemExit(not report['passed'])
