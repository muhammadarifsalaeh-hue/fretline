"""Shared browser QA helpers. No app mutations, request mocking or image replacement."""
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import os
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(os.environ.get('FRETLINE_QA_OUTPUT_DIR', str(Path(__file__).resolve().parents[1]))).resolve()
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:5203').rstrip('/')
VIEWPORTS = [(1440, 1000, 'desktop'), (1024, 768, 'tablet-landscape'),
             (768, 1024, 'tablet'), (390, 844, 'mobile'), (320, 740, 'small-mobile')]
PACIFICA = 'yamaha-pacifica-612viifm'
COMPARE_IDS = [PACIFICA, 'yamaha-fg800', 'fender-american-professional-ii-stratocaster',
               'gibson-les-paul-standard-60s']
BRAND_ORDER = ['yamaha', 'fender', 'gibson', 'taylor', 'ibanez', 'prs',
               'epiphone', 'martin', 'squier', 'cordoba']


def catalogue_records():
    """Read identity/category/featured facts, without evaluating application code.

    This deliberately narrow reader matches the legacy source format used by the
    repository validator. It is not another trust/price/recommendation algorithm.
    The existing npm checks remain authoritative for the complete dataset.
    """
    source = (ROOT / 'src/data/guitars.js').read_text()
    raw = source.split('const raw = [', 1)[1].split('\n];', 1)[0]
    records = []
    for block in re.split(r'\n  \{\n', raw)[1:]:
        record = {}
        for field in ['id', 'brand', 'name', 'category']:
            match = re.search(r"\b" + field + r": '((?:[^'\\]|\\.)*)'", block)
            assert match, ('Legacy identity reader needs review', field, block[:80])
            record[field] = match.group(1).replace("\\'", "'")
        featured = re.search(r'\bfeatured: (true|false)', block)
        record['featured'] = bool(featured and featured.group(1) == 'true')
        records.append(record)
    data = ROOT / 'src/data/catalog'
    records += json.loads((data / 'extraGuitars.json').read_text())
    records += json.loads((data / 'phase7Guitars.json').read_text())
    reviewed = json.loads((data / 'reviewedGuitars.json').read_text())
    archived = set(json.loads((data / 'catalogPolicy.json').read_text())['archivedIds'])
    return [{**record, **reviewed.get(record['id'], {}), 'id': record['id']}
            for record in records if record['id'] not in archived]


RECORDS = catalogue_records()
BY_ID = {record['id']: record for record in RECORDS}
CATEGORY_COUNTS = dict(Counter(record['category'] for record in RECORDS))
BRAND_COUNTS = dict(Counter(record['brand'] for record in RECORDS))


def report_template():
    return {'baseURL': BASE, 'browser': 'Chromium on Linux; physical Safari/iPad not tested',
            'checks': [], 'consoleErrors': [], 'runtimeErrors': [], 'failedRequests': []}


def new_page(browser, report, case, width=1440, height=1000):
    context = browser.new_context(viewport={'width': width, 'height': height},
                                  has_touch=width <= 1024, reduced_motion='reduce')
    context.add_init_script('''if (!sessionStorage.getItem('phase-c-qa-seeded')) {
      localStorage.setItem('fretline:compare', '[]');
      localStorage.setItem('fretline:wishlist', '[]');
      sessionStorage.setItem('phase-c-qa-seeded', 'true');
    }''')
    page = context.new_page()
    page.on('console', lambda msg: report['consoleErrors'].append({'case': case, 'text': msg.text})
            if msg.type == 'error' else None)
    page.on('pageerror', lambda err: report['runtimeErrors'].append({'case': case, 'text': str(err)}))
    page.on('requestfailed', lambda req: report['failedRequests'].append(
        {'case': case, 'url': req.url, 'failure': req.failure}))
    return context, page


def go(page, route='/'):
    page.goto(BASE + route, wait_until='networkidle')
    page.locator('#main-content h1').wait_for(state='visible')
    page.evaluate('document.fonts.ready')


def query(page):
    return parse_qs(urlparse(page.url).query)


def stored(page, key):
    return page.evaluate('(key) => JSON.parse(localStorage.getItem(key) || "[]")',
                         'fretline:' + key)


