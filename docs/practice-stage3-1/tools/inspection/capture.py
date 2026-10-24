"""Capture actual Stage 3.1 candidate geometry. Does not approve a pose.

Requires an explicitly configured candidate. Screenshots retain the research
banner. Linux WebKit is not physical iPad Safari. No canvas/image substitution.
"""
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl
import argparse
import json
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True, help='Inspector URL with explicit ?config= path')
parser.add_argument('--engine', choices=['chromium', 'webkit'], default='chromium')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
assert dict(parse_qsl(urlsplit(args.url).query)).get('config'), 'Explicit candidate config required'
args.output.mkdir(parents=True, exist_ok=True)
report = {'engine': args.engine, 'url': args.url, 'poseApproved': False,
          'limitations': ['Research inspector, not Fretline app adoption.',
                          'No physical iPad Safari or GPU/frame-rate verdict.'],
          'checks': [], 'errors': [], 'responses': [], 'failedRequests': []}

with sync_playwright() as playwright:
    browser = (playwright.chromium.launch(executable_path='/usr/bin/chromium', args=[
        '--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        if args.engine == 'chromium' else playwright.webkit.launch())
    report['browserVersion'] = browser.version
    for width, height, label in [(1440, 1050, 'desktop'), (1024, 768, 'tablet'), (390, 844, 'mobile'), (320, 740, 'small-mobile')]:
        context = browser.new_context(viewport={'width': width, 'height': height},
                                      device_scale_factor=1, has_touch=width <= 1024)
        page = context.new_page()
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        page.on('console', lambda msg: report['errors'].append(msg.text) if msg.type == 'error' else None)
        page.on('response', lambda response: report['responses'].append({'url': response.url, 'status': response.status}))
        page.on('requestfailed', lambda request: report['failedRequests'].append({'url': request.url, 'failure': request.failure}))
        page.goto(args.url)
        page.wait_for_function('window.inspectionReady || window.inspectionError', timeout=60000)
        error = page.evaluate('window.inspectionError || null')
        assert not error, error
        assert page.evaluate('window.inspectionReady')
        views = []
        for name in ['front', 'side', 'back', 'player']:
            button = page.locator(f'[data-view="{name}"]')
            button.tap() if width <= 1024 else button.click()
            page.wait_for_function('(name) => window.inspectionView === name', arg=name)
            page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            projection = page.evaluate('window.inspectionProjection()')
            assert max(abs(point[axis]) for point in projection for axis in [0, 1]) < .99, (label, name, projection)
            filename = f'{args.engine}-{label}-{name}.png'
            page.screenshot(path=str(args.output / filename), full_page=True)
            views.append({'name': name, 'camera': page.evaluate('window.inspectionCamera'), 'focusNdcCorners': projection, 'canvasBounds': page.locator('canvas').bounding_box(), 'screenshot': filename})
        canvas = page.locator('canvas')
        before = page.evaluate('window.inspectionCamera')
        canvas.focus()
        page.keyboard.press('ArrowRight')
        page.wait_for_function('(before)=>JSON.stringify(window.inspectionCamera.position)!==JSON.stringify(before)', arg=before['position'])
        after = page.evaluate('window.inspectionCamera')
        page.keyboard.press('+')
        page.wait_for_function('(before)=>window.inspectionCamera.distance<before', arg=after['distance'])
        page.locator('#reset').tap() if width <= 1024 else page.locator('#reset').click()
        page.wait_for_function('(before)=>window.inspectionCamera.position.every((n,i)=>Math.abs(n-before[i])<1e-8)', arg=before['position'])
        overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth')
        assert not overflow, label
        report['checks'].append({'viewport': label, 'width': width, 'height': height, 'views': views,
                                 'keyboardOrbitZoomReset': True, 'noPageOverflow': True})
        if label == 'desktop':
            report['proof'] = page.evaluate('window.inspectionProof')
            (args.output / f'{args.engine}-vertices.json').write_text(json.dumps(page.evaluate('window.inspectionVertices')))
        context.close()
    browser.close()

report['passedRenderingChecks'] = not report['errors'] and not report['failedRequests'] and all(row['status'] < 400 for row in report['responses'])
(args.output / f'{args.engine}-capture-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'engine': args.engine, 'renderChecksPassed': report['passedRenderingChecks'],
                  'viewsCaptured': sum(len(check['views']) for check in report['checks']),
                  'errors': report['errors'], 'failedRequests': report['failedRequests']}, indent=2))
