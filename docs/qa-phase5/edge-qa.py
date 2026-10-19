from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json, os, re, traceback

OUTPUT = Path(__file__).resolve().parent
BASE = os.environ.get('FRETLINE_DEV_QA_URL', 'http://127.0.0.1:5186')
report = {'checks': [], 'page_errors': [], 'console_errors': []}
A = 'yamaha-fg830'; B = 'yamaha-fg820'; C = 'taylor-214ce'

def check(name, condition=True):
    report['checks'].append({'name': name, 'passed': bool(condition)})
    print(name, bool(condition), flush=True)
    assert condition, name

def track(page):
    page.on('pageerror', lambda error: report['page_errors'].append(str(error)))
    page.on('console', lambda message: report['console_errors'].append(message.text) if message.type == 'error' else None)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN', '/usr/bin/chromium'), args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        track(page)
        page.goto(BASE + '/brands', wait_until='networkidle')
        page.evaluate('({ids})=>{localStorage.setItem("fretline:wishlist",JSON.stringify(ids));localStorage.setItem("fretline:compare","[]")}', {'ids': [A, A, 'deleted', B, C]})
        page.goto(BASE + '/wishlist', wait_until='networkidle')
        expect(page.locator('.wishlist-row')).to_have_count(3)
        check('Development Strict Mode normalizes duplicate persisted wishlist IDs')
        page.get_by_role('button', name='เปรียบเทียบ 3 รุ่น', exact=True).click()
        expect(page.get_by_role('table', name='ตารางเปรียบเทียบสเปกกีตาร์')).to_be_visible()
        expected = [C, B, A]
        check('Wishlist-to-Compare URL survives Strict Mode effect replay', page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))') == expected)
        page.reload(wait_until='networkidle')
        check('Shared comparison reload preserves all wishlist-selected IDs', page.evaluate('JSON.parse(localStorage.getItem("fretline:compare"))') == expected)
        page.goto(BASE + '/wishlist', wait_until='networkidle')
        page.locator('.wishlist-row').first.get_by_role('button', name=re.compile('^นำ .*ออกจากรายการโปรด')).click()
        expect(page.locator('.wishlist-row')).to_have_count(2)
        page.reload(wait_until='networkidle')
        check('Wishlist removal persists under development Strict Mode', page.locator('.wishlist-row').count() == 2)
        page.evaluate('localStorage.setItem("fretline:lang","en")')
        for path, title in [('/brands', 'Explore the brands'), ('/brands/fender', 'Fender'), ('/wishlist', 'My wishlist')]:
            page.goto(BASE + path, wait_until='networkidle')
            expect(page.locator('h1')).to_have_text(title)
            check('English fallback remains usable: ' + path, not re.search(r'p5\.', page.locator('main').inner_text()))
        page.close()
        blocked = browser.new_context(viewport={'width': 768, 'height': 1024})
        blocked.add_init_script('''Object.defineProperty(Storage.prototype,'getItem',{value(){throw new DOMException('Blocked by QA','SecurityError')}});Object.defineProperty(Storage.prototype,'setItem',{value(){throw new DOMException('Blocked by QA','SecurityError')}});''')
        page = blocked.new_page()
        track(page)
        page.goto(BASE + '/brands/fender', wait_until='networkidle')
        page.locator('.brand-model-grid article').first.get_by_role('button', name=re.compile('^บันทึก .*ในรายการโปรด')).click()
        page.locator('header a[href="/wishlist"]').first.click()
        expect(page.locator('.wishlist-row')).to_have_count(1)
        check('Blocked Local Storage retains in-memory wishlist across client navigation')
        page.locator('.wishlist-row').first.get_by_role('button', name=re.compile('^นำ .*ออกจากรายการโปรด')).click()
        expect(page.get_by_role('heading', name='ยังไม่มีกีตาร์ในรายการโปรด', exact=True)).to_be_visible()
        check('Blocked Local Storage can still remove saved guitars')
        check('No development page or runtime errors', not report['page_errors'])
        check('No development console errors', not report['console_errors'])
        blocked.close()
        browser.close()

try:
    run()
    report['passed'] = True
except Exception:
    report['passed'] = False
    report['failure'] = traceback.format_exc()
    print(report['failure'], flush=True)
finally:
    (OUTPUT / 'edge-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
if not report['passed']:
    raise SystemExit(1)
