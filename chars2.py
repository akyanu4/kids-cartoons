"""Version 2 characters: proper faces (eye whites, irises, lids, lashes, brows, nose, lips, cheek shading),
hands with fingers and a thumb, bending elbows and knees, shoulders that lift, body lean and sway.
Ali is drawn after the user's son (round face, spiky black hair under a white topi, red T-shirt);
Nana after the elder's photo (grey hair, short white beard, aviator glasses, white kurta with buttons and a pocket).

Origin = between the feet; face +1 = right, -1 = left. Angles in degrees: 0 hangs down, 90 points forward, 180 up.
State keys (all optional except x, y):
  s, face, walk (phase), bob, lean, expr, talk (0..1 mouth), blink (0..1), look (-1..1 horizontal), look_y,
  arm_f / arm_b (shoulder angle), elb_f / elb_b (elbow bend), hand_f / hand_b ('relax','open','point','hold','wave','fist'),
  hold ('bottle'), hold_tilt."""
import math

INK = '#3b2a20'
STROKE = 5


import soft as _soft
if _soft.ON: INK = '#5e4434'          # soft look: thin warm-brown outlines instead of thick dark ink
def SW(w=STROKE): return f'stroke="{INK}" stroke-width="{w * 0.5 if _soft.ON else w}" stroke-linejoin="round" stroke-linecap="round"'


def shade(hexc, f=0.82):
    h = hexc.lstrip('#'); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x' % (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)))


DEFS = ('<defs>'
        '<radialGradient id="blush"><stop offset="0" stop-color="#ff7d7d" stop-opacity=".55"/><stop offset="1" stop-color="#ff7d7d" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="glass" cx=".35" cy=".3"><stop offset="0" stop-color="#ffffff" stop-opacity=".55"/><stop offset="1" stop-color="#c9e6f5" stop-opacity=".18"/></radialGradient>'
        '</defs>')

# ------------------------------------------------------------------ expressions
# brow: raise (-1 low .. 1 high), tilt (+ inner ends up = sad/worried, - = cross/focused)
# open: eye openness, squint: lower lid up, mouth: curve (-1 frown .. 1 smile), mopen: base mouth opening, closed: ^^ eyes
EXPR = {
    'neutral':    dict(raise_=0.0, tilt=0.0, open=1.0, squint=0.0, curve=0.35, mopen=0.0),
    'happy':      dict(raise_=0.25, tilt=0.0, open=0.95, squint=0.35, curve=1.0, mopen=0.15),
    'gentle':     dict(raise_=0.15, tilt=0.15, open=0.9, squint=0.3, curve=0.7, mopen=0.0),
    'warm':       dict(raise_=0.15, tilt=0.1, open=0.85, squint=0.35, curve=0.8, mopen=0.0),
    'proud':      dict(raise_=0.3, tilt=0.0, open=0.8, squint=0.45, curve=0.9, mopen=0.05),
    'excited':    dict(raise_=0.6, tilt=0.0, open=1.1, squint=0.1, curve=1.0, mopen=0.35),
    'laugh':      dict(raise_=0.5, tilt=0.0, open=1.0, squint=0.0, curve=1.0, mopen=0.75, closed=True),
    'surprised':  dict(raise_=1.0, tilt=0.0, open=1.25, squint=0.0, curve=0.0, mopen=0.55, o=True),
    'sad':        dict(raise_=0.1, tilt=0.9, open=0.8, squint=0.0, curve=-0.8, mopen=0.0, look_y=0.5),
    'worried':    dict(raise_=0.35, tilt=0.8, open=1.0, squint=0.0, curve=-0.45, mopen=0.05, wavy=True),
    'tired':      dict(raise_=-0.2, tilt=0.35, open=0.55, squint=0.0, curve=-0.2, mopen=0.3),
    'thoughtful': dict(raise_=0.3, tilt=-0.2, open=0.9, squint=0.15, curve=0.15, mopen=0.0, look_y=-0.7, side=True),
    'angry':      dict(raise_=-0.3, tilt=-0.9, open=1.05, squint=0.2, curve=-0.7, mopen=0.25),
    'naughty':    dict(raise_=0.35, tilt=-0.25, open=0.85, squint=0.4, curve=1.0, mopen=0.1, side=True),   # cheeky: one brow up, sly smile
}


def ex(name):
    e = dict(EXPR['neutral'])
    e.update(name if isinstance(name, dict) else EXPR.get(name or 'neutral', {})); return e


_UID = 0


