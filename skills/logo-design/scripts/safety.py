"""Shared static SVG, resource and output boundaries. Standard library, Python 3.9+."""
import base64
import binascii
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import tempfile
import xml.etree.ElementTree as ET
import zlib
from typing import Any, Iterable, Optional, Tuple, Union

PathInput = Union[str, os.PathLike]
SVG_NS = 'http://www.w3.org/2000/svg'
XLINK_NS = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG_NS)
ET.register_namespace('xlink', XLINK_NS)
MAX_BYTES = 8 * 1024 * 1024
MAX_ELEMENTS = 20000
MAX_DEPTH = 64
MAX_TOKENS = 250000
MAX_GEOMETRY = 10000000
MAX_EXPANSION = 200000
MAX_PIXELS = 64000000
MAX_SIDE = 16384
MAX_JOBS = 256
MAX_AUDIT_PAIRS = 2000000
MAX_CSS_RULES = 4096
MAX_DECLARATIONS = 4096
RENDER_TIMEOUT = 45
NUMBER = r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?'
NUM_RE = re.compile(NUMBER)
ID_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_.:-]*\Z')
TAGS = set('svg g defs path rect circle ellipse line polygon polyline title desc metadata text tspan clipPath mask pattern symbol marker linearGradient radialGradient stop use image filter feBlend feColorMatrix feGaussianBlur feFlood feOffset feComposite feMerge feMergeNode'.split())
ATTRS = set('id class version viewBox width height x y x1 x2 y1 y2 cx cy r rx ry dx dy d points transform gradientTransform patternTransform fill stroke color fill-rule clip-rule fill-opacity stroke-opacity opacity stroke-width stroke-miterlimit stroke-linecap stroke-linejoin stroke-dasharray stroke-dashoffset clip-path mask filter marker-start marker-mid marker-end gradientUnits gradientSpread spreadMethod gradientUnits fx fy fr offset stop-color stop-opacity maskUnits maskContentUnits patternUnits patternContentUnits filterUnits primitiveUnits color-interpolation-filters result in in2 mode type values stdDeviation flood-color flood-opacity operator k1 k2 k3 k4 preserveAspectRatio href style font-family font-size font-weight font-style text-anchor dominant-baseline letter-spacing role aria-label focusable display visibility vector-effect overflow'.split())
CSS_PROPERTIES = set('fill stroke color fill-rule clip-rule fill-opacity stroke-opacity opacity stroke-width stroke-linecap stroke-linejoin stroke-miterlimit stroke-dasharray stroke-dashoffset stop-color stop-opacity flood-color flood-opacity clip-path mask filter mask-type mix-blend-mode display visibility font-family font-size font-weight font-style text-anchor letter-spacing'.split())
GEOMETRY = set('viewBox width height x y x1 x2 y1 y2 cx cy r rx ry dx dy fx fy fr d points transform gradientTransform patternTransform offset stroke-width stroke-miterlimit stroke-dasharray stroke-dashoffset opacity fill-opacity stroke-opacity stop-opacity flood-opacity values stdDeviation k1 k2 k3 k4 font-size letter-spacing'.split())
PAINT = {'fill', 'stroke', 'color', 'stop-color', 'flood-color'}
REF_ATTR = {'clip-path', 'mask', 'filter', 'marker-start', 'marker-mid', 'marker-end'}


class SafetyError(ValueError):
    """Input violates a boundary; never reinterpret as a backend failure."""


def bounded_read(path: PathInput, limit: int = MAX_BYTES) -> bytes:
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as fh:
        if not stat.S_ISREG(os.fstat(fh.fileno()).st_mode):
            raise SafetyError('input must be a regular file')
        data = fh.read(limit + 1)
    if len(data) > limit:
        raise SafetyError('input exceeds byte limit')
    return data


def finite(value: Any, low: float = -MAX_GEOMETRY, high: float = MAX_GEOMETRY) -> float:
    if isinstance(value, bool):
        raise SafetyError('expected finite number')
    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise SafetyError('expected finite number') from exc
    if not math.isfinite(number) or not low <= number <= high:
        raise SafetyError('number outside finite geometry limits')
    return number


def dimensions(width: int, height: int) -> Tuple[int, int]:
    if type(width) is not int or type(height) is not int:
        raise SafetyError('raster dimensions must be integers')
    if not (1 <= width <= MAX_SIDE and 1 <= height <= MAX_SIDE) or width * height > MAX_PIXELS:
        raise SafetyError('raster dimensions exceed area/side limits')
    return width, height


