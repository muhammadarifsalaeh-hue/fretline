"""Check every existing route at five sizes in Chromium and WebKit.

Use a frozen production build. --before optionally verifies the original Admin
screenshots pixel for pixel in Chromium; it never logs in or writes cloud data.
"""
import argparse
import json
import re
import traceback
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import expect, sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--before', type=Path)
args = parser.parse_args()
base = args.url.rstrip('/')
args.output.mkdir(parents=True, exist_ok=True)

routes = {
    'home': '/', 'brands': '/brands', 'brand': '/brands/yamaha',
    'catalog': '/guitars', 'detail': '/guitars/yamaha-pacifica-612viifm',
    'compare': '/compare?ids=yamaha-pacifica-612viifm,yamaha-fg820-12',
    'quiz': '/find-my-guitar', 'favorites': '/wishlist',
    'practice': '/practice', 'credits': '/image-credits', 'qr': '/qr',
    '404': '/missing-signature-route', 'admin': '/admin',
}
sizes = {'desktop': (1440, 1000), 'landscape': (1194, 834),
         'portrait': (768, 1024), 'mobile': (390, 844), 'narrow': (320, 740)}
report = {'checks': [], 'consoleErrors': [], 'runtimeErrors': [],
          'realSupabaseTested': False, 'physicalIPadSafariTested': False}
report_path = args.output / 'browser-results.json'

with sync_playwright() as playwright:
    for engine in ['chromium', 'webkit']:
        browser = (playwright.chromium.launch(executable_path='/usr/bin/chromium',
                   args=['--no-sandbox', '--enable-unsafe-swiftshader'])
                   if engine == 'chromium' else playwright.webkit.launch())
        for device, (width, height) in sizes.items():
            # Match the original audit context for pixel comparisons. Touch
            # interactions are exercised separately by the other two suites.
            context = browser.new_context(viewport={'width': width, 'height': height},
                                          reduced_motion='reduce')
            page = context.new_page()
            page.on('pageerror', lambda error: report['runtimeErrors'].append(str(error)))
            page.on('console', lambda message: report['consoleErrors'].append(message.text)
                    if message.type == 'error' else None)
            for name, path in routes.items():
                label = f'{engine}-{device}-{name}'
                try:
                    page.goto(base + path, wait_until='networkidle')
                    expect(page.locator('main h1')).to_be_visible()
                    page.evaluate('document.fonts.ready')
                    if name == 'practice':
                        expect(page.locator('[data-practice-status]')).to_have_attribute(
                            'data-practice-status', 'ready', timeout=60000)
                        expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute(
                            'data-hand-asset-status', re.compile('ready|error'), timeout=60000)
                    metrics = page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
                    assert metrics['scrollWidth'] <= metrics['width'] + 1, metrics
                    if name == 'admin':
                        expect(page.locator('.fretline-signature')).to_have_count(0)
                    else:
                        expect(page.locator('.fretline-signature')).to_have_count(1)
                    if device in ['desktop', 'mobile']:
                        screenshot = args.output / f'{label}.png'
                        page.screenshot(path=str(screenshot), animations='disabled')
                        if name == 'admin' and engine == 'chromium' and args.before:
                            before = Image.open(args.before / f'{device}-admin.png').convert('RGB')
                            after = Image.open(screenshot).convert('RGB')
                            metrics['adminPixelIdentical'] = ImageChops.difference(before, after).getbbox() is None
                            assert metrics['adminPixelIdentical'], 'Original Admin presentation changed'
                    report['checks'].append({'name': label, 'passed': True, 'metrics': metrics})
                    print('PASS', label, flush=True)
                except Exception:
                    report['checks'].append({'name': label, 'passed': False, 'error': traceback.format_exc()})
                    print('FAIL', label, traceback.format_exc(), flush=True)
                report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            context.close()
        browser.close()

report['passed'] = (all(check['passed'] for check in report['checks'])
                    and not report['consoleErrors'] and not report['runtimeErrors'])
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('FINAL', report['passed'], len(report['checks']), flush=True)
raise SystemExit(not report['passed'])
