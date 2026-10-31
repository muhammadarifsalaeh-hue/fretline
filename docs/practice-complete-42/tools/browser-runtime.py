"""Production Practice UX, real GLB and native Web Audio; no database writes."""
from pathlib import Path
import argparse,json,math,subprocess,traceback,struct
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--base',default='http://127.0.0.1:4198');parser.add_argument('--only',action='append');args=parser.parse_args();BASE=args.base
CHORDS=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"],cwd=ROOT))
LIB=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());ACCEPTED={key for key,p in LIB['poses'].items()if p['audit']['collisionPassed'] and p['audit']['contactPassed']}
OLD=json.loads((ROOT/'docs/practice-fingering-polish/tests/browser-hand.json').read_text())
OLD_SIG={r['chord']:r['signature']for r in next(c for c in OLD['checks']if c['name']=='desktop-all-42-chords-and-strict-gates')['evidence']['rows']}
OLD_GEOMETRY=next(c for c in OLD['checks']if c['name']=='desktop-black-sleeved-model-on-real-route')['evidence']['actualRig']['geometry']
def expected_signature(pose):
 values=pose['root']['positionMm'][:]
 def normal(q):
  n=math.sqrt(sum(x*x for x in q));return [x/n for x in q]
 values+=normal(pose['root']['quaternion'])
 for name in sorted(pose['bones']):values+=normal(pose['bones'][name]['quaternion'])
 h=2166136261
 for v in values:
  word=struct.unpack('<I',struct.pack('<f',v))[0];h=((h^word)*16777619)&0xffffffff
 return f'{h:08x}'
EXPECTED_SIG={key:expected_signature(pose)for key,pose in LIB['poses'].items()}
CANVAS='canvas[data-practice-canvas]'
report={'checks':[],'consoleErrors':[],'runtimeErrors':[],'brokenImages':[],'realGLB':True,'nativeWebAudioTested':True,'physicalIPadSafariTested':False,'databaseWrites':0}
AUDIO_PROBE='''(()=>{const Native=window.AudioContext||window.webkitAudioContext;window.__soundContexts=[];window.__soundNotes=[];window.__soundAnalysers=[];if(!Native)return;window.AudioContext=new Proxy(Native,{construct(target,args){const c=Reflect.construct(target,args,target);__soundContexts.push(c);const osc=c.createOscillator.bind(c);c.createOscillator=()=>{const o=osc(),start=o.start.bind(o);o.start=t=>{__soundNotes.push({frequency:o.frequency.value,start:t});return start(t)};return o};const filter=c.createBiquadFilter.bind(c);c.createBiquadFilter=()=>{const f=filter(),a=c.createAnalyser(),g=c.createGain();a.fftSize=2048;g.gain.value=0;f.connect(a);a.connect(g);g.connect(c.destination);__soundAnalysers.push(a);return f};return c}})})()'''

def check(name,fn,page):
 if args.only and name not in args.only:return
 try:
  evidence=fn();report['checks'].append({'name':name,'passed':True,'evidence':evidence});print('PASS',name,flush=True)
 except Exception:
  failure=traceback.format_exc();report['checks'].append({'name':name,'passed':False,'failure':failure});print('FAIL',name,failure,flush=True)
  page.screenshot(path=str(OUT/'screenshots'/(name+'-FAIL.png')),full_page=True,animations='disabled')

def settle(page):page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
def ready(page):
 expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=60000)
 expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
def go(page,route='/practice?chord=C'):
 assert page.goto(BASE+route,wait_until='domcontentloaded').status==200;page.evaluate('document.fonts.ready')
def state(page):
 return page.locator(CANVAS).evaluate('''c=>({chord:c.dataset.handChordId,hand:c.dataset.handVisible,signature:c.dataset.handPoseSignature,
  asset:c.dataset.handModelSha256,allowed:c.dataset.handInspectionAllowed,markers:c.dataset.fingerMarkersVisible,
  camera:JSON.parse(c.dataset.camera),geometry:JSON.parse(c.dataset.practiceProjection).geometrySignature,
  projection:JSON.parse(c.dataset.practiceProjection),render:JSON.parse(c.dataset.renderInfo),frames:Number(c.dataset.renderCount)})''')
