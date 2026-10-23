"""Read-only QA for the restored Home marquee and existing Brand Directory.

Reuse the existing source identity reader, navigation, image waits and error
listeners. No application data/styles, HTTP responses or screenshots are mocked.
"""
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from collections import Counter
import os
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(os.environ.get('FRETLINE_QA_OUTPUT_DIR', str(Path(__file__).resolve().parents[1]))).resolve()
OUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('FRETLINE_QA_OUTPUT_DIR', str(OUT))
sys.path.insert(0, str(ROOT / 'docs/signature-redesign/phase-c/tests'))
from support import (BASE, VIEWPORTS, RECORDS, BY_ID, report_template, go,
                     viewport_paint_ready, paint_ready, page_metrics, assert_page,
                     new_page as shared_new_page)


def brand_id(name):
    return ''.join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c)).lower()


BRAND_COUNTS = Counter(r['brand'] for r in RECORDS)
BRAND_NAMES = {brand_id(name): name for name in BRAND_COUNTS}
BRAND_IDS = set(BRAND_NAMES)


def new_page(browser, report, case, width=1440, height=1000, motion='reduce'):
    context, page = shared_new_page(browser, report, case, width, height)
    page.emulate_media(reduced_motion=motion)
    return context, page


def sweep(page):
    """Scroll the real document to trigger native images/reveals, then return."""
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    step = max(240, round(page.viewport_size['height'] * .7))
    height = page.evaluate('document.documentElement.scrollHeight')
    for position in range(0, height, step):
        page.evaluate('(top)=>window.scrollTo({top,behavior:"instant"})', position)
        viewport_paint_ready(page)
    viewport = page.locator('[data-marquee-viewport]')
    if viewport.count() and viewport.evaluate('e=>/auto|scroll/.test(getComputedStyle(e).overflowX)'):
        extent = viewport.evaluate('e=>e.scrollWidth-e.clientWidth')
        for position in range(0, int(extent) + step, step):
            viewport.evaluate('(e,left)=>e.scrollTo({left,behavior:"instant"})', position)
            viewport_paint_ready(page)
        viewport.evaluate('e=>e.scrollTo({left:0,behavior:"instant"})')
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    viewport_paint_ready(page)
    paint_ready(page)


def marquee_metrics(page):
    return page.locator('#brands').evaluate(r'''section=>{
      const rect=e=>{if(!e)return null;const r=e.getBoundingClientRect();return {left:r.left,top:r.top,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
      const style=e=>{if(!e)return null;const s=getComputedStyle(e);return {display:s.display,visibility:s.visibility,opacity:s.opacity,transform:s.transform,animation:s.animationName,animationDuration:s.animationDuration,animationTiming:s.animationTimingFunction,animationPlayState:s.animationPlayState,overflowX:s.overflowX,pointerEvents:s.pointerEvents}};
      const track=section.querySelector('.signature-marquee-track'),viewport=section.querySelector('[data-marquee-viewport]');
      const link=a=>({id:a.dataset.brandId,href:a.getAttribute('href'),label:a.getAttribute('aria-label'),text:a.textContent.trim(),rect:rect(a),tabIndex:a.tabIndex,inert:Boolean(a.closest('[inert]')),style:style(a),
        logos:[...a.querySelectorAll('[data-brand-logo]')].map(i=>({src:i.currentSrc,alt:i.alt,rect:rect(i),complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,fit:getComputedStyle(i).objectFit})),
        fallback:[...a.querySelectorAll('[data-brand-fallback]')].map(e=>({text:e.textContent.trim(),rect:rect(e)}))});
      return {rect:rect(section),className:section.className,manual:section.dataset.manual,
        viewport:{rect:rect(viewport),style:style(viewport),scrollLeft:viewport?.scrollLeft,scrollWidth:viewport?.scrollWidth,clientWidth:viewport?.clientWidth},
        track:{rect:rect(track),style:style(track),scrollWidth:track?.scrollWidth,
          animations:track?[...track.getAnimations()].map(a=>({name:a.animationName,playState:a.playState,currentTime:a.currentTime,timing:a.effect.getComputedTiming(),keyframes:a.effect.getKeyframes()})):[]},
        groups:[...section.querySelectorAll('.signature-marquee-group')].map(g=>({primary:g.hasAttribute('data-marquee-primary'),ariaHidden:g.getAttribute('aria-hidden'),inert:g.inert,rect:rect(g),style:style(g),links:[...g.querySelectorAll('a[data-brand-id]')].map(link)})),
        photos:section.querySelectorAll('[data-brand-photo],.signature-brand-photo').length,
        controls:[...section.querySelectorAll('button')].map(b=>({label:b.getAttribute('aria-label')||b.textContent.trim(),rect:rect(b),pressed:b.getAttribute('aria-pressed')}))};
    }''')


