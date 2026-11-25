# الذاكرة: 400 دورة (قالب + سحب + رسم + تراجع) ثم مقارنة حجم الذاكرة بعد جمع المهملات
import asyncio, json
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--js-flags=--expose-gc']); pg=await b.new_page(viewport={'width':360,'height':1000})
    await pg.route('**/office.js',lambda r:r.fulfill(body='',content_type='text/javascript'))
    await pg.goto('file:///home/claude/uula-geometry/app.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_function('typeof draw==="function"')
    r=await pg.evaluate("""async()=>{ const heap=()=>{ gc(); gc(); return performance.memory.usedJSHeapSize/1048576; }; const ks=TPL_LIST.map(x=>x[0]);
      const cyc=n=>{ for(let i=0;i<n;i++){ applyTpl(ks[i%ks.length]); for(let j=0;j<10;j++){ const f=S.p.pts.findIndex((_,k)=>!isDerived(S.p,k)); setVertex(f,add(S.p.pts[f],[1,1])); draw(); } } HIST.length=0; };
      cyc(50); const h0=heap(); cyc(400); const h1=heap(); return {heapMB_after_warmup:+h0.toFixed(2), heapMB_after_400_more:+h1.toFixed(2), listeners_note:'draw() replaces innerHTML; no listeners are added per draw'}; }""")
    print(json.dumps(r)); await b.close()
asyncio.run(main())
