"""Phase C actual Homepage acceptance; run against an existing production server.

Optional FRETLINE_QA_CASES=identity,search,featured,categories,brands,quiz,compare,responsive
Every case records its own evidence/failure. No mocked requests or application edits.
"""
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect
import json
import os
import re
import traceback
from support import (BASE, OUT, VIEWPORTS, PACIFICA, COMPARE_IDS, RECORDS, BY_ID,
                     BRAND_ORDER, BRAND_COUNTS, CATEGORY_COUNTS, new_page, go,
                     query, stored, sweep_home, paint_ready, page_metrics,
                     brand_metrics, assert_page, assert_brands, report_template)

REPORT = report_template()
(OUT / 'failures').mkdir(parents=True, exist_ok=True)


def identity(page):
    assert len(RECORDS) == len(BY_ID) == 200, len(RECORDS)
    assert len(BRAND_COUNTS) == 10 and set(BRAND_COUNTS.values()) == {20}, BRAND_COUNTS
    names = [re.sub(r'[^a-z0-9]', '', (record['brand'] + record['name']).lower())
             for record in RECORDS]
    assert len(set(names)) == 200, 'Duplicate brand/model identity'
    go(page)
    expect(page.locator('.signature-home')).to_have_count(1)
    assert_page(page_metrics(page))
    return {'models': len(RECORDS), 'uniqueIDs': len(BY_ID),
            'brands': BRAND_COUNTS, 'categories': CATEGORY_COUNTS}


def search(page):
    go(page)
    searchbox = page.locator('#hero-search')
    expect(searchbox).to_have_attribute('role', 'combobox')
    searchbox.fill('612VIIFM')
    expect(page.locator('#search-results [role="option"]')).to_have_count(1)
    searchbox.press('ArrowDown')
    expect(searchbox).to_have_attribute('aria-activedescendant', 'search-option-0')
    expect(page.locator('#search-option-0')).to_have_attribute('aria-selected', 'true')
    searchbox.press('Enter')
    expect(page).to_have_url(BASE + '/guitars/' + PACIFICA)
    expect(page.locator('.detail-summary h1')).to_have_text('Pacifica 612VIIFM')
    page.go_back(wait_until='networkidle')
    expect(page.locator('#hero-search')).to_be_visible()
    page.go_forward(wait_until='networkidle')
    expect(page.locator('.detail-summary h1')).to_have_text('Pacifica 612VIIFM')
    go(page)
    searchbox.fill('Yamaha')
    expect(page.locator('#search-results [role="option"]')).to_have_count(5)
    searchbox.press('ArrowUp')
    expect(page.locator('#search-option-4')).to_have_attribute('aria-selected', 'true')
    searchbox.press('Escape')
    expect(searchbox).to_have_attribute('aria-expanded', 'false')
    expect(searchbox).to_have_value('Yamaha')
    assert urlparse(page.url).path == '/'
    searchbox.fill('  612VIIFM  ')
    searchbox.press('Enter')
    expect(page).to_have_url(re.compile(r'/guitars\?q=612VIIFM$'))
    expect(page.locator('.catalog-grid article[data-guitar-id]')).to_have_count(1)
    assert page.locator('.catalog-grid article').get_attribute('data-guitar-id') == PACIFICA
    chip_queries = [{'max': ['20000']}, {'q': ['ผู้เริ่มต้น']}, {'q': ['มือซ้าย']},
                    {'type': ['acoustic']}, {'type': ['electric']}]
    for index, expected in enumerate(chip_queries):
        go(page)
        chips = page.locator('#search ul a')
        expect(chips).to_have_count(5)
        assert chips.nth(index).bounding_box()['height'] >= 43.5
        chips.nth(index).click()
        expect(page.locator('#catalog-search')).to_be_visible()
        assert query(page) == expected, (index, page.url, expected)
    go(page)
    searchbox.fill('no-such-model-phase-c')
    expect(page.locator('#search-results')).to_be_visible()
    expect(page.locator('#search-results [role="option"]')).to_have_count(0)
    return {'keyboardAutocomplete': 'Down/Up, active descendant, Enter, Escape',
            'trimmedSearchSubmit': True, 'quickFilterQueries': chip_queries,
            'detailHistory': 'Back and Forward'}


