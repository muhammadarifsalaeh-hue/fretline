"""Actual marquee motion/input, Directory art/destinations/filter and responsive QA."""
from playwright.sync_api import sync_playwright,expect
from urllib.parse import parse_qs,urlparse
import json
import os
import re
import traceback
from directory_support import (BASE,OUT,VIEWPORTS,RECORDS,BRAND_COUNTS,BRAND_IDS,BRAND_NAMES,
    new_page,go,sweep,viewport_paint_ready,page_metrics,assert_page,marquee_metrics,
    directory_metrics,assert_marquee,assert_directory,report_template,finish_report)

REPORT=report_template()
REPORT['scope']='Correct placement of restored animated Home marquee; actual movement/pause/keyboard/reduced-motion behavior; existing Directory filters, licensed art mapping, real model counts and filtered Catalog destinations.'
REPORT['limits']=['Chromium/Linux viewport and touch emulation; physical iPad Safari and WebKit not tested.','Motion sampling and identical-group/keyframe checks support a seamless loop; they do not claim a visual frame-by-frame full-cycle recording.','Image subject/lighting/logo-ink fidelity still needs manual screenshot review.']
(OUT/'failures').mkdir(exist_ok=True)


def responsive(page):
    go(page);sweep(page);home=page_metrics(page);assert_page(home)
    marquee=marquee_metrics(page);layout=assert_marquee(marquee,reduced=True)
    sections={s['id']:s for s in home['sections']}
    assert sections['top']['top']<sections['brands']['top']<sections['featured']['top'],sections
    assert page.locator('#brands .signature-brand-grid').count()==0,'The photographic card grid must not replace Home marquee'
    go(page,'/brands');sweep(page);directory=page_metrics(page);assert_page(directory)
    art=directory_metrics(page);result=assert_directory(art)
    return {'home':home,'marquee':layout,'marqueeGeometry':marquee,'directory':directory,'directoryLayout':result,'directoryGeometry':art}


def animated_setup(page):
    page.emulate_media(reduced_motion='no-preference')
    go(page)
    page.locator('#brands').scroll_into_view_if_needed()
    page.mouse.move(1,1)
    viewport_paint_ready(page)
    return page.locator('.signature-marquee-track')


def track_x(track):
    return track.evaluate('e=>new DOMMatrixReadOnly(getComputedStyle(e).transform).m41')


def frozen(track):
    before=track_x(track);track.page.wait_for_timeout(180);after=track_x(track)
    assert abs(after-before)<.75,{'before':before,'after':after}
    return {'before':before,'after':after}


def motion(page):
    track=animated_setup(page)
    metrics=marquee_metrics(page)
    assert len(metrics['groups'])==2,metrics
    first,second=metrics['groups']
    assert abs(first['rect']['width']-second['rect']['width'])<=1,metrics
    assert abs(metrics['track']['rect']['width']-first['rect']['width']-second['rect']['width'])<=2,metrics
    assert [i['id'] for i in first['links']]==[i['id'] for i in second['links']],metrics
    assert metrics['track']['style']['animationTiming']=='linear',metrics
    animations=metrics['track']['animations'];assert animations,metrics
    animation=animations[0]
    assert any('-50%' in f.get('transform','') for f in animation['keyframes']),animation
    assert animation['timing']['duration']>=10000,animation
    samples=track.evaluate('''async e=>{
      const values=[];for(let i=0;i<12;i++){
        await new Promise(r=>requestAnimationFrame(r));
        values.push({time:performance.now(),x:new DOMMatrixReadOnly(getComputedStyle(e).transform).m41});
      }return values;
    }''')
    assert samples[-1]['x']<samples[0]['x']-1,samples
    speeds=[-(b['x']-a['x'])/(b['time']-a['time']) for a,b in zip(samples,samples[1:]) if b['time']>a['time']]
    assert all(speed>=-.001 for speed in speeds),{'samples':samples,'speeds':speeds}
    page.locator('[data-marquee-viewport]').hover()
    hover=frozen(track)
    page.mouse.move(1,1)
    pause=page.locator('[data-marquee-pause]');pause.click();expect(pause).to_have_attribute('aria-pressed','true')
    page.mouse.move(1,1);paused=frozen(track)
    pause.click();expect(pause).to_have_attribute('aria-pressed','false')
    page.locator('.site-header a[href="/"]').first.focus();page.mouse.move(1,1)
    before=track_x(track);page.wait_for_timeout(180);after=track_x(track)
    assert after<before-1,{'resumeBefore':before,'resumeAfter':after}
    return {'movement':samples,'speedsPixelsPerMs':speeds,'equalLoopGroups':True,'linearHalfTrackKeyframe':True,'hoverPaused':hover,'buttonPaused':paused,'resumed':{'before':before,'after':after},'cloneLinks':second['links']}


