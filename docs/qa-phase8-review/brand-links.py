"""Follow every actual brand card link; verify all ten detail routes and model links."""
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,os,csv
OUT=Path(__file__).parent;BASE=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:4188')
ids={g['id'] for g in csv.DictReader((OUT.parent/'qa-phase7/catalog-200.csv').open(encoding='utf-8-sig'))};report={'brands':[],'errors':[]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pg=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.goto(BASE+'/brands',wait_until='networkidle')
 links=pg.locator('.brand-directory-card').evaluate_all('(els)=>els.map(e=>({href:e.getAttribute("href"),brand:e.getAttribute("data-brand-id")}))')
 for brand in links:
  pg.goto(BASE+brand['href'],wait_until='networkidle');expect(pg.locator('.brand-model-grid article')).to_have_count(20)
  urls=pg.locator('.brand-model-grid article h3 a').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
  valid=len(urls)==20 and all(u.removeprefix('/guitars/') in ids for u in urls)
  report['brands'].append({**brand,'modelCount':len(urls),'allDetailLinksResolve':valid});assert valid,brand
  print(brand['href'],'20 working model IDs',flush=True)
 b.close()
report['passed']=len(report['brands'])==10 and not report['errors'];(OUT/'brand-links-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
