from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import json,os,traceback
OUTPUT=Path(__file__).resolve().parent
BASE=os.environ.get('FRETLINE_DEV_URL','http://127.0.0.1:5173')
report={'checks':[],'fixture_note':'Only runtime in-memory SVG test patterns; no product images or catalog records added to source.','page_errors':[]}
def check(name,value=True):
 report['checks'].append({'name':name,'passed':bool(value)});print(name,bool(value),flush=True);assert value,name
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN','/usr/bin/chromium'),args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':1000})
  page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
  page.goto(BASE,wait_until='networkidle')
  page.evaluate('''async () => {
    const data = await import('/src/data/guitars.js');
    const guitar = data.GUITARS_BY_ID['yamaha-fg830'];
    guitar.gallery = ['front','back','headstock'].map((label,index)=>({
      src:'data:image/svg+xml,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="320" height="480"><rect width="320" height="480" fill="${['#395c46','#374e6d','#6b453d'][index]}"/><text x="30" y="240" fill="white">QA ${label} TEST ONLY</text></svg>`),
      label:'QA '+label, credit:'Synthetic QA fixture; not a product photograph'
    }));
    window.history.pushState({},'', '/guitars/yamaha-fg830');
    window.dispatchEvent(new PopStateEvent('popstate'));
  }''')
  expect(page.locator('.gallery-thumbnails button')).to_have_count(3)
  check('Gallery exposes actual supplied thumbnail count')
  page.get_by_role('button',name='ดู QA back',exact=True).click()
  check('Thumbnail changes main image','QA back' in page.locator('.gallery-main img').get_attribute('alt'))
  check('Only active full-size image mounted',page.locator('.gallery-main img').count()==1)
  page.get_by_role('button',name='เปิดดูรูปขนาดใหญ่',exact=True).click()
  dialog=page.get_by_role('dialog');expect(dialog).to_be_visible();check('Lightbox opens')
  page.keyboard.press('ArrowRight');check('Lightbox keyboard next','QA headstock' in dialog.locator('img').first.get_attribute('alt'))
  page.keyboard.press('ArrowLeft');check('Lightbox keyboard previous','QA back' in dialog.locator('img').first.get_attribute('alt'))
  dialog.locator('button').last.focus();page.keyboard.press('Tab')
  expect(dialog.locator('button').first).to_be_focused();check('Lightbox traps Tab')
  page.keyboard.press('Escape');expect(dialog).not_to_be_visible()
  expect(page.get_by_role('button',name='เปิดดูรูปขนาดใหญ่',exact=True)).to_be_focused();check('Escape restores gallery opener')
  page.set_viewport_size({'width':390,'height':844})
  page.locator('.gallery-main').evaluate("(element)=>{const event=new Event('touchstart',{bubbles:true});Object.defineProperty(event,'touches',{value:[{clientX:300}]});element.dispatchEvent(event)}")
  page.locator('.gallery-main').evaluate("(element)=>{const event=new Event('touchend',{bubbles:true});Object.defineProperty(event,'changedTouches',{value:[{clientX:100}]});element.dispatchEvent(event)}")
  check('Mobile swipe advances image','QA headstock' in page.locator('.gallery-main img').get_attribute('alt'))
  page.get_by_role('button',name='ดู QA front',exact=True).click()
  check('Mobile thumbnail navigation retained','QA front' in page.locator('.gallery-main img').get_attribute('alt'))
  page.route('**/qa-missing.png',lambda route:route.fulfill(status=404,body='missing'))
  page.evaluate("async () => {const data=await import('/src/data/guitars.js');data.GUITARS_BY_ID['yamaha-fg830'].gallery[2].src='/qa-missing.png'}")
  page.get_by_role('button',name='ดู QA headstock',exact=True).click()
  expect(page.locator('.gallery-main .image-placeholder')).to_be_visible();check('Broken photo falls back to labelled placeholder')
  page.get_by_role('button',name='ดู QA front',exact=True).click()
  expect(page.locator('.gallery-main img')).to_be_visible();check('Valid image recovers after a broken source')
  check('Gallery fixture has no runtime errors',not report['page_errors'])
  browser.close()
 report['passed']=True
except Exception:
 report['passed']=False;report['failure']=traceback.format_exc();print(report['failure'],flush=True)
finally:
 (OUTPUT/'gallery-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
