const fs=require('fs'), path=require('path');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const {word,wordData}=require('/home/user/logo-design-skill/levia/build/word.js');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const C={off:'#F2EFE9',green:'#3A4C40',sage:'#8BA892',terra:'#C4694A',acc:'#9E4A2C'};
const FRA='/home/user/fonts/static/F-o24-w500-s50.ttf';
const ROOT='/home/user/logo-design-skill/levia';
const TITLE={sym:'Levia symbol',wm:'Levia wordmark',lock:'Levia logo'};
const doc=(inner,vb,w,h,title)=>`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${w}" height="${h}" role="img" aria-label="${title}">
  <title>${title}</title>
  ${inner}
</svg>
`;
// --- symbol: tight ink canvas ---
function symbol(spec,color,{square=false,pad=6}={}){
  const bb=g.inkBox(spec);
  let x=bb.x-pad,y=bb.y-pad,w=bb.w+2*pad,h=bb.h+2*pad;
  if(square){const s=Math.max(w,h);x-= (s-w)/2;y-=(s-h)/2;w=h=s;}
  return doc(g.d(spec,color),`${g.R(x)} ${g.R(y)} ${g.R(w)} ${g.R(h)}`,Math.round(w*4),Math.round(h*4),TITLE.sym);
}
// --- wordmark ---
function wordmark(color){
  const t=wordData(FRA,'Levia',100,-1.0), pad=4;
  const x=t.bb.x1-pad,y=t.bb.y1-pad,w=t.bb.x2-t.bb.x1+2*pad,h=t.bb.y2-t.bb.y1+2*pad;
  return doc(word(FRA,'Levia',100,color,-1.0),`${g.R(x)} ${g.R(y)} ${g.R(w)} ${g.R(h)}`,Math.round(w*4),Math.round(h*4),TITLE.wm);
}
// --- lockups ---
function lockup(spec,color,{stacked=false}={}){
  const bb=g.inkBox(spec);
  const markH=100, scale=markH/bb.h, markW=bb.w*scale, pad=8;
  const fontSize=markH*0.92;                    // em size
  const t=wordData(FRA,'Levia',fontSize,-fontSize*0.012);
  const tw=t.bb.x2-t.bb.x1;
  if(!stacked){
    const gap=markH*0.40, H=markH+2*pad, W=markW+gap+tw+2*pad;
    return doc(`<g transform="translate(${g.R(pad-bb.x*scale)} ${g.R(pad-bb.y*scale)}) scale(${g.R(scale)})">${g.d(spec,color)}</g>
  <g transform="translate(${g.R(pad+markW+gap-t.bb.x1)} ${g.R(pad+markH-t.bb.y2)})">${word(FRA,'Levia',fontSize,color,-fontSize*0.012)}</g>`,
    `0 0 ${g.R(W)} ${g.R(H)}`,Math.round(W*4),Math.round(H*4),TITLE.lock);
  }
  const gap=markH*0.34, W=Math.max(markW,tw)+2*pad, H=markH+gap+(t.bb.y2-t.bb.y1)+2*pad;
  return doc(`<g transform="translate(${g.R(pad+(W-2*pad-markW)/2-bb.x*scale)} ${g.R(pad-bb.y*scale)}) scale(${g.R(scale)})">${g.d(spec,color)}</g>
  <g transform="translate(${g.R((W-tw)/2-t.bb.x1)} ${g.R(pad+markH+gap-t.bb.y1)})">${word(FRA,'Levia',fontSize,color,-fontSize*0.012)}</g>`,
    `0 0 ${g.R(W)} ${g.R(H)}`,Math.round(W*4),Math.round(H*4),TITLE.lock);
}
const L={};
L['levia-symbol.svg']=symbol(g.MASTER,C.green);
L['levia-symbol-small.svg']=symbol(g.SMALL,C.green);
L['levia-symbol-square.svg']=symbol(g.MASTER,C.off,{square:true,pad:34}); // reversed on green tile
L['levia-symbol-onecolour.svg']=symbol(g.MASTER,'#000000');
L['levia-wordmark.svg']=wordmark(C.green);
L['levia-wordmark-reversed.svg']=wordmark(C.off);
L['levia-lockup-horizontal.svg']=lockup(g.MASTER,C.green);
L['levia-lockup-stacked.svg']=lockup(g.MASTER,C.green,{stacked:true});
L['levia-lockup-horizontal-reversed.svg']=lockup(g.MASTER,C.off);
fs.mkdirSync(ROOT+'/logo',{recursive:true});
for(const [n,c] of Object.entries(L)) fs.writeFileSync(ROOT+'/logo/'+n,c);
console.log('wrote',Object.keys(L).length,'files');

