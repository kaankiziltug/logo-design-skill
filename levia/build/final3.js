const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const {cap,R}=require('/home/user/logo-design-skill/levia/build/marks2.js');
const {textPath}=require('/home/user/logo-design-skill/levia/build/type2path.js');
const FRA='/home/user/fonts/static/F-o24-w500-s50.ttf';
const C={off:'#F2EFE9',green:'#3A4C40',sage:'#8BA892',terra:'#C4694A',acc:'#9E4A2C'};

// ---- three directions, 256 box ----
const DIR={
  A:{ // The Fold — folded section, two rest heights
    svg:(c)=>[cap(40,88,216,88,28),cap(168,88,168,178,28),cap(168,178,96,178,28)].map(d=>`<path d="${d}" fill="${c}"/>`).join(''),
    // bbox of ink
    box:[26,74,230,192]
  },
  B:{ // The L — letterform, foot folds up
    svg:(c)=>[cap(96,52,96,176,26),cap(96,176,196,176,26),cap(196,176,196,140,26)].map(d=>`<path d="${d}" fill="${c}"/>`).join(''),
    box:[83,39,209,189]
  },
  C:{ // The Keep — rounded tile, one rest slot in negative space
    svg:(c)=>`<path d="M72 48H184A44 44 0 0 1 228 92V164A44 44 0 0 1 184 208H72A44 44 0 0 1 28 164V92A44 44 0 0 1 72 48Z" fill="${c}"/><path d="M64 118H192A14 14 0 0 1 192 146H64A14 14 0 0 1 64 118Z" fill="${C.off}"/>`,
    box:[28,48,228,208]
  }
};
const wm=textPath(FRA,'Levia',100,-1.0);
function mark(c,size,color){ // standalone square svg string
  const d=DIR[c];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="26 34 204 204" width="${size}" height="${size}">${d.svg(color)}</svg>`;
}
// lockup: mark (height = cap height) + wordmark, baseline aligned to mark bottom
function lockup(c,{h=120,color=C.green,wmColor=null,stacked=false}={}){
  const d=DIR[c];
  const bb=d.box; const mh=bb[3]-bb[1];
  const capH=70; // Fraunces cap height at opsz24 w500 ~ 0.70 em
  const wsize=h*0.92;
  const t=textPath(FRA,'Levia',wsize,-1.2);
  const inkH=t.bb.y2-t.bb.y1;
  if(!stacked){
    const gap=h*0.30;
    const markW=h;
    const totalW=markW+gap+(t.bb.x2-t.bb.x1);
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${totalW} ${h}" width="${totalW}" height="${h}">
      <g transform="translate(0 0)"><svg x="0" y="0" width="${markW}" height="${h}" viewBox="${bb[0]} ${bb[1]} ${bb[2]-bb[0]} ${bb[3]-bb[1]}" preserveAspectRatio="xMidYMid meet">${d.svg(color)}</svg></g>
      <g transform="translate(${markW+gap} ${h - 4 + (0)})"><path d="${t.d}" fill="${wmColor||color}" transform="translate(${-t.bb.x1} ${-(t.bb.y2)})"/></g>
    </svg>`;
  }
}
(async()=>{
  const tiles=[];
  const W=1560, bg=C.off;
  let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="980"><rect width="${W}" height="980" fill="${bg}"/>`;
  const names={A:'A · The Fold',B:'B · The L',C:'C · The Keep'};
  let y=40;
  for(const k of ['A','B','C']){
    s+=`<text x="40" y="${y+16}" font-family="HindVadodara" font-size="18" fill="${C.green}">${names[k]}</text>`;
    s+=`<g transform="translate(40 ${y+30}) scale(1.0)"><svg width="150" height="150" viewBox="${DIR[k].box[0]-8} ${DIR[k].box[1]-8} ${DIR[k].box[2]-DIR[k].box[0]+16} ${DIR[k].box[3]-DIR[k].box[1]+16}">${DIR[k].svg(C.green)}</svg></g>`;
    // horizontal lockup
    s+=`<g transform="translate(230 ${y+40})"><svg width="430" height="110" viewBox="0 0 430 110">${inlineLock(k,110)}</svg></g>`;
    // one-colour black
    s+=`<g transform="translate(700 ${y+60})"><svg width="56" height="56" viewBox="${DIR[k].box[0]} ${DIR[k].box[1]} ${DIR[k].box[2]-DIR[k].box[0]} ${DIR[k].box[3]-DIR[k].box[1]}">${DIR[k].svg('#000')}</svg></g>`;
    // reversed on green
    s+=`<g transform="translate(790 ${y+50})"><rect x="0" y="0" width="150" height="76" rx="6" fill="${C.green}"/><svg x="20" y="14" width="48" height="48" viewBox="${DIR[k].box[0]} ${DIR[k].box[1]} ${DIR[k].box[2]-DIR[k].box[0]} ${DIR[k].box[3]-DIR[k].box[1]}">${DIR[k].svg(C.off)}</svg></g>`;
    // sizes
    [64,32,16].forEach((n,j)=>{ s+=`<svg x="${980+j*100}" y="${y+50}" width="${n}" height="${n}" viewBox="${DIR[k].box[0]} ${DIR[k].box[1]} ${DIR[k].box[2]-DIR[k].box[0]} ${DIR[k].box[3]-DIR[k].box[1]}">${DIR[k].svg(C.green)}</svg>`; });
    y+=300;
  }
  fs.writeFileSync('/home/user/logo-design-skill/levia/src/final3.svg',s+'</svg>');
  console.log('written');
})();
function inlineLock(k,h){
  const bb=DIR[k].box, mh=bb[3]-bb[1], mw=bb[2]-bb[0];
  const markW=h*0.86, gap=h*0.26, wsize=h*1.16;
  const t=textPath(FRA,'Levia',wsize,-1.6);
  const tw=t.bb.x2-t.bb.x1;
  const wmX=markW+gap;
  return `<g><svg x="0" y="0" width="${markW}" height="${h}" viewBox="${bb[0]} ${bb[1]} ${mw} ${mh}">${DIR[k].svg(C.green)}</svg>
  <g transform="translate(${wmX} ${h})"><path d="${t.d}" fill="${C.green}" transform="translate(${-t.bb.x1} ${-t.bb.y2})"/></g></g>`;
}
