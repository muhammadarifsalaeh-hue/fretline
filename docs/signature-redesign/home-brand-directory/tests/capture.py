"""Real Home and Directory viewport/full-page/section captures; no app mutation."""
from PIL import Image
from playwright.sync_api import sync_playwright
import math
import os
import traceback
from directory_support import (OUT, VIEWPORTS, new_page, go, sweep, viewport_paint_ready, page_metrics,
                               assert_page, marquee_metrics, directory_metrics,
                               assert_marquee, assert_directory, report_template, finish_report)

STAGE=os.environ.get('FRETLINE_QA_STAGE','after')
assert STAGE in {'before','after'},STAGE
MOTION=os.environ.get('FRETLINE_QA_MOTION','no-preference')
assert MOTION in {'no-preference','reduce'},MOTION
SHOTS=OUT/STAGE
SHOTS.mkdir(parents=True,exist_ok=True)
REPORT=report_template()
REPORT['stage']=STAGE
REPORT['motionPreference']=MOTION
REPORT['method']='Actual production app; native vertical/horizontal scrolling, fonts and decoded visible images. Animations are allowed to run naturally without seeking or screenshot-only DOM/style replacements. Section crops use real full-page pixels.'
REPORT['limitations']=['Chromium/Linux viewport and touch emulation only; physical Safari/iPad not tested.',
    'Default captures show a natural frame of the running marquee and its default controls; viewport and full-page captures may record different animation phases. Continuous behavior is verified separately.' if MOTION=='no-preference' else 'Optional reduced-motion captures show the real static/manual-scroll accessibility presentation, not the default animated layout.',
    'Photographic fidelity requires manual reference review.']
selected=set(filter(None,os.environ.get('FRETLINE_QA_VIEWPORTS','').split(',')))


def capture(page,slug,selector,label):
    bounds=page.locator(selector).evaluate('e=>{const r=e.getBoundingClientRect();return {x:r.left+scrollX,y:r.top+scrollY,width:r.width,height:r.height}}')
    viewport=SHOTS/f'{slug}-{label}.png';full=SHOTS/f'{slug}-{label}-full.png';section=SHOTS/f'{slug}-{label}-section.png'
    page.screenshot(path=str(viewport),animations='allow')
    page.screenshot(path=str(full),full_page=True,animations='allow')
    with Image.open(full) as image:
        scale=image.width/page.viewport_size['width']
        image.crop((math.floor(bounds['x']*scale),math.floor(bounds['y']*scale),min(image.width,math.ceil((bounds['x']+bounds['width'])*scale)),min(image.height,math.ceil((bounds['y']+bounds['height'])*scale)))).save(section)
    return {'bounds':bounds,'screenshots':[str(x.relative_to(OUT)) for x in [viewport,full,section]]}


try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('FRETLINE_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        for width,height,label in VIEWPORTS:
            if selected and label not in selected:continue
            context,page=new_page(browser,REPORT,'capture-'+STAGE+'-'+label,width,height,motion=MOTION)
            try:
                go(page);sweep(page);home=page_metrics(page);assert_page(home)
                home_details=capture(page,'home','#brands',label)
                if STAGE=='after':
                    home_details['marqueeGeometry']=marquee_metrics(page)
                    home_details['marquee']=assert_marquee(home_details['marqueeGeometry'],reduced=MOTION=='reduce')
                    page.evaluate('(top)=>window.scrollTo({top,behavior:"instant"})',max(0,home_details['bounds']['y']-120))
                    viewport_paint_ready(page)
                    overview=SHOTS/f'home-marquee-{label}.png'
                    page.screenshot(path=str(overview),animations='allow')
                    home_details['screenshots'].append(str(overview.relative_to(OUT)))
                go(page,'/brands');sweep(page);directory=page_metrics(page);assert_page(directory)
                directory_details=capture(page,'directory','.brands-page',label)
                directory_details['geometry']=directory_metrics(page)
                if STAGE=='after':
                    directory_details['layout']=assert_directory(directory_details['geometry'])
                    grid_top=page.locator('.brand-directory-grid').evaluate('e=>e.getBoundingClientRect().top+scrollY')
                    page.evaluate('(top)=>window.scrollTo({top,behavior:"instant"})',max(0,grid_top-104))
                    viewport_paint_ready(page)
                    overview=SHOTS/f'directory-cards-{label}.png'
                    page.screenshot(path=str(overview),animations='allow')
                    directory_details['screenshots'].append(str(overview.relative_to(OUT)))
                REPORT['checks'].append({'case':label,'passed':True,'home':home,'homeCapture':home_details,'directory':directory,'directoryCapture':directory_details})
                print('PASS capture-'+STAGE+'-'+label,flush=True)
            except Exception:
                failure=traceback.format_exc();REPORT['checks'].append({'case':label,'passed':False,'failure':failure});print('FAIL '+label+'\n'+failure,flush=True)
            finally:context.close()
        browser.close()
except Exception:REPORT['harnessFailure']=traceback.format_exc()
raise SystemExit(0 if finish_report(REPORT,f'capture-{STAGE}.json') else 1)
