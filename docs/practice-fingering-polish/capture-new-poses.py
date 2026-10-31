"""Capture integrated endpoints using the real production GLB, never fixtures."""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
rows=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
 context=browser.new_context(viewport={'width':1194,'height':834},has_touch=True,reduced_motion='reduce');page=context.new_page()
 for key in [row['id'] for row in json.loads((OUT/'import-ledger.json').read_text())['newAccepted']]:
  assert page.goto('http://127.0.0.1:4196/practice?chord='+key,wait_until='domcontentloaded').status==200
  canvas=page.locator('canvas[data-practice-canvas]');expect(canvas).to_have_attribute('data-hand-asset-status','ready',timeout=60000);expect(canvas).to_have_attribute('data-hand-visible','true')
  page.locator('.practice-camera-views summary').click()
  for view in ['front','side','player']:
   page.locator('[data-camera-preset="'+view+'"]').click()
   page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
   file=OUT/'screenshots'/('new-'+key+'-'+view+'.png');page.locator('.practice-viewer').screenshot(path=str(file),animations='disabled')
   rows.append({'chord':key,'view':view,'screenshot':str(file.relative_to(ROOT)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'transformSignature':canvas.get_attribute('data-hand-pose-signature'),'handVisible':True,'teachingApprovalClaimed':False})
 context.close();browser.close()
(OUT/'tests/new-pose-captures.json').write_text(json.dumps({'actualGLB':True,'productionBuild':True,'physicalIPad':False,'rows':rows},indent=2)+'\n')
print(json.dumps({'captures':len(rows),'teachingApprovalClaimed':False}))
