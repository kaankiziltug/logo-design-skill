// Canonical Levia geometry. Canvas 256 x 256. All strokes are round-capped capsules.
const R=n=>+n.toFixed(2);
function capsule(x1,y1,x2,y2,w){
  const dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,nx=-uy,ny=ux,h=w/2;
  const a=[x1-nx*h,y1-ny*h], b=[x2-nx*h,y2-ny*h], c=[x2+nx*h,y2+ny*h], d=[x1+nx*h,y1+ny*h];
  return `M${R(a[0])} ${R(a[1])}L${R(b[0])} ${R(b[1])}A${R(h)} ${R(h)} 0 0 1 ${R(c[0])} ${R(c[1])}L${R(d[0])} ${R(d[1])}A${R(h)} ${R(h)} 0 0 1 ${R(a[0])} ${R(a[1])}Z`;
}
// Master: three bars, one weight 28/256
const MASTER = {
  w: 28,
  parts: [
    { name:'deck',  x1:40,  y1:88,  x2:216, y2:88,  note:'upper rest (lean height)' },
    { name:'riser', x1:168, y1:88,  x2:168, y2:178, note:'the fold' },
    { name:'perch', x1:168, y1:178, x2:96,  y2:178, note:'lower rest (perch height)' },
  ],
};
// Small cut: fatter, squarer footprint, arms brought closer
const SMALL = {
  w: 44,
  parts: [
    { name:'deck',  x1:62,  y1:74,  x2:210, y2:74 },
    { name:'riser', x1:158, y1:74,  x2:158, y2:186 },
    { name:'perch', x1:158, y1:186, x2:116, y2:186 },
  ],
};
function d(spec, color){ return spec.parts.map(p=>`<path d="${capsule(p.x1,p.y1,p.x2,p.y2,spec.w)}" fill="${color}"/>`).join('\n  '); }
function inkBox(spec){
  const h=spec.w/2; let x1=1e9,y1=1e9,x2=-1e9,y2=-1e9;
  for(const p of spec.parts){ x1=Math.min(x1,p.x1-h,p.x2-h); x2=Math.max(x2,p.x1+h,p.x2+h); y1=Math.min(y1,p.y1-h,p.y2-h); y2=Math.max(y2,p.y1+h,p.y2+h); }
  return {x:x1,y:y1,w:x2-x1,h:y2-y1};
}
function symbolSVG(spec, color, {bg=null}={}){
  const bb=inkBox(spec);
  const pad = 0;
  const vb = `${R(bb.x-pad)} ${R(bb.y-pad)} ${R(bb.w+2*pad)} ${R(bb.h+2*pad)}`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" role="img" aria-label="Levia">
  ${bg?`<rect x="${R(bb.x-pad)}" y="${R(bb.y-pad)}" width="${R(bb.w+2*pad)}" height="${R(bb.h+2*pad)}" fill="${bg}"/>`:''}
  ${d(spec,color)}
</svg>`;
}
module.exports = { MASTER, SMALL, capsule, d, inkBox, symbolSVG, R };