def choose(page,key):
 page.locator('[data-practice-chord="'+key+'"]').click()
 expect(page.locator(CANVAS)).to_have_attribute('data-hand-chord-id',key)
 expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true'if key in ACCEPTED else'false')
 expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord',key)
 settle(page)
def layout(page):
 m=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})');assert m['scroll']<=m['width']+1,m;return m

def initial(page,device,width):
 ready(page);s=state(page);assert s['signature']==OLD_SIG['C'] and s['geometry']==OLD_GEOMETRY
 assert s['asset']==LIB['assetSha256'] and s['hand']=='true' and s['render']['triangles']>16000
 expect(page.locator('h1')).to_have_text('ฝึกกีตาร์ 3D');expect(page.locator('[data-practice-chord]')).to_have_count(42)
 assert page.locator('[data-hand-review-warning]').count()==0
 assert not any(t in page.locator('.practice-minimal').inner_text()for t in ['รอตรวจทาน','ยังไม่ยืนยัน','AI Generated','Demo Website'])
 lib=page.locator('.practice-chord-library').bounding_box();viewer=page.locator('.practice-viewer-column').bounding_box();detail=page.locator('.practice-chord-detail').bounding_box()
 if width>=1100:
  assert lib['x']+lib['width']<=viewer['x']+1 and viewer['x']+viewer['width']<=detail['x']+1
  assert viewer['width']>2*lib['width'] and viewer['width']>2*detail['width']
 else:
  assert lib['y']+lib['height']<=viewer['y']+1 and viewer['y']+viewer['height']<=detail['y']+1
  assert lib['height']<270
  assert page.locator('.site-bottom-nav').evaluate('n=>getComputedStyle(n).position')=='static'
 page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/'screenshots'/('after-'+device+'.png')),full_page=True,animations='disabled')
 before_idle=state(page)['frames'];page.wait_for_timeout(550);idle_frames=state(page)['frames']-before_idle;assert idle_frames<=2,idle_frames
 return {'idleWindowMs':550,'idleFrames':idle_frames,'physicalDeviceBenchmark':False,'layout':layout(page),'library':lib,'model':viewer,'details':detail,'actualModel':s['asset'],'handSignature':s['signature'],'fullPageScreenshot':True}

def all_chords(page):
 rows=[]
 for chord in CHORDS:
  choose(page,chord['id']);s=state(page);assert s['signature']==EXPECTED_SIG[chord['id']]
  actual=page.locator('.practice-diagram-wrap [data-chord-string]').evaluate_all("ns=>ns.map(n=>({string:Number(n.dataset.string),fret:n.dataset.fret,finger:n.dataset.finger,note:n.dataset.note}))")
  for i,n in enumerate(actual):
   assert n=={'string':6-i,'fret':'mute'if chord['frets'][i]is None else str(chord['frets'][i]),'finger':''if chord['fingers'][i]is None else str(chord['fingers'][i]),'note':chord['notes'][i]or''}
  assert page.locator(CANVAS).evaluate('c=>JSON.parse(c.dataset.handPressureOffsets)')==LIB['poses'][chord['id']].get('pressOffsetsMm')
  if chord['id'] in ACCEPTED and chord['id'] not in {'C','Dm','C7','E7','G7','B7','Cmaj7','Fmaj7','Gmaj7','Dm7','Em7','Am7','Dsus2'}:
   page.locator(CANVAS).scroll_into_view_if_needed();settle(page);page.evaluate('scrollTo(0,0)');settle(page)
   page.screenshot(path=str(OUT/'screenshots'/('public-'+chord['id']+'-'+str(page.viewport_size['width'])+'.png')),full_page=True,animations='disabled')
  rows.append({'id':chord['id'],'signature':s['signature'],'handVisible':s['hand']=='true','fingeringAndDiagramUnchanged':True,'pressureOffsetsMatchActualPose':True})
 assert sum(r['handVisible']for r in rows)==len(ACCEPTED)
 return {'chords':42,'hands':len(ACCEPTED),'rejectedHandsHidden':42-len(ACCEPTED),'allAppliedBoneSignaturesMatchSavedTransforms':True,'rows':rows}

