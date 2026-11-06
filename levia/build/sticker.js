const fs=require('fs');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const g=require('/home/user/logo-design-skill/levia/build/geo.js');
const {word,wordData}=require('/home/user/logo-design-skill/levia/build/word.js');
const C={off:'#F2EFE9',green:'#3A4C40',sage:'#8BA892',terra:'#C4694A',acc:'#9E4A2C'};
const FRA='/home/user/fonts/static/F-o24-w500-s50.ttf';
const b64=b=>'data:image/png;base64,'+Buffer.from(b).toString('base64');
const FONTS=['/home/user/fonts/HindVadodara-Regular.ttf','/home/user/fonts/HindVadodara-Medium.ttf','/home/user/fonts/HindVadodara-SemiBold.ttf'];
function renderSvg(svg,w){ return new Resvg(svg,{fitTo:{mode:'width',value:w},font:{fontFiles:FONTS,loadSystemFonts:false,defaultFontFamily:'Hind Vadodara'}}).render().asPng(); }

// STICKER: 400 x 102 mm -> units 400 x 102
function stickerSvg(){
  const bb=g.inkBox(g.MASTER);
  const markH=54, sc=markH/bb.h, markW=bb.w*sc;
  const wm=wordData(FRA,'Levia',100,-1.0);
  const wmSize=66;
  const w=wordData(FRA,'Levia',wmSize,-wmSize*0.012);
  const wmW=w.bb.x2-w.bb.x1;
  const padL=26, gap=20;
  const totalW=padL+markW+gap+wmW+26;
  const y0=(102)/2;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 102" width="1200" height="306">
    <rect x="0" y="0" width="400" height="102" rx="6" fill="${C.off}"/>
    <g transform="translate(${padL-bb.x*sc} ${y0-markH/2-bb.y*sc}) scale(${sc})">${g.d(g.MASTER,C.green)}</g>
    <g transform="translate(${padL+markW+gap-w.bb.x1} ${y0+ (w.bb.y2-w.bb.y1)/2 - w.bb.y2})">${word(FRA,'Levia',wmSize,C.green,-wmSize*0.012)}</g>
  </svg>`;
}
// 180 x 46 mm minimum
function stickerSmallSvg(){
  const bb=g.inkBox(g.SMALL);
  const markH=30, sc=markH/bb.h, markW=bb.w*sc;
  const wmSize=34;
  const w=wordData(FRA,'Levia',wmSize,-wmSize*0.012);
  const wmW=w.bb.x2-w.bb.x1;
  const padL=13, gap=11;
  const y0=46/2;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 46" width="1080" height="276">
    <rect width="180" height="46" rx="3" fill="${C.off}"/>
    <g transform="translate(${padL-bb.x*sc} ${y0-markH/2-bb.y*sc}) scale(${sc})">${g.d(g.SMALL,C.green)}</g>
    <g transform="translate(${padL+markW+gap-w.bb.x1} ${y0+(w.bb.y2-w.bb.y1)/2-w.bb.y2})">${word(FRA,'Levia',wmSize,C.green,-wmSize*0.012)}</g>
  </svg>`;
}
fs.writeFileSync('/home/user/logo-design-skill/levia/logo/levia-sticker-400x102.svg',stickerSvg());
fs.writeFileSync('/home/user/logo-design-skill/levia/logo/levia-sticker-min-180x46.svg',stickerSmallSvg());

