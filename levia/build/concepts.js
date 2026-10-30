const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const {word,wordData}=require('/home/user/logo-design-skill/levia/build/word.js');
const C={off:'#F2EFE9',green:'#3A4C40',sage:'#8BA892',terra:'#C4694A',acc:'#9E4A2C'};
const FRA='/home/user/fonts/static/F-o24-w500-s50.ttf';
const FONTS=['/home/user/fonts/HindVadodara-Regular.ttf','/home/user/fonts/HindVadodara-Medium.ttf','/home/user/fonts/HindVadodara-SemiBold.ttf'];
const b64=b=>'data:image/png;base64,'+Buffer.from(b).toString('base64');
const render=(svg,w)=>new Resvg(svg,{fitTo:{mode:'width',value:w},font:{fontFiles:FONTS,loadSystemFonts:false,defaultFontFamily:'Hind Vadodara'}}).render().asPng();

// ---------- three marks, all in a 256 box ----------
const MARKS={
  A:{ // The Fold — current master
    svg:(c)=>g.d(g.MASTER,c), box:g.inkBox(g.MASTER),
  },
  B:{ // The L — letterform: L's foot folds up into a tab
    svg:(c)=>{
      const cap=(x1,y1,x2,y2,w)=>{const dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,nx=-uy,ny=ux,h=w/2;
        const a=[x1-nx*h,y1-ny*h],b=[x2-nx*h,y2-ny*h],cc=[x2+nx*h,y2+ny*h],d=[x1+nx*h,y1+ny*h];
        return `M${a[0].toFixed(2)} ${a[1].toFixed(2)}L${b[0].toFixed(2)} ${b[1].toFixed(2)}A${h} ${h} 0 0 1 ${cc[0].toFixed(2)} ${cc[1].toFixed(2)}L${d[0].toFixed(2)} ${d[1].toFixed(2)}A${h} ${h} 0 0 1 ${a[0].toFixed(2)} ${a[1].toFixed(2)}Z`;};
      return [cap(92,44,92,184,30),cap(92,184,204,184,30),cap(204,184,204,140,30)].map(d=>`<path d="${d}" fill="${c}"/>`).join('');
    },
    box:{x:77,y:29,w:157,h:185},
  },
  C:{ // The Keep — rounded tile, one horizontal rest in negative space, echoes a rounded seat pad
    svg:(c)=>`<path d="M74 40H182A48 48 0 0 1 230 88V168A48 48 0 0 1 182 216H74A48 48 0 0 1 26 168V88A48 48 0 0 1 74 40Z" fill="${c}"/>
      <path d="M62 112H194A16 16 0 0 1 194 144H62A16 16 0 0 1 62 112Z" fill="${C.off}"/>`,
    box:{x:26,y:40,w:204,h:176},
  },
};
function markImg(k,color,pad=8){
  const bb=MARKS[k].box;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${bb.x-pad} ${bb.y-pad} ${bb.w+2*pad} ${bb.h+2*pad}">${MARKS[k].svg(color)}</svg>`;
}
// fit an image inside a w x h box, preserving aspect
function fitImg(k,color,pad,pngW,px,py,bw,bh){
  const bb=MARKS[k].box;
  const vbW=bb.w+2*pad, vbH=bb.h+2*pad, ar=vbW/vbH;
  let w=bw, h=w/ar;
  if(h>bh){ h=bh; w=h*ar; }
  return `<image x="${(px+(bw-w)/2).toFixed(1)}" y="${(py+(bh-h)/2).toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" href="${b64(render(markImg(k,color,pad),pngW))}"/>`;
}
(async()=>{
  const W=1600,H=1300, bg=C.off;
  let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${bg}"/>
  <text x="64" y="54" font-family="Hind Vadodara" font-size="12" letter-spacing="1.8" fill="${C.green}" opacity=".6">LEVIA — EXPLORATION CONCEPTS · NOT FOR PRODUCTION</text>
  <text x="64" y="92" font-family="Hind Vadodara" font-size="26" fill="${C.green}">Three directions, one colour, true sizes</text>`;
  const cols=[
    {k:'A',name:'A · The Fold',idea:'A section through the rest at both heights — perch low, lean high, one continuous surface.',tag:'RECOMMENDED'},
    {k:'B',name:'B · The L',idea:'The L of Levia, its foot folded up like the rest itself — a monogram that is also the product.',tag:''},
    {k:'C',name:'C · The Keep',idea:'A soft rounded pad with one rest line held in negative space — a bench seat, softened nearly to abstraction.',tag:''},
  ];
  let x0=64;
  for(const c of cols){
    const colW=480;
    s+=`<text x="${x0}" y="170" font-family="Hind Vadodara" font-size="20" fill="${C.green}">${c.name}</text>`;
    if(c.tag) s+=`<text x="${x0}" y="150" font-family="Hind Vadodara" font-size="10.5" letter-spacing="1.6" fill="${C.terra}">${c.tag}</text>`;
    // big mark
    s+=fitImg(c.k,C.green,10,460,x0,180,240,220);
    // sizes true + zoom
    let sx=x0+270, sy=200;
    for(const px of [64,32,16]){
      const b=await new Promise(r=>r(render(markImg(c.k,C.green,4),px)));
      const bb=MARKS[c.k].box, ar=(bb.w+8)/(bb.h+8);
      const h=px/ar;
      s+=`<image x="${sx}" y="${sy+(px-h)/2}" width="${px}" height="${h.toFixed(2)}" href="${b64(b)}"/>`;
      s+=`<text x="${sx}" y="${sy+px+16}" font-family="Hind Vadodara" font-size="10" fill="${C.green}" opacity=".5">${px}</text>`;
      sy+=px+34;
    }
    // one-colour black + reversed chips
    s+=`<rect x="${x0}" y="440" width="86" height="86" fill="#fff" stroke="#E2DDD2"/>`;
    s+=fitImg(c.k,'#000000',6,140,x0+8,448,70,70);
    s+=`<rect x="${x0+100}" y="440" width="86" height="86" rx="4" fill="${C.green}"/>`;
    s+=fitImg(c.k,C.off,6,140,x0+108,448,70,70);
    s+=`<text x="${x0}" y="546" font-family="Hind Vadodara" font-size="10.5" fill="${C.green}" opacity=".5">one colour</text>`;
    s+=`<text x="${x0+100}" y="546" font-family="Hind Vadodara" font-size="10.5" fill="${C.green}" opacity=".5">reversed</text>`;
    // idea text (wrapped manually)
    const words=c.idea.split(' '); let line='', lines=[];
    for(const word of words){ if((line+word).length>42){lines.push(line.trim()); line='';} line+=word+' '; }
    if(line.trim()) lines.push(line.trim());
    lines.forEach((l,i)=>{ s+=`<text x="${x0}" y="${600+i*24}" font-family="Hind Vadodara" font-size="15" fill="${C.green}" opacity=".85">${l}</text>`; });
    x0+=500;
  }
  // ---------- lockups row ----------
  s+=`<text x="64" y="740" font-family="Hind Vadodara" font-size="12" letter-spacing="1.8" fill="${C.green}" opacity=".6">LOCKUPS — MARK + WORDMARK</text>`;
  let y=770;
  for(const c of cols){
    const bb=MARKS[c.k].box;
    const markH=64, sc=markH/bb.h, markW=bb.w*sc;
    const wmSize=markH*0.92;
    const w=wordData(FRA,'Levia',wmSize,-wmSize*0.012);
    const gap=markH*0.40;
    s+=`<g transform="translate(64 ${y})"><g transform="translate(${-bb.x*sc} ${-bb.y*sc}) scale(${sc})">${MARKS[c.k].svg(C.green)}</g>`;
    s+=`<g transform="translate(${markW+gap-w.bb.x1} ${markH-w.bb.y2})">${word(FRA,'Levia',wmSize,C.green,-wmSize*0.012)}</g></g>`;
    s+=`<text x="64" y="${y+markH+26}" font-family="Hind Vadodara" font-size="11" fill="${C.green}" opacity=".5">${c.name}</text>`;
    y+=150;
  }
  // ---------- note ----------
  s+=`<text x="640" y="790" font-family="Hind Vadodara" font-size="14" fill="${C.green}" opacity=".8">All three are built from one stroke weight, round caps, no gradients.</text>`;
  s+=`<text x="640" y="816" font-family="Hind Vadodara" font-size="14" fill="${C.green}" opacity=".8">Each survives one colour; each avoids hearts, crosses, wheels, sticks and carts.</text>`;
  s+=`<text x="640" y="842" font-family="Hind Vadodara" font-size="14" fill="${C.green}" opacity=".8">Same palette and same wordmark throughout, so only the idea competes.</text>`;
  s+=`<rect x="640" y="880" width="880" height="1" fill="${C.green}" opacity=".15"/>`;
  s+=`<text x="640" y="920" font-family="Hind Vadodara" font-size="14" fill="${C.green}">Recommendation: A. It is the only one that states the two heights — the reason the product exists —</text>`;
  s+=`<text x="640" y="944" font-family="Hind Vadodara" font-size="14" fill="${C.green}">without drawing furniture. B is the most ownable but reads as a generic letter until explained.</text>`;
  s+=`<text x="640" y="968" font-family="Hind Vadodara" font-size="14" fill="${C.green}">C is the warmest but flattens to a pill at 16 px.</text>`;
  s+=`<text x="640" y="1030" font-family="Hind Vadodara" font-size="12" fill="${C.green}" opacity=".45">Grey-first on purpose: colour is tested later, on the direction you choose.</text>`;
  s+='</svg>';
  fs.writeFileSync('/home/user/logo-design-skill/levia/out/concepts.png',render(s,W));
  console.log('ok');
})();