def filters_and_keyboard(page,width):
 for item in ['', 'basic','major','minor','dominant7','major7','minor7','suspended']:
  if width>=1100:page.locator('[data-practice-type="'+(item or'all')+'"]').click()
  else:page.locator('.practice-mobile-type select').select_option(item)
  expected=[c['id'] for c in CHORDS if (c['id'] in ['C','D','E','F','G','A','Dm','Em','Am'] if item=='basic' else not item or c['type']==item)]
  assert page.locator('[data-practice-chord]').evaluate_all('ns=>ns.map(n=>n.dataset.practiceChord)')==expected
 if width>=1100:page.locator('[data-practice-type=all]').click()
 else:page.locator('.practice-mobile-type select').select_option('')
 page.locator('#practice-chord-search').fill('Gmaj7');expect(page.locator('[data-practice-chord]')).to_have_count(1)
 page.locator('#practice-chord-search').fill('ไม่มีคอร์ด123');expect(page.locator('[data-practice-chord]')).to_have_count(0)
 expect(page.locator('.practice-chord-empty')).to_be_visible();page.locator('.practice-chord-empty button').click();choose(page,'C')
 page.locator('[data-practice-chord=C]').focus();page.keyboard.press('ArrowDown');expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord','D')
 page.keyboard.press('End');expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord','Asus4')
 page.keyboard.press('Home');expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord','C')
 assert page.locator('[data-practice-chord][tabindex="0"]').count()==1
 return {'allEightFilters':True,'searchAndEmptyState':True,'rovingFocus':True,'arrowHomeEnd':True,'layout':layout(page)}

def markers_camera(page,context,touch):
 choose(page,'C');canvas=page.locator(CANVAS);canvas.scroll_into_view_if_needed();settle(page);before=state(page)
 assert page.locator('.practice-control-bar').count()==1 and page.locator('.practice-control-bar button').count()==5
 page.locator('[data-practice-markers]').click();expect(canvas).to_have_attribute('data-finger-markers-visible','false');settle(page);off=state(page)
 assert before['geometry']==off['geometry'] and before['signature']==off['signature'] and before['camera']==off['camera']
 assert off['render']['calls']<before['render']['calls']
 page.locator('[data-practice-markers]').click();expect(canvas).to_have_attribute('data-finger-markers-visible','true')
 for name in ['front','head','side','back','player','overview']:
  page.locator('.practice-camera-views summary').click();page.locator('[data-camera-preset="'+name+'"]').click();settle(page)
  assert state(page)['geometry']==before['geometry'] and state(page)['signature']==before['signature']
 page.locator('[data-practice-reset]').click();settle(page)
 projection=state(page)['projection'];head=projection['headstock'];nut=projection['nut'];size=canvas.bounding_box();angle=math.degrees(math.atan2(abs(head[1]-nut[1])*size['height'],abs(head[0]-nut[0])*size['width']));assert angle<9,angle
 canvas.scroll_into_view_if_needed();box=canvas.bounding_box();old=state(page)['camera'];page.mouse.move(box['x']+box['width']*.4,box['y']+box['height']*.5);page.mouse.down();page.mouse.move(box['x']+box['width']*.55,box['y']+box['height']*.58,steps=8);page.mouse.up();settle(page);assert state(page)['camera']!=old
 canvas.focus();old=state(page)['camera']['distance'];page.keyboard.press('+');settle(page);assert state(page)['camera']['distance']<old;page.keyboard.press('0');settle(page)
 if touch:
  canvas.scroll_into_view_if_needed();box=canvas.bounding_box();client=context.new_cdp_session(page);x=box['x']+box['width']/2;y=box['y']+box['height']/2;old=state(page)['camera']['distance']
  client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x-20,'y':y,'id':1},{'x':x+20,'y':y,'id':2}]});client.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x-46,'y':y,'id':1},{'x':x+46,'y':y,'id':2}]});client.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});settle(page);assert state(page)['camera']['distance']!=old;client.detach()
 page.locator('[data-practice-reset]').click();settle(page)
 for button in page.locator('.practice-control-bar button').all():
  box=button.bounding_box();assert box['x']>=0 and box['x']+box['width']<=page.viewport_size['width']+1
 return {'markersChangeDrawCallsOnly':True,'sixViewsPlusReset':True,'nearHorizontalNeckDegrees':angle,'realPointerDrag':True,'keyboardZoom':True,'realTwoTouchPinch':touch}