def keyboard_and_arrows(page):
    track=animated_setup(page)
    links=page.locator('[data-marquee-primary] a[data-brand-id]')
    assert links.count()==10
    links.first.focus();expect(page.locator('#brands')).to_have_attribute('data-manual','true')
    focused=[]
    for index in range(10):
        item=links.nth(index);expect(item).to_be_focused()
        page.wait_for_function('''()=>{const a=document.activeElement,v=document.querySelector('[data-marquee-viewport]');if(!a||!v)return false;const x=a.getBoundingClientRect(),b=v.getBoundingClientRect();return x.left>=b.left-1&&x.right<=b.right+1}''')
        focused.append(item.get_attribute('data-brand-id'))
        frozen(track)
        if index<9:page.keyboard.press('Tab')
    metrics=marquee_metrics(page)
    assert metrics['groups'][1]['style']['display']=='none',metrics
    viewport=page.locator('[data-marquee-viewport]')
    before=viewport.evaluate('e=>e.scrollLeft')
    page.locator('[data-marquee-prev]').click()
    page.wait_for_function('(before)=>document.querySelector("[data-marquee-viewport]").scrollLeft<before-1',arg=before)
    previous=viewport.evaluate('e=>e.scrollLeft')
    page.locator('[data-marquee-next]').click()
    page.wait_for_function('(before)=>document.querySelector("[data-marquee-viewport]").scrollLeft>before+1',arg=previous)
    return {'allPrimaryBrandsKeyboardReachable':focused,'focusPausesAndReveals':True,'cloneHiddenInManualMode':True,'previousScroll':{'before':before,'after':previous},'nextScroll':viewport.evaluate('e=>e.scrollLeft')}


def clone_pointer(page):
    track=animated_setup(page)
    metadata=marquee_metrics(page);clone=metadata['groups'][1]
    assert clone['ariaHidden']=='true' and all(a['tabIndex']==-1 and not a['inert'] and a['style']['pointerEvents']!='none' for a in clone['links']),clone
    duration=metadata['track']['animations'][0]['timing']['duration']
    # Wait for a real continuously moving clone to enter the actual viewport.
    # Do not seek animation time or replace transforms just to make it clickable.
    page.wait_for_function('''()=>{const v=document.querySelector('[data-marquee-viewport]').getBoundingClientRect();return [...document.querySelectorAll('.signature-marquee-group:not([data-marquee-primary]) a[data-brand-id]')].some(a=>{const r=a.getBoundingClientRect(),x=(r.left+r.right)/2;return x>v.left+8&&x<v.right-8})}''',timeout=min(120000,duration+5000))
    target=page.evaluate('''()=>{const v=document.querySelector('[data-marquee-viewport]').getBoundingClientRect();const a=[...document.querySelectorAll('.signature-marquee-group:not([data-marquee-primary]) a[data-brand-id]')].find(a=>{const r=a.getBoundingClientRect(),x=(r.left+r.right)/2;return x>v.left+8&&x<v.right-8});const r=a.getBoundingClientRect();return {href:a.getAttribute('href'),id:a.dataset.brandId,x:(r.left+r.right)/2,y:(r.top+r.bottom)/2}}''')
    page.mouse.move(target['x'],target['y']);page.mouse.click(target['x'],target['y'])
    expect(page).to_have_url(BASE+target['href'])
    return {'naturallyVisibleCloneClicked':target,'actualDestination':page.url,'clonesExcludedFromKeyboard':True}


