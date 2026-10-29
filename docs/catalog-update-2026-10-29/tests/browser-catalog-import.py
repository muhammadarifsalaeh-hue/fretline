"""Actual production-browser acceptance for the October 29 catalog import.

The independent expectations come from the pre-import effective catalog and
the source-audited attachment, not a snapshot of the new implementation.
"""
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
from urllib.request import urlopen
from hashlib import sha256
from collections import Counter
from playwright.sync_api import sync_playwright, expect
import argparse, json, re, traceback

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'docs/catalog-update-2026-10-29'
parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--engines', nargs='+', default=['chromium', 'webkit'])
parser.add_argument('--sizes', nargs='+', default=['desktop', 'landscape', 'portrait', 'mobile'])
parser.add_argument('--cases', nargs='+', default=['catalog', 'detail', 'compare-prices', 'compare-materials', 'catalog-all', 'picker', 'preservation'])
args = parser.parse_args()
BASE = args.url.rstrip('/')
OUT = args.output
OUT.mkdir(parents=True, exist_ok=True)
SIZES = {'desktop': (1440, 1000), 'landscape': (1194, 834), 'portrait': (768, 1024), 'mobile': (390, 844)}
before = json.loads((DOC / 'baseline-effective.json').read_text())
BY_ID = {g['id']: g for g in before}
price_proof = json.loads((DOC / 'verification/fender-sources.json').read_text())
NEW_PRICES = {g['id']: g['acceptedAmountTHB'] for g in price_proof['results'] if g['accepted']}
EXPECTED_PRICES = {g['id']: g['price'] for g in before if g.get('price') is not None} | NEW_PRICES
SOURCE_URLS = {g['id']: g['sourceURL'] for g in price_proof['results'] if g['accepted']}
assert len(BY_ID) == 200 and len(NEW_PRICES) == 9 and len(EXPECTED_PRICES) == 27
PRICE_IDS = ['fender-player-ii-stratocaster', 'fender-player-ii-telecaster-hh', 'yamaha-pacifica-612viifm', 'martin-d-18']
WOOD_IDS = ['yamaha-fgx830c', 'yamaha-fgx820c', 'fender-player-ii-stratocaster', 'martin-d-18']
REQUIRED_ROWS = {'brand', 'model', 'price', 'type', 'bodyShape', 'body', 'top', 'back', 'sides', 'neck', 'fretboard', 'strings', 'frets', 'scale', 'pickups', 'electronics', 'bridge'}
ACTIVE = ''

def snapshot():
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for folder in ['src', 'dist'] for p in (ROOT / folder).rglob('*') if p.is_file()}

start = snapshot()
report = {'baseURL': BASE, 'checks': [], 'consoleErrors': [], 'runtimeErrors': [], 'networkErrors': [], 'failedRequests': [], 'screenshots': [], 'physicalIPadSafariTested': False, 'servedHTMLSHA256': sha256(urlopen(BASE).read()).hexdigest(), 'viewports': SIZES, 'independentExpectedNewPrices': NEW_PRICES}

