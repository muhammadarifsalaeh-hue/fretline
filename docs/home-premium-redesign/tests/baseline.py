from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'before';OUT.mkdir(exist_ok=True)
assert not (OUT/'baseline.json').exists(), 'Never overwrite frozen before screenshots; use a distinct evidence folder.'
BASE='http://127.0.0.1:5451';COMMIT='4bbecf86585ab14cca2d23e2b65f090db20a1816'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
paths=git('ls-tree','-r','--name-only',COMMIT,'src/data','src/features/practice','src/components/quiz','src/components/layout','src/utils','src/context','src/pages','src/components/compare','scripts/practice','src/i18n','src/styles/premium-quiz.css','src/styles/premium-compare.css','src/styles/tokens.css','src/styles/polish.css','src/index.css','src/assets/guitars','src/assets/discovery','src/assets/home-brands','package.json','package-lock.json','vite.config.js').decode().splitlines()
excluded={'src/data/homeBrandAssets.js','src/pages/HomePage.jsx','src/pages/ImageCreditsPage.jsx','src/components/compare/CompareSection.jsx'}
protected={s:sha(git('show',COMMIT+':'+s)) for s in paths if s not in excluded}
report={'baselineCommit':COMMIT,'protectedSHA256':protected,'physicalIPadSafariTested':False,'screenshots':[],'errors':[],'productionIndexSHA256':sha((ROOT/'dist/index.html').read_bytes())}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,w,h in [('desktop',1440,1000),('tablet',768,1024),('mobile',390,844)]:
  c=b.new_context(viewport={'width':w,'height':h},reduced_motion='reduce');page=c.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.goto(BASE+'/',wait_until='networkidle');page.evaluate('document.fonts.ready');expect(page.locator('#home-find-title')).to_be_visible()
  for region,name in [('#brands','brands'),('#find','quiz'),('#compare','compare')]:
   el=page.locator(region);el.scroll_into_view_if_needed();page.wait_for_timeout(500)
   for im in el.locator('img').all():
    if im.is_visible():im.evaluate('(i)=>i.decode()')
   filename=name+'-'+label+'.png';el.screenshot(path=str(OUT/filename),animations='disabled');report['screenshots'].append(filename)
  page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/('homepage-'+label+'.png')),full_page=True,animations='disabled');report['screenshots'].append('homepage-'+label+'.png');c.close()
 b.close()
report['passed']=not report['errors'] and len(report['screenshots'])==12
(OUT/'baseline.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('BASELINE',report['passed'],len(protected),'protected files',len(report['screenshots']),'real screenshots')
assert report['passed'],report
