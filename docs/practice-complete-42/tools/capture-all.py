"""All 42 real GLB poses in an isolated authoring view, including rejected ones.
Rejected candidates are never exposed by the public Practice route.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/practice-complete-42'
ap=argparse.ArgumentParser();ap.add_argument('--library',type=Path);ap.add_argument('--label',default='baseline');args=ap.parse_args()
lib=json.loads((args.library or ROOT/'src/features/practice/assets/hand-poses.json').read_text());chords=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"],cwd=ROOT));folder=OUT/'screenshots'/args.label;folder.mkdir(parents=True,exist_ok=True);report={'realGLB':True,'publicGateModified':False,'poseSource':str(args.library or 'runtime-baseline'),'sourceSHA256':hashlib.sha256((args.library or ROOT/'src/features/practice/assets/hand-poses.json').read_bytes()).hexdigest(),'rows':[],'errors':[]}
report_file=OUT/'tests'/('captures-'+args.label+'.json')
previous=json.loads(report_file.read_text())if report_file.exists()else{'rows':[]}
viewer_sha=hashlib.sha256(Path(__file__).with_name('inspector.js').read_bytes()+Path(__file__).with_name('inspector.html').read_bytes()+(ROOT/'src/features/practice/data/chords.js').read_bytes()).hexdigest()
report['viewerSourceSHA256']=viewer_sha
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);context=browser.new_context(viewport={'width':1100,'height':740},reduced_motion='reduce');page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.goto('http://127.0.0.1:4197/docs/practice-complete-42/tools/inspector.html');expect(page.locator('body')).to_have_attribute('data-ready','true',timeout=60000)
 for chord in chords:
  key=chord['id'];scene_sha=hashlib.sha256(json.dumps({'root':lib['poses'][key]['root'],'bones':lib['poses'][key]['bones'],'pressure':lib['poses'][key].get('pressOffsetsMm')},sort_keys=True,separators=(',',':')).encode()).hexdigest();page.evaluate('([id,p])=>inspect.choose(id,p)',[key,lib['poses'][key]])
  for view in ['front','side','back','player']:
   file=folder/(key+'-'+view+'.png');prior=next((r for r in previous['rows']if r['id']==key and r['view']==view and r.get('sceneSHA256')==scene_sha and r.get('viewerSourceSHA256')==viewer_sha and file.exists()and hashlib.sha256(file.read_bytes()).hexdigest()==r['imageSHA256']),None)
   if prior:report['rows'].append(prior);continue
   page.evaluate('v=>inspect.viewAngle(v)',view);page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');file=folder/(key+'-'+view+'.png');page.screenshot(path=str(file),animations='disabled');meta=page.evaluate('({signature:inspect.signature(),triangles:inspect.renderInfo().triangles,model:inspect.modelSHA256})');assert meta['triangles']>16000
   report['rows'].append({'id':key,'view':view,'file':str(file.relative_to(ROOT)),'imageSHA256':hashlib.sha256(file.read_bytes()).hexdigest(),'actual':meta,'notTeachingApproval':True,'sceneSHA256':scene_sha,'viewerSourceSHA256':viewer_sha})
  report_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('CAPTURED',key,flush=True)
 context.close();browser.close()
for view in ['front','side','back','player']:
 for batch in range(3):
  group=chords[batch*14:(batch+1)*14];sheet=Image.new('RGB',(1100,7*380),'#080808');draw=ImageDraw.Draw(sheet)
  for i,chord in enumerate(group):
   im=Image.open(folder/(chord['id']+'-'+view+'.png')).convert('RGB');im.thumbnail((550,370));x=(i%2)*550;y=(i//2)*380;sheet.paste(im,(x,y));draw.text((x+8,y+365),chord['id']+' / '+chord['voicing'],fill='#d9b675')
  sheet.save(folder/('sheet-'+view+'-'+str(batch+1)+'.jpg'),quality=92)
(OUT/'tests'/('captures-'+args.label+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'captures':len(report['rows']),'errors':report['errors']}));assert len(report['rows'])==168 and not report['errors']
