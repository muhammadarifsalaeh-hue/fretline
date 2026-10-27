from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import subprocess,time,os,signal,urllib.request,json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE='http://127.0.0.1:5452'
report={'checks':[],'errors':[],'physicalIPadSafariTested':False,'mode':'Development source review; final production QA is performed separately by root.'}
with (OUT/'server.txt').open('w') as log:
 server=subprocess.Popen(['npm','run','dev','--','--host','0.0.0.0','--port','5452','--strictPort'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  for _ in range(100):
   if server.poll() is not None:raise RuntimeError('Review server failed')
   try:
    with urllib.request.urlopen(BASE,timeout=1) as response:
     if response.status==200:break
   except OSError:pass
   time.sleep(.1)
  else:raise RuntimeError('Review server not ready')
  with sync_playwright() as p:
   b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
   for label,w,h in [('desktop',1440,1000),('tablet',768,1024),('mobile',390,844),('small',320,740)]:
    c=b.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion='reduce');page=c.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else None)
    page.goto(BASE+'/find-my-guitar',wait_until='networkidle');expect(page.locator('h1')).to_have_text('Find My Guitar Quiz')
    for im in page.locator('main img').all():im.scroll_into_view_if_needed();im.evaluate('(i)=>i.decode()')
    metrics=page.evaluate('({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth})');assert metrics['scrollWidth']<=w,metrics
    assert page.locator('input[name=type]').count()==5
    assert page.locator('.quiz-editorial-triptych img').count()==3
    page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'quiz-{label}.png'),full_page=True,animations='disabled')
    page.get_by_role('button',name='เริ่มค้นหากีตาร์',exact=True).click();expect(page.locator('#quiz-type-title')).to_be_focused()
    choices=[('type','acoustic',5),('level','beginner',3),('style','folk',5),('budget','mid',5),('priority','value',4)]
    for index,(field,value,count) in enumerate(choices):
     expect(page.get_by_role('progressbar')).to_have_attribute('aria-valuenow',str(index+1));assert page.locator(f'input[name={field}]').count()==count
     page.locator(f'input[name={field}][value={value}]').locator('..').click();expect(page.locator(f'input[name={field}][value={value}]')).to_be_checked();expect(page.locator(f'input[name={field}][value={value}]').locator('..')).to_have_class(__import__('re').compile('is-selected'))
     assert page.locator('.quiz-option-description').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=12
     page.locator('.quiz-step-actions button[type=submit]').click()
    expect(page.locator('.quiz-results-page')).to_be_visible();assert page.locator('.match-card').count()>0
    for im in page.locator('main img').all():im.scroll_into_view_if_needed();im.evaluate('(i)=>i.decode()')
    after=page.evaluate('document.documentElement.scrollWidth');assert after<=w,after;page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'results-{label}.png'),full_page=True,animations='disabled')
    report['checks'].append({'viewport':label,'width':w,'overflow':False,'allFiveSteps':True,'optionCounts':[5,3,5,5,4],'photoTriptychLoaded':True,'realResults':page.locator('.match-card').count()});print('PASS',label,flush=True);c.close()
   b.close()
  report['passed']=len(report['checks'])==4 and not report['errors'];(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert report['passed'],report
 finally:
  if server.poll() is None:
   os.killpg(server.pid,signal.SIGTERM)
   try:server.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait()
