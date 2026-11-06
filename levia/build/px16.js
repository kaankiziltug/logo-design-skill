const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const C={off:'#F2EFE9',green:'#3A4C40'};
const b64=b=>'data:image/png;base64,'+Buffer.from(b).toString('base64');
const spec=(w,deck,riser,perch)=>({w,parts:[
  {x1:deck[0],y1:deck[1],x2:deck[2],y2:deck[1]},
  {x1:riser,y1:deck[1],x2:riser,y2:perch},
  {x1:riser,y1:perch,x2:deck[3],y2:perch},
]});
const CANDS={
  'master w28': {spec:g.MASTER},
  'w44': {spec:spec(44,62,74,210,158,116)},
  'w52 short': {spec:spec(52,70,76,196,152,124)},
  'w60 stub': {spec:spec(60,82,80,190,152,140)},
};
function svgOf(s,color,pad=0){
  const bb=g.inkBox(s); const m=Math.max(bb.w,bb.h);
  const x=bb.x-(m-bb.w)/2, y=bb.y-(m-bb.h)/2;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${x} ${y} ${m} ${m}">${g.d(s,color)}</svg>`;
}
async function sq(svg,px){
  const r=new Resvg(svg,{fitTo:{mode:'width',value:px},background:'rgba(0,0,0,0)'});
  const m=r.render();
  const canvas=await sharp({create:{width:px,height:px,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).png().toBuffer();
  return await sharp(canvas).composite([{input:m.asPng(),left:0,top:0}]).png().toBuffer();
}
(async()=>{
  const comps=[]; let y=64;
  comps.push({input:Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="64"><rect width="100%" height="100%" fill="${C.off}"/><text x="24" y="30" font-family="sans-serif" font-size="14" fill="${C.green}">16 px ONLY — 12x zoom (left) and true 16 px (right). Which cut still shows a step?</text></svg>`),left:0,top:0});
  for(const [name,{spec}] of Object.entries(CANDS)){
    const p=await sq(svgOf(spec,C.green),16);
    const z=await sharp(p).resize(16*12,16*12,{kernel:'nearest'}).png().toBuffer();
    comps.push({input:z,left:24,top:y});
    comps.push({input:p,left:24+16*12+30,top:y+88});
    comps.push({input:Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="300" height="26"><text x="24" y="18" font-family="sans-serif" font-size="13" fill="#555">${name}</text></svg>`),left:0,top:y+16*12+6});
    y+=16*12+50;
  }
  const out=await sharp({create:{width:1200,height:y+80,channels:4,background:C.off}}).composite(comps).png().toBuffer();
  fs.writeFileSync('out/px16.png',out);
  console.log('ok',y);
})();
