from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json, os, re, traceback

OUTPUT = Path(__file__).resolve().parent
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:4185')
report = {'checks': [], 'page_errors': [], 'console_errors': []}
def check(name, condition=True):
    report['checks'].append({'name': name, 'passed': bool(condition)})
    print(name, bool(condition), flush=True)
    assert condition, name

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN', '/usr/bin/chromium'), args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1100})
        page.on('pageerror', lambda error: report['page_errors'].append(str(error)))
        page.on('console', lambda message: report['console_errors'].append(message.text) if message.type == 'error' else None)
        for label, width, height in [('desktop', 1440, 1100), ('tablet', 768, 1024), ('mobile', 390, 844)]:
            page.set_viewport_size({'width': width, 'height': height})
            page.goto(BASE + '/brands', wait_until='networkidle')
            page.get_by_role('searchbox', name='ค้นหาแบรนด์', exact=True).fill('Yamaha')
            card = page.locator('.brand-directory-card')
            expect(card).to_have_count(1)
            card.focus()
            page.keyboard.press('Enter')
            expect(page.locator('h1')).to_have_text('Yamaha')
            check('Search and keyboard brand navigation: ' + label)
            cards = page.locator('.brand-model-grid article')
            total = cards.count()
            page.get_by_role('group', name='ประเภทกีตาร์', exact=True).get_by_role('button', name='กีตาร์ไฟฟ้า', exact=True).click()
            expect(cards).to_have_count(1)
            check('Brand Detail type filtering: ' + label, 'type=electric' in page.url and 'Pacifica' in cards.first.inner_text())
            page.go_back(wait_until='networkidle')
            expect(cards).to_have_count(total)
            page.get_by_role('combobox', name='เรียงตาม', exact=True).select_option('name')
            names = cards.locator('h3').all_text_contents()
            check('Brand Detail model name sorting: ' + label, names == sorted(names, key=str.lower))
            page.get_by_role('link', name='เปิดในแคตตาล็อก', exact=True).click()
            expect(page.locator('.catalog-grid article')).to_have_count(9)
            check('Brand-specific Catalog navigation: ' + label, 'brand=Yamaha' in page.url and all('Yamaha' in value for value in page.locator('.catalog-grid article').all_text_contents()))
            page.go_back(wait_until='networkidle')
            expect(page.locator('h1')).to_have_text('Yamaha')
            check('Back from catalog retains Brand Detail sort: ' + label, 'sort=name' in page.url)
        check('No page or runtime errors in responsive interactions', not report['page_errors'])
        check('No console errors in responsive interactions', not report['console_errors'])
        browser.close()
try:
    run()
    report['passed'] = True
except Exception:
    report['passed'] = False
    report['failure'] = traceback.format_exc()
    print(report['failure'], flush=True)
finally:
    (OUTPUT / 'interaction-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
if not report['passed']:
    raise SystemExit(1)
