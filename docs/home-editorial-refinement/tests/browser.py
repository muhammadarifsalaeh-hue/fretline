"""Production browser checks for the simplified editorial Home.

The unchanged marquee probe retains its previous strict motion/input criteria.
Real iPad Safari remains a separate physical-device review.
"""
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, expect
import argparse, hashlib, json, re, time, traceback

ROOT = Path(__file__).resolve().parents[3]
DIR = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--url', required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--engines', nargs='+', default=['chromium', 'webkit'])
p.add_argument('--viewports', nargs='+', default=['desktop', 'tablet', 'mobile'])
p.add_argument('--cases', nargs='+', default=['composition', 'search', 'navigation', 'reduced', 'carousel', 'routes', 'hero', 'featured'])
args = p.parse_args()
BASE = args.url.rstrip('/')
OUT = args.output
OUT.mkdir(parents=True, exist_ok=True)
VIEWPORTS = {'desktop': (1440, 1000), 'tablet': (768, 1024), 'mobile': (390, 844)}
IDS = ['yamaha-fg820-12', 'martin-d-28', 'yamaha-pacifica-612viifm', 'yamaha-fg800']

def sha(data): return hashlib.sha256(data).hexdigest()
def snapshot():
    return {str(f.relative_to(ROOT)): sha(f.read_bytes()) for folder in ['src', 'dist']
            for f in (ROOT / folder).rglob('*') if f.is_file()}

start = snapshot()
ACTIVE = None
report = {'baseURL': BASE, 'checks': [], 'consoleErrors': [], 'runtimeErrors': [],
          'networkErrors': [], 'failedRequests': [], 'screenshots': [],
          'physicalIPadSafariTested': False, 'nativeWebKitTouchDragAvailable': False,
          'sourceAndBuildSHA256': start}

def check(name, fn, page):
    global ACTIVE
    ACTIVE = name
    try:
        evidence = fn()
        report['checks'].append({'case': name, 'passed': True, 'evidence': evidence})
        print('PASS', name, flush=True)
    except Exception:
        error = traceback.format_exc()
        file = name + '-FAIL.png'
        try: page.screenshot(path=str(OUT / file), full_page=True, animations='disabled')
        except Exception: pass
        report['checks'].append({'case': name, 'passed': False, 'error': error, 'url': page.url, 'screenshot': file})
        print('FAIL', name, error, flush=True)

