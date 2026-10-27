from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,traceback
ROOT=Path(__file__).resolve().parents[3]
out=ROOT/'docs/premium-quiz-compare/tests/home-shared';out.mkdir(exist_ok=True)
BASE='http://127.0.0.1:5451';IDS=['yamaha-pacifica-612viifm','yamaha-fg820-12','martin-d-28'];report={'checks':[],'consoleErrors':[],'runtimeErrors':[],'physicalIPadSafariTested':False}
def check(name,value=True):
 report['checks'].append({'name':name,'passed':bool(value)});print('PASS' if value else 'FAIL',name,flush=True);assert value,name
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');context.add_init_script('localStorage.setItem("fretline:compare",'+json.dumps(json.dumps(IDS))+')');page=context.new_page();page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)));page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
  page.goto(BASE+'/',wait_until='networkidle');expect(page.locator('#home-compare-title')).to_be_visible()
  def expand():
   page.locator('[data-home-compare-expand]').click();expect(page.locator('[data-home-compare-panel]')).to_be_visible();table=page.locator('[data-home-compare-panel] [role=table]');expect(table).to_be_visible();return table
  def info():
   return page.locator('[data-home-compare-panel]').evaluate('''e=>({premiumAncestor:!!e.closest('.premium-compare'),compact:e.querySelectorAll('[data-compact-comparison]').length,images:e.querySelectorAll('img').length,models:[...e.querySelectorAll('[role=columnheader] > a.font-serif')].map(a=>a.textContent),styles:[...e.querySelectorAll('[role=columnheader] a,img,[role=cell]')].map(a=>{let s=getComputedStyle(a),r=a.getBoundingClientRect();return {text:a.textContent,font:s.fontSize,color:s.color,fit:s.objectFit,width:Math.round(r.width),height:Math.round(r.height)}})})''')
  expand();page.evaluate('document.fonts.ready');before=info();check('Home full comparison uses original noncompact model header',before['compact']==0 and before['images']>=3 and len(before['models'])==3);check('Home remove controls retain all actual selected IDs',page.locator('[data-home-compare-panel] [data-compare-remove]').count()==3)
  page.locator('.home-experience-cta[href="/compare"]').click();expect(page.locator('.premium-compare')).to_be_visible();check('Navigating Compare loads new scoped page style',page.locator('[data-compact-comparison]').count()==1)
  page.locator('header a[href="/"]').first.click();expect(page.locator('#home-compare-title')).to_be_visible();expand();after=info();check('Home full comparison has identical computed styles after Compare CSS loads',before==after);check('Home remains outside premium page CSS scope',not after['premiumAncestor']);page.locator('[data-home-compare-panel] [data-compare-remove]').first.click();expect(page.locator('[data-home-compare-panel] [data-compare-remove]')).to_have_count(2);check('Shared full-table remove action updates actual selection')
  check('No page horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'));check('No console/runtime errors',not report['consoleErrors'] and not report['runtimeErrors']);report['before']=before;report['after']=after;browser.close()
 report['passed']=True
except Exception:
 report['passed']=False;report['failure']=traceback.format_exc();print(report['failure'],flush=True)
(out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise SystemExit(not report['passed'])
