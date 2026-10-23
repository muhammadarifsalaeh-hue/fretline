"""Focused real-browser Córdoba update QA; root starts/runs production preview.

No request interception, DOM styles, content substitutions or product-data edits.
Uses the existing Phase C measurement helpers with explicit photographic frames.
"""
from pathlib import Path
import json
import os
import sys
import traceback
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(os.environ.get('FRETLINE_QA_OUTPUT_DIR', str(Path(__file__).resolve().parents[1]))).resolve()
sys.path.insert(0, str(ROOT / 'docs/signature-redesign/phase-c/tests'))
from support import (BASE, VIEWPORTS, BRAND_ORDER, RECORDS, BY_ID, new_page, go,
                     sweep_home, brand_metrics, page_metrics, assert_brands,
                     assert_page, report_template)

REPORT = report_template()
REPORT['scope'] = 'Córdoba licensed background and same-photo authentic wordmark; all ten brand destinations; existing model identities unchanged.'
REPORT['metadataOnlyLimitation'] = 'Automated geometry and asset matching do not independently judge wordmark legibility or exact photographic subject crop; screenshots require visual review.'
SHOTS = OUT / 'after'
SHOTS.mkdir(parents=True, exist_ok=True)


def screenshot(page, locator, label):
    locator.scroll_into_view_if_needed()
    page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
    target = SHOTS / ('cordoba-card-' + label + '.png')
    locator.screenshot(path=str(target), animations='disabled')
    return str(target.relative_to(OUT))


try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('FRETLINE_CHROMIUM', '/usr/bin/chromium'), args=['--no-sandbox'])
        for width, height, label in VIEWPORTS:
            context, page = new_page(browser, REPORT, label, width, height)
            try:
                go(page)
                sweep_home(page)
                all_brands = brand_metrics(page)
                summary = assert_brands(all_brands, width)
                assert summary['licensedLogoSlots'] == 9 and summary['photographedWordmarks'] == 1, summary
                assert summary['brandPhotos'] == 10 and summary['explicitTextFallbacks'] == 0, summary
                cordoba = next(card for card in all_brands['cards'] if card['id'] == 'cordoba')
                assert len(cordoba['logo']) == len(cordoba['photos']) == 1 and not cordoba['fallback'], cordoba
                wordmark = cordoba['logo'][0]
                assert wordmark['kind'] == 'photographic' and wordmark['src'] == cordoba['photos'][0]['src'], cordoba
                assert (wordmark['naturalWidth'], wordmark['naturalHeight']) == (1920, 1280), wordmark
                assert wordmark['frame'] and wordmark['frame']['width'] < wordmark['rect']['width'], wordmark
                card = page.locator('#brands a[data-brand-id="cordoba"]')
                expect(card).to_have_accessible_name('สำรวจ Córdoba · 20 รุ่นในแคตตาล็อก')
                expect(card.locator('img[data-brand-logo]')).to_have_attribute('alt', 'Córdoba')
                expect(card.locator('[data-brand-logo-frame]')).to_be_visible()
                card.focus()
                expect(card).to_be_focused()
                image = screenshot(page, card, label)
                assert_page(page_metrics(page))
                if width <= 1024:
                    card.tap()
                else:
                    card.press('Enter')
                expect(page).to_have_url(BASE + '/brands/cordoba')
                expect(page.locator('.brand-models-section article[data-guitar-id]')).to_have_count(20)
                ids = page.locator('.brand-models-section article[data-guitar-id]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)')
                assert all(BY_ID[guitar]['brand'] == 'Córdoba' for guitar in ids), ids
                page.go_back(wait_until='networkidle')
                expect(page.locator('#brands a[data-brand-id="cordoba"]')).to_be_visible()
                REPORT['checks'].append({'case': 'cordoba-' + label, 'passed': True,
                                         'brands': summary, 'cordoba': cordoba,
                                         'screenshot': image, 'keyboardOrTouchNavigation': True,
                                         'brandDetailIDs': ids, 'browserBack': True})
                print('PASS cordoba-' + label, flush=True)
                if width == 1440:
                    destinations = []
                    for brand_id in BRAND_ORDER:
                        go(page)
                        page.locator('#brands a[data-brand-id="' + brand_id + '"]').click()
                        expect(page).to_have_url(BASE + '/brands/' + brand_id)
                        cards = page.locator('.brand-models-section article[data-guitar-id]')
                        expect(cards).to_have_count(20)
                        ids = cards.evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)')
                        assert len(ids) == len(set(ids)) == 20 and all(guitar in BY_ID for guitar in ids), ids
                        names = {BY_ID[guitar]['brand'] for guitar in ids}
                        assert len(names) == 1, names
                        expected = {guitar['id'] for guitar in RECORDS if guitar['brand'] in names}
                        assert set(ids) == expected, {'brand': brand_id, 'ids': ids, 'expected': sorted(expected)}
                        destinations.append({'brand': brand_id, 'modelCount': len(ids)})
                    REPORT['checks'].append({'case': 'all-brand-destinations', 'passed': True, 'destinations': destinations})
                    print('PASS all-brand-destinations', flush=True)
            except Exception:
                error = traceback.format_exc()
                REPORT['checks'].append({'case': label, 'passed': False, 'url': page.url, 'failure': error})
                print('FAIL ' + label + '\n' + error, flush=True)
            finally:
                context.close()
        browser.close()
except Exception:
    REPORT['harnessFailure'] = traceback.format_exc()
finally:
    REPORT['passed'] = bool(REPORT['checks']) and all(check['passed'] for check in REPORT['checks']) \
        and not REPORT.get('harnessFailure') and not REPORT['consoleErrors'] \
        and not REPORT['runtimeErrors'] and not REPORT['failedRequests']
    (OUT / 'browser.json').write_text(json.dumps(REPORT, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if REPORT['passed'] else 1)
