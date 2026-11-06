// geom.js — build logo artwork from exact primitives with boolean union, output a single clean path.
const pc = require('/home/user/.renderenv/node_modules/polygon-clipping');
const R = (n) => Math.round(n * 100) / 100;
const P = (a) => [R(a[0]), R(a[1])];

// --- primitives as polygon rings ---
function ringFromCapsule(x1, y1, x2, y2, w, n = 18) {
  const h = w / 2, dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1e-9;
  const ux = dx / L, uy = dy / L, nx = -uy, ny = ux, base = Math.atan2(uy, ux);
  const pts = [];
  for (let i = 0; i <= n; i++) { const a = base - Math.PI / 2 + (Math.PI * i) / n; pts.push(P([x2 + h * Math.cos(a), y2 + h * Math.sin(a)])); }
  for (let i = 0; i <= n; i++) { const a = base + Math.PI / 2 + (Math.PI * i) / n; pts.push(P([x1 + h * Math.cos(a), y1 + h * Math.sin(a)])); }
  return pts;
}
// arc capsule ring: centre cx,cy, centreline radius r, width w, angles in degrees (screen coords)
function ringFromArc(cx, cy, r, w, a1, a2, n = 40) {
  const h = w / 2, ro = r + h, ri = r - h;
  const rad = (a) => (a * Math.PI) / 180;
  const sweep = a2 - a1;
  const pts = [];
  for (let i = 0; i <= n; i++) { const a = a1 + (sweep * i) / n; pts.push(P([cx + ro * Math.cos(rad(a)), cy + ro * Math.sin(rad(a))])); }
  const ae = rad(a2);
  for (let i = 0; i <= 12; i++) { // end cap around centre point at a2
    const c = [cx + r * Math.cos(ae), cy + r * Math.sin(ae)];
    const a = (sweep > 0 ? -90 : 90) + ae * 180 / Math.PI + (sweep > 0 ? 1 : -1) * (180 * i / 12);
    pts.push(P([c[0] + h * Math.cos(a * Math.PI / 180), c[1] + h * Math.sin(a * Math.PI / 180)]));
  }
  for (let i = 0; i <= n; i++) { const a = a2 - (sweep * i) / n; pts.push(P([cx + ri * Math.cos(rad(a)), cy + ri * Math.sin(rad(a))])); }
  const as = rad(a1);
  for (let i = 0; i <= 12; i++) {
    const c = [cx + r * Math.cos(as), cy + r * Math.sin(as)];
    const a = (sweep > 0 ? 90 : -90) + as * 180 / Math.PI + (sweep > 0 ? -1 : 1) * (180 * i / 12);
    pts.push(P([c[0] + h * Math.cos(a * Math.PI / 180), c[1] + h * Math.sin(a * Math.PI / 180)]));
  }
  return pts;
}
function ringFromRect(x, y, w, h, rad = 0, steps = 10) {
  if (!rad) return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(P);
  const pts = [];
  const corners = [[x + w - rad, y + rad, -90], [x + w - rad, y + h - rad, 0], [x + rad, y + h - rad, 90], [x + rad, y + rad, 180]];
  for (const [cx, cy, a0] of corners) for (let i = 0; i <= steps; i++) { const a = (a0 + (90 * i) / steps) * Math.PI / 180; pts.push(P([cx + rad * Math.cos(a), cy + rad * Math.sin(a)])); }
  return pts;
}
function circleRing(cx, cy, r, n = 60) { const pts = []; for (let i = 0; i < n; i++) { const a = (2 * Math.PI * i) / n; pts.push(P([cx + r * Math.cos(a), cy + r * Math.sin(a)])); } return pts; }

// --- boolean ops ---
function toMulti(g) {
  if (!Array.isArray(g) || !g.length) return [];
  const d = (a) => (Array.isArray(a) ? 1 + d(a[0]) : 0);
  const depth = d(g);
  if (depth === 2) return [[g]];            // ring
  if (depth === 3) return [g];              // polygon
  if (depth === 4) return g;                // multipolygon
  throw new Error('bad geometry depth ' + depth);
}
function union(list) {
  const ins = list.map(toMulti).filter(m => m.length);
  const flat = ins.flat();
  if (ins.length === 1) return ins[0];
  return pc.union(...ins.map(m => m));
}
function subtract(a, b) {
  const A = toMulti(a); const B = (b || []).map(toMulti).filter(m => m.length);
  if (!B.length) return A;
  return pc.difference(A, B.flat());
}
function intersect(a, b) { return pc.intersection(toMulti(a), toMulti(b)); }

// --- output: rounded path (polygon → path with slight corner rounding via quadratic) ---
function pathFromMulti(multipoly, { smooth = true } = {}) {
  let d = '';
  for (const poly of multipoly) for (const ring of poly) {
    if (!ring.length) continue;
    d += ringToPath(ring, smooth) + ' ';
  }
  return d.trim();
}
function ringToPath(ring, smooth) {
  const pts = ring.slice(0, ring.length - 1).length > 2 && Math.abs(ring[0][0] - ring[ring.length-1][0]) < 1e-9 && Math.abs(ring[0][1] - ring[ring.length-1][1]) < 1e-9 ? ring.slice(0, -1) : ring.slice();
  if (!smooth) return 'M' + pts.map(p => `${R(p[0])} ${R(p[1])}`).join('L') + 'Z';
  // quadratic smoothing: midpoints + control points (Chaikin-like but keeps curve fidelity)
  const n = pts.length; let d = '';
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  const m0 = mid(pts[n - 1], pts[0]);
  d += `M${R(m0[0])} ${R(m0[1])}`;
  for (let i = 0; i < n; i++) {
    const p = pts[i], m = mid(p, pts[(i + 1) % n]);
    d += `Q${R(p[0])} ${R(p[1])} ${R(m[0])} ${R(m[1])}`;
  }
  return d + 'Z';
}
// bbox
function bbox(multipoly) {
  let x1 = 1e9, y1 = 1e9, x2 = -1e9, y2 = -1e9;
  for (const poly of multipoly) for (const ring of poly) for (const [x, y] of ring) { x1 = Math.min(x1, x); y1 = Math.min(y1, y); x2 = Math.max(x2, x); y2 = Math.max(y2, y); }
  return { x1, y1, x2, y2, w: x2 - x1, h: y2 - y1 };
}
module.exports = { ringFromCapsule, ringFromArc, ringFromRect, circleRing, union, subtract, intersect, pathFromMulti, bbox, toMulti };
