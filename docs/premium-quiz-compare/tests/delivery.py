"""Capture the shipped UI and measure actual browser image/layout behavior.

These are localhost production observations, not Lighthouse or iPad certification.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/premium-quiz-compare/screenshots'
OUT.mkdir(exist_ok=True)
BASE = 'http://127.0.0.1:5451'
IDS = 'yamaha-pacifica-612viifm,yamaha-fg820-12,martin-d-28'
report = {'physicalIPadSafariTested': False, 'checks': [], 'errors': [], 'measurements': []}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for label, width, height in [('desktop', 1440, 1000), ('tablet', 768, 1024), ('mobile', 390, 844)]:
        context = browser.new_context(viewport={'width': width, 'height': height}, has_touch=width < 1024, reduced_motion='reduce')
        context.add_init_script("""window.__layoutShifts=[];new PerformanceObserver(list=>{
          for(const e of list.getEntries())if(!e.hadRecentInput)window.__layoutShifts.push(e.value);
        }).observe({type:'layout-shift',buffered:true});""")
        page = context.new_page()
        page.on('pageerror', lambda e: report['errors'].append(str(e)))
        page.on('console', lambda m: report['errors'].append(m.text) if m.type == 'error' else None)
        for name, route in [('quiz', '/find-my-guitar'), ('compare', '/compare?ids=' + IDS)]:
            page.goto(BASE + route, wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            for im in page.locator('main img').all():
                im.scroll_into_view_if_needed()
                im.evaluate('(i)=>i.decode()')
                # Editorial mobile hero is deliberately dimmed; product fade-ins
                # must finish at full opacity before capturing model evidence.
                editorial_hero = im.evaluate('(i)=>Boolean(i.closest(".pc-hero__photograph"))')
                expect(im).to_have_css('opacity', '0.72' if editorial_hero and width < 600 else '1')
            # Return to the actual default viewport; retain all fixed navigation.
            page.evaluate('scrollTo(0,0)')
            page.screenshot(path=str(OUT / f'{name}-{label}-hero.png'), animations='disabled')
            content = page.locator('.quiz-studio-panel' if name == 'quiz' else '.pc-workspace')
            content.scroll_into_view_if_needed()
            content.screenshot(path=str(OUT / f'{name}-{label}-workspace.png'), animations='disabled')
            page.evaluate('scrollTo(0,0)')
            measurements = page.evaluate("""()=>({
              viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
              cls:window.__layoutShifts.reduce((a,b)=>a+b,0),
              navigation:performance.getEntriesByType('navigation').map(n=>({domContentLoadedMs:n.domContentLoadedEventEnd,loadMs:n.loadEventEnd})),
              resources:performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,bytes:r.encodedBodySize,durationMs:r.duration})),
              images:[...document.querySelectorAll('main img')].map(i=>({src:new URL(i.currentSrc).pathname,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,width:i.width,height:i.height,fit:getComputedStyle(i).objectFit})),
              breadcrumbTop:document.querySelector('main nav').getBoundingClientRect().top,
              headerBottom:document.querySelector('.site-header').getBoundingClientRect().bottom
            })""")
            assert measurements['scrollWidth'] <= width + 1, measurements
            assert measurements['breadcrumbTop'] >= measurements['headerBottom'], measurements
            assert not any('practice-three' in r['name'] or r['name'].endswith('.glb') for r in measurements['resources']), 'Unrelated 3D must stay lazy'
            assert all(i['naturalWidth'] > 0 and i['naturalHeight'] > 0 for i in measurements['images'])
            report['measurements'].append({'page': name, 'viewport': label, **measurements})
            if name == 'quiz':
                page.get_by_role('button', name='เริ่มค้นหากีตาร์', exact=True).click()
                radio = page.locator('input[name="type"][value="electric"]')
                radio.focus()
                page.keyboard.press('Space')
                expect(radio).to_be_checked()
                focus = radio.locator('..').locator('.quiz-option-focus')
                assert focus.evaluate('(e)=>getComputedStyle(e).outlineStyle') != 'none'
                duration = page.locator('.quiz-question').evaluate('(e)=>getComputedStyle(e).animationDuration')
                assert all(float(v.strip().removesuffix('s')) <= .001 for v in duration.split(',')), duration
                report['checks'].append({'page': name, 'viewport': label, 'radioKeyboardFocusAndSelection': True, 'reducedMotionAnimationDuration': duration})
            else:
                credit = page.locator('.pc-photo-credits')
                credit.click()
                expect(page).to_have_url(BASE + '/image-credits#discovery-photography')
                section = page.locator('#discovery-photography')
                expect(section).to_be_visible()
                assert section.locator('img').count() == 5
                assert section.locator('a[href="https://unsplash.com/license"]').count() == 5
                report['checks'].append({'page': name, 'viewport': label, 'realCreditsRouteAndAllFiveLicenses': True})
        context.close()
    browser.close()

report['passed'] = len(report['checks']) == 6 and not report['errors']
(OUT / 'delivery-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Delivery browser checks:', report['passed'], len(report['checks']))
assert report['passed'], report
