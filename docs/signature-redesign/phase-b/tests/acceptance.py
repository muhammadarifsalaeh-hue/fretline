"""Phase B browser acceptance. Run against an existing production server; not Safari.

FRETLINE_QA_URL=http://127.0.0.1:5201 python docs/signature-redesign/phase-b/tests/acceptance.py
Optional FRETLINE_QA_CASES=price,filters,hover,contrast,navigation,focus,gallery,wishlist,compare,quiz,responsive
"""
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, expect
import json, os, re, traceback

OUT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:5201').rstrip('/')
ID = 'yamaha-pacifica-612viifm'
SECOND = 'yamaha-fg800'
THIRD = 'fender-american-professional-ii-stratocaster'
FOURTH = 'gibson-les-paul-standard-60s'
FIFTH = 'prs-se-custom-24'
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'failures').mkdir(exist_ok=True)
REPORT = {'browser': 'Chromium / Linux; physical iPad and Safari not tested',
          'baseURL': BASE, 'checks': [], 'consoleErrors': [], 'runtimeErrors': [],
          'failedRequests': [], 'responsive': []}
ACTIVE = None


def context_for(browser, width=1440, height=1000, touch=False):
    context = browser.new_context(viewport={'width': width, 'height': height},
                                  has_touch=touch, reduced_motion='reduce')
    context.add_init_script('''if (!sessionStorage.getItem('phase-b-seeded')) {
        localStorage.setItem('fretline:compare', '[]');
        localStorage.setItem('fretline:wishlist', '[]');
        sessionStorage.setItem('phase-b-seeded', 'true');
    }''')
    page = context.new_page()
    page.on('console', lambda msg: REPORT['consoleErrors'].append({'case': ACTIVE, 'text': msg.text}) if msg.type == 'error' else None)
    page.on('pageerror', lambda err: REPORT['runtimeErrors'].append({'case': ACTIVE, 'text': str(err)}))
    page.on('requestfailed', lambda req: REPORT['failedRequests'].append({'case': ACTIVE, 'url': req.url, 'failure': req.failure}))
    return context, page


def go(page, path):
    page.goto(BASE + path, wait_until='networkidle')
    page.locator('#main-content h1').wait_for(state='visible')
    page.evaluate('document.fonts.ready')


def count_cards(page, expected):
    expect(page.locator('.catalog-grid article[data-guitar-id]')).to_have_count(expected)


def model_ids(page):
    return page.locator('.catalog-grid article[data-guitar-id]').evaluate_all('(nodes) => nodes.map(n => n.dataset.guitarId)')


def price(page):
    go(page, '/guitars')
    count_cards(page, 9)
    page.get_by_role('button', name='มากกว่า ฿70k', exact=True).click()
    count_cards(page, 0)
    assert parse_qs(urlparse(page.url).query).get('min') == ['70000'], page.url
    page.go_back(wait_until='networkidle')
    count_cards(page, 9)
    assert 'min' not in parse_qs(urlparse(page.url).query), page.url
    page.go_forward(wait_until='networkidle')
    count_cards(page, 0)
    page.get_by_role('button', name='ล้างตัวกรองทั้งหมด', exact=True).click()
    count_cards(page, 9)
    query = parse_qs(urlparse(page.url).query)
    assert not any(key in query for key in ['min', 'max', 'brand', 'type', 'q']), query
    go(page, '/guitars?max=30000')
    count_cards(page, 0)
    go(page, '/guitars?min=34000&max=34000')
    count_cards(page, 1)
    assert model_ids(page) == [ID]
    go(page, '/guitars?min=70000')
    count_cards(page, 0)
    return {'semantics': 'Unknown prices excluded; bounds remain inclusive and >70k stays above the sole verified 34k price.'}