# Ancestor opacity matters for responsive duplicate/hidden artwork. Image opacity
# itself is intentionally not a visibility exclusion: SmartImage must really load
# and paint before a screenshot is considered ready. Horizontally clipped carousel
# items are excluded until genuinely scrolled into the rail.
RENDERED_IMAGES = r'''() => [...document.images].filter(img => {
  let box=img.getBoundingClientRect();
  if(box.width<=0||box.height<=0)return false;
  let left=box.left,right=box.right,top=box.top,bottom=box.bottom;
  for(let node=img;node;node=node.parentElement){
    const s=getComputedStyle(node),r=node.getBoundingClientRect();
    if(s.display==='none'||s.visibility==='hidden'||node.hidden||node.inert)return false;
    if(node!==img&&Number(s.opacity)===0)return false;
    if(node!==img&&/hidden|clip|auto|scroll/.test(s.overflowX)){left=Math.max(left,r.left);right=Math.min(right,r.right)}
    if(node!==img&&/hidden|clip|auto|scroll/.test(s.overflowY)){top=Math.max(top,r.top);bottom=Math.min(bottom,r.bottom)}
  }
  return right-left>1&&bottom-top>1;
})'''

VIEWPORT_IMAGES = '(' + RENDERED_IMAGES + ')().filter(img => {const r=img.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth})'


def viewport_paint_ready(page):
    """Let lazy assets load and decode while their actual viewport is displayed."""
    page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
    page.wait_for_function('() => ' + VIEWPORT_IMAGES +
                           '.every(img=>img.complete&&img.naturalWidth>0)', timeout=15000)
    page.evaluate('async () => Promise.all(' + VIEWPORT_IMAGES + '.map(img=>img.decode()))')
    page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')


def paint_ready(page):
    page.evaluate('document.fonts.ready')
    page.wait_for_function(RENDERED_IMAGES +
        '.every(img=>img.complete&&img.naturalWidth>0&&Number(getComputedStyle(img).opacity)>0)',
        timeout=15000)
    page.evaluate('async () => Promise.all((' + RENDERED_IMAGES + ')().map(img=>img.decode()))')
    page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')


def sweep_home(page):
    """Use actual scrolling to reveal sections and trigger native lazy loading."""
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    step = max(250, round(page.viewport_size['height'] * .7))
    height = page.evaluate('document.documentElement.scrollHeight')
    for position in range(0, height, step):
        page.evaluate('(top)=>window.scrollTo({top,behavior:"instant"})', position)
        viewport_paint_ready(page)
    page.evaluate('window.scrollTo({top:document.documentElement.scrollHeight,behavior:"instant"})')
    viewport_paint_ready(page)
    # Every brand card has genuinely entered the viewport above. Wait for ALL
    # brand images, not just images surviving an ancestor/clip visibility filter.
    # This prevents full-page capture racing decode/compositing of card photos.
    page.wait_for_function('''() => [...document.querySelectorAll('#brands img')]
      .every(img=>img.complete&&img.naturalWidth>0)''', timeout=15000)
    page.evaluate('''async () => Promise.all([...document.querySelectorAll('#brands img')]
      .map(img=>img.decode()))''')
    page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    viewport_paint_ready(page)
    paint_ready(page)


def page_metrics(page):
    return page.evaluate(r'''() => ({
      viewport:{width:innerWidth,height:innerHeight},
      scrollWidth:document.documentElement.scrollWidth,
      documentHeight:document.documentElement.scrollHeight,
      headings:[...document.querySelectorAll('h1')].filter(e=>e.getBoundingClientRect().width>0).map(e=>e.textContent.trim()),
      brokenImages:[...document.images].filter(i=>i.currentSrc&&i.complete&&i.naturalWidth===0).map(i=>i.currentSrc),
      sections:[...document.querySelectorAll('main section[id]')].map(e=>({id:e.id,top:e.getBoundingClientRect().top+scrollY,height:e.getBoundingClientRect().height})),
      resources:performance.getEntriesByType('resource').map(e=>({name:e.name,type:e.initiatorType,bytes:e.transferSize,duration:e.duration}))
    })''')