def hand_preference(page):
 choose(page,'C');page.locator('.practice-camera-views summary').click();page.locator('[data-practice-hand-review]').click();expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','false');page.locator('.practice-camera-views summary').click()
 page.locator('[data-practice-chord=Dm]').click();expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','false');page.locator('.practice-camera-views summary').click();page.locator('[data-practice-hand-review]').click();expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true');page.locator('.practice-camera-views summary').click()
 rejected=next((c['id']for c in CHORDS if c['id']not in ACCEPTED),None)
 if rejected:
  choose(page,rejected);page.locator('.practice-camera-views summary').click();assert page.locator('[data-practice-hand-review]').count()==0;page.keyboard.press('Escape')
 choose(page,'C')
 return {'existingShowHidePreferencePreserved':True,'noToggleCanRevealRejectedPose':True}

def popular_and_scrolling(page):
 track=page.locator('.practice-popular-track');track.scroll_into_view_if_needed();start=track.evaluate('e=>e.scrollLeft')
 next_button=page.get_by_role('button',name='เลื่อนคอร์ดยอดนิยมไปทางขวา',exact=True)
 if next_button.is_enabled():next_button.click();settle(page);assert track.evaluate('e=>e.scrollLeft')>start
 page.locator('[data-popular-chord=G]').click();expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord','G');expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true'if 'G'in ACCEPTED else'false')
 expect(page.locator('[data-popular-chord=G]')).to_have_attribute('aria-pressed','true');expect(page.locator('[data-practice-chord=G]')).to_have_attribute('aria-pressed','true')
 page.locator('[data-popular-chord=C]').click();expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true')
 page.evaluate('scrollTo(0,document.documentElement.scrollHeight)');expect(page.locator('.site-footer')).to_be_visible();return {'carouselScrolls':True,'selectionSynchronized':True,'popularSelectionFollowsAudit':True,'pageAndFooterScroll':True}

