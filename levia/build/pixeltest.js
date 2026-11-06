const fs=require('fs');
const R=n=>+n.toFixed(2);
function cap(x1,y1,x2,y2,w){const dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,nx=-uy,ny=ux,h=w/2;
 const a=[x1+nx*h,y1+ny*h],b=[x2+nx*h,y2+ny*h],c=[x2-nx*h,y2-ny*h],d=[x1-nx*h,y1-ny*h];
 return `M${R(a[0])} ${R(a[1])}L${R(b[0])} ${R(b[1])}A${R(h)} ${R(h)} 0 0 0 ${R(c[0])} ${R(c[1])}L${R(d[0])} ${R(d[1])}A${R(h)} ${R(h)} 0 0 0 ${R(a[0])} ${R(a[1])}Z`;}
function crank(w, over=48, deck=[40,216], drop=168, y1=88, y2=178, perch=96){
  return [cap(deck[0],y1,deck[1],y1,w), cap(drop,y1,drop,y2,w), cap(drop,y2,perch,y2,w)].join(' ');
}
const rows = [
  {name:'w28 master',   d: crank(28)},
  {name:'w32',          d: crank(32)},
  {name:'w36',          d: crank(36)},
  {name:'w40 small cut', d: crank(40, 0, [40,208], 160, 92, 176, 96)},
];
let s='', y=14;
const W=900;
s+=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="520"><rect width="100%" height="100%" fill="#fff"/>`;
rows.forEach((r,i)=>{
  const yy = 20 + i*120;
  s+=`<text x="14" y="${yy+12}" font-family="HindVadodara" font-size="13" fill="#666">${r.name}</text>`;
  [64,32,24,16].forEach((n,j)=>{
    const x = 210 + j*110;
    s+=`<svg x="${x}" y="${yy}" width="${n}" height="${n}" viewBox="0 0 256 256"><path d="${r.d}" fill="#111"/></svg>`;
    s+=`<text x="${x}" y="${yy+82}" font-family="HindVadodara" font-size="11" fill="#aaa">${n}px</text>`;
    // magnified neighbour for inspection
    s+=`<svg x="${x+40}" y="${yy}" width="${n*4}" height="${n*4}" viewBox="0 0 256 256" shape-rendering="crispEdges" style="image-rendering:pixelated"><path d="${r.d}" fill="#111"/></svg>`;
  });
});
fs.writeFileSync('/home/user/levia/src/pixeltest.svg',s+'</svg>');
console.log('ok');
