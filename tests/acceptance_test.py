# اختبارات القبول من الملف المرجعي: لكل شكل مركب
# 1 الإنشاء  2 تحريك النقاط  3 بقاء العلاقات  4 تغيير القياسات والتسميات  5 إضافة العلامات
# 6 الإدراج (واجهة أوفيس وهمية)  8 إعادة الفتح من بيانات الوسم  10 النسخ (نسخة البيانات تفتح وتُعدّل مستقلة)
# (7 و 9 — التعديل داخل باوربوينت والحفظ وإعادة فتح الملف — تحتاج باوربوينت الحقيقي؛ خطواتها في التقرير)
import asyncio, json, sys
from playwright.async_api import async_playwright
sys.path.insert(0,'/home/claude/uula-geometry/tests'); from tpl_test import CHECK
CASES=[('genProblem','ص96 المسألة العامة'),('tanSecChord','ص93 س2 مماس وقاطع ووتر'),('inQuad','ص85 س7 دائرة داخل رباعي'),('inTriPts','ص79 دائرة داخل مثلث ونقاط التماس'),('cyclicQuad','ص72 رباعي دائري وقطراه'),('eqChords','ص60 وتران متطابقان وبعداهما عن المركز')]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':360,'height':1000})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/office.js',lambda r:r.fulfill(path='/home/claude/uula-geometry/tests/mock_office.js',content_type='text/javascript'))
    await pg.goto('file:///home/claude/uula-geometry/app.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_function('typeof draw==="function"'); await pg.wait_for_timeout(300)
    E=pg.evaluate; total=0; okc=0
    for key,title in CASES:
      res={}
      await E("applyTpl('%s')"%key); res['1 create']=(await E(CHECK))==[]
      if key=='eqChords':   # بالأدوات: عمودان من المركز على الوترين (كما في ص60)
        await E("""(()=>{ const G=S.p; FT='k_perp'; const O=0; [[1,2],[3,4]].forEach(([a,b])=>{ FT='k_perp'; PICK=[]; consTool({dataset:{h:'vert',i:String(O)}},{}); consTool({dataset:{h:'side',i:String(sideIndexOf(G,a,b))}},{}); }); FT='move'; draw(); })()""")
        res['1 create']=res['1 create'] and (await E("Object.values(S.p.def).filter(d=>d.t==='foot').length"))==2
      bad=[]
      for i in await E("S.p.pts.map((_,i)=>i).filter(i=>!isDerived(S.p,i))"):
        for dv in ([23,-14],[-31,9]):
          await E("(()=>{ setVertex(%d,add(S.p.pts[%d],%s)); draw(); })()"%(i,i,json.dumps(dv))); bad+=await E(CHECK)
      res['2-3 drag keeps relations']=not bad
      await E("""(()=>{ const G=S.p; G.sides[0].len='2x+3'; G.sides[0].show=true; G.verts[1].name=isEn()?'P':'ف'; const k=Object.keys(G.angs)[0]||angKey(...(()=>{ for(let i=0;i<G.pts.length;i++){ const a=freeAngles(G,i); if(a.length) return [i,a[0][0],a[0][1]]; } })()); G.angs[k]=Object.assign(G.angs[k]||{},{showAng:true,ang:'x°'}); draw(); })()""")
      res['4 labels/measures']=await E("PR.some(q=>q.t==='txt'&&/2|٢/.test(q.s))&&PR.some(q=>q.t==='txt'&&/°/.test(q.s))")
      await E("(()=>{ S.p.sides[0].ticks=2; S.p.sides[0].par=1; draw(); })()"); res['5 marks']=(await E("PR.filter(q=>q.t==='seg').length"))>(await E("S.p.sides.length"))
      ins=await E("""async()=>{ __shapes.length=0; __syncs=0; $('insert').click(); for(let i=0;i<200&&!/تم|Inserted|خطأ|rror/.test($('msg').textContent);i++) await new Promise(r=>setTimeout(r,5)); const m=$('msg').textContent; $('msg').textContent=''; const g=__shapes.find(s=>s.type==='Group'); return {m, n:__shapes.length, syncs:__syncs, tag:g&&g.tag}; }""")
      res['6 insert (mock)']=bool(ins['tag']) and ins['syncs']<=3
      before=await E("JSON.stringify(S.p.pts)")
      re=await E("""t=>{ const data=JSON.parse(t); const d=defaults(); S=Object.assign(d,data.s); S.look=Object.assign(d.look,data.s.look||{}); fixS(); solve(S.p); draw(); return [data.v, JSON.stringify(S.p.pts)]; }""",ins['tag'])
      res['8 reopen from tag']=re[0]==2 and json.loads(re[1])==json.loads(before) and (await E(CHECK))==[]
      dup=await E("""t=>{ const a=JSON.parse(t), b=JSON.parse(t); const d=defaults(); S=Object.assign(d,b.s); fixS(); solve(S.p); setVertex(S.p.pts.findIndex((_,i)=>!isDerived(S.p,i)),[10,10]); return JSON.stringify(a.s.p.pts)!==JSON.stringify(S.p.pts); }""",ins['tag'])
      res['10 duplicate independent']=dup and (await E(CHECK))==[]
      allok=all(res.values()); total+=1; okc+=allok
      print(('PASS ' if allok else 'FAIL ')+title+'  ['+key+']  shapes=%d syncs=%d'%(ins['n'],ins['syncs']))
      for k,v in res.items():
        if not v: print('   ✗',k)
    print('%d/%d acceptance cases pass; page errors: %s'%(okc,total,errs or 'none')); await b.close(); sys.exit(0 if okc==total and not errs else 1)
asyncio.run(main())
