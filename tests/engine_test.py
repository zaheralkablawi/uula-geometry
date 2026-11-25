# اختبارات المحرك الهندسي: تُنشئ الأشكال بأدوات الواجهة (نقرات حقيقية) ثم تتحقق من العلاقات رياضيًا بعد سحب النقاط.
import asyncio, json, sys, math
from playwright.async_api import async_playwright
APP='file:///home/claude/uula-geometry/app.html'
FAIL=[]
def check(name,cond,info=''):
  print(('PASS ' if cond else 'FAIL ')+name+(' '+str(info) if info and not cond else '')); 
  if not cond: FAIL.append(name)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':360,'height':1000})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/office.js',lambda r:r.fulfill(body='',content_type='text/javascript'))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_function('typeof draw==="function"')
    E=lambda js: pg.evaluate(js)
    async def tool(k):
      sel='#segCons [data-k="%s"]'%k if k.startswith('k_') else '#segFree [data-k="%s"]'%k
      if await E('FT')!=k: await pg.click(sel)
    async def click_obj(h,i):   # نقر على عنصر في المعاينة بمركزه
      xy=await E("""(()=>{ const el=document.querySelector('#fig [data-h="%s"][data-i="%s"]'); if(!el) return null; const G=S.p, m=$('fig').getScreenCTM(); let q;
        if('%s'==='vert') q=G.pts[%s]; else if('%s'==='side'){ const sd=G.sides[%s]; q=[G.pts[sd.a][0]*.6+G.pts[sd.b][0]*.4,G.pts[sd.a][1]*.6+G.pts[sd.b][1]*.4]; } else { const o=G.circles[%s]; q=[o.c[0]+o.r*Math.cos(-2.2),o.c[1]+o.r*Math.sin(-2.2)]; }
        return [q[0]*m.a+q[1]*m.c+m.e, q[0]*m.b+q[1]*m.d+m.f]; })()"""%(h,i,h,i,h,i,i))
      assert xy, (h,i); await pg.mouse.click(*xy); await pg.wait_for_timeout(30)
    async def drag(i,to):
      await E("""(()=>{ const G=S.p, m=$('fig').getScreenCTM(), sc=q=>[q[0]*m.a+q[1]*m.c+m.e, q[0]*m.b+q[1]*m.d+m.f]; const el=document.querySelector('#fig [data-h="vert"][data-i="%d"]'), a=sc(G.pts[%d]), z=sc(%s);
        el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:a[0],clientY:a[1],pointerId:1,button:0}));
        for(let k=1;k<=6;k++) $('fig').dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:a[0]+(z[0]-a[0])*k/6,clientY:a[1]+(z[1]-a[1])*k/6,pointerId:1}));
        $('fig').dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1})); })()"""%(i,i,json.dumps(to)))
    async def setup(js):
      await E("()=>{ S.empty=false; S.tab='p'; %s; FT='move'; syncUI(); draw(); }"%js)
    G=lambda: E("JSON.parse(JSON.stringify(S.p))")
    d=lambda a,b: math.hypot(a[0]-b[0],a[1]-b[1])
    dotp=lambda u,v:u[0]*v[0]+u[1]*v[1]
    sub=lambda a,b:[a[0]-b[0],a[1]-b[1]]
    # 1) نقطة على الدائرة تبقى عليها، وتتبعها عند تحريك المركز
    await setup("S.p=mkFree([[160,130]],[]); S.p.circles=[{c:[160,130],r:80,cp:0}]")
    await tool('addpt'); await click_obj('circ',0)
    await tool('move'); await drag(1,[300,40]); g=await G()
    check('point stays on circle after drag', abs(d(g['pts'][1],g['circles'][0]['c'])-80)<1e-6, g['pts'][1])
    await drag(0,[120,150]); g=await G()
    check('circle follows its center point', d(g['circles'][0]['c'],[120,150])<2 and abs(d(g['pts'][1],g['circles'][0]['c'])-80)<1e-6)
    # 2) المماسان من نقطة خارجية: التعامد يبقى بعد تحريك النقطة الخارجية
    await setup("S.p=mkFree([[100,130],[270,130]],[]); S.p.circles=[{c:[100,130],r:60,cp:0}]")
    await tool('k_tan'); await click_obj('vert',1); await click_obj('circ',0)
    g=await G(); n=len(g['pts'])
    check('two tangent points created', n==4, n)
    for to in ([300,40],[230,220],[175,135]):
      await tool('move'); await drag(1,to); g=await G(); O=g['circles'][0]['c']; P=g['pts'][1]
      for k in (2,3):
        T=g['pts'][k]; check('tangent ⟂ radius (P=%s,T%d)'%(to,k), abs(dotp(sub(T,O),sub(P,T)))<1e-6*max(1,d(T,O)*d(P,T)) and abs(d(T,O)-60)<1e-6)
    await drag(1,[110,140]); g=await G()   # نقطة داخل الدائرة: حالة مستحيلة
    check('tangent from inside: no NaN, marked bad', all(all(map(math.isfinite,q)) for q in g['pts']) and any(v.get('bad') for v in g['def'].values()))
    # 3) المنتصف والعمود
    await setup("S.p=mkFree([[40,200],[280,180],[150,40]],[[0,1]])")
    await tool('k_mid'); await click_obj('side',0); g=await G()
    check('midpoint', d(g['pts'][3],[160,190])<1e-6 and len(g['sides'])==2)
    await tool('k_perp'); await click_obj('vert',2); await click_obj('side',0)
    await tool('move'); await drag(0,[20,150]); await drag(2,[230,60]); g=await G()
    F=[k for k,v in g['def'].items() if v['t']=='foot'][0]; F=int(F); A,B,C=g['pts'][0],g['pts'][1],g['pts'][2]; Fp=g['pts'][F]
    check('foot ⟂ after drags', abs(dotp(sub(C,Fp),sub(B,A)))<1e-6*d(B,A)*max(1,d(C,Fp)))
    check('midpoint after drags', d(g['pts'][3],[(A[0]+B[0])/2,(A[1]+B[1])/2])<1e-6)
    check('right-angle mark set', any(v.get('right') for v in g['angs'].values()))
    # 4) التقاطعات
    await setup("S.p=mkFree([[40,40],[280,200],[40,200],[280,40]],[[0,1],[2,3]]); S.p.circles=[{c:[160,120],r:70}]")
    await tool('k_inter'); await click_obj('side',0); await click_obj('side',1); g=await G()
    X=g['pts'][4]; check('line-line intersection', d(X,[160,120])<1e-6, X)
    await tool('k_inter'); await click_obj('side',0); await click_obj('circ',0); g=await G()
    xs=[g['pts'][int(k)] for k,v in g['def'].items() if v['t']=='xlc']; check('line-circle: 2 points on circle', len(xs)==2 and all(abs(d(q,[160,120])-70)<1e-6 for q in xs), [xs,g['def'],g['sides']])
    await setup("S.p=mkFree([],[]); S.p.circles=[{c:[120,120],r:60},{c:[200,120],r:50}]")
    await tool('k_inter'); await click_obj('circ',0); await click_obj('circ',1); g=await G()
    xs=g['pts']; check('circle-circle: 2 points on both', len(xs)==2 and all(abs(d(q,[120,120])-60)<1e-6 and abs(d(q,[200,120])-50)<1e-6 for q in xs))
    # 5) الدائرة المحيطة والداخلية
    await setup("S.p=mkFree([[60,200],[270,190],[120,50]],[[0,1],[1,2],[2,0]])")
    await tool('k_c3'); [await click_obj('vert',i) for i in (0,1,2)]
    await tool('k_cin'); [await click_obj('vert',i) for i in (0,1,2)]
    await tool('move'); await drag(2,[200,40]); g=await G(); P=g['pts']; c0,c1=g['circles']
    check('circumcircle passes through vertices', all(abs(d(P[i],c0['c'])-c0['r'])<1e-6 for i in range(3)))
    def segd(q,a,b):
      t=max(0,min(1,dotp(sub(q,a),sub(b,a))/dotp(sub(b,a),sub(b,a)))); return d(q,[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t])
    check('incircle tangent to all sides', all(abs(segd(c1['c'],P[a],P[b])-c1['r'])<1e-6 for a,b in ((0,1),(1,2),(2,0))))
    cen=[int(k) for k,v in g['def'].items() if v['t']=='cen']; check('centers follow circles', d(P[cen[0]],c0['c'])<1e-9 and d(P[cen[1]],c1['c'])<1e-9)
    # 6) دائرة مرتبطة بنقطتين (المركز ونقطة على المحيط)
    await setup("S.p=mkFree([[150,120],[220,120]],[])")
    await tool('circ'); await click_obj('vert',0); await click_obj('vert',1)
    await tool('move'); await drag(1,[150,30]); g=await G()
    check('circle radius follows its point', abs(g['circles'][0]['r']-90)<1e-6)
    # 7) حذف نقطة تعتمد عليها نقاط أخرى: لا انهيار، والتابعة تبقى حرة
    await E("()=>{ freeDelPoint(S.p,0); solve(S.p); draw(); }"); g=await G()
    check('delete base point keeps others', len(g['pts'])==1 and not g.get('circles',[{}])[0].get('cp'))
    # 8) وتر موازٍ من نقطة على الدائرة، ومستقيم موازٍ من نقطة حرة
    await setup("S.p=mkFree([[160,125],[80,170],[240,170],[100,60],[290,30]],[[1,2]]); S.p.circles=[{c:[160,125],r:91.8,cp:0}]; S.p.onc={1:[0,ang(sub([80,170],[160,125]))],2:[0,ang(sub([240,170],[160,125]))]}; solve(S.p)")
    await tool('addpt'); await click_obj('circ',0)
    n0=len((await G())['pts'])-1
    await tool('k_par'); await click_obj('side',0); await click_obj('vert',n0)
    await tool('k_par'); await click_obj('side',0); await click_obj('vert',4)
    await tool('move'); await drag(2,[230,200]); await drag(n0,[200,40]); g=await G(); P=g['pts']; A,B=P[1],P[2]; u=sub(B,A)
    pcs=[(int(k),v) for k,v in g['def'].items() if v['t']=='pc']; prs=[(int(k),v) for k,v in g['def'].items() if v['t']=='par']
    k,v=pcs[0]; Q=P[k]; Pp=P[v['p']]; cr=lambda a,b:a[0]*b[1]-a[1]*b[0]
    check('parallel chord stays parallel and on circle', abs(cr(u,sub(Q,Pp)))<1e-6*d(A,B)*d(Q,Pp) and abs(d(Q,g['circles'][0]['c'])-g['circles'][0]['r'])<1e-6)
    k,v=prs[0]; check('parallel line stays parallel', abs(cr(u,sub(P[k],P[v['p']])))<1e-6*d(A,B)*d(P[k],P[v['p']]))
    # 9) تمييز قوس وتسميته
    await tool('k_arc'); await click_obj('vert',1); await click_obj('vert',2); g=await G()
    check('arc highlighted', len(g['circles'][0].get('arcs',[]))==1)
    await E("()=>{ S.p.circles[0].arcs[0].lab='80°'; S.p.circles[0].arcs[0].show=true; draw(); }")
    check('arc label drawn', await E("PR.some(q=>q.t==='txt'&&(q.s.includes('80')||q.s.includes('٨٠')))"))
    check('no page errors', not errs, errs)
    await b.close()
  print('\n%d failures'%len(FAIL)); sys.exit(1 if FAIL else 0)
asyncio.run(main())