def go(page, path='/'):
    page.goto(BASE + path, wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    expect(page.locator('main h1')).to_be_visible()

def metrics(page):
    result = page.evaluate('({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll("main h1").length})')
    assert result['scrollWidth'] <= result['viewport'] + 1, result
    assert result['h1'] == 1, result
    return result

def decode(im):
    im.scroll_into_view_if_needed()
    im.evaluate('(i)=>i.decode()')
    data = im.evaluate('(i)=>({src:i.getAttribute("src"),currentSrc:i.currentSrc,width:i.naturalWidth,height:i.naturalHeight,fit:getComputedStyle(i).objectFit,loading:i.loading})')
    assert data['width'] > 0 and data['height'] > 0, data
    assert data['fit'] in ['contain', 'cover'], data
    return data

def viewport_shot(page, selector, name):
    el = page.locator(selector)
    for im in el.locator('img').all():
        if im.is_visible(): decode(im)
    el.evaluate("e=>scrollBy(0,e.getBoundingClientRect().top-document.querySelector('.site-header').getBoundingClientRect().height-12)")
    if selector == '#top': page.evaluate('scrollTo(0,0)')
    page.screenshot(path=str(OUT / name), animations='disabled')
    report['screenshots'].append(name)

def composition(page, engine, viewport):
    go(page)
    assert page.evaluate('scrollY') < 30
    expect(page.locator('main h1')).to_contain_text('ค้นพบ')
    expect(page.locator('main h1')).to_contain_text('เสียงที่เป็นคุณ')
    assert page.locator('.signature-hero-slide').count() == 3
    assert page.locator('.signature-hero-description,.signature-hero-caption,.signature-stats-note,.signature-hero-search ul').count() == 0
    assert page.locator('[data-home-quiz-panel],#find input,#find form,#find [role=progressbar],#compare table,#compare [role=table],#compare [role=switch],.home-compare-preview,[data-home-compare-expand]').count() == 0
    stats = page.locator('.signature-stats-list dd').all_text_contents()
    assert stats == ['200', '10', '4', '4'], stats
    text = page.locator('main').inner_text()
    assert not re.search(r'AI\s*(?:Generated|Edited)|Powered\s+by\s+AI|ออกแบบด้วย\s*AI|เครดิตภาพประกอบ|ภาพประกอบบรรยากาศ|ข้อมูลสำหรับค้นหาและเปรียบเทียบ|ไม่มีระบบซื้อขาย', text, re.I)
    order = page.locator('.premium-home > section,.premium-home > .home-editorial-pair').evaluate_all('(nodes)=>nodes.map(n=>n.id||n.className)')
    assert order[0:3] == ['top','brands','categories'], order
    assert 'home-editorial-pair' in order[3] and order[4] == 'featured', order
    find = page.locator('#find').bounding_box(); compare = page.locator('#compare').bounding_box()
    if page.viewport_size['width'] >= 1024:
        assert abs(find['y']-compare['y'])<=1 and find['x']+find['width'] <= compare['x'], (find,compare)
    else:
        assert find['y']+find['height'] <= compare['y'], (find,compare)
    photos = {}
    for name, selector in [('hero', '#top'), ('find', '#find'), ('compare', '#compare')]:
        images = page.locator(selector).locator('img')
        assert images.count() >= 1, selector
        photos[name] = [decode(im) for im in images.all()]
    cards = page.locator('.signature-category-card')
    assert cards.count() == 4
    for index, kind in enumerate(['electric', 'acoustic', 'classical', 'bass']):
        card = cards.nth(index)
        assert card.get_attribute('href') == '/guitars?type=' + kind
        expect(card.locator('img')).to_have_count(1)
        photos[kind] = decode(card.locator('img'))
        expect(card.locator('img')).to_have_css('object-fit', 'contain')
        expect(card.locator('img')).to_have_css('opacity', '1')
        assert card.locator('h3').inner_text().strip()
        assert re.search(r'\d', card.locator('p').inner_text())
    credit_link = page.locator('.site-footer a[href="/image-credits"]')
    expect(credit_link).to_have_count(1)
    resources = page.evaluate('performance.getEntriesByType("resource").map(r=>new URL(r.name).pathname)')
    assert not any('practice-three' in r or r.endswith('.glb') for r in resources)
    for name, selector in [('hero', '#top'), ('brands', '#brands'), ('categories', '#categories'), ('find', '#find'), ('compare', '#compare'), ('featured', '#featured')]:
        viewport_shot(page, selector, f'{engine}-{viewport}-{name}.png')
    page.evaluate('scrollTo(0,0)')
    page.screenshot(path=str(OUT / f'{engine}-{viewport}-full.png'), full_page=True, animations='disabled')
    report['screenshots'].append(f'{engine}-{viewport}-full.png')
    return {'statistics': stats, 'noInlineQuizOrComparison': True, 'removedHomeCopy': True, 'photographs': photos,
            'footerLicenseIndexRetained': True, 'noPracticeModelLoaded': True, **metrics(page)}

def search(page):
    go(page)
    field = page.locator('#hero-search')
    field.fill('FG820-12')
    expect(page.locator('#search-results [role=option]')).not_to_have_count(0)
    expect(field).to_have_attribute('aria-expanded', 'true')
    page.keyboard.press('Escape')
    expect(field).to_have_attribute('aria-expanded', 'false')
    page.locator('#search button').first.click()
    expect(page).to_have_url(re.compile(r'/guitars\?q=FG820-12$'))
    expect(page.locator('main')).to_contain_text('FG820-12')
    go(page)
    field = page.locator('#hero-search')
    field.fill('FG820-12')
    field.press('ArrowDown')
    expect(field).to_have_attribute('aria-activedescendant', 'search-option-0')
    target = page.locator('#search-option-0').inner_text()
    field.press('Enter')
    expect(page).to_have_url(re.compile(r'/guitars/yamaha-fg820-12$'))
    expect(page.locator('main h1')).to_contain_text('FG820-12')
    go(page)
    page.locator('#search button').first.click()
    expect(page).to_have_url(BASE + '/guitars')
    return {'searchSubmitCatalogQuery': True, 'keyboardAutocompleteActualDetail': target, 'emptySearchCatalog': True}

def navigation(page):
    go(page)
    link = page.locator('#find a[href="/find-my-guitar"]')
    expect(link).to_have_count(1)
    expect(link).to_have_text(re.compile('เริ่มค้นหากีตาร์'))
    link.click()
    expect(page).to_have_url(BASE + '/find-my-guitar')
    expect(page.locator('.premium-quiz')).to_be_visible()
    page.get_by_role('button', name='เริ่มค้นหากีตาร์', exact=True).click()
    expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow', '1')
    assert page.locator('input[name=type]').count() == 5
    go(page)
    page.locator('#compare a[href="/compare"]').click()
    expect(page).to_have_url(re.compile(r'/compare(?:\?ids=)?$'))
    expect(page.locator('.premium-compare')).to_be_visible()
    assert page.locator('[data-compare-card]').count() == 0
    # Home must not manufacture an example selection, and must preserve real saved choices.
    assert page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))') == []
    go(page,'/compare?ids='+','.join(IDS))
    expect(page.locator('[data-compare-card]')).to_have_count(4)
    go(page)
    page.locator('#compare a[href="/compare"]').click()
    expect(page.locator('[data-compare-card]')).to_have_count(4)
    chosen = page.locator('[data-compare-card]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.compareCard)')
    assert chosen == IDS, chosen
    page.evaluate('localStorage.setItem("fretline:compare","[]")')
    return {'findOpensOriginalQuizFirstStep': True, 'compareEmptyStateRoute': True, 'allFourSavedChoicesPreserved': chosen}

