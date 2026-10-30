const fs = require('fs');
const G = require('/home/user/levia/build/geom.js');
const { ringFromCapsule, ringFromArc, ringFromRect, union, subtract, pathFromMulti, bbox } = G;
const W = 22;
// --- builders (all drawn in a 256 box, centred later) ---
function poly(points, w) { // stroked polyline, round joins/caps = union of capsules
  const rings = [];
  for (let i = 0; i < points.length - 1; i++) rings.push(ringFromCapsule(points[i][0], points[i][1], points[i+1][0], points[i+1][1], w));
  return union(rings);
}
function arcLine(cx, cy, r, w, a1, a2) { return union([ringFromArc(cx, cy, r, w, a1, a2)]); }
function add(...ms) { return union(ms.flat()); }

const marks = {};
// A: step / perch profiles at three riser angles
marks['A1_step45'] = () => poly([[56,72],[200,72]],W).concat ? null : add(poly([[56,72],[200,72]],W), poly([[56,184],[56,72]],W), poly([[56,184],[140,184]],W));
marks['A2_step60'] = () => add(poly([[64,72],[196,72]],W), poly([[64,72],[136,184]],W), poly([[136,184],[64,184]],W));
marks['A3_Z'] = () => add(poly([[56,72],[204,72]],W), poly([[204,72],[92,180]],W), poly([[92,180],[56,180]],W));
// B: S-ramp between two levels
function sramp(x1, y1, x2, y2, w, side = 1) { // horizontal start/end tangents
  const r = Math.abs(y2 - y1) / 2;
  const midY = (y1 + y2) / 2;
  const a = ringFromArc(x1 + r, midY, r, w, y1 < y2 ? 270 : 90, y1 < y2 ? 360 : 180);
  const b = ringFromArc(x2 - r, midY, r, w, y1 < y2 ? 180 : 0, y1 < y2 ? 270 : 90);
  return union([a, b]);
}
marks['B1_sramp_big'] = () => add(poly([[48,176],[60,176]],W), sramp(60,176,188,72,W), poly([[188,72],[208,72]],W));
marks['B2_sramp_wide'] = () => add(poly([[40,176],[56,176]],W), sramp(56,176,200,64,W), poly([[200,64],[216,64]],W));
marks['B3_sramp_narrow'] = () => add(poly([[76,168],[88,168]],W), sramp(88,168,168,88,W), poly([[168,88],[180,88]],W));
// C: deck + arch (bridge), arch springs from deck
marks['C1_arch'] = () => add(poly([[48,176],[208,176]],W), arcLine(128,176,80,W,180,360));
marks['C2_arch_wide'] = () => add(poly([[40,184],[216,184]],W), arcLine(128,184,88,W,180,360));
marks['C3_arch_open'] = () => add(poly([[40,184],[216,184]],W), arcLine(128,184,88,W,200,340));
// D: folded L profile
marks['D1_foldL'] = () => add(poly([[92,64],[92,176]],W), poly([[92,176],[180,176]],W), poly([[180,176],[180,112]],W));
marks['D2_foldL_low'] = () => add(poly([[84,56],[84,184]],W), poly([[84,184],[196,184]],W), poly([[196,184],[196,132]],W));
// E: tile with negative-space rests
marks['E1_tile2'] = () => subtract(union([ringFromRect(32,48,192,160,36)]), [ringFromRect(64,88,128,20,10), ringFromRect(64,150,80,20,10)]);
marks['E2_tile1'] = () => subtract(union([ringFromRect(32,48,192,160,36)]), [ringFromRect(64,116,128,24,12)]);
// F: continuous settle stroke — high bar, quarter arc down, low bar
marks['F1_settle'] = () => add(poly([[120,64],[208,64]],W), arcLine(120,152,88,W,180,270), poly([[56,152],[120,152]],W));
marks['F2_settle_short'] = () => add(poly([[136,72],[208,72]],W), arcLine(136,144,72,W,180,270), poly([[64,144],[136,144]],W));
// G: shelf + shadow (two bars, unequal)
marks['G1_bars'] = () => add(poly([[48,88],[208,88]],26), poly([[48,168],[136,168]],26));
marks['G2_bars_indent'] = () => add(poly([[64,96],[192,96]],26), poly([[64,168],[160,168]],26));
// H: fold down / hinge — bar with a folded tab under one end
marks['H1_hinge'] = () => add(poly([[56,96],[192,96]],W), poly([[192,96],[192,152]],W), poly([[56,160],[136,160]],18));
// I: the "levare" lift: low bar at left rising as a curve into a short high bar
marks['I1_lift'] = () => add(poly([[48,176],[104,176]],W), arcLine(104,112,64,W,90,180), poly([[168,112],[208,112]],W));

const names = Object.keys(marks);
const cols = 4, cell = 300;
let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${cols*cell}" height="${Math.ceil(names.length/cols)*cell}"><rect width="100%" height="100%" fill="#fff"/>`;
names.forEach((k, i) => {
  const x = (i % cols) * cell, y = Math.floor(i / cols) * cell;
  let m; try { m = marks[k](); } catch (e) { console.error('FAIL', k, e.message); return; }
  let bb; try { bb = bbox(m); } catch (e) { console.error('BADGEOM', k); return; }
  const s = Math.min(150 / Math.max(bb.w, bb.h), 3);
  const tx = x + cell/2 - (bb.x1 + bb.w/2) * s, ty = y + cell/2 - 10 - (bb.y1 + bb.h/2) * s;
  svg += `<g transform="translate(${tx} ${ty}) scale(${s})"><path d="${pathFromMulti(m)}" fill="#111"/></g>`;
  svg += `<text x="${x+16}" y="${y+cell-14}" font-family="HindVadodara" font-size="15" fill="#777">${k}</text>`;
});
fs.writeFileSync('/home/user/levia/src/sweep.svg', svg + '</svg>');
console.log('ok');
