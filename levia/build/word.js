const { execFileSync } = require('child_process');
const PY='/home/user/.venv/bin/python', EX='/home/user/logo-design-skill/levia/build/extract.py';
const cache={};
function wordData(fontPath, text, size, trackingPx=0){
  const key=[fontPath,text,size,trackingPx].join('|');
  if(cache[key]) return cache[key];
  const j=JSON.parse(execFileSync(PY,[EX,fontPath,text,String(trackingPx/size)],{maxBuffer:1<<26}).toString());
  const s=size/j.upem;
  const inner=j.glyphs.map(g=>`<path d="${g.d}" transform="translate(${(0).toFixed(2)} 0) scale(${s} ${-s})"/>`).join('');
  // rebuild with correct x offsets
  let x=0, parts=[];
  for(const g of j.glyphs){
    parts.push(`<path d="${g.d}" transform="translate(${(x*s).toFixed(3)} 0) scale(${s.toFixed(8)})"/>`);
    x+=g.adv+trackingPx/s;
  }
  const out={parts, bb:{x1:j.bbox[0]*s,y1:j.bbox[1]*s,x2:j.bbox[2]*s,y2:j.bbox[3]*s}, advance:x*s};
  cache[key]=out; return out;
}
function word(fontPath,text,size,color,trackingPx=0){
  return wordData(fontPath,text,size,trackingPx).parts.join('').replace(/<path /g,`<path fill="${color}" `);
}
module.exports={wordData,word};
