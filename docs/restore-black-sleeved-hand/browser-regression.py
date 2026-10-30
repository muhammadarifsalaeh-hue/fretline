"""Production-build regression reused unchanged from the validated image-system release."""
from pathlib import Path
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright, expect
import argparse
import hashlib
import json
import traceback

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--production', default='http://127.0.0.1:4192')
parser.add_argument('--preview', default='http://127.0.0.1:4191')
parser.add_argument('--only-failed-from', type=Path)
args = parser.parse_args()
failed_names = {case['name'] for case in json.loads(args.only_failed_from.read_text())['checks'] if not case['passed']} if args.only_failed_from else None
audit = json.loads((ROOT / 'docs/yamaha-live-release-2026-10-30/tests/data-and-images.json').read_text())
models = [{**g, 'detailsRoute': '/guitars/' + g['id'], 'previewGallery': g['gallery']} for g in audit['modes'][0]['yamaha']]
report = {'checks': [], 'consoleErrors': [], 'runtimeErrors': [], 'imageResponseErrors': [],
          'physicalIPadSafariTested': False, 'engine': 'Chromium', 'databaseWrites': False}


def check(name, fn, page):
    if failed_names is not None and name not in failed_names:
        return
    try:
        report['checks'].append({'name': name, 'passed': True, 'evidence': fn()})
        print('PASS', name, flush=True)
    except Exception:
        (OUT / 'screenshots').mkdir(exist_ok=True)
        page.screenshot(path=str(OUT / 'screenshots' / (name + '-FAIL.png')), animations='disabled')
        report['checks'].append({'name': name, 'passed': False, 'failure': traceback.format_exc()})
        print('FAIL', name, traceback.format_exc(), flush=True)


def go(page, base, route):
    response = page.goto(base + route, wait_until='domcontentloaded')
    assert response.status == 200
    expect(page.locator('main h1')).to_be_visible(timeout=15000)
    page.evaluate('document.fonts.ready')
    return response


