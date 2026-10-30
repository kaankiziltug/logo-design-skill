const fs = require('fs');
const G = require('/home/user/levia/build/geom.js');
const { ringFromCapsule, ringFromArc, ringFromRect, circleRing, union, subtract, intersect, pathFromMulti, bbox } = G;
const W = 24;
function poly(points, w) { const r = []; for (let i = 0; i < points.length - 1; i++) r.push(ringFromCapsule(points[i][0], points[i][1], points[i+1][0], points[i+1][1], w)); return union(r); }
function arc(cx, cy, r, w, a1, a2) { return union([ringFromArc(cx, cy, r, w, a1, a2)]); }
function box(x, y, w, h, r) { return union([ringFromRect(x, y, w, h, r)]); }
function add(...ms) { return union(ms.flat().filter(Boolean)); }
function cut(a, ...bs) { return subtract(a, bs.flat().filter(Boolean)); }

const marks = {};
// --- letterform L family: L built as two rest planes, mitred or rounded fold ---
marks['L1_L_round'] = () => add(poly([[88,56],[88,188]],W), poly([[88,188],[196,188]],W));
marks['L2_L_tab'] = () => add(poly([[88,56],[88,188]],W), poly([[88,188],[196,188]],W), poly([[196,188],[196,140]],W));
marks['L3_L_asym'] = () => add(poly([[76,56],[76,180]],16), poly([[76,180],[200,180]],W), poly([[200,180],[200,150]],12));
// --- arch family ---
marks['M1_arch_alone'] = () => arc(128,184,72,W,180,360);
marks['M2_arch_bar'] = () => add(arc(128,184,72,W,180,360), poly([[40,184],[216,184]],W));
marks['M3_arch_over'] = () => add(arc(128,184,76,W,180,360), poly([[24,184],[232,184]],20));
marks['M4_arch_asym'] = () => add(arc(96,176,64,W,180,360), poly([[96,176],[232,176]],W));
marks['M5_arch_2legs'] = () => add(arc(128,152,64,W,180,360), poly([[64,152],[64,196]],W), poly([[192,152],[192,196]],W));
// --- arch + lower rest = two heights ---
marks['N1_arch_2levels'] = () => add(arc(96,152,56,W,180,360), poly([[96,152],[152,152]],W), poly([[152,152],[152,196]],W), poly([[64,196],[152,196]],W));
// --- fold: shallow V / chevron, the "fold seen from the front" ---
marks['P1_foldV'] = () => poly([[48,64],[128,176],[208,64]],W);
marks['P2_foldV_asym'] = () => poly([[48,72],[112,180],[208,72]],W);
marks['P3_foldV_deep'] = () => poly([[56,56],[128,200],[200,56]],W);
// --- the "pause": a line that dips and recovers ---
marks['Q1_cradle'] = () => add(poly([[40,104],[88,104]],W), arc(128,104,40,W,180,360), poly([[168,104],[216,104]],W));
marks['Q2_cradle_wide'] = () => add(poly([[32,96],[80,96]],W), arc(128,96,48,W,160,380), poly([[176,96],[224,96]],W));
// --- two planes at two heights, hinge on the left, rounded ---
marks['R1_hinge_step'] = () => add(poly([[56,84],[208,84]],W), poly([[56,84],[56,180]],W), poly([[56,180],[152,180]],W));
marks['R2_hinge_soft'] = () => add(arc(56,84,0.01,W,0,0), poly([[56,84],[208,84]],W), poly([[56,84],[56,180]],W), poly([[56,180],[152,180]],W));
// --- bracket: fold both ends (like the part itself) ---
marks['S1_bracket'] = () => add(poly([[48,168],[48,88],[208,88]],W), poly([[208,88],[208,120]],W));
marks['S2_bracket_tabs'] = () => add(poly([[48,176],[48,80],[208,80],[208,112]],W));
// --- seat profile, but reduced to a single wave ---
marks['T1_wave'] = () => add(arc(88,140,44,W,120,300), arc(168,140,44,W,300,120));
const names = Object.keys(marks);
const cols = 4, cell = 300;
let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${cols*cell}" height="${Math.ceil(names.length/cols)*cell}"><rect width="100%" height="100%" fill="#fff"/>`;
names.forEach((k, i) => {
  const x = (i % cols) * cell, y = Math.floor(i / cols) * cell;
  let m; try { m = marks[k](); } catch (e) { console.error('FAIL', k, e.message); return; }
  let bb; try { bb = bbox(m); } catch (e) { console.error('BADGEOM', k); return; }
  const s = Math.min(160 / Math.max(bb.w, bb.h), 3);
  const tx = x + cell/2 - (bb.x1 + bb.w/2) * s, ty = y + cell/2 - 12 - (bb.y1 + bb.h/2) * s;
  svg += `<g transform="translate(${tx} ${ty}) scale(${s})"><path d="${pathFromMulti(m)}" fill="#111"/></g>`;
  svg += `<text x="${x+14}" y="${y+cell-12}" font-family="HindVadodara" font-size="15" fill="#777">${k}</text>`;
});
fs.writeFileSync('/home/user/levia/src/sweep2.svg', svg + '</svg>');
console.log('ok');