def reduced(page):
    go(page)
    rail = page.locator('[data-marquee-viewport]')
    rail.scroll_into_view_if_needed()
    expect(rail).to_have_attribute('data-marquee-motion', 'reduced')
    before = rail.evaluate('(e)=>e.scrollLeft')
    page.wait_for_timeout(350)
    assert abs(rail.evaluate('(e)=>e.scrollLeft') - before) <= 1
    assert rail.locator('[data-marquee-clone]:visible').count() == 0
    assert page.locator('#brands button').count() == 0
    last = rail.locator('[data-marquee-primary] a').last
    last.focus()
    expect(last).to_be_focused()
    link, bounds = last.bounding_box(), rail.bounding_box()
    assert link['x'] >= bounds['x'] - 1 and link['x'] + link['width'] <= bounds['x'] + bounds['width'] + 1, (link, bounds)
    last.press('Enter')
    expect(page).to_have_url(re.compile('/guitars\\?brand='))
    return {'motionDisabled': True, 'clonesHidden': True, 'keyboardBrandVisibleAndNavigates': True}

def routes(page):
    actual = []
    for kind in ['electric', 'acoustic', 'classical', 'bass']:
        go(page)
        card = page.locator('.signature-category-card[href="/guitars?type=' + kind + '"]')
        card.click()
        assert parse_qs(urlparse(page.url).query).get('type') == [kind]
        expect(page.locator('main h1')).to_be_visible()
        actual.append({'category': kind, 'url': page.url})
    go(page)
    links = page.locator('[data-marquee-primary] a').evaluate_all('(nodes)=>nodes.map(n=>({id:n.dataset.brandId,href:n.getAttribute("href")}))')
    assert len({item['id'] for item in links}) == 10
    for item in links:
        go(page)
        link = page.locator('[data-marquee-primary] a[data-brand-id="' + item['id'] + '"]')
        link.focus()
        link.press('Enter')
        expect(page).to_have_url(BASE + item['href'])
        expect(page.locator('main h1')).to_be_visible()
    responsive = []
    for width, height in [(320, 740), (834, 1194), (1024, 768), (1194, 834)]:
        page.set_viewport_size({'width': width, 'height': height})
        go(page)
        for selector in ['#top', '#categories', '#find', '#compare']:
            page.locator(selector).scroll_into_view_if_needed()
            responsive.append({'section': selector, **metrics(page)})
    page.set_viewport_size({'width':1440,'height':1000})
    return {'fourActualCategoryRoutes': actual, 'tenActualBrandRoutes': links, 'responsive': responsive}


