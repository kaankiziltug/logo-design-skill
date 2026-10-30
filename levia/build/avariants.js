const fs = require('fs');
const V = [
  { id:'A-a', w:28, d:['M44 88H212','M212 88V172H116'] },
  { id:'A-b', w:28, d:['M40 88H216','M190 88V172H110'] },
  { id:'A-c', w:28, d:['M36 88H220','M176 88V172H96'] },
  { id:'A-d', w:28, d:['M40 84H216','M196 84V176H104'] },
  { id:'A-e', w:26, d:['M40 84H216','M196 84V176H104','M196 176H216'] },
  { id:'A-f', w:28, d:['M216 88H44','M72 88V172H150'] },
];
const cell=330, cols=3;
let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${cols*cell}" height="${Math.ceil(V.length/cols)*cell}"><rect width="100%" height="100%" fill="#fff"/>`;
V.forEach((v,i)=>{
  const x=(i%cols)*cell, y=Math.floor(i/cols)*cell;
  s+=`<g transform="translate(${x+30} ${y+30})"><svg width="200" height="200" viewBox="0 0 256 256">`+v.d.map(d=>`<path d="${d}" fill="none" stroke="#111" stroke-width="${v.w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('')+`</svg></g>`;
  // small sizes
  let sx=x+250;
  [64,32,16].forEach(n=>{ s+=`<svg x="${sx}" y="${y+40}" width="${n}" height="${n}" viewBox="0 0 256 256">`+v.d.map(d=>`<path d="${d}" fill="none" stroke="#111" stroke-width="${v.w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('')+`</svg>`; sx+=n+26; });
  s+=`<text x="${x+30}" y="${y+cell-16}" font-family="HindVadodara" font-size="16" fill="#666">${v.id}</text>`;
});
fs.writeFileSync('/home/user/levia/src/avariants.svg', s+'</svg>');
console.log('ok');
