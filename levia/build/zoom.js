const fs=require('fs');
const {G}=require('/home/user/levia/build/marks2.js');
const d=G.fold.d(28);
// crop the two junctions at high magnification
const mk=(x,y,w,h,scale,file)=>{
  const s=`<svg xmlns="http://www.w3.org/2000/svg" width="${w*scale}" height="${h*scale}" viewBox="${x} ${y} ${w} ${h}"><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#F2EFE9"/><path d="${d}" fill="#3A4C40"/></svg>`;
  fs.writeFileSync(file,s);
};
mk(150,70,60,60,8,'/home/user/levia/src/j1.svg');   // top-right junction
mk(150,150,60,60,8,'/home/user/levia/src/j2.svg');  // bottom junction
console.log('ok');