def face(r, st, kind):
    """Face features centred on (0,0) of a head of radius r. kind: 'ali' | 'maryam' | 'nana'."""
    global _UID
    _UID += 1; u = _UID
    e = ex(st.get('expr')); talk = st.get('talk', 0); blink = st.get('blink', 0)
    look = st.get('look', 0.35); look_y = st.get('look_y', e.get('look_y', 0))
    fx = r * 0.14                    # features turned a little toward the facing side
    ey = -r * 0.06; exs = r * 0.36; ew, eh = (r * 0.22, r * 0.195) if _soft.ON else (r * 0.2, r * 0.17)   # soft look: bigger eyes
    s = ''
    # cheek blush + soft shading on the far side
    s += f'<ellipse cx="{fx - exs - r*.08}" cy="{r*.3}" rx="{r*.24}" ry="{r*.16}" fill="url(#blush)"/>'
    s += f'<ellipse cx="{fx + exs + r*.08}" cy="{r*.3}" rx="{r*.24}" ry="{r*.16}" fill="url(#blush)"/>'
    openv = e['open'] * (1 - blink) * (1 - 0.5 * max(0.0, min(1.0, st.get('look_y', e.get('look_y', 0)))))
    for sx in (-1, 1):
        cx = fx + sx * exs * (0.92 if sx < 0 else 1.0)   # far eye a bit closer (3/4 view)
        wq = ew * (0.9 if sx < 0 else 1.0)
        if st.get('wink') and sx < 0 and not e.get('closed'):   # a cheeky wink with the far eye
            s += f'<path d="M{cx-wq},{ey} Q{cx},{ey-r*.09} {cx+wq},{ey}" fill="none" {SW(5)}/>'
        elif e.get('closed') or openv < 0.12:
            curve = -r * .09 if e.get('closed') else r * .03
            s += f'<path d="M{cx-wq},{ey} Q{cx},{ey+curve} {cx+wq},{ey}" fill="none" {SW(4.5)}/>'
            if kind == 'maryam':
                s += f'<path d="M{cx+wq*.7},{ey-2} l{wq*.35},{-r*.06} M{cx+wq*.95},{ey+2} l{wq*.4},{-r*.02}" {SW(3)}/>'
        else:
            h = eh * openv; cid = f'e{kind}{sx}_{u}'
            top = ey - h; bot = ey + h * (1 - 0.55 * e['squint'])
            eye = f'M{cx-wq},{ey} Q{cx-wq*.6},{top} {cx},{top} Q{cx+wq*.6},{top} {cx+wq},{ey} Q{cx+wq*.5},{bot} {cx},{bot} Q{cx-wq*.5},{bot} {cx-wq},{ey}Z'
            ix = cx + look * wq * 0.42; iy = ey + look_y * h * 0.8 + h * 0.08
            ir = eh * 0.72
            s += f'<clipPath id="{cid}"><path d="{eye}"/></clipPath><path d="{eye}" fill="#fff"/>'
            s += (f'<g clip-path="url(#{cid})"><circle cx="{ix}" cy="{iy}" r="{ir}" fill="#6b3d22"/><circle cx="{ix}" cy="{iy}" r="{ir*.62}" fill="#3a1f10"/>'
                  f'<circle cx="{ix}" cy="{iy}" r="{ir*.42}" fill="#120a06"/><circle cx="{ix+ir*.38}" cy="{iy-ir*.4}" r="{ir*.24}" fill="#fff"/>'
                  f'<circle cx="{ix-ir*.3}" cy="{iy+ir*.35}" r="{ir*.1}" fill="#fff" opacity=".8"/>'
                  f'<rect x="{cx-wq}" y="{top-2}" width="{2*wq}" height="{h*.32}" fill="#000" opacity=".1"/></g>')
            # upper lid (heavier line), lower lid (thin)
            s += f'<path d="M{cx-wq-2},{ey+1} Q{cx-wq*.6},{top-1} {cx},{top-1} Q{cx+wq*.6},{top-1} {cx+wq+2},{ey-1}" fill="none" {SW(5)}/>'
            s += f'<path d="M{cx-wq*.7},{bot-h*.15} Q{cx},{bot+1.5} {cx+wq*.7},{bot-h*.15}" fill="none" stroke="{INK}" stroke-width="2" opacity=".55"/>'
            if e['open'] < 0.7:   # tired: heavy lid fold
                s += f'<path d="M{cx-wq},{top-5} Q{cx},{top-10} {cx+wq},{top-5}" fill="none" stroke="{INK}" stroke-width="2.2" opacity=".6"/>'
            if kind == 'maryam':
                for k in range(3):
                    a0 = 0.45 + k * 0.25
                    px = cx + wq * a0; py = top + (ey - top) * (a0 - 0.2) ** 2
                    s += f'<path d="M{px},{py} l{wq*.32},{-r*.07 + k*2}" {SW(3)}/>'
        # eyebrows
        braise = e['raise_'] * r * 0.09
        inner = cx - sx * wq * 0.9 if False else None
        bx0, bx1 = cx - wq * 1.05, cx + wq * 1.05      # left -> right
        by = ey - eh * 1.9 - braise
        # inner end is the one toward the nose: for the left eye (sx=-1) that is bx1
        tilt = e['tilt'] * r * 0.1
        y0 = by + (0 if sx < 0 else -tilt); y1 = by + (-tilt if sx < 0 else 0)
        if e.get('side') and sx > 0: y0 -= r * .06; y1 -= r * .08
        col = '#2a1a12' if kind != 'nana' else '#8f8a85'
        bw = 7 if kind == 'ali' else (5.5 if kind == 'maryam' else 7)
        s += f'<path d="M{bx0},{y0} Q{(bx0+bx1)/2},{min(y0,y1) - r*.05} {bx1},{y1}" fill="none" stroke="{col}" stroke-width="{bw}" stroke-linecap="round"/>'
    # nose (soft)
    nx = fx + r * 0.04; ny = r * 0.16
    s += f'<path d="M{nx+2},{ey+r*.05} Q{nx+r*.1},{ny} {nx+r*.02},{ny+r*.06}" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linecap="round" opacity=".75"/>'
    s += f'<ellipse cx="{nx-r*.03}" cy="{ny+r*.07}" rx="{r*.07}" ry="{r*.035}" fill="#000" opacity=".1"/>'
    # mouth
    my = r * 0.45; mw = r * (0.24 + 0.06 * max(0, e['curve']))
    op = max(e['mopen'], 0) * 0.55 + talk
    op = min(op, 1.15)
    if e.get('o') and talk < 0.35:
        op = max(op, 0.5)
        s += f'<ellipse cx="{fx}" cy="{my+r*.04}" rx="{r*.09}" ry="{r*(.07+.08*op)}" fill="#6e1f2a" {SW(4)}/>'
    elif op > 0.12:
        h = r * (0.06 + 0.24 * op); c = e['curve']
        top = my - r * 0.02 + (-c * r * .05)
        corner = my - c * r * 0.07
        bot = my + h + c * r * .05
        d = f'M{fx-mw},{corner} Q{fx},{top} {fx+mw},{corner} Q{fx+mw*.6},{bot} {fx},{bot} Q{fx-mw*.6},{bot} {fx-mw},{corner}Z'
        cid = f'm{kind}_{u}'
        s += f'<clipPath id="{cid}"><path d="{d}"/></clipPath><path d="{d}" fill="#6e1f2a"/>'
        s += f'<g clip-path="url(#{cid})"><rect x="{fx-mw}" y="{top-4}" width="{2*mw}" height="{r*.07}" fill="#fff"/><ellipse cx="{fx}" cy="{bot}" rx="{mw*.6}" ry="{h*.38}" fill="#e2727c"/></g>'
        s += f'<path d="{d}" fill="none" {SW(4)}/>'
        if kind != 'nana': s += f'<path d="M{fx-mw*.55},{bot+r*.05} Q{fx},{bot+r*.09} {fx+mw*.55},{bot+r*.05}" fill="none" stroke="#c26a6a" stroke-width="3" opacity=".6"/>'
    else:
        c = e['curve']
        if e.get('wavy'):
            s += f'<path d="M{fx-mw*.8},{my+2} q{mw*.4},{-r*.05} {mw*.8},0 t{mw*.8},0" fill="none" {SW(4)}/>'
        else:
            s += f'<path d="M{fx-mw},{my - c*r*.04} Q{fx},{my + c*r*.12} {fx+mw},{my - c*r*.04}" fill="none" {SW(4.5)}/>'
            # lower lip
            if kind != 'nana':
                s += f'<path d="M{fx-mw*.45},{my + c*r*.08 + r*.06} Q{fx},{my + c*r*.1 + r*.1} {fx+mw*.45},{my + c*r*.08 + r*.06}" fill="none" stroke="#c26a6a" stroke-width="4" stroke-linecap="round" opacity=".7"/>'
    if st.get('sweat'):
        k = st['sweat'] % 1
        s += f'<path d="M{-r*.85},{-r*.2 + k*r*.5} q-9,15 0,22 q9,-7 0,-22Z" fill="#8fd8ff" stroke="#3b7fb3" stroke-width="3" opacity="{1-k*.8}"/>'
    return s


