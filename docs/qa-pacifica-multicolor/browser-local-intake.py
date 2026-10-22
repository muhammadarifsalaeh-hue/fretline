"""Simulate Codespaces: select original JPEGs locally, without sending an upload."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json, traceback

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'.local-preview/multicolor'
ID = 'yamaha-pacifica-612viifm'
result = {'checks':[], 'runtimeErrors':[], 'consoleErrors':[], 'uploads':[]}

def check(name, condition):
    result['checks'].append({'name':name,'passed':bool(condition)})
    print(('PASS ' if condition else 'FAIL ')+name,flush=True)
    assert condition,name

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
        page.on('pageerror',lambda e:result['runtimeErrors'].append(str(e)))
        page.on('console',lambda m:result['consoleErrors'].append(m.text) if m.type=='error' else None)
        page.on('request',lambda req:result['uploads'].append(req.url) if req.method in ['POST','PUT','PATCH'] else None)
        page.goto('http://127.0.0.1:5174/guitars/'+ID,wait_until='networkidle')
        picker = page.locator('[data-local-preview-picker]')
        expect(picker).to_be_visible()
        expect(page.locator('.gallery-main .image-placeholder')).to_be_visible()
        expect(picker.get_by_role('button',name='แสดงภาพทั้ง 4',exact=True)).to_be_disabled()
        check('Fresh Codespace displays the private image picker without failing to start',True)
        check('Picker fits 390px without horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        files=['01-black.jpg','02-red.jpg','03-blue-teal.jpg','04-all-colors.jpg']
        for index,file in enumerate(files):picker.locator('input[type="file"]').nth(index).set_input_files(ROOT/'.local-preview'/ID/file)
        picker.get_by_role('button',name='แสดงภาพทั้ง 4',exact=True).click()
        expect(page.locator('.gallery-main [data-preview-image="black"]')).to_be_visible()
        expect(page.locator('.gallery-thumbnails button')).to_have_count(4)
        src=page.locator('.gallery-main img').get_attribute('src')
        check('Original JPEGs become browser-local blob URLs',src.startswith('blob:'))
        for name,color in [('Red','red'),('Blue / Teal','blue-teal'),('Black','black')]:
            page.get_by_role('radio',name=name,exact=True).click()
            expect(page.locator('.gallery-main [data-preview-image="'+color+'"]')).to_be_visible()
        check('All three browser-local colors remain interactive',True)
        # Use SPA navigation; a full reload intentionally clears local images.
        page.locator('.discovery-breadcrumb a[href="/guitars"]').click()
        card=page.locator('article[data-guitar-id="'+ID+'"]')
        expect(card.locator('[data-preview-image="black"]')).to_have_count(1)
        check('Browser images work across Catalog navigation without adding a variant',True)
        card.locator('h3 a').click()
        page.locator('.detail-actions button').nth(1).click()
        page.locator('a[href="/wishlist"]').first.click()
        expect(page.locator('.wishlist-row [data-preview-image="black"]')).to_have_count(1)
        check('Wishlist uses the same browser-local image and original ID',True)
        page.locator('.wishlist-row h2 a').click()
        picker=page.locator('[data-local-preview-picker]')
        picker.locator('summary').click()
        picker.get_by_role('button',name='ล้างภาพจากเบราว์เซอร์',exact=True).click()
        expect(page.locator('.gallery-main .image-placeholder')).to_be_visible()
        check('Clear revokes browser images and resets all four file inputs',picker.locator('input[type="file"]').evaluate_all('(els)=>els.every(e=>e.files.length===0)'))
        # Reject invalid file bytes without breaking the app or sending a request.
        for index,file in enumerate(files):picker.locator('input[type="file"]').nth(index).set_input_files(ROOT/'.local-preview'/ID/file)
        picker.locator('input[type="file"]').first.set_input_files({'name':'not-an-image.jpg','mimeType':'image/jpeg','buffer':b'not a jpeg'})
        picker.get_by_role('button',name='แสดงภาพทั้ง 4',exact=True).click()
        expect(picker.get_by_role('alert')).to_be_visible()
        check('Invalid images show an error while the placeholder remains',page.locator('.gallery-main .image-placeholder').count()==1)
        page.reload(wait_until='networkidle')
        expect(page.locator('.gallery-main .image-placeholder')).to_be_visible()
        check('Refreshing does not persist private image data',True)
        check('No image uploads, console or runtime errors occurred',not result['uploads'] and not result['runtimeErrors'] and not result['consoleErrors'])
        page.screenshot(path=str(OUT/'screenshots/codespaces-local-picker-mobile.png'),full_page=True)
        browser.close()
    result['passed']=True
except Exception:
    result['passed']=False;result['failure']=traceback.format_exc();print(result['failure'],flush=True)
finally:(OUT/'local-intake-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if result['passed'] else 1)
