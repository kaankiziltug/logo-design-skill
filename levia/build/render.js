// svg2png: node render.js in.svg out.png [width] [height]
const fs = require('fs');
const path = require('path');
const { Resvg } = require('/home/user/.renderenv/node_modules/@resvg/resvg-js');
const FDIR = '/home/user/fonts';
const files = [
  path.join(FDIR,'static/F-w500-o60-s40-w0.ttf'),
  path.join(FDIR,'static/F-w600-o60-s40-w0.ttf'),
  path.join(FDIR,'static/F-w500-o60-s40-w1.ttf'),
  path.join(FDIR,'static/F-w600-o60-s40-w1.ttf'),
  path.join(FDIR,'static/F-w500-o30-s60-w0.ttf'),
  path.join(FDIR,'HindVadodara-Regular.ttf'),
  path.join(FDIR,'HindVadodara-Medium.ttf'),
  path.join(FDIR,'HindVadodara-SemiBold.ttf'),
];
const [, , input, output, w, h] = process.argv;
const svg = fs.readFileSync(input, 'utf8');
const r = new Resvg(svg, {
  fitTo: w ? { mode: 'width', value: parseInt(w,10) } : { mode: 'original' },
  background: 'rgba(0,0,0,0)',
  font: { fontFiles: files, loadSystemFonts: false, defaultFontFamily: 'Fraunces' },
});
const png = r.render().asPng();
fs.writeFileSync(output, png);
console.log('wrote', output, png.length, 'bytes');
