"""Phase 9: all detail routes, checked fields, licensed photo and deliberate fallback.

FRETLINE_QA_URL=http://127.0.0.1:4199 python docs/qa-phase9/browser-batch.py
Uses the environment's Python Playwright and Chromium; no application dependency.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json, os, re, traceback

OUT = Path(__file__).resolve().parent
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:4199')
records = json.loads((OUT / 'audit-after.json').read_text())
evidence = {item['id']: item for item in json.loads((OUT / 'field-evidence.json').read_text())}
rights = json.loads((OUT.parent.parent / 'src/data/catalog/imageRights.json').read_text())
report = {'browser': 'Chromium on Linux, not physical iPad/Safari', 'routes': [], 'checks': [],
          'page_errors': [], 'console_errors': [], 'failed_requests': [], 'expected_faults': []}

def check(name, condition=True):
    report['checks'].append({'name': name, 'passed': bool(condition)})
    print(name, bool(condition), flush=True)
    assert condition, name

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page.on('pageerror', lambda e: report['page_errors'].append(str(e)))
        page.on('console', lambda m: report['console_errors'].append(m.text) if m.type == 'error' else None)
        page.on('requestfailed', lambda r: report['failed_requests'].append({'url': r.url, 'failure': r.failure}))
        for index, guitar in enumerate(records):
            response = page.goto(BASE + '/guitars/' + guitar['id'], wait_until='load')
            expect(page.locator('.detail-summary h1')).to_have_text(guitar['name'])
            expect(page.locator('.detail-summary')).to_contain_text(guitar['brand'])
            assert response.status == 200 and page.locator('.archive-notice').count() == 0
            if guitar['id'] in evidence:
                # Inspect the exact published text, not just a successful route.
                page.get_by_role('tab').nth(1).click()
                table = page.locator('.spec-table:visible')
                expect(table).to_be_visible()
                text = table.inner_text()
                for key in ['body', 'neck', 'fretboard', 'pickups', 'bridge', 'controls']:
                    if guitar['specs'][key] is not None:
                        assert guitar['specs'][key] in text, guitar['id'] + '/' + key
                scope = page.locator('#specs .data-status-note')
                expect(scope).to_contain_text('2026-10-20')
                assert scope.locator('a').first.get_attribute('href') == guitar['source']['url']
            report['routes'].append({'id': guitar['id'], 'checkedSpecs': guitar['id'] in evidence, 'passed': True})
            if (index + 1) % 25 == 0: print(f'{index + 1}/200 detail routes checked', flush=True)
        check('All 200 detail routes resolve; all 20 batch specification tables match the reviewed facts', len(report['routes']) == 200)

        page.goto(BASE + '/guitars/martin-d-28', wait_until='networkidle')
        image = page.locator('.gallery-main img')
        expect(image).to_be_visible()
        page.wait_for_function('() => {const i=document.querySelector(".gallery-main img");return i && i.complete && i.naturalWidth>0}')
        check('New D-28 image loads with exact intrinsic dimensions', image.get_attribute('width') == '1200' and image.get_attribute('height') == '1594')
        check('New gallery image uses responsive sources and eager priority', all(str(n) + 'w' in image.get_attribute('srcset') for n in [480,960,1200]) and image.get_attribute('loading') == 'eager')
        attribution = page.locator('.guitar-gallery > .image-attribution')
        expect(attribution).to_contain_text('2018')
        expect(attribution).to_contain_text('Golden Era')
        check('Attribution visibly distinguishes the 2018 owner photo from current GE specifications', attribution.locator('a').first.get_attribute('href') == rights['martin-d-28'][0]['sourceUrl'])
        check('CC BY-SA license is linked beside the photo', attribution.locator('a').nth(1).get_attribute('href') == rights['martin-d-28'][0]['licenseUrl'])
        opener = page.locator('.gallery-main').get_by_role('button', name='เปิดดูรูปขนาดใหญ่', exact=True)
        opener.focus(); page.keyboard.press('Enter')
        expect(page.get_by_role('dialog')).to_be_visible()
        expect(page.get_by_role('dialog').locator('.image-attribution')).to_contain_text('IchiroNakagawa')
        page.keyboard.press('Escape')
        check('New photo lightbox supports keyboard open/close and restores focus', opener.evaluate('(e)=>e===document.activeElement'))

        page.goto(BASE + '/guitars?q=D-28&brand=Martin', wait_until='networkidle')
        card = page.locator('article[data-guitar-id="martin-d-28"]')
        expect(card).to_be_visible()
        check('Catalog uses lazy loading for the new licensed image', card.locator('img').get_attribute('loading') == 'lazy')
        card.get_by_role('button', name=re.compile('^บันทึก .*ในรายการโปรด')).click()
        card.get_by_role('button', name=re.compile('^เพิ่ม .*ในการเปรียบเทียบ')).click()
        page.goto(BASE + '/wishlist', wait_until='networkidle')
        expect(page.locator('.wishlist-row')).to_have_count(1)
        check('New photo and original model ID work in Wishlist', page.locator('.wishlist-row img').count() == 1)
        page.goto(BASE + '/compare?ids=martin-d-28,cordoba-c5,prs-se-mccarty-594-singlecut,ibanez-sr300e', wait_until='networkidle')
        table = page.get_by_role('table', name='ตารางเปรียบเทียบสเปกกีตาร์')
        expect(table).to_contain_text('2 volume, 2 push/pull tone controls, 3-way toggle on upper bout')
        expect(table).to_contain_text('GE Modified Low Oval')
        check('Four-model Compare displays checked specs and the licensed D-28 photo', page.locator('.compare-table-scroll img').count() == 1)
        page.goto(BASE + '/image-credits', wait_until='networkidle')
        expect(page.locator('.image-credits-page')).to_contain_text('IchiroNakagawa')
        expect(page.locator('.image-credits-page')).to_contain_text('Peternick2468')
        check('Image credits retain both photographers', page.locator('.image-credits-page .phase5-body > ul > li').count() == 2)
        check('No runtime, console or failed-request errors in normal batch flows', not any(report[k] for k in ['page_errors','console_errors','failed_requests']))

        # Fault injection is isolated: these failed requests are expected and recorded separately.
        faulty = browser.new_page(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        faults = []
        faulty.on('requestfailed', lambda r: report['expected_faults'].append({'url': r.url, 'failure': r.failure}))
        faulty.on('pageerror', lambda e: faults.append(str(e)))
        # Obtain the actual built URLs; keep the unrelated licensed photo available.
        page.goto(BASE + '/guitars/martin-d-28', wait_until='networkidle')
        urls = page.locator('.gallery-main img').evaluate('(i)=>[i.src,...i.srcset.split(",").map(s=>new URL(s.trim().split(" ")[0],location.href).href)]')
        faulty.route('**/*', lambda route: route.abort() if route.request.url in urls else route.continue_())
        faulty.goto(BASE + '/guitars/martin-d-28', wait_until='networkidle')
        expect(faulty.locator('.gallery-main .image-placeholder')).to_be_visible()
        check('A deliberately blocked D-28 photo falls back to a labeled illustration without runtime errors', not faults and bool(report['expected_faults']))
        browser.close()
    report['passed'] = True
except Exception:
    report['passed'] = False
    report['failure'] = traceback.format_exc()
    print(report['failure'], flush=True)
finally:
    (OUT / 'browser-batch-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if report['passed'] else 1)
