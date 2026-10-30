const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const S=(w,deckX1,deckX2,y1,riserX,perchY,perchX2)=>({w,parts:[
  {x1:deckX1,y1,x2:deckX2,y2:y1},
  {x1:riserX,y1,x2:riserX,y2:perchY},
  {x1:riserX,y1:perchY,x2:perchX2,y2:perchY}]});
const cands={
  A:g.MASTER,
  B:S(44,62,210,74,158,186,116),
  C:S(52,70,196,76,152,178,124),
  D:S(60,82,190,80,152,168,140),
};
function svgOf(s,c){const bb=g.inkBox(s);const m=Math.max(bb.w,bb.h);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${bb.x-(m-bb.w)/2} ${bb.y-(m-bb.h)/2} ${m} ${m}" width="256" height="256">${g.d(s,c)}</svg>`;}
for(const [k,s] of Object.entries(cands)){
  console.log(k, JSON.stringify(g.inkBox(s)));
  const r=new Resvg(svgOf(s,'#3A4C40'),{fitTo:{mode:'width',value:16},background:'rgba(0,0,0,0)'});
  const p=r.render();
  fs.writeFileSync('out/c16-'+k+'.png',p.asPng());
}