def face_profile(r, st, kind, skin):
    """Side view, facing +x in head space (used in ruku and sajda, so the face points at the floor)."""
    blink = st.get('blink', 0)
    s = f'<ellipse cx="{-r*.3}" cy="{r*.08}" rx="{r*.12}" ry="{r*.17}" fill="{shade(skin,.9)}" stroke="{INK}" stroke-width="3.5"/>'       # ear
    s += f'<path d="M{-r*.33},{r*.0} q{r*.05},{r*.08} 0,{r*.15}" fill="none" stroke="{INK}" stroke-width="2.2" opacity=".5"/>'
    # nose sticking out past the outline
    s += (f'<path d="M{r*.9},{-r*.12} Q{r*1.18},{r*.14} {r*1.0},{r*.24} Q{r*.92},{r*.28} {r*.86},{r*.22}Z" fill="{skin}" {SW(4)}/>')
    ex_, ey_ = r * .58, -r * .1
    if blink > 0.5 or st.get('eyes_down'):    # closed / lowered: a soft downward lid line with lashes
        s += f'<path d="M{ex_-r*.11},{ey_-r*.01} Q{ex_},{ey_+r*.07} {ex_+r*.12},{ey_+r*.02}" fill="none" {SW(4)}/>'
    else:
        s += f'<path d="M{ex_-r*.1},{ey_} Q{ex_},{ey_-r*.14} {ex_+r*.12},{ey_+r*.01} Q{ex_},{ey_+r*.1} {ex_-r*.1},{ey_}Z" fill="#fff" {SW(3.5)}/>'
        s += f'<circle cx="{ex_+r*.05}" cy="{ey_}" r="{r*.065}" fill="#3a1f10"/><circle cx="{ex_+r*.07}" cy="{ey_-r*.03}" r="{r*.022}" fill="#fff"/>'
        if kind == 'maryam': s += f'<path d="M{ex_+r*.1},{ey_-r*.05} l{r*.08},{-r*.05}" {SW(3)}/>'
    col = '#2a1a12' if kind != 'nana' else '#8f8a85'
    s += f'<path d="M{ex_-r*.14},{ey_-r*.24} Q{ex_},{ey_-r*.32} {ex_+r*.18},{ey_-r*.24}" fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round"/>'
    tk = st.get('talk', 0) or 0
    if tk > 0.08:
        s += f'<path d="M{r*.64},{r*.46} Q{r*.78},{r*.5} {r*.9},{r*.44} Q{r*.84},{r*(.5+.22*tk)} {r*.7},{r*(.52+.16*tk)}Z" fill="#6e1f2a" {SW(3.5)}/>'
    else:
        s += f'<path d="M{r*.66},{r*.48} Q{r*.78},{r*.52} {r*.86},{r*.46}" fill="none" {SW(4)}/>'                     # calm closed mouth
    s += f'<ellipse cx="{r*.4}" cy="{r*.3}" rx="{r*.16}" ry="{r*.1}" fill="url(#blush)"/>'
    return s


# ------------------------------------------------------------------ limbs
def pt(x, y, ang, L):
    a = math.radians(ang); return x + L * math.sin(a), y + L * math.cos(a)


def capsule(pts, w, fill, outline=True):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    s = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + 2*STROKE}" stroke-linecap="round" stroke-linejoin="round"/>' if outline else ''
    return s + f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def hand(x, y, ang, size, pose, skin, back=False):
    """Hand at wrist (x,y), pointing along angle `ang`. Fingers, thumb, palm."""
    col = shade(skin, .9) if back else skin
    s = f'<g transform="translate({x:.1f},{y:.1f}) rotate({-ang:.1f}) scale({size/30:.3f})">'
    fw = 7.5
    def finger(fx, fy, a, L, bend=0):
        x1, y1 = fx + L * .55 * math.sin(math.radians(a)), fy + L * .55 * math.cos(math.radians(a))
        x2, y2 = x1 + L * .45 * math.sin(math.radians(a + bend)), y1 + L * .45 * math.cos(math.radians(a + bend))
        return capsule([(fx, fy), (x1, y1), (x2, y2)], fw, col)
    if pose in ('open', 'wave'):
        spread = 1.4 if pose == 'wave' else 1.0
        for i, (fx, a, L) in enumerate(((-9, -16, 22), (-3, -5, 26), (3, 5, 25), (9, 15, 21))):
            s += finger(fx, 18, a * spread, L)
        s += finger(12, 6, 70, 18, -20)
        s += f'<ellipse cx="0" cy="12" rx="15" ry="15" fill="{col}" {SW(4)}/>'
        s += f'<path d="M-9,10 Q0,16 9,10" fill="none" stroke="{INK}" stroke-width="1.8" opacity=".35"/>'
    elif pose == 'point':
        s += f'<ellipse cx="0" cy="14" rx="14" ry="13" fill="{col}" {SW(4)}/>'
        s += finger(-4, 20, 12, 30)
        for fx in (2, 7, 11): s += f'<circle cx="{fx}" cy="25" r="5.5" fill="{col}" {SW(3)}/>'
        s += finger(11, 8, 40, 12, 30)
    elif pose in ('hold', 'fist'):
        s += f'<ellipse cx="0" cy="14" rx="15" ry="14" fill="{col}" {SW(4)}/>'
        for i, fx in enumerate((-9, -3, 3, 9)):
            s += f'<ellipse cx="{fx}" cy="24" rx="5.6" ry="6.5" fill="{col}" {SW(3)}/>'
        s += finger(13, 8, 35, 14, 25)
    elif pose == 'flat':   # palm flat, fingers together and straight, seen from the side (thumb on top)
        s += f'<path d="M-10,-2 Q-13,12 -11,24 L-9,42 Q-8,50 0,50 Q8,50 9,42 L11,24 Q14,10 10,-2Z" fill="{col}" {SW(4)}/>'
        s += f'<path d="M-4,28 L-3,44 M3,28 L3,44" stroke="{INK}" stroke-width="1.8" opacity=".4" stroke-linecap="round"/>'
        s += f'<path d="M-8,4 Q-16,12 -14,22 Q-12,27 -7,24" fill="{col}" {SW(3.5)}/>'          # thumb
        s += f'<ellipse cx="3" cy="14" rx="5" ry="7" fill="#fff" opacity=".15"/>'
    else:  # relax: fingers together, slightly curled, thumb along the side
        s += f'<path d="M-13,4 Q-16,22 -8,32 Q2,38 11,30 Q16,20 13,4Z" fill="{col}" {SW(4)}/>'
        s += f'<path d="M-6,22 L-6,31 M0,23 L0,34 M6,22 L6,31" stroke="{INK}" stroke-width="2" opacity=".45" stroke-linecap="round"/>'
        s += finger(12, 6, 45, 15, 15)
    return s + '</g>'


def bottle(x, y, ang, tilt):
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({tilt:.1f})"><g transform="translate(0,4)">'
            f'<rect x="-14" y="-30" width="28" height="60" rx="9" fill="#9fd6f5" {SW(4)}/>'
            f'<rect x="-14" y="6" width="28" height="24" rx="7" fill="#4aa8e0"/><rect x="-9" y="-44" width="18" height="15" rx="4" fill="#2d6fb5" {SW(4)}/>'
            f'<rect x="-9" y="-22" width="5" height="34" rx="2" fill="#fff" opacity=".6"/></g></g>')


