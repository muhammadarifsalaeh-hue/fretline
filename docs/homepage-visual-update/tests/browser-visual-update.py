"""Browser checks for the explicitly requested Homepage visual update.

Run against a frozen production build. Historical reports and acceptance scripts
are kept intact; this suite checks the new authorized copy and background assets.
"""
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from hashlib import sha256
from playwright.sync_api import sync_playwright, expect
import argparse, json, re, traceback

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--engines', nargs='+', default=['chromium', 'webkit'])
args = parser.parse_args()
BASE = args.url.rstrip('/')
OUT = args.output
OUT.mkdir(parents=True, exist_ok=True)
SIZES = {'desktop': (1440, 1000), 'landscape': (1194, 834), 'portrait': (768, 1024), 'mobile': (390, 844), 'narrow': (320, 740), 'portrait-edge': (1024, 1366)}
CATEGORIES = [('electric', 'กีตาร์ไฟฟ้า', 90), ('acoustic', 'กีตาร์โปร่ง', 73), ('classical', 'กีตาร์คลาสสิก', 20), ('bass', 'เบส', 17)]
FEATURES = [('42 คอร์ด', 'ครบทุกพื้นฐาน'), ('มุมมอง 3D', 'หมุน ซูม ได้อิสระ'), ('เรียนรู้ทีละขั้น', 'พัฒนาต่อเนื่อง')]
ACTIVE = ''
report = {'baseURL': BASE, 'physicalIPadSafariTested': False, 'checks': [], 'consoleErrors': [], 'runtimeErrors': [], 'networkErrors': [], 'failedRequests': [], 'screenshots': [], 'servedHTMLSHA256': sha256(urlopen(BASE).read()).hexdigest(), 'notes': ['Linux WebKit with synthetic touch does not certify native iPad Safari.', 'Category scenes are generic illustrations and never named-product evidence.']}
def snapshot():
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for folder in ['src', 'dist'] for p in (ROOT / folder).rglob('*') if p.is_file()}
start = snapshot()
def normalized(text): return re.sub(r'\s+', '', text)
def check(name, function, page):
    global ACTIVE
    ACTIVE = name
    try:
        evidence = function()
        report['checks'].append({'name': name, 'passed': True, 'evidence': evidence})
        print('PASS', name, flush=True)
    except Exception:
        error = traceback.format_exc()
        file = name + '-FAIL.png'
        try: page.screenshot(path=str(OUT / file), full_page=True, animations='disabled')
        except Exception: pass
        report['checks'].append({'name': name, 'passed': False, 'error': error, 'url': page.url, 'screenshot': file})
        print('FAIL', name, error, flush=True)
    (OUT / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
def attach(page):
    page.on('console', lambda m: report['consoleErrors'].append({'case': ACTIVE, 'message': m.text}) if m.type == 'error' else None)
    page.on('pageerror', lambda e: report['runtimeErrors'].append({'case': ACTIVE, 'message': str(e)}))
    page.on('response', lambda r: report['networkErrors'].append({'case': ACTIVE, 'url': r.url, 'status': r.status}) if r.status >= 400 else None)
    page.on('requestfailed', lambda r: report['failedRequests'].append({'case': ACTIVE, 'url': r.url, 'failure': r.failure}))
def go(page, path='/'):
    if page.url != 'about:blank':
        # SPA content can introduce a new font face after its DOM assertions
        # succeed. Allow its actual paint and font load to finish before a hard
        # navigation, rather than cancelling that resource as a harness artifact.
        page.evaluate('async()=>{await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));await document.fonts.ready}')
    page.goto(BASE + path, wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    expect(page.locator('main h1')).to_be_visible()
def metrics(page):
    data = page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
    assert data['scrollWidth'] <= data['width'] + 1, data
    return data
def photo(image):
    image.scroll_into_view_if_needed()
    image.evaluate('(i)=>i.decode()')
    data = image.evaluate('(i)=>({src:i.currentSrc,width:i.naturalWidth,height:i.naturalHeight,fit:getComputedStyle(i).objectFit,loading:i.loading,srcset:i.srcset,sizes:i.sizes})')
    assert data['width'] > 0 and data['height'] > 0, data
    return data
def screenshot(page, selector, filename):
    el = page.locator(selector)
    el.scroll_into_view_if_needed()
    for im in el.locator('img').all(): photo(im)
    page.evaluate('document.activeElement?.blur()')
    el.screenshot(path=str(OUT / filename), animations='disabled')
    report['screenshots'].append(filename)
def inside(inner, outer):
    return inner['x'] >= outer['x'] - 1 and inner['y'] >= outer['y'] - 1 and inner['x'] + inner['width'] <= outer['x'] + outer['width'] + 1 and inner['y'] + inner['height'] <= outer['y'] + outer['height'] + 1
def document_rect(locator):
    # Each lazy image can move the viewport while decoding. Use stable document
    # coordinates so row/column comparisons retain their original criteria.
    return locator.evaluate('(e)=>{const r=e.getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height}}')
def categories(page, engine, size):
    cards = page.locator('.signature-category-card')
    expect(cards).to_have_count(4)
    rows = []
    for i, (category, title, count) in enumerate(CATEGORIES):
        card = cards.nth(i)
        expect(card).to_have_attribute('href', '/guitars?type=' + category)
        expect(card.locator('h3')).to_have_text(title)
        expect(card.locator('.signature-category-copy p')).to_have_text(f'{count} รุ่น')
        info = photo(card.locator('img'))
        assert info['fit'] == 'cover', info
        assert info['srcset'] and info['sizes'], info
        rect = document_rect(card)
        art = document_rect(card.locator('.signature-category-art'))
        assert abs(art['width'] - rect['width']) <= 3 and abs(art['height'] - rect['height']) <= 3, (rect, art)
        copy = document_rect(card.locator('.signature-category-copy'))
        assert copy['x'] >= rect['x'] + rect['width'] * .48, (rect, copy)
        assert inside(copy, rect), (rect, copy)
        assert card.locator('h3').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
        assert rect['width'] >= 44 and rect['height'] >= 44
        rows.append({'category': category, 'count': count, 'image': info, 'rect': rect, 'copyRect': copy})
    r = [x['rect'] for x in rows]
    if page.viewport_size['width'] >= 640:
        assert abs(r[0]['y'] - r[1]['y']) < 2 and abs(r[2]['y'] - r[3]['y']) < 2, r
        assert abs(r[0]['x'] - r[2]['x']) < 2 and r[0]['x'] + r[0]['width'] < r[1]['x'], r
        assert r[0]['y'] + r[0]['height'] < r[2]['y'], r
    else:
        assert all(r[i]['y'] + r[i]['height'] < r[i + 1]['y'] for i in range(3)), r
    cards.first.focus()
    assert cards.first.evaluate('(e)=>getComputedStyle(e).outlineStyle') != 'none'
    screenshot(page, '#categories', f'{engine}-{size}-categories.png')
    return {'actualCategoryCounts': rows, **metrics(page)}
def mode_cards(page, engine, size):
    group = page.locator('#home-features')
    assert group.locator(':scope > *').count() == 3
    practice = group.locator('[data-home-practice-card]')
    expect(practice.locator('.signature-section-eyebrow')).to_have_text('01 / GUITAR PRACTICE STUDIO')
    assert normalized(practice.locator('h2').inner_text()) == 'โหมดฝึกกีตาร์'
    assert practice.locator('h2 br').count() == 1
    expect(practice.locator('.home-editorial-description')).to_have_text('ฝึกจับคอร์ด เล่นกีตาร์ไปกับบทเรียนที่สนุก ตั้งแต่พื้นฐาน จนถึงขั้นสูง', use_inner_text=True)
    features = practice.locator('.home-practice-features li')
    expect(features).to_have_count(3)
    for i, (title, detail) in enumerate(FEATURES):
        expect(features.nth(i)).to_contain_text(title)
        expect(features.nth(i)).to_contain_text(detail)
    practice_photo = photo(practice.locator('img'))
    assert 'practice-long-haired-guitarist-' in practice_photo['src'], practice_photo
    assert practice_photo['fit'] == 'cover'
    expected = [('home-practice', '/practice', 'เริ่มฝึกกีตาร์'), ('find', '/find-my-guitar', 'เริ่มค้นหากีตาร์'), ('compare', '/compare', 'เริ่มเปรียบเทียบ')]
    card_rows = []
    for key, href, label in expected:
        card = group.locator('#' + key)
        link = card.locator('.home-editorial-cta')
        expect(link).to_have_attribute('href', href)
        expect(link).to_contain_text(label)
        assert 'linear-gradient' in link.evaluate('(e)=>getComputedStyle(e).backgroundImage')
        rect = document_rect(card)
        for child in ['h2', '.home-editorial-description', '.home-editorial-cta']:
            assert inside(document_rect(card.locator(child)), rect), (key, child, rect)
        assert link.bounding_box()['height'] >= 44
        card_rows.append({'id': key, 'rect': rect})
    expect(group.locator('#find .signature-section-eyebrow')).to_have_text('03 / FIND MY GUITAR')
    assert normalized(group.locator('#find h2').inner_text()) == 'กีตาร์ที่ใช่เริ่มจากตัวคุณ'
    expect(group.locator('#find .home-editorial-description')).to_have_text('5 คำถามสั้น ๆ เพื่อค้นหากีตาร์ที่เข้ากับสไตล์ของคุณ')
    assert 'electric-studio-' in photo(group.locator('#find img'))['src']
    expect(group.locator('#compare .signature-section-eyebrow')).to_have_text('04 / SIDE BY SIDE')
    assert normalized(group.locator('#compare h2').inner_text()) == 'มองเห็นความต่างก่อนตัดสินใจ'
    expect(group.locator('#compare .home-editorial-description')).to_have_text('เลือก 2–4 รุ่น แล้ววางรายละเอียดข้างกัน ดูว่าอะไรสำคัญกับการเล่นของคุณ', use_inner_text=True)
    assert 'quiz-studio-' in photo(group.locator('#compare img'))['src']
    r = [x['rect'] for x in card_rows]
    w, h = page.viewport_size['width'], page.viewport_size['height']
    stack = w < 1024 or (h > w and w <= 1366)
    if stack:
        assert r[0]['y'] + r[0]['height'] < r[1]['y'] and r[1]['y'] + r[1]['height'] < r[2]['y'], r
    else:
        assert abs(r[0]['y'] - r[1]['y']) < 2 and abs(r[0]['y'] + r[0]['height'] - r[2]['y'] - r[2]['height']) < 2, r
        assert r[0]['x'] + r[0]['width'] < r[1]['x'] and abs(r[1]['x'] - r[2]['x']) < 2, r
        assert r[0]['height'] > r[1]['height'], r
    assert group.evaluate('(e)=>e.nextElementSibling.id') == 'featured'
    assert group.locator('form,input,table').count() == 0
    screenshot(page, '#home-features', f'{engine}-{size}-features.png')
    # Individual cards fit ordinary viewport captures and avoid the fixed-chrome
    # stitching artifacts of a locator taller than the viewport. No CSS is hidden.
    for key in ['home-practice', 'find', 'compare']:
        card = group.locator('#' + key)
        page.evaluate('document.activeElement?.blur()')
        card.evaluate('(e)=>scrollBy(0,e.getBoundingClientRect().top-document.querySelector(".site-header").getBoundingClientRect().height-12)')
        filename = f'{engine}-{size}-{key}-card.png'
        card.screenshot(path=str(OUT / filename), animations='disabled')
        report['screenshots'].append(filename)
    return {'stacked': stack, 'cards': card_rows, 'practicePhoto': practice_photo, **metrics(page)}
def preserved_home(page, engine, size):
    assert page.locator('.signature-hero-slide').count() == 3
    expect(page.locator('.signature-hero-title')).to_contain_text('ค้นพบ')
    expect(page.locator('.signature-hero-title')).to_contain_text('เสียงที่เป็นคุณ')
    assert page.locator('.signature-stats-list dd').all_text_contents() == ['200', '10', '4', '4']
    assert page.locator('[data-marquee-primary] [data-brand-id]').count() == 10
    assert page.locator('#brands button').count() == 0
    assert page.locator('#featured [role=tab]').count() == 4
    assert page.locator('#featured .guitar-card').count() > 0
    for tab in page.locator('#featured [role=tab]').all():
        tab.click()
        expect(tab).to_have_attribute('aria-selected', 'true')
    page.locator('#featured [role=tab]').first.click()
    track = page.locator('.signature-collection-track')
    assert track.evaluate('(e)=>e.scrollWidth>e.clientWidth')
    track.evaluate('(e)=>e.scrollLeft=120')
    assert track.evaluate('(e)=>e.scrollLeft') > 0
    track.evaluate('(e)=>e.scrollLeft=0')
    assert not re.search(r'\bAI\s*(?:Generated|Edited)|Powered\s+by\s+AI', page.locator('main').inner_text(), re.I)
    page.evaluate('scrollTo(0,0)')
    file = f'{engine}-{size}-home.png'
    page.screenshot(path=str(OUT / file), full_page=True, animations='disabled')
    report['screenshots'].append(file)
    return {'heroSlides': 3, 'brandLinks': 10, 'featuredTabs': 4, 'featuredScroll': True, **metrics(page)}
def navigation_and_state(page):
    rows = []
    for category, title, count in CATEGORIES:
        go(page)
        page.locator('.signature-category-card--' + category).click()
        assert urlparse(page.url).path == '/guitars' and parse_qs(urlparse(page.url).query)['type'] == [category]
        expect(page.locator('.catalog-result-count')).to_contain_text(str(count))
        rows.append({'category': category, 'actualCatalogCount': count})
    for selector, path in [('#home-practice .home-editorial-cta', '/practice'), ('#find .home-editorial-cta', '/find-my-guitar'), ('#compare .home-editorial-cta', '/compare')]:
        go(page)
        page.locator(selector).click()
        assert urlparse(page.url).path == path
        if path == '/practice':
            expect(page.locator('[data-practice-chord]')).to_have_count(42)
            expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord', 'C')
            expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status', re.compile('^(ready|error)$'), timeout=60000)
            if page.locator('[data-practice-status]').get_attribute('data-practice-status') == 'ready':
                expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status', 'ready', timeout=60000)
            page.locator('[data-practice-chord="Am"]').click()
            expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord', 'Am')
        elif path == '/find-my-guitar':
            expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow', '1')
            expect(page.locator('input[name="type"]')).to_have_count(5)
        else: expect(page.locator('[data-compare-empty-slot]')).to_have_count(4)
    go(page)
    page.locator('#hero-search').fill('FG820-12')
    page.locator('#hero-search').press('Enter')
    assert parse_qs(urlparse(page.url).query)['q'] == ['FG820-12']
    card = page.locator('[data-guitar-id="yamaha-fg820-12"]')
    expect(card).to_have_count(1)
    wish = card.get_by_role('button', name=re.compile('รายการโปรด'))
    wish.click()
    expect(wish).to_have_attribute('aria-pressed', 'true')
    assert 'yamaha-fg820-12' in page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))')
    wish.click()
    compare = card.locator('.catalog-card-actions button')
    compare.click()
    expect(compare).to_have_attribute('aria-pressed', 'true')
    go(page, '/compare')
    expect(page.locator('[data-compare-card="yamaha-fg820-12"]')).to_have_count(1)
    return {'categoryRoutes': rows, 'allThreeModeCTAs': True, 'practice42AndChordSelection': True, 'quizFirstQuestion': True, 'compareFourSlots': True, 'heroSearchWishlistCompare': True}
