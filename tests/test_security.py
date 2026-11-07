"""Regression tests for adopted static-input, output and resource boundaries.

Only dummy files under the task TMPDIR are used. LOGO_TEST_SCRIPTS can point to an
isolated mutant copy; it never changes the production checkout's imports.
"""
import base64
import binascii
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
import zlib

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(os.environ.get('LOGO_TEST_SCRIPTS', str(ROOT / 'skills/logo-design/scripts')))
sys.path.insert(0, str(SCRIPTS))
import safety
import svglib
import render_png as render
import export_variants as export
import concept_sheet as concept
import presentation_board as board
import preview_sheet as preview
import build_catalog as catalog
import svg_audit

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect x="2" y="2" width="28" height="28" fill="#abc"/></svg>'
NS = '{http://www.w3.org/2000/svg}'


def png(w=2, h=2, raster=None):
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', binascii.crc32(kind + body) & 0xffffffff)
    rows = raster if raster is not None else (b'\x00' + b'\x00\x80\xff\xff' * w) * h
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='logo-security-')
        self.addCleanup(self.temp.cleanup)
        self.tmp = Path(self.temp.name)
        self.svg = self.tmp / 'input.svg'
        self.svg.write_text(SVG, encoding='utf-8')

    def cli(self, script, *args, env=None):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        if env:
            environment.update(env)
        return subprocess.run([sys.executable, str(SCRIPTS / script)] + [str(a) for a in args], cwd=str(self.tmp), env=environment, capture_output=True, text=True, timeout=20)

    def rejected(self, script, *args, reason=None):
        result = self.cli(script, *args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        if reason:
            self.assertIn(reason, result.stdout + result.stderr)
        return result


class StaticSVG(Fixture):
    def test_active_foreign_and_unknown_structure(self):
        for body in ['<script/>', '<foreignObject/>', '<animate/>', '<set/>', '<a/>', '<iframe/>', '<feImage href="file:///dummy"/>', '<path onload="dummy"/>', '<g xmlns="urn:foreign"/>', '<path xmlns:q="urn:foreign" q:fill="red"/>']:
            with self.subTest(body=body), self.assertRaises(safety.SafetyError):
                safety.parse_svg('<svg>' + body + '</svg>')
        for text in ['<html/>', '<!DOCTYPE svg><svg/>', '<!DOCTYPE svg [<!ENTITY x "dummy">]><svg>&x;</svg>', '<?x dummy?><svg/>', '<svg><?x dummy?></svg>', b'\xff<svg/>']:
            with self.subTest(text=text), self.assertRaises(safety.SafetyError):
                safety.parse_svg(text)

    def test_external_references_and_css(self):
        cases = ['<use href="../dummy.svg#x"/>', '<use href="https://invalid.example/x"/>', '<image href="data:image/svg+xml;base64,PHN2Zy8+"/>', '<image href="data:image/png;base64,notPNG"/>', '<path fill="url(file:///dummy)"/>', '<path filter="url(https://invalid.example)"/>', '<path style="fill:red;cursor:url(dummy)"/>', '<path style="fill:expression(dummy)"/>', '<path style="fill:u\\72l(dummy)"/>', '<style>@import "dummy";</style>', '<style>path{fill:url(https://invalid.example)}</style>', '<style>path{font-family:foo;behavior:dummy}</style>', '<path style="fill:red;broken"/>', '<style>path{fill:red} broken</style>']
        for body in cases:
            with self.subTest(body=body), self.assertRaises(safety.SafetyError):
                safety.parse_svg('<svg>' + body + '</svg>')

    def test_local_resources_styles_and_namespaces_roundtrip(self):
        source = "<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 32 32'><defs><path id='p' d='M0 0L20 20Z'/><mask id='m'><use xlink:href='#p'/></mask><filter id='f'><feGaussianBlur stdDeviation='1'/></filter></defs><style>.art{fill:#abc;stroke:url(#grad)}</style><linearGradient id='grad'><stop offset='0' stop-color='red'/></linearGradient><use class='art' xlink:href='#p' mask='url(#m)' filter='url(#f)' aria-label='A &quot; B'/></svg>"
        self.svg.write_text(source, encoding='utf-8')
        raw, root = safety.load_svg(self.svg)
        self.assertIn('xlink:href="#p"', raw)
        self.assertEqual(ET.fromstring(raw).find(NS + 'use').get('aria-label'), 'A " B')
        decoded = base64.b64decode(svglib.svg_data_uri(self.svg).split(',')[1])
        self.assertEqual(ET.fromstring(decoded).get('width'), '32.0')
        self.assertNotIn(b'<?', decoded)
        for markup in [render.wrap_svg(self.svg, 64, 32), concept.embed(self.svg, 'one', 0, 0, 64, 32), export.square_wrap(raw, root)]:
            safety.parse_svg(markup)
            self.assertEqual(ET.fromstring(markup).tag, NS + 'svg')
        self.assertIn('#abc', concept.embed(self.svg, 'two', 0, 0, 32, 32))

    def test_all_embedding_paths_reject_before_render(self):
        self.svg.write_text('<svg><script/></svg>', encoding='utf-8')
        for action in [lambda: svglib.load_svg(self.svg), lambda: svglib.svg_data_uri(self.svg), lambda: concept.embed(self.svg, 'x', 0, 0, 1, 1), lambda: render.wrap_svg(self.svg, 2, 2), lambda: export.recolor(self.svg.read_text(), '#fff')]:
            with self.subTest(action=action), self.assertRaises(safety.SafetyError):
                action()
        with mock.patch.object(render, 'available_backends') as available, self.assertRaises(safety.SafetyError):
            render.render(self.svg, self.tmp / 'out.png', 2, 2)
        available.assert_not_called()
        for script, args in [('preview_sheet.py', [self.svg, '-o', self.tmp / 'p.html']), ('concept_sheet.py', [self.svg, '-o', self.tmp / 'c.png']), ('export_variants.py', [self.svg, '--out-dir', self.tmp / 'out']), ('render_png.py', [self.svg, '-o', self.tmp / 'r.png']), ('svg_audit.py', [self.svg])]:
            with self.subTest(script=script):
                self.rejected(script, *args, reason='unsupported SVG element')

    def test_reference_cycles_missing_and_amplification(self):
        for body in ['<use href="#missing"/>', '<g id="a"><use href="#a"/></g>', '<g id="a"/><g id="a"/>', '<g id="a"><use href="#b"/></g><g id="b"><use href="#a"/></g>']:
            with self.subTest(body=body), self.assertRaises(safety.SafetyError):
                safety.parse_svg('<svg>' + body + '</svg>')
        chain = '<g id="g0"><path d="M0 0L1 1"/></g>' + ''.join(f'<g id="g{i}"><use href="#g{i-1}"/><use href="#g{i-1}"/></g>' for i in range(1, 20))
        with self.assertRaisesRegex(safety.SafetyError, 'expansion'):
            safety.parse_svg('<svg><defs>' + chain + '</defs><use href="#g19"/></svg>')
        with self.assertRaisesRegex(safety.SafetyError, 'reference depth'):
            with mock.patch.object(safety, 'MAX_DEPTH', 4):
                safety.parse_svg('<svg><defs><g id="a"/><g id="b"><use href="#a"/></g><g id="c"><use href="#b"/></g></defs><use href="#c"/></svg>')

    def test_png_validation_and_embedded_png(self):
        valid = png()
        self.assertEqual(safety.png_dimensions(valid), (2, 2))
        encoded = base64.b64encode(valid).decode('ascii')
        safety.parse_svg('<svg><image href="data:image/png;base64,' + encoded + '"/></svg>')
        for data in [b'', b'\x89PNG\r\n\x1a\n', valid[:24], valid[:-1], valid + b'junk', valid[:40] + b'x' + valid[41:], png(raster=b'\x00'), png(raster=b'\xff' + b'\0' * 17), png(0, 1)]:
            with self.subTest(data=data[:25]), self.assertRaises(safety.SafetyError):
                safety.png_dimensions(data)

    def test_byte_element_depth_token_geometry_caps(self):
        for constant, limit, source, reason in [('MAX_BYTES', 6, '<svg/> ', 'byte'), ('MAX_ELEMENTS', 2, '<svg><g/><g/></svg>', 'element'), ('MAX_DEPTH', 2, '<svg><g><path/></g></svg>', 'depth'), ('MAX_TOKENS', 3, '<svg><path d="M0 0L1 1"/></svg>', 'token')]:
            with self.subTest(constant=constant), mock.patch.object(safety, constant, limit), self.assertRaisesRegex(safety.SafetyError, reason):
                safety.parse_svg(source)
        with self.assertRaisesRegex(safety.SafetyError, 'byte'):
            safety.bounded_read(self.svg, 4)
        if hasattr(os, 'mkfifo'):
            fifo = self.tmp / 'dummy.fifo'
            os.mkfifo(fifo)
            with self.assertRaisesRegex(safety.SafetyError, 'regular'):
                safety.bounded_read(fifo)
        for attr in ['viewBox="0 0 0 1"', 'viewBox="0 0 1"', 'width="NaN"', 'height="1e999"', 'x="10000001"', 'transform="scale(10000000) scale(2)"', 'transform="translate()"', 'transform="unknown(1)"', 'transform="rotate(1) garbage"', 'points="1 2 3"', 'width="junk"']:
            with self.subTest(attr=attr), self.assertRaises(safety.SafetyError):
                safety.parse_svg('<svg ' + attr + '/>')
        with self.assertRaises(safety.SafetyError):
            safety.parse_svg('<svg><g transform="scale(10000000)"><g transform="scale(2)"/></g></svg>')
        with self.assertRaises(safety.SafetyError):
            svglib.apply((10000000, 0, 0, 1, 0, 0), (2, 0))

    def test_path_progress_and_malformed_cli_are_bounded(self):
        cases = ['M0 0 Z 1', 'M0', 'M0 0 X1', 'M0 0 L', 'M0 0 L1 Z', 'M0 0 @', 'M0 0 A1 1 0 2 0 1 1', 'M0 0 L1e999 0', 'L1 1']
        for path in cases:
            with self.subTest(path=path), self.assertRaises(safety.SafetyError):
                svglib.parse_path(path)
        self.assertTrue(svglib.parse_path('M0 0L2 2Z M4 4a1 1 0 011 1Z'))
        self.svg.write_text('<svg><path d="M0 0 Z 1"/></svg>')
        self.rejected('svg_audit.py', self.svg, reason='path data without command')

    def test_css_caps_and_reference_composed_geometry(self):
        with mock.patch.object(safety, 'MAX_CSS_RULES', 1), self.assertRaisesRegex(safety.SafetyError, 'CSS rule'):
            safety.parse_svg('<svg><style>.a{fill:red}.b{fill:blue}</style></svg>')
        with mock.patch.object(safety, 'MAX_DECLARATIONS', 2), self.assertRaisesRegex(safety.SafetyError, 'CSS declaration'):
            safety.parse_svg('<svg><path style="fill:red;stroke:blue;opacity:1"/></svg>')
        with mock.patch.object(safety, 'MAX_TOKENS', 2), self.assertRaisesRegex(safety.SafetyError, 'token'):
            safety.parse_svg('<svg><style>.a{stroke-dasharray:1 2 3}</style></svg>')
        with self.assertRaisesRegex(safety.SafetyError, 'finite geometry'):
            safety.parse_svg('<svg><defs><g id="a" transform="scale(10000000)"/></defs><use href="#a" transform="scale(2)"/></svg>')
        self.svg.write_text('<svg viewBox="0 0 32 32"><style>#abc{fill:#abc}</style><path id="abc" d="M0 0L2 2Z"/></svg>')
        embedded = concept.embed(self.svg, 'prefix', 0, 0, 32, 32)
        self.assertIn('#prefix-abc{fill:#abc}', embedded)
        safety.parse_svg(embedded)
        self.svg.write_text('<svg><style>' + 'a' * 100000 + '</style></svg>')
        self.rejected('svg_audit.py', self.svg, reason='malformed stylesheet')

    def test_all_1432_library_assets(self):
        files = sorted((ROOT / 'skills/logo-design/assets/library/svg').glob('*.svg'))
        self.assertEqual(len(files), 1432)
        for path in files:
            with self.subTest(asset=path.name):
                raw, root = safety.load_svg(path)
                self.assertEqual(root.tag, NS + 'svg')
                safety.parse_svg(raw)


class SpecAndText(Fixture):
    def spec(self, **extra):
        data = {'brand': 'Dummy', 'concepts': [{'name': 'A', 'symbol': 'input.svg'}]}
        data.update(extra)
        path = self.tmp / 'spec.json'
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def test_asset_root_resolves_paths_and_symlinks(self):
        folder = self.tmp / 'assets'
        folder.mkdir()
        good = folder / 'good.svg'
        good.write_text(SVG)
        outside = self.tmp / 'outside.svg'
        outside.write_text(SVG)
        self.assertEqual(safety.asset_path('good.svg', folder), str(good))
        self.assertEqual(safety.asset_path(str(good), folder), str(good))
        (folder / 'ok.svg').symlink_to(good)
        self.assertEqual(safety.asset_path('ok.svg', folder), str(good))
        (folder / 'escape.svg').symlink_to(outside)
        sibling = self.tmp / 'assets-sibling'
        sibling.mkdir()
        (sibling / 'bad.svg').write_text(SVG)
        for path in ['../outside.svg', str(outside), 'escape.svg', '../assets-sibling/bad.svg']:
            with self.subTest(path=path), self.assertRaisesRegex(safety.SafetyError, 'escapes'):
                safety.asset_path(path, folder)
        self.assertEqual(safety.asset_path('../outside.svg', folder, self.tmp), str(outside))
        (folder / 'dummy.txt').write_text(SVG)
        with self.assertRaisesRegex(safety.SafetyError, 'regular SVG'):
            safety.asset_path('dummy.txt', folder)

    def test_cli_spec_root_only_override_and_explicit_paths_legal(self):
        sub = self.tmp / 'specs'
        sub.mkdir()
        spec = sub / 'spec.json'
        spec.write_text(json.dumps({'asset_root': str(self.tmp), 'concepts': [{'symbol': '../input.svg'}]}))
        out = self.tmp / 'explicit' / 'board.html'
        self.rejected('presentation_board.py', spec, '-o', out, reason='escapes allowed root')
        self.assertFalse(out.exists())
        result = self.cli('presentation_board.py', spec, '--asset-root', self.tmp, '-o', out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('data:image/svg+xml;base64,', out.read_text())
        good = self.cli('preview_sheet.py', self.svg, '-o', self.tmp / 'elsewhere' / 'p.html')
        self.assertEqual(good.returncode, 0, good.stderr)
        self.svg.write_text('dummy non-SVG bytes')
        self.rejected('presentation_board.py', self.spec(), '-o', self.tmp / 'bad.html', reason='invalid SVG XML')

    def test_typed_fields_and_strict_colours(self):
        invalid = [{'brand': []}, {'round': '<b>dummy</b>'}, {'round': True}, {'date': 1}, {'greyscale': 'false'}, {'final': 1}, {'adjectives': 'abc'}, {'nav': [1]}, {'mockups': {}}, {'next_steps': [False]}, {'concepts': {}}, {'concepts': [1]}, {'concepts': [{'symbol': 1}]}, {'concepts': [{'symbol': 'x.svg', 'rationale': 'bad'}]}, {'concepts': [{}]}]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(safety.SafetyError):
                safety.validate_spec(value)
        for value in ['red; background:url(dummy)', '#fff\" onload=\"dummy', 'rgb(1,2,3)junk', 'rgba(1,2,3,1)', '#fff</style>', 'url(#x)', 'rgb(256,0,0)', 'rgb(NaN,0,0)', None]:
            with self.subTest(value=value), self.assertRaises(safety.SafetyError):
                safety.canonical_color(value)
        self.assertEqual(safety.canonical_color('#AbC'), '#aabbcc')
        self.assertEqual(safety.canonical_color('rgb(100%,0%,0%)'), '#ff0000')
        self.assertEqual(safety.canonical_color('teal'), '#008080')
        self.rejected('preview_sheet.py', self.svg, '--brand-color', '#fff;dummy', '-o', self.tmp / 'c.html', reason='unsupported colour')
        self.rejected('export_variants.py', self.svg, '--icon-bg', '#fff;dummy', reason='unsupported colour')
        self.rejected('export_variants.py', self.svg, '--mono', 'rgb(1,2,3)junk', reason='unsupported colour')
        self.rejected('presentation_board.py', self.spec(brand_color='#fff;dummy'), reason='unsupported colour')

    def test_board_text_escaped_in_all_contexts(self):
        payload = '<img src="dummy" onerror="dummy"> & "test"'
        spec = self.spec(brand=payload, date=payload, label=payload, designer=payload, deck_title=payload, brief=payload, criteria=payload, tagline=payload, adjectives=[payload], nav=[payload], recommendation=payload, next_steps=[payload], concepts=[{'symbol': 'input.svg', 'name': payload, 'idea': payload, 'rationale': [payload]}])
        out = self.tmp / 'board.html'
        result = self.cli('presentation_board.py', spec, '-o', out)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = out.read_text()
        self.assertNotIn(payload, text)
        self.assertNotIn('onerror="dummy"', text)
        self.assertIn('&lt;img', text)
        self.assertIn('&amp;', text)
        self.assertIn('&quot;test&quot;', text)

    def test_gallery_json_and_dom_sinks_and_checked_in_regeneration(self):
        record = {'file': 'dummy.svg', 'brand': '</script><img src=dummy>', 'note': '<b>dummy</b>'}
        generated = catalog.gallery([record])
        embedded = generated.split('const DATA = ', 1)[1].split(';\n', 1)[0]
        self.assertNotIn('<', embedded)
        self.assertEqual(json.loads(embedded), [record])
        self.assertNotIn('innerHTML', generated)
        self.assertIn('node.textContent=text', generated)
        self.assertIn('encodeURIComponent(d.file)', generated)
        with self.assertRaises(safety.SafetyError):
            catalog.gallery([{'file': '../dummy.svg'}])
        records = json.loads((ROOT / 'skills/logo-design/assets/library/catalog.json').read_text())
        slim = [{k: r[k] for k in ('file', 'brand', 'mark_type', 'symbol_type', 'subject', 'techniques', 'geometry', 'industry', 'exemplary', 'note', 'n_colors', 'primary_family', 'aspect_class')} for r in records]
        self.assertEqual((ROOT / 'skills/logo-design/assets/library/gallery.html').read_text(), catalog.gallery(slim))


class OutputAndRendering(Fixture):
    def test_portable_basenames(self):
        for name in ['../escape', '/dummy', 'a/b', 'a\\b', '..', '.', 'dummy.', 'CON', 'nul.svg', 'COM1', 'lpt9.svg', 'a:b', 'a b', '-x', 'x' * 121]:
            with self.subTest(name=name), self.assertRaises(safety.SafetyError):
                safety.portable_name(name)
        self.assertEqual(safety.portable_name('A-logo_2.v1'), 'A-logo_2.v1')
        self.rejected('export_variants.py', self.svg, '--name', '../escape', '--out-dir', self.tmp / 'out', reason='portable basename')
        self.assertFalse((self.tmp / 'escape-black.svg').exists())

    def test_no_clobber_overwrite_regular_alias_and_collisions(self):
        out = self.tmp / 'out.txt'
        safety.write_output(out, 'first')
        with self.assertRaisesRegex(safety.SafetyError, 'exists'):
            safety.write_output(out, 'second')
        self.assertEqual(out.read_text(), 'first')
        safety.write_output(out, 'third', overwrite=True)
        self.assertEqual(out.read_text(), 'third')
        for target in [self.svg, self.tmp / 'missing']:
            link = self.tmp / ('dangling' if not target.exists() else 'link')
            link.symlink_to(target)
            for overwrite in [False, True]:
                with self.subTest(target=target, overwrite=overwrite), self.assertRaisesRegex(safety.SafetyError, 'symlink'):
                    safety.write_output(link, 'dummy', overwrite)
        with self.assertRaisesRegex(safety.SafetyError, 'regular'):
            safety.write_output(self.tmp, 'dummy', True)
        with self.assertRaisesRegex(safety.SafetyError, 'alias'):
            safety.write_output(self.svg, 'dummy', True, [self.svg])
        hardlink = self.tmp / 'hard.svg'
        os.link(self.svg, hardlink)
        with self.assertRaisesRegex(safety.SafetyError, 'alias'):
            safety.plan_outputs([hardlink], True, [self.svg])
        with self.assertRaisesRegex(safety.SafetyError, 'collision'):
            safety.plan_outputs([out, out.parent / '.' / out.name], True)
        with self.assertRaisesRegex(safety.SafetyError, 'collision'):
            safety.plan_outputs([self.svg, hardlink], True)

    def test_cli_all_writers_refuse_existing_and_symlink_targets(self):
        spec = self.tmp / 'spec.json'
        spec.write_text(json.dumps({'concepts': [{'symbol': 'input.svg'}]}))
        for script, args, output in [('preview_sheet.py', [self.svg], 'p.html'), ('presentation_board.py', [spec], 'b.html'), ('concept_sheet.py', [self.svg], 'c.png'), ('render_png.py', [self.svg], 'r.png')]:
            with self.subTest(script=script):
                out = self.tmp / output
                primary = out.with_suffix('.svg') if script == 'concept_sheet.py' else out
                primary.symlink_to(self.tmp / 'missing')
                self.rejected(script, *args, '-o', out, '--overwrite', reason='symlink')
                primary.unlink()
                primary.write_text('untouched')
                self.rejected(script, *args, '-o', out, reason='exists')
                self.assertEqual(primary.read_text(), 'untouched')
        self.rejected('preview_sheet.py', self.svg, '-o', self.svg, '--overwrite', reason='alias')
        dist = self.tmp / 'dist'
        dist.mkdir()
        (dist / 'input-black.svg').symlink_to(self.tmp / 'missing')
        self.rejected('export_variants.py', self.svg, '--out-dir', dist, '--overwrite', reason='symlink')
        self.rejected('export_variants.py', self.svg, '--out-dir', self.tmp / 'duplicate', '--mono', '#abc', '--mono', '#aabbcc', reason='collision')
        self.assertFalse((self.tmp / 'duplicate').exists())
        self.rejected('render_png.py', self.svg, self.svg, '--out-dir', self.tmp / 'batch', reason='collision')

    def test_raster_size_padding_jobs_ico_and_audit_caps(self):
        for dimensions in [(0, 1), (-1, 1), (16385, 1), (10000, 10000), (1.5, 2), (True, 1)]:
            with self.subTest(dimensions=dimensions), self.assertRaises(safety.SafetyError):
                safety.dimensions(*dimensions)
        for padding in [float('nan'), float('inf'), -1, 0.41]:
            with self.subTest(padding=padding), self.assertRaises(safety.SafetyError):
                render.wrap_svg(self.svg, 2, 2, padding)
        for count in [-1, safety.MAX_JOBS + 1]:
            with self.assertRaisesRegex(safety.SafetyError, 'job'):
                safety.jobs(count)
        self.rejected('render_png.py', self.svg, '--size', '0', reason='raster dimensions')
        self.rejected('render_png.py', self.svg, '--ico', self.tmp / 'f.ico', '--ico-sizes', '257', reason='1 to 256')
        self.rejected('render_png.py', self.svg, '--ico', self.tmp / 'f.ico', '--ico-sizes', '16', '16', reason='unique')
        self.rejected('preview_sheet.py', self.svg, '--refs-count', '-1', reason='refs-count')
        self.rejected('preview_sheet.py', *([self.svg] * 257), reason='job limit')
        self.svg.write_text('<svg viewBox="0 0 32 32">' + '<rect width="1" height="1"/>' * 4 + '</svg>')
        with mock.patch.object(safety, 'MAX_AUDIT_PAIRS', 2), self.assertRaisesRegex(safety.SafetyError, 'pair-work'):
            svg_audit.audit(self.svg)
        bad = self.tmp / 'bad.png'
        bad.write_bytes(png(3, 2))
        with self.assertRaisesRegex(safety.SafetyError, 'square'):
            render.write_ico([bad], self.tmp / 'bad.ico')

    def test_fresh_backend_staging_wrong_dimensions_and_failures(self):
        dest = self.tmp / 'result.png'
        old = png(2, 2)
        dest.write_bytes(old)
        with mock.patch.object(render, 'available_backends', return_value=['rsvg-convert']), mock.patch.dict(render.BACKENDS, {'rsvg-convert': lambda *a: None}):
            with self.assertRaises(OSError):
                render.render(self.svg, dest, 2, 2, overwrite=True)
        self.assertEqual(dest.read_bytes(), old)
        def wrong(source, output, w, h):
            Path(output).write_bytes(png(1, 1))
        with mock.patch.dict(render.BACKENDS, {'rsvg-convert': wrong}), self.assertRaisesRegex(RuntimeError, 'dimensions mismatch'):
            render.render(self.svg, dest, 2, 2, backend='rsvg-convert', overwrite=True)
        self.assertEqual(dest.read_bytes(), old)
        with mock.patch.dict(render.BACKENDS, {'rsvg-convert': mock.Mock(side_effect=safety.SafetyError('planted safety violation')), 'chrome': mock.Mock()}) as backends, mock.patch.object(render, 'available_backends', return_value=['rsvg-convert', 'chrome']):
            with self.assertRaisesRegex(safety.SafetyError, 'planted safety violation'):
                render.render(self.svg, self.tmp / 'safe.png', 2, 2)
            backends['chrome'].assert_not_called()
        def good(source, output, w, h):
            self.assertFalse(Path(output).exists())
            Path(output).write_bytes(png(w, h))
        failure = mock.Mock(side_effect=RuntimeError('dummy backend failed'))
        with mock.patch.dict(render.BACKENDS, {'rsvg-convert': failure, 'chrome': good}), mock.patch.object(render, 'available_backends', return_value=['rsvg-convert', 'chrome']):
            self.assertEqual(render.render(self.svg, dest, 2, 2, overwrite=True), 'chrome')
        with mock.patch.object(render, 'available_backends', return_value=[]), self.assertRaisesRegex(RuntimeError, 'no available backend'):
            render.render(self.svg, self.tmp / 'nothing.png', 2, 2)

    def test_requested_raster_failures_are_not_swallowed(self):
        for module, argv in [(export, ['export', str(self.svg), '--out-dir', str(self.tmp / 'export'), '--png', '16']), (export, ['export', str(self.svg), '--out-dir', str(self.tmp / 'web'), '--web-icons']), (concept, ['concept', str(self.svg), '-o', str(self.tmp / 'concept.png')])]:
            with self.subTest(module=module, argv=argv), mock.patch.object(sys, 'argv', argv), mock.patch.object(render, 'render', side_effect=RuntimeError('dummy requested raster failure')), contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'dummy requested raster failure'):
                module.main()
        spec = self.tmp / 'spec.json'
        spec.write_text(json.dumps({'concepts': [{'symbol': 'input.svg'}]}))
        with mock.patch.object(sys, 'argv', ['board', str(spec), '-o', str(self.tmp / 'board.html'), '--png-dir', str(self.tmp / 'slides')]), mock.patch.object(render, '_screenshot_generated', side_effect=RuntimeError('dummy browser failure')), contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'dummy browser failure'):
            board.main()
        dummy_bin = self.tmp / 'bin'
        dummy_bin.mkdir()
        executable = dummy_bin / 'rsvg-convert'
        executable.write_text('#!/bin/sh\nexit 7\n')
        executable.chmod(0o700)
        if os.name == 'posix':
            result = self.cli('render_png.py', self.svg, '-o', self.tmp / 'failure.png', '--backend', 'rsvg-convert', env={'PATH': str(dummy_bin)})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('render failed', result.stderr)
            self.assertFalse((self.tmp / 'failure.png').exists())
            (dummy_bin / 'cairosvg.py').write_text('def svg2png(**kwargs):\n    raise RuntimeError("dummy cairo failure")\n')
            result = self.cli('export_variants.py', self.svg, '--out-dir', self.tmp / 'actual-fail', '--png', '16', env={'PATH': str(dummy_bin), 'PYTHONPATH': str(dummy_bin)})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('render failed', result.stderr)
            self.assertFalse(list((self.tmp / 'actual-fail').glob('*.png')))

    def test_native_subprocess_timeout_contract(self):
        with mock.patch.object(subprocess, 'run') as run:
            render._rsvg('dummy.svg', 'dummy.png', 1, 1)
            render._inkscape('dummy.svg', 'dummy.png', 1, 1)
            self.assertEqual(run.call_count, 2)
            for call in run.call_args_list:
                self.assertEqual(call.kwargs['timeout'], safety.RENDER_TIMEOUT)
                self.assertTrue(call.kwargs['check'])
                self.assertNotIn('shell', call.kwargs)
        with mock.patch.object(safety, 'RENDER_TIMEOUT', 0.1), self.assertRaises(subprocess.TimeoutExpired):
            render._run([sys.executable, '-c', 'import time; time.sleep(3)'])

    def test_optional_backend_contracts(self):
        cairo = mock.Mock()
        with mock.patch.dict(sys.modules, {'cairosvg': cairo}):
            render._cairosvg(str(self.svg), str(self.tmp / 'c.png'), 2, 2)
        self.assertEqual(cairo.svg2png.call_args.kwargs['bytestring'], self.svg.read_bytes())
        self.assertNotIn('url', cairo.svg2png.call_args.kwargs)
        def quicklook(command):
            self.assertEqual(command[0], 'qlmanage')
            Path(command[-1] + '.png').write_bytes(png(2, 2))
        with mock.patch.dict(sys.modules, {'PIL': None}), mock.patch.object(render, '_run', side_effect=quicklook), contextlib.redirect_stderr(io.StringIO()) as stderr:
            render._qlmanage(str(self.svg), str(self.tmp / 'q.png'), 2, 2)
            self.assertIn('opaque white', stderr.getvalue())
            with self.assertRaisesRegex(RuntimeError, 'Pillow'):
                render._qlmanage(str(self.svg), str(self.tmp / 'q2.png'), 2, 1)
        self.assertEqual(render.png_size(self.tmp / 'q.png'), (2, 2))

    def test_private_generated_browser_and_no_html_cli(self):
        self.assertFalse(hasattr(render, 'screenshot_html'))
        arbitrary = self.tmp / 'dummy.html'
        arbitrary.write_text('<p>dummy</p>')
        self.rejected('render_png.py', arbitrary, '-o', self.tmp / 'dummy.png', reason='.svg input')
        captured = []
        def browser(command):
            page = Path(command[-1].removeprefix('file://'))
            text = page.read_text()
            captured.append((command, text))
            shot = next(v.split('=', 1)[1] for v in command if v.startswith('--screenshot='))
            Path(shot).write_bytes(png(2, 2))
        with mock.patch.object(render, 'find_chrome', return_value='dummy-chrome'), mock.patch.object(render, '_run', side_effect=browser):
            render._screenshot_generated('<!doctype html><html><head></head><body>dummy</body></html>', self.tmp / 'browser.png', 2, 2)
        command, text = captured[0]
        self.assertIn('Content-Security-Policy', text)
        self.assertIn("default-src 'none'", text)
        self.assertIn("img-src data:", text)
        self.assertFalse(any('no-sandbox' in a or 'disable-setuid-sandbox' in a or 'disable-web-security' in a for a in command))
        self.assertTrue(any(a.startswith('--user-data-dir=') for a in command))
        self.assertFalse(Path(command[-1].removeprefix('file://')).exists())
        self.assertEqual(render.png_size(self.tmp / 'browser.png'), (2, 2))

    @unittest.skipUnless(shutil.which('rsvg-convert'), 'native librsvg not installed')
    def test_actual_native_render_and_ico(self):
        dest = self.tmp / 'actual.png'
        self.assertEqual(render.render(self.svg, dest, 48, 32, backend='rsvg-convert'), 'rsvg-convert')
        self.assertEqual(render.png_size(dest), (48, 32))
        result = self.cli('render_png.py', self.svg, '--ico', self.tmp / 'favicon.ico', '--backend', 'rsvg-convert')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = (self.tmp / 'favicon.ico').read_bytes()
        self.assertEqual(struct.unpack('<HHH', data[:6]), (0, 1, 3))
        self.rejected('render_png.py', self.svg, '-o', dest, '--backend', 'rsvg-convert', reason='exists')
        result = self.cli('render_png.py', self.svg, '-o', dest, '--backend', 'rsvg-convert', '--overwrite', '--size', '16')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(render.png_size(dest), (16, 16))


if __name__ == '__main__':
    unittest.main()