(async()=>{
  const st=renderSvg(stickerSvg(),1200);
  const stMin=renderSvg(stickerSmallSvg(),1080);
  fs.writeFileSync('/home/user/logo-design-skill/levia/out/sticker-400x102.png',st);
  // real-world scale factor: 1600px wide render of ~1.05m wide scene => 1 px ≈ 0.65 mm; sticker 400mm ≈ 610px
  const W=1600,H=880, bg='#E9E5DD';
  let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${bg}"/>
  <text x="60" y="52" font-family="Hind Vadodara" font-size="12" letter-spacing="1.8" fill="${C.green}" opacity=".6">APPLICATION TEST — FOLD-DOWN REST</text>
  <text x="60" y="86" font-family="Hind Vadodara" font-size="24" fill="${C.green}">Sticker on the rest panel</text>`;
  // ---- Panel A: handle + rest, front-on
  s+=`<text x="60" y="150" font-family="Hind Vadodara" font-size="11.5" fill="${C.green}" opacity=".55">FRONT ON — handle tube Ø 25 mm, rest panel 400 mm wide</text>`;
  // handle
  s+=`<rect x="60" y="180" width="880" height="22" rx="11" fill="${C.green}"/>`;
  // hinge brackets
  s+=`<rect x="300" y="202" width="26" height="18" fill="#C9C2B4"/><rect x="674" y="202" width="26" height="18" fill="#C9C2B4"/>`;
  // panel (with slight shadow)
  s+=`<rect x="300" y="220" width="400" height="102" rx="8" fill="#D6D0C3"/>`;
  s+=`<image x="300" y="220" width="400" height="102" href="${b64(st)}"/>`;
  // panel edge detail
  s+=`<rect x="300" y="220" width="400" height="102" rx="8" fill="none" stroke="#C6BFB1"/>`;
  s+=`<text x="60" y="360" font-family="Hind Vadodara" font-size="11.5" fill="${C.green}" opacity=".55">1:1 at 100% — mark 54 mm high, wordmark 66 pt-equivalent</text>`;
  // ---- Panel B: minimum size
  s+=`<text x="60" y="440" font-family="Hind Vadodara" font-size="11.5" fill="${C.green}" opacity=".55">MINIMUM — 180 × 46 mm, small cut of the mark</text>`;
  s+=`<rect x="60" y="460" width="180" height="46" rx="3" fill="#D6D0C3"/>`;
  s+=`<image x="60" y="460" width="180" height="46" href="${b64(stMin)}"/>`;
  s+=`<rect x="60" y="460" width="180" height="46" rx="3" fill="none" stroke="#C6BFB1"/>`;
  // ---- Panel C: standing distance, 1.2 m
  s+=`<text x="560" y="440" font-family="Hind Vadodara" font-size="11.5" fill="${C.green}" opacity=".55">AT 1.2 M — as a standing shopper sees it</text>`;
  s+=`<rect x="560" y="460" width="300" height="76" rx="6" fill="#D6D0C3"/>`;
  s+=`<image x="560" y="460" width="300" height="76.5" href="${b64(st)}"/>`;
  s+=`<rect x="560" y="460" width="300" height="76" rx="6" fill="none" stroke="#C6BFB1"/>`;
  // blurred version to simulate acuity at 1.2m (small)
  const small=await sharp(st).resize(150,38).blur(0.6).toBuffer();
  s+=`<text x="900" y="440" font-family="Hind Vadodara" font-size="11.5" fill="${C.green}" opacity=".55">ACUITY SIMULATION</text>`;
  s+=`<image x="900" y="452" width="150" height="38" href="${b64(small)}"/>`;
  s+=`<image x="900" y="500" width="75" height="19" href="${b64(await sharp(st).resize(75,19).blur(0.4).toBuffer())}"/>`;
  s+=`<text x="900" y="540" font-family="Hind Vadodara" font-size="10.5" fill="${C.green}" opacity=".45">100% and 50% scale, slight blur</text>`;
  // ---- notes
  const notes=[
    'The mark reads as two surfaces at two heights — a rest, not furniture clip-art.',
    'At 1.2 m the wordmark still holds; the mark alone carries the shape.',
    'Keep 8 mm clear around the sticker edge; never wrap text around the tube radius.',
    'Below 180 × 46 mm the lockup stops working — use the mark alone, no wordmark.',
  ];
  notes.forEach((n,i)=>{ s+=`<circle cx="66" cy="${620+i*36}" r="3.4" fill="${C.terra}"/><text x="84" y="${625+i*36}" font-family="Hind Vadodara" font-size="15" fill="${C.green}">${n}</text>`; });
  s+=`<text x="60" y="820" font-family="Hind Vadodara" font-size="11" fill="${C.green}" opacity=".4">Schematic mockup — dimensions indicative; confirm against the actual moulding and print process.</text>`;
  s+='</svg>';
  const out=renderSvg(s,W);
  fs.writeFileSync('/home/user/logo-design-skill/levia/out/sticker.png',out);
  console.log('ok');
})();