def filters(page):
    go(page, '/guitars?brand=Yamaha')
    count_cards(page, 9)
    assert all(guitar.startswith('yamaha-') for guitar in model_ids(page))
    assert '20' in page.locator('.catalog-result-count').inner_text()
    page.locator('.catalog-toolbar select').select_option('name')
    expect(page).to_have_url(re.compile(r'[?&]sort=name(?:&|$)'))
    names = page.locator('.catalog-grid article h3').all_text_contents()
    assert page.evaluate('(names) => names.every((n,i) => !i || new Intl.Collator(undefined,{numeric:true,sensitivity:"base"}).compare(names[i-1],n) <= 0)', names), names
    first_page = model_ids(page)
    page.locator('.catalog-pagination').get_by_role('button', name='หน้าถัดไป', exact=True).click()
    expect(page).to_have_url(re.compile(r'[?&]page=2(?:&|$)'))
    second_page = model_ids(page)
    assert len(second_page) == 9 and not set(first_page) & set(second_page)
    page.go_back(wait_until='networkidle')
    assert model_ids(page) == first_page
    page.go_forward(wait_until='networkidle')
    assert model_ids(page) == second_page
    go(page, '/guitars?brand=Yamaha&type=electric&q=612VIIFM')
    count_cards(page, 1)
    assert model_ids(page) == [ID]
    page.locator('#catalog-search').fill('does-not-match-phase-b')
    expect(page.locator('#catalog-search')).to_be_focused()
    count_cards(page, 0)
    page.locator('#catalog-search').fill('612VIIFM')
    count_cards(page, 1)
    assert parse_qs(urlparse(page.url).query).get('brand') == ['Yamaha']
    assert parse_qs(urlparse(page.url).query).get('type') == ['electric']
    return {'brandModels': 20, 'pageSize': 9, 'combination': 'type + brand + search; sort and pagination preserve URL history'}


PAINT = r'''img => {
    const r=img.getBoundingClientRect(),s=getComputedStyle(img);
    const scale=s.transform==='none'?1:new DOMMatrixReadOnly(s.transform).a;
    const fit=Math.min(r.width/scale/img.naturalWidth,r.height/scale/img.naturalHeight);
    const width=img.naturalWidth*fit*scale,height=img.naturalHeight*fit*scale;
    const painted={left:r.left+(r.width-width)/2,top:r.top+(r.height-height)/2,width,height};
    const clipped=[];
    for(let frame=img.parentElement;frame;frame=frame.parentElement){
      const fs=getComputedStyle(frame),f=frame.getBoundingClientRect();
      if(/hidden|clip/.test(fs.overflowX+' '+fs.overflowY)){
        clipped.push({tag:frame.tagName,className:frame.className,
          top:Math.max(0,f.top-painted.top),bottom:Math.max(0,painted.top+height-f.bottom),
          left:Math.max(0,f.left-painted.left),right:Math.max(0,painted.left+width-f.right)});
      }
      if(frame.tagName==='ARTICLE')break;
    }
    return {fit:s.objectFit,transform:s.transform,painted,clipped,naturalWidth:img.naturalWidth};
}'''


def hover(page):
    page.emulate_media(reduced_motion='no-preference')
    measurements = []
    for route in ['/', '/guitars?q=612VIIFM']:
        go(page, route)
        card = page.locator('article[data-guitar-id="' + ID + '"]')
        expect(card).to_be_visible()
        image = card.locator('img').first
        image.evaluate('(img) => img.decode()')
        card.scroll_into_view_if_needed()
        page.mouse.move(1, 1)
        before = image.evaluate(PAINT)
        card.hover()
        page.wait_for_timeout(700)
        after = image.evaluate(PAINT)
        for state, result in [('before', before), ('hover', after)]:
            assert result['naturalWidth'] > 0 and result['fit'] == 'contain', result
            assert result['clipped'], 'No clipping ancestor found: inspect test geometry before claiming a pass'
            for frame in result['clipped']:
                assert max(frame[key] for key in ['top', 'bottom', 'left', 'right']) <= 1, {'route': route, 'state': state, 'frame': frame}
        measurements.append({'route': route, 'before': before, 'hover': after})
    return measurements


