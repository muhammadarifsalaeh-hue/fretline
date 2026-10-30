"""Read-only browser proof for existing Yamaha records and original preview images."""
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
parser.add_argument('--production', default='http://127.0.0.1:4190')
parser.add_argument('--preview', default='http://127.0.0.1:4191')
args = parser.parse_args()
audit = json.loads((OUT / 'audit.json').read_text())
models = audit['models']
report = {'checks': [], 'consoleErrors': [], 'runtimeErrors': [], 'imageResponseErrors': [],
          'physicalIPadSafariTested': False, 'engine': 'Chromium', 'databaseWrites': False}


def check(name, fn, page):
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
    assert len(pictures) == (2 if mode == 'production' else 19), pictures
    go(page, base, '/guitars?brand=Yamaha')
    page.locator('#catalog-search').fill('FSX830C')
    expect(page.locator('.catalog-grid article')).to_have_count(1)
    expect(page.locator('article[data-guitar-id="yamaha-fsx830c"]')).to_be_visible()
    return {'ids': ids, 'modelsWithRenderedImages': pictures, 'searchPassed': True, 'layout': layout(page)}


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for mode, base in [('production', args.production), ('preview', args.preview)]:
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda error: report['runtimeErrors'].append(str(error)))
        page.on('console', lambda message: report['consoleErrors'].append(message.text) if message.type == 'error' else None)
        page.on('response', lambda response: report['imageResponseErrors'].append({'url': response.url, 'status': response.status}) if response.request.resource_type == 'image' and response.status >= 400 else None)
        check(mode + '-catalog-search-links', lambda: catalog(page, base, mode), page)
        for model in models:
            check(mode + '-' + model['id'], lambda model=model: detail(page, context, base, mode, model), page)
        for name, width, height in [('tablet-portrait', 768, 1024), ('tablet-landscape', 1194, 834), ('mobile', 390, 844)]:
            page.set_viewport_size({'width': width, 'height': height})
            for gid in ['yamaha-fg800', 'yamaha-fsx830c']:
                model = next(model for model in models if model['id'] == gid)
                check(mode + '-' + name + '-' + gid, lambda model=model: detail(page, context, base, mode, model), page)
            go(page, base, '/guitars/yamaha-fg800')
            (OUT / 'screenshots').mkdir(exist_ok=True)
            page.screenshot(path=str(OUT / 'screenshots' / (mode + '-' + name + '-fg800.png')), full_page=True, animations='disabled')
        context.close()
    browser.close()

report['passed'] = all(case['passed'] for case in report['checks']) and not any(report[key] for key in ['consoleErrors', 'runtimeErrors', 'imageResponseErrors'])
(OUT / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'checks': len(report['checks']), 'failures': sum(not case['passed'] for case in report['checks']), 'consoleErrors': len(report['consoleErrors']), 'runtimeErrors': len(report['runtimeErrors']), 'imageResponseErrors': len(report['imageResponseErrors'])}))
raise SystemExit(0 if report['passed'] else 1)
