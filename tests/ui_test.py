# الواجهة: التكبير، التحديد المتعدد، المفضلة والأخيرة، الالتصاق
import asyncio, json, sys
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':360,'height':1000},device_scale_factor=2)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/office.js',lambda r:r.fulfill(body='',content_type='text/javascript'))
    await pg.goto('file:///home/claude/uula-geometry/app.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_function('typeof draw==="function"')
    E=pg.evaluate; fails=[]
    def ck(n,c,i=''):
      print(('PASS ' if c else 'FAIL ')+n+('' if c else ' '+str(i)))
      if not c: fails.append(n)
    await E("applyTpl('cyclicQuad')")
    # التكبير بعجلة الفأرة مع Ctrl، ثم السحب لتحريك المعاينة، ثم الإرجاع
    box=await E("(()=>{ const r=$('fig').getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2]; })()")
    await pg.mouse.move(*box); await pg.keyboard.down('Control'); await pg.mouse.wheel(0,-200); await pg.keyboard.up('Control'); await pg.wait_for_timeout(100)
    k=await E("ZOOM.k"); ck('ctrl+wheel zooms the preview', k>1.5, k)
    pts0=await E("JSON.stringify(S.p.pts)")
    vb0=await E("$('fig').getAttribute('viewBox')")
    corner=await E("(()=>{ const r=$('fig').getBoundingClientRect(); for(let y=r.top+8;y<r.bottom-60;y+=6) for(let x=r.left+8;x<r.right-8;x+=6){ const el=document.elementFromPoint(x,y); if(el&&el.id==='fig') return [x,y]; } return null; })()")
    await pg.mouse.move(*corner); await pg.mouse.down(); await pg.mouse.move(corner[0]+40,corner[1]+20,steps=5); await pg.mouse.up()
    ck('drag pans when zoomed', (await E("$('fig').getAttribute('viewBox')"))!=vb0)
    ck('zoom/pan do not change the figure', (await E("JSON.stringify(S.p.pts)"))==pts0)
    await pg.keyboard.press('Control+0'); ck('ctrl+0 resets zoom', (await E("ZOOM.k"))==1)
    # التحديد المتعدد: Shift + نقر على نقطتين، ثم سحب إحداهما يحرك الاثنتين
    sc="(i=>{ const q=S.p.pts[i], m=$('fig').getScreenCTM(); return [q[0]*m.a+q[1]*m.c+m.e, q[0]*m.b+q[1]*m.d+m.f]; })"
    free=await E("S.p.pts.map((_,i)=>i).filter(i=>!isDerived(S.p,i)&&!S.p.onc[i])")
    a,bq=free[0],free[1] if len(free)>1 else None
    # نقطتان على الدائرة (أ، ب)
    ia,ib=1,2
    for i in (ia,ib):
      xy=await E(sc+"(%d)"%i); await pg.keyboard.down('Shift'); await pg.mouse.click(*xy); await pg.keyboard.up('Shift')
    ck('shift+click selects 2 points', (await E("MSEL.size"))==2)
    before=await E("[S.p.onc[%d][1],S.p.onc[%d][1]]"%(ia,ib))
    xy=await E(sc+"(%d)"%ia); await pg.mouse.move(*xy); await pg.mouse.down(); await pg.mouse.move(xy[0]+30,xy[1]+25,steps=6); await pg.mouse.up()
    after=await E("[S.p.onc[%d][1],S.p.onc[%d][1]]"%(ia,ib))
    ck('dragging one moves both (stay on circle)', before[0]!=after[0] and before[1]!=after[1], [before,after])
    n0=await E("S.p.pts.length")
    await pg.keyboard.press('Delete'); n1=await E("S.p.pts.length")
    ck('delete removes the selected points', n1==n0-2, [n0,n1])
    # المفضلة والأخيرة
    await E("applyTpl('twoTangents')"); await pg.click('#favBtn')
    ck('favorite saved', (await E("FAVS.length"))==1 and (await E("$('favBtn').getAttribute('aria-pressed')"))=='true')
    ck('recent list has templates', (await E("RECENT.slice(0,2).join(',')"))=='twoTangents,cyclicQuad')
    await E("applyTpl('diamChord')"); await pg.select_option('#tplSel','fav:0')
    ck('favorite re-opens', (await E("S.p.def&&Object.values(S.p.def).filter(d=>d.t==='tan').length"))==2)
    await pg.reload(); await pg.wait_for_function('typeof draw==="function"')
    ck('favorites persist after reload', (await E("$('tplSel').innerHTML.includes('★')")))
    # الالتصاق
    await E("(()=>{ SNAP=false; S.empty=false; S.tab='p'; S.p=mkFree([[160,125]],[]); S.p.circles=[{c:[160,125],r:80,cp:0}]; syncUI(); draw(); })()")
    ck('snap off: no circle snapping', (await E("nearCirc(S.p,[240,126])"))==-1)
    await E("SNAP=true"); ck('snap on: snaps', (await E("nearCirc(S.p,[240,126])"))==0)
    ck('no page errors', not errs, errs)
    await b.close(); print('%d failures'%len(fails)); sys.exit(1 if fails else 0)
asyncio.run(main())
