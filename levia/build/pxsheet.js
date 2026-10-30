// pixel-exact 16/32/64 test: render at exact pixel width on a square canvas, then nearest-neighbour zoom
const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const C={off:'#F2EFE9',green:'#3A4C40',terra:'#C4694A'};
const b64=b=>'data:image/png;base64,'+Buffer.from(b).toString('base64');
async function squarePng(file,px,color){
  // place the mark inside a square px canvas without resampling: render at native, then composite
  const svg=fs.readFileSync(file,'utf8');
  const r=new Resvg(svg,{fitTo:{mode:'width',value:px},background:'rgba(0,0,0,0)'});
  const m=r.render();
  const canvas=await sharp({create:{width:px,height:px,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).png().toBuffer();
  return await sharp(canvas).composite([{input:m.asPng(),left:0,top:Math.floor((px-m.height)/2)}]).png().toBuffer();
}
(async()=>{
  const rows=[['logo/levia-symbol.svg','Master 28/256'],['logo/levia-symbol-small.svg','Small cut 44/256']];
  const zoom=8;
  const cellW=560, cellH=200;
  let comps=[]; let y=0;
  const head=await sharp({create:{width:1700,height:70,channels:4,background:C.off}}).png().toBuffer();
  comps.push({input:Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="70"><rect width="100%" height="100%" fill="${C.off}"/><text x="30" y="30" font-family="sans-serif" font-size="15" fill="${C.green}">TRUE PIXELS + 8x ZOOM  |  16 px, 32 px, 64 px  (rendered at exact size, then enlarged with nearest neighbour)</text></svg>`),left:0,top:0});
  y=70;
  for(const [f,label] of rows){
    let x=30;
    comps.push({input:Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="28"><text x="30" y="20" font-family="sans-serif" font-size="13" fill="#666">${label}</text></svg>`),left:0,top:y});
    y+=28;
    for(const px of [16,32,64]){
      const sq=await squarePng(f,px);
      const z=await sharp(sq).resize(px*zoom,px*zoom,{kernel:'nearest'}).png().toBuffer();
      comps.push({input:z,left:x,top:y});
      comps.push({input:sq,left:x+px*zoom+14,top:y});
      x+=px*zoom+14+px+60;
    }
    y+=64*zoom+44;
  }
  const out=await sharp({create:{width:1700,height:y,channels:4,background:C.off}}).composite(comps).png().toBuffer();
  fs.writeFileSync('out/pixel-test.png',out);
  console.log('ok',y);
})();
