"""Actual engine Before/After captures; synthetic aspect-ratio diagnostic is explicit."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os
import traceback
from browser_support import OUT,ENGINE,VIEWPORTS,report_template,launch,new_page,go,sweep,settle,wait_artwork,metrics,assert_layout,pixel_evidence,finish

STAGE=os.environ.get('FRETLINE_QA_STAGE','after')
assert STAGE in {'before','after'}
DIAGNOSTIC=os.environ.get('FRETLINE_QA_DISABLE_ASPECT')=='1'
KIND='diagnostic-aspect-disabled' if DIAGNOSTIC else 'actual'
REPORT=report_template()
REPORT.update({'stage':STAGE,'kind':KIND,'syntheticLayoutFault':DIAGNOSTIC,'notPhysicalSafari':True,
    'successMeaning':'After requires healthy rendered cards. Before means successful evidence collection, not a healthy baseline UI.',
    'method':'Actual application screenshots, native scroll and local fonts. No content or image replacement. '+('The only injected CSS disables aspect-ratio explicitly to test lost-ratio resilience; this is NOT a recording of Safari behavior.' if DIAGNOSTIC else 'No screenshot-only CSS or animation substitutions.')})
SHOTS=OUT/STAGE/ENGINE/KIND;SHOTS.mkdir(parents=True,exist_ok=True)
selected=set(filter(None,os.environ.get('FRETLINE_QA_VIEWPORTS','').split(',')))
try:
    with sync_playwright() as p:
        browser=launch(p,REPORT)
        for width,height,label in VIEWPORTS:
            if selected and label not in selected:continue
            context,page=new_page(browser,REPORT,'capture-'+label,width,height)
            try:
                go(page)
                if DIAGNOSTIC:page.add_style_tag(content='.brands-page .brand-directory-card{aspect-ratio:auto !important}')
                sweep(page)
                if STAGE=='after':wait_artwork(page)
                data=metrics(page)
                paths=[]
                for suffix,full in [('',False),('-full',True)]:
                    target=SHOTS/f'directory-{label}{suffix}.png';page.screenshot(path=str(target),full_page=full,animations='allow');paths.append(str(target.relative_to(OUT)))
                if data['grid']:
                    page.evaluate('(y)=>window.scrollTo({top:y-104,behavior:"instant"})',data['grid']['y']);settle(page)
                    target=SHOTS/f'directory-{label}-cards.png';page.screenshot(path=str(target),animations='allow');paths.append(str(target.relative_to(OUT)))
                details={'metrics':data,'screenshots':paths}
                if STAGE=='after':
                    details['layout']=assert_layout(data)
                    details['paintedIdentity']=pixel_evidence(page,'capture-'+label)
                else:
                    details['baselineVisualAudit']={'collapsedCards':[c['id'] for c in data['cards'] if c['rect']['height']<12 or c['rect']['width']<12],
                        'allCardsHaveUsefulSize':len(data['cards'])==10 and all(c['rect']['height']>150 and c['rect']['width']>100 for c in data['cards']),
                        'loadedBackgrounds':sum(bool(c['photos']) and c['photos'][0]['complete'] and c['photos'][0]['naturalWidth']>0 for c in data['cards']),
                        'note':'A capture pass does not mean these baseline cards are visibly healthy.'}
                    if DIAGNOSTIC:details['interpretation']='Synthetic loss-of-ratio observations only; not evidence of a specific physical iPad cause.'
                REPORT['checks'].append({'case':label,'passed':True,'details':details});print('PASS '+STAGE+'-'+ENGINE+'-'+KIND+'-'+label,flush=True)
            except Exception:
                failure=traceback.format_exc();REPORT['checks'].append({'case':label,'passed':False,'failure':failure});print('FAIL '+label+'\n'+failure,flush=True)
            finally:context.close()
        browser.close()
except Exception:REPORT['harnessFailure']=traceback.format_exc()
raise SystemExit(0 if finish(REPORT,f'capture-{STAGE}-{ENGINE}-{KIND}.json') else 1)
