const fs=require('fs');
const {textPath, load}=require('/home/user/levia/build/type2path.js');
const f=load('/home/user/fonts/static/F-o24-w500-s50.ttf');
const gl=f.stringToGlyphs('Levia');
gl.forEach((g,i)=>{const bb=g.getBoundingBox(); console.log(i, f.glyphs.get(g.index).name, 'x1',bb.x1.toFixed(1),'x2',bb.x2.toFixed(1),'y1',bb.y1.toFixed(1),'y2',bb.y2.toFixed(1),'adv',g.advanceWidth);});
const t=textPath('/home/user/fonts/static/F-o24-w500-s50.ttf','Levia',200,0);
// render just the L at big size
let s=`<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500"><rect width="100%" height="100%" fill="#fff"/>
<g transform="translate(60 400)"><path d="${textPath('/home/user/fonts/static/F-o24-w500-s50.ttf','L',200,0).d}" fill="#111"/></g>
<g transform="translate(400 400)"><path d="${textPath('/home/user/fonts/static/F-o24-w500-s50.ttf','e',200,0).d}" fill="#111"/></g></svg>`;
fs.writeFileSync('/home/user/levia/src/lstudy.svg',s);
