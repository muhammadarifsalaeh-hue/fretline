"""Focused final visual, keyboard, touch and reduced-motion checks.

Run against an existing production preview. No app styles/content are replaced.
Functional data/search/Quiz/Compare/Wishlist suites are run separately unchanged.
"""
from playwright.sync_api import sync_playwright,expect
import json
import os
import traceback
from polish_support import (BASE,OUT,VIEWPORTS,CAPTURE_VIEWPORTS,new_page,go,
                            sweep_home,page_metrics,brand_metrics,assert_page,
                            assert_brand_layout,homepage_geometry,report_template)

REPORT=report_template()
REPORT['scope']='Final Homepage composition, brand-mark alignment and source loading, header/mobile navigation from Home, stable hover crop, visible focus, reduced motion and footer clearance.'
REPORT['limits']=['Chromium/Linux touch emulation, not physical iPad/Safari.','Manual screenshot/reference review is required for guitar subject crop, logo ink legibility and cinematic lighting.']
(OUT/'failures').mkdir(exist_ok=True)


def composition(page):
    go(page);sweep_home(page)
    metrics=page_metrics(page);assert_page(metrics)
    brands=brand_metrics(page);layout=assert_brand_layout(brands,page.viewport_size['width'],'after')
    geometry=homepage_geometry(page)
    h=geometry['hero']
    for key in ['title','description','actions','search']:
        r=geometry[key]
        assert r and r['width']>0 and r['left']>=h['left']-1 and r['right']<=h['right']+1,(key,r,h)
        assert r['top']>=h['top']-1 and r['bottom']<=h['bottom']+1,(key,r,h)
    for previous,next_item in [('title','description'),('description','actions'),('actions','search')]:
        assert geometry[previous]['bottom']<=geometry[next_item]['top']+1,(previous,next_item,geometry)
    assert geometry['title']['top']>=geometry['header']['bottom']+8,geometry
    for item in geometry['svgCenters']:
        assert min(item['rect']['width'],item['rect']['height'])>=43.5,item
        if item['centerDelta'] is not None:assert abs(item['centerDelta'])<=1.5,item
    for icon in geometry['headerIconPaint']:
        assert icon['svg'] and min(icon['svg']['width'],icon['svg']['height'])>0,icon
        assert icon['svgStyle']['display']!='none' and icon['svgStyle']['visibility']!='hidden' and float(icon['svgStyle']['opacity'])>0,icon
        assert any(shape['painted'] and shape['length']>0 for shape in icon['shapes']),icon
    # All brand frames should share a deliberate optical center. Individual true
    # artwork may include internal whitespace; native frame placement is measured.
    relative=[]
    for frame,card in zip(geometry['brandMarkFrames'],brands['cards']):
        assert frame['id']==card['id']
        r=frame['rect'];c=card['rect'];center=((r['top']+r['bottom'])/2-c['top'])/c['height']
        assert .30<=center<=.65,(frame,card,center)
        relative.append(center)
    # Optical artwork centers may differ deliberately (for example circular
    # Taylor vs long wordmarks); record the spread for manual review, not an
    # artificial exact-equality rule for genuinely different logo shapes.
    count_offsets=[c['rect']['bottom']-c['count']['bottom'] for c in brands['cards']]
    assert max(count_offsets)-min(count_offsets)<=1,{'countBottomOffsets':count_offsets}
    for fallback in geometry['fallback']:
        assert float(fallback['style']['fontSize'].replace('px',''))>=20,fallback
    page.evaluate('window.scrollTo({top:document.documentElement.scrollHeight,behavior:"instant"})')
    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    footer=page.locator('.site-footer').bounding_box()
    bottom=page.locator('.site-bottom-nav').bounding_box()
    if bottom and bottom['width']>0:
        assert footer['y']+footer['height']<=bottom['y']+1,{'footer':footer,'bottomNav':bottom}
    assert_page(page_metrics(page))
    return {'page':metrics,'brands':layout,'composition':geometry,
            'relativeMarkCenters':relative,'countBottomOffsets':count_offsets,
            'footer':footer,'bottomNav':bottom}


