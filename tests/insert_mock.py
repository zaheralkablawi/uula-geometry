# الإدراج مع واجهة أوفيس وهمية: عدد رحلات sync وعدد الأشكال وزمن JavaScript (بدون زمن باوربوينت الحقيقي)
import asyncio, json, sys
from playwright.async_api import async_playwright
APP=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/uula-geometry/app.html'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':360,'height':1000})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/office.js',lambda r:r.fulfill(path='/home/claude/uula-geometry/tests/mock_office.js',content_type='text/javascript'))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_function('typeof draw==="function"'); await pg.wait_for_timeout(300)
    cases={'triangle':"S.empty=false;S.tab='p';S.p=defaults().p;",'cube':"S.empty=false;S.tab='s';S.s.kind='cube';",'circle_tab':"S.empty=false;S.tab='c';"}
    has=await pg.evaluate("typeof applyTpl==='function'")
    if has: cases.update({'tpl_genProblem':"applyTpl('genProblem');",'tpl_twoTangents':"applyTpl('twoTangents');",'tpl_cyclicQuad':"applyTpl('cyclicQuad');"})
    out={}
    for k,js in cases.items():
      runs=[]
      for i in range(3):
        await pg.evaluate("()=>{ %s syncUI(); draw(); __shapes.length=0; __syncs=0; }"%js)
        t=await pg.evaluate("""async()=>{ const a=performance.now(); $('insert').click(); for(let i=0;i<200&&!/تم|Inserted|خطأ|rror/.test($('msg').textContent);i++) await new Promise(r=>setTimeout(r,5)); const ms=performance.now()-a; const m=$('msg').textContent; $('msg').textContent=''; return {ms:+ms.toFixed(1),syncs:__syncs,shapes:__shapes.length,msg:m}; }""")
        runs.append(t)
      out[k]={'first':runs[0],'next':runs[2]}
    print(json.dumps(out,ensure_ascii=False,indent=1)); print('errors',errs or 'none'); await b.close()
asyncio.run(main())