def jobs(count: int) -> None:
    if not 0 <= count <= MAX_JOBS:
        raise SafetyError('job limit exceeded')


def canonical_color(value: str) -> str:
    if not isinstance(value, str):
        raise SafetyError('colour must be a string')
    v = value.strip().lower()
    names = {'black': '#000000', 'white': '#ffffff', 'red': '#ff0000', 'green': '#008000', 'blue': '#0000ff', 'gray': '#808080', 'grey': '#808080', 'navy': '#000080', 'teal': '#008080', 'yellow': '#ffff00', 'orange': '#ffa500', 'purple': '#800080'}
    if v in names:
        return names[v]
    if re.fullmatch(r'#[0-9a-f]{3}', v):
        return '#' + ''.join(c * 2 for c in v[1:])
    if re.fullmatch(r'#[0-9a-f]{6}', v):
        return v
    match = re.fullmatch(r'rgb\(\s*(' + NUMBER + r'%?)\s*,\s*(' + NUMBER + r'%?)\s*,\s*(' + NUMBER + r'%?)\s*\)', v)
    if match:
        parts = [round(finite(c[:-1], 0, 100) * 255 / 100) if c.endswith('%') else round(finite(c, 0, 255)) for c in match.groups()]
        return '#%02x%02x%02x' % tuple(parts)
    raise SafetyError('unsupported colour; use #rgb, #rrggbb, rgb() or a documented basic name')


