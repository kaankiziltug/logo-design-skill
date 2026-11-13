#!/usr/bin/env python3
"""Rebuild the reference-library catalog from the SVG files + visual classifications.

Maintainer tool. Produces, inside assets/library/:
  catalog.json   one record per SVG (structure, colours, complexity + visual classification)
  stats.json     distribution statistics used by svg_audit.py for comparisons
  gallery.html   a self-contained, filterable browser for humans (open it locally)

Usage:
  python3 scripts/build_catalog.py            # rebuild everything
  python3 scripts/build_catalog.py --check    # verify every SVG has a classification

To add logos: drop SVGs into assets/library/svg/, add matching objects to
assets/library/classifications.json (schema: see references/library-guide.md), then rerun.
"""
import argparse
import json
import os
import statistics
import sys
from collections import Counter

sys.dont_write_bytecode = True  # keep the skill folder clean (no __pycache__)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svglib  # noqa: E402

CLASS_PATH = os.path.join(svglib.LIBRARY_DIR, "classifications.json")
GALLERY_PATH = os.path.join(svglib.LIBRARY_DIR, "gallery.html")


def analyse(path, names):
    fname = os.path.basename(path)
    base = fname[:-4]
    is_icon = base.endswith("-icon")
    brand = base[:-5] if is_icon else base
    raw, root = svglib.load_svg(path)
    vb = svglib.view_box(root)
    w, h = (vb[2], vb[3]) if vb else (None, None)
    aspect = round(w / h, 3) if w and h else None
    counts = svglib.element_counts(root)
    geo = svglib.document_geometry(root)
    colors = svglib.collect_colors(root)
    fams = Counter(svglib.hue_family(c) for c in colors)
    chroma = sorted({f for f in fams if f not in ("black", "white", "gray")})
    if len(chroma) == 1:
        primary = chroma[0]
    elif len(chroma) > 1:
        primary = "multi"
    else:
        primary = "mono"
    pair = None
    if is_icon and brand in names:
        pair = brand + ".svg"
    elif not is_icon and (brand + "-icon") in names:
        pair = brand + "-icon.svg"
    return {
        "file": fname,
        "brand": brand,
        "variant": "icon" if is_icon else "main",
        "pair": pair,
        "width": w,
        "height": h,
        "aspect": aspect,
        "aspect_class": svglib.aspect_class(aspect),
        "bytes": os.path.getsize(path),
        "shapes": sum(counts.get(t, 0) for t in svglib.SHAPE_TAGS),
        "anchors": geo["anchors"],
        "colors": colors,
        "n_colors": len(colors),
        "color_families": sorted(fams),
        "primary_family": primary,
        "gradients": counts.get("linearGradient", 0) + counts.get("radialGradient", 0),
        "has_mask": counts.get("mask", 0) > 0,
        "has_filter": counts.get("filter", 0) > 0,
    }


def pct(values, q):
    values = sorted(values)
    if not values:
        return None
    k = (len(values) - 1) * q
    f, c = int(k), min(int(k) + 1, len(values) - 1)
    return round(values[f] + (values[c] - values[f]) * (k - f), 2)


def build_stats(records):
    def dist(vals):
        return {"p10": pct(vals, .1), "p25": pct(vals, .25), "median": pct(vals, .5),
                "p75": pct(vals, .75), "p90": pct(vals, .9), "p95": pct(vals, .95)}
    icons = [r for r in records if r["aspect_class"] == "square"]
    n = len(records)
    return {
        "count": n,
        "anchors_all": dist([r["anchors"] for r in records]),
        "anchors_square": dist([r["anchors"] for r in icons]),
        "shapes_all": dist([r["shapes"] for r in records]),
        "n_colors_all": dist([r["n_colors"] for r in records]),
        "n_colors_square": dist([r["n_colors"] for r in icons]),
        "gradient_share": round(sum(1 for r in records if r["gradients"]) / n, 3),
        "mark_types": Counter(r.get("mark_type") for r in records).most_common(),
        "primary_family": Counter(r["primary_family"] for r in records).most_common(),
        "aspect_class": Counter(r["aspect_class"] for r in records).most_common(),
        "techniques": Counter(t for r in records for t in r.get("techniques", [])).most_common(),
        "geometry": Counter(g for r in records for g in r.get("geometry", [])).most_common(),
        "industries": Counter(r.get("industry") for r in records).most_common(),
    }


