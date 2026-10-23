"""Capture real Phase C Homepage and Brands, with measured responsive evidence.

Uses existing Python Playwright + Pillow. No image generation, screenshots with
modified content, network mocking, DOM style changes, or application state edits.
Brands crops come from the untouched full-page PNG; document bounds are recorded.
"""
from PIL import Image
from playwright.sync_api import sync_playwright
import json
import math
import os
import traceback
from support import (OUT, VIEWPORTS, new_page, go, sweep_home, page_metrics,
                     brand_metrics, assert_page, assert_brands, report_template)

REPORT = report_template()
REPORT['method'] = {
    'scroll': 'Real vertical scroll sweep triggers native lazy images and reveal observers; then return to top.',
    'ready': 'Wait local fonts, rendered image decode/positive opacity and animation frames.',
    'brands': 'Crop section document bounds from the unmodified full Homepage PNG using Pillow.',
    'reference': 'Manual visual comparison required; no automated pixel match claimed without the original reference file.',
    'deviceLimit': 'Chromium viewport/touch emulation does not constitute actual Safari/iPad testing.',
}
REPORT['screenshots'] = []
SHOTS = OUT / 'after'
SHOTS.mkdir(parents=True, exist_ok=True)
selected = set(filter(None, os.environ.get('FRETLINE_QA_VIEWPORTS', '').split(',')))

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('FRETLINE_CHROMIUM', '/usr/bin/chromium'),
                                    args=['--no-sandbox'])
        for width, height, label in VIEWPORTS:
            if selected and label not in selected:
                continue
            context, page = new_page(browser, REPORT, 'capture-' + label, width, height)
            try:
                go(page)
                sweep_home(page)
                metrics = page_metrics(page)
                brands = brand_metrics(page)
                assert_page(metrics)
                geometry = assert_brands(brands, width)
                document_brands = page.locator('#brands').evaluate('''e=>{
                  const r=e.getBoundingClientRect();return {x:r.left+scrollX,y:r.top+scrollY,width:r.width,height:r.height};
                }''')
                # Blur only an incidental focused element; this is a normal user
                # focus state reset, not a visual/content/style override.
                page.evaluate('document.activeElement?.blur()')
                viewport = SHOTS / ('home-' + label + '.png')
                full = SHOTS / ('home-' + label + '-full.png')
                brand_shot = SHOTS / ('brands-' + label + '.png')
                page.screenshot(path=str(viewport), animations='disabled')
                page.screenshot(path=str(full), full_page=True, animations='disabled')
                with Image.open(full) as png:
                    scale_x = png.width / width
                    scale_y = scale_x  # CSS pixels at context deviceScaleFactor=1.
                    crop = (max(0, math.floor(document_brands['x'] * scale_x)),
                            max(0, math.floor(document_brands['y'] * scale_y)),
                            min(png.width, math.ceil((document_brands['x'] + document_brands['width']) * scale_x)),
                            min(png.height, math.ceil((document_brands['y'] + document_brands['height']) * scale_y)))
                    png.crop(crop).save(brand_shot)
                names = [str(path.relative_to(OUT)) for path in [viewport, full, brand_shot]]
                REPORT['screenshots'].extend(names)
                REPORT['checks'].append({'case': label, 'passed': True, 'page': metrics,
                                         'brands': brands, 'geometry': geometry,
                                         'brandsCropCSSPixels': document_brands,
                                         'screenshots': names})
                print('PASS capture-' + label, flush=True)
            except Exception:
                error = traceback.format_exc()
                REPORT['checks'].append({'case': label, 'passed': False, 'failure': error})
                print('FAIL capture-' + label + '\n' + error, flush=True)
            finally:
                context.close()
        browser.close()
except Exception:
    REPORT['harnessFailure'] = traceback.format_exc()
finally:
    REPORT['passed'] = bool(REPORT['checks']) and all(check['passed'] for check in REPORT['checks']) \
        and not REPORT.get('harnessFailure') and not REPORT['consoleErrors'] \
        and not REPORT['runtimeErrors'] and not REPORT['failedRequests']
    (OUT / os.environ.get('FRETLINE_QA_REPORT', 'capture.json')).write_text(
        json.dumps(REPORT, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if REPORT['passed'] else 1)
