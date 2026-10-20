"""Targeted data migration, Strict Mode, image failure and image sizing checks."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json, os, re, traceback

OUT = Path(__file__).resolve().parent
DEV = os.environ.get('FRETLINE_QA_DEV_URL', 'http://127.0.0.1:5187')
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:4186')
PHOTO = 'yamaha-fg820-12'
B = 'ibanez-sr300e'
C = 'taylor-gs-mini'
D = 'taylor-214ce'
report = {'checks': [], 'normal_errors': [], 'expected_image_failures': [], 'photo_candidates': []}

def check(name, condition=True):
    report['checks'].append({'name': name, 'passed': bool(condition)})
    print(name, bool(condition), flush=True)
    assert condition, name

def saved(page, key):
    return page.evaluate('(key)=>JSON.parse(localStorage.getItem("fretline:"+key)||"[]")', key)

def count(page, key, size):
    page.wait_for_function('({key,size})=>JSON.parse(localStorage.getItem("fretline:"+key)||"[]").length===size', arg={'key': key, 'size': size})

def visit(page, base, path):
    page.goto(base+path, wait_until='networkidle')

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN','/usr/bin/chromium'), args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1280,'height':900})
        page.set_default_timeout(10000)
        page.on('pageerror',lambda error:report['normal_errors'].append(str(error)))
        page.on('console',lambda message:report['normal_errors'].append(message.text) if message.type=='error' else None)
        visit(page, DEV, '/')
        page.evaluate('([a,b])=>{localStorage.setItem("fretline:wishlist",JSON.stringify([a,a,b,"constructor","missing"]));localStorage.setItem("fretline:compare",JSON.stringify([b,b,a,"__proto__","missing"]))}', [PHOTO,B])
        page.reload(wait_until='networkidle')
        count(page,'wishlist',2);count(page,'compare',2)
        check('Existing saved IDs migrate without duplicates or inherited-object IDs',saved(page,'wishlist')==[PHOTO,B] and saved(page,'compare')==[B,PHOTO])
        visit(page, DEV, '/compare?ids='+PHOTO+','+B+','+PHOTO+',constructor,missing')
        count(page,'compare',2)
        check('Strict Mode shared Compare URL reconciles with stored state',saved(page,'compare')==[PHOTO,B])
        page.get_by_role('button',name='เพิ่มกีตาร์',exact=True).click()
        dialog=page.get_by_role('dialog',name='เพิ่มกีตาร์',exact=True)
        search=dialog.get_by_role('searchbox')
        search.fill('GS Mini Mahogany')
        dialog.locator('.picker-model-row').click()
        count(page,'compare',3)
        check('Picker adds a third source-backed model',saved(page,'compare')==[PHOTO,B,C])
        search.fill('214ce')
        dialog.locator('.picker-model-row').click()
        count(page,'compare',4)
        check('Picker adds a fourth model without replacing saved IDs',saved(page,'compare')==[PHOTO,B,C,D])
        search.fill('RG550')
        expect(dialog.locator('.picker-model-row')).to_be_disabled()
        check('Fifth model is disabled and the maximum is explained','เลือกครบ 4 รุ่นแล้ว' in dialog.inner_text())
        page.keyboard.press('Escape')
        expect(dialog).not_to_be_visible()
        expect(page.get_by_role('button',name='ครบ 4 รุ่นแล้ว',exact=True)).to_be_disabled()
        check('Compare header exposes the four-model limit')
        page.locator('.compare-table-scroll').get_by_role('button',name='นำ 214ce Grand Auditorium ออกจากการเปรียบเทียบ',exact=True).click()
        count(page,'compare',3)
        check('Remove frees a comparison slot and preserves favourites',saved(page,'compare')==[PHOTO,B,C] and saved(page,'wishlist')==[PHOTO,B])
        page.go_back(wait_until='networkidle')
        count(page,'compare',4)
        check('Browser Back restores the four-model shared URL',saved(page,'compare')==[PHOTO,B,C,D])
        page.go_forward(wait_until='networkidle')
        count(page,'compare',3)
        check('Browser Forward restores the removal',saved(page,'compare')==[PHOTO,B,C])
        visit(page, DEV, '/guitars/'+PHOTO)
        expect(page.locator('.gallery-main img')).to_be_visible()
        check('Development Vite route renders the licensed model photo')
        visit(page, DEV, '/guitars/constructor')
        check('Inherited guitar route recovers without a crash',page.locator('.detail-summary').count()==0 and page.locator('main h1').count()==1)
        check('Development Strict Mode has no runtime or console errors',not report['normal_errors'])
        page.close()

        # A separate context isolates deliberately aborted image requests from normal QA.
        context=browser.new_context(viewport={'width':390,'height':844})
        broken=context.new_page()
        runtime=[]
        broken.on('pageerror',lambda error:runtime.append(str(error)))
        broken.on('requestfailed',lambda request:report['expected_image_failures'].append({'url':request.url,'failure':request.failure}))
        broken.route('**/*.webp',lambda route:route.abort())
        visit(broken, BASE, '/guitars/'+PHOTO)
        expect(broken.locator('.gallery-main .image-placeholder')).to_be_visible()
        check('A failed real-photo request falls back to the existing labelled placeholder', 'FG820-12' in broken.locator('.gallery-main .image-placeholder').get_attribute('aria-label'))
        check('Intentional image failures do not cause runtime errors',not runtime and len(report['expected_image_failures'])>0)
        context.close()

        # New contexts prevent an earlier larger candidate from being reused from cache.
        for label,width,height in [('mobile',390,844),('tablet',768,1024),('desktop',1440,1100)]:
            context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1)
            image_page=context.new_page()
            visit(image_page,BASE,'/guitars/'+PHOTO)
            image_page.wait_for_function('()=>{const image=document.querySelector(".gallery-main img");return image&&image.complete&&image.naturalWidth>0}')
            meta=image_page.locator('.gallery-main img').evaluate('(image)=>({src:image.currentSrc,sizes:image.sizes,width:image.width,naturalWidth:image.naturalWidth})')
            meta['viewport']=width
            report['photo_candidates'].append(meta)
            check(label+' selects a real responsive photo candidate',bool(re.search(r'01-front(?:-480|-960)?-',meta['src'])))
            if label=='mobile':
                check('Mobile at DPR 1 uses the 480px derivative','01-front-480-' in meta['src'])
                image_page.screenshot(path=str(OUT/'detail-mobile-viewport.png'),animations='disabled')
            context.close()

        english=browser.new_page(viewport={'width':1280,'height':900})
        visit(english,BASE,'/')
        english.evaluate('localStorage.setItem("fretline:lang","en")')
        visit(english,BASE,'/guitars/'+PHOTO)
        check('English fallback keeps unknown prices and source disclosure','Price on request' in english.locator('main').inner_text() and english.locator('html').get_attribute('lang')=='en')
        visit(english,BASE,'/image-credits')
        check('English credit page retains the actual license','CC-BY-SA-4.0' in english.locator('main').inner_text())
        browser.close()

try:
    run()
    report['passed']=True
except Exception:
    report['passed']=False
    report['failure']=traceback.format_exc()
    print(report['failure'],flush=True)
finally:
    (OUT/'browser-edges-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if not report['passed']:raise SystemExit(1)
