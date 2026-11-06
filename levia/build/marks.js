// Three directions, each defined as one stroked polyline (round cap/join) on a 256 box.
const S = 256;
const DIRS = {
  // A — "Two Rests": a folded section. Deck at lean height, riser, lower perch. The deck overhangs the fold.
  A: { w: 26, pts: [[52, 92], [204, 92], [204, 176], [110, 176]] },
  // B — "Shelter": a shallow segmental arch landing on a long deck.
  B: { w: 22, deck: { y: 178, x1: 34, x2: 222 }, arch: { cx: 128, cy: 262, r: 118, a1: 209, a2: 331 } },
  // C — "The Folded L": monogram L whose foot runs both ways — short hinge tab left, long rest right.
  C: { w: 30, pts: [[128, 56], [128, 172], [72, 172], [206, 172]] },
};
module.exports = DIRS;
