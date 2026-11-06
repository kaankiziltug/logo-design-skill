const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const C={off:'#F2EFE9',green:'#3A4C40'};
function svg(spec,color,pad=0,aspect='square'){
  const bb=g.inkBox(spec);
  let vb, W, H;
  if(aspect==='square'){ const s=Math.max(bb.w,bb.h); vb=`${bb.x-(s-bb.w)/2} ${bb.y-(s-bb.h)/2} ${s} ${s}`; }
  else { vb=`${bb.x} ${bb.y} ${bb.w} ${bb.h}`; }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}">${g.d(spec,color)}</svg>`;
}
(async()=>{
  const out=[];
  for(const [name,spec] of [['master',g.MASTER],['small',g.SMALL]]){
    for(const px of [16,24,32,48,64]){
      const r=new Resvg(svg(spec,C.green),{fitTo:{mode:'width',value:px}});
      const buf=await sharp(r.render().asPng()).toBuffer();
      out.push({name,px,buf});
      fs.writeFileSync(`/home/user/logo-design-skill/levia/out/${name}-${px}.png`,buf);
    }
  }
  // montage: each variant, 6x zoom next to true size
  const tiles=[], cellW=200, cellH=170, bg=C.off;
  let y=10;
  const comps=[];
  comps.push({input:Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${cellW*6}" height="30"><rect width="100%" height="100%" fill="${bg}"/><text x="8" y="20" font-family="HindVadodara" font-size="14" fill="#555">true px (top) vs 6x pixel zoom (bottom)</text></svg>`),left:0,top:0});
  y=44;
  for(const name of ['master','small']){
    let x=10;
    for(const px of [16,24,32,48,64]){
      const t=out.find(o=>o.name===name&&o.px===px);
      const z=await sharp(t.buf).resize(px*6,px*6,{kernel:'nearest'}).toBuffer();
      comps.push({input:t.buf,left:x,top:y+40-px/2});
      comps.push({input:z,left:x,top:y+60});
      x+=cellW;
    }
    y+=cellH+110;
  }
  const H=y+10;
  const canvas=await sharp({create:{width:cellW*5+20,height:H,channels:4,background:bg}}).composite(comps).png().toBuffer();
  fs.writeFileSync('/home/user/logo-design-skill/levia/out/size-test.png',canvas);
  console.log('ok');
})();