def arm(sx, sy, ang, bend, L1, L2, w, sleeve, sleeve_len, skin, pose, back=False, holding=None, hold_tilt=0, hand_ang=None):
    """Upper arm from shoulder, forearm bent forward by `bend` degrees. sleeve_len: 0..1 of upper arm, or 2 = full sleeve."""
    ex_, ey_ = pt(sx, sy, ang, L1)
    fa = ang + bend
    wx, wy = pt(ex_, ey_, fa, L2)
    skin_c = shade(skin, .9) if back else skin
    sl = shade(sleeve, .85) if back else sleeve
    s = ''
    if sleeve_len >= 2:
        s += capsule([(sx, sy), (ex_, ey_), (wx, wy)], w, sl)
        s += f'<path d="M{wx:.1f},{wy:.1f}" />'
    else:
        s += capsule([(sx, sy), (ex_, ey_), (wx, wy)], w * 0.86, skin_c)
        mx, my = pt(sx, sy, ang, L1 * sleeve_len)
        s += capsule([(sx, sy), (mx, my)], w * 1.25, sl)
    if holding == 'bottle':
        s += bottle(wx, wy, fa, hold_tilt)
    elif holding == 'phone':     # a smartphone held up in the hand, screen facing the viewer
        s += (f'<g transform="translate({wx:.1f},{wy:.1f}) rotate({hold_tilt:.1f})"><rect x="-17" y="-40" width="34" height="60" rx="7" fill="#22252b" {SW(4)}/>'
              f'<rect x="-13" y="-35" width="26" height="46" rx="3" fill="#7fd3ff"/><rect x="-11" y="-31" width="22" height="9" rx="2" fill="#fff" opacity=".7"/></g>')
    elif holding == 'suitcase':  # a suitcase hanging from the hand
        s += (f'<g transform="translate({wx:.1f},{wy:.1f})"><path d="M-14,4 L-14,-8 Q0,-18 14,-8 L14,4" fill="none" {SW(6)}/>'
              f'<rect x="-62" y="4" width="124" height="96" rx="12" fill="#a0522d" {SW(5)}/><rect x="-62" y="38" width="124" height="10" fill="#7a3b1e"/>'
              f'<rect x="-30" y="0" width="10" height="100" fill="#d9b26a" opacity=".85"/><rect x="20" y="0" width="10" height="100" fill="#d9b26a" opacity=".85"/></g>')
    s += hand(wx, wy, fa if hand_ang is None else hand_ang, w * 0.95, 'hold' if holding in ('bottle', 'suitcase') else pose, skin, back)
    return s


def leg(hx, hy, ang, knee, L1, L2, w, pants, shoe, back=False, foot=None):
    if foot == 'front': back = False          # facing the viewer: both legs are seen equally, same colours
    kx, ky = pt(hx, hy, ang, L1)
    sa = ang - knee                              # shin bends backward
    ax, ay = pt(kx, ky, sa, L2)
    p = shade(pants, .88) if back else pants
    s = capsule([(hx, hy), (kx, ky), (ax, ay)], w, p)
    sh = shade(shoe, .85) if back else shoe
    if foot == 'front':      # standing facing the viewer: toes point at the camera, seen from the front
        s += (f'<g transform="translate({ax:.1f},{ay:.1f})"><path d="M{-w*.6},-6 Q{-w*.72},{w*.52} 0,{w*.55} Q{w*.72},{w*.52} {w*.6},-6Z" fill="{sh}" {SW(4)}/>'
              f'<ellipse cx="0" cy="{w*.3}" rx="{w*.32}" ry="{w*.13}" fill="#fff" opacity=".18"/></g>')
        return s
    s += f'<g transform="translate({ax:.1f},{ay:.1f}) rotate({(-sa*0.35 if foot is None else foot):.1f})"><path d="M{-w*.55},-4 Q{-w*.6},{w*.45} {-w*.2},{w*.5} L{w*1.15},{w*.5} Q{w*1.35},{w*.1} {w*.6},-6Z" fill="{sh}" {SW(4)}/></g>'
    return s


def gait(st, swing=24):
    """Returns legA, kneeA, legB, kneeB, armswing, bob."""
    ph = st.get('walk')
    if ph is None: return 0, 3, 0, 3, 0, 0
    a = math.sin(ph * 2 * math.pi)
    kA = 8 + 34 * max(0, math.sin(ph * 2 * math.pi + 1.6))
    kB = 8 + 34 * max(0, math.sin(ph * 2 * math.pi + 1.6 + math.pi))
    return swing * a, kA, -swing * a, kB, a, -abs(math.cos(ph * 2 * math.pi)) * 6


# ------------------------------------------------------------------ characters
ALI_SKIN = '#E7B48C'; MAR_SKIN = '#EDC09A'; NANA_SKIN = '#C9906A'


def _arms_state(st, swing_a, holding_front):
    af, ab = st.get('arm_f', 6), st.get('arm_b', 6)
    if st.get('walk') is not None:
        if holding_front is None and 'arm_f' not in st: af = 6 - 20 * swing_a
        if 'arm_b' not in st: ab = 6 + 20 * swing_a
    def default_bend(a): return 12 if a < 40 else (25 if a < 120 else 30)
    return (af, st.get('elb_f', default_bend(af)), ab, st.get('elb_b', default_bend(ab)))


def _shoulder_lift(a): return -max(0, (a - 80)) / 100 * 10



def hair(style, hy):
    H = '#1c1714'
    if style == 'spiky':
        d = (f'M-72,{hy-14} L-80,{hy-34} L-66,{hy-30} L-70,{hy-54} L-54,{hy-42} L-50,{hy-62} L-36,{hy-46} L-26,{hy-60} L-18,{hy-42} '
             f'L-6,{hy-58} L4,{hy-40} L16,{hy-56} L24,{hy-40} L38,{hy-54} L42,{hy-38} L58,{hy-50} L56,{hy-32} L74,{hy-38} L70,{hy-14} '
             f'Q60,{hy-30} 46,{hy-26} Q20,{hy-38} 0,{hy-30} Q-24,{hy-38} -46,{hy-26} Q-62,{hy-30} -72,{hy-14}Z')
        return (f'<path d="{d}" fill="{H}" {SW(4)}/>'
                f'<path d="M-66,{hy-18} L-74,{hy+6} L-62,{hy-2}Z M66,{hy-18} L74,{hy+4} L62,{hy-2}Z" fill="{H}" {SW(3)}/>')
    if style == 'curly':
        s = f'<path d="M-72,{hy-10} Q-76,{hy-60} 0,{hy-64} Q76,{hy-60} 72,{hy-10} Q40,{hy-36} 0,{hy-34} Q-40,{hy-36} -72,{hy-10}Z" fill="{H}" {SW(4)}/>'
        for i in range(9):
            cx = -64 + i * 16; cy = hy - 30 - 8 * math.sin(i / 8 * math.pi)
            s += f'<circle cx="{cx}" cy="{cy}" r="11" fill="{H}" stroke="{INK}" stroke-width="3"/>'
        return s
    # 'flat': smooth side-swept fringe
    return (f'<path d="M-72,{hy-6} Q-78,{hy-62} 0,{hy-66} Q78,{hy-62} 72,{hy-6} Q66,{hy-30} 40,{hy-30} Q10,{hy-24} -20,{hy-40} Q-50,{hy-30} -72,{hy-6}Z" fill="#3a2516" {SW(4)}/>'
            f'<path d="M-30,{hy-52} Q10,{hy-40} 50,{hy-50}" fill="none" stroke="#5a3b26" stroke-width="4"/>')


