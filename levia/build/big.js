const fs=require('fs');
const {G}=require('/home/user/levia/build/marks2.js');
const d=G.fold.d(28);
let s=`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620">
<rect width="1200" height="620" fill="#F2EFE9"/>
<g transform="translate(40 40) scale(2.2)"><path d="${d}" fill="#3A4C40"/></g>
<g transform="translate(700 40)"><path d="${d}" fill="#3A4C40"/></g>
</svg>`;
fs.writeFileSync('/home/user/levia/src/big.svg',s);
