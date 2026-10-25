"""Diagnose startup render/resize settling without changing app code."""
from pathlib import Path
import argparse, hashlib, json
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('--url',required=True);ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',locale='th-TH')
    context.add_init_script('''(() => {
      window.__practiceTimeline=[];
      const state=()=>{ const c=document.querySelector('canvas[data-practice-canvas]'); const r=c?.getBoundingClientRect(); return {at:performance.now(),count:c?.dataset.renderCount,asset:c?.dataset.handAssetStatus,width:r?.width,height:r?.height}; };
      const raf=window.requestAnimationFrame.bind(window);
      window.requestAnimationFrame=callback=>{ const origin=new Error().stack;const scheduled=performance.now(); return raf(time=>{window.__practiceTimeline.push({kind:'raf-before',scheduled,origin,...state()});callback(time);window.__practiceTimeline.push({kind:'raf-after',...state()});}); };
      const NativeResizeObserver=window.ResizeObserver;
      window.ResizeObserver=class extends NativeResizeObserver {constructor(callback){super((entries,observer)=>{window.__practiceTimeline.push({kind:'resize',rects:entries.map(e=>({width:e.contentRect.width,height:e.contentRect.height})),...state()});callback(entries,observer);});}};
    })();''')
    page=context.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(args.url.rstrip('/')+'/practice',wait_until='networkidle')
    canvas=page.locator('canvas[data-practice-canvas]')
    expect(canvas).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
    page.evaluate('document.fonts.ready')
    samples=[]
    for _ in range(25):
        samples.append(canvas.evaluate('c=>({at:performance.now(),count:Number(c.dataset.renderCount),asset:c.dataset.handAssetStatus,width:c.getBoundingClientRect().width,height:c.getBoundingClientRect().height})'))
        page.wait_for_timeout(250)
    trace=page.evaluate('window.__practiceTimeline')
    report={'scope':'Startup timing diagnosis; instrumentation only observes existing app rAF and ResizeObserver callbacks',
      'browserVersion':browser.version,'samples':samples,'trace':trace,'runtimeErrors':errors,
      'productionSceneSHA256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'dist/assets').glob('practice-three-*.js')}}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'samples':samples,'resizeEvents':[e for e in trace if e['kind']=='resize'],'runtimeErrors':errors},indent=2))
    browser.close()
