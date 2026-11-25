# المجسمات: الحواف المخفية محسوبة من اتجاه الرؤية (تُختبر على زوايا دوران كثيرة)، وصور لكل مجسم
import asyncio, json, sys, math, random
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':360,'height':1000},device_scale_factor=2)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/office.js',lambda r:r.fulfill(body='',content_type='text/javascript'))
    await pg.goto('file:///home/claude/uula-geometry/app.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_function('typeof draw==="function"')
    fails=0; random.seed(3)
    # مكعب: عدد الأوجه الظاهرة (1 أو 2 أو 3) يحدد عدد الحواف المخفية 8 أو 5 أو 3
    for i in range(300):
      yaw=random.uniform(-180,180); pitch=random.uniform(-85,85); persp=random.random()<.5
      r=await pg.evaluate("""([y,p,ps])=>{ S.empty=false; S.tab='s'; S.s.kind='cube'; S.s.hidden='dash'; S.s.view={cube:{yaw:y,pitch:p,persp:ps}}; build(); const seg=PR.filter(q=>q.t==='seg'); return [seg.filter(q=>q.dash).length, seg.length]; }""",[yaw,pitch,persp])
      # حساب مستقل: الأوجه الظاهرة بالإسقاط المتوازي
      cy,sy,cp,sp=math.cos(math.radians(yaw)),math.sin(math.radians(yaw)),math.cos(math.radians(pitch)),math.sin(math.radians(pitch))
      rot=lambda q:(q[0]*cy+q[2]*sy,(q[1])*cp-(-q[0]*sy+q[2]*cy)*sp,q[1]*sp+(-q[0]*sy+q[2]*cy)*cp)
      if not persp:
        vis=sum(1 for n in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)] if rot(n)[2]>1e-9)
        exp={1:8,2:5,3:3}[vis]
      else: exp=None
      ok=r[1]==12 and (r[0]==exp if exp is not None else r[0] in (3,5,8))
      if not ok: fails+=1; print('BAD cube',yaw,pitch,persp,r,exp)
    print('cube rotations: %d bad of 300'%fails)
    # كل المجسمات: افتراضي، ومدوَّر، ومنظوري؛ بلا NaN، وصورة
    kinds=await pg.evaluate("GAL_S.map(x=>x[0])")
    for k in kinds:
      for mode in ['def','rot','persp']:
        r=await pg.evaluate("""([k,m])=>{ S.empty=false; S.tab='s'; S.s.kind=k; S.s.view={}; if(m!=='def'&&POLY3.includes(k)) S.s.view[k]={yaw:-50,pitch:28,persp:m==='persp'}; if(m==='rot'&&ROUND3.includes(k)) S.s.size[k].e=.18; syncUI(); draw();
          const bad=PR.some(q=>/\[null|,null\]|NaN/.test(JSON.stringify(q))); return [bad, PR.length]; }""",[k,mode])
        if r[0]: fails+=1; print('BAD',k,mode,r)
        el=await pg.query_selector('#fig'); await el.screenshot(path='/tmp/sol_%s_%s.png'%(k,mode))
    print('errors:',errs or 'none','fails',fails); await b.close(); sys.exit(1 if fails or errs else 0)
asyncio.run(main())