def card_ids(page):
    return page.locator('#featured article[data-guitar-id]').evaluate_all(
        '(nodes)=>nodes.map(node=>node.dataset.guitarId)')


def press_card_action(page, guitar_id, index):
    button = page.locator('#featured article[data-guitar-id="' + guitar_id + '"] button').nth(index)
    button.focus()
    button.press('Space')
    return button


def featured(page):
    go(page)
    expected_original = {g['id'] for g in RECORDS if g.get('featured')}
    actual = card_ids(page)
    assert len(actual) == len(set(actual)), actual
    assert expected_original <= set(actual), {'missingOriginalFeatured': list(expected_original - set(actual))}
    assert actual[:3] == [PACIFICA, 'martin-d-28', 'yamaha-fg820-12'], actual
    expect(page.locator('#featured article[data-guitar-id="' + PACIFICA + '"]')).to_contain_text('฿34,000')
    page.locator('#featured-tab-electric').focus()
    page.keyboard.press('ArrowRight')
    expect(page.locator('#featured-tab-acoustic')).to_be_focused()
    expect(page.locator('#featured-tab-acoustic')).to_have_attribute('aria-selected', 'true')
    assert set(card_ids(page)) == {g['id'] for g in RECORDS if g['category'] == 'acoustic'}
    page.keyboard.press('End')
    expect(page.locator('#featured-tab-bass')).to_be_focused()
    assert set(card_ids(page)) == {g['id'] for g in RECORDS if g['category'] == 'bass'}
    page.keyboard.press('Home')
    expect(page.locator('#featured-tab-all')).to_have_attribute('aria-selected', 'true')
    for category in ['electric', 'acoustic', 'bass']:
        page.locator('#featured-tab-' + category).click()
        assert set(card_ids(page)) == {g['id'] for g in RECORDS if g['category'] == category}
    page.locator('#featured-tab-all').click()
    track = page.locator('#featured-models')
    track.scroll_into_view_if_needed()
    expect(track).to_have_attribute('role', 'tabpanel')
    assert track.evaluate('(e)=>e.scrollWidth>e.clientWidth+1'), 'Collection lost its horizontal rail'
    if page.viewport_size['width'] >= 768:
        page.locator('#featured').get_by_role('button', name='กีตาร์ถัดไป', exact=True).click()
        page.wait_for_function('document.querySelector("#featured-models").scrollLeft > 10')
        page.locator('#featured').get_by_role('button', name='กีตาร์ก่อนหน้า', exact=True).click()
        page.wait_for_function('document.querySelector("#featured-models").scrollLeft < 5')
    else:
        track.focus()
        page.keyboard.press('ArrowRight')
        page.wait_for_function('document.querySelector("#featured-models").scrollLeft > 1')
    # Use the actual card controls, including focus behavior of hover-hidden actions.
    save = press_card_action(page, PACIFICA, 0)
    expect(save).to_have_attribute('aria-pressed', 'true')
    page.wait_for_function('(id)=>JSON.parse(localStorage.getItem("fretline:wishlist")).includes(id)', arg=PACIFICA)
    compare_button = press_card_action(page, PACIFICA, 1)
    expect(compare_button).to_have_attribute('aria-pressed', 'true')
    assert stored(page, 'compare') == [PACIFICA]
    go(page, '/wishlist')
    expect(page.locator('.wishlist-row')).to_have_count(1)
    expect(page.locator('.wishlist-row')).to_contain_text('Pacifica 612VIIFM')
    page.reload(wait_until='networkidle')
    expect(page.locator('.wishlist-row')).to_have_count(1)
    go(page)
    expect(page.locator('#featured article[data-guitar-id="' + PACIFICA + '"] button').nth(0)).to_have_attribute('aria-pressed', 'true')
    press_card_action(page, PACIFICA, 0)
    assert stored(page, 'wishlist') == []
    press_card_action(page, PACIFICA, 1)
    assert stored(page, 'compare') == []
    # Add four through the same shared controls; a fifth is disabled, never duplicated.
    selectable = card_ids(page)[:5]
    for guitar_id in selectable[:4]:
        control = press_card_action(page, guitar_id, 1)
        expect(control).to_have_attribute('aria-pressed', 'true')
    assert stored(page, 'compare') == selectable[:4]
    expect(page.locator('#featured article[data-guitar-id="' + selectable[4] + '"] button').nth(1)).to_be_disabled()
    assert len(stored(page, 'compare')) == len(set(stored(page, 'compare'))) == 4
    press_card_action(page, selectable[0], 1)
    assert stored(page, 'compare') == selectable[1:4]
    return {'originalFeaturedPreserved': len(expected_original), 'allRailIDs': actual,
            'tabsExactCategorySets': True, 'keyboardTabs': True, 'carousel': True,
            'wishlistCrossPageReloadRemove': True, 'compareFourLimitRemove': True}


