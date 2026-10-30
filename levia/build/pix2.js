const fs=require('fs');
const {G}=require('/home/user/levia/build/marks2.js');
const {Resvg}=require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const sharp=require('/home/user/.renderenv/node_modules/sharp');
const fdir='/home/user/fonts';
const fonts=[fdir+'/static/F-o24-w500-s50.ttf',fdir+'/static/F-w500-o60-s40-w0.ttf',fdir+'/HindVadodara-Regular.ttf',fdir+'/HindVadodara-Medium.ttf'];
function svgFor(d,w,color='#3A4C40'){ // 256 box, no padding
  return `<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><path d="${d}" fill="${color}"/></svg>`;
}
async function renderMark(d,w,px){
  const r=new Resvg(svgFor(d,w),{fitTo:{mode:'width',value:px},background:'rgba(0,0,0,0)'});
  return await sharp(r.render().asPng()).png().toBuffer();
}
(async()=>{
  const sizes=[64,32,16];
  const tiles=[];
  const labelH=26, zoom=6, bg='#F2EFE9';
  for (const [key,label] of [['fold','Master (28/256)'],['foldSmall','Small cut (40/256)']]){
    const m=G[key];
    for (const s of sizes){
      const png=await renderMark(m.d(m.w),m.w,s);
      // true size on a light tile
      const trueTile=await sharp({create:{width:Math.max(s,88),height:Math.max(s,88),channels:4,background:bg}})
        .composite([{input:png,left:Math.floor((Math.max(s,88)-s)/2),top:Math.floor((Math.max(s,88)-s)/2)}]).png().toBuffer();
      // pixel zoom
      const zoomTile=await sharp(png).resize(s*zoom,s*zoom,{kernel:'nearest'}).toBuffer();
      tiles.push({key,label,s,trueTile,zoomTile});
    }
  }
  // compose: rows = variant, cols = size
  const cellW=260, cellH=260, rowsList=['Master (28/256)','Small cut (40/256)'];
  let composites=[]; let y=0;
  const header=await sharp({create:{width:cellW*3+40,height:50,channels:4,background:bg}}).png().toBuffer();
  composites.push({input:header,left:0,top:0}); y=50;
  for(const lab of rowsList){
    const rowTiles=tiles.filter(t=>t.label===lab);
    let x=20;
    for(const t of rowTiles){
      composites.push({input:t.zoomTile,left:x,top:y+10});
      x+=cellW;
    }
    y+=cellH;
    // true-size row
    x=20;
    for(const t of rowTiles){
      composites.push({input:t.trueTile,left:x,top:y+10});
      x+=cellW;
    }
    y+=120;
  }
  const out=await sharp({create:{width:cellW*3+40,height:y+20,channels:4,background:bg}}).composite(composites).png().toBuffer();
  fs.writeFileSync('/home/user/levia/out/pix2.png',out);
  console.log('ok', out.length);
})();