GALLERY_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Logo Reference Library</title>
<style>
:root{--bg:#f6f6f4;--card:#fff;--ink:#1b1b1b;--muted:#6b6b6b;--line:#e3e3df;--accent:#0f7c80}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--card:#1e1e1e;--ink:#eee;--muted:#999;--line:#333;--accent:#4fc3c7}}
*{box-sizing:border-box}body{margin:0;font:14px/1.4 system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--ink)}
header{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px}
h1{font-size:18px;margin:0 0 8px}.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
select,input,button{font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
button{cursor:pointer}button:hover:not(:disabled){border-color:var(--accent);color:var(--accent)}
button:disabled{opacity:.45;cursor:default}
label{display:flex;gap:4px;align-items:center;color:var(--muted)}#count{color:var(--muted);margin-left:auto}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:12px;padding:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px;display:flex;flex-direction:column;gap:6px}
.thumb{height:110px;display:flex;align-items:center;justify-content:center;background:#fff;border-radius:6px}
.thumb img{max-width:92%;max-height:92px}.name{font-weight:600;word-break:break-all}.meta{color:var(--muted);font-size:12px}
.star{color:#d4a017}.note{font-size:12px}
</style></head><body>
<header><h1>Logo Reference Library <span class="meta">— for studying patterns; all marks are trademarks of their owners. Never copy.</span></h1>
<div class="filters">
<input id="q" placeholder="search name / subject / note" size="26">
<select id="type"><option value="">all mark types</option></select>
<select id="tech"><option value="">all techniques</option></select>
<select id="geo"><option value="">all geometry</option></select>
<select id="ind"><option value="">all industries</option></select>
<select id="fam"><option value="">all colour families</option></select>
<label><input type="checkbox" id="ex"> exemplary only</label>
<label><input type="checkbox" id="icon"> icons only</label>
<button type="button" id="clear" disabled>clear filters</button>
<span id="count"></span></div></header>
<main id="grid"></main>
<script>
const DATA = __DATA__;
const $ = id => document.getElementById(id);
function fill(sel, vals){[...new Set(vals)].filter(Boolean).sort().forEach(v=>{const o=document.createElement('option');o.value=o.textContent=v;sel.appendChild(o)})}
fill($('type'), DATA.map(d=>d.mark_type)); fill($('tech'), DATA.flatMap(d=>d.techniques||[]));
fill($('geo'), DATA.flatMap(d=>d.geometry||[])); fill($('ind'), DATA.map(d=>d.industry)); fill($('fam'), DATA.map(d=>d.primary_family));
function render(){
  const q=$('q').value.toLowerCase(), t=$('type').value, te=$('tech').value, g=$('geo').value, i=$('ind').value, f=$('fam').value;
  const rows = DATA.filter(d=>(!t||d.mark_type===t)&&(!te||(d.techniques||[]).includes(te))&&(!g||(d.geometry||[]).includes(g))
    &&(!i||d.industry===i)&&(!f||d.primary_family===f)&&(!$('ex').checked||d.exemplary)&&(!$('icon').checked||d.aspect_class==='square')
    &&(!q||(d.file+' '+(d.subject||'')+' '+(d.note||'')).toLowerCase().includes(q)));
  $('count').textContent = rows.length + ' / ' + DATA.length;
  $('grid').innerHTML = rows.slice(0,600).map(d=>`<div class="card"><div class="thumb"><img loading="lazy" src="svg/${d.file}" alt="${d.brand}"></div>
   <div class="name">${d.exemplary?'<span class="star">★</span> ':''}${d.file}</div>
   <div class="meta">${d.mark_type}${d.symbol_type?' · '+d.symbol_type:''} · ${d.industry} · ${d.n_colors} col</div>
   <div class="meta">${(d.techniques||[]).join(', ')}</div>${d.note?`<div class="note">${d.note}</div>`:''}</div>`).join('');
  $('clear').disabled = !($('q').value||$('type').value||$('tech').value||$('geo').value||$('ind').value||$('fam').value||$('ex').checked||$('icon').checked);
}
$('clear').addEventListener('click',()=>{['q','type','tech','geo','ind','fam'].forEach(id=>$(id).value='');$('ex').checked=$('icon').checked=false;$('q').focus();render()});
['q','type','tech','geo','ind','fam','ex','icon'].forEach(id=>$(id).addEventListener('input',render)); render();
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only verify classification coverage")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(svglib.LIBRARY_SVG_DIR) if f.lower().endswith(".svg"))
    names = {f[:-4] for f in files}
    classes = {}
    if os.path.exists(CLASS_PATH):
        with open(CLASS_PATH, encoding="utf-8") as fh:
            classes = {c["file"]: c for c in json.load(fh)}
    missing = [f for f in files if f not in classes]
    if args.check:
        print(f"{len(files)} SVGs, {len(classes)} classifications, {len(missing)} missing")
        for f in missing:
            print("  missing:", f)
        return 1 if missing else 0

    records = []
    for f in files:
        try:
            rec = analyse(os.path.join(svglib.LIBRARY_SVG_DIR, f), names)
        except Exception as exc:  # keep going; report broken files
            print("  ! could not parse", f, exc, file=sys.stderr)
            continue
        c = classes.get(f, {})
        for key in ("mark_type", "symbol_type", "subject", "geometry", "techniques", "type_style", "case",
                    "mood", "industry", "exemplary", "note"):
            rec[key] = c.get(key)
        rec["techniques"] = rec["techniques"] or []
        rec["geometry"] = rec["geometry"] or []
        rec["mood"] = rec["mood"] or []
        rec["exemplary"] = bool(rec["exemplary"])
        records.append(rec)

    with open(svglib.CATALOG_PATH, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, separators=(",", ":"))
    stats = build_stats(records)
    with open(svglib.STATS_PATH, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=1)
    slim = [{k: r[k] for k in ("file", "brand", "mark_type", "symbol_type", "subject", "techniques", "geometry",
                               "industry", "exemplary", "note", "n_colors", "primary_family", "aspect_class")}
            for r in records]
    with open(GALLERY_PATH, "w", encoding="utf-8") as fh:
        fh.write(GALLERY_TEMPLATE.replace("__DATA__", json.dumps(slim, ensure_ascii=False)))
    print(f"catalog: {len(records)} records -> {svglib.CATALOG_PATH}")
    print(f"stats   -> {svglib.STATS_PATH}")
    print(f"gallery -> {GALLERY_PATH}")
    if missing:
        print(f"warning: {len(missing)} SVGs have no classification (run with --check)")
    print("median anchors (square):", stats["anchors_square"]["median"], "| p90:", stats["anchors_square"]["p90"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