def hero(page, context, engine, viewport):
    page.add_init_script("""window.__heroChanges=[];new MutationObserver(()=>{
      const hero=document.querySelector('#top');if(!hero)return;const index=hero.dataset.heroSlideIndex;
      if(index!==undefined&&index!==window.__heroChanges.at(-1)?.index)__heroChanges.push({index,time:performance.now()});
    }).observe(document,{attributes:true,subtree:true,childList:true});""")
    go(page)
    top = page.locator('#top')
    assert top.locator('.signature-hero-slide').count()==3
    page.wait_for_function('window.__heroChanges.length>=4',timeout=22000)
    changes=page.evaluate('__heroChanges.slice(0,4)')
    assert [x['index'] for x in changes]==['0','1','2','0'],changes
    intervals=[b['time']-a['time'] for a,b in zip(changes,changes[1:])]
    assert all(5600<=delta<=7000 for delta in intervals),intervals
    expect(top).to_have_attribute('data-hero-slide-index','0')
    bounds=top.bounding_box(); x=bounds['x']+bounds['width']*.82; y=bounds['y']+min(180,bounds['height']*.4)
    assert page.evaluate('([x,y])=>!!document.elementFromPoint(x,y)?.closest("#top")',[x,y])
    page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-150,y,steps=12);page.mouse.up()
    expect(top).to_have_attribute('data-hero-slide-index','1')
    assert page.url==BASE+'/'
    page.mouse.move(x-150,y);page.mouse.down();page.mouse.move(x,y,steps=12);page.mouse.up()
    expect(top).to_have_attribute('data-hero-slide-index','0')
    # Native controls must never become drag handles.
    field=page.locator('#hero-search');field.fill('FG820-12');field.press('Escape')
    expect(top).to_have_attribute('data-hero-slide-index','0')
    native=False
    if engine=='chromium' and viewport!='desktop':
        session=context.new_cdp_session(page)
        session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':1}]})
        for step in range(1,9):
            session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x-step*19,'y':y,'id':1}]});time.sleep(.02)
        session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
        expect(top).to_have_attribute('data-hero-slide-index','1')
        session.detach();native=True
    page.emulate_media(reduced_motion='reduce');page.reload(wait_until='networkidle')
    expect(top).to_have_attribute('data-hero-slide-index','0');page.wait_for_timeout(6300)
    expect(top).to_have_attribute('data-hero-slide-index','0')
    page.emulate_media(reduced_motion='no-preference')
    return {'threeRealPhotos':True,'automatic6000msCycle0120':True,'actualIntervalsMs':intervals,'mouseSwipeBothDirections':True,'searchInputExcludedFromDrag':True,'nativeChromiumTouch':native,'reducedMotionStatic':True,'physicalIPadTested':False}

def trusted_price(g):
    source=g.get('source') or {}; price=g.get('price'); ps=g.get('priceSource') or {}
    backed=g.get('dataStatus') in ['partial','verified'] and source.get('url','').startswith(('https://','http://')) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}',source.get('verifiedOn','')))
    fields=source.get('fields')
    supported=not isinstance(fields,list) or 'price' in fields
    sourced=not isinstance(fields,list) or (ps.get('currency')=='THB' and ps.get('url','').startswith(('https://','http://')) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}',ps.get('verifiedOn',''))))
    return price if backed and supported and sourced and isinstance(price,(int,float)) and price>0 else None

