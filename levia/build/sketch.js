const fs = require('fs');
const { capsule, arcCapsule, circle, rrect } = require('/home/user/levia/build/shapes.js');
const W = 24;
const marks = {
  a1_twoRests: () => capsule(40,72,212,72,W) + capsule(40,168,116,168,W) + capsule(116,168,212,72,W),
  a2_mirror: () => capsule(44,72,216,72,W) + capsule(140,168,216,168,W) + capsule(44,72,140,168,W),
  a3_ribbon: () => capsule(52,60,204,60,W) + capsule(52,188,120,188,W) + arcCapsule(120,124,64,W,90,180) + capsule(120,60,204,60,W),
  b1_bridge: () => capsule(40,88,216,88,W) + arcCapsule(128,88,88,W,180,360),
  b2_sling: () => capsule(56,104,200,104,W) + arcCapsule(128,104,72,W,180,360),
  b3_settle: () => arcCapsule(120,196,108,W,180,270) + capsule(228,196,236,196,W),
  c1_foldedL: () => capsule(96,52,96,168,W) + capsule(96,168,180,168,W) + capsule(180,168,180,104,W),
  c2_mitre: () => capsule(88,44,88,168,W) + capsule(88,168,200,168,W) + capsule(200,168,200,116,W),
  d1_lever: () => capsule(40,92,216,92,W) + arcCapsule(128,132,62,W,240,300),
  d2_twinarcs: () => arcCapsule(128,152,88,W,180,360) + arcCapsule(128,190,52,W,196,344),
  e1_shelf: () => rrect(44,64,168,52,26) + capsule(44,172,124,172,20),
  e2_pair: () => rrect(56,56,120,44,22) + rrect(56,130,144,44,22),
};
const cells = Object.entries(marks);
const cols = 4, cell = 300, pad = 34;
let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${cols*cell}" height="${Math.ceil(cells.length/cols)*cell}" viewBox="0 0 ${cols*cell} ${Math.ceil(cells.length/cols)*cell}">
<rect width="100%" height="100%" fill="#fff"/>`;
cells.forEach(([k, fn], i) => {
  const x = (i % cols) * cell, y = Math.floor(i / cols) * cell;
  svg += `<g transform="translate(${x+pad} ${y+pad})"><path d="${fn()}" fill="#111"/></g>`;
  svg += `<text x="${x+pad}" y="${y+cell-16}" font-family="HindVadodara" font-size="16" fill="#777">${k}</text>`;
});
svg += `</svg>`;
fs.writeFileSync('/home/user/levia/src/sketch.svg', svg);
console.log('ok');
