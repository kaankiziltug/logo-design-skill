// sheet.js — build a variant sheet: large mark + 64/32/16 + hint
const fs = require('fs');
const { textPath } = require('/home/user/levia/build/type2path.js');
const FRA = '/home/user/fonts/static/F-w500-o60-s40-w0.ttf';

const variants = [
  // A family: section profiles (stroked polylines)
  { id: 'A1', w: 26, paths: [[[52,92],[204,92]], [[204,92],[204,176]], [[204,176],[110,176]]] },
  { id: 'A2', w: 26, paths: [[[52,92],[204,92]], [[150,92],[150,176]], [[92,176],[150,176]]] },
  { id: 'A3', w: 26, paths: [[[56,84],[200,84]], [[200,84],[200,172],[104,172]]] },
  { id: 'A4', w: 22, paths: [[[44,88],[212,88]], [[128,88],[128,180]], [[76,180],[180,180]]] },
  // B family: shallow segmental arch + deck (built with arc commands)
  { id: 'B1', w: 22, paths: [['M34 178H222'], shallowArc(128, 262, 118, 209, 331)] },
  { id: 'B2', w: 22, paths: [['M34 186H222'], shallowArc(128, 268, 112, 208, 332)] },
  { id: 'B3', w: 24, paths: [['M40 180H216'], arcPath(128, 180, 74, 180, 360)] },
  // C family: monogram L (hinge tab)
  { id: 'C1', w: 30, paths: [['M104 56V172'], ['M72 172H208']] },
  { id: 'C2', w: 26, paths: [['M100 52V176'], ['M60 176H212']] },
];
function arcPath(cx, cy, r, a1, a2) {
  const rad = a => a * Math.PI / 180;
  const p1 = [cx + r * Math.cos(rad(a1)), cy + r * Math.sin(rad(a1))];
  const p2 = [cx + r * Math.cos(rad(a2)), cy + r * Math.sin(rad(a2))];
  const large = Math.abs(a2 - a1) > 180 ? 1 : 0, sweep = a2 > a1 ? 1 : 0;
  return `M${p1[0].toFixed(2)} ${p1[1].toFixed(2)}A${r} ${r} 0 ${large} ${sweep} ${p2[0].toFixed(2)} ${p2[1].toFixed(2)}`;
}
function shallowArc(cx, cy, r, a1, a2) { return arcPath(cx, cy, r, a1, a2); }

const rows = 3, cell = 330, pad = 24;
let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${Math.ceil(variants.length/rows)*cell}" height="${rows*cell+60}"><rect width="100%" height="100%" fill="#fff"/>`;
variants.forEach((v, i) => {
  const x = Math.floor(i / rows) * cell, y = (i % rows) * cell;
  const base = `fill="none" stroke="#111" stroke-width="${v.w}" stroke-linecap="round" stroke-linejoin="round"`;
  svg += `<g transform="translate(${x+pad} ${y+pad}) scale(0.62)">` + v.paths.map(p => `<path d="${Array.isArray(p[0]) ? 'M' + p.map(q => q.join(' ')).join('L') : p}" ${base}/>`).join('') + `</g>`;
  // true sizes
  [64, 32, 16].forEach((s, j) => {
    const sc = s / 256 * 1.55;
    const bx = x + pad + 210 + j * 40, by = y + pad + 30;
    svg += `<g transform="translate(${bx} ${by}) scale(${sc})">` + v.paths.map(p => `<path d="${Array.isArray(p[0]) ? 'M' + p.map(q => q.join(' ')).join('L') : p}" ${base}/>`).join('') + `</g>`;
    svg += `<text x="${bx}" y="${by + 130}" font-family="HindVadodara" font-size="12" fill="#999">${s}</text>`;
  });
  svg += `<text x="${x+pad}" y="${y+cell-20}" font-family="HindVadodara" font-size="18" fill="#555">${v.id}</text>`;
});
fs.writeFileSync('/home/user/levia/src/sheet.svg', svg + '</svg>');
console.log('ok');
