const fs=require('fs');
const S=28,R=n=>+n.toFixed(2);
function cap(x1,y1,x2,y2,w=S){const dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,nx=-uy,ny=ux,h=w/2;
 const a=[x1+nx*h,y1+ny*h],b=[x2+nx*h,y2+ny*h],c=[x2-nx*h,y2-ny*h],d=[x1-nx*h,y1-ny*h];
 return `M${R(a[0])} ${R(a[1])}L${R(b[0])} ${R(b[1])}A${R(h)} ${R(h)} 0 0 0 ${R(c[0])} ${R(c[1])}L${R(d[0])} ${R(d[1])}A${R(h)} ${R(h)} 0 0 0 ${R(a[0])} ${R(a[1])}Z`;}
function arcCap(cx,cy,r,w,a1,a2,steps=48){ // filled arc band (round ends)
  const h=w/2,ro=r+h,ri=r-h,rad=a=>a*Math.PI/180;
  let d='';const pts=[];
  for(let i=0;i<=steps;i++){const a=rad(a1+(a2-a1)*i/steps);pts.push([cx+ro*Math.cos(a),cy+ro*Math.sin(a)]);}
  // cap at a2
  const A2=rad(a2),c2=[cx+r*Math.cos(A2),cy+r*Math.sin(A2)];
  for(let i=1;i<12;i++){const a=A2+(a2>a1?1:-1)*(-Math.PI/2+Math.PI*i/12);pts.push([c2[0]+h*Math.cos(a),c2[1]+h*Math.sin(a)]);}
  for(let i=steps;i>=0;i--){const a=rad(a1+(a2-a1)*i/steps);pts.push([cx+ri*Math.cos(a),cy+ri*Math.sin(a)]);}
  const A1=rad(a1),c1=[cx+r*Math.cos(A1),cy+r*Math.sin(A1)];
  for(let i=1;i<12;i++){const a=A1+(a2>a1?-1:1)*(-Math.PI/2+Math.PI*i/12);pts.push([c1[0]+h*Math.cos(a),c1[1]+h*Math.sin(a)]);}
  return 'M'+pts.map(p=>R(p[0])+' '+R(p[1])).join('L')+'Z';
}
const V = {
  'G1 crank':      [cap(40,88,216,88), cap(168,88,168,176), cap(168,176,96,176)],
  'G2 crank wide': [cap(32,84,224,84), cap(156,84,156,180), cap(156,180,80,180)],
  'G3 hook':       [cap(88,64,88,140,26), arcCap(140,140,52,26,180,270), cap(140,192,196,192,26)],
  'G4 settle':     [arcCap(120,120,72,26,180,270), cap(120,192,196,192,26), cap(56,192,120,192,26)],
  'G5 dogear':     [cap(72,64,184,64), cap(72,64,72,192), cap(72,192,184,192), cap(184,192,184,128), cap(184,128,140,128)],
  'G6 two bars':   [cap(44,92,196,92), cap(60,168,212,168)],
};
const names=Object.keys(V),cols=2,cell=430,rowH=250;
const W=cols*cell,H=Math.ceil(names.length/cols)*rowH+20;
let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><rect width="100%" height="100%" fill="#fff"/>`;
s+=`<defs><filter id="blur"><feGaussianBlur stdDeviation="1.6"/></filter></defs>`;
names.forEach((k,i)=>{
  const x=(i%cols)*cell,y=Math.floor(i/cols)*rowH+16;
  const g=V[k].join(' ');
  s+=`<svg x="${x+16}" y="${y}" width="170" height="170" viewBox="0 0 256 256"><path d="${g}" fill="#111"/></svg>`;
  let sx=x+200;
  [[64,0],[32,0],[16,0]].forEach(([n])=>{ s+=`<svg x="${sx}" y="${y+10}" width="${n}" height="${n}" viewBox="0 0 256 256"><path d="${g}" fill="#111"/></svg>`; sx+=n+18;});
  // blur (squint) at 96
  s+=`<svg x="${x+200}" y="${y+110}" width="96" height="96" viewBox="0 0 256 256"><path d="${g}" fill="#111" filter="url(#blur)"/></svg>`;
  s+=`<text x="${x+16}" y="${y+rowH-46}" font-family="HindVadodara" font-size="15" fill="#555">${k}</text>`;
});
fs.writeFileSync('/home/user/levia/src/audition.svg',s+'</svg>');
console.log('ok');
