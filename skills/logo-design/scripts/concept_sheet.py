#!/usr/bin/env python3
"""Build a one-page concept overview (SVG + PNG) to show the user BEFORE any kit is produced.

Each concept gets a card: the artwork large, the same mark at 64 / 32 / 16 px (so scale is judged honestly),
a letter + name, and a one-line idea. Optionally a secondary file per concept (e.g. the lockup) under the symbol.
The PNG is rendered with render_png.py's backends (cairosvg, rsvg-convert, Inkscape, Chrome, Quick Look);
the SVG is always written.

Usage:
  python3 scripts/concept_sheet.py a.svg b.svg c.svg --names "Next Block" "Ranked F" "Forward f" \\
      --notes "One block steps forward: the next move." "An F of ranked priority bars." "The i-dot steps ahead." \\
      --title "Fabbit — logo concepts" --recommend 1 -o concepts.png
  python3 scripts/concept_sheet.py a.svg b.svg c.svg --lockups a-h.svg b-h.svg c-h.svg --greyscale -o round1.png

Show the resulting PNG to the user (view it yourself first), then stop and ask how to proceed.
"""
import argparse
import html
import os
import re
import sys

sys.dont_write_bytecode = True  # keep the skill folder clean (no __pycache__)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_png  # noqa: E402
import svglib  # noqa: E402


def embed(path, key, x, y, w, h):
    """Nested <svg> that fits the file into the box; ids are prefixed so several files can coexist."""
    raw = open(path, encoding="utf-8", errors="ignore").read()
    raw = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", raw, flags=re.I)
    raw = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{key}-{m.group(1)}"', raw)
    raw = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{key}-{m.group(1)})", raw)
    raw = re.sub(r'(xlink:href|href)="#([^"]+)"', lambda m: f'{m.group(1)}="#{key}-{m.group(2)}"', raw)
    m = re.search(r"<svg\b[^>]*>", raw)
    tag = m.group(0)
    root_vb = svglib.view_box(svglib.load_svg(path)[1])
    vb = f' viewBox="{root_vb[0]:g} {root_vb[1]:g} {root_vb[2]:g} {root_vb[3]:g}"' if root_vb else ""
    new_tag = re.sub(r'\s(width|height|x|y|viewBox|preserveAspectRatio)\s*=\s*"[^"]*"', "", tag)
    new_tag = new_tag[:-1].rstrip("/") + f'{vb} x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" preserveAspectRatio="xMidYMid meet">'
    return raw.replace(tag, new_tag, 1)


def _is_cjk(ch):
    """True for CJK ideographs, kana, hangul and full-width punctuation."""
    cp = ord(ch)
    return (
        0x3040 <= cp <= 0x30FF      # kana
        or 0x3400 <= cp <= 0x4DBF   # CJK ext A
        or 0x4E00 <= cp <= 0x9FFF   # CJK unified
        or 0xF900 <= cp <= 0xFAFF   # CJK compat
        or 0xFF00 <= cp <= 0xFFEF   # full-width forms
        or 0xAC00 <= cp <= 0xD7AF   # hangul
    )


def _tokens(text):
    """Split into wrappable tokens: CJK chars stand alone, Latin words stay whole."""
    out, buf = [], ""
    for ch in text:
        if _is_cjk(ch):
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
        elif ch.isspace():
            if buf:
                out.append(buf)
                buf = ""
        else:
            buf += ch
    if buf:
        out.append(buf)
    return out


def text_units(s):
    """Approximate rendered width in half-em units: CJK = 2, Latin = 1."""
    return sum(2 if _is_cjk(ch) else 1 for ch in s)


def wrap_px(text, max_units):
    """Wrap so no line exceeds max_units half-em units (the SVG half-em = font-size/2)."""
    return wrap(text, max_units)


