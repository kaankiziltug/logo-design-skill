const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const {textPath}=require('/home/user/logo-design-skill/levia/build/type2path.js');
const C={off:'#F2EFE9',green:'#3A4C40',sage:'#8BA892',terra:'#C4694A',acc:'#9E4A2C'};
const FRA='/home/user/fonts/static/F-o24-w500-s50.ttf';

function squareVB(spec){ const bb=g.inkBox(spec); const s=Math.max(bb.w,bb.h)*1.06; return {vb:`${bb.x-(s-bb.w)/2} ${bb.y-(s-bb.h)/2} ${s} ${s}`, s}; }
function svgOf(spec,color,square=true){
  const bb=g.inkBox(spec);
  const vb = square? squareVB(spec).vb : `${bb.x} ${bb.y} ${bb.w} ${bb.h}`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}">${g.d(spec,color)}</svg>`;
}
async function png(spec,color,px,square=true){
  const r=new Resvg(svgOf(spec,color,square),{fitTo:{mode:'width',value:px},background:'rgba(0,0,0,0)'});
  return r.render().asPng();
}
const b64=b=>'data:image/png;base64,'+Buffer.from(b).toString('base64');

(async()=>{
  const W=1680,H=1180;
  let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${C.off}"/>`;
  // --- header
  s+=`<text x="56" y="58" font-family="Hind Vadodara" font-size="15" fill="${C.green}" opacity=".7">LEVIA · DIRECTION A — THE FOLD · SYMBOL TESTS</text>`;
  // --- master symbol big
  s+=`<image x="56" y="80" width="300" height="220" href="${b64(await png(g.MASTER,C.green,600,false))}"/>`;
  s+=`<text x="56" y="330" font-family="Hind Vadodara" font-size="13" fill="${C.green}" opacity=".6">Symbol, master (three bars · 1 weight · 3.87:1 L×H)</text>`;

  // --- size ladder at 1x
  let x=400,y=110;
  s+=`<text x="400" y="90" font-family="Hind Vadodara" font-size="13" fill="${C.green}" opacity=".6">True size (pixel-bound)</text>`;
  [[64,0],[32,0],[16,0]].forEach(async()=>{});
  let sizes=[64,32,16];
  let cx=400;
  for(const px of sizes){
    const buf=await png(g.MASTER,C.green,px);
    s+=`<image x="${cx}" y="${y}" width="${px}" height="${px}" href="${b64(buf)}"/>`;
    s+=`<text x="${cx}" y="${y+px+22}" font-family="Hind Vadodara" font-size="12" fill="${C.green}" opacity=".55">${px} px</text>`;
    cx+=px+56;
  }
  // zoom row
  s+=`<text x="400" y="270" font-family="Hind Vadodara" font-size="13" fill="${C.green}" opacity=".6">8× pixel zoom</text>`;
  cx=400;
  for(const px of sizes){
    const buf=await png(g.MASTER,C.green,px);
    const z=await sharp(buf).resize(px*8,px*8,{kernel:'nearest'}).png().toBuffer();
    s+=`<image x="${cx}" y="${286}" width="${px*8}" height="${px*8}" href="${b64(z)}" image-rendering="pixelated"/>`;
    cx+=px*8+28;
  }
  // small cut row
  s+=`<text x="400" y="800" font-family="Hind Vadodara" font-size="13" fill="${C.green}" opacity=".6">Small cut (40/256 weight, squarer, arms closer) — true size 32/16, 8× zoom</text>`;
  cx=400;
  for(const px of [32,16]){
    const buf=await png(g.SMALL,C.green,px);
    const z=await sharp(buf).resize(px*8,px*8,{kernel:'nearest'}).png().toBuffer();
    s+=`<image x="${cx}" y="${830}" width="${px*8}" height="${px*8}" href="${b64(z)}" image-rendering="pixelated"/>`;
    s+=`<image x="${cx+px*8+14}" y="${830}" width="${px}" height="${px}" href="${b64(buf)}"/>`;
    cx+=px*8+90;
  }
  // --- one-colour / reversed / accent panels
  s+=`<text x="56" y="380" font-family="Hind Vadodara" font-size="13" fill="${C.green}" opacity=".6">One colour · reversed · supporting colour</text>`;
  const panels=[
    {label:'Black on white (print, engraving)', bg:'#FFFFFF', fg:'#000000', x:56, y:400},
    {label:'Dark green on off-white (primary)', bg:C.off, fg:C.green, x:56, y:530},
    {label:'Off-white on dark green (reversed)', bg:C.green, fg:C.off, x:56, y:660},
  ];
  for(const p of panels){
    s+=`<rect x="${p.x}" y="${p.y}" width="300" height="104" fill="${p.bg}" stroke="${p.bg==='#FFFFFF'?'#DDD':'none'}"/>`;
    s+=`<image x="${p.x+26}" y="${p.y+24}" width="140" height="62" href="${b64(await png(g.MASTER,p.fg,480,false))}"/>`;
    s+=`<text x="${p.x}" y="${p.y-8}" font-family="Hind Vadodara" font-size="12" fill="${C.green}" opacity=".6">${p.label}</text>`;
  }
  // --- reverse/rotate/reading checks
  s+=`<text x="400" y="1000" ... `; // placeholder removed below
  s=s.replace(/<text x="400" y="1000" \.\.\. `; \/\/ placeholder removed below/,'');
  fs.writeFileSync('/home/user/logo-design-skill/levia/src/sheetfinal.svg',s+'</svg>');
  console.log('ok');
})();
