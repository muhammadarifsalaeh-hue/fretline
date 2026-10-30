"""Local lab only: does not claim field Core Web Vitals or real-device INP."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json, statistics, argparse

P=argparse.ArgumentParser();P.add_argument('--url',required=True);P.add_argument('--before-url',required=True);P.add_argument('--output',type=Path,required=True);A=P.parse_args();A.output.parent.mkdir(parents=True,exist_ok=True)
INIT="""window.experienceMetrics={lcp:[],shifts:[],events:[]};
new PerformanceObserver(list=>list.getEntries().forEach(e=>experienceMetrics.lcp.push({time:e.startTime,size:e.size,url:e.url,tag:e.element?.tagName}))).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(list=>list.getEntries().forEach(e=>{if(!e.hadRecentInput)experienceMetrics.shifts.push({time:e.startTime,value:e.value})})).observe({type:'layout-shift',buffered:true});
new PerformanceObserver(list=>list.getEntries().forEach(e=>{if(e.interactionId)experienceMetrics.events.push({name:e.name,duration:e.duration,interactionId:e.interactionId})})).observe({type:'event',buffered:true,durationThreshold:16});"""
report={'environment':{'engine':'local Chromium','cpuSlowdown':4,'latencyMs':40,'downloadMbps':10,'uploadMbps':5,'cache':'fresh browser context per run','viewport':[390,844],'samplesPerVersion':3,'fieldCoreWebVitalsVerified':False,'note':'Controlled local lab, not production RUM. Event timing samples are not a certified field INP.'},'runs':[]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for version,url in [('before',A.before_url),('after',A.url)]:
  for n in range(3):
   context=b.new_context(viewport={'width':390,'height':844},has_touch=True,reduced_motion='no-preference');page=context.new_page();page.add_init_script(INIT);session=context.new_cdp_session(page)
   session.send('Network.enable');session.send('Network.setCacheDisabled',{'cacheDisabled':True});session.send('Network.emulateNetworkConditions',{'offline':False,'latency':40,'downloadThroughput':10*1024*1024/8,'uploadThroughput':5*1024*1024/8});session.send('Emulation.setCPUThrottlingRate',{'rate':4})
   page.goto(url,wait_until='load');page.locator('main h1').wait_for();page.evaluate('document.fonts.ready');page.wait_for_timeout(2800)
   # A genuine tap ends the initial LCP window before the six-second slideshow.
   page.locator('#top input').tap();page.wait_for_timeout(150);page.locator('#top input').fill('Yamaha');page.wait_for_timeout(300)
   m=page.evaluate("""()=>({...experienceMetrics,resources:performance.getEntriesByType('resource').map(r=>({url:r.name,type:r.initiatorType,bytes:r.transferSize,decoded:r.decodedBodySize,start:r.startTime})),navigation:performance.getEntriesByType('navigation')[0].toJSON()})""")
   best=0;total=0;first=0;last=0
   for s in m['shifts']:
    if s['time']-last>1000 or s['time']-first>5000:total=0;first=s['time']
    total+=s['value'];last=s['time'];best=max(best,total)
   assert not [r for r in m['resources'] if 'practice-three' in r['url'] or '.glb' in r['url']],'3D must not load on Home'
   item={'version':version,'run':n+1,'lcpMs':m['lcp'][-1]['time'] if m['lcp'] else None,'cls':best,'eventTimingMaxMs':max([e['duration'] for e in m['events']],default=0),'initialSceneTransfers':[r for r in m['resources'] if ('quiz-studio' in r['url'] or 'compare-guitars' in r['url']) and r['start']<2000],'resourceBytes':sum(r['bytes'] for r in m['resources']),'homeLoaded3D':False,'raw':m}
   report['runs'].append(item);print(json.dumps({k:v for k,v in item.items() if k!='raw'}),flush=True);A.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');context.close()
 b.close()
report['summary']={v:{'medianLcpMs':statistics.median(r['lcpMs'] for r in report['runs'] if r['version']==v),'medianCLS':statistics.median(r['cls'] for r in report['runs'] if r['version']==v),'maxObservedLabEventMs':max(r['eventTimingMaxMs'] for r in report['runs'] if r['version']==v)} for v in ['before','after']};A.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report['summary']),flush=True)