CONTRAST = r'''el => {
 const rgba=s=>{const v=s.match(/[\d.]+/g)?.map(Number)||[0,0,0,0];return [v[0],v[1],v[2],v.length>3?v[3]:1]};
 const over=(a,b)=>{const alpha=a[3]+b[3]*(1-a[3]);return [0,1,2].map(i=>(a[i]*a[3]+b[i]*b[3]*(1-a[3]))/(alpha||1)).concat(alpha)};
 const path=[];for(let p=el;p;p=p.parentElement)path.unshift(p);
 let bg=[0,0,0,1];for(const p of path)bg=over(rgba(getComputedStyle(p).backgroundColor),bg);
 const cs=getComputedStyle(el);let opacity=1;for(const p of path)opacity*=parseFloat(getComputedStyle(p).opacity);
 const fg=rgba(cs.color);fg[3]*=opacity;const text=over(fg,bg);
 const lum=c=>c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
 const a=lum(text),b=lum(bg);return {text:el.textContent.trim(),color:cs.color,background:bg,opacity,fontSize:cs.fontSize,contrast:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
}'''


def contrast(page):
    go(page, '/compare?ids=' + ID + ',' + SECOND)
    table = page.locator('.compare-table-scroll')
    expect(table).to_be_visible()
    samples = []
    for locator in [table.get_by_text('เหมือนกัน', exact=True), table.get_by_text('Yamaha', exact=True)]:
        assert locator.count(), 'Expected an equal-value comparison sample'
        for element in locator.all():
            sample = element.evaluate(CONTRAST)
            assert sample['contrast'] >= 4.5, sample
            samples.append(sample)
    return samples


def gallery(page):
    go(page, '/guitars/' + ID)
    main = page.locator('.gallery-main img')
    expect(main).to_have_attribute('src', re.compile('01-black'))
    for color, filename in [('Red', '02-red'), ('Blue / Teal', '03-blue-teal'), ('Black', '01-black')]:
        control = page.get_by_role('radio', name=color, exact=True)
        control.tap() if page.viewport_size['width'] < 1024 else control.click()
        expect(control).to_be_checked()
        expect(main).to_have_attribute('src', re.compile(filename))
        assert main.evaluate('(i) => getComputedStyle(i).objectFit') == 'contain'
    page.locator('.gallery-thumbnails button').last.click()
    expect(main).to_have_attribute('src', re.compile('04-all-colors'))
    page.get_by_role('button', name='เปิดดูรูปขนาดใหญ่', exact=True).click()
    dialog = page.get_by_role('dialog')
    expect(dialog).to_be_visible()
    page.keyboard.press('Escape')
    expect(dialog).to_be_hidden()
    return {'colors': ['Black', 'Red', 'Blue / Teal'], 'overview': True, 'lightboxEscape': True}


def navigation(page):
    go(page, '/guitars/' + ID)
    trigger = page.locator('button[aria-controls="guitar-navigation"]')
    if not trigger.count():
        trigger = page.locator('button[aria-controls="guitar-mega-menu"]')
    assert trigger.count() == 1, 'Desktop Catalog needs an explicit accessible disclosure control'
    trigger.focus()
    page.keyboard.press('Enter')
    expect(trigger).to_have_attribute('aria-expanded', 'true')
    controlled = page.locator('#' + trigger.get_attribute('aria-controls'))
    expect(controlled).to_be_visible()
    page.keyboard.press('Escape')
    expect(trigger).to_have_attribute('aria-expanded', 'false')
    expect(trigger).to_be_focused()
    if page.viewport_size['width'] == 1024:
        trigger.tap()
        expect(trigger).to_have_attribute('aria-expanded', 'true')
        page.keyboard.press('Escape')
        expect(trigger).to_have_attribute('aria-expanded', 'false')
    return {'desktopDisclosure': 'Enter opens, Escape closes and restores focus', 'touch1024': page.viewport_size['width'] == 1024}


