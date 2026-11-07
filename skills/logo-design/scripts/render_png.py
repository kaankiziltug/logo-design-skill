#!/usr/bin/env python3
"""Render validated static SVG to exact-size PNG or favicon ICO.

Examples:
  python3 scripts/render_png.py logo.svg -o logo.png --size 512
  python3 scripts/render_png.py logo.svg --ico favicon.ico --ico-sizes 16 32 48
  python3 scripts/render_png.py --which

HTML file screenshots are deliberately unsupported. --overwrite replaces regular files only.
Native renderers have 45-second deadlines. Optional CairoSVG/Pillow execute in-process;
structural limits are not a hard CPU/memory sandbox.
"""
import argparse
import base64
import importlib.util
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safety
import svglib

CHROME_CANDIDATES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'brave-browser',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
]
CSP = "default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; object-src 'none'; frame-src 'none'"


def png_size(path):
    return safety.png_dimensions(safety.bounded_read(path))


def wrap_svg(svg_path, width, height, padding=0.0, bg=None):
    safety.dimensions(width, height)
    padding = safety.finite(padding, 0, 0.4)
    bg = safety.canonical_color(bg) if bg is not None else None
    _, source = safety.load_svg(svg_path)
    vb = svglib.view_box(source)
    if not vb or vb[2] <= 0 or vb[3] <= 0:
        raise safety.SafetyError('SVG requires positive viewBox or dimensions')
    source.set('viewBox', ' '.join(str(v) for v in vb))
    for key, value in {'x': width * padding, 'y': height * padding, 'width': width * (1 - 2 * padding), 'height': height * (1 - 2 * padding), 'preserveAspectRatio': 'xMidYMid meet'}.items():
        source.set(key, str(value))
    root = ET.Element('{' + safety.SVG_NS + '}svg', {'width': str(width), 'height': str(height), 'viewBox': f'0 0 {width} {height}'})
    if bg:
        ET.SubElement(root, '{' + safety.SVG_NS + '}rect', {'width': '100%', 'height': '100%', 'fill': bg})
    root.append(source)
    return safety.serialize(safety.parse_svg(safety.serialize(root)))


def find_chrome():
    return next((shutil.which(c) for c in CHROME_CANDIDATES if shutil.which(c)), None)


def available_backends():
    found = []
    if importlib.util.find_spec('cairosvg'):
        found.append('cairosvg')
    found += [n for n in ('rsvg-convert', 'inkscape') if shutil.which(n)]
    if find_chrome():
        found.append('chrome')
    if shutil.which('qlmanage'):
        found.append('qlmanage')
    return found


def _run(command):
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=safety.RENDER_TIMEOUT)


def _cairosvg(svg_file, png, w, h):
    import cairosvg
    cairosvg.svg2png(bytestring=safety.bounded_read(svg_file), write_to=png, output_width=w, output_height=h)


def _rsvg(svg_file, png, w, h):
    _run(['rsvg-convert', '-w', str(w), '-h', str(h), '-o', png, svg_file])


def _inkscape(svg_file, png, w, h):
    _run(['inkscape', svg_file, '--export-type=png', f'--export-filename={png}', '-w', str(w), '-h', str(h)])


def _screenshot_generated(document, png, w, h, overwrite=False):
    """Private template-only entry point. No caller-supplied HTML files or trust flags."""
    safety.dimensions(w, h)
    safety.check_output(png, overwrite)
    chrome = find_chrome()
    if not chrome:
        raise RuntimeError('no Chromium-based browser available')
    if not isinstance(document, str) or len(document.encode('utf-8')) > safety.MAX_BYTES * 16:
        raise safety.SafetyError('generated document exceeds byte limit')
    with tempfile.TemporaryDirectory(prefix='logo-browser-') as tmp:
        page = Path(tmp) / 'generated.html'
        shot = Path(tmp) / 'shot.png'
        document = document.replace('<head>', '<head><meta http-equiv="Content-Security-Policy" content="' + CSP + '">', 1)
        page.write_text(document, encoding='utf-8')
        _run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
              '--no-default-browser-check', '--disable-extensions', '--disable-background-networking',
              '--default-background-color=00000000', f'--window-size={w},{h}', f'--screenshot={shot}',
              f'--user-data-dir={Path(tmp) / "profile"}', page.as_uri()])
        if png_size(shot) != (w, h):
            raise RuntimeError('browser PNG dimensions mismatch')
        safety.write_output(png, safety.bounded_read(shot), overwrite)