def categories(page):
    results = []
    for category, count in CATEGORY_COUNTS.items():
        go(page)
        links = page.locator('#categories a[href^="/guitars?type="]')
        expect(links).to_have_count(4)
        card = page.locator('#categories a[href="/guitars?type=' + category + '"]')
        expect(card).to_have_count(1)
        assert re.search(r'\b' + str(count) + r'\b', card.inner_text()), (category, count, card.inner_text())
        card.click()
        expect(page.locator('#catalog-search')).to_be_visible()
        assert query(page).get('type') == [category], page.url
        expect(page.locator('.catalog-result-count')).to_contain_text(str(count))
        results.append({'category': category, 'actualCatalogModels': count})
    assert sum(CATEGORY_COUNTS.values()) == 200, CATEGORY_COUNTS
    return results


def brands(page):
    go(page)
    sweep_home(page)
    metrics = brand_metrics(page)
    result = assert_brands(metrics, page.viewport_size['width'])
    squier = page.locator('#brands [data-brand-id="squier"] [data-brand-logo]')
    assert squier.evaluate('(e)=>getComputedStyle(e).filter') == 'none', 'Preserve white Squier letters on its genuine dark oval'
    links = page.locator('#brands a[data-brand-id]')
    first = links.first
    first.focus()
    expect(first).to_be_focused()
    focus = first.evaluate('''a=>{const s=getComputedStyle(a);return {
      focusVisible:a.matches(':focus-visible'),outlineStyle:s.outlineStyle,
      outlineWidth:s.outlineWidth,outlineColor:s.outlineColor,boxShadow:s.boxShadow}}''')
    assert focus['focusVisible'], focus
    assert (focus['outlineStyle'] != 'none' and float(focus['outlineWidth'].replace('px', '')) > 0) or focus['boxShadow'] != 'none', focus
    page.keyboard.press('Enter')
    expect(page).to_have_url(BASE + '/brands/yamaha')
    expect(page.locator('.brand-models-section article[data-guitar-id]')).to_have_count(20)
    assert all(guitar.startswith('yamaha-') for guitar in page.locator('.brand-models-section article').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.guitarId)'))
    if page.viewport_size['width'] == 1440:
        # All ten destinations must resolve actual twenty-model brand collections.
        for brand_id in BRAND_ORDER[1:]:
            go(page)
            page.locator('#brands a[data-brand-id="' + brand_id + '"]').click()
            expect(page).to_have_url(BASE + '/brands/' + brand_id)
            expect(page.locator('.brand-models-section article[data-guitar-id]')).to_have_count(20)
    elif page.viewport_size['width'] <= 1024:
        go(page)
        page.locator('#brands a[data-brand-id="cordoba"]').tap()
        expect(page).to_have_url(BASE + '/brands/cordoba')
        expect(page.locator('.brand-models-section article[data-guitar-id]')).to_have_count(20)
    return {**result, 'geometry': metrics, 'keyboardWholeCard': True,
            'allBrandDestinationsChecked': page.viewport_size['width'] == 1440,
            'touchWholeCard': page.viewport_size['width'] <= 1024, 'focus': focus}


