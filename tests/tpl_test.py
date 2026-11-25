# كل قالب: يُبنى، لا أخطاء، لا قيم NaN، العلاقات صحيحة، ثم سحب كل نقطة حرة وإعادة التحقق؛ وتُحفظ صورة لكل قالب
import asyncio, json, sys, math
from playwright.async_api import async_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/tpl'
CHECK=r'''(()=>{ const G=S.p, P=G.pts, C=G.circles, bad=[]; const d=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
  P.forEach((q,i)=>{ if(!isFinite(q[0])||!isFinite(q[1])) bad.push('nan p'+i); });
  Object.entries(G.onc||{}).forEach(([k,[ci,a]])=>{ const o=C[ci]; if(Math.abs(d(P[k],o.c)-o.r)>1e-6) bad.push('onc '+k); });
  Object.entries(G.def||{}).forEach(([k,df])=>{ if(df.bad) return; const q=P[k], o=C[df.ci];
    if(df.t==='tan'){ const r=[q[0]-o.c[0],q[1]-o.c[1]], t=[P[df.p][0]-q[0],P[df.p][1]-q[1]]; if(Math.abs(r[0]*t[0]+r[1]*t[1])>1e-6*Math.hypot(...r)*Math.hypot(...t)||Math.abs(d(q,o.c)-o.r)>1e-6) bad.push('tan '+k); }
    if(df.t==='foot'){ const A=P[df.a],B=P[df.b],Q=P[df.p]; if(Math.abs((Q[0]-q[0])*(B[0]-A[0])+(Q[1]-q[1])*(B[1]-A[1]))>1e-6*d(A,B)*Math.max(1,d(Q,q))) bad.push('foot '+k); }
    if(df.t==='xlc'||df.t==='eqc'||df.t==='rotc'){ if(Math.abs(d(q,o.c)-o.r)>1e-6) bad.push(df.t+' '+k); }
    if(df.t==='eqc'&&Math.abs(d(q,P[df.p])-d(P[df.a],P[df.b]))>1e-6) bad.push('eqc len '+k);
    if(df.t==='xtt'){ const u=[P[df.a][0]-o.c[0],P[df.a][1]-o.c[1]], t=[q[0]-P[df.a][0],q[1]-P[df.a][1]]; if(Math.abs(u[0]*t[0]+u[1]*t[1])>1e-6*Math.hypot(...u)*Math.max(1,Math.hypot(...t))) bad.push('xtt '+k); } });
  C.forEach((o,ci)=>{ if(o.def&&!o.bad){ const ps=['a','b','c'].filter(x=>o.def[x]!=null).map(x=>P[o.def[x]]); if(o.def.t!=='in'&&ps.some(q=>Math.abs(d(q,o.c)-o.r)>1e-6)) bad.push('c3 '+ci); } });
  return bad; })()'''
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':360,'height':1000},device_scale_factor=2)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/office.js',lambda r:r.fulfill(body='',content_type='text/javascript'))
    await pg.goto('file:///home/claude/uula-geometry/app.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_function('typeof draw==="function"')
    keys=await pg.evaluate('TPL_LIST.map(x=>x[0])'); fails=0
    for lang in ['ar','en']:
      await pg.evaluate("setScript&&setScript('%s')"%lang)
      for k in keys:
        await pg.select_option('#tplSel',k); bad=await pg.evaluate(CHECK)
        free=await pg.evaluate("S.p.pts.map((_,i)=>i).filter(i=>!isDerived(S.p,i))")
        for i in free:
          await pg.evaluate("(()=>{ const G=S.p; setVertex(%d,add(G.pts[%d],[17,-11])); draw(); })()"%(i,i)); bad+=await pg.evaluate(CHECK)
        await pg.evaluate("applyTpl('%s')"%k)
        if lang=='ar': el=await pg.query_selector('#fig'); await el.screenshot(path='%s_%s.png'%(OUT,k))
        print(('OK  ' if not bad else 'BAD ')+lang+' '+k, bad[:4]); fails+=bool(bad)
    print('errors:',errs or 'none'); await b.close(); sys.exit(1 if fails or errs else 0)
asyncio.run(main())
