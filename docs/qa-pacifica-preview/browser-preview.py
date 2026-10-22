"""Local-only layout QA. Screenshots include an image without publication rights.

Run after starting npm run dev:pacifica-preview on port 5173.
Outputs deliberately stay in the Git-ignored .local-preview directory.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import hashlib, json, re, traceback

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '.local-preview'
SHOTS = OUT / 'screenshots'
SHOTS.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:5173'
MODEL = 'yamaha-pacifica-612viifm'
report = {'browser': 'Chromium on Linux; not physical iPad or Safari', 'checks': [],
          'pageErrors': [], 'consoleErrors': [], 'failedRequests': [], 'screenshots': []}

def check(name, condition=True):
    report['checks'].append({'name': name, 'passed': bool(condition)})
    print(('PASS ' if condition else 'FAIL ') + name, flush=True)
    assert condition, name

def illustration(page, where):
    element = page.locator(where + ' [data-development-image-preview]').first
    expect(element).to_be_visible()
    image = element.locator('img')
    expect(image).to_be_visible()
    image.evaluate('(i) => i.decode()')
    facts = image.evaluate('''i => ({complete:i.complete, width:i.naturalWidth, height:i.naturalHeight,
      fit:getComputedStyle(i).objectFit, box:i.getBoundingClientRect().toJSON(),
      parent:i.parentElement.getBoundingClientRect().toJSON(), alt:i.alt, loading:i.loading})''')
    check(where + ' preserves original 1254×1254 PNG with contain sizing',
          facts['complete'] and facts['width'] == facts['height'] == 1254 and facts['fit'] == 'contain'
          and facts['box']['width'] > 20 and facts['box']['height'] > 20
          and facts['box']['height'] <= facts['parent']['height'] + 1)
    check(where + ' exposes AI/unverified text', 'AI' in facts['alt'] and 'AI' in element.inner_text())
    return image.get_attribute('src')

def no_overflow(page, name):
    check(name + ' has no page-level horizontal overflow',
          page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))

def shot(page, name, full=True):
    page.screenshot(path=str(SHOTS / name), full_page=full, animations='disabled')
    report['screenshots'].append(name)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda e: report['pageErrors'].append(str(e)))
        page.on('console', lambda m: report['consoleErrors'].append(m.text) if m.type == 'error' else None)
        page.on('requestfailed', lambda r: report['failedRequests'].append({'url':r.url,'failure':r.failure}))

        page.goto(BASE + '/guitars?q=612VIIFM', wait_until='networkidle')
        card = page.locator('article[data-guitar-id="' + MODEL + '"]')
        expect(card).to_have_count(1)
        expect(page.locator('.catalog-grid article')).to_have_count(1)
        expect(card).to_contain_text('฿34,000')
        expect(card.locator('.price-source-note')).to_contain_text('Yamaha ประเทศไทย')
        src = illustration(page, '.catalog-card-image')
        check('Catalog image is lazy-loaded', card.locator('img').get_attribute('loading') == 'lazy')
        response = context.request.get(BASE + src)
        original = (OUT / (MODEL + '-preview.png')).read_bytes()
        check('Preview endpoint serves unchanged bytes with no-store and noindex',
              response.status == 200 and hashlib.sha256(response.body()).digest() == hashlib.sha256(original).digest()
              and response.headers.get('cache-control') == 'no-store'
              and 'noindex' in response.headers.get('x-robots-tag', ''))
        for path in ['/.local-preview/' + MODEL + '-preview.png', '/@fs' + str(OUT / (MODEL + '-preview.png'))]:
            blocked = context.request.get(BASE + path)
            check('Direct private-file path is denied: ' + path, blocked.status in [403,404])
        check('Another model cannot use the image endpoint', context.request.get(BASE + src.replace(MODEL, 'yamaha-fg800')).status == 404)
        card.get_by_role('button', name=re.compile('^บันทึก .*ในรายการโปรด')).click()
        card.get_by_role('button', name=re.compile('^เพิ่ม .*ในการเปรียบเทียบ')).click()
        check('Catalog actions save the existing ID once', page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))') == [MODEL]
              and page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))') == [MODEL])

        page.goto(BASE + '/guitars/' + MODEL, wait_until='networkidle')
        expect(page.locator('.detail-summary h1')).to_have_text('Pacifica 612VIIFM')
        expect(page.locator('.detail-price-block')).to_contain_text('฿34,000')
        expect(page.locator('.detail-price-block')).to_contain_text('ไม่ใช่การรับประกันราคาขายของร้านค้า')
        check('Detail and Catalog share the exact development image', illustration(page, '.gallery-main') == src)
        check('Illustration is not presented as a licensed gallery or zoomable product photo',
              page.locator('.gallery-thumbnails').count() == 0 and page.locator('.gallery-main button').count() == 0)
        page.get_by_role('tab').nth(1).click()
        table = page.locator('.spec-table:visible')
        expect(table).to_contain_text('Gloss Polyurethane')
        expect(table).to_contain_text('Seymour Duncan SSL-1 RwRp')
        expect(table).to_contain_text('350 mm')
        expect(table).to_contain_text('648 mm (25.5")')
        expect(table).to_contain_text('Graph Tech TUSQ')
        expect(table).to_contain_text('Grover Locking Tuners')
        check('Specification rows show the manufacturer facts and leave unknown shape unspecified',
              'SP90' not in table.inner_text() and 'Fired Red' not in table.inner_text()
              and 'ไม่ระบุ' in table.locator('tr').filter(has=page.get_by_role('rowheader', name='ทรงบอดี้', exact=True)).inner_text())
        page.get_by_role('tab').nth(2).click()
        expect(page.locator('.review-empty:visible')).to_contain_text('รีวิว')

        page.goto(BASE + '/wishlist', wait_until='networkidle')
        expect(page.locator('.wishlist-row')).to_have_count(1)
        expect(page.locator('.wishlist-row')).to_contain_text('฿34,000')
        check('Wishlist keeps the same model and image', illustration(page, '.wishlist-image') == src)
        page.reload(wait_until='networkidle')
        check('Wishlist survives reload without duplicates', page.locator('.wishlist-row').count() == 1)

        page.goto(BASE + '/compare?ids=' + MODEL + ',yamaha-fg800', wait_until='networkidle')
        comparison = page.get_by_role('table', name='ตารางเปรียบเทียบสเปกกีตาร์')
        expect(comparison).to_contain_text('Gloss Polyurethane')
        expect(comparison).to_contain_text('฿34,000')
        expect(comparison).to_contain_text('ราคาขายปลีกแนะนำ')
        check('Compare shows only the authorized model illustration',
              all(value == MODEL for value in page.locator('[data-development-image-preview]').evaluate_all('(els)=>els.map(e=>e.dataset.developmentImagePreview)')))

        for width, height, label in [(1440,1000,'desktop'), (1024,768,'tablet-landscape'), (768,1024,'tablet-portrait'), (390,844,'mobile'), (320,740,'small-mobile')]:
            page.set_viewport_size({'width':width,'height':height})
            # Keep the illustration review unobscured by the existing Compare tray.
            page.evaluate('localStorage.setItem("fretline:compare", "[]")')
            page.goto(BASE + '/guitars?q=612VIIFM', wait_until='networkidle')
            illustration(page, '.catalog-card-image'); no_overflow(page, 'Catalog ' + label)
            shot(page, 'catalog-' + label + '.png')
            if label in ['desktop','mobile']: shot(page, 'catalog-' + label + '-viewport.png', full=False)
            page.goto(BASE + '/guitars/' + MODEL, wait_until='networkidle')
            illustration(page, '.gallery-main'); no_overflow(page, 'Detail ' + label)
            shot(page, 'detail-' + label + '.png')
            if label in ['desktop','mobile']: shot(page, 'detail-' + label + '-viewport.png', full=False)
            page.get_by_role('tab').nth(1).click()
            no_overflow(page, 'Specs ' + label)
            if label in ['desktop','mobile']: shot(page, 'specs-' + label + '.png')
            page.goto(BASE + '/wishlist', wait_until='networkidle')
            no_overflow(page, 'Wishlist ' + label)
            illustration(page, '.wishlist-image')
            page.goto(BASE + '/compare?ids=' + MODEL + ',yamaha-fg800', wait_until='networkidle')
            no_overflow(page, 'Compare ' + label)
            if label in ['desktop','mobile']: shot(page, 'compare-' + label + '.png')

        page.goto(BASE + '/guitars/yamaha-fg800', wait_until='networkidle')
        check('A different Yamaha retains its placeholder', page.locator('.gallery-main .image-placeholder').count() == 1
              and page.locator('.gallery-main [data-development-image-preview]').count() == 0)
        page.goto(BASE + '/wishlist', wait_until='networkidle')
        page.locator('.wishlist-row').get_by_role('button', name=re.compile('^นำ .*ออกจากรายการ')).click()
        expect(page.locator('.wishlist-row')).to_have_count(0)
        check('Wishlist removal still works', page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))') == [])
        check('No JavaScript, console or request failures in normal flows',
              not report['pageErrors'] and not report['consoleErrors'] and not report['failedRequests'])
        browser.close()
    report['passed'] = True
except Exception:
    report['passed'] = False
    report['failure'] = traceback.format_exc()
    print(report['failure'], flush=True)
finally:
    (OUT / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if report['passed'] else 1)