// ---------- RENDERS ----------
async function png(svgStr,px){ return new Resvg(svgStr,{fitTo:{mode:'width',value:px},background:'rgba(0,0,0,0)'}).render().asPng(); }
const b64=b=>'data:image/png;base64,'+Buffer.from(b).toString('base64');
const svgOf=(spec,color,square=false,pad=6)=>{const bb=g.inkBox(spec);let x=bb.x-pad,y=bb.y-pad,w=bb.w+2*pad,h=bb.h+2*pad;
  if(square){const s=Math.max(w,h);x-=(s-w)/2;y-=(s-h)/2;w=h=s;}
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${x} ${y} ${w} ${h}">${g.d(spec,color)}</svg>`;};
module.exports={png,b64,svgOf};
(async()=>{
  const W=1600,H=1220;
  let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${C.off}"/>
  <text x="64" y="50" font-family="Hind Vadodara" font-size="12" letter-spacing="1.8" fill="${C.green}" opacity=".6">LEVIA — DIRECTION A · THE FOLD</text>
  <text x="64" y="84" font-family="Hind Vadodara" font-size="25" fill="${C.green}">Symbol, wordmark, lockup and size tests</text>`;
  const label=(x,y,txt)=>`<text x="${x}" y="${y}" font-family="Hind Vadodara" font-size="11.5" fill="${C.green}" opacity=".58">${txt}</text>`;
  // helper: place an image at native aspect ratio inside a box (fit width)
  async function img(svgStr, x, y, boxW, boxH){
    const m = svgStr.match(/viewBox="([-\d.\s]+)"/);
    const vb = m[1].trim().split(/\s+/).map(Number);
    const ar = vb[2]/vb[3];
    let w = boxW, h = w/ar;
    if(h > boxH){ h = boxH; w = h*ar; }
    const b = await png(svgStr, Math.round(w*2));
    return `<image x="${x.toFixed(1)}" y="${(y + (boxH-h)/2).toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" href="${b64(b)}"/>`;
  }
  // ---------- ROW 1 ----------
  const symSvg = svgOf(g.MASTER,C.green);
  s += await img(symSvg, 64, 110, 300, 180);
  s += label(64, 316, 'Symbol — 204 × 118 ink units · one weight (28/256)');
  const wm=wordData(FRA,'Levia',100,-1.0);
  s += `<g transform="translate(${430-wm.bb.x1} ${282})">${word(FRA,'Levia',100,C.green,-1.0)}</g>`;
  s += label(430, 316, 'Wordmark — Fraunces 500 · opsz 24 · SOFT 50 · WONK 0 · −1.2%');
  const ls=fs.readFileSync(ROOT+'/logo/levia-lockup-stacked.svg','utf8');
  s += await img(ls, 1150, 104, 300, 220);
  s += label(1150, 340, 'Stacked lockup');
  // ---------- ROW 2 ----------
  const lh=fs.readFileSync(ROOT+'/logo/levia-lockup-horizontal.svg','utf8');
  s += await img(lh, 64, 370, 700, 120);
  s += label(64, 506, 'Horizontal lockup — mark height 1.00 · gap 0.40 · wordmark cap 0.92 em');
  // ---------- ROW 3 ----------
  s += `<text x="64" y="560" font-family="Hind Vadodara" font-size="12" letter-spacing="1.8" fill="${C.green}" opacity=".6">SIZE TEST — TRUE PIXELS (LEFT OF EACH PAIR) AND PIXEL ZOOM</text>`;
  const yTop=586;
  let x=64;
  for(const [px,zoom] of [[16,7],[32,6],[64,4]]){
    const b=await png(symSvg,px);
    const z=await sharp(b).resize(px*zoom,px*zoom,{kernel:'nearest'}).png().toBuffer();
    s+=`<image x="${x}" y="${yTop}" width="${px}" height="${px}" href="${b64(b)}"/>`;
    s+=`<text x="${x}" y="${yTop+px+16}" font-family="Hind Vadodara" font-size="11" fill="${C.green}" opacity=".7">${px} px</text>`;
    s+=`<image x="${x+px+14}" y="${yTop}" width="${px*zoom}" height="${px*zoom}" href="${b64(z)}" image-rendering="pixelated"/>`;
    s+=`<text x="${x+px+14}" y="${yTop+px*zoom+16}" font-family="Hind Vadodara" font-size="10.5" fill="${C.green}" opacity=".45">${zoom}× zoom</text>`;
    x += px + 14 + px*zoom + 44;
  }
  // small cut
  s += `<text x="1080" y="560" font-family="Hind Vadodara" font-size="12" letter-spacing="1.8" fill="${C.green}" opacity=".6">SMALL CUT — 16–24 PX</text>`;
  x=1080;
  for(const px of [16,32]){
    const b=await png(svgOf(g.SMALL,C.green),px);
    const z=await sharp(b).resize(px*5,px*5,{kernel:'nearest'}).png().toBuffer();
    s+=`<image x="${x}" y="${yTop}" width="${px}" height="${px}" href="${b64(b)}"/>`;
    s+=`<text x="${x}" y="${yTop+px+16}" font-family="Hind Vadodara" font-size="11" fill="${C.green}" opacity=".7">${px} px</text>`;
    s+=`<image x="${x+px+14}" y="${yTop}" width="${px*5}" height="${px*5}" href="${b64(z)}" image-rendering="pixelated"/>`;
    x += px + 14 + px*5 + 40;
  }
  // ---------- ROW 4: colour ----------
  s+=`<text x="64" y="960" font-family="Hind Vadodara" font-size="12" letter-spacing="1.8" fill="${C.green}" opacity=".6">COLOUR TESTS — REFERENCE ONLY (PALETTE IS FIXED BY THE BRIEF)</text>`;
  const panels=[
    ['One colour — black',"#FFFFFF",'#000000',64,988],
    ['Dark green on off-white',C.off,C.green,64,1092],
    ['Reversed — off-white on green',C.green,C.off,566,988],
    ['Sage — support shapes only',C.off,C.sage,566,1092],
    ['Terracotta — accent shapes only',C.off,C.terra,1068,988],
    ['Text accent #9E4A2C — words only',C.off,C.acc,1068,1092],
  ];
  for(const [lab,bg,fg,px,py] of panels){
    s+=`<rect x="${px}" y="${py}" width="440" height="84" fill="${bg}" stroke="${bg==='#FFFFFF'?'#DDD':'none'}"/>`;
    s+=`<image x="${px+16}" y="${py+16}" width="86" height="52" href="${b64(await png(svgOf(g.MASTER,fg),344))}"/>`;
    const lw=wordData(FRA,'Levia',42,-0.5);
    s+=`<g transform="translate(${px+124-lw.bb.x1} ${py+70})">${word(FRA,'Levia',42,fg,-0.5)}</g>`;
    s+=label(px,py+104,lab);
  }
  s+='</svg>';
  fs.writeFileSync(ROOT+'/src/sheet-tests.svg',s);
  console.log('sheet written');
})();
