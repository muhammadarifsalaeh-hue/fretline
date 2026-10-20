"""Phase 8 real-browser functional regression. Requires Python Playwright + Chromium.

Run: FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8/browser-phase8.py
Responsive screenshots, axe audit and all-200 detail audit run separately.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json, os, re, traceback

OUT = Path(__file__).resolve().parent
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:4188')
PHOTO = 'yamaha-fg820-12'
A = 'yamaha-fg830'
B = 'ibanez-sr300e'
C = 'taylor-gs-mini'
D = 'taylor-214ce'
NEW = 'fender-player-ii-telecaster'
ARCHIVES = ['yamaha-c40', 'gretsch-g2420-streamliner']
BRANDS = ['Yamaha', 'Fender', 'Epiphone', 'Ibanez', 'Taylor', 'Córdoba', 'Gibson', 'Martin', 'PRS', 'Squier']
report = {'checks': [], 'page_errors': [], 'console_errors': [], 'failed_requests': [], 'base_url': BASE, 'browser': 'Chromium; not physical Safari/iPad'}


def check(name, condition=True):
    report['checks'].append({'name': name, 'passed': bool(condition)})
    print(name, bool(condition), flush=True)
    assert condition, name


def visit(page, path):
    page.goto(BASE + path, wait_until='networkidle')


def stored(page, key):
    return page.evaluate('(key) => JSON.parse(localStorage.getItem("fretline:" + key) || "[]")', key)


def count(page, key, expected):
    page.wait_for_function('({key,n}) => JSON.parse(localStorage.getItem("fretline:" + key) || "[]").length === n', arg={'key': key, 'n': expected})


def choose(page, value):
    page.locator(f'label.quiz-option:has(input[value="{value}"])').click()


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN', '/usr/bin/chromium'), args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1100}, reduced_motion='reduce')
        page.set_default_timeout(12000)
        page.on('pageerror', lambda error: report['page_errors'].append(str(error)))
        page.on('console', lambda message: report['console_errors'].append(message.text) if message.type == 'error' else None)
        page.on('requestfailed', lambda request: report['failed_requests'].append({'url': request.url, 'failure': request.failure}))

        visit(page, '/brands')
        expect(page.locator('.brand-directory-card')).to_have_count(10)
        counts = page.locator('.brand-card-count').all_text_contents()
        check('Ten active brands each display exactly twenty real catalog models', len(counts) == 10 and all(int(re.search(r'\d+', value)[0]) == 20 for value in counts))
        for brand in BRANDS:
            visit(page, '/guitars?' + __import__('urllib.parse', fromlist=['urlencode']).urlencode({'brand': brand}))
            check('Brand filter returns twenty models: ' + brand, '20' in page.locator('.catalog-results').inner_text())
            expect(page.locator('.catalog-grid article')).to_have_count(9)

        visit(page, '/guitars')
        cards = page.locator('.catalog-grid article')
        expect(cards).to_have_count(9)
        first_id = cards.first.get_attribute('data-guitar-id')
        check('Catalog announces 200 actual results', '200' in page.locator('.catalog-result-count').inner_text())
        page.get_by_role('button', name='หน้าถัดไป', exact=True).click()
        check('Pagination pushes page two into URL history', 'page=2' in page.url and cards.first.get_attribute('data-guitar-id') != first_id)
        page.go_back(wait_until='networkidle')
        check('Browser Back restores page one', cards.first.get_attribute('data-guitar-id') == first_id)
        page.go_forward(wait_until='networkidle')
        check('Browser Forward restores page two', 'page=2' in page.url)
        visit(page, '/guitars?page=23')
        expect(cards).to_have_count(2)
        expect(page.get_by_role('button', name='หน้าถัดไป', exact=True)).to_be_disabled()
        check('Final page contains exactly two models')
        visit(page, '/guitars?type=bass&brand=Ibanez')
        expect(cards).to_have_count(1)
        check('Brand and guitar type filters intersect', cards.first.get_attribute('data-guitar-id') == B)
        visit(page, '/guitars?q=Cordoba')
        check('Accent-insensitive search finds Córdoba models', cards.count() > 0 and 'córdoba' in cards.first.inner_text().casefold())
        visit(page, '/guitars?q=FG820%2012')
        check('Space query matches punctuation in FG820-12 model', cards.locator(f'[data-guitar-id="{PHOTO}"]').count() > 0 or page.locator(f'.catalog-grid article[data-guitar-id="{PHOTO}"]').count() == 1)
        visit(page, '/guitars?sort=name')
        expect(cards).to_have_count(9)
        check('Name sorting resolves to a populated catalog', 'sort=name' in page.url)
        visit(page, '/guitars?sort=constructor&page=99999999')
        check('Malformed sort and oversized page parameters resolve safely', cards.count() > 0)
        visit(page, '/guitars?q=NoSuchFretlineGuitarXYZ')
        expect(cards).to_have_count(0)
        check('Unmatched query renders an honest empty state', page.locator('main h1').count() == 1)
        page.get_by_role('button', name='ล้างตัวกรองทั้งหมด', exact=True).click()
        expect(cards).to_have_count(9)
        check('Clear filters restores catalog')

        visit(page, '/guitars?q=FG820')
        photo_card = page.locator(f'article[data-guitar-id="{PHOTO}"]')
        photo_card.get_by_role('button', name=re.compile('^บันทึก .*ในรายการโปรด')).click()
        count(page, 'wishlist', 1)
        photo_card.get_by_role('button', name=re.compile('^เพิ่ม .*ในการเปรียบเทียบ')).click()
        count(page, 'compare', 1)
        photo_card.get_by_role('link', name='ดูรายละเอียด', exact=True).click()
        expect(page.locator('.detail-summary h1')).to_be_visible()
        check('Catalog details use original ID', '/guitars/' + PHOTO in page.url)
        image = page.locator('.gallery-main img')
        page.wait_for_function('() => {const image=document.querySelector(".gallery-main img");return image && image.complete && image.naturalWidth>0}')
        check('Licensed real photo retains eager loading and intrinsic dimensions', image.get_attribute('loading') == 'eager' and bool(image.get_attribute('width')))
        page.get_by_role('tab', name='รีวิว', exact=True).click()
        check('Review tab has no invented reviews', 'ยังไม่มีรีวิวที่ตรวจสอบแล้ว' in page.locator('[role="tabpanel"]:visible').inner_text())
        page.locator('.gallery-main').get_by_role('button', name='เปิดดูรูปขนาดใหญ่', exact=True).click()
        expect(page.get_by_role('dialog')).to_be_visible()
        page.keyboard.press('Escape')
        expect(page.get_by_role('dialog')).not_to_be_visible()
        check('Lightbox Escape restores opening button focus', page.locator('.gallery-main button[aria-label="เปิดดูรูปขนาดใหญ่"]').evaluate('(button) => button === document.activeElement'))

        visit(page, '/wishlist')
        expect(page.locator('.wishlist-row')).to_have_count(1)
        check('Wishlist persists while navigating pages', stored(page, 'wishlist') == [PHOTO])
        page.reload(wait_until='networkidle')
        check('Wishlist persists after reload', stored(page, 'wishlist') == [PHOTO])
        page.locator('.wishlist-row').get_by_role('button', name=re.compile('^นำ .*ออกจากรายการโปรด')).click()
        count(page, 'wishlist', 0)
        check('Wishlist explicit remove works')

        visit(page, '/compare?ids=' + ','.join([A, A, B]))
        count(page, 'compare', 2)
        check('Comparison URL deduplicates IDs', stored(page, 'compare') == [A, B])
        expect(page.get_by_role('table', name='ตารางเปรียบเทียบสเปกกีตาร์')).to_be_visible()
        page.locator('.compare-toolbar').get_by_role('button', name=re.compile('เพิ่มกีตาร์')).click()
        dialog = page.get_by_role('dialog')
        expect(dialog).to_be_visible()
        check('Guitar picker opens with search input focused', dialog.locator('input[type="search"]').evaluate('(input) => input === document.activeElement'))
        for model_id in [C, D]:
            # The model row includes brand, status and price; the name is the stable identifier.
            model_name = 'GS Mini' if model_id == C else '214ce'
            dialog.locator('input[type="search"]').fill(model_name)
            row = dialog.locator('.picker-model-row').filter(has_text=model_name).first
            expect(row).to_be_visible()
            row.click()
        count(page, 'compare', 4)
        check('Picker can add to four unique models', len(set(stored(page, 'compare'))) == 4)
        page.keyboard.press('Escape')
        expect(dialog).not_to_be_visible()
        expect(page.locator('.compare-toolbar button').first).to_be_disabled()
        check('Four-model limit is visible and prevents a fifth selection')
        visit(page, '/guitars/' + PHOTO)
        expect(page.locator('.detail-summary').get_by_role('button', name=re.compile('เปรียบเทียบ'))).to_be_disabled()
        check('Detail comparison control disables when four other guitars are selected')
        visit(page, '/compare')
        remove = page.locator('.compare-table-scroll').get_by_role('button', name=re.compile('^นำ .*ออกจากการเปรียบเทียบ')).first
        remove.focus()
        page.keyboard.press('Enter')
        count(page, 'compare', 3)
        check('Removing a comparison retains useful keyboard focus', page.evaluate('document.activeElement !== document.body'))
        page.go_back(wait_until='networkidle')
        count(page, 'compare', 4)
        page.go_forward(wait_until='networkidle')
        count(page, 'compare', 3)
        check('Compare Browser Back and Forward restore selection state')

        visit(page, '/find-my-guitar')
        page.get_by_role('button', name='เริ่มค้นหากีตาร์', exact=True).click()
        expect(page.get_by_role('button', name='ถัดไป', exact=True)).to_be_disabled()
        check('Quiz prevents unanswered progress')
        choose(page, 'acoustic'); page.get_by_role('button', name='ถัดไป', exact=True).click()
        choose(page, 'intermediate'); page.get_by_role('button', name='ถัดไป', exact=True).click()
        choose(page, 'folk'); page.get_by_role('button', name='ก่อนหน้า', exact=True).click()
        expect(page.locator('input[value="intermediate"]')).to_be_checked()
        check('Quiz Previous preserves earlier choices')
        page.get_by_role('button', name='ถัดไป', exact=True).click()
        expect(page.locator('input[value="folk"]')).to_be_checked()
        page.get_by_role('button', name='ถัดไป', exact=True).click()
        choose(page, 'mid'); page.get_by_role('button', name='ถัดไป', exact=True).click()
        choose(page, 'versatile'); page.get_by_role('button', name='ดูผลแนะนำ', exact=True).click()
        expect(page.locator('.match-card')).to_have_count(3)
        check('Five-step quiz produces real catalog results and shareable answers', all(key + '=' in page.url for key in ['type', 'level', 'style', 'budget', 'priority']))
        check('Quiz result heading receives keyboard focus', page.locator('main h1').evaluate('(heading) => heading === document.activeElement'))
        result = page.locator('.match-card').first
        check('Recommendations clearly show partial data and unknown prices', 'ตรวจสอบบางส่วน' in result.inner_text() and 'ยังไม่มีข้อมูลราคา' in result.inner_text())
        result.get_by_role('button', name=re.compile('^บันทึก .*ในรายการโปรด')).click()
        count(page, 'wishlist', 1)
        result.get_by_role('link', name='ดูรายละเอียด', exact=True).click()
        expect(page.locator('.detail-summary h1')).to_be_visible()
        page.go_back(wait_until='networkidle')
        expect(page.locator('.match-card')).to_have_count(3)
        check('Quiz result detail navigation and Browser Back retain answers')

        page.evaluate('([a,b,c]) => {localStorage.setItem("fretline:wishlist",JSON.stringify([a,b,a,c]));localStorage.setItem("fretline:compare",JSON.stringify([a,b]))}', [*ARCHIVES, NEW])
        visit(page, '/wishlist')
        count(page, 'wishlist', 3)
        expect(page.locator('.wishlist-row')).to_have_count(3)
        check('Legacy archived favourites remain saved and deduplicated', stored(page, 'wishlist') == [*ARCHIVES, NEW])
        check('Wishlist labels both archived models explicitly', page.locator('.wishlist-row .archive-label').count() == 2)
        for archived in ARCHIVES:
            visit(page, '/guitars/' + archived)
            expect(page.locator('.detail-summary h1')).to_be_visible()
            check('Archived detail preserves ID and explains exclusion: ' + archived, 'ไม่รวมในยอด 200 รุ่น' in page.locator('.archive-notice').inner_text())
        visit(page, '/compare?ids=' + ','.join([*ARCHIVES, NEW]))
        count(page, 'compare', 3)
        check('Legacy shared comparison retains and labels archived models', page.locator('.compare-table-scroll .archive-label').count() == 2)
        visit(page, '/brands/gretsch')
        expect(page.locator('h1')).to_have_text('Gretsch')
        check('Legacy archived brand link is handled', page.locator('.archive-notice').count() == 1)

        # Small-screen drawer interaction is covered here; full 5-width screenshots run separately.
        page.set_viewport_size({'width': 390, 'height': 844})
        visit(page, '/guitars')
        trigger = page.locator('.catalog-filter-trigger')
        trigger.click()
        drawer = page.locator('#catalog-filter-dialog')
        expect(drawer).to_be_visible()
        page.wait_for_function('() => document.querySelector("#catalog-filter-dialog").contains(document.activeElement)')
        check('Mobile filter drawer traps active focus inside dialog', drawer.evaluate('(dialog) => dialog.contains(document.activeElement)'))
        page.keyboard.press('Escape')
        check('Mobile drawer Escape restores trigger focus', trigger.evaluate('(button) => button === document.activeElement'))
        check('No runtime errors in normal flows', not report['page_errors'])
        check('No console errors in normal flows', not report['console_errors'])
        check('No failed requests in normal flows', not report['failed_requests'])
        browser.close()


try:
    run()
    report['passed'] = True
except Exception:
    report['passed'] = False
    report['failure'] = traceback.format_exc()
    print(report['failure'], flush=True)
finally:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'browser-phase8-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
if not report['passed']:
    raise SystemExit(1)