def png_dimensions(data: bytes) -> Tuple[int, int]:
    """Validate chunks, CRCs, raster stream and dimensions without native decoders."""
    if len(data) > MAX_BYTES or data[:8] != b'\x89PNG\r\n\x1a\n':
        raise SafetyError('invalid PNG signature/size')
    def safe_png_metadata(kind, body):
        if kind in (b'iCCP', b'zTXt', b'iTXt'):
            raise SafetyError('compressed/international PNG metadata unsupported')
    pos, chunks, compressed, wh, interlace = 8, [], [], None, None
    w = h = depth = color = palette = 0
    idat_finished = False
    while pos < len(data):
        if pos + 12 > len(data):
            raise SafetyError('truncated PNG')
        length, kind = struct.unpack('>I4s', data[pos:pos + 8])
        end = pos + 12 + length
        if end > len(data):
            raise SafetyError('truncated PNG chunk')
        body = data[pos + 8:pos + 8 + length]
        safe_png_metadata(kind, body)
        crc = struct.unpack('>I', data[pos + 8 + length:end])[0]
        if binascii.crc32(kind + body) & 0xffffffff != crc:
            raise SafetyError('invalid PNG CRC')
        if not chunks and kind != b'IHDR':
            raise SafetyError('PNG missing IHDR')
        if kind == b'IHDR':
            if chunks or length != 13:
                raise SafetyError('invalid PNG IHDR')
            w, h, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', body)
            wh = dimensions(w, h)
            legal = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
            if depth not in legal.get(color, ()) or compression or filtering or interlace not in (0, 1):
                raise SafetyError('unsupported PNG encoding')
        elif kind == b'PLTE':
            if palette or compressed or length == 0 or length % 3 or length > 768 or color in (0, 4):
                raise SafetyError('invalid PNG palette')
            palette = length // 3
            if color == 3 and palette > 2 ** depth:
                raise SafetyError('PNG palette exceeds bit depth')
        elif kind == b'IDAT':
            if idat_finished or (color == 3 and not palette):
                raise SafetyError('invalid PNG IDAT order/palette')
            compressed.append(body)
        elif kind == b'IEND':
            if length or end != len(data):
                raise SafetyError('invalid PNG end')
        elif kind not in (b'PLTE', b'tRNS', b'gAMA', b'cHRM', b'sRGB', b'pHYs', b'bKGD', b'tEXt', b'zTXt', b'iTXt', b'tIME', b'sBIT', b'iCCP', b'eXIf'):
            raise SafetyError('unsupported PNG chunk')
        if compressed and kind != b'IDAT':
            idat_finished = True
        chunks.append(kind)
        pos = end
    if not chunks or chunks[-1] != b'IEND' or not compressed:
        raise SafetyError('incomplete PNG')
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    passes = [(0, 0, 1, 1)] if not interlace else [(0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)]
    rows = []
    for x, y, sx, sy in passes:
        pw, ph = max(0, (w - x + sx - 1) // sx), max(0, (h - y + sy - 1) // sy)
        if pw and ph:
            rows.extend([1 + (pw * channels * depth + 7) // 8] * ph)
    expected = sum(rows)
    decoder = zlib.decompressobj()
    try:
        raster = decoder.decompress(b''.join(compressed), expected + 1)
    except zlib.error as exc:
        raise SafetyError('invalid PNG raster') from exc
    if len(raster) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise SafetyError('invalid PNG raster size')
    pos = 0
    for length in rows:
        if raster[pos] > 4:
            raise SafetyError('invalid PNG row filter')
        pos += length
    return w, h


def _paint(value):
    if value in ('none', 'transparent', 'currentColor', 'inherit'):
        return
    if re.fullmatch(r'url\(#[A-Za-z_][A-Za-z0-9_.:-]*\)', value):
        return
    canonical_color(value)


def _declarations(text):
    if text.count(';') >= MAX_DECLARATIONS:
        raise SafetyError('CSS declaration limit exceeded')
    declarations = []
    for item in text.split(';'):
        if not item.strip():
            continue
        if ':' not in item:
            raise SafetyError('malformed CSS declaration')
        key, value = (s.strip() for s in item.split(':', 1))
        if key not in CSS_PROPERTIES:
            raise SafetyError('unsupported CSS property: ' + key)
        _value(key, value)
        declarations.append((key, value))
    return declarations


def stylesheet_rules(css: str) -> list:
    if re.search(r'[/\\@<>]', css):
        raise SafetyError('unsafe stylesheet')
    result, position = [], 0
    while position < len(css):
        position = re.compile(r'\s*').match(css, position).end()
        if position == len(css):
            break
        if len(result) >= MAX_CSS_RULES:
            raise SafetyError('CSS rule limit exceeded')
        opening = css.find('{', position)
        closing = css.find('}', opening + 1) if opening >= 0 else -1
        if opening < 0 or closing < 0:
            raise SafetyError('malformed stylesheet')
        selector, body = css[position:opening].strip(), css[opening + 1:closing]
        if not re.fullmatch(r'[A-Za-z0-9_.# ,:-]+', selector) or '{' in body:
            raise SafetyError('unsupported CSS selector')
        _declarations(body)
        result.append((selector, body))
        position = closing + 1
    return result


def _value(key, value):
    if any(c in value for c in '\\<>@{}') or any(ord(c) < 32 and c not in '\t\n\r' for c in value):
        raise SafetyError('unsafe attribute/CSS value')
    if key in PAINT:
        _paint(value)
    elif key in REF_ATTR:
        if value != 'none' and not re.fullmatch(r'url\(#[A-Za-z_][A-Za-z0-9_.:-]*\)', value):
            raise SafetyError('external/invalid resource reference')
    elif re.search(r'url\s*\(|expression\s*\(|(?:https?|file|data|javascript):', value, re.I):
        raise SafetyError('resource URL not allowed here')
    if key in GEOMETRY:
        if re.search(r'(?i)(?:nan|inf)', value):
            raise SafetyError('nonfinite geometry')
        for number in NUM_RE.findall(value):
            finite(number)
    if key in ('transform', 'gradientTransform', 'patternTransform'):
        transform_matrix(value)
    if key == 'points':
        if NUM_RE.sub('', value).strip(' ,\t\r\n') or len(NUM_RE.findall(value)) % 2:
            raise SafetyError('invalid points')
    if key in GEOMETRY - {'d', 'points', 'transform', 'gradientTransform', 'patternTransform', 'viewBox'}:
        residue = re.sub(NUMBER + r'(?:%|px|pt|pc|mm|cm|in|em|ex)?', '', value)
        if residue.strip(' ,\t\r\n') and value != 'none':
            raise SafetyError('invalid numeric geometry: ' + key)
    if key == 'viewBox':
        parts = re.split(r'[ ,]+', value.strip())
        if len(parts) != 4:
            raise SafetyError('invalid viewBox')
        nums = [finite(v) for v in parts]
        if nums[2] <= 0 or nums[3] <= 0:
            raise SafetyError('viewBox must have positive extent')


def path_tokens(d: str) -> list:
    if not isinstance(d, str) or len(d) > MAX_BYTES:
        raise SafetyError('path byte limit exceeded')
    argc = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}
    out, i, cmd, count = [], 0, None, 0
    while i < len(d):
        ch = d[i]
        if ch.isspace() or ch == ',':
            i += 1
            continue
        if ch.isalpha() and ch not in 'eE':
            if cmd and (count == 0 or count % argc[cmd]):
                raise SafetyError('short path command')
            if ch.upper() not in argc:
                raise SafetyError('unknown path command')
            cmd, count = ch.upper(), 0
            if not out and cmd != 'M':
                raise SafetyError('path must start with moveto')
            out.append(ch)
            i += 1
            if cmd == 'Z':
                cmd = None
            continue
        if cmd is None:
            raise SafetyError('path data without command')
        if cmd == 'A' and count % 7 in (3, 4):
            if ch not in '01':
                raise SafetyError('arc flag must be 0 or 1')
            token, i = ch, i + 1
        else:
            match = NUM_RE.match(d, i)
            if not match:
                raise SafetyError('invalid path token')
            token, i = match.group(0), match.end()
            finite(token)
        count += 1
        out.append(token)
        if len(out) > MAX_TOKENS:
            raise SafetyError('path token limit exceeded')
    if cmd and (count == 0 or count % argc[cmd]):
        raise SafetyError('short path command')
    return out


def transform_matrix(text):
    result = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    if not text:
        return result
    position = 0
    for match in re.finditer(r'([A-Za-z]+)\s*\(([^()]*)\)', text):
        if text[position:match.start()].strip(' ,\t\r\n'):
            raise SafetyError('malformed transform')
        name, args = match.groups()
        if NUM_RE.sub('', args).strip(' ,\t\r\n'):
            raise SafetyError('invalid transform number')
        values = [finite(n) for n in NUM_RE.findall(args)]
        arities = {'matrix': (6,), 'translate': (1, 2), 'scale': (1, 2), 'rotate': (1, 3), 'skewX': (1,), 'skewY': (1,)}
        if len(values) not in arities.get(name, ()):
            raise SafetyError('invalid transform command/arity')
        if name == 'matrix':
            current = tuple(values)
        elif name == 'translate':
            current = (1, 0, 0, 1, values[0], values[1] if len(values) == 2 else 0)
        elif name == 'scale':
            current = (values[0], 0, 0, values[1] if len(values) == 2 else values[0], 0, 0)
        elif name == 'rotate':
            angle = math.radians(values[0])
            c, s = math.cos(angle), math.sin(angle)
            x, y = values[1:] if len(values) == 3 else (0, 0)
            current = (c, s, -s, c, x - c * x + s * y, y - s * x - c * y)
        else:
            tangent = math.tan(math.radians(values[0]))
            current = (1, 0, tangent, 1, 0, 0) if name == 'skewX' else (1, tangent, 0, 1, 0, 0)
        result = multiply_matrix(result, current)
        position = match.end()
    if position == 0 or text[position:].strip(' ,\t\r\n'):
        raise SafetyError('malformed transform')
    return result


def multiply_matrix(a, b):
    return tuple(finite(v) for v in (a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3], a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]))


