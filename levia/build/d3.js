const fs=require('fs');
const {cap,R}=require('/home/user/levia/build/marks2.js');
const {textPath}=require('/home/user/levia/build/type2path.js');
const FRA='/home/user/fonts/static/F-o24-w500-s50.ttf';

// B: letterform — the L of Levia, foot lifted into a shallow fold (single stroke, no serifs)
// Stem + foot where the foot has a downward-right fold tab.
const B = {
  'B1 L-fold':   [cap(96,56,96,168,26), cap(96,168,196,168,26), cap(196,168,196,132,26)],
  'B2 L-lift':   [cap(96,56,96,168,26), cap(96,168,196,168,26)],
  'B3 L-tab':    [cap(92,52,92,172,28), cap(92,172,204,172,28), cap(204,172,204,140,20)],
  'B4 L-serif':  [cap(92,52,92,174,26), cap(92,174,208,174,26), cap(92,174,60,174,26)],
};
// C: emblem tile with two slots
function tile(x,y,w,h,r,slots){
  const rr=`M${x+r} ${y}H${x+w-r}A${r} ${r} 0 0 1 ${x+w} ${y+r}V${y+h-r}A${r} ${r} 0 0 1 ${x+w-r} ${y+h}H${x+r}A${r} ${r} 0 0 1 ${x} ${y+h-r}V${y+r}A${r} ${r} 0 0 1 ${x+r} ${y}Z`;
  const s2=slots.map(s=>`M${s[0]} ${s[1]}H${s[2]}A${s[3]} ${s[3]} 0 0 1 ${s[2]} ${s[1]+2*s[3]}H${s[0]}A${s[3]} ${s[3]} 0 0 1 ${s[0]} ${s[1]}Z`).join(' ');
  return `<path d="${rr}" fill="#111"/><path d="${s2}" fill="#F2EFE9"/>`;
}
const C = {
  'C1 slots2': tile(28,48,200,160,44,[[64,92,192,12],[64,152,136,12]]),
  'C2 slot1':  tile(28,48,200,160,44,[[64,118,192,14]]),
  'C3 offset': tile(28,48,200,160,44,[[64,96,192,11],[64,156,120,11]]),
};
const variants=[...Object.entries(B).map(([k,v])=>({k,svg:v.map(d=>`<path d="${d}" fill="#111"/>`).join('')})),
  ...Object.entries(C).map(([k,v])=>({k,svg:v}))];
const cols=3,cell=340;
let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${cols*cell}" height="${Math.ceil(variants.length/cols)*cell}"><rect width="100%" height="100%" fill="#F2EFE9"/>`;
variants.forEach((v,i)=>{
  const x=(i%cols)*cell,y=Math.floor(i/cols)*cell;
  s+=`<g transform="translate(${x+30} ${y+26}) scale(0.72)">${v.svg}</g>`;
  [64,32,16].forEach((n,j)=>{ s+=`<g transform="translate(${x+230+j*30} ${y+40}) scale(${n/256})">${v.svg.replace(/#F2EFE9/g,'#F2EFE9')}</g>`; });
  s+=`<text x="${x+30}" y="${y+cell-20}" font-family="HindVadodara" font-size="16" fill="#666">${v.k}</text>`;
});
fs.writeFileSync('/home/user/levia/src/d3.svg',s+'</svg>');
console.log('ok');
