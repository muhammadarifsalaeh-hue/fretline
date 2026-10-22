'''Reproduce audit findings without changing any application data or files.'''
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json,traceback

OUT=Path(__file__).resolve().parent/'focused'
OUT.mkdir(parents=True,exist_ok=True)
BASE='http://127.0.0.1:5192'
ID='yamaha-pacifica-612viifm'
report={'baseline':'82fbe9b','findings':{},'screenshots':[],'errors':[]}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':1440,'height':1000})
  page=context.new_page()
  page.goto(BASE+'/guitars?q=612VIIFM',wait_until='networkidle')
  card=page.locator('article[data-guitar-id="'+ID+'"]')
  image=card.locator('.catalog-card-image img');image.evaluate('(i)=>i.decode()')
  card.scroll_into_view_if_needed();page.mouse.move(10,120)
  card.screenshot(path=str(OUT/'catalog-image-before-hover.png'),animations='disabled')
  before=image.evaluate('(i)=>({rect:i.getBoundingClientRect().toJSON(),transform:getComputedStyle(i).transform,fit:getComputedStyle(i).objectFit})')
  card.hover();page.wait_for_timeout(850)
  hovered=image.evaluate('''i=>{const r=i.getBoundingClientRect(),f=i.closest('.catalog-card-image').getBoundingClientRect();
    const s=getComputedStyle(i),matrix=new DOMMatrixReadOnly(s.transform),scale=matrix.a;
    const fit=Math.min(r.width/scale/i.naturalWidth,r.height/scale/i.naturalHeight);
    const h=i.naturalHeight*fit*scale,w=i.naturalWidth*fit*scale;
    const top=r.y+r.height/2-h/2,left=r.x+r.width/2-w/2;
    return {transform:s.transform,scale,fit:s.objectFit,frame:f.toJSON(),painted:{top,left,width:w,height:h},
      clippedTop:Math.max(0,f.top-top),clippedBottom:Math.max(0,top+h-f.bottom),
      clippedLeft:Math.max(0,f.left-left),clippedRight:Math.max(0,left+w-f.right)};}''')
  card.screenshot(path=str(OUT/'catalog-image-hover.png'))
  report['findings']['hover']={'before':before,'hovered':hovered,'edgeClippingReproduced':hovered['clippedTop']>.5 or hovered['clippedBottom']>.5,
    'scope':'Rendered image boundaries clip at the frame; this is not an assertion that every model headstock is cut.'}
  page.goto(BASE+'/guitars',wait_until='networkidle')
  preset=page.get_by_role('button',name='มากกว่า ฿70k',exact=True)
  preset.click();page.wait_for_timeout(250)
  expect(page.locator('.catalog-grid article')).to_have_count(1)
  result=page.locator('.catalog-grid article')
  report['findings']['over70k']={'requestedPreset':'มากกว่า ฿70k','url':page.url,'modelCount':result.count(),
    'resultText':result.inner_text(),'wrongPriceReproduced':result.get_attribute('data-guitar-id')==ID and '฿34,000' in result.inner_text(),
    'expected':'No verified-price guitar above70000 exists; do not return34000 as matching the requested threshold.'}
  page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(OUT/'catalog-over70k-wrong-result.png'),animations='disabled')
  page.goto(BASE+'/compare?ids='+ID+',yamaha-fg800',wait_until='networkidle')
  report['findings']['compareText']=page.locator('[class*="text-bone/45"],[class*="text-mute/60"]').evaluate_all('''es=>es.slice(0,8).map(e=>({text:e.textContent.trim(),color:getComputedStyle(e).color,fontSize:getComputedStyle(e).fontSize,background:getComputedStyle(e).backgroundColor}))''')
  report['findings']['runtimeData']=page.evaluate('''async()=>{const m=await import('/src/data/guitars.js');const counts={};m.GUITARS.forEach(g=>counts[g.brand]=(counts[g.brand]||0)+1);
    const g=m.GUITARS_BY_ID['yamaha-pacifica-612viifm'];return {models:m.GUITARS.length,brands:counts,uniqueIds:new Set(m.GUITARS.map(g=>g.id)).size,
    everyDetailResolves:m.GUITARS.every(g=>m.SAVED_GUITARS_BY_ID[g.id]?.id===g.id),pacificaGallery:g.gallery.length,pacificaPrice:g.price,pacificaStoredColors:g.colors.length};}''')
  report['findings']['fixedLayers']=[]
  for width,height in [(390,844),(768,1024),(320,740)]:
   page.set_viewport_size({'width':width,'height':height})
   page.goto(BASE+'/guitars/'+ID,wait_until='networkidle');page.evaluate('window.scrollTo(0,1800)');page.wait_for_timeout(600)
   areas=page.evaluate('''()=>[...document.querySelectorAll('body *')].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.position==='fixed'&&s.visibility!=='hidden'&&parseFloat(s.opacity)>.01&&r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight}).map(e=>({tag:e.tagName,className:e.className,rect:e.getBoundingClientRect().toJSON()}))''')
   report['findings']['fixedLayers'].append({'width':width,'height':height,'areas':areas})
  browser.close()
 report['screenshots']=['catalog-image-before-hover.png','catalog-image-hover.png','catalog-over70k-wrong-result.png']
 report['completed']=True
except Exception:
 report['completed']=False;report['errors'].append(traceback.format_exc());print(report['errors'][-1],flush=True)
finally:(OUT/'findings.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'completed':report['completed'],'over70k':report['findings'].get('over70k',{}).get('wrongPriceReproduced'),'hoverClipping':report['findings'].get('hover',{}).get('edgeClippingReproduced')}),flush=True)
raise SystemExit(0 if report['completed'] else 1)