def layout(page):
    metrics = page.evaluate('({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
    assert metrics['scrollWidth'] <= metrics['viewport'] + 1, metrics
    return metrics


def detail(page, context, base, mode, model):
    go(page, base, model['detailsRoute'])
    expect(page.locator('.detail-summary h1')).to_have_text(model['name'])
    overview = page.locator('.detail-tab-panel:not([hidden]) p.whitespace-pre-line')
    expect(overview).to_have_text(model['description'])
    expect(page.locator('.detail-price-block')).to_contain_text(
        'สอบถามราคา' if model['priceTHB'] is None else '฿' + format(model['priceTHB'], ','))
    expected = model['gallery'] if mode == 'production' else model['previewGallery']
    thumbs = page.locator('.gallery-thumbnails button')
    assert thumbs.count() == len(expected), (model['id'], thumbs.count(), len(expected))
    seen = []
    for index, image in enumerate(expected):
        thumbs.nth(index).click()
        element = page.locator('.gallery-main img')
        expect(element).to_be_visible()
        element.evaluate('(image)=>image.decode()')
        info = element.evaluate('(image)=>({src:image.src,currentSrc:image.currentSrc,width:image.naturalWidth,height:image.naturalHeight,fit:getComputedStyle(image).objectFit})')
        assert info['width'] > 0 and info['height'] > 0 and info['fit'] == 'contain', info
        response = context.request.get(info['src'])
        assert response.status == 200
        digest = hashlib.sha256(response.body()).hexdigest()
        if image['sha256']:
            assert digest == image['sha256'], (model['id'], image, info)
        else:
            source = ROOT / urlparse(image['src']).path.lstrip('/')
            assert source.is_file(), source
            assert digest == hashlib.sha256(source.read_bytes()).hexdigest()
        if '__fretline_yamaha_import_preview__' in info['src']:
            assert mode == 'preview'
            assert 'noindex' in response.headers['x-robots-tag']
        seen.append({'sha256': digest, 'width': info['width'], 'height': info['height']})
    if not expected:
        expect(page.locator('.gallery-main .image-placeholder')).to_be_visible()
        assert page.locator('.gallery-main img').count() == 0
    if mode == 'preview' and model['id'] in ['yamaha-fg800', 'yamaha-fg820-12']:
        page.get_by_role('button', name='เปิดดูรูปขนาดใหญ่', exact=True).click()
        expect(page.get_by_role('dialog')).to_be_visible()
        page.keyboard.press('Escape')
        expect(page.get_by_role('dialog')).to_have_count(0)
    page.get_by_role('tab', name='สเปก', exact=True).click()
    table = page.locator('.spec-table')
    expect(table).to_be_visible()
    for key in ['body', 'neck', 'fretboard', 'pickups', 'bridge', 'controls', 'top', 'back', 'sides', 'electronics']:
        value = model['specs'].get(key)
        if value is not None:
            expect(table).to_contain_text(str(value))
    return {'id': model['id'], 'descriptionVisible': True, 'specificationsVisible': True, 'images': seen, 'layout': layout(page)}


def catalog(page, base, mode):
    go(page, base, '/guitars?brand=Yamaha')
    expect(page.locator('.catalog-result-count')).to_contain_text('20')
    ids, pictures = [], []
    for index in range(3):
        cards = page.locator('.catalog-grid article[data-guitar-id]')
        expect(cards).to_have_count(9 if index < 2 else 2)
        for card in cards.all():
            gid = card.get_attribute('data-guitar-id')
            ids.append(gid)
            links = card.locator('h3 a')
            assert links.get_attribute('href') == '/guitars/' + gid
            for image in card.locator('img').all():
                image.scroll_into_view_if_needed()
                image.evaluate('(image)=>image.decode()')
                assert image.evaluate('(image)=>image.naturalWidth>0')
                pictures.append(gid)
        if index < 2:
            page.locator('.catalog-pagination').get_by_role('button', name='หน้าถัดไป', exact=True).click()
    assert len(ids) == len(set(ids)) == 20
    assert set(ids) == {model['id'] for model in models}
    assert len(pictures) == 19, pictures
    go(page, base, '/guitars?brand=Yamaha')
    page.locator('#catalog-search').fill('FSX830C')
    expect(page.locator('.catalog-grid article')).to_have_count(1)
    expect(page.locator('article[data-guitar-id="yamaha-fsx830c"]')).to_be_visible()
    return {'ids': ids, 'modelsWithRenderedImages': pictures, 'searchPassed': True, 'layout': layout(page)}


import re
BASE = args.production.rstrip('/')
ROUTES = ['/', '/guitars', '/brands', '/brands/yamaha', '/wishlist', '/compare?ids=yamaha-fg800,yamaha-fsx830c', '/find-my-guitar', '/practice', '/admin', '/qr', '/image-credits', '/guitars/yamaha-pacifica-612viifm', '/missing-route']

def frames(page):
    result = []
    for element in page.locator('main [data-product-image-slot],main .guitar-image-frame').all():
        if element.is_visible():
            result.append(element.evaluate("e=>({w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height,bg:getComputedStyle(e).backgroundColor})"))
    assert all(r['w']>=32 and r['h']>=32 and abs(r['w']-r['h'])<=1.5 and r['bg']=='rgb(0, 0, 0)' for r in result),result
    for img in page.locator('main .guitar-image-frame>img').all():
        assert img.evaluate("(i)=>getComputedStyle(i).objectFit==='contain'&&getComputedStyle(i).padding==='0px'&&getComputedStyle(i).transform==='none'")
        assert img.evaluate("i=>{const a=i.getBoundingClientRect(),b=i.parentElement.getBoundingClientRect();return a.width<=b.width+1&&a.height<=b.height+1&&a.left>=b.left-1&&a.top>=b.top-1&&a.right<=b.right+1&&a.bottom<=b.bottom+1}"), 'Image element overflows its square frame'
    return result

def route_check(page, route):
    go(page, BASE, route)
    page.evaluate('''async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=innerHeight){scrollTo(0,y);await new Promise(r=>requestAnimationFrame(r))}scrollTo(0,0)}''')
    for image in page.locator('main img').all():
        if image.is_visible():
            image.scroll_into_view_if_needed()
            image.evaluate('(image)=>image.decode()')
            assert image.evaluate('(image)=>image.naturalWidth>0')
    assert page.locator('main h1').count() == 1
    assert not page.locator('.site-header a[href="/admin"]').count()
    text = page.locator('main').inner_text()
    assert not re.search(r'AI\s*(Generated|Edited)|Made (?:with|by) AI|Powered by AI|Demo Website|Placeholder Content', text, re.I)
    assert not re.search(r'\b(?:Search|Favorites|Loading|Filter|Sort|Explore by Brand)\b', text)
    if route == '/':
        expect(page.locator('.signature-stats-list dd')).to_have_text(['200', '10', '4', '4'])
        expect(page.locator('[data-marquee-primary] a')).to_have_count(10)
    if route == '/admin':
        expect(page.get_by_role('heading', name='เชื่อมต่อโปรเจกต์ Fretline')).to_be_visible()
        assert page.locator('.fretline-experience').count() == 0
    if route == '/practice':
        expect(page.locator('[data-practice-chord]')).to_have_count(42)
        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status', 'ready', timeout=60000)
        expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status', 'ready', timeout=60000)
    frame_info = frames(page)
    return {'route': route, 'frames': frame_info, 'noBrokenVisibleImages': True, 'thaiUI': True, 'layout': layout(page)}

def compare(page):
    ids = ['yamaha-fg800', 'yamaha-fsx830c', 'yamaha-fg820', 'yamaha-fg830']
    go(page, BASE, '/compare?ids=' + ','.join(ids))
    expect(page.locator('[data-compare-remove]')).to_have_count(4)
    table = page.get_by_role('table')
    for gid in ids:
        g = next(g for g in models if g['id'] == gid)
        expect(table).to_contain_text(g['name'])
        expect(table).to_contain_text('฿' + format(g['priceTHB'], ','))
    assert page.locator('.compare-table-scroll img').count() == 4
    page.locator('[data-compare-remove]').last.click()
    expect(page.locator('[data-compare-remove]')).to_have_count(3)
    return {'models': ids, 'originalPricesVisible': True, 'images': 4, 'removeWorks': True, 'layout': layout(page)}

def favorites(page):
    go(page, BASE, '/guitars/yamaha-fg800')
    button = page.locator('.detail-actions button').nth(1)
    if button.get_attribute('aria-pressed') != 'true': button.click()
    go(page, BASE, '/wishlist')
    expect(page.locator('.wishlist-row')).to_have_count(1)
    expect(page.locator('.wishlist-row')).to_contain_text('FG800')
    expect(page.locator('.wishlist-row img')).to_be_visible()
    page.reload(wait_until='domcontentloaded')
    expect(page.locator('.wishlist-row')).to_have_count(1)
    page.locator('.wishlist-heart').click()
    expect(page.locator('.wishlist-row')).to_have_count(0)
    return {'save': True, 'imageVisible': True, 'persistReload': True, 'remove': True}

def quiz(page):
    go(page, BASE, '/find-my-guitar?step=1')
    for step in range(5):
        option = page.locator('.quiz-option').first
        expect(option).to_be_visible()
        option.click()
        expect(page.locator('.quiz-option.is-selected')).to_have_count(1)
        page.locator('.quiz-next').click()
    expect(page.locator('.quiz-results-page')).to_be_visible()
    assert page.locator('.quiz-results-page [data-guitar-id]').count() > 0
    frames(page)
    return {'originalFiveQuestionsCompleted': True, 'actualCatalogResults': True}

def practice(page):
    go(page, BASE, '/practice')
    expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status', 'ready', timeout=60000)
    for gid in ['C', 'Am', 'F', 'Cmaj7', 'Bm7', 'Csus4']:
        page.locator('[data-practice-chord="' + gid + '"]').click()
        expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord', gid)
    for button in page.locator('.practice-camera-controls button').all():
        expect(button).to_be_enabled()
        button.click()
    page.locator('#practice-chord-search').fill('Am')
    assert 0 < page.locator('[data-practice-chord]').count() < 42
    return {'actual3DReady': True, 'sixChordsSelectable': True, 'cameraControls': True, 'chordSearch': True}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
    for device, width, height in [('desktop', 1440, 1000), ('landscape', 1194, 834), ('portrait', 768, 1024), ('mobile', 390, 844)]:
        context = browser.new_context(viewport={'width': width, 'height': height}, has_touch=device != 'desktop', reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda error: report['runtimeErrors'].append(str(error)))
        page.on('console', lambda message: report['consoleErrors'].append(message.text) if message.type == 'error' else None)
        page.on('response', lambda response: report['imageResponseErrors'].append({'url': response.url, 'status': response.status}) if response.request.resource_type == 'image' and response.status >= 400 else None)
        for index, route in enumerate(ROUTES):
            check(device + '-route-' + str(index), lambda route=route: route_check(page, route), page)
        check(device + '-yamaha-catalog', lambda: catalog(page, BASE, 'production'), page)
        selected = models if device == 'desktop' else [g for g in models if g['id'] in ['yamaha-fg800', 'yamaha-fsx830c']]
        for model in selected:
            check(device + '-' + model['id'], lambda model=model: detail(page, context, BASE, 'production', model), page)
        check(device + '-compare', lambda: compare(page), page)
        check(device + '-favorites', lambda: favorites(page), page)
        check(device + '-quiz', lambda: quiz(page), page)
        check(device + '-practice', lambda: practice(page), page)
        go(page, BASE, '/guitars/yamaha-fg800')
        (OUT / 'screenshots').mkdir(exist_ok=True)
        page.screenshot(path=str(OUT / 'screenshots' / (device + '-fg800.png')), full_page=True, animations='disabled')
        context.close()
    browser.close()
report['adminBackendVerified'] = False
report['livePublishedCatalogVerified'] = False
report['passed'] = all(c['passed'] for c in report['checks']) and not any(report[k] for k in ['consoleErrors', 'runtimeErrors', 'imageResponseErrors'])
(OUT / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'checks': len(report['checks']), 'failed': sum(not c['passed'] for c in report['checks']), 'consoleErrors': len(report['consoleErrors']), 'runtimeErrors': len(report['runtimeErrors']), 'brokenImageRequests': len(report['imageResponseErrors']), 'adminBackendVerified': False}))
raise SystemExit(0 if report['passed'] else 1)