def featured(page,context,engine,viewport):
    catalog=json.loads((DIR/'catalog-fixture.json').read_text());byid={g['id']:g for g in catalog}
    go(page);region=page.locator('#featured');region.scroll_into_view_if_needed()
    tabs=region.get_by_role('tab');assert tabs.count()==4
    expected_tabs=['featured-tab-popular','featured-tab-new','featured-tab-price-desc','featured-tab-price-asc']
    assert tabs.evaluate_all('(nodes)=>nodes.map(n=>n.id)')==expected_tabs
    ids=lambda:region.locator('article[data-guitar-id]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)')
    prefix=['yamaha-pacifica-612viifm','martin-d-28','yamaha-fg820-12']
    popular=prefix+[g['id'] for g in catalog if g.get('featured') and g['id'] not in prefix]
    assert ids()==popular
    evidence={}
    for tab in ['new','price-desc','price-asc']:
        page.locator('#featured-tab-'+tab).click();expect(page.locator('#featured-tab-'+tab)).to_have_attribute('aria-selected','true')
        actual=ids()
        if tab=='new':
            expected=[g['id'] for g in sorted([g for g in catalog if (g.get('intake') or {}).get('batch')],key=lambda g:g['intake']['batch'],reverse=True)]
        else:
            expected=[g['id'] for g in sorted(catalog,key=lambda g: (trusted_price(g) is None, (trusted_price(g) or 0)*(1 if tab=='price-asc' else -1)))]
        assert actual==expected,(tab,actual[:10],expected[:10]);evidence[tab]={'count':len(actual),'first10':actual[:10],'knownPrices':sum(trusted_price(byid[gid]) is not None for gid in actual)}
        if tab.startswith('price'):
            missing_started=False
            for gid in actual:
                if trusted_price(byid[gid]) is None:missing_started=True
                else:assert not missing_started,'Unconfirmed prices must remain at end'
    # Keyboard tab navigation preserves roving focus.
    page.locator('#featured-tab-price-asc').focus();page.keyboard.press('Home');expect(page.locator('#featured-tab-popular')).to_be_focused();expect(page.locator('#featured-tab-popular')).to_have_attribute('aria-selected','true')
    first=region.locator('article[data-guitar-id]').first;first.hover()
    wish=first.get_by_role('button').nth(0);wish.focus();wish.click();expect(wish).to_have_attribute('aria-pressed','true')
    saved=page.evaluate('JSON.parse(localStorage.getItem("fretline:wishlist"))');assert prefix[0] in saved
    wish.click();expect(wish).to_have_attribute('aria-pressed','false')
    track=page.locator('#featured-models');track.evaluate('(e)=>e.scrollLeft=0');before=track.evaluate('(e)=>({left:e.scrollLeft,width:e.clientWidth,scroll:e.scrollWidth})')
    assert before['scroll']>before['width'],before
    slider_mode='arrow-buttons'
    if viewport=='mobile':
        slider_mode='native-touch' if engine=='chromium' else 'native-wheel'
        track.scroll_into_view_if_needed();bounds=track.bounding_box();x=bounds['x']+bounds['width']*.8;y=bounds['y']+90
        if engine=='chromium':
            session=context.new_cdp_session(page);session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':1}]})
            for step in range(1,9):
                session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x-step*18,'y':y,'id':1}]});time.sleep(.02)
            session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});session.detach()
        else:
            page.mouse.move(x,y);page.mouse.wheel(180,0)
        page.wait_for_function('e=>e.scrollLeft>20',arg=track.element_handle(),timeout=2000)
        assert page.url==BASE+'/'
        moved=track.evaluate('(e)=>e.scrollLeft')
    else:
        next_button=region.locator('.signature-collection-arrow').nth(1);expect(next_button).to_be_enabled();next_button.click();page.wait_for_timeout(300)
        moved=track.evaluate('(e)=>e.scrollLeft');assert moved>before['left']+20,(before,moved)
        region.locator('.signature-collection-arrow').first.click();page.wait_for_timeout(300);assert track.evaluate('(e)=>e.scrollLeft')<moved
    viewport_shot(page,'#featured',f'{engine}-{viewport}-featured-interactions.png')
    return {'originalFeaturedModelsRetained':popular,'tabs':evidence,'unconfirmedPricesLast':True,'wishlistToggleActualStorage':True,'keyboardTabs':True,'sliderInput':slider_mode,'sliderPixels':moved,**metrics(page)}