def quiz(page):
    go(page)
    link = page.locator('#find a[href="/find-my-guitar"]').first
    expect(link).to_be_visible()
    link.click()
    expect(page).to_have_url(BASE + '/find-my-guitar')
    expect(page.get_by_role('button', name='เริ่มค้นหากีตาร์', exact=True)).to_be_visible()
    options = []
    for category in ['electric', 'acoustic', 'classical', 'bass']:
        go(page)
        option = page.locator('#find a[data-home-quiz-option="' + category + '"]')
        expect(option).to_have_count(1)
        option.click()
        expect(page.locator('#quiz-type-title')).to_be_visible()
        expect(page.locator('input[name="type"][value="' + category + '"]')).to_be_checked()
        assert query(page).get('type') == [category] and query(page).get('step') == ['1'], page.url
        options.append(category)
    return {'welcomeCTA': True, 'realQuizPrefillLinks': options}


def home_compare(page):
    go(page)
    expect(page.locator('#compare [data-home-compare-remove]')).to_have_count(0)
    expect(page.locator('#compare [data-home-compare-panel]')).to_be_hidden()
    expect(page.locator('#compare .compare-table-scroll')).to_have_count(0)
    expand = page.locator('#compare [data-home-compare-expand]')
    expect(expand).to_have_attribute('aria-expanded', 'false')
    expand.focus()
    expand.press('Enter')
    expect(expand).to_have_attribute('aria-expanded', 'true')
    expect(page.locator('#compare .compare-table-scroll')).to_be_visible()
    expand.press('Enter')
    expect(page.locator('#compare [data-home-compare-panel]')).to_be_hidden()
    expect(page.locator('#compare .compare-table-scroll')).to_have_count(0)
    selections = []
    for count in [2, 3, 4]:
        go(page, '/compare?ids=' + ','.join(COMPARE_IDS[:count]))
        expect(page.locator('[data-compare-remove]')).to_have_count(count)
        go(page)
        expect(page.locator('#compare [data-home-compare-remove]')).to_have_count(count)
        selected_ids = page.locator('#compare [data-home-compare-remove]').evaluate_all('(nodes)=>nodes.map(e=>e.dataset.homeCompareRemove)')
        assert selected_ids == COMPARE_IDS[:count], selected_ids
        expect(page.locator('#compare .home-compare-preview-table')).to_contain_text('ราคาขายปลีกแนะนำ')
        expand = page.locator('#compare [data-home-compare-expand]')
        expand.click()
        expect(page.locator('#compare [data-compare-remove]')).to_have_count(count)
        switch = page.locator('#compare [role="switch"]')
        expect(switch).to_have_attribute('aria-checked', 'true')
        diff_rows = page.locator('#compare [data-home-compare-panel]').get_by_role('row').count()
        switch.click()
        expect(switch).to_have_attribute('aria-checked', 'false')
        all_rows = page.locator('#compare [data-home-compare-panel]').get_by_role('row').count()
        assert all_rows >= diff_rows > 0, {'onlyDifferent': diff_rows, 'all': all_rows}
        switch.focus()
        switch.press('Space')
        expect(switch).to_have_attribute('aria-checked', 'true')
        region = page.locator('#compare .compare-table-scroll')
        if page.viewport_size['width'] < 1024:
            assert region.evaluate('(e)=>e.scrollWidth>e.clientWidth'), 'Expanded comparison needs its own scroll region'
            region.focus()
            region.press('ArrowRight')
            page.wait_for_function('document.querySelector("#compare .compare-table-scroll").scrollLeft>0')
        assert_page(page_metrics(page))
        expand.click()
        expect(page.locator('#compare [data-home-compare-panel]')).to_be_hidden()
        expect(page.locator('#compare .compare-table-scroll')).to_have_count(0)
        selections.append({'models': count, 'onlyDifferentRows': diff_rows, 'allRows': all_rows})
    page.locator('#compare [data-home-compare-remove="' + COMPARE_IDS[0] + '"]').click()
    expect(page.locator('#compare [data-home-compare-remove]')).to_have_count(3)
    assert stored(page, 'compare') == COMPARE_IDS[1:4]
    expand.click()
    page.locator('#compare [data-compare-remove="' + COMPARE_IDS[1] + '"]').click()
    expect(page.locator('#compare [data-home-compare-remove]')).to_have_count(2)
    assert stored(page, 'compare') == COMPARE_IDS[2:4]
    detail = page.locator('#compare [data-home-compare-panel] a[href="/guitars/' + COMPARE_IDS[2] + '"]').first
    detail.click()
    expect(page.locator('.detail-summary h1')).to_be_visible()
    assert urlparse(page.url).path == '/guitars/' + COMPARE_IDS[2]
    page.go_back(wait_until='networkidle')
    expect(page.locator('#compare [data-home-compare-remove]')).to_have_count(2)
    return {'sampleStillAvailable': True, 'liveSelections': selections,
            'previewAndFullTableRemove': True, 'differencesKeyboardToggle': True,
            'detailAndBrowserBack': True}


