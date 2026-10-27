from pathlib import Path
from playwright.sync_api import sync_playwright
import json
out=Path(__file__).resolve().parent/'webkit-motion-trace';out.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.webkit.launch();page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='no-preference');page.goto('http://127.0.0.1:5451/',wait_until='networkidle');rail=page.locator('[data-marquee-viewport]');rail.evaluate('(e)=>e.scrollIntoView({block:"center",behavior:"instant"})');page.wait_for_timeout(1400)
 r=rail.evaluate('''async(e)=>{const frames=[],events=[];const begin=performance.now();const listener=()=>events.push({t:performance.now()-begin,x:e.scrollLeft,mode:e.dataset.marqueeMotion});e.addEventListener('scroll',listener,{passive:true});await new Promise(resolve=>{const tick=t=>{frames.push({t:t-begin,x:e.scrollLeft,mode:e.dataset.marqueeMotion,docHidden:document.hidden,viewport:e.getBoundingClientRect().top});if(t-begin<1800)requestAnimationFrame(tick);else resolve()};requestAnimationFrame(tick)});e.removeEventListener('scroll',listener);return {frames,events}}''');(out/'trace.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));b.close()