def parse_svg(data: Union[str, bytes]) -> ET.Element:
    if isinstance(data, str):
        data = data.encode('utf-8')
    if len(data) > MAX_BYTES:
        raise SafetyError('SVG exceeds byte limit')
    try:
        text = data.decode('utf-8-sig')
    except UnicodeError as exc:
        raise SafetyError('SVG must be UTF-8') from exc
    text = re.sub(r'^\s*<\?xml\s+[^?]*\?>', '', text, count=1)
    if '<!' in re.sub(r'<!--.*?-->', '', text, flags=re.S) or '<?' in text:
        raise SafetyError('DTD, entities and processing instructions are forbidden')
    try:
        root = None
        depth = count = 0
        for event, el in ET.iterparse(io.StringIO(text), events=('start', 'end')):
            if event == 'start':
                depth += 1
                count += 1
                if root is None:
                    root = el
                if depth > MAX_DEPTH or count > MAX_ELEMENTS:
                    raise SafetyError('SVG depth/element limit exceeded')
            else:
                depth -= 1
    except ET.ParseError as exc:
        raise SafetyError('invalid SVG XML') from exc
    if root is None or root.tag not in ('svg', '{' + SVG_NS + '}svg'):
        raise SafetyError('root must be SVG')
    ids, edges, token_count = {}, {}, 0
    elements = list(root.iter())
    for el in elements:
        if el.tag.startswith('{'):
            namespace, tag = el.tag[1:].split('}', 1)
            if namespace != SVG_NS:
                raise SafetyError('foreign element namespace')
        else:
            tag = el.tag
            el.tag = '{' + SVG_NS + '}' + tag
        if tag not in TAGS and tag != 'style':
            raise SafetyError('unsupported SVG element: ' + tag)
        edges[el] = list(el)
        if el.get('id'):
            ident = el.get('id')
            if not ID_RE.fullmatch(ident) or ident in ids:
                raise SafetyError('invalid/duplicate SVG id')
            ids[ident] = el
        for attr, value in el.attrib.items():
            key = attr
            if attr.startswith('{'):
                if attr != '{' + XLINK_NS + '}href':
                    raise SafetyError('foreign attribute namespace')
                key = 'href'
            if key not in ATTRS:
                raise SafetyError('unsupported SVG attribute: ' + key)
            if key == 'href':
                if value.startswith('#') and ID_RE.fullmatch(value[1:]):
                    pass
                elif tag == 'image' and value.startswith('data:image/png;base64,'):
                    try:
                        png_dimensions(base64.b64decode(value.split(',', 1)[1], validate=True))
                    except (ValueError, binascii.Error) as exc:
                        raise SafetyError('invalid embedded PNG') from exc
                else:
                    raise SafetyError('external/invalid href')
            elif key == 'style':
                _declarations(value)
            else:
                _value(key, value)
            if key == 'd':
                path_tokens(value)
            if key in GEOMETRY or key == 'style':
                token_count += len(NUM_RE.findall(value))
        if tag == 'image' and not any(a.endswith('href') for a in el.attrib):
            raise SafetyError('image missing embedded PNG')
        if tag == 'style':
            css = el.text or ''
            token_count += len(NUM_RE.findall(css))
            if list(el):
                raise SafetyError('unsafe stylesheet')
            stylesheet_rules(css)
    if token_count > MAX_TOKENS:
        raise SafetyError('SVG token limit exceeded')
    for el in elements:
        references = []
        for attr, value in el.attrib.items():
            if attr in ('href', '{' + XLINK_NS + '}href') and value.startswith('#'):
                references.append(value[1:])
            references.extend(re.findall(r'url\(#([^)]*)\)', value))
        if el.tag == '{' + SVG_NS + '}style':
            references.extend(re.findall(r'url\(#([^)]*)\)', el.text or ''))
        for ident in references:
            if ident not in ids:
                raise SafetyError('missing SVG reference: ' + ident)
            edges[el].append(ids[ident])
    def check_transforms(el, parent):
        matrix = multiply_matrix(parent, transform_matrix(el.get('transform')))
        for child in edges[el]:
            check_transforms(child, matrix)
    costs, heights, active = {}, {}, set()
    def cost(el, depth=0):
        if el in active:
            raise SafetyError('cyclic SVG reference')
        if depth > MAX_DEPTH:
            raise SafetyError('reference depth limit exceeded')
        if el in costs:
            if depth + heights[el] > MAX_DEPTH:
                raise SafetyError('reference depth limit exceeded')
            return costs[el]
        active.add(el)
        total, height = 1, 0
        for child in edges[el]:
            total += cost(child, depth + 1)
            height = max(height, 1 + heights[child])
            if total > MAX_EXPANSION:
                raise SafetyError('SVG reference expansion limit exceeded')
        active.remove(el)
        costs[el], heights[el] = total, height
        return total
    cost(root)
    for el in elements:
        cost(el)
    check_transforms(root, (1, 0, 0, 1, 0, 0))
    return root