def directory_metrics(page):
    return page.locator('.brands-page').evaluate(r'''section=>{
      const box=r=>({left:r.left,top:r.top,width:r.width,height:r.height,right:r.right,bottom:r.bottom});
      const rect=e=>e?box(e.getBoundingClientRect()):null;
      const visibleTextRects=e=>{
        if(!e)return [];
        const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT),rects=[];
        let text;
        while(text=walker.nextNode()){
          if(!text.nodeValue.trim())continue;
          let visible=true;
          for(let node=text.parentElement;node;node=node.parentElement){
            const s=getComputedStyle(node);
            if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0||node.hidden){visible=false;break}
            if(node===e)break;
          }
          if(!visible)continue;
          const range=document.createRange();range.selectNodeContents(text);
          rects.push(...[...range.getClientRects()].filter(r=>r.width>0&&r.height>0).map(box));
        }
        return rects;
      };
      const grid=section.querySelector('.brand-directory-grid');
      return {rect:rect(section),columns:grid?getComputedStyle(grid).gridTemplateColumns:null,grid:rect(grid),
        cards:[...section.querySelectorAll('.brand-directory-card[data-brand-id]')].map(a=>{
          const count=a.querySelector('[data-brand-count],.brand-card-count');
          return {id:a.dataset.brandId,href:a.getAttribute('href'),label:a.getAttribute('aria-label'),text:a.textContent.trim(),rect:rect(a),
          photos:[...a.querySelectorAll('[data-brand-photo]')].map(i=>({src:i.currentSrc,rect:rect(i),complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight})),
          logos:[...a.querySelectorAll('[data-brand-logo]')].map(i=>({src:i.currentSrc,alt:i.alt,rect:rect(i),complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,fit:getComputedStyle(i).objectFit})),
          fallback:[...a.querySelectorAll('[data-brand-fallback]')].map(e=>({text:e.textContent.trim(),rect:rect(e)})),
          count:count?.innerText.trim(),countRect:rect(count),countTextRects:visibleTextRects(count),
          types:a.querySelector('.brand-card-types')?.textContent.trim(),arrow:rect(a.querySelector('.brand-card-arrow'))};
        }),
        controls:[...section.querySelectorAll('.brands-toolbar button,.brands-toolbar select,.brands-toolbar input')].filter(e=>e.getBoundingClientRect().width>0).map(e=>({tag:e.tagName,label:e.getAttribute('aria-label')||e.textContent.trim(),rect:rect(e)}))};
    }''')


def assert_artwork(item, photos=False):
    identity = item['id']
    assert identity in BRAND_IDS, item
    assert BRAND_NAMES[identity] in (item['label'] or ''), item
    assert re.search(r'\b20\b', item['label'] or ''), item
    if photos:
        assert len(item['photos']) == 1, item
        photo = item['photos'][0]
        assert photo['complete'] and min(photo['naturalWidth'], photo['naturalHeight']) > 0, item
        assert re.search(r'/' + identity + r'(?:[-.])', photo['src']), item
    if identity == 'cordoba':
        assert not item['logos'] and len(item['fallback']) == 1, item
        assert item['fallback'][0]['text'] == BRAND_NAMES[identity], item
        mark = item['fallback'][0]['rect']
    else:
        assert len(item['logos']) == 1 and not item['fallback'], item
        logo = item['logos'][0]
        assert logo['complete'] and min(logo['naturalWidth'], logo['naturalHeight']) > 0, item
        assert re.search(r'/' + identity + r'(?:[-.])', logo['src']), item
        assert logo['alt'] == BRAND_NAMES[identity] and logo['fit'] == 'contain', item
        mark = logo['rect']
    assert mark['left'] >= item['rect']['left'] - 1 and mark['right'] <= item['rect']['right'] + 1, item
    assert mark['top'] >= item['rect']['top'] - 1 and mark['bottom'] <= item['rect']['bottom'] + 1, item


