import json, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

def run(fontpath, text, tracking=0.0):
    f = TTFont(fontpath)
    upem = f['head'].unitsPerEm
    cmap = f.getBestCmap()
    hmtx = f['hmtx']
    gs = f.getGlyphSet()
    glyphs, x = [], 0.0
    x1=y1=1e18; x2=y2=-1e18
    for ch in text:
        gname = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
        tp = TransformPen(pen, Transform(1, 0, 0, -1, 0, 0))
        gs[gname].draw(tp)
        bp = BoundsPen(gs)
        gs[gname].draw(bp)
        if bp.bounds:
            bx1, by1, bx2, by2 = bp.bounds
            x1 = min(x1, bx1 + x); x2 = max(x2, bx2 + x)
            y1 = min(y1, -by2);    y2 = max(y2, -by1)
        glyphs.append({'ch': ch, 'adv': hmtx[gname][0], 'd': pen.getCommands()})
        x += hmtx[gname][0] + tracking * upem
    return {'upem': upem, 'advance': x, 'bbox': [x1, y1, x2, y2], 'glyphs': glyphs}

if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.0)))