DIMS = {'kid': (150, 70), 'girl': (140, 66), 'nana': (175, 84)}


# per body type: hip height, thigh, shin, shoulder front (x,y), shoulder back, upper arm, forearm, head centre y, head r, hand size
BODY = {'kid': dict(neck=-300, hip=150, thigh=70, sf=(42, -280), sb=(-40, -280), L1=60, L2=56, head=-360, r=70, hand=26),
        'girl': dict(neck=-290, hip=140, thigh=66, sf=(38, -272), sb=(-36, -272), L1=56, L2=52, head=-342, r=60, hand=23),
        'nana': dict(neck=-420, hip=175, thigh=84, sf=(52, -392), sb=(-50, -392), L1=86, L2=80, head=-486, r=62, hand=30)}


def _rot(px, py, cx, cy, deg):
    a = math.radians(deg); dx, dy = px - cx, py - cy
    return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)


def _ik(sx, sy, tx, ty, L1, L2, up=True):
    """two-bone IK in screen space; returns world angles (0 = down, + = forward) of upper arm and forearm"""
    dx, dy = tx - sx, ty - sy; d = max(1e-6, min(math.hypot(dx, dy), L1 + L2 - 1))
    w0 = math.atan2(dx, dy); c = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d); a1 = math.acos(max(-1, min(1, c)))
    best = None
    for sgn in (1, -1):
        w1 = w0 + sgn * a1; ex, ey = sx + L1 * math.sin(w1), sy + L1 * math.cos(w1)
        w2 = math.atan2(tx - ex, ty - ey)
        if best is None or (ey < best[2]) == up: best = (w1, w2, ey)
    return math.degrees(best[0]), math.degrees(best[1])


def _arm_to(B, lean, drop, shoulder, target, up, wrist=False):
    hipy = -B['hip']
    sx, sy = _rot(shoulder[0], shoulder[1], 0, hipy, lean); sy += drop
    w1, w2 = _ik(sx, sy, target[0], target[1], B['L1'], B['L2'] + (0 if wrist else B['hand'] * 0.6), up)
    return lean + w1, w2 - w1          # body-frame shoulder angle, elbow bend


def _nose(B, lean, drop):
    r = B['r']; return _rot(r * 1.08, B['head'] + r * 0.2, 0, -B['hip'], lean)[0], _rot(r * 1.08, B['head'] + r * 0.2, 0, -B['hip'], lean)[1] + drop


def _head_pt(B, lean, drop, tilt, px, py):
    """world position of a point (px, py) given in head space (relative to the head centre, in units of r)"""
    r = B['r']; x, y = _rot(px * r, B['head'] + py * r, 0, B['neck'], tilt)
    x, y = _rot(x, y, 0, -B['hip'], lean); return x, y + drop


def apply_pose(st, kind):
    """Salah and sitting positions. Sets arms, lean, legs and how far the body drops."""
    p = st.get('pose')
    if not p or p == 'stand': return st
    q = dict(st)
    def put(**k):
        for kk, v in k.items(): q.setdefault(kk, v)
    B = BODY[kind]
    if p == 'takbir':
        put(arm_f=38, elb_f=122, hand_f='open', arm_b=-28, elb_b=-150, hand_b='open', look_y=0.9)
    elif p == 'qiyam':
        # right hand over left on the chest, both visible
        cy = (B['sf'][1] + (-B['hip'])) / 2 + (B['hip'] * 0.05)
        af, ef = _arm_to(B, 0, 0, B['sf'], (B['sf'][0] * 0.15, cy - 6), up=False)
        ab, eb = _arm_to(B, 0, 0, B['sb'], (B['sf'][0] * 0.35, cy + 4), up=False)
        q['arms_front'] = True
        put(arm_f=af, elb_f=ef, hand_f='relax', arm_b=ab, elb_b=eb, hand_b='relax', look_y=0.9)
    elif p == 'ruku':
        # back flat, head in line with the back, face looking at the floor; both hands on the knees
        lean = 90; q['profile'] = True; q['arms_front'] = True
        knee = (6, -B['hip'] + B['thigh'])
        af, ef = _arm_to(B, lean, 0, B['sf'], (knee[0] + 14, knee[1] - 4), up=False)
        ab, eb = _arm_to(B, lean, 0, B['sb'], (knee[0] - 10, knee[1] - 10), up=False)
        put(lean=lean, arm_f=af, elb_f=ef, hand_f='relax', arm_b=ab, elb_b=eb, hand_b='relax')
    elif p == 'sajda':
        # knees, toes, palms, nose and forehead on the floor; face turned down to the floor, eyes lowered;
        # palms flat beside the cheeks with the fingers together pointing forward (to the qibla); elbows up
        q['profile'] = True; q['arms_front'] = True; q['eyes_down'] = True
        q['legs'] = (0, 112, 0, 112, 0, 0); drop = B['hip'] - B['thigh'] - 20; q['drop'] = drop; q['foot'] = 95
        FACE = 100                                       # total head turn: forehead and nose both on the floor
        nose = lambda L: _head_pt(B, L, drop, FACE - L, 1.12, 0.16)
        lo, hi = 90.0, 175.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if nose(mid)[1] < -1: lo = mid
            else: hi = mid
        lean = lo; tilt = FACE - lean
        cx, _ = _head_pt(B, lean, drop, tilt, 0.5, 0.35)       # cheek
        hl = B['hand'] * 1.25                                   # palm + fingers length
        af, ef = _arm_to(B, lean, drop, B['sf'], (cx - hl * 0.55, -B['hand'] * 0.3), up=False, wrist=True)
        ab, eb = _arm_to(B, lean, drop, B['sb'], (cx - hl * 0.75, -B['hand'] * 0.35), up=False, wrist=True)
        q['head_tilt'] = tilt
        put(lean=lean, arm_f=af, elb_f=ef, hand_f='flat', arm_b=ab, elb_b=eb, hand_b='flat',
            hand_ang_f=90 + lean, hand_ang_b=90 + lean)
    elif p == 'jalsa':
        # side view, sitting back on the heels: knees on the floor in front, near foot upright on its toes,
        # far foot laid flat under the body; back straight, hands flat on the thighs, looking ahead
        q['profile'] = True; q['arms_front'] = True
        T, w = B['thigh'], {'kid': 36, 'girl': 30, 'nana': 38}[kind]          # thigh length, leg thickness
        H = w * 1.45                                     # hip height above the floor
        ky = -w * 0.5                                    # knee centre on the floor
        dy = H + ky; dx = math.sqrt(max(1, T * T - dy * dy))
        thigh = math.degrees(math.atan2(dx, dy))         # 0 = down, 90 = forward
        kx = dx; ankle_h = w * 1.0
        def shin_to(ax, ay):
            vx, vy = ax - kx, ay - (-H + dy)
            sa = math.degrees(math.atan2(vx, vy)); return thigh - sa
        kA = shin_to(-w * 0.3, -ankle_h - w * 0.2)      # near leg: ankle raised on the upright foot
        kB = shin_to(-w * 0.6, -w * 0.5)                # far leg: shin flat on the floor
        q['legs'] = (thigh, kA, thigh - 2, kB, 0, 0); q['drop'] = B['hip'] - H
        q['foot'] = 82; q['foot_b'] = 172
        lean = 4
        hx, hy = dx * 0.62, -H + dy * 0.62 - w * 0.55   # on top of the thigh, near the knee
        af, ef = _arm_to(B, lean, B['hip'] - H, B['sf'], (hx, hy), up=False, wrist=True)
        ab, eb = _arm_to(B, lean, B['hip'] - H, B['sb'], (hx - 8, hy + 2), up=False, wrist=True)
        put(lean=lean, arm_f=af, elb_f=ef, hand_f='flat', arm_b=ab, elb_b=eb, hand_b='flat',
            hand_ang_f=thigh + lean, hand_ang_b=thigh + lean)
    elif p == 'sit':
        q['legs'] = (88, 172, 84, 172, 0, 0); q['drop'] = B['hip'] - 36; q['arms_front'] = True
        knee_y = -36; dr = B['hip'] - 36
        if st.get('fold'):     # arms folded across the chest, listening politely
            cy = B['sf'][1] + (B['hip'] * 0.34) + dr
            af, ef = _arm_to(B, 0, dr, B['sf'], (B['sb'][0] + 8, cy), up=False)
            ab, eb = _arm_to(B, 0, dr, B['sb'], (B['sf'][0] - 4, cy + 12), up=False)
            put(arm_f=af, elb_f=ef, hand_f='fist', arm_b=ab, elb_b=eb, hand_b='fist')
        else:
            af, ef = _arm_to(B, 0, dr, B['sf'], (B['thigh'] * 0.85, knee_y - 22), up=False)
            ab, eb = _arm_to(B, 0, dr, B['sb'], (B['thigh'] * 0.6, knee_y - 26), up=False)
            put(arm_f=af, elb_f=ef, hand_f='relax', arm_b=ab, elb_b=eb, hand_b='relax', look_y=0.9)
    return q


