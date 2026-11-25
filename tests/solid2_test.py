# المقاطع وتلوين الأوجه وإمالة المجسمات الدورانية
import asyncio, json, sys
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':360,'height':1000},device_scale_factor=2)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/office.js',lambda r:r.fulfill(path='/home/claude/uula-geometry/tests/mock_office.js',content_type='text/javascript'))
    await pg.goto('file:///home/claude/uula-geometry/app.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_function('typeof draw==="function"'); await pg.wait_for_timeout(300)
    E=pg.evaluate; fails=[]
    def ck(n,c,i=''):
      print(('PASS ' if c else 'FAIL ')+n+('' if c else ' '+str(i)))
      if not c: fails.append(n)
    kinds=await E("GAL_S.map(x=>x[0])")
    for k in kinds:
      r=await E("""k=>{ S.empty=false; S.tab='s'; S.s.kind=k; S.s.view={}; S.s.sec={}; S.s.sec[k]=.5; syncUI(); draw(); const polys=PR.filter(q=>q.t==='poly'&&q.fill==='#cfe0fa'||q.t==='ell'&&q.fill==='#cfe0fa'); return [polys.length, !!SOL.secH, PR.some(q=>/NaN|\\[null/.test(JSON.stringify(q)))]; }""",k)
      ck('section '+k, r[0]==1 and r[1] and not r[2], r)
      el=await pg.query_selector('#fig'); await el.screenshot(path='/tmp/sec_%s.png'%k)
    # مقطع المكعب عند منتصف الارتفاع: مربع (4 رؤوس) بأضلاع متساوية في الفراغ
    r=await E("""(()=>{ S.s.kind='cube'; S.s.sec={cube:.5}; draw(); return PR.find(q=>q.t==='poly'&&q.fill==='#cfe0fa').pts.length; })()""")
    ck('cube mid-section has 4 vertices', r==4, r)
    r=await E("""(()=>{ S.s.kind='npyr'; S.s.size.npyr.n=6; S.s.sec={npyr:.3}; draw(); return PR.find(q=>q.t==='poly'&&q.fill==='#cfe0fa').pts.length; })()""")
    ck('hexagonal pyramid section has 6 vertices', r==6, r)
    # تلوين وجه بالنقر
    await E("(()=>{ S.s.kind='cube'; S.s.sec={}; S.s.view={}; syncUI(); draw(); })()")
    fi=await E("SOL.faces[0].fi")
    xy=await E("""(()=>{ const f=SOL.faces[0], c=cen(f.pts), m=$('fig').getScreenCTM(); return [c[0]*m.a+c[1]*m.c+m.e, c[0]*m.b+c[1]*m.d+m.f]; })()""")
    await pg.mouse.click(*xy); await pg.wait_for_timeout(50)
    ck('face click colors it', await E("(S.s.ff&&S.s.ff.cube&&S.s.ff.cube[%d])==='#cfe0fa'"%fi))
    await pg.mouse.click(*xy); await pg.wait_for_timeout(50)
    ck('second click changes color', await E("S.s.ff.cube[%d]==='#fde2fd'"%fi), await E('JSON.stringify([S.s.ff, SOL.faces.map(f=>f.fi)])'))
    # السحب على الوجه يدير المكعب ولا يلونه
    await pg.mouse.move(*xy); await pg.mouse.down(); await pg.mouse.move(xy[0]+60,xy[1]-20,steps=6); await pg.mouse.up()
    ck('drag on face orbits', await E("!!(S.s.view.cube&&Math.abs(S.s.view.cube.yaw+32)>5)"))
    # إمالة الأسطوانة بالسحب الأفقي
    await E("(()=>{ S.s.kind='cyl'; S.s.view={}; if(S.s.rot) delete S.s.rot.cyl; syncUI(); draw(); })()")
    bx=await E("(()=>{ const r=$('fig').getBoundingClientRect(); return [r.left+15,r.top+15]; })()")
    await pg.mouse.move(*bx); await pg.mouse.down(); await pg.mouse.move(bx[0]+50,bx[1],steps=5); await pg.mouse.up()
    ck('horizontal drag tilts the cylinder', await E("Math.abs((S.s.rot||{}).cyl||0)>=10"), await E("JSON.stringify(S.s.rot)"))
    # الإدراج مع مقطع وألوان (واجهة وهمية)
    await E("(()=>{ S.s.kind='cube'; S.s.sec={cube:.4}; syncUI(); draw(); })()")
    ins=await E("""async()=>{ __shapes.length=0; $('insert').click(); for(let i=0;i<200&&!/تم|Inserted|خطأ|rror/.test($('msg').textContent);i++) await new Promise(r=>setTimeout(r,5)); const m=$('msg').textContent; $('msg').textContent=''; return m; }""")
    ck('insert with section and colors', 'تم' in ins, ins)
    ck('no page errors', not errs, errs)
    await b.close(); print('%d failures'%len(fails)); sys.exit(1 if fails else 0)
asyncio.run(main())
