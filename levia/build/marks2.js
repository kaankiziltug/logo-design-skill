// Final geometry, 256 box. Reference cap tested visually: a(top-left) -> b(top-right) -> c(bottom-right) -> d(bottom-left), sweep 0 both.
const R=n=>+n.toFixed(2);
function cap(x1,y1,x2,y2,w){
  const dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,nx=-uy,ny=ux,h=w/2;
  const a=[x1-nx*h,y1-ny*h], b=[x2-nx*h,y2-ny*h], c=[x2+nx*h,y2+ny*h], d=[x1+nx*h,y1+ny*h];
  return `M${R(a[0])} ${R(a[1])}L${R(b[0])} ${R(b[1])}A${R(h)} ${R(h)} 0 0 1 ${R(c[0])} ${R(c[1])}L${R(d[0])} ${R(d[1])}A${R(h)} ${R(h)} 0 0 1 ${R(a[0])} ${R(a[1])}Z`;
}
const G = {
  fold:      { w:28, d(c){ return [cap(40,88,216,88,c), cap(168,88,168,178,c), cap(168,178,96,178,c)].join(' '); } },
  foldSmall: { w:40, d(c){ return [cap(44,96,204,96,c), cap(166,96,166,170,c), cap(166,170,100,170,c)].join(' '); } },
};
module.exports = { G, cap, R };