ALI_LOOK = dict(shirt='#D52B31', pants='#3d4f75', shoe='#f2f2f2', skin=ALI_SKIN, hair='spiky', cap='#fbfbf7', kind='ali')


def ali(st, look=None):
    L = dict(ALI_LOOK); L.update(look or {})
    st = apply_pose(st, 'kid')
    x, y, s, f = st['x'], st['y'] + st.get('drop', 0) * st.get('s', 1), st.get('s', 1), st.get('face', 1)
    lA, kA, lB, kB, sw, bob = st['legs'] if 'legs' in st else gait(st)
    bob += st.get('bob', 0)
    lean = st.get('lean', 0) + (4 if st.get('walk') is not None else 0)
    af, ebf, ab, ebb = _arms_state(st, sw, st.get('hold'))
    RED, PANTS, SHOE, ALI_SKIN_ = L['shirt'], L['pants'], L['shoe'], L['skin']
    g = f'<g transform="translate({x},{y + bob*s}) scale({s*f},{s})">'
    # legs (hip at -150)
    g += leg(-15, -150, lB, kB, 70, 68, 36, PANTS, SHOE, back=True, foot=st.get('foot_b', st.get('foot')))
    g += f'<g transform="rotate({lean},0,-150)">'
    if not st.get('arms_front'): g += arm(-40, -280 + _shoulder_lift(ab), ab, ebb, 60, 56, 27, RED, .45, ALI_SKIN_, st.get('hand_b', 'relax'), back=True, hand_ang=st.get('hand_ang_b'))
    g += '</g>'
    g += leg(15, -150, lA, kA, 70, 68, 36, PANTS, SHOE, foot=st.get('foot'))
    g += f'<g transform="rotate({lean},0,-150)">'
    # torso: chubby kid, red T-shirt
    g += f'<path d="M-50,-292 Q-70,-240 -62,-170 Q-60,-138 -48,-130 L48,-130 Q60,-138 62,-170 Q70,-240 50,-292 Q0,-306 -50,-292Z" fill="{RED}" {SW()}/>'
    g += f'<path d="M-48,-136 Q0,-124 48,-136 L46,-128 Q0,-118 -46,-128Z" fill="{shade(RED,.8)}"/>'
    g += f'<path d="M-24,-298 Q0,-282 24,-298" fill="none" stroke="{shade(RED,.75)}" stroke-width="7" stroke-linecap="round"/>'
    g += f'<path d="M30,-230 Q50,-200 46,-150" fill="none" stroke="{shade(RED,.8)}" stroke-width="4" opacity=".6"/>'
    # neck + head
    hy = -366
    g += f'<rect x="-15" y="-312" width="30" height="24" fill="{shade(ALI_SKIN_,.88)}"/>'
    g += f'<g transform="rotate({st.get("head_tilt",0)},0,-300)">'
    PROF = st.get('profile')
    if not PROF: g += f'<ellipse cx="-70" cy="{hy+8}" rx="15" ry="19" fill="{shade(ALI_SKIN_,.94)}" {SW(4)}/>'
    if not PROF: g += f'<ellipse cx="74" cy="{hy+8}" rx="13" ry="18" fill="{ALI_SKIN_}" {SW(4)}/>'
    # round face, full cheeks
    g += f'<path d="M-70,{hy-20} Q-74,{hy+50} -38,{hy+70} Q0,{hy+86} 40,{hy+70} Q76,{hy+50} 72,{hy-20} Q66,{hy-80} 0,{hy-82} Q-64,{hy-80} -70,{hy-20}Z" fill="{ALI_SKIN_}" {SW()}/>'
    g += f'<path d="M-62,{hy+20} Q-60,{hy+56} -30,{hy+70}" fill="none" stroke="{shade(ALI_SKIN_,.85)}" stroke-width="10" opacity=".5"/>'
    # spiky black hair below the topi (sides + short fringe spikes)
    g += hair(L['hair'], hy)
    # white topi (round cap) on top
    g += f'<path d="M-60,{hy-50} Q-58,{hy-108} 0,{hy-112} Q58,{hy-108} 60,{hy-50} Q0,{hy-64} -60,{hy-50}Z" fill="{L['cap']}" {SW()}/>'
    g += f'<path d="M-56,{hy-60} Q0,{hy-74} 56,{hy-60}" fill="none" stroke="#d8d4c4" stroke-width="4"/>'
    for i in range(-3, 4):
        g += f'<path d="M{i*15},{hy-108+abs(i)*2} L{i*17},{hy-70}" stroke="#e3dfd0" stroke-width="2"/>'
    g += f'<g transform="translate(0,{hy+6})">' + (face_profile(70, st, L['kind'], ALI_SKIN_) if PROF else face(70, st, L['kind'])) + '</g>'
    g += '</g>'
    # front arm
    if st.get('arms_front'): g += arm(-40, -280 + _shoulder_lift(ab), ab, ebb, 60, 56, 27, RED, .45, ALI_SKIN_, st.get('hand_b', 'relax'), back=bool(st.get('profile')), hand_ang=st.get('hand_ang_b'))
    g += arm(42, -280 + _shoulder_lift(af), af, ebf, 60, 56, 27, RED, .45, ALI_SKIN_, st.get('hand_f', 'relax'), hand_ang=st.get('hand_ang_f'),
             holding=st.get('hold'), hold_tilt=st.get('hold_tilt', 0))
    g += f'<ellipse cx="38" cy="{-276 + _shoulder_lift(af)}" rx="18" ry="16" fill="{RED}"/>'
    g += '</g></g>'
    return g


