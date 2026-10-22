"""Verify that no permission-pending image or color UI enters Production."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import hashlib, json, traceback

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '.local-preview/multicolor'
OUT.mkdir(parents=True, exist_ok=True)
ID = 'yamaha-pacifica-612viifm'
BASE = 'http://127.0.0.1:5180'
images = json.loads((ROOT/'docs/qa-pacifica-multicolor/image-intake.json').read_text())['images']
hashes = {image['sha256'] for image in images}
result = {'checks':[], 'runtimeErrors':[], 'consoleErrors':[], 'browser':'Chromium on Linux'}

def check(name, condition):
    result['checks'].append({'name':name,'passed':bool(condition)})
    print(('PASS ' if condition else 'FAIL ') + name, flush=True)
    assert condition, name

try:
    for directory in [ROOT/'dist', Path('/tmp/fretline-pacifica-mode-build')]:
        files = [p for p in directory.rglob('*') if p.is_file()]
        check(str(directory) + ' excludes all four original JPEGs and their endpoint', bool(files) and not any(
            hashlib.sha256(p.read_bytes()).hexdigest() in hashes or b'__fretline_development_preview__' in p.read_bytes()
            or any(image['file'].encode() in p.read_bytes() for image in images) for p in files))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':390,'height':844}, reduced_motion='reduce')
        page.on('pageerror', lambda e:result['runtimeErrors'].append(str(e)))
        page.on('console', lambda m:result['consoleErrors'].append(m.text) if m.type=='error' else None)
        for route,where in [('/guitars?q=612VIIFM','.catalog-card-image'),('/guitars/'+ID,'.gallery-main')]:
            page.goto(BASE + route, wait_until='networkidle')
            expect(page.locator(where + ' .image-placeholder')).to_be_visible()
            check('Production '+route+' keeps its placeholder and excludes the unverified color UI',
                  page.locator('[data-development-image-preview], .preview-color-selector, [data-preview-color-indicators], [data-local-preview-picker]').count()==0)
            expect(page.locator('main')).to_contain_text('฿34,000')
        check('Production does not pretend to have a four-photo licensed gallery', page.locator('.gallery-thumbnails').count()==0)
        for image in images:
            for route in ['/.local-preview/'+ID+'/'+image['file'],
                          '/__fretline_development_preview__/'+ID+'/'+image['id']+'/'+image['sha256'][:20]+'.jpg']:
                response = page.request.get(BASE+route)
                check('Production cannot retrieve '+route, not response.headers.get('content-type','').startswith('image/')
                      and hashlib.sha256(response.body()).hexdigest() not in hashes)
        check('Production has no runtime or console errors', not result['runtimeErrors'] and not result['consoleErrors'])
        browser.close()
    result['passed'] = True
except Exception:
    result['passed'] = False
    result['failure'] = traceback.format_exc()
    print(result['failure'], flush=True)
finally:
    (OUT/'production-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if result['passed'] else 1)
