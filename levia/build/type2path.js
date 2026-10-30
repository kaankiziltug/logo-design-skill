const opentype = require('/home/user/.renderenv/node_modules/opentype.js');
const fs = require('fs');
const cache = {};
function load(fontPath) {
  if (cache[fontPath]) return cache[fontPath];
  const buf = fs.readFileSync(fontPath);
  const f = opentype.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
  cache[fontPath] = f; return f;
}
function textPath(fontPath, text, size, tracking = 0) {
  const font = load(fontPath);
  const scale = size / font.unitsPerEm;
  const gl = font.stringToGlyphs(text);
  let x = 0, d = '';
  for (let i = 0; i < gl.length; i++) {
    const g = gl[i];
    d += g.getPath(x, 0, size, {}).toPathData(2) + ' ';
    let adv = g.advanceWidth;
    if (gl[i + 1]) adv += font.getKerningValue(gl[i], gl[i + 1]) || 0;
    x += adv * scale + tracking;
  }
  const total = x - (tracking || 0) + (tracking ? 0 : 0);
  const bb = font.getPath(text, 0, 0, size, { kerning: true }).getBoundingBox();
  const last = gl[gl.length - 1];
  const inkWidth = (x - (tracking ? tracking : 0)) - (last.advanceWidth * scale - last.getBoundingBox().x2 * (last.getBoundingBox().x2 ? 1 : 1));
  return { d: d.trim(), advance: x, bb, font };
}
module.exports = { textPath, load };
if (require.main === module) {
  const [, , fp, t, s] = process.argv;
  const r = textPath(fp, t, parseFloat(s || 100));
  console.log('bb', r.bb, 'advance', r.advance);
  console.log(r.d.slice(0, 300));
}
