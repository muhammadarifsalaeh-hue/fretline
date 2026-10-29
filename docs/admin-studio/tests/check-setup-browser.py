"""Check the unconfigured entry only; this does not test Supabase auth or RLS."""
import json
import subprocess
import traceback
from hashlib import sha256
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:4179'
report = {'scope': 'Phase 1 setup entry and existing Catalog navigation only',
          'supabaseConnected': False, 'physicalIPadTested': False,
          'checks': [], 'errors': [], 'screenshots': [],
          'productionIndexSHA256': sha256((ROOT / 'dist/index.html').read_bytes()).hexdigest()}
sizes = {'desktop': (1440, 1000), 'ipad-landscape': (1194, 834),
         'ipad-portrait': (768, 1024), 'mobile': (390, 844)}

with sync_playwright() as p:
    for engine in ['chromium', 'webkit']:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) if engine == 'chromium' else p.webkit.launch()
        report.setdefault('browserVersions', {})[engine] = browser.version
        for size, (width, height) in sizes.items():
            name = f'{engine}-{size}-setup-and-catalog-return'
            context = browser.new_context(viewport={'width': width, 'height': height},
                                          has_touch=size != 'desktop', reduced_motion='reduce')
            page = context.new_page()
            page.on('pageerror', lambda e: report['errors'].append(str(e)))
            page.on('console', lambda m: report['errors'].append(m.text) if m.type == 'error' else None)
            page.on('response', lambda r: report['errors'].append(f'HTTP {r.status}: {r.url}') if r.status >= 400 else None)
            try:
                page.goto(BASE + '/admin', wait_until='networkidle')
                expect(page.locator('main h1')).to_have_text('Admin Studio')
                expect(page.locator('main')).to_contain_text('ยังไม่ได้เชื่อมต่อฐานข้อมูล')
                expect(page.locator('main input, main form')).to_have_count(0)
                expect(page.locator('main a', has_text='เปิด Supabase')).to_have_attribute('href', 'https://supabase.com/dashboard')
                for link in page.locator('.admin-setup-actions a').all():
                    assert link.bounding_box()['height'] >= 44
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                heading = page.locator('main h1').bounding_box()
                header = page.locator('.site-header').bounding_box()
                assert heading['y'] >= header['y'] + header['height']
                if engine == 'webkit' and size in ['ipad-landscape', 'ipad-portrait']:
                    filename = f'admin-setup-{size}.png'
                    page.screenshot(path=str(OUT / filename), animations='disabled', full_page=True)
                    report['screenshots'].append(filename)
                page.get_by_role('link', name='กลับไป Catalog', exact=True).click()
                expect(page.locator('.catalog-result-count > p').first).to_have_text('200 รุ่น')
                page.locator('#catalog-search').fill('Player II Stratocaster')
                expect(page.locator('[data-guitar-id="fender-player-ii-stratocaster"]')).to_contain_text('฿30,600')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                report['checks'].append({'name': name, 'passed': True})
                print('PASS', name, flush=True)
            except Exception:
                report['checks'].append({'name': name, 'passed': False, 'error': traceback.format_exc()})
                print('FAIL', name, traceback.format_exc(), flush=True)
            finally:
                context.close()
        browser.close()

changed = subprocess.check_output(['git', 'diff', '--name-only', 'a620d5e', '--', 'src', 'public'], cwd=ROOT, text=True).splitlines()
baseline_files = set(subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', 'a620d5e', '--', 'src', 'public'], cwd=ROOT, text=True).splitlines())
existing_changes = [name for name in changed if name in baseline_files]
assert existing_changes == ['src/App.jsx'], existing_changes
report['existingFilesChanged'] = existing_changes
report['protectedExistingSourceAndAssetFiles'] = len(baseline_files) - 1
report['passed'] = len(report['checks']) == 8 and all(c['passed'] for c in report['checks']) and not report['errors']
(OUT / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('FINAL', sum(c['passed'] for c in report['checks']), '/', len(report['checks']), report['passed'], flush=True)
raise SystemExit(0 if report['passed'] else 1)