def maryam(st):
    st = apply_pose(st, 'girl')
    x, y, s, f = st['x'], st['y'] + st.get('drop', 0) * st.get('s', 1), st.get('s', 1), st.get('face', 1)
    lA, kA, lB, kB, sw, bob = st['legs'] if 'legs' in st else gait(st, 20)
    bob += st.get('bob', 0)
    lean = st.get('lean', 0) + (3 if st.get('walk') is not None else 0)
    af, ebf, ab, ebb = _arms_state(st, sw, None)
    DRESS, SCARF = '#E86FA0', '#8E7CC3'
    g = f'<g transform="translate({x},{y + bob*s}) scale({s*f},{s})">'
    g += leg(-13, -140, lB, kB, 66, 64, 30, '#f6d7e6', '#c0396b', back=True, foot=st.get('foot_b', st.get('foot')))
    g += f'<g transform="rotate({lean},0,-140)">' + ('' if st.get('arms_front') else arm(-36, -272 + _shoulder_lift(ab), ab, ebb, 56, 52, 24, DRESS, 2, MAR_SKIN, st.get('hand_b', 'relax'), back=True, hand_ang=st.get('hand_ang_b'))) + '</g>'
    g += leg(13, -140, lA, kA, 66, 64, 30, '#f6d7e6', '#c0396b', foot=st.get('foot'))
    g += f'<g transform="rotate({lean},0,-140)">'
    g += f'<path d="M-44,-286 Q-56,-200 -80,-92 Q0,-74 80,-92 Q56,-200 44,-286 Q0,-298 -44,-286Z" fill="{DRESS}" {SW()}/>'
    g += '<path d="M-74,-112 Q0,-98 74,-112" fill="none" stroke="#fff" stroke-width="7" opacity=".75"/>'
    for i in (-40, 0, 40): g += f'<circle cx="{i}" cy="-150" r="7" fill="#ffd6e8"/>'
    hy = -352
    g += f'<g transform="rotate({st.get("head_tilt",0)},0,-290)">'
    # scarf behind
    g += f'<path d="M-84,{hy} Q-92,{hy+92} -60,{hy+104} L62,{hy+104} Q94,{hy+92} 86,{hy} A86,86 0 0 0 -84,{hy}Z" fill="{SCARF}" {SW()}/>'
    g += f'<ellipse cx="0" cy="{hy+6}" rx="62" ry="64" fill="{MAR_SKIN}" {SW()}/>'
    g += f'<path d="M-66,{hy-2} Q-60,{hy-60} 0,{hy-66} Q60,{hy-60} 66,{hy-2} Q50,{hy-46} 0,{hy-50} Q-50,{hy-46} -66,{hy-2}Z" fill="{SCARF}" {SW(4)}/>'
    g += f'<path d="M-40,{hy-40} Q0,{hy-52} 40,{hy-40}" fill="none" stroke="#2a1a12" stroke-width="8" stroke-linecap="round"/>'
    g += f'<g transform="translate(0,{hy+10})">' + (face_profile(60, st, 'maryam', MAR_SKIN) if st.get('profile') else face(60, st, 'maryam')) + '</g></g>'
    if st.get('arms_front'): g += arm(-36, -272 + _shoulder_lift(ab), ab, ebb, 56, 52, 24, DRESS, 2, MAR_SKIN, st.get('hand_b', 'relax'), back=bool(st.get('profile')), hand_ang=st.get('hand_ang_b'))
    g += arm(38, -272 + _shoulder_lift(af), af, ebf, 56, 52, 24, DRESS, 2, MAR_SKIN, st.get('hand_f', 'relax'), hand_ang=st.get('hand_ang_f'))
    g += f'<ellipse cx="34" cy="{-268 + _shoulder_lift(af)}" rx="16" ry="15" fill="{DRESS}"/>'
    g += '</g></g>'
    return g