def motion(page):
    go(page)
    hero = page.locator('[data-hero-slide-index]')
    before = hero.get_attribute('data-hero-slide-index')
    page.wait_for_function('(before)=>document.querySelector("[data-hero-slide-index]").dataset.heroSlideIndex!==before', arg=before, timeout=10000)
    after = hero.get_attribute('data-hero-slide-index')
    rail = page.locator('[data-marquee-viewport]')
    rail.scroll_into_view_if_needed()
    start = rail.evaluate('(e)=>e.scrollLeft')
    page.wait_for_timeout(500)
    end = rail.evaluate('(e)=>e.scrollLeft')
    assert end != start, (start, end)
    r = rail.bounding_box()
    page.mouse.move(r['x'] + r['width'] * .7, r['y'] + r['height'] * .5)
    page.mouse.down()
    page.mouse.move(r['x'] + r['width'] * .3, r['y'] + r['height'] * .5, steps=12)
    moved = rail.evaluate('(e)=>e.scrollLeft')
    page.mouse.up()
    assert moved != end, (end, moved)
    page.wait_for_timeout(1800)
    resumed = rail.evaluate('(e)=>e.scrollLeft')
    assert resumed != moved
    return {'heroBefore': before, 'heroAfter': after, 'brandAuto': [start, end], 'brandDrag': moved, 'brandAutoResumed': resumed}