def mobile_navigation(page):
    go(page, '/guitars')
    trigger = page.locator('button[aria-controls="mobile-navigation"]')
    trigger.click()
    expect(trigger).to_have_attribute('aria-expanded', 'true')
    panel = page.locator('#mobile-navigation')
    expect(panel).to_be_visible()
    page.keyboard.press('Escape')
    expect(trigger).to_have_attribute('aria-expanded', 'false')
    expect(trigger).to_be_focused()
    filter_trigger = page.locator('.catalog-filter-trigger')
    filter_trigger.click()
    drawer = page.get_by_role('dialog')
    expect(drawer).to_be_visible()
    page.keyboard.press('Tab')
    assert drawer.evaluate('(d) => d.contains(document.activeElement)'), 'Focus escaped the open filter dialog'
    page.keyboard.press('Escape')
    expect(drawer).to_be_hidden()
    expect(filter_trigger).to_be_focused()
    trigger.click()
    expect(panel).to_be_visible()
    expect(panel).not_to_have_attribute('inert', '')
    brand_link = panel.locator('nav a[href="/brands"]')
    brand_link.focus()
    expect(brand_link).to_be_focused()
    page.keyboard.press('Enter')
    expect(page).to_have_url(BASE + '/brands')
    expect(page.locator('main')).to_be_focused()
    return {'mobileDisclosure': True, 'filterKeyboardModal': True, 'keyboardRouteFocus': True}


def focus(page):
    go(page, '/guitars/' + ID)
    page.locator('.site-header').get_by_role('button', name='ค้นหา', exact=True).click()
    expect(page.locator('#hero-search')).to_be_focused()
    go(page, '/guitars')
    page.locator('.site-header').get_by_role('button', name='ค้นหา', exact=True).click()
    expect(page.locator('#catalog-search')).to_be_focused()
    page.locator('#catalog-search').fill('612VIIFM')
    count_cards(page, 1)
    expect(page.locator('#catalog-search')).to_be_focused()
    go(page, '/guitars/' + ID + '#specs')
    expect(page.get_by_role('tab', name='สเปก', exact=True)).to_have_attribute('aria-selected', 'true')
    expect(page.locator('#specs')).to_be_visible()
    return {'headerSearchFromDetailAndCatalog': True, 'queryRetainsInputFocus': True, 'specsAnchorSelectsTab': True}


def wishlist(page):
    go(page, '/guitars/' + ID)
    button = page.locator('.detail-actions button').nth(1)
    button.click()
    expect(button).to_have_attribute('aria-pressed', 'true')
    go(page, '/wishlist')
    expect(page.locator('.wishlist-row')).to_have_count(1)
    expect(page.locator('.wishlist-row [data-wishlist-detail][href="/guitars/' + ID + '"]')).to_have_count(1)
    page.reload(wait_until='networkidle')
    expect(page.locator('.wishlist-row')).to_have_count(1)
    go(page, '/guitars/' + ID)
    button = page.locator('.detail-actions button').nth(1)
    expect(button).to_have_attribute('aria-pressed', 'true')
    button.click()
    go(page, '/wishlist')
    expect(page.locator('.wishlist-row')).to_have_count(0)
    stored = page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))')
    assert stored == [], stored
    return {'crossPagePersistence': True, 'reloadPersistence': True, 'remove': True}