def serialize(root: ET.Element) -> str:
    return ET.tostring(root, encoding='unicode')


def load_svg(path: PathInput) -> Tuple[str, ET.Element]:
    if Path(path).suffix.lower() != '.svg':
        raise SafetyError('expected .svg input')
    root = parse_svg(bounded_read(path))
    return serialize(root), root


def asset_path(path: str, base: PathInput, asset_root: Optional[PathInput] = None) -> str:
    if not isinstance(path, str) or not path:
        raise SafetyError('asset path must be a nonempty string')
    root = Path(asset_root or base).resolve(strict=True)
    candidate = (Path(base) / path).resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise SafetyError('asset escapes allowed root') from exc
    if not candidate.is_file() or candidate.suffix.lower() != '.svg':
        raise SafetyError('asset must be a regular SVG')
    return str(candidate)


def portable_name(name: str) -> str:
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,119}', name) or name.endswith('.'):
        raise SafetyError('name must be a portable basename')
    if name.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL'} | {'COM' + str(n) for n in range(1, 10)} | {'LPT' + str(n) for n in range(1, 10)}:
        raise SafetyError('reserved output basename')
    return name


def check_output(path: PathInput, overwrite: bool = False, inputs: Iterable[PathInput] = ()) -> Path:
    p = Path(path)
    if p.is_symlink():
        raise SafetyError('refusing symlink output')
    if p.exists() and (not overwrite or not p.is_file()):
        raise SafetyError('output exists; --overwrite permits regular files only')
    resolved = p.resolve()
    for source in inputs:
        source = Path(source)
        if resolved == source.resolve() or (p.exists() and source.exists() and os.path.samefile(p, source)):
            raise SafetyError('input/output alias')
    return p


