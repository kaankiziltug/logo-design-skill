const fs = require('fs');
const { textPath } = require('/home/user/levia/build/type2path.js');
const F = '/home/user/fonts/static/';
const rows = [
  ['F-w500-o60-s40-w0.ttf', 'Levia', 92],
  ['F-w600-o60-s40-w0.ttf', 'Levia', 92],
  ['F-w500-o60-s40-w1.ttf', 'Levia', 92],
  ['F-w500-o60-s40-w0.ttf', 'levia', 92],
  ['F-w500-o30-s60-w0.ttf', 'Levia', 92],
];
let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="640" viewBox="0 0 1100 640">
<rect width="1100" height="640" fill="#F2EFE9"/>`;
rows.forEach(([file, txt, size], i) => {
  const y = 120 + i * 105;
  const r = textPath(F + file, txt, size, -1.5);
  svg += `<text x="40" y="${y - 55}" font-family="HindVadodara" font-size="13" fill="#8B8B84">${file} · ${txt} · ${size}px</text>`;
  svg += `<g transform="translate(40 ${y})"><path d="${r.d}" fill="#3A4C40"/></g>`;
});
// supporting line
svg += `<text x="40" y="600" font-family="HindVadodara" font-size="22" fill="#3A4C40">Hind Vadodara — supporting text, 22 px</text>`;
svg += `</svg>`;
fs.writeFileSync('/home/user/levia/src/type-test.svg', svg);
console.log('ok');
