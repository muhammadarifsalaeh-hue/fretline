"""Actual Directory engine coverage; intentional image faults are reported separately."""
from playwright.sync_api import sync_playwright,expect
from urllib.parse import parse_qs,urlparse
import os
import traceback
from browser_support import BASE,OUT,ENGINE,VIEWPORTS,BRAND_NAMES,BY_ID,report_template,launch,new_page,go,sweep,settle,wait_artwork,metrics,assert_layout,pixel_evidence,image_target,finish

REPORT=report_template()
REPORT['scope']='Only Brand Directory display, native layout, source mapping, image failures, destinations and existing filters; no Home edits or Home test substitutions.'
REPORT['syntheticFaultPolicy']='Image404/corrupt200 and disabledaspectratio cases are deliberate fault injection, not natural Safari observations. Expected image network/decode errors are retained separately; runtime errors always fail.'

def rendering(page,name):
    go(page);sweep(page);wait_artwork(page);data=metrics(page)
    return {'layout':assert_layout(data),'metrics':data,'paintedIdentity':pixel_evidence(page,name)}

def aspect_fault(page,name):
    go(page)
    page.add_style_tag(content='.brands-page .brand-directory-card{aspect-ratio:auto !important}')
    sweep(page);wait_artwork(page);data=metrics(page)
    return {'syntheticLayoutFault':True,'notActualSafariReproduction':True,'layout':assert_layout(data),'metrics':data,'paintedIdentity':pixel_evidence(page,name)}

def image_fault(page,name,kind,mode):
    injected=[]
    def route_image(route):
        url=route.request.url
        if not image_target(url,kind):return route.continue_()
        row={'case':name,'url':url,'kind':kind,'mode':mode};injected.append(row);REPORT['injectedImageFaults'].append(row)
        if mode=='404':route.fulfill(status=404,content_type='text/plain',body='Deliberately missing QA image')
        else:route.fulfill(status=200,content_type='image/webp' if kind=='photo' else 'image/svg+xml',body=b'Not a decodable image: deliberate QA corruption')
    page.route('**/*',route_image)
    go(page);sweep(page)
    page.wait_for_function('''kind=>[...document.querySelectorAll('.brand-directory-card')].every(a=>{if(kind==='logo'&&a.dataset.brandId==='cordoba')return true;const name='data-'+kind+'-status';return (a.getAttribute(name)||a.querySelector('['+name+']')?.getAttribute(name))==='error'})''',arg=kind)
    data=metrics(page);assert_layout(data,normal=False)
    assert injected,kind
    for c in data['cards']:
        if kind=='logo':
            assert any(f['text']==BRAND_NAMES[c['id']] and not f['hidden'] and f['rect']['height']>10 for f in c['fallbacks']),c
            if c['id']!='cordoba':assert c['logoStatus']=='error',c
        else:
            assert c['photoStatus']=='error',c
            assert any(not f['hidden'] and f['rect']['height']>40 for f in c['photoFallbacks']),c
    target=OUT/'faults'/ENGINE/(name+'.png');target.parent.mkdir(parents=True,exist_ok=True)
    page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(target),full_page=True,animations='allow')
    paint=pixel_evidence(page,name)
    # The real card remains navigable even while its artwork is unavailable.
    first=data['cards'][0];page.locator('.brand-directory-card[data-brand-id="'+first['id']+'"]').click()
    expect(page).to_have_url(BASE+first['href'])
    expect(page.locator('.catalog-result-count')).to_contain_text('20')
    return {'deliberateImageFault':{'kind':kind,'mode':mode},'interceptions':injected,'metrics':data,'paintedIdentity':paint,'screenshot':str(target.relative_to(OUT)),'filteredCatalogAfterFault':page.url}