with sync_playwright() as p:
    for engine in args.engines:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader']) if engine == 'chromium' else p.webkit.launch()
        report.setdefault('browserVersions', {})[engine] = browser.version
        for size, (w, h) in SIZES.items():
            context = browser.new_context(viewport={'width': w, 'height': h}, has_touch=size != 'desktop', reduced_motion='reduce')
            page = context.new_page()
            attach(page)
            go(page)
            check(f'{engine}-{size}-fullbleed-category-grid', lambda: categories(page, engine, size), page)
            check(f'{engine}-{size}-three-mode-card-layout', lambda: mode_cards(page, engine, size), page)
            check(f'{engine}-{size}-preserved-home-sections', lambda: preserved_home(page, engine, size), page)
            if size in ['desktop', 'mobile']:
                check(f'{engine}-{size}-navigation-real-data-state', lambda: navigation_and_state(page), page)
            context.close()
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='no-preference')
        page = context.new_page()
        attach(page)
        check(f'{engine}-normal-motion-hero-brand', lambda: motion(page), page)
        context.close()
        browser.close()
report['sourceAndBuildUnchangedDuringRun'] = start == snapshot()
report['passed'] = all(x['passed'] for x in report['checks']) and report['sourceAndBuildUnchangedDuringRun'] and not any(report[k] for k in ['consoleErrors', 'runtimeErrors', 'networkErrors', 'failedRequests'])
(OUT / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('FINAL', sum(c['passed'] for c in report['checks']), '/', len(report['checks']), report['passed'], flush=True)
raise SystemExit(0 if report['passed'] else 1)