def directory_destinations(page):
    go(page,'/brands');sweep(page);metrics=directory_metrics(page);assert_directory(metrics)
    samples=[]
    for card in metrics['cards']:
        go(page,'/brands')
        page.locator('.brand-directory-card[data-brand-id="'+card['id']+'"]').click()
        expect(page).to_have_url(BASE+card['href'])
        expect(page.locator('.catalog-result-count p').first).to_contain_text('20')
        ids=page.locator('.catalog-grid [data-guitar-id]').evaluate_all('nodes=>nodes.map(e=>e.dataset.guitarId)')
        assert ids and all(next(r for r in RECORDS if r['id']==identity)['brand']==BRAND_NAMES[card['id']] for identity in ids),(card,ids)
        samples.append({'brand':card['id'],'url':page.url,'actualCountText':page.locator('.catalog-result-count').inner_text(),'visibleGuitarIds':ids})
        page.go_back(wait_until='networkidle');expect(page.locator('.brands-page')).to_be_visible()
    return {'allTenFilteredCatalogs':samples,'catalogSourceCounts':dict(BRAND_COUNTS)}


def directory_filters(page):
    go(page,'/brands')
    search=page.locator('#brands-search');cards=page.locator('.brand-directory-card[data-brand-id]')
    search.fill('YAMAHA');expect(cards).to_have_count(1);expect(cards).to_have_attribute('data-brand-id','yamaha')
    assert parse_qs(urlparse(page.url).query).get('q')==['YAMAHA'],page.url
    page.locator('.brands-search button').click();expect(cards).to_have_count(10);expect(search).to_be_focused()
    type_button=page.locator('.brands-filter-row button').nth(1);type_button.click()
    expect(type_button).to_have_attribute('aria-pressed','true')
    expected={r['brand'] for r in RECORDS if r['category']=='electric'}
    ids=cards.evaluate_all('nodes=>nodes.map(e=>e.dataset.brandId)')
    assert {BRAND_NAMES[i] for i in ids}==expected,ids
    type_url=page.url
    sort=page.locator('.phase5-sort select');sort.select_option('price')
    expect(sort).to_have_value('price');assert parse_qs(urlparse(page.url).query).get('sort')==['price'],page.url
    expect(cards.first).to_have_attribute('data-brand-id','yamaha')
    price_url=page.url
    page.go_back(wait_until='networkidle');expect(page).to_have_url(type_url);expect(sort).to_have_value('models')
    page.go_forward(wait_until='networkidle');expect(page).to_have_url(price_url);expect(sort).to_have_value('price')
    details=page.locator('.brands-extra-filters')
    if details.get_attribute('open') is None:details.locator('summary').click()
    details.get_by_role('button',name='Japan',exact=True).click()
    ids=cards.evaluate_all('nodes=>nodes.map(e=>e.dataset.brandId)')
    assert set(ids)=={'yamaha','ibanez'},ids
    search.fill('Yamaha');expect(cards).to_have_count(1);expect(cards).to_have_attribute('data-brand-id','yamaha')
    combined=parse_qs(urlparse(page.url).query)
    assert combined.get('type')==['electric'] and combined.get('country')==['Japan'] and combined.get('q')==['Yamaha'],combined
    page.locator('.brands-result-bar button').click();expect(cards).to_have_count(10);expect(search).to_be_focused()
    params=parse_qs(urlparse(page.url).query);assert params=={'sort':['price']},params
    sort.select_option('name')
    sorted_ids=cards.evaluate_all('nodes=>nodes.map(e=>e.dataset.brandId)')
    assert [BRAND_NAMES[i] for i in sorted_ids]==sorted(BRAND_NAMES.values(),key=str.casefold),sorted_ids
    search.fill('fretline-no-such-brand-99881');expect(cards).to_have_count(0)
    expect(page.get_by_role('heading',name='ไม่พบแบรนด์ที่ตรงกัน',exact=True)).to_be_visible()
    page.locator('.brands-result-bar button').click();expect(cards).to_have_count(10)
    return {'searchCaseInsensitive':True,'electricMatchesSourceBrands':sorted(expected),'countryRetainedAsExistingUnverifiedFilter':ids,'combinedParams':combined,'clearPreservesSort':params,'nameOrder':sorted_ids,'emptyAndClear':True,'browserBackForward':True}


