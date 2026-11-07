# Static-input and output boundaries

The tools require Python 3.9 or newer and only the standard library. Renderers are
optional installed programs/packages; nothing downloads or installs a renderer.

## Intentional CLI changes

- SVG inputs must be UTF-8 `.svg` regular files containing a supported static SVG
  tree. Every embed, transform and renderer receives serialized validated XML,
  never the original bytes. Quoted attributes, default SVG and xlink namespaces
  are preserved by XML serialization rather than regular-expression tag surgery.
- Scripts, events, animation, foreign namespaces/content, unknown SVG elements or
  attributes, DTD/entity declarations and processing instructions are rejected.
  Simple style rules and an allowlisted set of presentation declarations are
  supported; imports, escaped CSS, external URLs and unsupported CSS properties
  are rejected. Only internal fragment references and validated embedded PNGs
  are resources. Missing/duplicate IDs, cycles, excessive reference expansion
  and excessive composed transforms are errors. Masks, filters, gradients,
  patterns, use, inline styles and the bundled waffle-icon PNG remain supported.
  All 1,432 bundled SVG assets have a corpus regression test; none are excluded.
- PNG checks cover signature, chunk framing/CRC, critical ordering/palette,
  dimensions, bounded decompression to the exact expected row size (including
  Adam7), row filter codes and a complete end marker. Compressed/international
  metadata chunks (iCCP, zTXt and iTXt) are intentionally unsupported. Ordinary
  PNG metadata, including the bundled image's eXIf, is accepted. This is not a
  replacement for maintaining current native image/XML libraries.
- Presentation JSON is typed. Text is escaped; colours are canonical `#rrggbb`.
  Accepted colour inputs are complete `#rgb`, `#rrggbb`, comma-separated `rgb()`
  (channels 0..255 or percentages 0..100), and these basic names: black, white,
  red, green, blue, gray/grey, navy, teal, yellow, orange, purple. Alpha, trailing
  CSS, out-of-range channels and unknown names are errors, not silent skips.
- Paths selected by presentation JSON resolve relative to the resolved spec's
  directory, and must remain inside it after resolving symlinks. In-root absolute
  paths and in-root symlinks work. Only the owner-selected CLI `--asset-root DIR`
  may widen that root; a JSON field cannot. Explicit command-line SVG inputs and
  output directories may be anywhere the owner chooses, not just the skill.
- All deliverable writers default to no-clobber. `--overwrite` permits replacing
  regular files, never directories or symlinks (including dangling symlinks).
  Inputs cannot alias outputs, including hardlinks. Multi-output plans reject
  collisions before publication. Export `--name` must be an ASCII portable
  basename, 1..120 characters, start with an alphanumeric character, use only
  alphanumerics/period/underscore/hyphen, not end with a period, and not use a
  reserved Windows device stem. Use a different name or explicit `--overwrite`
  for reruns. `build_catalog.py --overwrite` regenerates existing library files.
- Rendering occurs in fresh private staging; missing, corrupt, incomplete or
  wrongly sized PNGs cannot turn an old destination into a reported success.
  Requested PNG/ICO/board-slide failures exit nonzero; SVG/HTML already written
  by a multi-output command can remain, but a failed PNG is not published.
- `render_png.py` no longer screenshots HTML input files. Open HTML previews in
  your browser/tool instead. Board `--png-dir` still renders each freshly built
  slide through a private in-memory generated-document function. The Chrome SVG
  backend uses the same function. It writes a temporary generated document,
  uses a private browser profile, restrictive CSP (`default-src 'none'`, data
  images and inline styles only), and never disables the browser sandbox. It
  has no caller-file trust marker, HTML sanitization claim or public escape hatch.
- The reference gallery encodes `<` in its embedded JSON and puts metadata in
  DOM `textContent`; only a validated basename selects an encoded local image.

## Resource limits

The single source of truth is `scripts/safety.py`. Limits deliberately exceed
normal logo work; exceeding one is an explicit error, not a truncated export.

| Boundary | Limit |
|---|---:|
| SVG, JSON/catalog read or PNG bytes per file | 8 MiB |
| XML elements per SVG | 20,000 |
| XML nesting and expanded reference depth | 64 |
| Numeric/path tokens per SVG, including CSS numbers | 250,000 |
| Absolute numeric input/composed matrix or audited coordinate | 10,000,000, finite only |
| Expanded XML/resource-reference work per SVG | 200,000 nodes |
| Simple CSS rules per style block | 4,096 |
| Declarations per inline style or rule | 4,096 |
| Raster side | 16,384 px |
| Raster area, including embedded PNG | 64,000,000 pixels |
| CLI batch/planned outputs | 256 jobs |
| Presentation concepts; entries per text list | 32; 64 |
| Audit candidate shape pairs | 2,000,000 |
| Native renderer/browser subprocess call | 45 seconds |
| Private generated browser document | 128 MiB |

Malformed/unknown/short path commands are rejected; closing a subpath clears the
current command, so `M0 0 Z 1` cannot spin. Numerically degenerate arc radii below
1e-100 are treated as straight segments by the advisory geometry sampler.
The catalog builder processes the bundled corpus individually rather than
subjecting its 1,432 entries to the user-facing batch-job cap.

## Residual trust and limits

Use input and output directories controlled by the owner, not ones a hostile
concurrent process can rename or mutate. Checks resolve roots and reject output
symlinks, but do not provide directory-descriptor isolation or cross-file
transactions. Fresh same-directory staging and exclusive publication prevent
ordinary accidental clobbers; `--overwrite` checks immediately before atomic
replacement, but concurrent directory changes are outside the guarantee.

The renderer binaries and optional packages are trusted executable dependencies.
CairoSVG, PNG validation and optional Pillow/Quick Look matting run in-process:
size/structure/work caps are not hard CPU, address-space or memory limits.
Native subprocesses have timeouts, not an OS resource sandbox. The CSP limits
what generated pages can load; it is not a host/process or browser-network
sandbox. No claim is made that native renderers are bug-free. Quick Look needs
optional Pillow for non-square cropping and transparency recovery; otherwise
exact-size square output can remain opaque white with an explicit note.

## Verification

From the checkout, set `PYTHONDONTWRITEBYTECODE=1` and a task-owned `TMPDIR`, then
run twice on unchanged code:

```
python3 -m unittest discover -s tests -v
python3 tools/smoke_test.py
```

`tests/test_security.py` covers each boundary with dummy fixtures, real CLI
subprocesses, mocked backend failure/staging/browser contracts, all library
assets, and actual librsvg PNG/ICO output when installed. Native malformed-input
and timeout probes are bounded. Optional browser/CairoSVG/Quick Look availability
is not implied by a mocked contract test. `LOGO_TEST_SCRIPTS` permits running the
security tests against an isolated mutant scripts copy; never mutate a live
installed skill or run security probes against real secrets.
