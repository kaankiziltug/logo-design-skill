// Exact primitive path builders: capsules (round-capped bars) and arc capsules.
const R = (n) => Math.round(n * 100) / 100;
const P = (p) => `${R(p[0])} ${R(p[1])}`;
function capsule(x1, y1, x2, y2, w) {
  const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy);
  const ux = dx / L, uy = dy / L, nx = -uy, ny = ux, h = w / 2;
  const a = [x1 + nx * h, y1 + ny * h], b = [x2 + nx * h, y2 + ny * h];
  const c = [x2 - nx * h, y2 - ny * h], d = [x1 - nx * h, y1 - ny * h];
  return `M${P(a)}L${P(b)}A${R(h)} ${R(h)} 0 0 0 ${P(c)}L${P(d)}A${R(h)} ${R(h)} 0 0 0 ${P(a)}Z`;
}
// arc capsule: centre (cx,cy), radius r (centreline), width w, from angle a1 to a2 (deg, screen coords, 0=east, 90=south)
function arcCapsule(cx, cy, r, w, a1, a2) {
  const h = w / 2, ro = r + h, ri = r - h;
  const rad = (a) => (a * Math.PI) / 180;
  const pt = (rr, a) => [cx + rr * Math.cos(rad(a)), cy + rr * Math.sin(rad(a))];
  const sweep = a2 - a1;
  const large = Math.abs(sweep) > 180 ? 1 : 0;
  const s = sweep > 0 ? 1 : 0;
  const o1 = pt(ro, a1), o2 = pt(ro, a2), i1 = pt(ri, a1), i2 = pt(ri, a2);
  return `M${P(o1)}A${R(ro)} ${R(ro)} 0 ${large} ${s} ${P(o2)}A${R(h)} ${R(h)} 0 0 ${s} ${P(i2)}A${R(ri)} ${R(ri)} 0 ${large} ${1 - s} ${P(i1)}A${R(h)} ${R(h)} 0 0 ${s} ${P(o1)}Z`;
}
function circle(cx, cy, r) { return `M${R(cx - r)} ${R(cy)}a${R(r)} ${R(r)} 0 1 0 ${R(2 * r)} 0a${R(r)} ${R(r)} 0 1 0 ${R(-2 * r)} 0Z`; }
function rrect(x, y, w, h, r) {
  return `M${R(x + r)} ${R(y)}H${R(x + w - r)}A${R(r)} ${R(r)} 0 0 1 ${R(x + w)} ${R(y + r)}V${R(y + h - r)}A${R(r)} ${R(r)} 0 0 1 ${R(x + w - r)} ${R(y + h)}H${R(x + r)}A${R(r)} ${R(r)} 0 0 1 ${R(x)} ${R(y + h - r)}V${R(y + r)}A${R(r)} ${R(r)} 0 0 1 ${R(x + r)} ${R(y)}Z`;
}
module.exports = { capsule, arcCapsule, circle, rrect };
