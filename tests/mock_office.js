window.__syncs=0; window.__lat=0;
window.__shapes=[];
const mkShape=(type,o)=>{ const s={type,left:o.left,top:o.top,width:o.width,height:o.height,rotation:0,id:String(__shapes.length+1),
  lineFormat:{visible:true},fill:{clear(){s.fillc=null},setSolidColor(c){s.fillc=c}},tags:{add(k,v){s.tag=v}},
  adj:type==='Arc'?[16200000,0]:type==='Pie'?[0,16200000]:type==='Triangle'?[50000]:[],
  load(){}, delete(){s.deleted=true}};
  s.adjustments={get(i){return {get value(){return s.adj[i]}}},set(i,v){s.adj[i]=v}};
  s.textFrame={textRange:{font:{},paragraphFormat:{}}}; __shapes.push(s); return s; };
window.Office={onReady(f){setTimeout(()=>f({host:'PowerPoint'}),10)},context:{requirements:{isSetSupported:()=>true}},CoercionType:{XmlSvg:'x'}};
window.PowerPoint={run:async f=>{ const shapes={addLine:(t,o)=>mkShape('Line',o),addGeometricShape:(t,o)=>mkShape(t,o),addTextBox:(txt,o)=>{const s=mkShape('Text',o);s.text=txt;return s},
   addGroup:(ids)=>{const g=mkShape('Group',{});g.ids=ids;return g},getItemOrNullObject:()=>({isNullObject:true}),load(){},get items(){return __shapes.filter(s=>!s.deleted)}};
  const ctx={presentation:{getSelectedSlides:()=>({getItemAt:()=>({shapes})}),getSelectedShapes:()=>({items:[],load(){}}),pageSetup:{slideWidth:720,slideHeight:540,load(){}}},sync:async()=>{ __syncs++; if(window.__lat) await new Promise(r=>setTimeout(r,__lat)); }}; await f(ctx); }};