def assert_marquee(metrics, reduced=False):
    assert 'signature-brand-marquee' in metrics['className'], metrics
    assert metrics['photos'] == 0, metrics
    assert len(metrics['groups']) == 2, metrics
    primary, clone = metrics['groups']
    assert primary['primary'] and not clone['primary'], metrics
    assert clone['ariaHidden'] == 'true', metrics
    assert len(primary['links']) == len(clone['links']) == 10, metrics
    assert set(a['id'] for a in primary['links']) == BRAND_IDS, metrics
    assert [a['id'] for a in primary['links']] == [a['id'] for a in clone['links']], metrics
    for item in primary['links']:
        assert_artwork(item)
        assert item['tabIndex'] >= 0 and not item['inert'], item
        assert min(item['rect']['width'], item['rect']['height']) >= 43.5, item
    for item in clone['links']:
        assert item['tabIndex'] == -1, item
        assert not item['inert'] and item['style']['pointerEvents'] != 'none', item
    assert len(metrics['controls']) >= 3, metrics
    for button in metrics['controls']:
        assert min(button['rect']['width'], button['rect']['height']) >= 43.5, button
    if reduced:
        assert metrics['track']['style']['animation'] == 'none', metrics
        assert clone['style']['display'] == 'none', metrics
        assert metrics['viewport']['style']['overflowX'] in ['auto', 'scroll'], metrics
    return {'primaryBrands':10,'genuineMarks':9,'typographicNames':1,'cloneTabExcluded':True,'reducedMotion':reduced}


def assert_directory(metrics, all_brands=True):
    cards = metrics['cards']
    if all_brands:
        assert len(cards) == 10 and set(c['id'] for c in cards) == BRAND_IDS, metrics
    if cards:
        assert max(c['rect']['height'] for c in cards) - min(c['rect']['height'] for c in cards) <= 1, metrics
    for card in cards:
        assert_artwork(card, photos=True)
        destination = urlparse(card['href'])
        assert destination.path == '/guitars' and parse_qs(destination.query).get('brand') == [BRAND_NAMES[card['id']]], card
        assert re.search(r'\b20\b', card['count'] or ''), card
        assert card['countRect'] and card['countRect']['left'] >= card['rect']['left'], card
        assert card['countRect']['right'] <= card['rect']['right'] + 1 and card['countRect']['top'] >= card['rect']['top'], card
        assert card['countRect']['bottom'] <= card['rect']['bottom'] + 1, card
        assert card['countTextRects'], card
        for count_text in card['countTextRects']:
            assert count_text['left'] >= card['rect']['left'] - 1 and count_text['right'] <= card['rect']['right'] + 1, card
            assert count_text['top'] >= card['rect']['top'] - 1 and count_text['bottom'] <= card['rect']['bottom'] + 1, card
        if card['arrow']:
            arrow = card['arrow']
            assert arrow['left'] >= card['rect']['left'] and arrow['right'] <= card['rect']['right'] + 1, card
            # The paragraph also owns a decorative rule and padding. Compare
            # actual visible text ranges against the full arrow bounds instead
            # of falsely treating that non-text paragraph padding as lettering.
            for count_text in card['countTextRects']:
                assert min(arrow['right'],count_text['right'])-max(arrow['left'],count_text['left']) <= 1 or min(arrow['bottom'],count_text['bottom'])-max(arrow['top'],count_text['top']) <= 1, card
    for control in metrics['controls']:
        assert min(control['rect']['width'], control['rect']['height']) >= 43.5, control
    return {'brands':len(cards),'guitarPhotos':len(cards),'genuineMarks':sum(len(c['logos']) for c in cards),'fallbacks':sum(len(c['fallback']) for c in cards),'columns':len(metrics['columns'].split()) if metrics['columns'] else 0}


def finish_report(report, filename):
    import json
    report['passed'] = bool(report['checks']) and all(c['passed'] for c in report['checks']) and not report.get('harnessFailure') and not report['consoleErrors'] and not report['runtimeErrors'] and not report['failedRequests']
    (OUT / filename).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report['passed']