def plan_outputs(paths: Iterable[PathInput], overwrite: bool = False, inputs: Iterable[PathInput] = ()) -> None:
    paths = list(paths)
    jobs(len(paths))
    seen = set()
    existing = []
    for path in paths:
        p = check_output(path, overwrite, inputs)
        key = os.path.normcase(str(p.resolve()))
        if key in seen or any(p.exists() and os.path.samefile(p, other) for other in existing):
            raise SafetyError('planned output collision')
        seen.add(key)
        if p.exists():
            existing.append(p)


def write_output(path: PathInput, data: Union[str, bytes], overwrite: bool = False, inputs: Iterable[PathInput] = ()) -> None:
    p = check_output(path, overwrite, inputs)
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode('utf-8')
    fd, staging = tempfile.mkstemp(prefix='.logo-', dir=str(p.parent))
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(data)
        check_output(p, overwrite, inputs)
        if overwrite:
            os.replace(staging, p)
        else:
            os.link(staging, p)
    finally:
        if os.path.exists(staging):
            os.unlink(staging)


def safe_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')


def validate_spec(spec: Any) -> dict:
    if not isinstance(spec, dict):
        raise SafetyError('spec must be an object')
    strings = set('brand tagline brief criteria industry deck_title designer date label recommendation brand_color tile_color'.split())
    lists = set('adjectives nav mockups next_steps'.split())
    for key in strings:
        if key in spec and not isinstance(spec[key], str):
            raise SafetyError(key + ' must be a string')
    for key in lists:
        if key in spec and (not isinstance(spec[key], list) or len(spec[key]) > 64 or any(not isinstance(x, str) for x in spec[key])):
            raise SafetyError(key + ' must be a bounded string list')
    for key in ('greyscale', 'final'):
        if key in spec and type(spec[key]) is not bool:
            raise SafetyError(key + ' must be boolean')
    if 'round' in spec and (type(spec['round']) is not int or not 1 <= spec['round'] <= 10000):
        raise SafetyError('round must be an integer from 1 to 10000')
    concepts = spec.get('concepts', [])
    if not isinstance(concepts, list) or len(concepts) > 32:
        raise SafetyError('concepts must be a list of at most 32')
    asset_keys = set('symbol lockup avatar stacked symbol_on_dark symbol_on_tile lockup_on_dark lockup_on_tile stacked_on_dark stacked_on_tile'.split())
    for concept in concepts:
        if not isinstance(concept, dict):
            raise SafetyError('concept must be an object')
        for key in asset_keys | {'name', 'idea'}:
            if key in concept and not isinstance(concept[key], str):
                raise SafetyError('concept ' + key + ' must be a string')
        rationale = concept.get('rationale', [])
        if not isinstance(rationale, list) or len(rationale) > 64 or any(not isinstance(s, str) for s in rationale):
            raise SafetyError('rationale must be a bounded string list')
        if not any(concept.get(k) for k in ('symbol', 'lockup', 'avatar')):
            raise SafetyError('concept requires artwork')
    for key in ('brand_color', 'tile_color'):
        if key in spec:
            spec[key] = canonical_color(spec[key])
    return spec