def destinations(page,name):
    go(page);sweep(page);wait_artwork(page);data=metrics(page);assert_layout(data)
    results=[]
    for c in data['cards']:
        go(page);page.locator('.brand-directory-card[data-brand-id="'+c['id']+'"]').click()
        expect(page).to_have_url(BASE+c['href']);expect(page.locator('.catalog-result-count')).to_contain_text('20')
        ids=page.locator('.catalog-grid [data-guitar-id]').evaluate_all('nodes=>nodes.map(n=>n.dataset.guitarId)')
        assert ids and all(BY_ID[i]['brand']==BRAND_NAMES[c['id']] for i in ids),(c,ids)
        results.append({'brand':c['id'],'url':page.url,'resultText':page.locator('.catalog-result-count').inner_text(),'visibleGuitarIds':ids})
    return results

def filters(page,name):
    go(page);search=page.locator('#brands-search');cards=page.locator('.brand-directory-card[data-brand-id]')
    search.fill('YAMAHA');expect(cards).to_have_count(1);expect(cards).to_have_attribute('data-brand-id','yamaha')
    page.locator('.brands-search button').click();expect(cards).to_have_count(10)
    page.locator('.brands-filter-row button').nth(1).click();type_url=page.url
    select=page.locator('.phase5-sort select');select.select_option('price');price_url=page.url
    expect(cards.first).to_have_attribute('data-brand-id','yamaha')
    page.go_back(wait_until='networkidle');expect(page).to_have_url(type_url);expect(select).to_have_value('models')
    page.go_forward(wait_until='networkidle');expect(page).to_have_url(price_url);expect(select).to_have_value('price')
    details=page.locator('.brands-extra-filters')
    if details.get_attribute('open') is None:details.locator('summary').click()
    details.get_by_role('button',name='Japan',exact=True).click()
    assert set(cards.evaluate_all('nodes=>nodes.map(n=>n.dataset.brandId)'))=={'yamaha','ibanez'}
    search.fill('Yamaha');expect(cards).to_have_count(1)
    combined=parse_qs(urlparse(page.url).query)
    assert combined.get('type')==['electric'] and combined.get('country')==['Japan'] and combined.get('q')==['Yamaha'],combined
    search.fill('NO-SUCH-BRAND-DISPLAY-FIX');expect(cards).to_have_count(0)
    page.locator('.brands-result-bar button').click();expect(cards).to_have_count(10)
    select.select_option('name');expect(select).to_have_value('name');assert parse_qs(urlparse(page.url).query).get('sort')==['name']
    return {'search':True,'typesAndCountry':True,'allSorts':True,'history':True,'combinedQuery':combined,'emptyAndClear':True}

CASES=[('rendering-'+label,rendering,width,height,None) for width,height,label in VIEWPORTS]
CASES += [('diagnostic-aspect-disabled',aspect_fault,768,1024,None),('all-directory-destinations',destinations,1440,1000,None),('directory-filters-history',filters,1440,1000,None)]
for kind in ['photo','logo']:
    for mode in ['404','corrupt200']:
        CASES.append((kind+'-'+mode,lambda p,n,k=kind,m=mode:image_fault(p,n,k,m),768,1024,kind))
selected=set(filter(None,os.environ.get('FRETLINE_QA_CASES','').split(',')))
try:
    with sync_playwright() as p:
        browser=launch(p,REPORT)
        for name,test,width,height,fault_kind in CASES:
            if selected and not any(name==prefix or name.startswith(prefix+'-') for prefix in selected):continue
            context,page=new_page(browser,REPORT,name,width,height,fault_kind)
            try:
                details=test(page,name);REPORT['checks'].append({'case':name,'passed':True,'details':details});print('PASS '+ENGINE+'-'+name,flush=True)
            except Exception:
                failure=traceback.format_exc();path=OUT/'failures'/ENGINE/(name+'.png');path.parent.mkdir(parents=True,exist_ok=True)
                try:page.screenshot(path=str(path),full_page=True,animations='allow')
                except Exception as error:failure+='\nScreenshot failure: '+str(error)
                REPORT['checks'].append({'case':name,'passed':False,'failure':failure,'screenshot':str(path.relative_to(OUT))});print('FAIL '+name+'\n'+failure,flush=True)
            finally:context.close()
        browser.close()
except Exception:REPORT['harnessFailure']=traceback.format_exc()
raise SystemExit(0 if finish(REPORT,'acceptance-'+ENGINE+'.json') else 1)