def responsive(page):
    go(page)
    sweep_home(page)
    metrics = page_metrics(page)
    assert_page(metrics)
    assert_brands(brand_metrics(page), page.viewport_size['width'])
    expect(page.locator('#hero-search')).to_be_visible()
    expect(page.locator('#featured article[data-guitar-id="' + PACIFICA + '"]')).to_have_count(1)
    ids = [section['id'] for section in metrics['sections']]
    for required in ['top', 'featured', 'categories', 'brands', 'find', 'compare']:
        assert required in ids, {'missingSection': required, 'sections': ids}
    return metrics


CASES = {'identity': identity, 'search': search, 'featured': featured,
         'categories': categories, 'brands': brands, 'quiz': quiz,
         'compare': home_compare, 'responsive': responsive}
selected = set(filter(None, os.environ.get('FRETLINE_QA_CASES', '').split(',')))
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('FRETLINE_CHROMIUM', '/usr/bin/chromium'),
                                    args=['--no-sandbox'])
        for name, test in CASES.items():
            if selected and name not in selected:
                continue
            sizes = VIEWPORTS if name in ['brands', 'responsive'] else [VIEWPORTS[0]]
            if name in ['search', 'featured', 'quiz', 'compare']:
                sizes = [VIEWPORTS[0], VIEWPORTS[3]]
            for width, height, label in sizes:
                case = name + '-' + label
                context, page = new_page(browser, REPORT, case, width, height)
                try:
                    details = test(page)
                    REPORT['checks'].append({'case': case, 'passed': True, 'details': details})
                    print('PASS ' + case, flush=True)
                except Exception:
                    failure = traceback.format_exc()
                    screenshot = OUT / 'failures' / (case + '.png')
                    try:
                        page.screenshot(path=str(screenshot), full_page=True)
                    except Exception as error:
                        failure += '\nFailure screenshot unavailable: ' + str(error)
                    REPORT['checks'].append({'case': case, 'passed': False, 'failure': failure,
                                             'url': page.url, 'screenshot': str(screenshot.relative_to(OUT))})
                    print('FAIL ' + case + '\n' + failure, flush=True)
                finally:
                    context.close()
        browser.close()
except Exception:
    REPORT['harnessFailure'] = traceback.format_exc()
finally:
    REPORT['passed'] = bool(REPORT['checks']) and all(check['passed'] for check in REPORT['checks']) \
        and not REPORT.get('harnessFailure') and not REPORT['consoleErrors'] \
        and not REPORT['runtimeErrors'] and not REPORT['failedRequests']
    target = OUT / os.environ.get('FRETLINE_QA_REPORT', 'home-acceptance.json')
    target.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if REPORT['passed'] else 1)
