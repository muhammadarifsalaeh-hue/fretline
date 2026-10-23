"""Combined 404 artwork failure at 320px; no app/CSS/Home substitutions.

Run with FRETLINE_QA_ENGINE=chromium|webkit and an existing FRETLINE_QA_URL.
WebKit uses the same external runtime environment as the other engine scripts.
"""
from playwright.sync_api import sync_playwright, expect
from urllib.parse import urlparse
import re
import traceback

from browser_support import (BASE,OUT,ENGINE,BRAND_NAMES,BY_ID,report_template,
    launch,new_page,go,sweep,wait_artwork,settle,metrics,assert_layout,
    pixel_evidence,image_target,finish)

CASE='all-images-404-small-mobile'
REPORT=report_template()
REPORT['scope']='Combined failure of all ten brand photos and nine image marks at320px; no physical Safari claim.'
REPORT['intentionalFault']='Every matching brand photo/logo request receives deliberate404; expected HTTP/decode errors are retained separately. No CSS, content, image source or fallback state is substituted.'


def visible_text_ranges(page):
    """Read actual rendered text ranges, including each line of long names."""
    return page.locator('.brand-directory-card[data-brand-id]').evaluate_all(r'''cards=>{
      const rect=b=>({left:b.left,top:b.top,right:b.right,bottom:b.bottom,width:b.width,height:b.height});
      const rendered=e=>{for(let a=e;a&&a.nodeType===1;a=a.parentElement){const s=getComputedStyle(a);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false;}return true;};
      return cards.map(card=>{
        const walker=document.createTreeWalker(card,NodeFilter.SHOW_TEXT),texts=[];let node;
        while(node=walker.nextNode()){
          if(!node.textContent.trim()||!rendered(node.parentElement))continue;
          const range=document.createRange();range.selectNodeContents(node);
          const boxes=[...range.getClientRects()].filter(b=>b.width>0&&b.height>0).map(rect);
          if(boxes.length)texts.push({text:node.textContent.trim(),brandName:Boolean(node.parentElement.closest('[data-brand-fallback]')),rects:boxes});
        }
        return {id:card.dataset.brandId,card:rect(card.getBoundingClientRect()),texts};
      });
    }''')


def identity(url):
    filename=urlparse(url).path.rsplit('/',1)[-1]
    return next((key for key in BRAND_NAMES if re.match(re.escape(key)+r'[-.]',filename)),None)


def run(page):
    intercepted=[]
    def fail_artwork(route):
        url=route.request.url
        if not image_target(url,'all'):return route.continue_()
        row={'case':CASE,'url':url,'status':404,'kind':'photo' if image_target(url,'photo') else 'logo'}
        intercepted.append(row);REPORT['injectedImageFaults'].append(row)
        route.fulfill(status=404,content_type='text/plain',body='All brand artwork deliberately unavailable for combined QA failure')
    page.route('**/*',fail_artwork)
    go(page);sweep(page)
    page.wait_for_function('''()=>[...document.querySelectorAll('.brand-directory-card[data-brand-id]')].every(a=>{
      const status=name=>a.getAttribute(name)||a.querySelector('['+name+']')?.getAttribute(name);
      return status('data-photo-status')==='error'&&(a.dataset.brandId==='cordoba'||status('data-logo-status')==='error');
    })''')
    wait_artwork(page)
    data=metrics(page);layout=assert_layout(data,normal=False)
    photo_ids={identity(row['url']) for row in intercepted if row['kind']=='photo'}
    logo_ids={identity(row['url']) for row in intercepted if row['kind']=='logo'}
    assert photo_ids==set(BRAND_NAMES),photo_ids
    assert logo_ids==set(BRAND_NAMES)-{'cordoba'},logo_ids
    for card in data['cards']:
        assert card['photoStatus']=='error',card
        assert any(not f['hidden'] and f['rect']['height']>40 for f in card['photoFallbacks']),card
        assert any(f['text']==BRAND_NAMES[card['id']] and not f['hidden'] and f['rect']['height']>10 for f in card['fallbacks']),card
        if card['id']!='cordoba':assert card['logoStatus']=='error',card

    ranges=visible_text_ranges(page)
    for row in ranges:
        box=row['card'];assert row['texts'],row
        name_nodes=[t for t in row['texts'] if t['brandName']]
        assert ''.join(t['text'] for t in name_nodes)==BRAND_NAMES[row['id']],row
        for text in row['texts']:
            for line in text['rects']:
                assert line['left']>=box['left']-1 and line['right']<=box['right']+1,{'brand':row['id'],'text':text,'card':box}
                assert line['top']>=box['top']-1 and line['bottom']<=box['bottom']+1,{'brand':row['id'],'text':text,'card':box}

    target=OUT/'faults'/ENGINE/(CASE+'.png');target.parent.mkdir(parents=True,exist_ok=True)
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})');settle(page)
    page.screenshot(path=str(target),full_page=True,animations='allow')
    paint=pixel_evidence(page,CASE)
    # The long-name fallback remains an actual working native card link.
    sample=next(c for c in data['cards'] if c['id']=='epiphone')
    page.locator('.brand-directory-card[data-brand-id="epiphone"]').click()
    expect(page).to_have_url(BASE+sample['href'])
    expect(page.locator('.catalog-result-count')).to_contain_text('20')
    guitars=page.locator('.catalog-grid [data-guitar-id]').evaluate_all('nodes=>nodes.map(n=>n.dataset.guitarId)')
    assert guitars and all(BY_ID[i]['brand']=='Epiphone' for i in guitars),guitars
    return {'layout':layout,'metrics':data,'visibleTextRanges':ranges,
        'failedPhotoBrands':sorted(photo_ids),'failedLogoBrands':sorted(logo_ids),
        'paintedIdentity':paint,'screenshot':str(target.relative_to(OUT)),
        'catalogAfterFallbackClick':{'url':page.url,'countText':page.locator('.catalog-result-count').inner_text(),'visibleGuitarIds':guitars}}


try:
    with sync_playwright() as p:
        browser=launch(p,REPORT)
        context,page=new_page(browser,REPORT,CASE,320,740,fault_kind='all')
        try:
            details=run(page);REPORT['checks'].append({'case':CASE,'passed':True,'details':details});print('PASS '+ENGINE+'-'+CASE,flush=True)
        except Exception:
            failure=traceback.format_exc();path=OUT/'failures'/ENGINE/(CASE+'.png');path.parent.mkdir(parents=True,exist_ok=True)
            try:page.screenshot(path=str(path),full_page=True,animations='allow')
            except Exception as error:failure+='\nScreenshot failure: '+str(error)
            REPORT['checks'].append({'case':CASE,'passed':False,'failure':failure,'screenshot':str(path.relative_to(OUT))});print('FAIL '+ENGINE+'-'+CASE+'\n'+failure,flush=True)
        finally:context.close();browser.close()
except Exception:REPORT['harnessFailure']=traceback.format_exc()
raise SystemExit(0 if finish(REPORT,'all-image-failure-'+ENGINE+'.json') else 1)