def wrap(text, limit):
    """Wrap by rendered width. CJK counts as 2 units, Latin as 1 (half-em)."""
    if limit <= 0:
        return [text]
    lines, line, line_len = [], "", 0
    for tok in _tokens(text):
        # a space is needed before a Latin token if the line already has content
        need_space = 1 if (line and not _is_cjk(tok[0]) and not _is_cjk(line[-1])) else 0
        tok_w = text_units(tok)
        if line_len + tok_w + need_space > limit and line:
            lines.append(line)
            line, line_len = "", 0
            need_space = 0
        line += (" " if need_space else "") + tok
        line_len += tok_w + need_space
    if line:
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="one SVG per concept (usually the symbol)")
    ap.add_argument("--lockups", nargs="*", default=[], help="optional second file per concept (lockup/wordmark)")
    ap.add_argument("--names", nargs="*", default=[])
    ap.add_argument("--notes", nargs="*", default=[], help="one-sentence idea per concept")
    ap.add_argument("--title", default="Logo concepts")
    ap.add_argument("--subtitle", default="Concepts for review — pick a direction (or tell me what you like in each).")
    ap.add_argument("--recommend", type=int, help="1-based index of the recommended concept")
    ap.add_argument("--greyscale", action="store_true", help="show everything in greyscale (first-round rule)")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("-o", "--out", default="concepts.png", help="output .png (an .svg is written next to it)")
    a = ap.parse_args()

    n = len(a.files)
    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    W, pad, gap = a.width, 60, 28
    card_w = (W - 2 * pad - (cols - 1) * gap) / cols
    has_lock = bool(a.lockups)
    art_h = 300
    lock_h = 0
    if has_lock:
        ratios = []
        for lp in a.lockups:
            if lp:
                vb = svglib.view_box(svglib.load_svg(lp)[1])
                if vb and vb[3]:
                    ratios.append(vb[2] / vb[3])
        # wide lockups fit a short slot; squarish ones (emblems, stacked lockups) need more height
        lock_h = 120 if not ratios or min(ratios) >= 2.2 else (170 if min(ratios) >= 1.4 else 210)
    # notes wrap at inner_w/9.6; size the card to the tallest note instead of clipping it
    _inner_w_probe = card_w - 60
    _note_lines = 0
    for i in range(n):
        _note = a.notes[i] if i < len(a.notes) else ""
        if _note:
            _note_lines = max(_note_lines, len(wrap(_note, int(_inner_w_probe / 9.5))))
    # 26px leading per note line; guarantee at least one line of room
    note_h = max(1, _note_lines) * 26 + 8
    card_h = 40 + art_h + (lock_h + 24 if has_lock else 0) + 90 + 150 + (30 if a.recommend else 0) + note_h + 20
    header = 150
    H = header + rows * card_h + (rows - 1) * gap + pad
    parts = []
    filt = ('<defs><filter id="grey"><feColorMatrix type="saturate" values="0"/></filter></defs>' if a.greyscale else "")
    gattr = ' filter="url(#grey)"' if a.greyscale else ""
    font = "font-family=\"system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif\""
    parts.append(f'<rect width="{W}" height="{H}" fill="#f7f7f4"/>')
    parts.append(f'<text x="{pad}" y="78" {font} font-size="40" font-weight="700" fill="#161616">{html.escape(a.title)}</text>')
    parts.append(f'<text x="{pad}" y="116" {font} font-size="20" fill="#6b6b6b">{html.escape(a.subtitle)}</text>')
    for i, f in enumerate(a.files):
        r, c = divmod(i, cols)
        x = pad + c * (card_w + gap)
        y = header + r * (card_h + gap)
        rec = a.recommend == i + 1
        parts.append(f'<rect x="{x:g}" y="{y:g}" width="{card_w:g}" height="{card_h:g}" rx="18" fill="#fff" '
                     f'stroke="{"#161616" if rec else "#e4e4e0"}" stroke-width="{2 if rec else 1}"/>')
        inner_x, inner_w = x + 30, card_w - 60
        parts.append(f"<g{gattr}>" + embed(f, f"c{i}", inner_x, y + 40, inner_w, art_h) + "</g>")
        yy = y + 40 + art_h
        if has_lock and i < len(a.lockups) and a.lockups[i]:
            yy += 24
            parts.append(f"<g{gattr}>" + embed(a.lockups[i], f"l{i}", inner_x, yy, inner_w, lock_h) + "</g>")
            yy += lock_h
        # small sizes: 64 / 32 / 16 px, as they would appear
        sx = inner_x
        yy += 26
        for s in (64, 32, 16):
            parts.append(f"<g{gattr}>" + embed(f, f"s{i}{s}", sx, yy + (64 - s), s, s) + "</g>")
            parts.append(f'<text x="{sx + s / 2:g}" y="{yy + 84}" {font} font-size="12" fill="#8a8a8a" text-anchor="middle">{s}px</text>')
            sx += s + 26
        yy += 120
        raw = a.names[i] if i < len(a.names) else os.path.splitext(os.path.basename(f))[0]
        # avoid duplicating an existing "A ·" / "A —" / "A:" prefix
        if raw.lstrip()[:1] == chr(65 + i) and raw.lstrip()[1:2] in (" ", "·", "—", "-", ":"):
            label = raw.lstrip()[1:].lstrip(" ·—:-")
        else:
            label = f"{chr(65 + i)} · {raw}"
        parts.append(f'<text x="{inner_x}" y="{yy}" {font} font-size="26" font-weight="700" '
                     f'fill="{"#161616"}">{html.escape(label)}</text>')
        if rec:
            parts.append(f'<text x="{inner_x}" y="{yy + 28}" {font} font-size="15" font-weight="700" fill="#161616" '
                         f'letter-spacing="1.5">RECOMMENDED</text>')
            yy += 28
        note = a.notes[i] if i < len(a.notes) else ""
        # card_h already reserves exactly len(wrap(note)) lines, so draw them all
        for k, line in enumerate(wrap(note, int(inner_w / 9.5))):
            parts.append(f'<text x="{inner_x}" y="{yy + 34 + k * 26}" {font} font-size="19" fill="#555">{html.escape(line)}</text>')
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{W}" height="{H:g}" viewBox="0 0 {W} {H:g}">{filt}{"".join(parts)}</svg>\n')
    base = os.path.splitext(a.out)[0]
    svg_path = base + ".svg"
    with open(svg_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print("wrote", svg_path)
    png_path = base + ".png"
    used = render_png.render(svg_path, png_path, W, int(round(H)))
    if used:
        print(f"wrote {png_path} via {used} — view it, show it to the user, then stop and ask")
    else:
        print("PNG skipped (no renderer; see render_png.py --which) — show the SVG instead")


if __name__ == "__main__":
    main()
