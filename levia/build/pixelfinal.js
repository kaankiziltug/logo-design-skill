const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const C={off:'#F2EFE9',green:'#3A4C40',terra:'#C4694A'};
const b64=b=>'data:image/png;base64,'+Buffer.from(b).toString('base64');
function svgOf(s,color){const bb=g.inkBox(s);const m=Math.max(bb.w,bb.h);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${bb.x-(m-bb.w)/2} ${bb.y-(m-bb.h)/2} ${m} ${m}" width="256" height="256">${g.d(s,color)}</svg>`;}
async function px(spec,size){const r=new Resvg(svgOf(spec,C.green),{fitTo:{mode:'width',value:size},background:'rgba(0,0,0,0)'});return r.render().asPng();}
(async()=>{
  const W=1600,H=1020;
  let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${C.off}"/>
  <text x="56" y="46" font-family="Hind Vadodara" font-size="12" letter-spacing="1.8" fill="${C.green}" opacity=".6">SIZE TEST — RENDERED AT EXACT PIXEL SIZE, THEN ENLARGED 8× (NEAREST NEIGHBOUR)</text>
  <text x="56" y="80" font-family="Hind Vadodara" font-size="23" fill="${C.green}">The master holds to 32 px; below that use the small cut</text>`;
  const COLS=[{size:64,x:56,z:4},{size:32,x:420,z:6},{size:16,x:700,z:8}];
  const rows=[
    {label:'Master — stroke 28/256', spec:g.MASTER, y:130},
    {label:'Small cut — stroke 44/256 · arms closer · shorter deck', spec:g.SMALL, y:520},
  ];
  for(const r of rows){
    s+=`<text x="56" y="${r.y}" font-family="Hind Vadodara" font-size="13" fill="${C.green}">${r.label}</text>`;
    for(const c of COLS){
      const b=await px(r.spec,c.size);
      const z=await sharp(b).resize(c.size*c.z,c.size*c.z,{kernel:'nearest'}).png().toBuffer();
      s+=`<image x="${c.x}" y="${r.y+16}" width="${c.size*c.z}" height="${c.size*c.z}" href="${b64(z)}" image-rendering="pixelated"/>`;
      s+=`<text x="${c.x}" y="${r.y+16+c.size*c.z+18}" font-family="Hind Vadodara" font-size="11" fill="${C.green}" opacity=".55">${c.size} px · ${c.z}× zoom</text>`;
      s+=`<image x="${c.x+c.size*c.z+16}" y="${r.y+16}" width="${c.size}" height="${c.size}" href="${b64(b)}"/>`;
      s+=`<text x="${c.x+c.size*c.z+16}" y="${r.y+16+c.size+18}" font-family="Hind Vadodara" font-size="10.5" fill="${C.green}" opacity=".4">true size</text>`;
    }
  }
  const y=880;
  s+=`<text x="56" y="${y}" font-family="Hind Vadodara" font-size="12" letter-spacing="1.6" fill="${C.terra}">WHAT BREAKS AT SMALL SIZES</text>`;
  const brk=[
    'The notch between deck and lower arm goes first: at 16 px the master’s 28-unit gap lands on 1.75 px and greys into one blob.',
    'Rounded caps lose their radius below 24 px and the mark reads hard-edged — acceptable, as long as the two levels survive.',
    'Keep at least 14 % of the deck width overhanging past the riser, or the shape collapses into a plain T.',
    'Never scale the master down to 16 px. Swap to the small cut at 24 px and below; below 40 px total width, drop the wordmark.',
  ];
  brk.forEach((t,i)=>{ s+=`<circle cx="62" cy="${y+30+i*28}" r="3.2" fill="${C.terra}"/><text x="80" y="${y+35+i*28}" font-family="Hind Vadodara" font-size="14" fill="${C.green}" opacity=".85">${t}</text>`; });
  s+='</svg>';
  fs.writeFileSync('/home/user/logo-design-skill/levia/src/pixel-test.svg',s);
  const out=new Resvg(s,{fitTo:{mode:'width',value:W},font:{fontFiles:['/home/user/fonts/HindVadodara-Regular.ttf','/home/user/fonts/HindVadodara-Medium.ttf'],loadSystemFonts:false,defaultFontFamily:'Hind Vadodara'}}).render().asPng();
  fs.writeFileSync('/home/user/logo-design-skill/levia/out/pixel-test.png',out);
  console.log('ok');
})();
