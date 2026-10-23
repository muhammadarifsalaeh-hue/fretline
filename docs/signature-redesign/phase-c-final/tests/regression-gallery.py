'''Regression checks for the shipped Pacifica gallery, not the private preview.

FRETLINE_QA_URL=http://127.0.0.1:5203 FRETLINE_QA_RUN=production python docs/signature-redesign/phase-c-final/tests/regression-gallery.py
Uses the existing external Playwright/Chromium installation, no app dependencies.
'''
from pathlib import Path
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, expect
import hashlib, json, os, re, traceback

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(os.environ.get('FRETLINE_QA_OUTPUT_DIR', str(ROOT / 'docs/signature-redesign/phase-c-final'))) / 'regression'
SHOTS = OUT / 'screenshots'
SHOTS.mkdir(parents=True, exist_ok=True)
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:5203')
RUN = os.environ.get('FRETLINE_QA_RUN', 'phase-c-final')
ID = 'yamaha-pacifica-612viifm'
sources = {i['id']: i for i in json.loads((ROOT / 'src/data/catalog/projectArtwork.json').read_text())[ID]['images']}
report = {'mode': RUN, 'url': BASE, 'browser': 'Chromium on Linux; physical Safari/iPad not tested',
          'checks': [], 'consoleErrors': [], 'runtimeErrors': [], 'failedRequests': [], 'screenshots': []}

def check(name, condition=True):
    report['checks'].append({'name': name, 'passed': bool(condition)})
    print(('PASS ' if condition else 'FAIL ') + name, flush=True)
    assert condition, name