def navigation(page):
    go(page)
    width=page.viewport_size['width']
    if width>=1024:
        trigger=page.locator('button[aria-controls="guitar-navigation"]')
        trigger.focus();trigger.press('Enter')
        expect(trigger).to_have_attribute('aria-expanded','true')
        expect(page.locator('#guitar-navigation')).to_be_visible()
        page.keyboard.press('Escape')
        expect(trigger).to_have_attribute('aria-expanded','false');expect(trigger).to_be_focused()
        if width==1024:
            # Landscape iPad width uses the desktop disclosure with a true touch
            # context: no synthetic mouse hover is required to open the menu.
            trigger.tap();expect(trigger).to_have_attribute('aria-expanded','true')
            expect(page.locator('#guitar-navigation')).to_be_visible()
            page.keyboard.press('Escape')
            expect(trigger).to_have_attribute('aria-expanded','false')
            expect(trigger).to_be_focused()
        page.locator('.site-header').get_by_role('button',name='ค้นหา',exact=True).click()
        expect(page.locator('#hero-search')).to_be_focused()
        return {'homeDesktopDisclosure':True,'escapeRestoresFocus':True,'homeHeaderSearchFocus':True,'touch1024':width==1024}
    trigger=page.locator('button[aria-controls="mobile-navigation"]')
    trigger.focus();trigger.press('Enter')
    expect(trigger).to_have_attribute('aria-expanded','true')
    dialog=page.locator('#mobile-navigation');expect(dialog).to_be_visible()
    page.keyboard.press('Tab')
    assert dialog.evaluate('(e)=>e.contains(document.activeElement)'),'Focus escaped Mobile navigation'
    page.keyboard.press('Escape')
    expect(trigger).to_have_attribute('aria-expanded','false');expect(trigger).to_be_focused()
    trigger.tap();expect(dialog).to_be_visible()
    link=dialog.locator('nav a[href="/brands"]');link.tap()
    expect(page).to_have_url(BASE+'/brands');expect(dialog).to_be_hidden()
    expect(page.locator('main')).to_be_focused()
    page.go_back(wait_until='networkidle');expect(page.locator('.signature-home')).to_be_visible()
    page.locator('.site-bottom-nav').get_by_role('button',name='ค้นหา',exact=True).tap()
    expect(page.locator('#hero-search')).to_be_focused()
    return {'homeMobileDialog':True,'keyboardTrapEscapeRestore':True,
            'touchRouteClosesDialog':True,'browserBack':True,'bottomSearchFocus':True}


STYLE='''e=>{const s=getComputedStyle(e),p=getComputedStyle(e,'::after'),r=e.getBoundingClientRect();return {
 border:s.borderColor,shadow:s.boxShadow,glow:p.opacity,outline:s.outlineStyle,
 outlineWidth:s.outlineWidth,focusVisible:e.matches(':focus-visible'),
 box:{left:r.left,top:r.top,width:r.width,height:r.height},
 images:[...e.querySelectorAll('img')].map(i=>({src:i.currentSrc,transform:getComputedStyle(i).transform,fit:getComputedStyle(i).objectFit}))}}'''


def hover_and_focus(page):
    page.emulate_media(reduced_motion='no-preference')
    go(page);sweep_home(page)
    samples=[]
    for brand in ['yamaha','gibson','taylor']:
        card=page.locator('[data-brand-id="'+brand+'"]')
        card.scroll_into_view_if_needed();page.mouse.move(1,1);page.wait_for_timeout(450)
        before=card.evaluate(STYLE)
        card.hover();page.wait_for_timeout(450);after=card.evaluate(STYLE)
        assert before['images']==after['images'],{'brand':brand,'before':before,'after':after}
        assert abs(before['box']['width']-after['box']['width'])<=1 and abs(before['box']['height']-after['box']['height'])<=1,{'brand':brand,'before':before,'after':after}
        assert (before['border']!=after['border'] or before['shadow']!=after['shadow'] or float(after['glow'])>float(before['glow'])+.05),{'brand':brand,'before':before,'after':after}
        samples.append({'brand':brand,'before':before,'hover':after})
    page.mouse.move(1,1)
    card=page.locator('[data-brand-id="yamaha"]');card.focus();expect(card).to_be_focused()
    focus=card.evaluate(STYLE)
    assert focus['focusVisible'],focus
    assert (focus['outline']!='none' and float(focus['outlineWidth'].replace('px',''))>=1) or focus['shadow']!='none',focus
    return {'samples':samples,'keyboardFocus':focus}


def reduced_motion(page):
    go(page)
    page.locator('[data-brand-id="yamaha"]').scroll_into_view_if_needed()
    result=page.evaluate('''()=>({reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,
      elements:[document.querySelector('.site-header'),document.querySelector('[data-brand-id="yamaha"]'),document.querySelector('.signature-hero-visual img')].map(e=>{const s=getComputedStyle(e);return {className:e.className,transition:s.transitionDuration,animation:s.animationDuration}}),
      reveals:[...document.querySelectorAll('.reveal')].map(e=>{const s=getComputedStyle(e);return {opacity:s.opacity,transform:s.transform,transformIdentity:s.transform==='none'||new DOMMatrixReadOnly(s.transform).isIdentity}})})''')
    assert result['reduced'],result
    for e in result['elements']:
        for key in ['transition','animation']:
            values=[float(v.strip().removesuffix('s')) for v in e[key].split(',')]
            assert max(values)<=.001,e
    assert all(e['opacity']=='1' and e['transformIdentity'] for e in result['reveals']),result
    return result


CASES=[('composition-'+label,composition,width,height) for width,height,label in CAPTURE_VIEWPORTS]
CASES += [('navigation-'+label,navigation,width,height) for width,height,label in VIEWPORTS]
CASES += [('hover-and-focus',hover_and_focus,1440,1000),('reduced-motion',reduced_motion,1440,1000)]
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
finally:
    REPORT['passed']=bool(REPORT['checks']) and all(c['passed'] for c in REPORT['checks']) and not REPORT.get('harnessFailure') and not REPORT['consoleErrors'] and not REPORT['runtimeErrors'] and not REPORT['failedRequests']
    (OUT/'visual-acceptance.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if REPORT['passed'] else 1)