STYLE='''e=>{const s=getComputedStyle(e),b=getComputedStyle(e,'::before'),a=getComputedStyle(e,'::after'),r=e.getBoundingClientRect();return {border:s.borderColor,shadow:s.boxShadow,beforeOpacity:b.opacity,afterOpacity:a.opacity,outline:s.outlineStyle,outlineWidth:s.outlineWidth,focusVisible:e.matches(':focus-visible'),width:r.width,height:r.height,photos:[...e.querySelectorAll('[data-brand-photo]')].map(i=>({src:i.currentSrc,transform:getComputedStyle(i).transform}))}}'''


def directory_feedback(page):
    page.emulate_media(reduced_motion='no-preference');go(page,'/brands');sweep(page)
    card=page.locator('.brand-directory-card[data-brand-id="yamaha"]');card.scroll_into_view_if_needed()
    page.mouse.move(1,1);page.wait_for_timeout(450);before=card.evaluate(STYLE)
    card.hover();page.wait_for_timeout(450);hover=card.evaluate(STYLE)
    assert before['photos']==hover['photos'] and before['width']==hover['width'] and before['height']==hover['height'],{'before':before,'hover':hover}
    assert any(before[k]!=hover[k] for k in ['border','shadow','beforeOpacity','afterOpacity']),{'before':before,'hover':hover}
    page.mouse.move(1,1);page.keyboard.press('Tab');card.focus();focus=card.evaluate(STYLE)
    assert focus['focusVisible'] and (focus['shadow']!='none' or focus['outline']!='none' and float(focus['outlineWidth'].removesuffix('px'))>=1),focus
    return {'before':before,'hover':hover,'keyboardFocus':focus}


CASES=[('responsive-'+label,responsive,width,height) for width,height,label in VIEWPORTS]
CASES += [('marquee-motion-desktop',motion,1440,1000),('marquee-motion-mobile',motion,390,844),
          ('marquee-keyboard-desktop',keyboard_and_arrows,1440,1000),('marquee-keyboard-mobile',keyboard_and_arrows,390,844),
          ('marquee-live-clone-click',clone_pointer,1440,1000),('directory-destinations',directory_destinations,1440,1000),
          ('directory-filters-history',directory_filters,1440,1000),('directory-hover-focus',directory_feedback,1440,1000)]
selected=set(filter(None,os.environ.get('FRETLINE_QA_CASES','').split(',')))
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('FRETLINE_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        for name,test,width,height in CASES:
            if selected and not any(name==case or name.startswith(case+'-') for case in selected):continue
            context,page=new_page(browser,REPORT,name,width,height)
            try:
                details=test(page);REPORT['checks'].append({'case':name,'passed':True,'details':details});print('PASS '+name,flush=True)
            except Exception:
                failure=traceback.format_exc();target=OUT/'failures'/(name+'.png')
                try:page.screenshot(path=str(target),full_page=True)
                except Exception as error:failure+='\nScreenshot failed: '+str(error)
                REPORT['checks'].append({'case':name,'passed':False,'failure':failure,'url':page.url,'screenshot':str(target.relative_to(OUT))});print('FAIL '+name+'\n'+failure,flush=True)
            finally:context.close()
        browser.close()
except Exception:REPORT['harnessFailure']=traceback.format_exc()
raise SystemExit(0 if finish_report(REPORT,'acceptance.json') else 1)
