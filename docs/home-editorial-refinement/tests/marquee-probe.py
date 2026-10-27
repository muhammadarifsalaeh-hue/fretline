# Unchanged production-input and loop probe copied from the previous accepted Home harness.
# Kept local for replay; requires page/context/engine/viewport and imported expect/time/BASE.
def carousel(page,context,engine,viewport):
 go(page);rail=page.locator('[data-marquee-viewport]');rail.evaluate('(e)=>e.scrollIntoView({block:"center"})');page.wait_for_timeout(200);expect(rail).to_have_attribute('data-marquee-motion','auto');assert page.locator('#brands button').count()==0;assert not page.locator('#brands [data-marquee-prev],#brands [data-marquee-next],#brands [data-marquee-pause]').count();assert rail.evaluate('(e)=>getComputedStyle(e).scrollbarWidth')=='none'
 groups=rail.locator('.signature-marquee-group');assert groups.count()==3
 identities=groups.evaluate_all('(nodes)=>nodes.map(n=>[...n.querySelectorAll("a")].map(a=>({id:a.dataset.brandId,href:a.getAttribute("href"),image:a.querySelector("img")?.getAttribute("src")||null})))');assert identities[0]==identities[1]==identities[2];assert len(identities[1])==10
 W=rail.locator('[data-marquee-primary]').evaluate('(e)=>e.getBoundingClientRect().width')
 # A main-thread read between WebKit's delayed startup frames can observe a
 # stale native position. Sample position and time together after a real frame,
 # keeping the 30px/sec target and tightening the earlier broad tolerance.
 sample='(e)=>new Promise(resolve=>requestAnimationFrame(t=>resolve({left:e.scrollLeft,frameTime:t,observedTime:performance.now()})))'
 before_sample=rail.evaluate(sample);page.wait_for_timeout(800);after_sample=rail.evaluate(sample)
 before=before_sample['left'];after=after_sample['left'];delta=(after-before)%W;elapsed=after_sample['frameTime']-before_sample['frameTime'];assert elapsed>0,(before_sample,after_sample)
 pixels_per_second=delta*1000/elapsed;assert 27<=pixels_per_second<=33,(before_sample,after_sample,pixels_per_second)
 rb=rail.bounding_box();x=rb['x']+min(rb['width']*.7,500);y=rb['y']+rb['height']/2;page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-125,y,steps=12);expect(rail).to_have_attribute('data-marquee-dragging','true');dragged=rail.evaluate('(e)=>e.scrollLeft');page.mouse.up();assert page.url==BASE+'/'
 assert (dragged-after)%W>70,(after,dragged);page.wait_for_timeout(1800);expect(rail).to_have_attribute('data-marquee-motion','auto');resumed=rail.evaluate('(e)=>e.scrollLeft');assert (resumed-dragged)%W>8,(dragged,resumed)
 assert page.evaluate('([x,y])=>Boolean(document.elementFromPoint(x,y)?.closest("[data-marquee-viewport]"))',[x,y]),'Gesture must hit rail rather than fixed navigation'
 native_touch=False;wheel_evidence=None;touch_note='Mouse drag plus browser horizontal wheel; native touch drag is unavailable in Linux WebKit automation.'
 if engine=='chromium' and viewport!='desktop':
  session=context.new_cdp_session(page);rb=rail.bounding_box();tx=rb['x']+rb['width']*.8;ty=rb['y']+rb['height']/2;before_touch=rail.evaluate('(e)=>e.scrollLeft');session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':tx,'y':ty,'id':1}]})
  for i in range(1,9):session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':tx-i*16,'y':ty,'id':1}]});time.sleep(.025)
  held=rail.evaluate('(e)=>e.scrollLeft');page.wait_for_timeout(1250);still_held=rail.evaluate('(e)=>e.scrollLeft');assert abs(still_held-held)<=2,('Autoplay must not resume while a native touch remains down',held,still_held);expect(rail).to_have_attribute('data-marquee-motion','manual');session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});page.wait_for_timeout(300);after_touch=rail.evaluate('(e)=>e.scrollLeft');assert (after_touch-before_touch)%W>45,(before_touch,after_touch);native_touch=True;touch_note='Chromium native browser touch gesture dispatched via CDP; this is not a physical iPad.'
  page.wait_for_timeout(1800);expect(rail).to_have_attribute('data-marquee-motion','auto');session.detach()
 else:
  # Native wheel scrolling is asynchronous in WebKit. Keep the original >70px
  # movement requirement, but observe the actual trusted input lifecycle rather
  # than assume a 200ms IPC wait includes delivery and scrolling. Autoplay is
  # explicitly forbidden from supplying any pixels needed for a pass.
  page.mouse.move(x,y)
  rail.evaluate('''e=>new Promise(resolve=>requestAnimationFrame(t=>{
    window.__homeWheelProbe={before:{frameTime:t,time:performance.now(),left:e.scrollLeft},event:null,samples:[],seenManual:false,outcome:null};
    e.addEventListener('wheel',event=>{const p=__homeWheelProbe,now=performance.now();
      p.event={time:now,leftAtDelivery:e.scrollLeft,deltaX:event.deltaX,deltaY:event.deltaY,trusted:event.isTrusted};
      p.maximumPreEventAutoPixels=Math.max(0,now-p.before.frameTime)*30/1000;
    },{once:true,passive:true});resolve(__homeWheelProbe.before)}))''')
  page.mouse.wheel(180,0)
  page.wait_for_function('''([e,width])=>{const p=__homeWheelProbe;if(!p.event)return false;
    const delta=((e.scrollLeft-p.before.left)%width+width)%width,mode=e.dataset.marqueeMotion;
    const minimumNativePixels=Math.max(0,delta-p.maximumPreEventAutoPixels);
    p.samples.push({time:performance.now(),left:e.scrollLeft,totalDelta:delta,minimumNativePixels,mode});
    if(mode==='manual')p.seenManual=true;
    if(p.event.trusted&&mode==='manual'&&minimumNativePixels>70){p.outcome='native-movement-passed';return true}
    if(p.seenManual&&mode==='auto'){p.outcome='autoplay-resumed-before-native-movement';return true}
    return false}''',arg=[rail.element_handle(),W],timeout=2000)
  wheel_evidence=page.evaluate('__homeWheelProbe');assert wheel_evidence['outcome']=='native-movement-passed',wheel_evidence
  page.wait_for_timeout(1800);expect(rail).to_have_attribute('data-marquee-motion','auto')
 rail.evaluate('(e)=>{const w=e.querySelector("[data-marquee-primary]").getBoundingClientRect().width;e.scrollLeft=2*w-2}');page.wait_for_timeout(50)
 frames=rail.evaluate('''async(e)=>{const samples=[];for(let i=0;i<135;i++){await new Promise(requestAnimationFrame);const r=e.getBoundingClientRect();const links=[...e.querySelectorAll("a")].map(a=>a.getBoundingClientRect()).filter(a=>a.right>r.left&&a.left<r.right);samples.push({left:e.scrollLeft,covered:links.length>0&&Math.min(...links.map(a=>a.left))<=r.left+1&&Math.max(...links.map(a=>a.right))>=r.right-1});}return samples}''')
 jumps=[b['left']-a['left'] for a,b in zip(frames,frames[1:])];assert any(d<-W/2 for d in jumps),('No actual loop boundary crossed',min(jumps),W);normalized=[d+W if d<-W/2 else d-W if d>W/2 else d for d in jumps];assert min(normalized)>=-1 and max(normalized)<=3,(min(normalized),max(normalized));assert all(f['covered'] for f in frames),'Loop must not expose blank rail'
 return {'automaticMotion':{'targetPixelsPerSecond':30,'allowedPixelsPerSecond':[27,33],'measuredPixelsPerSecond':pixels_per_second,'pixels':delta,'elapsedMs':elapsed,'nominalWaitMs':800,'before':before_sample,'after':after_sample},'nativeWheel':wheel_evidence,'measuredGroupWidth':W,'actualLoopCrossed':True,'maximumNormalizedFrameDelta':max(normalized),'noBlankFrames':True,'mouseDragAndResume':True,'nativeChromiumTouchGesture':native_touch,'nativeTouchHoldChecked':native_touch,'touchLimit':touch_note,'allThreeCopiesIdentical':True,'realStandaloneLogoFiles':sum(bool(i['image']) for i in identities[1]),'typographicFallbackBrands':[i['id'] for i in identities[1] if not i['image']],'noControlsOrScrollbar':True}