# The function is copied byte-for-byte from the previous accepted production test.
exec((DIR / 'marquee-probe.py').read_text())

with sync_playwright() as p:
    for engine in args.engines:
        browser = None
        try:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) if engine == 'chromium' else p.webkit.launch()
            report.setdefault('browserVersions', {})[engine] = browser.version
            for viewport in args.viewports:
                width, height = VIEWPORTS[viewport]
                for motion in ['reduce', 'no-preference']:
                    context = browser.new_context(viewport={'width': width, 'height': height}, has_touch=width < 1024, reduced_motion=motion)
                    page = context.new_page()
                    page.on('console', lambda m: report['consoleErrors'].append({'case': ACTIVE, 'text': m.text}) if m.type == 'error' else None)
                    page.on('pageerror', lambda e: report['runtimeErrors'].append({'case': ACTIVE, 'text': str(e)}))
                    page.on('requestfailed', lambda r: report['failedRequests'].append({'case': ACTIVE, 'url': r.url, 'failure': r.failure}))
                    page.on('response', lambda r: report['networkErrors'].append({'case': ACTIVE, 'url': r.url, 'status': r.status}) if r.status >= 400 else None)
                    if motion == 'reduce':
                        if 'composition' in args.cases: check(f'{engine}-{viewport}-composition', lambda: composition(page, engine, viewport), page)
                        if 'search' in args.cases: check(f'{engine}-{viewport}-search', lambda: search(page), page)
                        if 'navigation' in args.cases: check(f'{engine}-{viewport}-cta-and-saved-comparison', lambda: navigation(page), page)
                        if 'reduced' in args.cases: check(f'{engine}-{viewport}-reduced-keyboard', lambda: reduced(page), page)
                        if 'featured' in args.cases: check(f'{engine}-{viewport}-featured-tabs-actions-slider', lambda: featured(page,context,engine,viewport), page)
                        if viewport == 'desktop' and 'routes' in args.cases: check(f'{engine}-{viewport}-all-routes-and-responsive', lambda: routes(page), page)
                    else:
                        if 'hero' in args.cases: check(f'{engine}-{viewport}-hero-slideshow', lambda: hero(page,context,engine,viewport), page)
                        if 'carousel' in args.cases: check(f'{engine}-{viewport}-marquee-motion-input-loop', lambda: carousel(page, context, engine, viewport), page)
                    context.close()
        except Exception:
            report.setdefault('harnessErrors', []).append({'engine': engine, 'error': traceback.format_exc()})
            print('HARNESSFAIL', engine, report['harnessErrors'][-1]['error'], flush=True)
        finally:
            if browser: browser.close()

report['sourceAndBuildUnchangedDuringRun'] = start == snapshot()
report['passed'] = bool(report['checks']) and all(c['passed'] for c in report['checks']) and report['sourceAndBuildUnchangedDuringRun'] and not any(report.get(key) for key in ['consoleErrors', 'runtimeErrors', 'networkErrors', 'failedRequests', 'harnessErrors'])
(OUT / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('RESULT', report['passed'], sum(c['passed'] for c in report['checks']), len(report['checks']), flush=True)
raise SystemExit(not report['passed'])
