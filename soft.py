"""Soft "almost 3D" look for the 2D characters (STYLE=soft, the default; STYLE=flat for the old look).

- thin, soft brown outlines instead of thick ink lines (chars2 reads ON)
- every character is rendered on its own layer and shaded: lit from the top-left, darker toward its edges,
  with a faint shine, so bodies and heads look rounded
- a soft contact shadow on the floor under each character
- backgrounds slightly blurred, so the characters stand out (depth of field)
"""
import os, io
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ON = os.environ.get('STYLE', 'soft') == 'soft'
MARK = '\x01'          # motion.scene wraps each character's SVG in these
_L = np.array([-0.45, -0.62, 0.64]); _L /= np.linalg.norm(_L)


def shade(o):
    """o: RGBA layer holding one character. Returns it shaded, with a contact shadow underneath."""
    bb = o.getbbox()
    if not bb: return o
    pad = 40
    x0, y0, x1, y1 = max(0, bb[0] - pad), max(0, bb[1] - pad), min(o.width, bb[2] + pad), min(o.height, bb[3] + pad)
    c = o.crop((x0, y0, x1, y1))
    a = np.asarray(c).astype(np.float32) / 255; A = a[..., 3]
    am = Image.fromarray((A * 255).astype('uint8'))
    def lit(r):
        B = np.asarray(am.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
        gy, gx = np.gradient(B)
        n = np.stack([-gx, -gy, np.full_like(B, 0.9 / r)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
        return np.clip((n * _L).sum(-1), 0, 1), B
    d1, B1 = lit(10)                                       # small scale: rounded edges of arms, heads, legs
    d2, B2 = lit(34)                                       # large scale: the whole body turns away from the light
    d = 0.55 * d1 + 0.45 * d2
    edge = np.clip(B1 * 1.7, 0, 1)                         # 0 at the silhouette edge, 1 inside
    sh = 0.66 + 0.46 * d - 0.14 * (1 - edge)
    spec = (np.clip(d1, 0, 1) ** 10) * 0.22
    rgb = np.clip(a[..., :3] * sh[..., None] + spec[..., None], 0, 1)
    out = Image.fromarray((np.dstack([rgb, A]) * 255).astype('uint8'), 'RGBA')
    # contact shadow on the floor, under the feet
    res = Image.new('RGBA', o.size, (0, 0, 0, 0))
    w = (bb[2] - bb[0]); cx = (bb[0] + bb[2]) / 2; fy = bb[3]
    shd = Image.new('RGBA', o.size, (0, 0, 0, 0)); ImageDraw.Draw(shd).ellipse([cx - w * 0.42, fy - 14, cx + w * 0.42, fy + 12], fill=(40, 20, 10, 70))
    res.alpha_composite(shd.filter(ImageFilter.GaussianBlur(8)))
    res.alpha_composite(out, (x0, y0))
    return res


def draw(world, lay, defs, width, height, svg2png):
    """paint lay (SVG fragment) onto world; characters (between MARKs) are shaded one by one"""
    parts = lay.split(MARK)
    for k, part in enumerate(parts):
        if not part.strip(): continue
        png = svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{defs}{part}</svg>'.encode())
        o = Image.open(io.BytesIO(png)).convert('RGBA')
        if k % 2 and ON: o = shade(o)
        world.paste(o, (0, 0), o)
    return world


def background(img):
    return img.filter(ImageFilter.GaussianBlur(2.2)) if ON else img
