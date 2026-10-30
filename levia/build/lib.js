// lib.js — shared helpers: mark definitions (256 box), SVG assembly, wordmark paths
const fs = require('fs');
const { textPath } = require('/home/user/levia/build/type2path.js');
const FR = {
  reg: '/home/user/fonts/static/F-w500-o60-s40-w0.ttf',
  semi: '/home/user/fonts/static/F-w600-o60-s40-w0.ttf',
};
const COL = { off: '#F2EFE9', green: '#3A4C40', sage: '#8BA892', terra: '#C4694A', textacc: '#9E4A2C' };

// ---- mark geometry: each is a list of stroked subpaths in a 256x256 box ----
const poly = (pts) => 'M' + pts.map(p => p.map(n => +n.toFixed(2)).join(' ')).join('L');
const arc = (cx, cy, r, a1, a2) => {
  const rad = a => a * Math.PI / 180;
  const p1 = [cx + r * Math.cos(rad(a1)), cy + r * Math.sin(rad(a1))];
  const p2 = [cx + r * Math.cos(rad(a2)), cy + r * Math.sin(rad(a2))];
  const large = Math.abs(a2 - a1) > 180 ? 1 : 0, sweep = a2 > a1 ? 1 : 0;
  return `M${p1[0].toFixed(2)} ${p1[1].toFixed(2)}A${r} ${r} 0 ${large} ${sweep} ${p2[0].toFixed(2)} ${p2[1].toFixed(2)}`;
};
const MARKS = {
  A: { strokes: [poly([[48, 86], [208, 86]]), poly([[208, 86], [208, 174], [112, 174]])], w: 28 },
  B: { strokes: [poly([[36, 178], [220, 178]]), arc(128, 178, 92, 180, 360)], w: 22 },
  C: { strokes: [poly([[104, 54], [104, 172]]), poly([[68, 172], [196, 172]]), poly([[196, 172], [196, 132]])], w: 28 },
};
// mark as an <svg> element placed at x,y with size (square box, mark is 256 box)
function markSVG(name, x, y, size, color, opts = {}) {
  const m = MARKS[name];
  const w = opts.w || m.w;
  const arts = m.strokes.map(d => `<path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  return `<svg x="${x}" y="${y}" width="${size}" height="${size}" viewBox="0 0 256 256" overflow="visible">${arts}</svg>`;
}
function markPath(name, color) { // for flat exports
  const m = MARKS[name];
  return m.strokes.map(d => `<path d="${d}" fill="none" stroke="${color}" stroke-width="${m.w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
}
// wordmark paths (outlined) — returns {d, bb}
function wordmark(size = 100, tracking = 0) { return textPath(FR.reg, 'Levia', size, tracking); }
module.exports = { MARKS, markSVG, markPath, poly, arc, wordmark, COL, FR };
