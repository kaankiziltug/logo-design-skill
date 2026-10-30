# Levia — exploration logo system

**Not final. Not for production.** Two existing uses of the name are on record in India
(Levia Technologies, kiosks; PMI's LEVIA, a non-tobacco product). Clearance and a
professional trademark search must be completed before any commercial use.

Exploration concepts only. The masters here are geometrically exact but were built as
proofs of an idea; the final mark must be redrawn and optically corrected by a human
designer in Figma or Inkscape.

---

## The direction: A — The Fold

A section through the rest at both heights: the upper deck (lean), the fold, the lower
perch. One stroke weight, round caps, nothing else.

- **Why it fits:** the product's whole proposition is two heights on one hinge. The mark
  states that in a single continuous shape without drawing furniture, a seat, a cart, a
  person or a body part.
- **Mark type:** abstract-geometric symbol, readable as a plan/section detail.
- **Not used:** hearts, crosses, pills, wheels, sticks, carts, kiosks, touchscreens.

---

## Geometry — master symbol

Canvas `256 × 256`. All three bars are **capsules**: a rounded rectangle with radius equal
to half the stroke, i.e. a stroked round-capped line. Draw each as a stroked path with
`stroke-width: 28`, `stroke-linecap: round`, `stroke-linejoin: round`.

| Part | From (x y) | To (x y) | Stroke | Note |
|---|---|---|---|---|
| Deck (upper rest) | 40, 88 | 216, 88 | 28 | 8 units overhangs past the riser, right |
| Riser (the fold) | 168, 88 | 168, 178 | 28 | 90° to the deck |
| Perch (lower rest) | 168, 178 | 96, 178 | 28 | 20 units short of the deck's left end |

Ink bounding box: `x 26 y 74 w 204 h 118` → **aspect 1.73 : 1**.
Angles: 0° and 90° only. Stroke : ink-height ratio = 28 : 118 = **0.237**.
Gap between the deck's underside and the perch's top = 178 − 88 − 28 = **62 units**, i.e.
2.2 × stroke — this is the "notch" and it is the measure that decides small-size legibility.

### Small cut (for 24 px and below)

Same three-part construction, retuned, not scaled:

| Part | From | To | Stroke |
|---|---|---|---|
| Deck | 62, 74 | 210, 74 | 44 |
| Riser | 158, 74 | 158, 186 | 44 |
| Perch | 158, 186 | 116, 186 | 44 |

Ink box `x 40 y 52 w 192 h 156`; stroke : height = 44 : 156 = **0.28**; notch = 68 units
= 1.55 × stroke. Fatter and squarer on purpose so the step survives rasterisation.

---

## Files

```
logo/
  levia-symbol.svg                      mark, dark green, tight ink canvas
  levia-symbol-small.svg                small cut, dark green
  levia-symbol-square.svg               mark reversed on off-white tile
  levia-symbol-onecolour.svg            mark, #000000 only
  levia-wordmark.svg                    outlined wordmark, dark green
  levia-wordmark-reversed.svg           outlined wordmark, off-white
  levia-lockup-horizontal.svg           mark + wordmark
  levia-lockup-stacked.svg              mark over wordmark
  levia-lockup-horizontal-reversed.svg  lockup, off-white
  levia-sticker-400x102.svg             rest-panel sticker, 400 × 102 mm
  levia-sticker-min-180x46.svg          minimum sticker, 180 × 46 mm
out/
  concepts.png        three directions, one colour, true sizes
  sheet-tests.png     symbol, wordmark, lockups, colour tests
  pixel-test.png      16 / 32 / 64 px with 8× pixel zoom + what breaks
  sticker.png         sticker on the rest panel, front-on + 1.2 m + acuity
build/                geometry + render scripts (node, resvg, sharp)
src/, explorations/   working SVGs
```

---

## Wordmark

**Fraunces**, variable, instance at `wght 500 · opsz 24 · SOFT 50 · WONK 0`, tracking
−1.2 % (−1.0 at 100 units), outlines only. Fraunces is SIL Open Font Licence 1.1 —
commercially usable, including logos. No letters have been modified: Fraunces' *L*
already has a lifted foot serif that rhymes with the mark's fold, and the *a* and *i* keep
a warm, humanist rhythm. If you redraw, preserve that foot — it is doing the work of
linking mark to word.

Supporting text: **Hind Vadodara** (SIL OFL 1.1), Regular / Medium / SemiBold.

Lockup ratios (horizontal): mark height 1.00 (cap height of the wordmark = 0.92 em),
optical gap = **0.40 × mark height**, wordmark baseline sits on the mark's baseline.
Stacked: gap = 0.34 × mark height, both centred.

---

## Colour

| Role | HEX | On off-white | Note |
|---|---|---|---|
| Background | `#F2EFE9` | — | main field |
| Mark and text | `#3A4C40` | **8.00 : 1** | passes AAA for any size |
| Sage | `#8BA892` | 2.26 : 1 | shapes and support only — never text |
| Terracotta | `#C4694A` | 3.35 : 1 | accent shapes and icons — never body text |
| Text accent | `#9E4A2C` | 5.27 : 1 | only when terracotta words are needed on off-white |

Reversed: `#F2EFE9` on `#3A4C40` = 8.00 : 1. Do not set terracotta or the text accent on
dark green — 2.39 : 1 and 1.52 : 1 respectively.

---

## Test results

| Test | Master (28/256) | Small cut (44/256) |
|---|---|---|
| 64 px | Clean. Caps read as round; both levels and the overhang legible. | Slightly heavy but correct. Use master at this size. |
| 32 px | Holds. Notch = 2.2 × stroke survives; overhang still reads. | Works; heavier than needed. |
| 16 px | **Fails.** Notch lands on ~1.75 px and greys out; the mark reads as one blob with a tail. | **Passes.** Step and notch both survive 16 px rasterisation. |
| One colour, black | Passes — no detail depends on colour. | Passes. |
| Reversed | Passes; no thinning needed (stroke is on the dark side of medium). | Passes. |
| Mirror / 180° | No hidden reading found. The mirrored form is also plausible as a section, so it is not a lock — but nothing offensive appears. | Same. |
| Grey / squint | Silhouette reads as a step, not as furniture. | Reads as a step slightly earlier. |

**Verification method:** each size was rendered by resvg at *exact* pixel width from the
same SVG, then enlarged with nearest-neighbour for inspection. Tests were run on Linux
(Freetype/resvg); the rasteriser on the final print or signage job will differ and must be
re-tested.

**What breaks, and the rules that follow**

1. The notch between the deck and the lower arm is the first casualty; below 24 px it
   closes. Threshold: keep the notch ≥ 1.5 × stroke.
2. Round caps lose their radius below ~24 px and the shape reads hard-edged. Acceptable —
   the two levels are the idea, not the softness.
3. Under ~14 % overhang past the riser the mark collapses into a plain *T*. Do not shorten
   the deck when adapting.
4. Never downscale the master to 16 px. Swap to the small cut at 24 px and below; below
   40 px total lockup width, drop the wordmark and use the mark alone.

---

## Sticker test — fold-down rest

Two production sizes checked: **400 × 102 mm** (panel face) and **180 × 46 mm** (minimum).

| Criterion | Reading |
|---|---|
| Legibility at 1.2 m standing distance | Wordmark holds comfortably; the mark's step is still identifiable. |
| At 2 m (approach) | Wordmark softens to a shape; the mark still reads as a folded surface. |
| Placement | Flat on the panel face, 8 mm clear inside the edge. Never wrap across the tube radius (Ø 25 mm) — the stroke would foreshorten and the notch would pinch. |
| Below minimum | The lockup stops working under 180 × 46 mm; set the mark alone. |
| Material | One-colour on matte vinyl or in-mould label. The mark needs no white keyline; the off-white field does the separating. |

Caveat: the mockup is a schematic. Confirm against the actual moulding, the print process,
and the viewing distance in a real aisle, not on a desk.

---

## Risks to clear before use

1. **Levia Technologies (India, kiosks)** — same name, adjacent retail environment. The
   mark must never resemble a screen, bezel, kiosk or interface. This mark does not, but
   the *name* is the conflict, not the symbol.
2. **PMI's LEVIA** — check the class and the device. Nothing here is a stick, rod, plume or
   flame; the mark is horizontal bars only. Keep it that way. Avoid any future version
   where the riser thins into a stem.
3. **Medical reading** — no cross, no heart, no pill, no pulse. The `#3A4C40` green could
   drift clinical; keep sage and terracotta in supporting shapes so the system does not
   read hospital-green.
4. **Furniture / signage** — at large sizes the mark could read as a bracket or shelf
   fixing. The rounded caps and the unequal overhangs are what stop that; do not square
   the caps.
5. **Generic-step risk** — a step is a common abstract motif (stairs, growth, progress).
   Distinctiveness here rests on the *unequal* overhangs and the weighted proportions, so
   a trademark search should include step/chevron marks in the furniture and retail classes.
6. **Fraunces** — OFL allows commercial logo use and embedding. Keep the licence file with
   the delivered outlines. If you alter the wordmark, it is no longer Fraunces and must be
   named as a custom lettering.

---

## Handover

- All marks are outlines. No live text, no rasters, no gradients, no filters.
- Geometric primitives are exact (capsules at 0°/90°); the small cut is retuned, not scaled.
- The final mark must be redrawn by a designer: confirm the optical centring in the lockups,
  the exact baseline relationship, and run the 16 px test again on the target rasteriser.
- Not delivered yet: CMYK/Pantone conversion, embroidery/etch artwork, motion, and the
  wider identity system. Those follow once a direction is chosen and cleared.