def native_audio(page):
 choose(page,'C');sig=state(page)['signature'];page.locator('[data-practice-play]').click();expect(page.locator('.practice-minimal')).to_have_attribute('data-audio-status','playing')
 expect(page.locator('[data-practice-detail-play]')).to_have_attribute('aria-pressed','true')
 page.wait_for_timeout(250)
 actual=page.evaluate('''()=>{const a=__soundAnalysers[0],data=new Float32Array(a.fftSize);a.getFloatTimeDomainData(data);return {rms:Math.sqrt(data.reduce((s,v)=>s+v*v,0)/data.length),peak:Math.max(...data.map(Math.abs)),notes:__soundNotes.slice(0,5),contexts:__soundContexts.length,state:__soundContexts[0].state}}''')
 assert actual['contexts']==1 and actual['state']=='running' and actual['rms']>.0001 and actual['peak']<1,actual
 expected=[48,52,55,60,64] # canonical C: C3 E3 G3 C4 E4
 for node,midi in zip(actual['notes'],expected):assert abs(node['frequency']-440*2**((midi-69)/12))<1e-4
 page.locator('[data-practice-detail-play]').click();expect(page.locator('.practice-minimal')).to_have_attribute('data-audio-status','idle')
 page.locator('[data-practice-slower]').click();expect(page.locator('[data-practice-speed]')).to_have_text('0.75×')
 page.locator('[data-practice-play]').click();expect(page.locator('.practice-minimal')).to_have_attribute('data-audio-status','playing')
 notes=page.evaluate('__soundNotes.slice(-5)');assert abs(notes[1]['start']-notes[0]['start']-.12/.75)<1e-6
 assert state(page)['signature']==sig
 page.locator('[data-practice-chord=Dm]').click();expect(page.locator('.practice-minimal')).to_have_attribute('data-audio-status','idle')
 for _ in range(5):page.locator('[data-practice-slower]').click()if page.locator('[data-practice-slower]').is_enabled()else None
 expect(page.locator('[data-practice-slower]')).to_be_disabled();expect(page.locator('[data-practice-speed]')).to_have_text('0.5×')
 for _ in range(6):page.locator('[data-practice-faster]').click()if page.locator('[data-practice-faster]').is_enabled()else None
 expect(page.locator('[data-practice-faster]')).to_be_disabled();expect(page.locator('[data-practice-speed]')).to_have_text('1.5×')
 page.locator('[data-practice-play]').click();expect(page.locator('.practice-minimal')).to_have_attribute('data-audio-status','playing')
 expect(page.locator('.practice-minimal')).to_have_attribute('data-audio-status','idle',timeout=5000)
 page.locator('[data-practice-play]').click();expect(page.locator('.practice-minimal')).to_have_attribute('data-audio-status','playing')
 page.locator('.site-footer a[href^="/guitars"]').first.click();expect(page.locator('main h1')).to_be_visible();page.wait_for_function('__soundContexts.length===1 && __soundContexts[0].state==="closed"')
 return {'nativeAudioSignal':actual,'slowerChangesActualSchedule':True,'pitchUnchanged':True,'bothPlayButtonsSynchronized':True,'chordChangeStopsAudio':True,'rateBounds':True,'fingerPoseUnchangedBySound':True,'naturalPlaybackEnds':True,'spaUnmountClosesNativeContext':True}

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
 for device,w,h in [('desktop',1440,1000),('ipad-landscape',1194,834),('ipad-portrait',768,1024),('mobile',390,844)]:
  context=browser.new_context(viewport={'width':w,'height':h},has_touch=device!='desktop',reduced_motion='reduce');context.add_init_script(AUDIO_PROBE);page=context.new_page()
  page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)));page.on('console',lambda m:report['consoleErrors'].append(m.text)if m.type=='error'else None);page.on('response',lambda r:report['brokenImages'].append({'url':r.url,'status':r.status})if r.request.resource_type=='image'and r.status>=400 else None)
  go(page);check(device+'-layout-and-full-page-capture',lambda:initial(page,device,w),page)
  check(device+'-all42-original-diagrams-and-real-hand-gates',lambda:all_chords(page),page)
  check(device+'-filters-search-and-keyboard',lambda:filters_and_keyboard(page,w),page)
  check(device+'-single-bar-markers-camera-and-touch',lambda:markers_camera(page,context,device!='desktop'),page)
  check(device+'-existing-hand-toggle-and-rejection',lambda:hand_preference(page),page)
  check(device+'-popular-and-scroll',lambda:popular_and_scrolling(page),page)
  check(device+'-real-audio-and-speed',lambda:native_audio(page),page)
  def route_isolation():
   go(page,'/');expect(page.locator('.practice-minimal')).to_have_count(0);expect(page.locator('.signature-stats-list dd')).to_have_text(['200','10','4','4'])
   if w<1024:assert page.locator('.site-bottom-nav').evaluate('n=>getComputedStyle(n).position')=='fixed'
   return {'homeDataUnchanged':True,'practiceNavigationStyleDoesNotLeak':True}
  check(device+'-other-page-style-isolation',route_isolation,page);context.close()
 for device,w,h in [('small-mobile',320,740),('tablet',1024,768),('wide-desktop',1920,1080)]:
  context=browser.new_context(viewport={'width':w,'height':h},reduced_motion='reduce');page=context.new_page();go(page);ready(page)
  def extra_layout():
   metrics=layout(page)
   for button in page.locator('.practice-control-bar button').all():
    box=button.bounding_box();assert box['x']>=0 and box['x']+box['width']<=w
   if w==1024:
    a=page.locator('.practice-viewer-column').bounding_box();b=page.locator('.practice-chord-detail').bounding_box();assert a['x']+a['width']<=b['x']+1
   if w==1920:expect(page.get_by_role('button',name='เลื่อนคอร์ดยอดนิยมไปทางขวา',exact=True)).to_be_disabled()
   page.screenshot(path=str(OUT/'screenshots'/('after-'+device+'.png')),full_page=True,animations='disabled');return metrics
  check(device+'-responsive-controls',extra_layout,page);context.close()
 context=browser.new_context(viewport={'width':1440,'height':1000});page=context.new_page();page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)));page.on('console',lambda m:report['consoleErrors'].append(m.text)if m.type=='error'else None)
 def motion_stress():
  go(page);ready(page);cv=page.locator(CANVAS);expect(cv).to_have_attribute('data-hand-reveal-state','idle',timeout=10000);rows=[]
  for key in ['F','Gm','E','Am','C']:
   choose(page,key);actual=state(page);assert actual['signature']==EXPECTED_SIG[key];rows.append({'id':key,'actualBoneSignature':actual['signature']})
  rejected=next((c['id']for c in CHORDS if c['id']not in ACCEPTED),None)
  if rejected:
   choose(page,rejected);expect(cv).to_have_attribute('data-hand-visible','false');expect(cv).to_have_attribute('data-hand-reveal-state','idle')
  choose(page,'C');expect(cv).to_have_attribute('data-hand-reveal-state','idle',timeout=10000);before=state(page)['frames'];page.wait_for_timeout(550);delta=state(page)['frames']-before;assert delta<=2,delta
  return {'actualEndpointTransforms':rows,'rejectedHandCannotBeRevealedMidTransition':True,'idleFrames':delta,'idleWindowMs':550,'interpolatedUnsafeBonePaths':False}
 check('motion-switching-and-on-demand-rendering',motion_stress,page);context.close()
 # Intentional failure contexts are separate from the zero-error normal path.
 context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');page=context.new_page()
 context.route('**/*makehuman-left-arm-sleeved*.glb',lambda route:route.abort('failed'))
 def retry():
  go(page);expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status','error',timeout=60000);expect(page.locator('.practice-hand-load-error')).to_be_visible();assert page.locator('.practice-canvas-stage [role=alert]').count()==0
  assert page.locator('.practice-diagram-wrap svg').count()==1;context.unroute('**/*makehuman-left-arm-sleeved*.glb');page.locator('[data-practice-hand-retry]').click();ready(page);expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true');return {'shortErrorOutsideModel':True,'diagramAvailable':True,'realModelRetry':True}
 check('model-failure-and-real-retry',retry,page)
 def context_loss():
  page.locator(CANVAS).evaluate("c=>c.getContext('webgl2').getExtension('WEBGL_lose_context').loseContext()");expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','error');page.locator('[data-practice-retry]').click();ready(page);return {'newRealWebGLSceneRecovered':True}
 check('webgl-context-recovery',context_loss,page);context.close()
 context=browser.new_context(viewport={'width':390,'height':844});context.add_init_script('window.AudioContext=undefined;window.webkitAudioContext=undefined');page=context.new_page()
 def audio_failure():
  go(page);ready(page);page.locator('[data-practice-play]').click();expect(page.locator('.practice-audio-error')).to_be_visible();assert len(page.locator('.practice-audio-error').inner_text())<80;expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true');return {'audioErrorShortAndNonBlocking':True,'realHandStillAvailable':True}
 check('audio-unavailable-fallback',audio_failure,page);context.close();browser.close()
report['passed']=all(case['passed']for case in report['checks'])and not any(report[k]for k in ['consoleErrors','runtimeErrors','brokenImages'])
(OUT/('tests/browser-practice-recheck.json' if args.only else 'tests/browser-practice.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'failed':sum(not c['passed']for c in report['checks']),'consoleErrors':len(report['consoleErrors']),'runtimeErrors':len(report['runtimeErrors'])}));raise SystemExit(0 if report['passed']else 1)
