"""Exercise the local-only four-image gallery. No application dependencies added.

FRETLINE_QA_URL=http://127.0.0.1:5173 python docs/qa-pacifica-multicolor/browser-gallery.py
Screenshots containing permission-pending illustrations stay Git-ignored.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import hashlib, json, math, os, re, traceback

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '.local-preview/multicolor'
SHOTS = OUT / 'screenshots'
SHOTS.mkdir(parents=True, exist_ok=True)
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:5173')
ID = 'yamaha-pacifica-612viifm'
intake = json.loads((ROOT / 'docs/qa-pacifica-multicolor/image-intake.json').read_text())['images']
sources = {i['id']: i for i in intake}
report = {'browser':'Chromium on Linux; no physical iPad or Safari', 'checks':[], 'screenshots':[],
          'runtimeErrors':[], 'consoleErrors':[], 'failedRequests':[]}

def check(name, condition=True):
    report['checks'].append({'name':name,'passed':bool(condition)})
    print(('PASS ' if condition else 'FAIL ') + name, flush=True)
    assert condition, name

def image_is(page, color, parent='.gallery-main'):
    container = page.locator(parent + ' [data-development-image-preview]')
    expect(container).to_have_attribute('data-preview-image', color)
    image = container.locator('img')
    image.evaluate('(i) => i.decode()')
    measured = image.evaluate('''i=>({w:i.naturalWidth,h:i.naturalHeight,fit:getComputedStyle(i).objectFit,
      rect:i.getBoundingClientRect().toJSON(),parent:i.parentElement.getBoundingClientRect().toJSON()})''')
    check(parent + ' shows ' + color + ' at its original aspect ratio without cropping',
          measured['w'] == sources[color]['width'] and measured['h'] == sources[color]['height']
          and measured['fit'] == 'contain' and measured['rect']['width'] > 0 and measured['rect']['height'] > 0
          and measured['rect']['height'] <= measured['parent']['height'] + 1)
    check(parent + ' has no image badge or text overlay', container.inner_text().strip() == '')
    return image.get_attribute('src')

def shot(page, name):
    page.evaluate('document.activeElement?.blur(); window.scrollTo(0,0)')
    page.screenshot(path=str(SHOTS / name), full_page=True, animations='disabled')
    report['screenshots'].append(name)

def hero_shot(page, name):
    # Capture at scroll zero so fixed navigation stays at the top of tall shots.
    page.evaluate('document.activeElement?.blur(); window.scrollTo(0,0)')
    rect = page.locator('.detail-hero').bounding_box()
    page.screenshot(path=str(SHOTS / name), full_page=True, animations='disabled',
                    clip={'x':0,'y':0,'width':page.viewport_size['width'],'height':math.ceil(rect['y']+rect['height'])})
    report['screenshots'].append(name)

def no_overflow(page, label):
    check(label + ' has no page-level horizontal overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        context = browser.new_context(viewport={'width':1440,'height':1100}, reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda e:report['runtimeErrors'].append(str(e)))
        page.on('console', lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
        page.on('requestfailed', lambda r:report['failedRequests'].append({'url':r.url,'failure':r.failure}))
        page.goto(BASE + '/guitars?q=612VIIFM', wait_until='networkidle')
        card = page.locator('article[data-guitar-id="' + ID + '"]')
        expect(card).to_have_count(1)
        expect(page.locator('.catalog-grid article')).to_have_count(1)
        expect(card).to_contain_text('฿34,000')
        black_src = image_is(page, 'black', '.catalog-card-image')
        check('Catalog has three descriptive dots and one guitar card', card.locator('[data-preview-color-indicators] li').count() == 3)
        check('Catalog has no visible AI label', not re.search(r'\bAI\b|AI Edited|AI Generated', card.inner_text()))
        check('Catalog image keeps lazy loading', card.locator('img').get_attribute('loading') == 'lazy')
        no_overflow(page, 'Catalog desktop')
        shot(page, 'catalog-desktop.png')

        page.goto(BASE + '/guitars/' + ID, wait_until='networkidle')
        expect(page.locator('.detail-summary h1')).to_have_text('Pacifica 612VIIFM')
        check('Initial Detail image is the same black image as Catalog', image_is(page, 'black') == black_src)
        expect(page.get_by_role('radio', name='Black', exact=True)).to_be_checked()
        expect(page.locator('.gallery-thumbnails button')).to_have_count(4)
        expect(page.locator('.detail-price-block')).to_contain_text('ราคาขายปลีกแนะนำโดย Yamaha ประเทศไทย')
        expect(page.locator('.detail-price-block')).to_contain_text('฿34,000')
        check('No visible AI decoration in the main image', 'AI' not in page.locator('.gallery-main').inner_text())
        no_overflow(page, 'Detail desktop')
        hero_shot(page, 'detail-black-desktop.png')
        urls = {'black':black_src}
        navigations = []
        page.on('framenavigated', lambda frame:navigations.append(frame.url) if frame==page.main_frame else None)
        page.evaluate('window.__galleryNavigationSentinel = "same-document"')
        before_url = page.url
        for label,color in [('Red','red'),('Blue / Teal','blue-teal'),('Black','black')]:
            radio = page.get_by_role('radio', name=label, exact=True)
            radio.click()
            expect(radio).to_be_checked()
            expect(page.locator('.preview-color-selector [data-color-name]')).to_have_text(label)
            expect(page.locator('[data-preview-selection]')).to_have_text(label)
            expect(radio).to_have_css('border-top-color', 'rgb(200, 161, 90)')
            check(label + ' uses the gold selected border', True)
            urls[color] = image_is(page, color)
            hero_shot(page, 'detail-' + color + '-desktop.png')
        check('Color changes do not reload or navigate the page', not navigations and page.url==before_url
              and page.evaluate('window.__galleryNavigationSentinel')=='same-document')
        check('Each single color has a different file', len(set(urls.values())) == 3)

        # Thumbnail -> radio and radio -> thumbnail share a single selection.
        page.locator('.gallery-thumbnails button').nth(1).click()
        image_is(page, 'red')
        expect(page.get_by_role('radio', name='Red', exact=True)).to_be_checked()
        page.locator('.gallery-thumbnails button').nth(3).click()
        urls['all-colors'] = image_is(page, 'all-colors')
        expect(page.locator('[data-preview-selection]')).to_have_text('ภาพรวม 3 สี')
        check('Overview is separate from the three color choices', page.get_by_role('radio').count()==3
              and page.get_by_role('radio', checked=True).count()==0)
        hero_shot(page, 'gallery-overview-desktop.png')

        page.get_by_role('button', name='เปิดดูรูปขนาดใหญ่', exact=True).click()
        dialog = page.get_by_role('dialog')
        expect(dialog).to_be_visible()
        image_is(page, 'all-colors', '[role="dialog"] > div:nth-child(2)')
        page.keyboard.press('ArrowRight')
        image_is(page, 'black', '[role="dialog"] > div:nth-child(2)')
        page.keyboard.press('ArrowRight')
        image_is(page, 'red', '[role="dialog"] > div:nth-child(2)')
        shot(page, 'lightbox-desktop.png')
        page.keyboard.press('Escape')
        expect(dialog).to_have_count(0)
        expect(page.get_by_role('radio', name='Red', exact=True)).to_be_checked()
        check('Lightbox selection updates the thumbnail and color', page.locator('.gallery-thumbnails button[aria-current="true"]').get_attribute('aria-label').endswith('Red'))

        # Roving radio focus and selected state work without a mouse.
        radio = page.get_by_role('radio', name='Red', exact=True)
        radio.focus(); page.keyboard.press('ArrowRight')
        expect(page.get_by_role('radio', name='Blue / Teal', exact=True)).to_be_focused()
        image_is(page, 'blue-teal')
        page.keyboard.press('Home')
        expect(page.get_by_role('radio', name='Black', exact=True)).to_be_checked()
        image_is(page, 'black')
        check('Keyboard radio navigation stays in sync with the main image')

        for key,src in urls.items():
            response = context.request.get(BASE + src)
            check(key + ' is the unchanged original JPEG with no-store/noindex',
                  response.status==200 and response.headers.get('content-type')=='image/jpeg'
                  and hashlib.sha256(response.body()).hexdigest()==sources[key]['sha256']
                  and response.headers.get('cache-control')=='no-store' and 'noindex' in response.headers.get('x-robots-tag',''))
        private = '/.local-preview/' + ID + '/01-black.jpg'
        check('Private asset directory is not directly readable', context.request.get(BASE + private).status in [403,404])
        check('Another guitar cannot claim this image endpoint', context.request.get(BASE + black_src.replace(ID,'yamaha-fg800')).status==404)

        page.locator('.detail-actions button').nth(1).click()
        page.locator('.detail-actions button').nth(0).click()
        page.goto(BASE + '/wishlist', wait_until='networkidle')
        expect(page.locator('.wishlist-row')).to_have_count(1)
        expect(page.locator('.wishlist-row')).to_contain_text('฿34,000')
        image_is(page, 'black', '.wishlist-image')
        check('Wishlist stores one original guitar ID, not color variants', page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))')==[ID])
        page.reload(wait_until='networkidle')
        expect(page.locator('.wishlist-row')).to_have_count(1)
        page.goto(BASE + '/compare?ids=' + ID + ',yamaha-fg800', wait_until='networkidle')
        expect(page.get_by_role('table')).to_contain_text('Gloss Polyurethane')
        check('Compare retains model data and the black presentation image', page.locator('.compare-table-scroll [data-preview-image="black"]').count()==1)

        for width,height,label in [(1024,768,'tablet-landscape'),(768,1024,'tablet-portrait'),(390,844,'mobile'),(320,740,'small-mobile')]:
            page.set_viewport_size({'width':width,'height':height})
            page.evaluate('localStorage.setItem("fretline:compare", "[]")')
            page.goto(BASE + '/guitars/' + ID, wait_until='networkidle')
            image_is(page, 'black'); no_overflow(page, 'Detail ' + label)
            if label=='mobile': hero_shot(page,'detail-black-mobile.png')
            for color_name,color in [('Red','red'),('Blue / Teal','blue-teal'),('Black','black')]:
                page.get_by_role('radio', name=color_name, exact=True).click()
                image_is(page, color)
                if label=='mobile' and color!='black': hero_shot(page,'detail-' + color + '-mobile.png')
            page.locator('.gallery-thumbnails button').nth(3).click()
            image_is(page, 'all-colors'); no_overflow(page, 'Overview ' + label)
            if label=='mobile': hero_shot(page,'gallery-overview-mobile.png')
            page.goto(BASE + '/guitars?q=612VIIFM', wait_until='networkidle')
            image_is(page, 'black', '.catalog-card-image'); no_overflow(page, 'Catalog ' + label)
            if label=='mobile': shot(page,'catalog-mobile.png')

        # Touch behavior on an iPad-sized viewport uses the same controls/state.
        touch_context = browser.new_context(viewport={'width':768,'height':1024}, has_touch=True, is_mobile=True, reduced_motion='reduce')
        touch = touch_context.new_page()
        touch.goto(BASE + '/guitars/' + ID, wait_until='networkidle')
        touch.get_by_role('radio', name='Red', exact=True).tap(); image_is(touch,'red')
        gallery = touch.locator('.gallery-main')
        gallery.evaluate('''e=>{
          const init={identifier:0,target:e,clientY:100};
          e.dispatchEvent(new TouchEvent('touchstart',{bubbles:true,touches:[new Touch({...init,clientX:250})]}));
          e.dispatchEvent(new TouchEvent('touchend',{bubbles:true,changedTouches:[new Touch({...init,clientX:100})]}));
        }''')
        image_is(touch,'blue-teal')
        check('Touch tap and gallery swipe synchronize the selected color')
        touch_context.close()

        page.goto(BASE + '/guitars/yamaha-fg820-12', wait_until='networkidle')
        check('Existing licensed Yamaha photo and its gallery remain unchanged', page.locator('.gallery-main img').count()==1
              and page.locator('[data-development-image-preview]').count()==0 and page.locator('.preview-color-selector').count()==0)
        page.get_by_role('button', name='เปิดดูรูปขนาดใหญ่', exact=True).click()
        expect(page.get_by_role('dialog')).to_be_visible()
        page.keyboard.press('Escape')
        check('Existing licensed-photo lightbox still opens and closes')
        check('No console/runtime or failed-request errors in normal flows', not report['runtimeErrors'] and not report['consoleErrors'] and not report['failedRequests'])
        browser.close()
    report['passed'] = True
except Exception:
    report['passed'] = False
    report['failure'] = traceback.format_exc()
    print(report['failure'], flush=True)
finally:
    (OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
