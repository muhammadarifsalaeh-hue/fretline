"""Verify that the separately served production build cannot show the AI PNG."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import hashlib, json, traceback

ROOT = Path(__file__).resolve().parents[2]
BASE = 'http://127.0.0.1:5180'
ID = 'yamaha-pacifica-612viifm'
SHA = '3af6ba415bd42469b84bf6747ebcf1fc43965efcad4d9783ebd5ccfcdaee9e37'
result = {'browser':'Chromium on Linux', 'checks':[], 'runtimeErrors':[], 'consoleErrors':[]}

def check(name, condition):
    result['checks'].append({'name':name, 'passed':bool(condition)})
    print(('PASS ' if condition else 'FAIL ') + name, flush=True)
    assert condition, name

try:
    for directory in [ROOT / 'dist', Path('/tmp/fretline-pacifica-mode-build')]:
        files = [p for p in directory.rglob('*') if p.is_file()]
        check(str(directory) + ' contains no original PNG or image endpoint', bool(files) and not any(
            hashlib.sha256(p.read_bytes()).hexdigest() == SHA or b'__fretline_development_preview__' in p.read_bytes()
            or (ID + '-preview.png').encode() in p.read_bytes() for p in files))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':390, 'height':844}, reduced_motion='reduce')
        page.on('pageerror', lambda e:result['runtimeErrors'].append(str(e)))
        page.on('console', lambda m:result['consoleErrors'].append(m.text) if m.type=='error' else None)
        for route, location in [('/guitars?q=612VIIFM', '.catalog-card-image'), ('/guitars/'+ID, '.gallery-main')]:
            page.goto(BASE + route, wait_until='networkidle')
            expect(page.locator(location + ' .image-placeholder')).to_be_visible()
            check('Production ' + route + ' retains the original model placeholder', page.locator('[data-development-image-preview]').count() == 0)
            expect(page.locator('main')).to_contain_text('฿34,000')
        for path in ['/.local-preview/' + ID + '-preview.png', '/__fretline_development_preview__/' + ID + '/' + SHA[:20] + '.png']:
            response = page.request.get(BASE + path)
            check('Production cannot retrieve illustration bytes: ' + path, response.headers.get('content-type','').split(';')[0] != 'image/png'
                  and hashlib.sha256(response.body()).hexdigest() != SHA)
        check('Production has no console or runtime errors', not result['runtimeErrors'] and not result['consoleErrors'])
        browser.close()
    result['passed'] = True
except Exception:
    result['passed'] = False
    result['failure'] = traceback.format_exc()
    print(result['failure'], flush=True)
finally:
    (ROOT / '.local-preview/production-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if result['passed'] else 1)
