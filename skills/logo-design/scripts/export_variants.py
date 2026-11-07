#!/usr/bin/env python3
"""Export static SVG variants, optional --png sizes and --web-icons.

--name is a portable basename. Outputs are no-clobber unless --overwrite is given.
Explicit CLI input/output directories remain unrestricted owner choices.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safety
import svglib
import render_png


def recolor(raw, color, keep_white=False):
    color = safety.canonical_color(color)
    root = safety.parse_svg(raw)
    def swap(value):
        if value in ('none', 'transparent'):
            return value
        normalized = svglib.normalize_color(value)
        return value if keep_white and normalized == '#ffffff' else color
    for el in root.iter():
        for key in ('fill', 'stroke', 'stop-color'):
            if key in el.attrib:
                el.set(key, swap(el.get(key)))
        if el.get('style'):
            props = safety._declarations(el.get('style'))
            el.set('style', ';'.join(k + ':' + (swap(v) if k in ('fill', 'stroke', 'stop-color') else v) for k, v in props))
        if svglib.local(el.tag) == 'style':
            el.text = re.sub(r'\b(fill|stroke|stop-color)\s*:\s*([^;}]+)', lambda m: m.group(1) + ':' + swap(m.group(2).strip()), el.text or '')
    root.set('fill', color)
    return safety.serialize(root)


def set_title(raw, title):
    if not title:
        return raw
    root = safety.parse_svg(raw)
    for child in list(root):
        if svglib.local(child.tag) == 'title':
            root.remove(child)
    node = ET.Element('{' + safety.SVG_NS + '}title')
    node.text = title
    root.insert(0, node)
    return safety.serialize(root)


def inner_markup(raw):
    root = safety.parse_svg(raw)
    return ''.join(safety.serialize(c) for c in root if svglib.local(c.tag) != 'title')


def square_wrap(raw, root, padding=0.1, bg=None, radius=0.0, fg=None, symbol_scale=None, offset=0.0, title=None):
    root = safety.parse_svg(raw)
    padding = safety.finite(padding, 0, 0.49)
    radius = safety.finite(radius, 0, 0.5)
    offset = safety.finite(offset, -1, 1)
    target = safety.finite(symbol_scale, 0.01, 1) if symbol_scale is not None else 1 - 2 * padding
    bg = safety.canonical_color(bg) if bg is not None else None
    vb = svglib.view_box(root)
    geo = svglib.document_geometry(root)
    if not vb:
        raise safety.SafetyError('square export needs viewBox/dimensions')
    bb = geo['bbox'] or (vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3])
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    if max(w, h) <= 0:
        raise safety.SafetyError('empty square geometry')
    scale = round(256 * target / max(w, h), 6)
    tx = round((256 - w * scale) / 2 - bb[0] * scale, 6)
    ty = round((256 - h * scale) / 2 - bb[1] * scale + offset * 256, 6)
    source = safety.parse_svg(recolor(raw, fg)) if fg else root
    out = ET.Element('{' + safety.SVG_NS + '}svg', {'viewBox': '0 0 256 256', 'width': '256', 'height': '256'})
    if title:
        ET.SubElement(out, '{' + safety.SVG_NS + '}title').text = title
    if bg:
        ET.SubElement(out, '{' + safety.SVG_NS + '}rect', {'width': '256', 'height': '256', 'rx': str(256 * radius), 'fill': bg})
    attrs = {k: v for k, v in source.attrib.items() if k not in ('width', 'height', 'x', 'y', 'viewBox', 'preserveAspectRatio', 'version')}
    original_transform = attrs.get('transform', '')
    attrs['transform'] = f'translate({tx} {ty}) scale({scale}) ' + original_transform
    group = ET.SubElement(out, '{' + safety.SVG_NS + '}g', attrs)
    group.extend(copy.deepcopy(c) for c in source if svglib.local(c.tag) != 'title')
    return safety.serialize(safety.parse_svg(safety.serialize(out)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('master')
    ap.add_argument('--out-dir')
    ap.add_argument('--name')
    ap.add_argument('--title')
    ap.add_argument('--mono', action='append', default=[])
    ap.add_argument('--icon-bg', default='#111111')
    ap.add_argument('--icon-fg', default='#ffffff')
    ap.add_argument('--icon-scale', type=float, default=0.62)
    ap.add_argument('--optical-offset', type=float, default=0.0)
    ap.add_argument('--favicon-source')
    ap.add_argument('--keep-white', action='store_true')
    ap.add_argument('--only', nargs='*', choices=['black', 'white', 'mono', 'square', 'favicon', 'app-icon'])
    ap.add_argument('--png', nargs='*', type=int, default=[])
    ap.add_argument('--web-icons', action='store_true')
    ap.add_argument('--overwrite', action='store_true')
    a = ap.parse_args()
    safety.jobs(len(a.mono) + len(a.png))
    raw, root = safety.load_svg(a.master)
    small_raw, small_root = safety.load_svg(a.favicon_source) if a.favicon_source else (raw, root)
    inputs = [a.master] + ([a.favicon_source] if a.favicon_source else [])
    outdir = Path(a.out_dir or Path(a.master).absolute().parent)
    base = safety.portable_name(a.name if a.name is not None else Path(a.master).stem)
    a.icon_bg = safety.canonical_color(a.icon_bg)
    fg = None if a.icon_fg == 'keep' else safety.canonical_color(a.icon_fg)
    monos = [safety.canonical_color(c) for c in a.mono]
    safety.finite(a.icon_scale, 0.01, 1)
    safety.finite(a.optical_offset, -1, 1)
    for size in a.png:
        safety.dimensions(size, size)
    want = set(a.only) if a.only is not None else {'black', 'white', 'mono', 'square', 'favicon', 'app-icon'}
    svg_jobs = []
    def add(suffix, content):
        svg_jobs.append((outdir / f'{base}-{suffix}.svg', content))
    if 'black' in want:
        add('black', set_title(recolor(raw, '#000000', a.keep_white), a.title))
    if 'white' in want:
        add('white', set_title(recolor(raw, '#ffffff'), a.title))
    if 'mono' in want:
        for color in monos:
            add('mono-' + color[1:], set_title(recolor(raw, color, a.keep_white), a.title))
    if 'square' in want:
        add('square', square_wrap(raw, root, padding=0.08, offset=a.optical_offset, title=a.title))
    if 'favicon' in want:
        add('favicon', square_wrap(small_raw, small_root, padding=0.02, offset=a.optical_offset, title=a.title))
    if 'app-icon' in want:
        add('app-icon', square_wrap(small_raw, small_root, bg=a.icon_bg, radius=0.225, fg=fg, symbol_scale=a.icon_scale, offset=a.optical_offset, title=a.title))
    rasters = []
    for path, content in svg_jobs:
        vb = svglib.view_box(safety.parse_svg(content))
        ratio = vb[2] / vb[3] if vb else 1
        for size in a.png:
            w, h = (size, max(1, round(size / ratio))) if ratio >= 1 else (max(1, round(size * ratio)), size)
            safety.dimensions(w, h)
            rasters.append((path, path.with_name(path.stem + f'-{size}.png'), w, h))
    web_names = ['favicon-16.png', 'favicon-32.png', 'favicon-48.png', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png', 'maskable-512.png', 'favicon.ico', 'favicon.svg', 'site.webmanifest', 'head-snippet.html'] if a.web_icons else []
    safety.plan_outputs([p for p, _ in svg_jobs] + [p for _, p, _, _ in rasters] + [outdir / n for n in web_names], a.overwrite, inputs)
    for path, content in svg_jobs:
        canonical = safety.serialize(safety.parse_svg(content))
        safety.write_output(path, canonical, a.overwrite, inputs)
        print('wrote', path)
    for source, dest, w, h in rasters:
        render_png.render(source, dest, w, h, overwrite=a.overwrite)
        print('wrote', dest)
    if a.web_icons:
        with tempfile.TemporaryDirectory(prefix='logo-web-') as tmp:
            tmp = Path(tmp)
            fav = square_wrap(small_raw, small_root, padding=0.02, offset=a.optical_offset, title=a.title)
            tile = square_wrap(small_raw, small_root, bg=a.icon_bg, fg=fg, symbol_scale=a.icon_scale, offset=a.optical_offset)
            mask = square_wrap(small_raw, small_root, bg=a.icon_bg, fg=fg, symbol_scale=min(a.icon_scale, 0.5), offset=a.optical_offset)
            for name, content in [('fav', fav), ('tile', tile), ('mask', mask)]:
                safety.write_output(tmp / (name + '.svg'), content)
            jobs = [('fav', 'favicon-16.png', 16), ('fav', 'favicon-32.png', 32), ('fav', 'favicon-48.png', 48), ('tile', 'apple-touch-icon.png', 180), ('tile', 'icon-192.png', 192), ('tile', 'icon-512.png', 512), ('mask', 'maskable-512.png', 512)]
            for src, dest, size in jobs:
                render_png.render(tmp / (src + '.svg'), outdir / dest, size, size, overwrite=a.overwrite)
            render_png.write_ico([outdir / f'favicon-{s}.png' for s in (16, 32, 48)], outdir / 'favicon.ico', a.overwrite)
            safety.write_output(outdir / 'favicon.svg', fav, a.overwrite, inputs)
            manifest = {'name': a.title or base, 'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}, {'src': '/maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}], 'theme_color': a.icon_bg, 'background_color': a.icon_bg, 'display': 'standalone'}
            safety.write_output(outdir / 'site.webmanifest', json.dumps(manifest, indent=2), a.overwrite, inputs)
            safety.write_output(outdir / 'head-snippet.html', '<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">\n' + f'<meta name="theme-color" content="{a.icon_bg}">\n', a.overwrite, inputs)
        print('wrote web icons to', outdir)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (safety.SafetyError, RuntimeError, OSError) as exc:
        print('error:', exc, file=sys.stderr)
        sys.exit(1)
