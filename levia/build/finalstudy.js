const fs=require('fs');
// candidates as filled geometry (analytic capsules) on 256 box, stroke 28
const S=28, H=S/2, R=(n)=>+n.toFixed(2);
function cap(x1,y1,x2,y2,w=S){ // exact capsule outline path
  const dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,nx=-uy,ny=ux,h=w/2;
  const a=[x1+nx*h,y1+ny*h],b=[x2+nx*h,y2+ny*h],c=[x2-nx*h,y2-ny*h],d=[x1-nx*h,y1-ny*h];
  return `M${R(a[0])} ${R(a[1])}L${R(b[0])} ${R(b[1])}A${R(h)} ${R(h)} 0 0 0 ${R(c[0])} ${R(c[1])}L${R(d[0])} ${R(d[1])}A${R(h)} ${R(h)} 0 0 0 ${R(a[0])} ${R(a[1])}Z`;
}
const V = {
  'F1 ortho':       { paths:[cap(44,84,216,84), cap(176,84,176,176), cap(176,176,92,176)] },
  'F2 ortho tall':  { paths:[cap(40,78,216,78), cap(180,78,180,182), cap(180,182,88,182)] },
  'F3 diag45':      { paths:[cap(44,84,216,84), cap(196,84,124,156), cap(196,84,196,168), cap(196,168,120,168)] },
  'F4 diag only':   { paths:[cap(44,84,216,84), cap(200,84,120,164), cap(200,164,96,164)] },
  'F5 diag45 b':    { paths:[cap(40,88,212,88), cap(212,88,212,150), cap(212,150,128,150), cap(128,150,56,222)] },
};
const cols=3,cell=340;
const names=Object.keys(V);
let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${cols*cell}" height="${Math.ceil(names.length/cols)*cell}"><rect width="100%" height="100%" fill="#fff"/>`;
names.forEach((k,i)=>{
  const x=(i%cols)*cell,y=Math.floor(i/cols)*cell;
  const g=V[k].paths.join(' ');
  s+=`<g transform="translate(${x+28} ${y+24})"><svg width="200" height="200" viewBox="0 0 256 256"><path d="${g}" fill="#111" fill-rule="nonzero"/></svg></g>`;
  let sx=x+248;
  [64,32,16].forEach(n=>{s+=`<svg x="${sx}" y="${y+40}" width="${n}" height="${n}" viewBox="0 0 256 256"><path d="${g}" fill="#111" fill-rule="nonzero"/></svg>`;sx+=n+22;});
  s+=`<text x="${x+28}" y="${y+cell-18}" font-family="HindVadodara" font-size="15" fill="#666">${k}</text>`;
});
fs.writeFileSync('/home/user/levia/src/finalstudy.svg',s+'</svg>');
console.log('ok');