def save():
    (OUT / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

def check(name, function, page):
    global ACTIVE
    ACTIVE = name
    try:
        result = function()
        report['checks'].append({'name': name, 'passed': True, 'evidence': result})
        print('PASS', name, flush=True)
    except Exception:
        error = traceback.format_exc()
        file = name + '-FAIL.png'
        try: page.screenshot(path=str(OUT / file), animations='disabled')
        except Exception: pass
        report['checks'].append({'name': name, 'passed': False, 'error': error, 'url': page.url, 'screenshot': file})
        print('FAIL', name, error, flush=True)
    save()

def attach(page):
    page.on('console', lambda m: report['consoleErrors'].append({'case': ACTIVE, 'text': m.text}) if m.type == 'error' else None)
    page.on('pageerror', lambda e: report['runtimeErrors'].append({'case': ACTIVE, 'text': str(e)}))
    page.on('response', lambda r: report['networkErrors'].append({'case': ACTIVE, 'url': r.url, 'status': r.status}) if r.status >= 400 else None)
    page.on('requestfailed', lambda r: report['failedRequests'].append({'case': ACTIVE, 'url': r.url, 'failure': r.failure}))

def settle(page):
    if page.url == 'about:blank': return
    scene = page.locator('[data-practice-status]')
    if scene.count():
        expect(scene).to_have_attribute('data-practice-status', re.compile('^(ready|error)$'), timeout=60000)
        if scene.get_attribute('data-practice-status') == 'ready':
            canvas = page.locator('canvas[data-practice-canvas]')
            expect(canvas).to_have_attribute('data-hand-asset-status', re.compile('^(ready|error)$'), timeout=60000)
    page.evaluate('async()=>{await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));await document.fonts.ready}')
    page.wait_for_load_state('networkidle')

def go(page, path='/'):
    settle(page)
    page.goto(BASE + path, wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    expect(page.locator('main h1')).to_be_visible()

def metrics(page):
    data = page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
    assert data['scrollWidth'] <= data['width'] + 1, data
    return data

def shot(page, selector, filename):
    el = page.locator(selector)
    el.scroll_into_view_if_needed()
    for im in el.locator('img').all():
        if im.is_visible(): im.evaluate('(i)=>i.decode()')
    settle(page)
    page.evaluate('document.activeElement?.blur()')
    el.evaluate('(e)=>scrollBy(0,e.getBoundingClientRect().top-document.querySelector(".site-header").getBoundingClientRect().height-12)')
    page.screenshot(path=str(OUT / filename), animations='disabled')
    report['screenshots'].append(filename)

def ids(page):
    return page.locator('#catalog-results [data-guitar-id]').evaluate_all('(ns)=>ns.map(n=>n.dataset.guitarId)')

def catalog_count(page, n):
    expect(page.locator('.catalog-result-count > p').first).to_have_text(f'{n} รุ่น')

def table_row(page, key): return page.locator(f'[data-compare-row="{key}"]')
def values(page, key): return table_row(page, key).locator('[role=cell]').all_text_contents()
def price(n): return '฿' + format(n, ',')

def catalog(page, engine, size):
    go(page, '/guitars')
    catalog_count(page, 200)
    expect(page.locator('#catalog-results [data-guitar-id]')).to_have_count(9)
    search = page.locator('#catalog-search')
    search.fill('Player II Stratocaster')
    card = page.locator('[data-guitar-id="fender-player-ii-stratocaster"]')
    expect(card).to_be_visible()
    expect(card).to_contain_text('฿30,600')
    search.fill('D-18')
    card = page.locator('[data-guitar-id="martin-d-18"]')
    expect(card).to_be_visible()
    expect(card).to_contain_text('สอบถามราคา')
    assert '฿0' not in card.inner_text()
    search.press('Enter')
    assert parse_qs(urlparse(page.url).query)['q'] == ['D-18']
    for gid, expected_price in [('yamaha-pacifica-612viifm', 34000), ('yamaha-fg820-12', 16500)]:
        search.fill(BY_ID[gid]['name'])
        c = page.locator(f'[data-guitar-id="{gid}"]')
        expect(c).to_be_visible(); expect(c).to_contain_text(price(expected_price))
    go(page, '/guitars?brand=Fender&min=0&max=40000&sort=price-asc')
    catalog_count(page, 8)
    listed = ids(page)
    expected = {gid for gid, p in NEW_PRICES.items() if p <= 40000}
    assert set(listed) == expected, (listed, expected)
    assert [NEW_PRICES[x] for x in listed] == sorted(NEW_PRICES[x] for x in listed)
    page.locator('.catalog-toolbar select').select_option('price-desc')
    expect(page.locator('.catalog-toolbar select')).to_have_value('price-desc')
    listed_desc = ids(page)
    assert [NEW_PRICES[x] for x in listed_desc] == sorted((NEW_PRICES[x] for x in listed_desc), reverse=True)
    if size == 'landscape': shot(page, '#catalog-results', f'{engine}-{size}-catalog-verified-prices.png')
    go(page, '/guitars?type=bass&q=Thunderbird')
    thunder = page.locator('[data-guitar-id="epiphone-thunderbird-64-with-rosewood-fretboard"]')
    expect(thunder).to_have_count(1); expect(thunder).to_contain_text('เบส')
    return {'searchAndUnknownPrice': True, 'preservedPrimaryPrices': {'Pacifica': 34000, 'FG820-12': 16500}, 'newFenderBudgetIDs': listed, 'incorrectIncomingThunderbirdCategoryRejected': True, **metrics(page)}

def spec_cell(page, label):
    row = page.locator('#specs .spec-table tr').filter(has=page.get_by_role('rowheader', name=label, exact=True))
    expect(row).to_have_count(1)
    return row.get_by_role('cell')

def detail(page, engine, size):
    gid = 'fender-player-ii-stratocaster'
    go(page, '/guitars/' + gid + '#specs')
    expect(page.locator('.detail-price-block')).to_contain_text('฿30,600')
    note = page.locator('.detail-price-block .price-source-note')
    expect(note).to_contain_text('Music Arms'); expect(note).to_contain_text('2026-10-29')
    expect(note.locator('a')).to_have_attribute('href', SOURCE_URLS[gid])
    expected_fender = {'ทรงบอดี้': 'Stratocaster', 'รูปแบบปิ๊กอัพ': 'SSS', 'ความกว้างนัต': '42 mm', 'รัศมีฟิงเกอร์บอร์ด': '241 mm'}
    for label, value in expected_fender.items(): expect(spec_cell(page, label)).to_have_text(value)
    expect(spec_cell(page, 'ตัวกีตาร์')).to_have_text(BY_ID[gid]['specs']['body'])
    expect(spec_cell(page, 'จำนวนสาย')).to_have_text('ไม่ระบุ')
    if size == 'landscape': shot(page, '.detail-information', f'{engine}-{size}-detail-new-specs.png')
    gid = 'yamaha-fgx830c'
    go(page, '/guitars/' + gid + '#specs')
    expected_yamaha = {'ทรงบอดี้': 'Dreadnought Cutaway Style', 'ไม้หน้า': 'Solid Spruce', 'ไม้หลัง': 'Rosewood', 'ไม้ข้าง': 'Rosewood', 'ระบบไฟฟ้า': 'SYSTEM66'}
    for label, value in expected_yamaha.items(): expect(spec_cell(page, label)).to_have_text(value)
    expect(spec_cell(page, 'ตัวกีตาร์')).to_have_text(BY_ID[gid]['specs']['body'])
    expect(page.locator('.detail-price-block')).to_contain_text('สอบถามราคา')
    expect(spec_cell(page, 'ราคา')).to_have_text('สอบถามราคา')
    go(page, '/guitars/martin-d-18#specs')
    expect(page.locator('.detail-price-block')).to_contain_text('สอบถามราคา')
    expect(spec_cell(page, 'ราคา')).to_have_text('สอบถามราคา')
    assert '฿0' not in page.locator('.detail-price-block').inner_text()
    if size == 'portrait': shot(page, '.detail-price-block', f'{engine}-{size}-detail-unknown-price.png')
    return {'newFenderSource': SOURCE_URLS['fender-player-ii-stratocaster'], 'checkedOn': '2026-10-29', 'fourNewFenderFields': expected_fender, 'fiveNewYamahaFields': expected_yamaha, 'broaderMaterialsRetained': True, 'unknownPricesNotZero': True, **metrics(page)}

def compare_prices(page, engine, size):
    go(page, '/compare?ids=' + ','.join(PRICE_IDS))
    expect(page.locator('[data-compare-card]')).to_have_count(4)
    expected_prices = [30600, 31500, 34000, None]
    for gid, amount in zip(PRICE_IDS, expected_prices):
        expect(page.locator(f'[data-compare-card="{gid}"] .pc-model-card__price')).to_have_text('สอบถามราคา' if amount is None else price(amount))
    expect(page.locator('[data-compare-card="fender-player-ii-stratocaster"] .price-source-note')).to_contain_text('Music Arms')
    assert REQUIRED_ROWS.issubset(set(page.locator('[data-compare-row]').evaluate_all('(ns)=>ns.map(n=>n.dataset.compareRow)')))
    p = table_row(page, 'price')
    expect(p).to_have_attribute('data-compare-different', 'true')
    expect(p).to_have_attribute('data-compare-incomplete', 'true')
    cells = p.locator('[role=cell]')
    expect(cells.nth(0)).to_contain_text('฿30,600'); expect(cells.nth(1)).to_contain_text('+฿900')
    expect(cells.nth(2)).to_contain_text('฿34,000'); expect(cells.nth(3)).to_have_text('สอบถามราคา')
    assert cells.nth(0).locator('span[title]').count() == 1
    assert cells.nth(3).locator('span[title],.comparison-value-note').count() == 0
    for key in ['bodyShape', 'top', 'back', 'sides', 'strings', 'electronics']:
        expect(table_row(page, key)).to_be_visible()
    strings = table_row(page, 'strings')
    assert strings.locator('[role=cell]').all_text_contents() == ['ไม่มีข้อมูล'] * 4
    assert strings.get_attribute('data-compare-different') is None
    assert strings.locator('.comparison-same-note').count() == 0
    for category in ['sound', 'materials', 'hardware', 'dimensions', 'all', 'main']:
        tab = page.locator(f'[data-compare-category="{category}"]'); tab.click()
        expect(tab).to_have_attribute('aria-selected', 'true')
        assert page.locator('[data-compare-row]').count() > 0
    region = page.locator('.compare-table-scroll')
    data = region.evaluate('(e)=>({width:e.clientWidth,scroll:e.scrollWidth})')
    if page.viewport_size['width'] < 1024:
        assert data['scroll'] > data['width'], data
        region.evaluate('(e)=>e.scrollLeft=e.scrollWidth')
        assert region.evaluate('(e)=>e.scrollLeft') > 0
        region.evaluate('(e)=>e.scrollLeft=0')
    if size in ['landscape', 'portrait']: shot(page, '.compare-table-scroll', f'{engine}-{size}-compare-prices.png')
    return {'selection': PRICE_IDS, 'requiredVisibleKeys': sorted(REQUIRED_ROWS), 'newPrices': expected_prices, 'cheapestKnownOnly': True, 'unknownSpecLabel': 'ไม่มีข้อมูล', 'unknownPriceLabel': 'สอบถามราคา', 'tableHorizontalScroll': data, **metrics(page)}

def compare_materials(page, engine, size):
    go(page, '/compare?ids=' + ','.join(WOOD_IDS))
    page.locator('[data-compare-category="materials"]').click()
    back = table_row(page, 'back')
    assert back.locator('[role=cell]').all_text_contents() == ['Rosewood', 'Mahogany', 'ไม่มีข้อมูล', 'ไม่มีข้อมูล']
    expect(back).to_have_attribute('data-compare-different', 'true')
    expect(back).to_have_attribute('data-compare-incomplete', 'true')
    top = table_row(page, 'top')
    assert top.locator('[role=cell]').all_text_contents() == ['Solid Spruce', 'Solid Spruce', 'ไม่มีข้อมูล', 'ไม่มีข้อมูล']
    expect(top).to_have_attribute('data-compare-incomplete', 'true')
    assert top.get_attribute('data-compare-different') is None
    assert top.locator('.comparison-same-note').count() == 0
    diff = page.get_by_role('switch', name='แสดงเฉพาะส่วนที่ต่างกัน', exact=True)
    diff.click(); expect(diff).to_have_attribute('aria-checked', 'true')
    assert top.evaluate('(e)=>e.closest("[aria-hidden=true]")!==null')
    assert not back.evaluate('(e)=>e.closest("[aria-hidden=true]")!==null')
    diff.click(); expect(diff).to_have_attribute('aria-checked', 'false')
    page.locator('[data-compare-category="sound"]').click()
    electronics = table_row(page, 'electronics')
    assert electronics.locator('[role=cell]').all_text_contents() == ['SYSTEM66', 'SYSTEM66', 'ไม่มีข้อมูล', 'ไม่มีข้อมูล']
    assert electronics.get_attribute('data-compare-different') is None
    expect(electronics).to_have_attribute('data-compare-incomplete', 'true')
    if size == 'mobile': shot(page, '.compare-table-scroll', f'{engine}-{size}-compare-materials.png')
    if size == 'desktop':
        go(page, '/compare?ids=yamaha-fg820-12,yamaha-fgx830c')
        page.locator('[data-compare-category="sound"]').click()
        electronics = table_row(page, 'electronics')
        assert electronics.locator('[role=cell]').all_text_contents() == ['None', 'SYSTEM66']
        expect(electronics).to_have_attribute('data-compare-different', 'true')
        go(page, '/compare?ids=fender-player-ii-stratocaster,fender-player-ii-telecaster')
        equal_price = table_row(page, 'price')
        assert equal_price.get_attribute('data-compare-different') is None
        expect(equal_price.locator('.comparison-same-note')).to_be_visible()
    return {'sourceBackWoodDiff': ['Rosewood', 'Mahogany'], 'equalKnownTopWithUnknownsNotFalseDifference': True, 'missingElectronicsNotNone': True, 'differencesOnlyPreserved': True, **metrics(page)}

def collect_pages(page):
    found = []
    while True:
        current = ids(page); assert current
        found.extend(current)
        next_button = page.get_by_role('button', name='หน้าถัดไป', exact=True)
        if next_button.is_disabled(): break
        next_button.scroll_into_view_if_needed(); settle(page); next_button.click()
        expect(page.locator('#catalog-results [data-guitar-id]').first).not_to_have_attribute('data-guitar-id', current[0])
    return found

def all_catalog(page):
    go(page, '/guitars')
    all_ids = collect_pages(page)
    assert len(all_ids) == len(set(all_ids)) == 200
    assert set(all_ids) == set(BY_ID)
    brands = Counter(BY_ID[x]['brand'] for x in all_ids)
    assert len(brands) == 10 and set(brands.values()) == {20}
    for brand in sorted(brands):
        go(page, '/guitars?' + urlencode({'brand': brand}))
        catalog_count(page, 20)
        assert all(BY_ID[x]['brand'] == brand for x in ids(page))
    go(page, '/guitars?min=0&sort=price-asc')
    catalog_count(page, 27)
    known = collect_pages(page)
    assert set(known) == set(EXPECTED_PRICES)
    assert [EXPECTED_PRICES[x] for x in known] == sorted(EXPECTED_PRICES[x] for x in known)
    go(page, '/guitars?brand=Fender&min=0')
    catalog_count(page, 9)
    assert set(ids(page)) == set(NEW_PRICES)
    return {'all200StableIDsVisitedViaPagination': True, 'brands': dict(brands), 'all27KnownPricesFilterAndSort': True, **metrics(page)}

def picker(page):
    go(page, '/compare?ids=')
    expect(page.locator('[data-compare-empty-slot]')).to_have_count(4)
    page.get_by_role('button', name='เพิ่มกีตาร์', exact=True).first.click()
    dialog = page.get_by_role('dialog', name='เพิ่มกีตาร์', exact=True)
    expect(dialog).to_be_visible()
    field = dialog.get_by_role('searchbox')
    for gid in PRICE_IDS:
        field.fill(BY_ID[gid]['name'])
        entry = dialog.locator('.picker-model-row').filter(has=page.get_by_text(BY_ID[gid]['name'], exact=True))
        expect(entry).to_have_count(1); entry.click(); expect(entry).to_have_attribute('aria-pressed', 'true')
    field.fill(BY_ID['yamaha-fg820-12']['name'])
    entry = dialog.locator('.picker-model-row').filter(has=page.get_by_text(BY_ID['yamaha-fg820-12']['name'], exact=True))
    expect(entry).to_be_disabled()
    dialog.get_by_role('button', name='เสร็จสิ้น', exact=True).click()
    expect(page.locator('[data-compare-card]')).to_have_count(4)
    page.get_by_role('button', name='แชร์ลิงก์', exact=True).click()
    field = page.locator('.share-link-control input')
    expect(field).to_be_visible()
    shared = field.input_value()
    assert parse_qs(urlparse(shared).query)['ids'][0].split(',') == PRICE_IDS
    page.locator('[data-compare-remove="' + PRICE_IDS[0] + '"]').click()
    expect(page.locator('[data-compare-card]')).to_have_count(3)
    settle(page); page.reload(wait_until='networkidle')
    expect(page.locator('[data-compare-card]')).to_have_count(3)
    page.get_by_role('button', name='ล้างการเปรียบเทียบ', exact=True).click()
    confirm = page.get_by_role('alertdialog')
    confirm.get_by_role('button', name='ยกเลิก', exact=True).click()
    expect(page.locator('[data-compare-card]')).to_have_count(3)
    page.get_by_role('button', name='ล้างการเปรียบเทียบ', exact=True).click()
    page.get_by_role('alertdialog').get_by_role('button', name='ยืนยันล้างรายการ', exact=True).click()
    expect(page.locator('[data-compare-empty-slot]')).to_have_count(4)
    go(page, '/compare?ids=' + ','.join(PRICE_IDS + ['yamaha-fg820-12', 'made-up-model', PRICE_IDS[0]]))
    assert page.locator('[data-compare-card]').evaluate_all('(ns)=>ns.map(n=>n.dataset.compareCard)') == PRICE_IDS
    return {'addFourFifthDisabled': True, 'sharedURL': shared, 'removeReloadClearCancelConfirm': True, 'invalidDuplicateOversizedShareIDsRejected': True, **metrics(page)}

def preserved_tools(page, engine):
    go(page)
    assert page.locator('.signature-hero-slide').count() == 3
    assert page.locator('[data-marquee-primary] [data-brand-id]').count() == 10
    assert page.locator('.signature-category-card').count() == 4
    assert page.locator('#home-features > *').count() == 3
    assert page.locator('#featured [role=tab]').count() == 4
    assert page.locator('.signature-stats-list dd').all_text_contents() == ['200', '10', '4', '4']
    for selector, path in [('#home-practice .home-editorial-cta', '/practice'), ('#find .home-editorial-cta', '/find-my-guitar'), ('#compare .home-editorial-cta', '/compare')]:
        expect(page.locator(selector)).to_have_attribute('href', path)
    go(page, '/brands')
    cards = page.locator('.brand-directory-card[data-brand-id]')
    expect(cards).to_have_count(10)
    for card in cards.all(): expect(card.locator('.brand-count-full')).to_have_text('20 รุ่นในแคตตาล็อก')
    page.locator('.brand-directory-card[data-brand-id="fender"]').click()
    assert parse_qs(urlparse(page.url).query)['brand'] == ['Fender']; catalog_count(page, 20)
    go(page)
    page.locator('#hero-search').fill('FG820-12'); page.locator('#hero-search').press('Enter')
    card = page.locator('[data-guitar-id="yamaha-fg820-12"]')
    expect(card).to_have_count(1)
    wish = card.get_by_role('button', name=re.compile('รายการโปรด'))
    wish.click(); expect(wish).to_have_attribute('aria-pressed', 'true')
    go(page, '/wishlist')
    expect(page.locator('[data-guitar-id="yamaha-fg820-12"]')).to_have_count(1)
    go(page, '/find-my-guitar')
    answers = [('type', 'electric'), ('level', 'beginner'), ('style', 'rock'), ('budget', 'high'), ('priority', 'value')]
    for index, (name, value) in enumerate(answers, 1):
        expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow', str(index))
        radio = page.locator(f'input[name="{name}"][value="{value}"]')
        radio.locator('..').click(); expect(radio).to_be_checked()
        page.get_by_role('button', name='ดูผลแนะนำ' if index == 5 else 'ถัดไป', exact=True).click()
    expect(page.locator('.quiz-results-page')).to_be_visible()
    result_cards = page.locator('.match-card[data-guitar-id]')
    assert result_cards.count() > 0
    result_ids = result_cards.evaluate_all('(ns)=>ns.map(n=>n.dataset.guitarId)')
    assert set(result_ids).issubset(BY_ID)
    for gid in result_ids:
        card = page.locator(f'.match-card[data-guitar-id="{gid}"]')
        if gid in EXPECTED_PRICES: expect(card).to_contain_text(price(EXPECTED_PRICES[gid]))
        else: expect(card).to_contain_text('สอบถามราคา')
    go(page, '/practice')
    expect(page.locator('[data-practice-chord]')).to_have_count(42)
    page.locator('[data-practice-chord="Am"]').click()
    expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord', 'Am')
    settle(page)
    status = page.locator('[data-practice-status]').get_attribute('data-practice-status')
    metrics(page)
    return {'homeHeroBrandCategoryFeaturesFeaturedPreserved': True, 'brandDirectoryTenByTwenty': True, 'heroSearchAndWishlist': True, 'fiveQuestionQuizResultsValidForNewData': result_ids, 'practice42AndChordSelection': True, 'actualPracticeStatus': status}

with sync_playwright() as p:
    for engine in args.engines:
        browser = None
        try:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader']) if engine == 'chromium' else p.webkit.launch()
            report.setdefault('browserVersions', {})[engine] = browser.version
            for size in args.sizes:
                w, h = SIZES[size]
                context = browser.new_context(viewport={'width': w, 'height': h}, has_touch=size != 'desktop', reduced_motion='reduce')
                context.add_init_script("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new Error('QA denied clipboard')}}});")
                page = context.new_page(); attach(page)
                for name, fn in [('catalog', catalog), ('detail', detail), ('compare-prices', compare_prices), ('compare-materials', compare_materials)]:
                    if name in args.cases: check(f'{engine}-{size}-{name}', lambda fn=fn: fn(page, engine, size), page)
                if size == 'desktop':
                    if 'catalog-all' in args.cases: check(f'{engine}-all-200-ids-and-brand-counts', lambda: all_catalog(page), page)
                    if 'picker' in args.cases: check(f'{engine}-actual-picker-share-selection', lambda: picker(page), page)
                    if 'preservation' in args.cases: check(f'{engine}-home-brands-quiz-practice-wishlist', lambda: preserved_tools(page, engine), page)
                settle(page); context.close()
        except Exception:
            report.setdefault('harnessFailures', []).append({'engine': engine, 'error': traceback.format_exc()})
            print('HARNESSFAIL', engine, report['harnessFailures'][-1]['error'], flush=True)
        finally:
            if browser: browser.close()

report['sourceAndBuildUnchangedDuringRun'] = start == snapshot()
report['passed'] = bool(report['checks']) and all(c['passed'] for c in report['checks']) and report['sourceAndBuildUnchangedDuringRun'] and not any(report.get(k) for k in ['consoleErrors', 'runtimeErrors', 'networkErrors', 'failedRequests', 'harnessFailures'])
save()
print('FINAL', sum(c['passed'] for c in report['checks']), '/', len(report['checks']), report['passed'], flush=True)
raise SystemExit(0 if report['passed'] else 1)
