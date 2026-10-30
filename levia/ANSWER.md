# Levia — exploration logo system

> **Not final.** Two existing uses of the name are on record in India — Levia Technologies (kiosks) and PMI's LEVIA (non-tobacco). **Clearance and a professional trademark search must happen before any commercial use.** These are exploration concepts; the final mark must be redrawn by a human designer.

## The brief in one line
A calm, dignified rest on a trolley, at two heights, for tired shoppers who must never feel like patients. So: no body, no seat, no cart, no cross, no stick.

## Three directions

| | Direction | One-line rationale |
|---|---|---|
| **A** ★ | **The Fold** — a section through the rest: upper deck, fold, lower perch | States the product's actual proposition — two heights on one hinge — without drawing furniture or a person. |
| **B** | **The L** — the *L* of Levia with its foot folded up into a tab | Turns the initial into the mechanism: a monogram that behaves like the product, so the name and the object are one shape. |
| **C** | **The Keep** — a soft rounded pad holding one rest-line in negative space | Warmest of the three: a bench softened nearly to abstraction, for shoppers who should read comfort, not equipment. |

**Recommended: A.** It is the only one whose shape carries information a competitor's mark cannot copy — the unequal overhangs are the *two heights*. B is more ownable but reads as a generic letter until someone explains it, which is a cost paid on every first encounter. C is the friendliest but flattens into a pill at 16 px.

---

## Direction A — the system

### Symbol
Three capsules — round-capped bars — one stroke weight, only 0° and 90°. The deck overhangs the riser by 8 units on the right and the perch stops 20 units short on the left: that asymmetry is what stops it reading as a *T* or a staircase, and it is the detail to protect.

| Part | From (x y) | To (x y) | Stroke |
|---|---|---|---|
| Deck (lean height) | 40, 88 | 216, 88 | 28 |
| Riser (the fold) | 168, 88 | 168, 178 | 28 |
| Perch (rest height) | 168, 178 | 96, 178 | 28 |

Canvas `256 × 256`. Ink box `26 74 204 118` → aspect **1.73 : 1**. Stroke : height = **0.237**. Notch (deck underside to perch top) = **62 units = 2.2 × stroke** — this is the number that decides small-size survival. Capsule = a stroked line with `stroke-linecap="round"`; radius always = half the stroke, no independent corner rounding.

**Small cut (24 px and below)** — retuned, not scaled: deck `62,74 → 210,74`, riser `158`, perch `158,186 → 116,186`, stroke **44**. Stroke : height **0.28**, notch 1.55 × stroke.

### Wordmark
**Fraunces** variable, instance `wght 500 · opsz 24 · SOFT 50 · WONK 0`, tracking −1.2 %, outlines only. SIL OFL 1.1 — commercially usable including logos. No letters altered: Fraunces' *L* already lifts its foot serif, which rhymes with the mark's fold. Supporting text **Hind Vadodara** (OFL 1.1).

Lockup: mark height 1.00, wordmark cap 0.92 em, optical gap **0.40 × mark height**, shared baseline. Stacked: gap 0.34, both centred.

### Colour

| Role | HEX | Contrast on off-white |
|---|---|---|
| Background | `#F2EFE9` | — |
| Mark / text | `#3A4C40` | **8.00 : 1** (AAA) |
| Sage — shapes only | `#8BA892` | 2.26 : 1 (never text) |
| Terracotta — accents only | `#C4694A` | 3.35 : 1 (never body text) |
| Text accent | `#9E4A2C` | 5.27 : 1 (only for words on off-white) |

Reversed `#F2EFE9` on `#3A4C40` = 8.00 : 1. Never set terracotta on dark green (2.39 : 1).

---

## Size test — rendered at exact pixels, then zoomed

| Size | Master (28/256) | Small cut (44/256) |
|---|---|---|
| 64 px | Clean; both levels and the overhang read | Correct but heavy — use the master here |
| 32 px | Holds; notch survives | Works, heavier than needed |
| 16 px | **Fails** — notch lands on ~1.75 px and greys out; reads as one blob with a tail | **Passes** — step and notch both survive rasterisation |
| One colour / black | Passes — no detail depends on colour | Passes |
| Reversed | Passes, no thinning needed | Passes |

**What breaks:** the notch goes first; round caps lose their radius below ~24 px (acceptable — the two levels are the idea, not the softness); under ~14 % overhang the mark collapses into a plain *T*. **Rule:** never downscale the master below 32 px — swap to the small cut at 24 px, and drop the wordmark below 40 px total width.

Method: resvg rasterisation at exact pixel width, inspected at 8× nearest-neighbour. Tested on one Linux stack; re-test on the final print/sign rasteriser.

---

## Sticker test — on the rest panel

| Criterion | Result |
|---|---|
| 400 × 102 mm, front-on | Lockup sits flat on the panel face, 8 mm clear inside the edge |
| At 1.2 m (standing) | Wordmark holds; the mark's step still identifiable |
| At 2 m (approach) | Wordmark softens to a shape; the mark still reads as a folded surface |
| 180 × 46 mm minimum | Works with the small cut; below this the lockup fails — mark alone |
| Placement rule | Never wrap across the Ø 25 mm tube radius: the stroke foreshortens and the notch pinches |
| Material | One-colour matte vinyl or in-mould label; no keyline needed, the off-white field separates |

The mockup is schematic — confirm against the real moulding and aisle viewing distance.

---

## Risks

1. **Levia Technologies (India, kiosks)** — same name, adjacent retail. The mark must never resemble a screen, bezel or kiosk. This one doesn't, but the *name* is the conflict.
2. **PMI's LEVIA** — nothing here is a stick, rod, plume or flame. Keep the riser from thinning into a stem in any future version.
3. **Clinical drift** — the brief's green can read hospital-green. Keep sage and terracotta in supporting shapes; never a cross, heart, pill or pulse.
4. **Furniture/signage** — at large sizes it can read as a bracket. The rounded caps and unequal overhangs prevent it; do not square the caps.
5. **Generic step** — stairs and chevrons are a crowded abstract motif. Distinctiveness rests on the *unequal* overhangs, so the search should include step/chevron marks in furniture and retail classes.
6. **Fraunces** — OFL permits logo use; ship the licence with the outlines. Altered letterforms must then be called custom lettering.

---

## What I'd do next
Redraw the master in Figma at the stated geometry, re-test 16 px on the target rasteriser, then extend into the wider system (sticker, handle decal, aisle signage, digital). CMYK/Pantone and etch/embroidery artwork are not done yet.

**Deliverables:** `levia/logo/` (12 SVG masters), `levia/out/` (concepts, test sheets, pixel test, sticker), `levia/README.md` (full spec and handover).