def compare(page):
    go(page, '/compare?ids=' + ','.join([ID, ID, SECOND]))
    expect(page.locator('[data-compare-remove]')).to_have_count(2)
    stored = page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))')
    assert len(stored) == len(set(stored)) == 2, stored
    go(page, '/compare?ids=' + ','.join([ID, SECOND, THIRD, FOURTH]))
    expect(page.locator('[data-compare-remove]')).to_have_count(4)
    expect(page.get_by_role('button', name='ครบ 4 รุ่นแล้ว', exact=True)).to_be_disabled()
    page.locator('[data-compare-remove]').first.click()
    expect(page.locator('[data-compare-remove]')).to_have_count(3)
    page.get_by_role('button', name='เพิ่มกีตาร์', exact=True).click()
    picker = page.get_by_role('dialog')
    expect(picker).to_be_visible()
    picker.locator('input[type="search"]').fill('612VIIFM')
    filtered_rows = picker.locator('.picker-model-row')
    expect(filtered_rows).to_have_count(1)
    expect(filtered_rows).to_contain_text('Pacifica 612VIIFM')
    filtered_rows.click()
    page.get_by_role('button', name='เสร็จสิ้น', exact=True).click()
    expect(page.locator('[data-compare-remove]')).to_have_count(4)
    go(page, '/compare?ids=' + ','.join([ID, SECOND, THIRD, FOURTH, FIFTH]))
    expect(page.locator('[data-compare-remove]')).to_have_count(4)
    stored = page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))')
    assert len(stored) == len(set(stored)) == 4, stored
    page.get_by_role('button', name='ล้างการเปรียบเทียบ', exact=True).click()
    confirmation = page.get_by_role('alertdialog')
    expect(confirmation).to_be_visible()
    confirmation.get_by_role('button').last.click()
    expect(page.locator('[data-compare-remove]')).to_have_count(0)
    return {'duplicateURLNormalized': True, 'twoToFour': True, 'fifthRejected': True, 'removeAndAdd': True, 'clearConfirmed': True}


def select_answer(page, question, value):
    radio = page.locator('input[type="radio"][name="' + question + '"][value="' + value + '"]')
    radio.locator('..').click()
    expect(radio).to_be_checked()


def quiz(page):
    go(page, '/find-my-guitar')
    page.get_by_role('button', name='เริ่มค้นหากีตาร์', exact=True).click()
    expect(page.locator('#quiz-type-title')).to_be_focused()
    select_answer(page, 'type', 'electric')
    page.locator('.quiz-step-actions button[type="submit"]').click()
    expect(page.locator('#quiz-level-title')).to_be_focused()
    select_answer(page, 'level', 'intermediate')
    page.locator('.quiz-step-actions button[type="submit"]').click()
    page.locator('.quiz-step-actions button[type="button"]').click()
    expect(page.locator('#quiz-level-title')).to_be_focused()
    expect(page.locator('input[name="level"][value="intermediate"]')).to_be_checked()
    select_answer(page, 'level', 'beginner')
    page.locator('.quiz-step-actions button[type="submit"]').click()
    for question, value in [('style', 'rock'), ('budget', 'high'), ('priority', 'versatile')]:
        expect(page.locator('#quiz-' + question + '-title')).to_be_focused()
        select_answer(page, question, value)
        page.locator('.quiz-step-actions button[type="submit"]').click()
    expect(page.locator('.quiz-results-page')).to_be_visible()
    expect(page.locator('.quiz-results-page h1')).to_be_focused()
    query = parse_qs(urlparse(page.url).query)
    assert query.get('level') == ['beginner'] and query.get('type') == ['electric'], query
    detail = page.locator('.quiz-results-page a[href^="/guitars/"]').first
    expect(detail).to_be_visible()
    target = detail.get_attribute('href')
    detail.click()
    expect(page).to_have_url(BASE + target)
    expect(page.locator('.detail-actions')).to_be_visible()
    page.go_back(wait_until='networkidle')
    expect(page.locator('.quiz-results-page')).to_be_visible()
    page.go_forward(wait_until='networkidle')
    expect(page.locator('.detail-actions')).to_be_visible()
    return {'fiveSteps': True, 'previousPreservesAnswer': True, 'editedAnswerInResultsURL': True, 'resultDetailAndHistory': True}