def nana(st):
    st = apply_pose(st, 'nana')
    x, y, s, f = st['x'], st['y'] + st.get('drop', 0) * st.get('s', 1), st.get('s', 1), st.get('face', 1)
    lA, kA, lB, kB, sw, bob = st['legs'] if 'legs' in st else gait(st, 16)
    bob += st.get('bob', 0)
    lean = st.get('lean', 0) + (2 if st.get('walk') is not None else 0)
    af, ebf, ab, ebb = _arms_state(st, sw, None)
    KURTA, KD = '#f8f8f4', '#dcdcd2'
    g = f'<g transform="translate({x},{y + bob*s}) scale({s*f},{s})">'
    g += leg(-17, -175, lB, kB, 84, 84, 38, '#f3f2ea', '#6b4a30', back=True, foot=st.get('foot_b', st.get('foot')))
    g += f'<g transform="rotate({lean},0,-175)">' + ('' if st.get('arms_front') else arm(-50, -392 + _shoulder_lift(ab), ab, ebb, 86, 80, 32, KURTA, 2, NANA_SKIN, st.get('hand_b', 'relax'), back=True, hand_ang=st.get('hand_ang_b'))) + '</g>'
    g += leg(17, -175, lA, kA, 84, 84, 38, '#f3f2ea', '#6b4a30', foot=st.get('foot'))
    g += f'<g transform="rotate({lean},0,-175)">'
    # long white kurta: band collar, button placket, chest pocket
    g += f'<path d="M-62,-410 Q-80,-300 -84,-120 Q0,-104 84,-120 Q80,-300 62,-410 Q0,-426 -62,-410Z" fill="{KURTA}" {SW()}/>'
    g += f'<path d="M-70,-300 Q-76,-220 -78,-130" fill="none" stroke="{KD}" stroke-width="6"/>'
    g += f'<rect x="-6" y="-406" width="16" height="170" rx="4" fill="#f1f1ea" stroke="{KD}" stroke-width="3"/>'
    for by in (-384, -350, -316, -282, -252): g += f'<circle cx="2" cy="{by}" r="5.5" fill="#fff" stroke="#b9b6a8" stroke-width="2.5"/>'
    g += f'<path d="M24,-330 L58,-330 L57,-288 Q41,-282 25,-288Z" fill="none" stroke="{KD}" stroke-width="4"/>'
    g += f'<path d="M-30,-424 Q0,-412 30,-424 L30,-410 Q0,-400 -30,-410Z" fill="#fff" {SW(3.5)}/>'
    hy = -488
    g += f'<rect x="-17" y="-438" width="34" height="26" fill="{shade(NANA_SKIN,.88)}"/>'
    g += f'<g transform="rotate({st.get("head_tilt",0)},0,-420)">'
    PROF = st.get('profile')
    if not PROF: g += f'<ellipse cx="-58" cy="{hy+6}" rx="13" ry="18" fill="{shade(NANA_SKIN,.94)}" {SW(4)}/><ellipse cx="62" cy="{hy+6}" rx="12" ry="17" fill="{NANA_SKIN}" {SW(4)}/>'
    g += f'<path d="M-60,{hy-10} Q-62,{hy+56} -30,{hy+74} Q0,{hy+86} 32,{hy+74} Q64,{hy+56} 62,{hy-10} Q58,{hy-74} 0,{hy-76} Q-58,{hy-74} -60,{hy-10}Z" fill="{NANA_SKIN}" {SW()}/>'
    # grey hair: short, combed, receding at the temples
    g += (f'<path d="M-62,{hy-6} Q-70,{hy-56} -36,{hy-74} Q0,{hy-90} 38,{hy-74} Q70,{hy-56} 62,{hy-6} Q56,{hy-40} 40,{hy-50} Q8,{hy-66} -20,{hy-58} '
          f'Q-44,{hy-50} -56,{hy-30}Z" fill="#a9a6a2" {SW(4)}/>')
    for i in range(-3, 4): g += f'<path d="M{i*13-4},{hy-80+abs(i)*3} Q{i*14},{hy-66} {i*15+6},{hy-56}" fill="none" stroke="#d7d5d1" stroke-width="3" opacity=".9"/>'
    if PROF:
        g += f'<g transform="translate(0,{hy+2})">' + face_profile(62, st, 'nana', NANA_SKIN)
        g += (f'<path d="M-4,8 Q-2,58 30,76 Q54,84 66,62 Q70,44 62,30 Q56,40 44,38 Q30,30 20,34 Q8,30 -4,8Z" fill="#eeeeea" {SW(4)}/>')   # beard along the jaw
        g += f'<path d="M40,26 Q52,20 62,26" fill="none" stroke="#dcdad4" stroke-width="7" stroke-linecap="round"/>'                      # moustache
        g += (f'<path d="M24,-20 Q36,-24 50,-20 Q52,-4 44,4 Q36,8 28,2 Q22,-6 24,-20Z" fill="url(#glass)" stroke="#3a2a22" stroke-width="5"/>'
              f'<path d="M24,-16 L-6,-10" stroke="#3a2a22" stroke-width="4"/>')                                                            # one lens + temple
    else:
        g += f'<g transform="translate(0,{hy+2})">' + face(62, st, 'nana')
        # short white beard (jaw + chin) and moustache
        talk = st.get('talk', 0) + ex(st.get('expr'))['mopen'] * .55
        jaw = min(talk, 1) * 10
        fx = 62 * 0.14
        g += (f'<path d="M-58,4 Q-58,{60+jaw} -22,{80+jaw} Q{fx},{92+jaw} 34,{80+jaw} Q62,{60+jaw} 60,4 Q54,40 40,46 Q{fx},{36} -24,46 Q-50,40 -58,4Z" '
              f'fill="#eeeeea" {SW(4)}/>')
        for i in range(7): g += f'<path d="M{-40+i*13},{50+jaw} q2,12 0,22" stroke="#c9c7c1" stroke-width="2.4" fill="none"/>'
        g += f'<path d="M{fx-26},22 Q{fx-12},14 {fx},20 Q{fx+12},14 {fx+26},22 Q{fx+14},28 {fx},24 Q{fx-14},28 {fx-26},22Z" fill="#dcdad4" {SW(3)}/>'
        # aviator glasses: teardrop lenses, thin metal double bridge, dark tortoise rims
        for sx in (-1, 1):
            cx = fx + sx * 62 * .36 * (0.92 if sx < 0 else 1)
            lens = f'M{cx-21},{-22} Q{cx},{-27} {cx+21},{-22} Q{cx+24},{2} {cx+12},{12} Q{cx},{18} {cx-12},{12} Q{cx-24},{2} {cx-21},{-22}Z'
            g += f'<path d="{lens}" fill="url(#glass)" stroke="#3a2a22" stroke-width="5"/>'
            g += f'<path d="M{cx-17},{-20} Q{cx},{-24} {cx+17},{-20}" fill="none" stroke="#c9b48a" stroke-width="2"/>'
        l, r_ = fx - 62 * .36 * .92 + 21, fx + 62 * .36 - 21
        g += f'<path d="M{l},-20 Q{(l+r_)/2},-28 {r_},-20 M{l+1},-12 L{r_-1},-12" fill="none" stroke="#c9b48a" stroke-width="3"/>'
        g += f'<path d="M{fx + 62*.36 + 21},-20 L60,-14" stroke="#3a2a22" stroke-width="4"/>'
    g += '</g></g>'
    if st.get('arms_front'): g += arm(-50, -392 + _shoulder_lift(ab), ab, ebb, 86, 80, 32, KURTA, 2, NANA_SKIN, st.get('hand_b', 'relax'), back=bool(st.get('profile')), hand_ang=st.get('hand_ang_b'))
    g += arm(52, -392 + _shoulder_lift(af), af, ebf, 86, 80, 32, KURTA, 2, NANA_SKIN, st.get('hand_f', 'relax'), hand_ang=st.get('hand_ang_f'))
    g += f'<ellipse cx="47" cy="{-386 + _shoulder_lift(af)}" rx="20" ry="18" fill="{KURTA}"/>'
    g += '</g></g>'
    return g


BILAL_LOOK = dict(shirt='#3f8fd2', pants='#e9e4d6', shoe='#6b4a30', skin='#B9825C', hair='curly', cap='#fbfbf7', kind='ali')
ZAID_LOOK = dict(shirt='#2f9e5b', pants='#4a4a52', shoe='#2b2b2b', skin='#F0C8A4', hair='flat', cap='#d9d4c8', kind='ali')


def bilal(st): return ali(st, BILAL_LOOK)
def zaid(st): return ali(st, ZAID_LOOK)


def kid(st, girl=False):
    return maryam(st) if girl else ali(st)
