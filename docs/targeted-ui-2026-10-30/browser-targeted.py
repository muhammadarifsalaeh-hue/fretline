"""Responsive and language acceptance for the targeted Home refinement.

Uses the unchanged project catalog. No SQL, database writes or HTTP fixtures.
Run against a frozen production build, after check-targeted-ui.mjs passes.
"""
import argparse
import json
import re
import traceback
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--pages', nargs='+', help='Optionally rerun only changed pages after an isolated polish.')
args = parser.parse_args()
base = args.url.rstrip('/')
args.output.mkdir(parents=True, exist_ok=True)
before = json.loads((ROOT / 'docs/targeted-ui-2026-10-30/before-layout.json').read_text())
routes = {
    'home': '/', 'catalog': '/guitars', 'detail': '/guitars/yamaha-pacifica-612viifm',
    'brands': '/brands', 'brand': '/brands/yamaha',
    'compare': '/compare?ids=yamaha-pacifica-612viifm,yamaha-fg820-12',
    'quiz': '/find-my-guitar', 'favorites': '/wishlist', 'practice': '/practice',
    'credits': '/image-credits', 'qr': '/qr', 'admin': '/admin', '404': '/missing-page',
}
sizes = {'desktop': (1440, 1000), 'landscape': (1194, 834),
         'portrait': (768, 1024), 'mobile': (390, 844), 'narrow': (320, 740)}
old_ui = ['THE ART OF FINDING YOUR SOUND', 'EXPLORE BY BRAND', 'EXPLORE BY CATEGORY',
          'YOUR PERSONAL COLLECTION', 'OWNER WORKSPACE', 'IMAGE SOURCES & LICENSES',
          'THE BRAND COLLECTION', 'BRAND DIRECTORY', 'This page is out of tune.',
          'Browse guitars', 'Back home', 'Find your tone.', 'Find My\nGuitar Quiz']
report = {'checks': [], 'consoleErrors': [], 'runtimeErrors': [],
          'physicalIPadSafariTested': False, 'hostedSupabaseTested': False,
          'dataSource': 'unchanged project data; no mocks or database writes'}