def responsive(page):
    measurements = []
    routes = ['/', '/guitars', '/guitars/' + ID, '/brands', '/brands/yamaha',
              '/compare?ids=' + ','.join([ID, SECOND, THIRD, FOURTH]), '/find-my-guitar', '/wishlist']
    for route in routes:
        go(page, route)
        metrics = page.evaluate('''() => ({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
          h1:[...document.querySelectorAll('h1')].filter(e=>e.getBoundingClientRect().width>0).length,
          brokenImages:[...document.images].filter(i=>i.complete&&i.currentSrc&&i.naturalWidth===0).map(i=>i.currentSrc)})''')
        assert metrics['scrollWidth'] <= metrics['viewport'] + 1, {'route': route, **metrics}
        assert metrics['h1'] == 1, {'route': route, **metrics}
        assert not metrics['brokenImages'], {'route': route, **metrics}
        if route.startswith('/compare'):
            region = page.locator('.compare-table-scroll')
            if metrics['viewport'] < 1024:
                assert region.evaluate('(e) => e.scrollWidth > e.clientWidth'), 'Comparison should scroll inside its region'
                region.focus()
                page.keyboard.press('ArrowRight')
                page.wait_for_timeout(150)
                assert region.evaluate('(e) => e.scrollLeft > 0'), 'Focused comparison region did not scroll with the keyboard'
        measurements.append({'path': route, **metrics})
    REPORT['responsive'].extend(measurements)
    return measurements


CASES = {'price': price, 'filters': filters, 'hover': hover, 'contrast': contrast,
         'navigation': navigation, 'focus': focus, 'gallery': gallery, 'wishlist': wishlist,
         'compare': compare, 'quiz': quiz, 'responsive': responsive}
selected = set(filter(None, os.environ.get('FRETLINE_QA_CASES', '').split(',')))
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get('FRETLINE_CHROMIUM', '/usr/bin/chromium'), args=['--no-sandbox'])
        for name, test in CASES.items():
            if selected and name not in selected:
                continue
            viewports = [(1440,1000)]
            if name == 'responsive':
                viewports = [(1440,1000),(1024,768),(768,1024),(390,844),(320,740)]
            elif name == 'gallery':
                viewports = [(1440,1000),(390,844)]
            elif name == 'navigation':
                viewports = [(1440,1000),(1024,768),(390,844)]
            for width, height in viewports:
                ACTIVE = name + '-' + str(width)
                context, page = context_for(browser, width, height, touch=width <= 1024)
                try:
                    result = mobile_navigation(page) if name == 'navigation' and width < 1024 else test(page)
                    REPORT['checks'].append({'case': ACTIVE, 'passed': True, 'details': result})
                    print('PASS ' + ACTIVE, flush=True)
                except Exception:
                    failure = traceback.format_exc()
                    screenshot = OUT / 'failures' / (ACTIVE + '.png')
                    try:
                        page.screenshot(path=str(screenshot), full_page=True)
                    except Exception as error:
                        failure += '\nFailure screenshot unavailable: ' + str(error)
                    REPORT['checks'].append({'case': ACTIVE, 'passed': False, 'failure': failure, 'url': page.url, 'screenshot': str(screenshot.relative_to(OUT))})
                    print('FAIL ' + ACTIVE + '\n' + failure, flush=True)
                finally:
                    context.close()
        browser.close()
except Exception:
    REPORT['harnessFailure'] = traceback.format_exc()
finally:
    REPORT['passed'] = bool(REPORT['checks']) and all(check['passed'] for check in REPORT['checks']) and not REPORT.get('harnessFailure') and not REPORT['consoleErrors'] and not REPORT['runtimeErrors'] and not REPORT['failedRequests']
    (OUT / os.environ.get('FRETLINE_QA_REPORT', 'acceptance.json')).write_text(json.dumps(REPORT, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if REPORT['passed'] else 1)