def brand_metrics(page):
    return page.locator('#brands').evaluate(r'''section => {
      const rect=e=>{if(!e)return null;const r=e.getBoundingClientRect();return {left:r.left,top:r.top,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
      const grid=section.querySelector('[data-brand-grid]');
      const cards=[...section.querySelectorAll('a[data-brand-id]')].map(a=>({
        id:a.dataset.brandId,href:a.getAttribute('href'),label:a.getAttribute('aria-label'),text:a.textContent.trim(),rect:rect(a),
        logo:[...a.querySelectorAll('img[data-brand-logo]')].map(i=>{
          const frame=i.closest('[data-brand-logo-frame]');
          return {src:i.currentSrc,alt:i.alt,rect:rect(i),naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,
            complete:i.complete,fit:getComputedStyle(i).objectFit,kind:i.dataset.brandLogoKind ?? 'file',
            frame:rect(frame),frameOverflow:frame?getComputedStyle(frame).overflow:null};
        }),
        photos:[...a.querySelectorAll('img.signature-brand-photo')].map(i=>({src:i.currentSrc,rect:rect(i),naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,complete:i.complete,fit:getComputedStyle(i).objectFit})),
        fallback:[...a.querySelectorAll('[data-brand-fallback]')].map(e=>({text:e.textContent.trim(),rect:rect(e)})),
        count:rect(a.querySelector('[data-brand-count]')),
        countText:a.querySelector('[data-brand-count]')?.textContent.trim() ?? null,
        arrow:rect(a.querySelector('.signature-brand-arrow')),
        imageCount:a.querySelectorAll('img').length
      }));
      return {section:rect(section),grid:rect(grid),columns:grid?getComputedStyle(grid).gridTemplateColumns:null,cards};
    }''')


def assert_page(metrics):
    assert metrics['scrollWidth'] <= metrics['viewport']['width'] + 1, metrics
    assert len(metrics['headings']) == 1, metrics
    assert not metrics['brokenImages'], metrics


def assert_brands(metrics, width):
    cards = metrics['cards']
    assert [card['id'] for card in cards] == BRAND_ORDER, metrics
    expected_columns = 5 if width >= 1280 else 3 if width >= 900 else 2
    assert len(metrics['columns'].split()) == expected_columns, metrics
    assert max(card['rect']['height'] for card in cards) - min(card['rect']['height'] for card in cards) <= 1, metrics
    assert sum(len(card['photos']) for card in cards) == 10, metrics
    rows = Counter(round(card['rect']['top']) for card in cards)
    assert sorted(rows.values(), reverse=True)[0] == expected_columns, metrics
    for card in cards:
        assert card['href'] == '/brands/' + card['id'], card
        assert card['countText'] and re.search(r'\b20\b', card['countText']), card
        assert card['arrow'] and min(card['arrow']['width'], card['arrow']['height']) >= 43.5, card
        assert len(card['photos']) == 1, card
        for photo in card['photos']:
            assert photo['complete'] and photo['naturalWidth'] > 0 and photo['naturalHeight'] > 0, card
            assert re.search(r'/' + re.escape(card['id']) + r'(?:[-.])', photo['src']), card
        if card['id'] == 'cordoba':
            # Final polish uses the user-approved temporary typography. Keep the
            # licensed photograph as the background, never pose text as an
            # officially supplied logo or reuse its photographed sign as a mark.
            assert not card['logo'] and len(card['fallback']) == 1, card
            assert card['fallback'][0]['text'] == 'Córdoba', card
            visible_mark = card['fallback'][0]['rect']
        else:
            assert len(card['logo']) == 1 and not card['fallback'], card
            logo = card['logo'][0]
            assert logo['complete'] and logo['naturalWidth'] > 0 and logo['naturalHeight'] > 0, card
            assert logo['kind'] != 'photographic' and logo['fit'] == 'contain', card
            visible_mark = logo['rect']
        assert visible_mark['left'] >= card['rect']['left'] - 1, card
        assert visible_mark['right'] <= card['rect']['right'] + 1, card
        assert visible_mark['top'] >= card['rect']['top'] - 1, card
        assert visible_mark['bottom'] <= card['rect']['bottom'] + 1, card
        if card['count']:
            # Count and arrow may share a horizontal row, but not the same pixels.
            a, b = card['count'], card['arrow']
            overlap = min(a['right'], b['right']) - max(a['left'], b['left'])
            vertical = min(a['bottom'], b['bottom']) - max(a['top'], b['top'])
            assert overlap <= 1 or vertical <= 1, card
    return {'columns': expected_columns, 'cards': len(cards),
            'licensedLogoSlots': sum(bool(card['logo']) and card['logo'][0]['kind'] != 'photographic' for card in cards),
            'photographedWordmarks': sum(bool(card['logo']) and card['logo'][0]['kind'] == 'photographic' for card in cards),
            'brandPhotos': sum(len(card['photos']) for card in cards),
            'explicitTextFallbacks': sum(bool(card['fallback']) for card in cards)}