def _chrome(svg_file, png, w, h):
    canonical, _ = safety.load_svg(svg_file)
    encoded = base64.b64encode(canonical.encode('utf-8')).decode('ascii')
    document = (f'<!doctype html><html><head><style>html,body{{margin:0;background:transparent;overflow:hidden}}'
                f'img{{display:block;width:{w}px;height:{h}px}}</style></head><body>'
                f'<img src="data:image/svg+xml;base64,{encoded}"></body></html>')
    _screenshot_generated(document, png, w, h)


def _qlmanage(svg_file, png, w, h):
    side = max(w, h)
    safety.dimensions(side, side)
    _, root = safety.load_svg(svg_file)
    root.set('width', str(side))
    root.set('height', str(side))
    ox, oy = (side - w) / 2, (side - h) / 2
    root.set('viewBox', f'{-ox} {-oy} {side} {side}')
    with tempfile.TemporaryDirectory(prefix='logo-quicklook-') as tmp:
        tmp = Path(tmp)
        def thumbnail(name, source):
            path = tmp / (name + '.svg')
            path.write_text(safety.serialize(source), encoding='utf-8')
            _run(['qlmanage', '-t', '-s', str(side), '-o', str(tmp), str(path)])
            produced = tmp / (path.name + '.png')
            png_size(produced)
            return produced
        white = thumbnail('white', root)
        try:
            from PIL import Image
        except ImportError:
            if png_size(white) != (w, h):
                raise RuntimeError('Quick Look needs optional Pillow for non-square/cropped output')
            shutil.copyfile(white, png)
            print('note: Quick Look output is opaque white without optional Pillow', file=sys.stderr)
            return
        background = ET.Element('{' + safety.SVG_NS + '}rect', {'x': str(-ox), 'y': str(-oy), 'width': str(side), 'height': str(side), 'fill': '#000000'})
        root.insert(0, background)
        black = thumbnail('black', root)
        with Image.open(white) as iw, Image.open(black) as ib:
            front, back = iw.convert('RGB'), ib.convert('RGB').resize(iw.size)
            pixels = []
            for (wr, wg, wb), (br, bg, bb) in zip(front.getdata(), back.getdata()):
                alpha = 255 - max(wr - br, wg - bg, wb - bb)
                pixels.append((min(255, br * 255 // alpha), min(255, bg * 255 // alpha), min(255, bb * 255 // alpha), alpha) if alpha > 0 else (0, 0, 0, 0))
            out = Image.new('RGBA', iw.size)
            out.putdata(pixels)
            scale = iw.size[0] / side
            out.crop((round(ox * scale), round(oy * scale), round((ox + w) * scale), round((oy + h) * scale))).resize((w, h)).save(png)


BACKENDS = {'cairosvg': _cairosvg, 'rsvg-convert': _rsvg, 'inkscape': _inkscape, 'chrome': _chrome, 'qlmanage': _qlmanage}


def render(svg_path, png_path, width, height, padding=0.0, bg=None, backend=None, overwrite=False):
    """Validate before backend selection; stage and validate each fresh result before publishing."""
    markup = wrap_svg(svg_path, width, height, padding, bg)
    safety.check_output(png_path, overwrite, (svg_path,))
    if backend is not None and backend not in BACKENDS:
        raise safety.SafetyError('unknown backend')
    order = [backend] if backend else available_backends()
    errors = []
    for name in order:
        with tempfile.TemporaryDirectory(prefix='logo-render-') as tmp:
            wrapped, staged = Path(tmp) / 'wrapped.svg', Path(tmp) / 'result.png'
            wrapped.write_text(markup, encoding='utf-8')
            try:
                BACKENDS[name](str(wrapped), str(staged), width, height)
            except safety.SafetyError:
                raise
            except (OSError, RuntimeError, ImportError, subprocess.SubprocessError) as exc:
                errors.append(name + ': ' + type(exc).__name__ + ': ' + str(exc))
                continue
            if png_size(staged) != (width, height):
                raise RuntimeError(name + ': PNG dimensions mismatch')
            safety.write_output(png_path, safety.bounded_read(staged), overwrite, (svg_path,))
            return name
    raise RuntimeError('render failed: ' + ('; '.join(errors) if errors else 'no available backend'))


def write_ico(png_paths, ico_path, overwrite=False):
    safety.jobs(len(png_paths))
    if not png_paths:
        raise safety.SafetyError('ICO needs images')
    blobs, entries = [], []
    for path in png_paths:
        blob = safety.bounded_read(path)
        w, h = safety.png_dimensions(blob)
        if w != h or w > 256:
            raise safety.SafetyError('ICO images must be square and at most 256px')
        blobs.append(blob)
        entries.append((w, h))
    offset = 6 + 16 * len(blobs)
    dirs = b''
    for (w, h), blob in zip(entries, blobs):
        dirs += struct.pack('<BBBBHHII', w % 256, h % 256, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    safety.write_output(ico_path, struct.pack('<HHH', 0, 1, len(blobs)) + dirs + b''.join(blobs), overwrite, png_paths)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('files', nargs='*')
    ap.add_argument('-o', '--out')
    ap.add_argument('--out-dir')
    ap.add_argument('--size', type=int)
    ap.add_argument('--width', type=int)
    ap.add_argument('--height', type=int)
    ap.add_argument('--padding', type=float, default=0.0)
    ap.add_argument('--bg')
    ap.add_argument('--backend', choices=sorted(BACKENDS))
    ap.add_argument('--ico')
    ap.add_argument('--ico-sizes', nargs='*', type=int, default=[16, 32, 48])
    ap.add_argument('--which', action='store_true')
    ap.add_argument('--overwrite', action='store_true')
    a = ap.parse_args()
    if a.which:
        print('available backends:', ', '.join(available_backends()) or 'none')
        return 0
    if not a.files or (a.out and len(a.files) != 1):
        ap.error('give SVG files; --out requires one input')
    safety.jobs(len(a.files) + (len(a.ico_sizes) if a.ico else 0))
    sources = {p: safety.load_svg(p)[1] for p in a.files}
    if a.ico:
        if len(a.files) != 1 or not a.ico_sizes or len(set(a.ico_sizes)) != len(a.ico_sizes):
            ap.error('ICO requires one SVG and unique sizes')
        for size in a.ico_sizes:
            if not 1 <= size <= 256:
                ap.error('ICO sizes must be 1 to 256')
        safety.plan_outputs([a.ico], a.overwrite, a.files)
        with tempfile.TemporaryDirectory(prefix='logo-ico-') as tmp:
            pngs = []
            for size in a.ico_sizes:
                p = str(Path(tmp) / f'{size}.png')
                render(a.files[0], p, size, size, a.padding, a.bg, a.backend)
                pngs.append(p)
            write_ico(pngs, a.ico, a.overwrite)
        print('wrote', a.ico)
        return 0
    outputs = [a.out or str(Path(a.out_dir or Path(p).absolute().parent) / (Path(p).stem + '.png')) for p in a.files]
    safety.plan_outputs(outputs, a.overwrite, a.files)
    for source, out in zip(a.files, outputs):
        vb = svglib.view_box(sources[source])
        ratio = vb[2] / vb[3] if vb else 1
        w = a.width if a.width is not None else a.size if a.size is not None else 512
        h = a.height if a.height is not None else a.size if a.size is not None else 512
        if a.width is not None and a.height is None:
            h = max(1, round(a.width / ratio))
        elif a.height is not None and a.width is None:
            w = max(1, round(a.height * ratio))
        used = render(source, out, w, h, a.padding, a.bg, a.backend, a.overwrite)
        print(f'wrote {out}  {w}×{h}  via {used}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (safety.SafetyError, RuntimeError, OSError) as exc:
        print('error:', exc, file=sys.stderr)
        sys.exit(1)
