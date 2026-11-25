# قياس أداء المحرك (بدون أوفيس): draw لكل شكل، وزمن حدث السحب الواحد. يطبع median و P95 بالمللي ثانية.
import asyncio, json, sys
from playwright.async_api import async_playwright
APP=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/uula-geometry/app.html'
JS=r'''
async ()=>{
 const q=a=>{a=a.slice().sort((x,y)=>x-y); return [+(a[Math.floor(a.length*.5)]).toFixed(3), +(a[Math.min(a.length-1,Math.floor(a.length*.95))]).toFixed(3)]};
 const R={};
 const cases={
  tri:()=>{S.empty=false;S.tab='p';S.p=defaults().p;},
  circle_tab:()=>{S.empty=false;S.tab='c';},
  cube:()=>{S.empty=false;S.tab='s';S.s.kind='cube';},
  cyl:()=>{S.empty=false;S.tab='s';S.s.kind='cyl';},
  composite:()=>{S.empty=false;S.tab='p';
    const c=[160,150],r=100,P=a=>[c[0]+r*Math.cos(a*Math.PI/180),c[1]+r*Math.sin(a*Math.PI/180)];
    const pts=[P(150),P(30),P(-120),P(-20),c.slice(),[160,200],[150,90]];
    const G=mkFree(pts,[[0,1],[4,0],[4,1],[2,0],[2,1],[2,3],[4,6],[4,5]]); G.circles=[{c:c.slice(),r}]; G.onc={0:[0,150],1:[0,30],2:[0,-120],3:[0,-20]}; S.p=G;}
 };
 for(const [k,f] of Object.entries(cases)){
   f(); syncUI&&syncUI(); draw(); const t=[];
   for(let i=0;i<150;i++){ const a=performance.now(); draw(); $('fig').getBBox(); document.body.offsetHeight; t.push(performance.now()-a); }
   const b=[]; for(let i=0;i<150;i++){ const a=performance.now(); build(); b.push(performance.now()-a); }
   R[k]={draw:q(t),build:q(b),stateKB:+(JSON.stringify(S).length/1024).toFixed(1),prims:PR.length};
 }
 if(typeof applyTpl==='function'){ applyTpl('genProblem'); const t=[]; for(let i=0;i<150;i++){ const a=performance.now(); draw(); $('fig').getBBox(); t.push(performance.now()-a); } R.genProblem={draw:q(t),prims:PR.length};
   const t2=[]; for(let i=0;i<150;i++){ const a=performance.now(); setVertex(2,add(S.p.pts[2],[Math.sin(i)*3,1])); t2.push(performance.now()-a); } R.genProblem.solve_on_drag=q(t2);
   const t3=[]; for(let i=0;i<60;i++){ const a=performance.now(); applyTpl('genProblem'); t3.push(performance.now()-a); } R.genProblem.create=q(t3); }
 // حدث سحب حقيقي على رأس (المسار الكامل: parse + قيد + draw)
 cases.composite(); draw();
 const fig=$('fig'), m=fig.getScreenCTM(), sc=([x,y])=>[x*m.a+y*m.c+m.e, x*m.b+y*m.d+m.f];
 const v=document.querySelector('[data-h="vert"][data-i="3"]'); const p0=S.p.pts[3]; const [x0,y0]=sc(p0);
 v.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:x0,clientY:y0,pointerId:1,button:0}));
 const t=[]; for(let i=1;i<=150;i++){ const [x,y]=sc([p0[0]+Math.sin(i/10)*30,p0[1]+i%30]); const a=performance.now(); fig.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:x,clientY:y,pointerId:1})); if(typeof dragFrame==='function'&&DRAG_RAF){ cancelAnimationFrame(DRAG_RAF); dragFrame(); } $('fig').getBBox(); document.body.offsetHeight; t.push(performance.now()-a); }
 fig.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1}));
 R.drag_event_composite=q(t);
 return R;
}'''
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':360,'height':900})
    await pg.route('**/office.js',lambda r:r.fulfill(body='',content_type='text/javascript'))
    t0=await pg.evaluate('performance.now()') if False else None
    await pg.goto(APP); await pg.wait_for_function('typeof draw==="function"')
    nav=await pg.evaluate('JSON.stringify((()=>{const n=performance.getEntriesByType("navigation")[0]; return {domContentLoaded:+n.domContentLoadedEventEnd.toFixed(1), load:+n.loadEventEnd.toFixed(1)}})())')
    await pg.evaluate('localStorage.clear()')
    r=await pg.evaluate(JS); r['open']=json.loads(nav)
    print(json.dumps(r,ensure_ascii=False,indent=1)); await b.close()
asyncio.run(main())
