"""Final polish QA adapters. Read-only DOM measurements; no app/style mocking."""
from collections import Counter
from pathlib import Path
import os
import re
import sys

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(os.environ.get('FRETLINE_QA_OUTPUT_DIR',str(Path(__file__).resolve().parents[1]))).resolve()
OUT.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('FRETLINE_QA_OUTPUT_DIR',str(OUT))
sys.path.insert(0,str(ROOT/'docs/signature-redesign/phase-c/tests'))
from support import (BASE,VIEWPORTS,BRAND_ORDER,RECORDS,BY_ID,new_page,go,sweep_home,
                     paint_ready,viewport_paint_ready,brand_metrics,page_metrics,
                     assert_page,report_template)

CAPTURE_VIEWPORTS=VIEWPORTS+[(1280,1000,'reference-desktop')]


def assert_brand_layout(metrics,width,stage='after'):
    cards=metrics['cards']
    assert [card['id'] for card in cards]==BRAND_ORDER,metrics
    columns=5 if width>=1280 else 3 if width>=900 else 2
    assert len(metrics['columns'].split())==columns,metrics
    assert max(c['rect']['height'] for c in cards)-min(c['rect']['height'] for c in cards)<=1,metrics
    assert sum(len(c['photos']) for c in cards)==10,metrics
    marks=[]
    for card in cards:
        assert card['href']=='/brands/'+card['id'],card
        assert card['countText'] and re.search(r'\b20\b',card['countText']),card
        assert min(card['arrow']['width'],card['arrow']['height'])>=43.5,card
        assert len(card['photos'])==1,card
        photo=card['photos'][0]
        assert photo['complete'] and min(photo['naturalWidth'],photo['naturalHeight'])>0,card
        assert re.search(r'/'+re.escape(card['id'])+r'(?:[-.])',photo['src']),card
        if card['id']=='cordoba' and stage!='before':
            assert not card['logo'] and len(card['fallback'])==1,card
            assert card['fallback'][0]['text']=='Córdoba',card
            mark=card['fallback'][0]['rect']
        else:
            assert len(card['logo'])==1 and not card['fallback'],card
            logo=card['logo'][0]
            assert logo['complete'] and min(logo['naturalWidth'],logo['naturalHeight'])>0,card
            if logo.get('kind')=='photographic':
                assert card['id']=='cordoba' and logo['src']==photo['src'],card
                assert logo['frame'] and 'hidden' in logo['frameOverflow'],card
                mark=logo['frame']
            else:
                assert logo['fit']=='contain',card
                mark=logo['rect']
        assert mark['left']>=card['rect']['left']-1 and mark['right']<=card['rect']['right']+1,card
        assert mark['top']>=card['rect']['top']-1 and mark['bottom']<=card['rect']['bottom']+1,card
        a,b=card['count'],card['arrow']
        overlap=min(a['right'],b['right'])-max(a['left'],b['left'])
        vertical=min(a['bottom'],b['bottom'])-max(a['top'],b['top'])
        assert overlap<=1 or vertical<=1,card
        marks.append({'id':card['id'],'visibleRect':mark,'centerY':(mark['top']+mark['bottom'])/2,
                      'relativeCenterY':((mark['top']+mark['bottom'])/2-card['rect']['top'])/card['rect']['height']})
    return {'columns':columns,'cards':len(cards),'backgroundPhotos':10,
            'imageMarks':sum(bool(c['logo']) for c in cards),
            'typographicNames':sum(bool(c['fallback']) for c in cards),'marks':marks}


def homepage_geometry(page):
    return page.evaluate(r'''()=>{
      const rect=e=>{if(!e)return null;const r=e.getBoundingClientRect();return {left:r.left,top:r.top,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
      const style=e=>{const s=getComputedStyle(e);return {font:s.fontFamily,fontSize:s.fontSize,lineHeight:s.lineHeight,filter:s.filter,objectFit:s.objectFit,objectPosition:s.objectPosition,transform:s.transform}};
      const visibleHeaderIcons=[...document.querySelectorAll('.site-header .site-icon-button')].filter(e=>e.getBoundingClientRect().width>0);
      const headerIconPaint=visibleHeaderIcons.map(e=>{
        const svg=e.querySelector('svg'),ss=svg?getComputedStyle(svg):null;
        const paint=(value,opacity)=>value!=='none'&&value!=='transparent'&&Number(opacity)>0&&!/rgba\([^)]*,\s*0(?:\.0*)?\)$/.test(value);
        return {label:e.getAttribute('aria-label')||e.textContent.trim(),rect:rect(e),svg:rect(svg),
          svgStyle:ss?{display:ss.display,visibility:ss.visibility,opacity:ss.opacity,color:ss.color}:null,
          shapes:svg?[...svg.querySelectorAll('path,circle,rect,line,polyline,polygon,ellipse')].map(shape=>{
            const s=getComputedStyle(shape);let length=0;try{length=shape.getTotalLength()}catch{}
            const stroke=paint(s.stroke,s.strokeOpacity)&&parseFloat(s.strokeWidth)>0,fill=paint(s.fill,s.fillOpacity);
            return {tag:shape.tagName,length,bounds:shape.getBBox().toJSON?shape.getBBox().toJSON():{x:shape.getBBox().x,y:shape.getBBox().y,width:shape.getBBox().width,height:shape.getBBox().height},
              stroke:s.stroke,strokeWidth:s.strokeWidth,strokeOpacity:s.strokeOpacity,fill:s.fill,fillOpacity:s.fillOpacity,
              opacity:s.opacity,painted:length>0&&Number(s.opacity)>0&&s.display!=='none'&&s.visibility!=='hidden'&&(stroke||fill)};
          }):[]};
      });
      const svgCenters=[...document.querySelectorAll('.site-header .site-icon-button,.signature-hero-actions a')].filter(e=>e.getBoundingClientRect().width>0).map(e=>{const svg=e.querySelector('svg'),a=rect(e),b=rect(svg);return {label:e.getAttribute('aria-label')||e.textContent.trim(),rect:a,svg:b,centerDelta:b?((b.top+b.bottom)-(a.top+a.bottom))/2:null}});
      return {hero:rect(document.querySelector('#top')),title:rect(document.querySelector('.signature-hero-title')),description:rect(document.querySelector('.signature-hero-description')),actions:rect(document.querySelector('.signature-hero-actions')),search:rect(document.querySelector('.signature-hero-search')),heroImage:[...document.querySelectorAll('.signature-hero-visual img')].map(i=>({src:i.currentSrc,rect:rect(i),style:style(i)})),header:rect(document.querySelector('.site-header')),svgCenters,headerIconPaint,
        sectionSpacing:[...document.querySelectorAll('.signature-home>section')].map(e=>({id:e.id,rect:rect(e),paddingTop:getComputedStyle(e).paddingTop,paddingBottom:getComputedStyle(e).paddingBottom})),
        brandMarkFrames:[...document.querySelectorAll('.signature-brand-mark')].map(e=>({id:e.closest('[data-brand-id]').dataset.brandId,rect:rect(e)})),
        fallback:[...document.querySelectorAll('[data-brand-fallback]')].map(e=>({text:e.textContent.trim(),rect:rect(e),style:style(e)}))};
    }''')
