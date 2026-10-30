const fs = require('fs');
const L = require('/home/user/levia/build/lib.js');
const { MARKS, markSVG, wordmark, COL } = L;
const W = 1500, H = 1180;
let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<rect width="${W}" height="${H}" fill="#fff"/>`;
['A', 'B', 'C'].forEach((k, i) => {
  const y = 40 + i * 380;
  s += `<text x="50" y="${y + 20}" font-family="HindVadodara" font-size="17" fill="#888">${k}</text>`;
  // large mark
  s += markSVG(k, 40, y + 36, 210, '#111');
  // horizontal lockup: mark + wordmark
  const wmSize = 92;
  const wm = wordmark(wmSize, -1.2);
  const scale = 0.62;
  s += markSVG(k, 300, y + 30, 150, '#111');
  s += `<g transform="translate(470 ${y + 30 + 75 + (wm.bb.y1 + wm.bb.y2) / 2})"><path d="${wm.d}" fill="#111"/></g>`;
  // stacked lockup
  s += `<g transform="translate(760 ${y + 260})"><path d="${wm.d}" fill="#111" transform="scale(0.62) translate(${-wm.bb.x1} 0)"/></g>`;
  s += markSVG(k, 760, y + 40, 96, '#111');
  // sizes: exact 64 / 32 / 16, drawn as nested svg
  let x = 960;
  [64, 32, 16].forEach(n => { s += markSVG(k, x, y + 60, n, '#111'); s += `<text x="${x}" y="${y + 160}" font-family="HindVadodara" font-size="12" fill="#aaa">${n}</text>`; x += n + 40; });
});
fs.writeFileSync('/home/user/levia/src/compare.svg', s + '</svg>');
console.log('ok');