def save():
    (args.output / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


def screenshot_section(page, selector, path):
    target = page.locator(selector)
    target.scroll_into_view_if_needed()
    for image in target.locator('img').all():
        image.evaluate('(image)=>image.decode()')
    target.screenshot(path=str(path), animations='disabled')


with sync_playwright() as playwright:
    for engine in ['chromium', 'webkit']:
        browser = (playwright.chromium.launch(executable_path='/usr/bin/chromium',
                   args=['--no-sandbox', '--enable-unsafe-swiftshader'])
                   if engine == 'chromium' else playwright.webkit.launch())
        for device, (width, height) in sizes.items():
            context = browser.new_context(viewport={'width': width, 'height': height},
                                          has_touch=device != 'desktop', reduced_motion='reduce')
            page = context.new_page()
            page.on('pageerror', lambda error: report['runtimeErrors'].append(str(error)))
            page.on('console', lambda message: report['consoleErrors'].append(message.text)
                    if message.type == 'error' else None)
            for name, path in routes.items():
                if args.pages and name not in args.pages:
                    continue
                label = f'{engine}-{device}-{name}'
                try:
                    page.goto(base + path, wait_until='networkidle')
                    expect(page.locator('main h1')).to_be_visible()
                    page.evaluate('document.fonts.ready')
                    expect(page.locator('html')).to_have_attribute('lang', 'th')
                    expect(page.locator('.fretline-signature')).to_have_count(0)
                    evidence = {'viewport': width, 'pageWidth': page.evaluate('document.documentElement.scrollWidth')}
                    assert evidence['pageWidth'] <= width + 1, evidence
                    text = page.locator('main').inner_text()
                    assert 'targeted.' not in text, 'Unresolved translation key'
                    assert not any(phrase in text for phrase in old_ui), 'Old interface copy remains'
                    if name == 'home':
                        cards = page.locator('.signature-category-pill')
                        expect(cards).to_have_count(4)
                        cols = page.locator('#categories .signature-category-grid').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length')
                        assert cols == (4 if width >= 1024 else 2 if width >= 640 else 1), cols
                        for category, count in before['categoryCounts'].items():
                            card = page.locator('.signature-category-card--' + category)
                            expect(card).to_contain_text(str(count) + ' รุ่น')
                            assert 'type=' + category in card.get_attribute('href')
                            expect(card.locator('svg image')).to_have_count(1)
                            bounds = card.bounding_box()
                            assert bounds['height'] <= 130 and bounds['width'] > 1.5 * bounds['height']
                            assert card.evaluate('(e)=>parseFloat(getComputedStyle(e).borderTopLeftRadius)') >= bounds['height'] / 2
                        if device in before['metrics']:
                            for selector in ['.site-header', '#top', '#top h1', '.signature-hero-actions', '.signature-hero-search', '.signature-stats']:
                                current = page.locator(selector).bounding_box()
                                original = before['metrics'][device][selector]
                                for coordinate in ['x', 'y', 'width', 'height']:
                                    assert abs(current[coordinate] - original[coordinate]) <= 1, (selector, coordinate, original, current)
                            evidence['heroNavStatsGeometryUnchanged'] = True
                        for key, value in [('200', 'รุ่นกีตาร์'), ('10', 'แบรนด์')]:
                            expect(page.locator('.signature-stats')).to_contain_text(key)
                        expect(page.locator('#home-practice')).to_contain_text('42 คอร์ด')
                        photo = page.locator('#home-practice .home-editorial-photo').bounding_box()
                        copy = page.locator('#home-practice .home-editorial-copy').bounding_box()
                        assert photo['x'] >= copy['x'] + copy['width'] or photo['y'] + photo['height'] <= copy['y'], (photo, copy)
                        expect(page.locator('#home-practice img')).to_have_attribute('src', re.compile('practice-black-gold-les-paul'))
                        assert page.locator('#home-practice img').evaluate('(e)=>getComputedStyle(e).objectFit') == 'contain'
                        expect(page.locator('#home-practice .home-editorial-cta')).to_have_attribute('href', '/practice')
                        for selector, suffix in [('#categories', 'categories'), ('#home-practice', 'practice-banner')]:
                            screenshot_section(page, selector, args.output / f'{engine}-{device}-{suffix}.png')
                        page.evaluate('window.scrollTo(0,0)')
                        page.wait_for_timeout(100)
                        evidence.update(categoryColumns=cols, practiceImageTextSeparated=True, modelCountsFromBaseline=True)
                    if name == 'practice':
                        expect(page.locator('[data-practice-chord]')).to_have_count(42)
                        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status', 'ready', timeout=60000)
                        expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status', 'ready', timeout=60000)
                        evidence['unchanged3DAnd42ChordsReady'] = True
                    if name == 'credits':
                        page.locator('main details').evaluate_all('(nodes)=>nodes.forEach(node=>node.open=true)')
                        text = page.locator('main').inner_text()
                        assert not re.search(r'\bAI\b|AI Generated|AI Edited|Powered by AI', text, re.I)
                        assert 'สิทธิ์ต้นฉบับและความตรงรุ่นยังไม่ได้รับการยืนยัน' in text
                        assert page.locator('main a[href*="creativecommons.org"]').count() >= 2
                        evidence['originalCreditsAndLimitationsPreserved'] = True
                    if name == 'admin':
                        expect(page.get_by_role('heading', name='จัดการเว็บไซต์', exact=True)).to_be_visible()
                        expect(page.get_by_label('URL โปรเจกต์', exact=True)).to_be_visible()
                        expect(page.get_by_label('คีย์สำหรับเผยแพร่ (Publishable key)', exact=True)).to_be_visible()
                        expect(page.locator('.site-nav a[href="/admin"]')).to_have_count(0)
                        evidence['thaiAdminSetupWithoutPublicAdminMenu'] = True
                    if device in ['desktop', 'mobile']:
                        page.screenshot(path=str(args.output / f'{label}.png'), animations='disabled')
                    report['checks'].append({'name': label, 'passed': True, 'evidence': evidence})
                    print('PASS', label, flush=True)
                except Exception:
                    report['checks'].append({'name': label, 'passed': False, 'error': traceback.format_exc()})
                    print('FAIL', label, traceback.format_exc(), flush=True)
                    page.screenshot(path=str(args.output / f'{label}-FAIL.png'), animations='disabled')
                save()
            context.close()
        browser.close()

report['passed'] = all(check['passed'] for check in report['checks']) and not report['consoleErrors'] and not report['runtimeErrors']
save()
print('FINAL', report['passed'], len(report['checks']), flush=True)
raise SystemExit(not report['passed'])
