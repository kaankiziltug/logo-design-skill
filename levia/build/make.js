const fs=require('fs');
const path=require('path');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const {textPath}=require('/home/user/logo-design-skill/levia/build/type2path.js');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const C={off:'#F2EFE9',green:'#3A4C40',sage:'#8BA892',terra:'#C4694A',acc:'#9E4A2C'};
const FRA='/home/user/fonts/static/F-o24-w500-s50.ttf';
const ROOT='/home/user/logo-design-skill/levia';

function bboxOf(spec){ return g.inkBox(spec); }
function svgDoc(inner, vb, w, h){
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${w}" height="${h}" role="img" aria-label="Levia">\n${inner}\n</svg>\n`;
}
// ---------- 1. SYMBOL FILES ----------
function symbolFile(spec,color,pad=6){
  const bb=bboxOf(spec); const s=Math.max(bb.w,bb.h);
  const vb=`${g.R(bb.x-(s-bb.w)/2-pad)} ${g.R(bb.y-(s-bb.h)/2-pad)} ${g.R(s+2*pad)} ${g.R(s+2*pad)}`;
  return svgDoc(g.d(spec,color), vb, 256, 256);
}
function wordmarkFile(color){
  const t=textPath(FRA,'Levia',100,-1.0);
  const pad=4;
  const vb=`${g.R(t.bb.x1-pad)} ${g.R(t.bb.y1-pad)} ${g.R(t.bb.x2-t.bb.x1+2*pad)} ${g.R(t.bb.y2-t.bb.y1+2*pad)}`;
  return svgDoc(`<path d="${t.d}" fill="${color}"/>`, vb, Math.round((t.bb.x2-t.bb.x1+2*pad)*2), Math.round((t.bb.y2-t.bb.y1+2*pad)*2));
}
// lockup: mark height = cap-ish height, optical gap = 0.42 x mark height
function lockup(spec, color, {stacked=false}={}){
  const bb=bboxOf(spec);
  const markH = 100;                      // target mark height in lockup units
  const scale = markH/bb.h;
  const markW = bb.w*scale;
  const capH = 70;                        // Fraunces cap height ≈ 0.70 em at opsz24/500
  const fontSize = 100 * (markH*0.64)/(0.70*100); // wordmark cap height = 0.64 x mark height
  const t=textPath(FRA,'Levia',fontSize,-fontSize*0.012);
  const tw=t.bb.x2-t.bb.x1;
  if(!stacked){
    const gap=markH*0.36, pad=markH*0.06;
    const H=markH+2*pad, W=markW+gap+tw+2*pad;
    const inner=`<g transform="translate(${g.R(pad-bb.x*scale)} ${g.R(pad-bb.y*scale)}) scale(${g.R(scale)})">${g.d(spec,color)}</g>
  <g transform="translate(${g.R(pad+markW+gap)} ${g.R(pad+markH)})"><path d="${t.d}" fill="${color}" transform="translate(${g.R(-t.bb.x1)} ${g.R(-t.bb.y2)})"/></g>`;
    return svgDoc(inner, `0 0 ${g.R(W)} ${g.R(H)}`, Math.round(W*2), Math.round(H*2));
  } else {
    const gap=markH*0.30, pad=markH*0.06;
    const W=Math.max(markW,tw)+2*pad, H=markH+gap+(t.bb.y2-t.bb.y1)+2*pad;
    const inner=`<g transform="translate(${g.R(pad+(W-2*pad-markW)/2-bb.x*scale)} ${g.R(pad-bb.y*scale)}) scale(${g.R(scale)})">${g.d(spec,color)}</g>
  <g transform="translate(${g.R((W-tw)/2-t.bb.x1)} ${g.R(pad+markH+gap-t.bb.y1)})"><path d="${t.d}" fill="${color}"/></g>`;
    return svgDoc(inner, `0 0 ${g.R(W)} ${g.R(H)}`, Math.round(W*2), Math.round(H*2));
  }
}
fs.mkdirSync(path.join(ROOT,'logo'),{recursive:true});
const files={
  'levia-symbol.svg':               symbolFile(g.MASTER,C.green),
  'levia-symbol-small.svg':         symbolFile(g.SMALL,C.green),
  'levia-symbol-onecolour.svg':     symbolFile(g.MASTER,'#000000'),
  'levia-wordmark.svg':             wordmarkFile(C.green),
  'levia-lockup-horizontal.svg':    lockup(g.MASTER,C.green),
  'levia-lockup-stacked.svg':       lockup(g.MASTER,C.green,{stacked:true}),
  'levia-lockup-reversed.svg':      lockup(g.MASTER,C.off),
};
for(const [n,content] of Object.entries(files)) fs.writeFileSync(path.join(ROOT,'logo',n),content);
console.log('svg files:',Object.keys(files).join(', '));
module.exports={C,g,textPath,FRA};