def no_overflow(page, label):
    check(label + ' has no page horizontal overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))

def image_is(page, color, parent='.gallery-main'):
    image = page.locator(parent).locator('img').first
    expect(image).to_be_visible()
    image.evaluate('(i) => i.decode()')
    measured = image.evaluate('(i)=>({w:i.naturalWidth,h:i.naturalHeight,fit:getComputedStyle(i).objectFit,src:i.getAttribute("src")})')
    original = sources[color]
    check(parent + ' displays ' + color + ' uncropped', measured['w'] == original['width']
          and measured['h'] == original['height'] and measured['fit'] == 'contain'
          and original['file'].rsplit('.', 1)[0] in measured['src'])
    return measured['src']

def shot(page, name):
    if RUN != 'production': return
    page.evaluate('document.activeElement?.blur(); window.scrollTo(0,0)')
    page.screenshot(path=str(SHOTS / name), full_page=True, animations='disabled')
    report['screenshots'].append(name)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 1440, 'height': 1100}, reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda e: report['runtimeErrors'].append(str(e)))
        page.on('console', lambda m: report['consoleErrors'].append(m.text) if m.type == 'error' else None)
        page.on('requestfailed', lambda r: report['failedRequests'].append({'url': r.url, 'failure': r.failure}))
        page.goto(BASE + '/guitars?q=612VIIFM', wait_until='networkidle')
        card = page.locator('article[data-guitar-id="' + ID + '"]')
        expect(card).to_have_count(1)
        expect(page.locator('.catalog-grid article')).to_have_count(1)
        expect(card).to_contain_text('฿34,000')
        black_src = image_is(page, 'black', '.catalog-card-image')
        check('Catalog contains one original model and three color dots', card.locator('[data-gallery-color-indicators] li').count() == 3)
        check('Catalog shows no AI badge', not re.search(r'\bAI\b|AI Edited|AI Generated', card.inner_text()))
        check('Catalog image is lazy loaded', card.locator('img').get_attribute('loading') == 'lazy')
        no_overflow(page, 'Catalog desktop'); shot(page, 'catalog-desktop.png')

        page.goto(BASE + '/guitars/' + ID, wait_until='networkidle')
        expect(page.locator('.detail-summary h1')).to_have_text('Pacifica 612VIIFM')
        expect(page.locator('.gallery-thumbnails button')).to_have_count(4)
        expect(page.get_by_role('radio', name='Black', exact=True)).to_be_checked()
        check('Detail defaults to the same black image as Catalog', image_is(page, 'black') == black_src)
        check('Normal website needs no local file picker', page.locator('input[type="file"]').count() == 0)
        expect(page.locator('.detail-price-block')).to_contain_text('฿34,000')
        expect(page.locator('.detail-price-block')).to_contain_text('ราคาขายปลีกแนะนำโดย Yamaha ประเทศไทย')
        check('Main gallery has no AI badge', not re.search(r'\bAI\b', page.locator('.gallery-main').inner_text()))
        shot(page, 'detail-black-desktop.png')
        page.evaluate('window.__gallerySentinel = "same-document"')
        urls = {'black': black_src}
        for label, color in [('Red', 'red'), ('Blue / Teal', 'blue-teal'), ('Black', 'black')]:
            radio = page.get_by_role('radio', name=label, exact=True)
            radio.click(); expect(radio).to_be_checked()
            expect(radio).to_have_css('border-top-color', 'rgb(200, 161, 90)')
            expect(page.locator('[data-gallery-selection]')).to_have_text(label)
            expect(page.locator('[data-color-name]')).to_have_text(label)
            urls[color] = image_is(page, color)
            shot(page, 'detail-' + color + '-desktop.png')
        check('Color changes do not reload', page.evaluate('window.__gallerySentinel') == 'same-document')
        check('Each color has its own asset', len(set(urls.values())) == 3)
        page.locator('.gallery-thumbnails button').nth(1).click()
        expect(page.get_by_role('radio', name='Red', exact=True)).to_be_checked(); image_is(page, 'red')
        page.locator('.gallery-thumbnails button').nth(3).click()
        urls['all-colors'] = image_is(page, 'all-colors')
        check('Overview is a fourth gallery entry, not a fourth color/model', page.get_by_role('radio').count() == 3
              and page.get_by_role('radio', checked=True).count() == 0)
        shot(page, 'gallery-overview-desktop.png')
        page.get_by_role('button', name='เปิดดูรูปขนาดใหญ่', exact=True).click()
        dialog = page.get_by_role('dialog'); expect(dialog).to_be_visible()
        image_is(page, 'all-colors', '[role="dialog"] > div:nth-child(2)')
        page.keyboard.press('ArrowRight'); image_is(page, 'black', '[role="dialog"] > div:nth-child(2)')
        page.keyboard.press('ArrowRight'); image_is(page, 'red', '[role="dialog"] > div:nth-child(2)')
        shot(page, 'lightbox-desktop.png')
        page.keyboard.press('Escape'); expect(dialog).to_have_count(0)
        expect(page.get_by_role('radio', name='Red', exact=True)).to_be_checked()
        page.get_by_role('radio', name='Red', exact=True).focus(); page.keyboard.press('ArrowRight')
        expect(page.get_by_role('radio', name='Blue / Teal', exact=True)).to_be_focused(); image_is(page, 'blue-teal')
        page.keyboard.press('Home'); image_is(page, 'black')
        check('Keyboard, thumbnail and lightbox selections share one state')
        for color, src in urls.items():
            response = context.request.get(urljoin(BASE, src))
            check(color + ' ships the unchanged original JPEG', response.status == 200
                  and hashlib.sha256(response.body()).hexdigest() == sources[color]['sha256'])
        page.get_by_role('tab').nth(1).click()
        expect(page.locator('[role="tabpanel"]:not([hidden])')).to_contain_text('Gloss Polyurethane')
        expect(page.locator('[role="tabpanel"]:not([hidden])')).to_contain_text('Seymour Duncan SSL-1')
        check('Existing detailed specifications remain available')
        page.locator('.detail-actions button').nth(1).click()
        page.locator('.detail-actions button').nth(0).click()
        page.goto(BASE + '/wishlist', wait_until='networkidle')
        expect(page.locator('.wishlist-row')).to_have_count(1)
        expect(page.locator('.wishlist-row')).to_contain_text('฿34,000'); image_is(page, 'black', '.wishlist-image')
        check('Wishlist stores exactly the original ID', page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))') == [ID])
        page.reload(wait_until='networkidle'); expect(page.locator('.wishlist-row')).to_have_count(1)
        page.goto(BASE + '/compare?ids=' + ID + ',yamaha-fg800', wait_until='networkidle')
        expect(page.get_by_role('table')).to_contain_text('Gloss Polyurethane')
        check('Compare resolves the black asset', page.locator('.compare-table-scroll img[src*="01-black"]').count() == 1)
        page.goto(BASE + '/', wait_until='networkidle')
        check('Homepage reuses the same model image', page.locator('article[data-guitar-id="' + ID + '"] img[src*="01-black"]').count() == 1)
        page.goto(BASE + '/brands/yamaha', wait_until='networkidle')
        check('Yamaha still has exactly twenty cards', page.locator('.brand-models-section article[data-guitar-id]').count() == 20)
        page.goto(BASE + '/find-my-guitar?type=electric&level=intermediate&style=rock&budget=high&priority=versatile', wait_until='networkidle')
        expect(page.locator('.quiz-results-page')).to_be_visible()
        check('Quiz results reuse the same Pacifica asset', page.locator('.quiz-results-page img[src*="01-black"]').count() == 1)

        for width, height, label in [(1024,768,'tablet-landscape'), (768,1024,'tablet'), (390,844,'mobile'), (320,740,'small-mobile')]:
            page.set_viewport_size({'width':width,'height':height})
            page.goto(BASE + '/guitars/' + ID, wait_until='networkidle')
            image_is(page, 'black'); no_overflow(page, 'Detail ' + label)
            if width in [768,390]: shot(page, 'detail-black-' + label + '.png')
            for color_name, color in [('Red','red'),('Blue / Teal','blue-teal'),('Black','black')]:
                page.get_by_role('radio', name=color_name, exact=True).click(); image_is(page, color)
                if width == 390 and color != 'black': shot(page, 'detail-' + color + '-mobile.png')
            page.locator('.gallery-thumbnails button').nth(3).click(); image_is(page,'all-colors')
            no_overflow(page, 'Overview ' + label)
            page.goto(BASE + '/guitars?q=612VIIFM', wait_until='networkidle')
            image_is(page, 'black', '.catalog-card-image'); no_overflow(page, 'Catalog ' + label)
            if width in [768,390]: shot(page, 'catalog-' + label + '.png')
        page.goto(BASE + '/guitars/' + ID, wait_until='networkidle')
        page.reload(wait_until='networkidle'); image_is(page,'black')
        page.goto(BASE + '/guitars?q=612VIIFM', wait_until='networkidle')
        page.go_back(wait_until='networkidle'); image_is(page,'black')
        page.go_forward(wait_until='networkidle'); expect(page.locator('.catalog-grid article')).to_have_count(1)
        check('Refresh and Browser Back/Forward retain working gallery routes')
        page.goto(BASE + '/guitars/yamaha-fg820-12', wait_until='networkidle')
        check('Existing licensed gallery is unchanged', page.locator('.gallery-main img').count() == 1
              and page.get_by_role('radio').count() == 0)
        page.get_by_role('button', name='เปิดดูรูปขนาดใหญ่', exact=True).click()
        expect(page.get_by_role('dialog')).to_be_visible(); page.keyboard.press('Escape')
        page.goto(BASE + '/guitars/yamaha-fg800', wait_until='networkidle')
        check('A model without images keeps its placeholder', page.locator('.gallery-main img').count() == 0)
        touch = browser.new_context(viewport={'width':768,'height':1024},has_touch=True,is_mobile=True,reduced_motion='reduce')
        tp = touch.new_page(); tp.goto(BASE + '/guitars/' + ID, wait_until='networkidle')
        tp.get_by_role('radio', name='Red', exact=True).tap(); image_is(tp,'red')
        tp.locator('.gallery-main').evaluate('''e=>{
          const i={identifier:0,target:e,clientY:100};
          e.dispatchEvent(new TouchEvent('touchstart',{bubbles:true,touches:[new Touch({...i,clientX:250})]}));
          e.dispatchEvent(new TouchEvent('touchend',{bubbles:true,changedTouches:[new Touch({...i,clientX:100})]}));
        }''')
        image_is(tp,'blue-teal'); check('Touch tap and swipe synchronize color')
        touch.close()
        check('No console errors, runtime errors or failed requests', not report['consoleErrors'] and not report['runtimeErrors'] and not report['failedRequests'])
        browser.close()
    report['passed'] = True
except Exception:
    report['passed'] = False; report['failure'] = traceback.format_exc(); print(report['failure'], flush=True)
finally:
    (OUT / ('browser-' + RUN + '.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2) + '\n')
raise SystemExit(0 if report['passed'] else 1)
