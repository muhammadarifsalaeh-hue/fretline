"""Final production-image checks; no product changes, uploads or database writes."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json
import sys
import traceback

OUT = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:4193'
failure_only = '--failure-only' in sys.argv
report = {'checks': [], 'engine': 'Chromium', 'databaseWrites': 0,
          'physicalIPadSafariTested': False, 'consoleErrors': [], 'runtimeErrors': []}


def check(name, fn):
    if failure_only and name != 'controlled-image-failure-and-layout-stability':
        return
    try:
        evidence = fn()
        report['checks'].append({'name': name, 'passed': True, 'evidence': evidence})
        print('PASS', name, flush=True)
    except Exception:
        report['checks'].append({'name': name, 'passed': False, 'error': traceback.format_exc()})
        print('FAIL', name, traceback.format_exc(), flush=True)


def go(page, route):
    assert page.goto(BASE + route, wait_until='domcontentloaded').status == 200
    expect(page.locator('main h1')).to_be_visible()
    page.evaluate('document.fonts.ready')


def geometry(locator):
    return locator.evaluate('''e=>{const r=e.getBoundingClientRect();return {w:r.width,h:r.height,bg:getComputedStyle(e).backgroundColor}}''')


def square(info):
    assert info['w'] >= 32 and info['h'] >= 32 and abs(info['w'] - info['h']) <= 1.5 and info['bg'] == 'rgb(0, 0, 0)', info


def frames(page):
    entries = []
    for frame in page.locator('main [data-product-image-slot]').all():
        if frame.is_visible():
            info = geometry(frame)
            square(info)
            entries.append(info)
    assert entries
    for img in page.locator('main .guitar-image-frame>img').all():
        assert img.evaluate("i=>{const a=i.getBoundingClientRect(),b=i.parentElement.getBoundingClientRect();return a.width<=b.width+1&&a.height<=b.height+1&&a.left>=b.left-1&&a.top>=b.top-1&&a.right<=b.right+1&&a.bottom<=b.bottom+1}"), 'Product image exceeds its container'
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    return entries


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for device, width, height in [('desktop',1440,1000),('landscape',1194,834),('portrait',768,1024),('mobile',390,844)]:
        context = browser.new_context(viewport={'width':width,'height':height}, has_touch=device!='desktop', reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda e: report['runtimeErrors'].append(str(e)))
        page.on('console', lambda m: report['consoleErrors'].append(m.text) if m.type=='error' else None)

        def capture():
            go(page, '/guitars?brand=Yamaha')
            cards = page.locator('.catalog-grid article')
            expect(cards).to_have_count(9)
            data = frames(page)
            for img in page.locator('.catalog-grid img').all():
                img.scroll_into_view_if_needed()
                img.evaluate('i=>i.decode()')
            page.locator('.catalog-grid').screenshot(path=str(OUT/'screenshots'/f'after-{device}-catalog.png'),animations='disabled')
            cards.first.screenshot(path=str(OUT/'screenshots'/f'after-{device}-first-card.png'),animations='disabled')
            go(page,'/guitars/yamaha-fg800')
            page.locator('.gallery-main img').evaluate('i=>i.decode()')
            square(geometry(page.locator('.gallery-main')))
            page.locator('.guitar-gallery').screenshot(path=str(OUT/'screenshots'/f'after-{device}-detail.png'),animations='disabled')
            return {'catalogFrames':data,'detailFrame':geometry(page.locator('.gallery-main'))}
        check(device+'-matching-before-after-captures',capture)

        def lightbox():
            img=page.locator('.gallery-main img')
            page.locator('.gallery-main').hover()
            assert img.evaluate("i=>getComputedStyle(i).transform==='none'")
            page.get_by_role('button',name='เปิดดูรูปขนาดใหญ่',exact=True).click()
            dialog=page.get_by_role('dialog')
            expect(dialog).to_be_visible()
            root=dialog.locator('.lightbox-product-image')
            square(geometry(root))
            box=root.bounding_box()
            assert box['y']>=0 and box['y']+box['height']<=height and box['x']>=0 and box['x']+box['width']<=width,box
            page.keyboard.press('ArrowRight')
            expect(dialog.locator('.lightbox-thumbnails button[aria-current="true"]')).to_have_count(1)
            page.keyboard.press('Escape')
            expect(dialog).to_have_count(0)
            return {'containedSquareInsideViewport':box,'noAutomaticHoverZoom':True,'keyboardNavigation':True}
        check(device+'-lightbox-and-no-cropping',lightbox)

        def missing():
            go(page,'/guitars/yamaha-fgx830c')
            expect(page.locator('.gallery-main .image-placeholder')).to_be_visible()
            assert page.locator('.gallery-main img,.gallery-main svg').count()==0
            info=geometry(page.locator('.gallery-main'))
            square(info)
            return {'blackSquare':info,'wrongModelArt':False,'brokenImageElement':False}
        check(device+'-missing-model-placeholder',missing)

        if device=='desktop':
            def categories():
                counts={}
                for kind,total in [('electric',90),('acoustic',73),('classical',20),('bass',17)]:
                    go(page,'/guitars?type='+kind)
                    expect(page.locator('.catalog-result-count')).to_contain_text(str(total))
                    frames(page)
                    if kind in ['classical','bass']:
                        assert page.locator('.catalog-grid .image-placeholder').count()>0
                        assert page.locator('.catalog-grid .image-placeholder svg,.catalog-grid .image-placeholder img').count()==0
                    counts[kind]=total
                return counts
            check('four-category-filters-and-true-placeholders',categories)

            def loading():
                go(page,'/guitars?brand=Yamaha')
                imgs=page.locator('.catalog-grid img').evaluate_all("es=>es.map(i=>({loading:i.loading,priority:i.getAttribute('fetchpriority'),sizes:i.sizes,srcset:i.srcset}))")
                assert len(imgs)==9,imgs
                assert all(i['loading']=='eager' and i['priority']=='high' for i in imgs[:3])
                assert all(i['loading']=='lazy' for i in imgs[3:])
                assert all(i['sizes'] for i in imgs)
                return {'pageImageElements':len(imgs),'priorityImages':3,'remainingLazyImages':6,'responsiveSizes':True,'doesNotRender200FullImages':True}
            check('lazy-loading-and-page-size',loading)
        context.close()

    def failed_image():
        # Deliberate single image failure, isolated from the zero-error regression.
        context=browser.new_context(viewport={'width':768,'height':1024})
        page=context.new_page()
        go(page,'/guitars/yamaha-fg820-12')
        page.locator('.gallery-main img').evaluate('i=>i.decode()')
        source=page.locator('.gallery-main img').evaluate('i=>i.currentSrc')
        before=geometry(page.locator('.gallery-main'))
        requested=[]
        def deny(route):
            requested.append(route.request.url)
            route.abort('failed')
        page.route(source,deny)
        page.reload(wait_until='domcontentloaded')
        expect(page.locator('.gallery-main .image-placeholder')).to_be_visible()
        page.evaluate('document.fonts.ready')
        after=geometry(page.locator('.gallery-main'))
        assert before==after,(before,after)
        assert requested, 'The responsive image failure must actually be injected'
        # Existing gallery control SVGs (arrows/expand) remain functional.
        assert page.locator('.gallery-main .guitar-image-frame img,.gallery-main .image-placeholder svg').count()==0
        context.close()
        return {'inducedImageNetworkFailure':True,'squareFrameStable':True,'before':before,'after':after,'noBrokenImageIcon':True}
    check('controlled-image-failure-and-layout-stability',failed_image)
    browser.close()

report['passed']=all(c['passed'] for c in report['checks']) and not report['runtimeErrors'] and not report['consoleErrors']
filename = 'final-image-failure-recheck.json' if failure_only else 'final-image-browser.json'
(OUT/'tests'/filename).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(report['checks'])}))
raise SystemExit(0 if report['passed'] else 1)
