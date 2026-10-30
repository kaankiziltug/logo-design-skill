const fs = require('fs');
const { textPath } = require('/home/user/levia/build/type2path.js');
const F = '/home/user/fonts/static/';
const rows = ['F-o9-w500-s50','F-o24-w500-s50','F-o60-w500-s50','F-o120-w400-s50','F-o9-w600-s50','F-o24-w600-s50','F-o24-w500-s0','F-o24-w500-s100','F-o24-w500-s50-wonk'];
const W=1200, rh=120;
let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${rows.length*rh+80}"><rect width="100%" height="100%" fill="#F2EFE9"/>`;
rows.forEach((r,i)=>{
  const y=70+i*rh;
  const t=textPath(F+r+'.ttf','Levia',66,-1.0);
  s+=`<text x="20" y="${y-40}" font-family="HindVadodara" font-size="12" fill="#8a8a80">${r}</text>`;
  s+=`<g transform="translate(20 ${y})"><path d="${t.d}" fill="#3A4C40"/></g>`;
});
fs.writeFileSync('/home/user/levia/src/typespec.svg', s+'</svg>');
console.log('ok');
