from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/practice-complete-42/screenshots/new';OUT.mkdir(parents=True,exist_ok=True);sources={'Csus4':ROOT/'.local-preview/practice-complete-42/Csus4-thumb/candidate.json'}
for item in json.loads((ROOT/'docs/practice-complete-42/tests/candidate-support.json').read_text()):
 if item['source']!='baseline'and item['thumbSupportPassed']and item['jointPlausibilityPassed']:
  path=ROOT/item['proposal'];pose=json.loads(path.read_text())['poses'][item['id']];target=OUT/(item['id']+'-capture-pose.json');target.write_text(json.dumps(pose));sources[item['id']]=target
rows=[]
with sync_playwright()as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':1100,'height':740},reduced_motion='reduce');page.goto('http://127.0.0.1:4197/docs/practice-complete-42/tools/inspector.html');expect(page.locator('body')).to_have_attribute('data-ready','true',timeout=60000)
 for key,file in sources.items():
  pose=json.loads(file.read_text());page.evaluate('([id,p])=>inspect.choose(id,p)',[key,pose])
  for view in ['front','side','back','player']:
   scene=hashlib.sha256(json.dumps({'root':pose['root'],'bones':pose['bones'],'pressOffsetsMm':pose.get('pressOffsetsMm')},sort_keys=True,separators=(',',':')).encode()).hexdigest()
   target=OUT/(key+'-'+scene[:8]+'-'+view+'.png')
   if target.exists():continue
   page.evaluate('v=>inspect.viewAngle(v)',view);page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');page.screenshot(path=str(target),animations='disabled');rows.append({'id':key,'view':view,'poseTransformSHA256':hashlib.sha256(json.dumps({'root':pose['root'],'bones':pose['bones']},sort_keys=True,separators=(',',':')).encode()).hexdigest(),'poseSource':str(file.relative_to(ROOT)),'screenshot':str(target.relative_to(ROOT)),'SHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'actualBoneSignature':page.evaluate('inspect.signature()')})
  print('CAPTURED',key,flush=True)
 b.close()
path=ROOT/'docs/practice-complete-42/tests/captures-new.json';previous=json.loads(path.read_text())if path.exists()else{'rows':[]};previous['rows']+=rows;path.write_text(json.dumps(previous,indent=2)+'\n')
