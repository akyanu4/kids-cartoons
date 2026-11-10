"""Render "Masjid ke Adaab". python3 masjid_voices.py; python3 masjid_render.py frames 5,30 | video 2"""
import os, sys, json, math, io, subprocess
from multiprocessing import Pool
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import chars2 as C, chars as C1, masjid_story as story

W, H, FPS = 1920, 1080, 24
GROUND = 1000
LIFT = 120
BUILD = 'build_masjid'
os.makedirs(f'{BUILD}/bg', exist_ok=True)
TL = json.load(open(f'{BUILD}/timeline.json'))
SHOTS, TOTAL = TL['shots'], TL['total']
_FD = os.path.expanduser('~/.fonts')
UFONT = os.environ.get('URDU_FONT', f'{_FD}/NotoNastaliqUrdu-Regular.ttf')
UFONT_B = os.environ.get('URDU_FONT_BOLD', f'{_FD}/NotoNastaliqUrdu-Bold.ttf')
LFONT = '/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf'
LFONT_B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
if not os.path.exists(LFONT): LFONT = LFONT_B

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * ease(x)

# ---------------------------------------------------------------- background: masjid prayer hall
S = 'stroke="#5b4636" stroke-width="6"'

def arch(x, y, w, h, fill, extra=''):
    return f'<path d="M{x},{y+h} L{x},{y+w/2} Q{x},{y} {x+w/2},{y-w*0.25} Q{x+w},{y} {x+w},{y+w/2} L{x+w},{y+h}Z" fill="{fill}" {S} {extra}/>'

def star(cx, cy, r, fill):
    pts = []
    for i in range(16):
        rr = r if i % 2 == 0 else r * 0.62; a = math.pi * i / 8
        pts.append(f'{cx + rr*math.cos(a):.1f},{cy + rr*math.sin(a):.1f}')
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="#b8860b" stroke-width="3"/>'

def lamp(x, y):
    return (f'<line x1="{x}" y1="0" x2="{x}" y2="{y-40}" stroke="#8a6d3b" stroke-width="4"/>'
            f'<path d="M{x-40},{y-40} Q{x},{y-70} {x+40},{y-40} L{x+26},{y+10} Q{x},{y+30} {x-26},{y+10}Z" fill="#e9b949" stroke="#8a6d3b" stroke-width="4"/>'
            f'<ellipse cx="{x}" cy="{y}" rx="18" ry="12" fill="#fff6c9" opacity=".9"/><circle cx="{x}" cy="{y+40}" r="60" fill="#fff3b0" opacity=".18"/>')

def hall(w):
    s = f'<rect width="{w}" height="{H}" fill="#f6ead2"/>'
    s += f'<rect y="0" width="{w}" height="70" fill="#e6d3ad"/>'
    for x in range(0, w, 60): s += f'<rect x="{x+10}" y="18" width="40" height="34" rx="6" fill="#d9c08f"/>'
    # windows with arches + star lattice
    for i, x in enumerate(range(120, w - 200, 420)):
        if abs((x + 120) - w / 2) < 260: continue
        s += arch(x, 250, 240, 330, '#a9d8f0')
        s += f'<path d="M{x+120},{190} L{x+120},{580} M{x},{420} L{x+240},{420}" stroke="#5b4636" stroke-width="5"/>' + star(x + 120, 420, 34, '#ffe08a')
    # mihrab in the middle of the back wall
    m = w / 2
    s += arch(m - 190, 230, 380, 420, '#2f7d5b')
    s += arch(m - 140, 300, 280, 350, '#3f9a70')
    for k in range(6): s += star(m - 100 + k * 40, 330 + (k % 2) * 30, 14, '#f5d06b')
    s += f'<rect x="{m-200}" y="640" width="400" height="22" fill="#b98a4b" {S}/>'
    # carpet with saff lines
    s += f'<rect y="660" width="{w}" height="{H-660}" fill="#b5383a"/>'
    for yy in (700, 800, 920, 1060):
        s += f'<rect y="{yy}" width="{w}" height="10" fill="#e9c46a"/><rect y="{yy+14}" width="{w}" height="4" fill="#7d2224"/>'
    for x in range(0, w, 160):
        for yy in (740, 852):
            s += f'<path d="M{x+80},{yy-24} L{x+104},{yy} L{x+80},{yy+24} L{x+56},{yy}Z" fill="#d4573f" stroke="#e9c46a" stroke-width="3"/>'
    s += f'<rect y="652" width="{w}" height="14" fill="#7a4a2a"/>'
    for x in (300, w - 300): s += lamp(x, 150)
    s += lamp(m, 120)
    return s

def screen(x, w):
    """wooden lattice divider for the sisters' side"""
    s = f'<rect x="{x}" y="760" width="{w}" height="{GROUND-740}" fill="#a0673a" {S}/>'
    for yy in range(785, GROUND - 20, 60):
        for xx in range(x + 20, x + w - 20, 60):
            s += f'<path d="M{xx+20},{yy} L{xx+40},{yy+25} L{xx+20},{yy+50} L{xx},{yy+25}Z" fill="#c98d5a" stroke="#6b3f22" stroke-width="3"/>'
    return s + f'<rect x="{x-10}" y="740" width="{w+20}" height="30" rx="8" fill="#8a5530" {S}/>'

def bg_svg(name):
    if name in ('title', 'moral', 'end'):
        return 1920, hall(1920)
    if name == 'hall':
        return 1920, hall(1920)
    if name == 'hall_wide':
        return 2600, hall(2600)
    raise KeyError(name)

_bg = {}
def bg(name):
    if name not in _bg:
        f = f'{BUILD}/bg/{name}.png'
        if not os.path.exists(f):
            w, s = bg_svg(name)
            cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}">{s}</svg>'.encode(), write_to=f)
        _bg[name] = Image.open(f).convert('RGB')
    return _bg[name]

# ---------------------------------------------------------------- timing
def shot_at(t):
    for s in SHOTS:
        if s['t0'] <= t < s['t1']: return s
    return SHOTS[-1]

def shot(name): return next(s for s in SHOTS if s['name'] == name)

SFX_MOUTH = {'nahin': ('ALI', 'BILAL', 'ZAID', 'MARYAM'), 'kids_giggle': ('ALI', 'BILAL', 'ZAID'), 'nana_giggle': ('NANA',)}

def mouth(t, who):
    for s in SHOTS:
        for b in s['beats']:
            ws = (b['who'],) if b['kind'] == 'say' else SFX_MOUTH.get(b.get('name'), ())
            if who in ws and b['t'] <= t < b['t'] + b['d']:
                i = int((t - b['t']) * FPS); e = b['env']
                return e[i] if i < len(e) else 0
    return 0

def active(t, sh, kind, name=None, pad=0.0):
    for b in sh['beats']:
        if b['kind'] == kind and (name is None or b.get('name') == name or b.get('who') == name) and b['t'] - pad <= t < b['t'] + b['d'] + pad: return b
    return None

def blink(t, seed): x = (t + seed * 1.37) % 3.6; return 1.0 if x < 0.12 else (0.5 if x < 0.16 else 0.0)

def caption(t):
    for s in SHOTS:
        if s['name'] == 'title': continue
        for b in s['beats']:
            if b['t'] <= t < b['t'] + b['d'] + 0.15:
                if b['kind'] == 'say': return b['who'], b['text']
                if b.get('name') == 'nahin': return 'ALL', 'Nahin!'
    return None

def talk(m): return min(1.0, m * 1.1)

def heart(x, y, s=1, op=1): return f'<path transform="translate({x},{y}) scale({s})" d="M0,10 C-25,-15 -50,10 0,45 C50,10 25,-15 0,10Z" fill="#ff5c8a" stroke="#3b2a20" stroke-width="4" opacity="{op}"/>'

def card(x, y, w, h, op, fill='#fff'):
    return f'<g opacity="{op}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="46" fill="{fill}" stroke="#3b2a20" stroke-width="8"/></g>'

def cross(x, y, op):
    return f'<g opacity="{op}"><circle cx="{x}" cy="{y}" r="70" fill="#fff" stroke="#e23b3b" stroke-width="14"/><path d="M{x-40},{y-40} L{x+40},{y+40} M{x+40},{y-40} L{x-40},{y+40}" stroke="#e23b3b" stroke-width="16" stroke-linecap="round"/></g>'

def tick(x, y, op):
    return f'<g opacity="{op}"><circle cx="{x}" cy="{y}" r="56" fill="#fff" stroke="#2E8B57" stroke-width="12"/><path d="M{x-28},{y} L{x-6},{y+24} L{x+30},{y-24}" fill="none" stroke="#2E8B57" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/></g>'

# ---------------------------------------------------------------- scenes
KIDS = (('ALI', C.ali), ('BILAL', C.bilal), ('ZAID', C.zaid))

def scene(t):
    sh = shot_at(t); n = sh['name']; lt = t - sh['t0']; D = sh['t1'] - sh['t0']
    A = lambda **k: dict(k)
    m = {w: talk(mouth(t, w)) for w in ('ALI', 'BILAL', 'ZAID', 'NANA', 'MARYAM')}
    bl = lambda i: blink(t, i)
    over = ''; texts = []
    wave = lambda ph: 150 + 18 * math.sin(t * 6 + ph)

    if n in ('title', 'moral', 'end'):
        k = ease(lt / 0.8)
        xs = (560, 780, 1000) if n != 'end' else (640, 860, 1080)
        lay = ''
        for i, (w, fn) in enumerate(KIDS):
            lay += fn(A(x=xs[i], y=GROUND, s=0.95, face=1 if i < 1 else -1, arm_f=wave(i), elb_f=25, hand_f='wave', blink=bl(i), expr='happy'))
        if n != 'end': lay += C.nana(A(x=1300, y=GROUND, s=0.92, face=-1, arm_f=40, hand_f='open', blink=bl(5), expr='warm'))
        if n == 'title':
            over = card(360, 90, 1200, 300, k)
            texts += [('U:' + story.TITLE_UR, 960, 190, 104, '#2E8B57', k), ('L:' + story.TITLE_RO, 960, 330, 52, '#c0396b', k)]
        elif n == 'moral':
            over = card(260, 80, 1400, 340, k, '#fffbea')
            texts += [('U:' + story.MORAL_HEAD, 960, 140, 50, '#c0396b', k), ('U:' + story.MORAL[0], 960, 245, 70, '#2E8B57', k),
                      ('U:' + story.MORAL[1], 960, 355, 54, '#3b2a20', k)]
        else:
            over = card(440, 80, 1040, 380, k) + f'<g opacity="{k}"><rect x="700" y="250" width="520" height="100" rx="50" fill="#e62117" stroke="#3b2a20" stroke-width="6"/></g>'
            texts += [('U:' + story.THANKS, 960, 165, 70, '#2E8B57', k), ('U:' + story.SUBSCRIBE, 960, 300, 48, '#ffffff', k),
                      ('L:' + story.CHANNEL, 960, 410, 42, '#3b2a20', k)]
        return 'hall', (0, 1), lay, over, texts

    if n in ('jamaat', 'jamaat2'):
        # row facing the mihrab; viewer sees them from behind-ish 3/4, standing in qiyam
        quiet = n == 'jamaat2'
        b1 = active(t, sh, 'say', 'N') if False else None
        beats = [b for b in sh['beats'] if b['kind'] == 'say']
        push1 = (not quiet) and t >= beats[1]['t'] + beats[1]['d'] * 0.55
        push2 = (not quiet) and len(beats) > 2 and t >= beats[2]['t'] + 0.4
        wob = lambda ph: (math.sin(t * 7 + ph) if push2 else 0)
        giggle = (not quiet) and (push1 and (active(t, sh, 'sfx', 'kids_giggle', 0.6) is not None or push2))
        lay = C.nana(A(x=1400, y=GROUND - 6, s=0.92, pose='qiyam', expr='neutral', blink=bl(5), look_y=0.7))
        base = (720, 940, 1160)
        for i, (w, fn) in enumerate(KIDS):
            st = A(x=base[i], y=GROUND, s=0.9, pose='qiyam', blink=bl(i), expr='neutral', look_y=0.7)
            if not quiet:
                if w == 'BILAL' and push1:
                    ph = (t * 2.2) % 1
                    st.update(x=base[i] - 26 * max(0, math.sin(ph * math.pi * 2)) + 12 * wob(1), arm_b=70, elb_b=10, hand_b='open', expr='laugh', head_tilt=-6)
                if w == 'ALI' and push1:
                    st.update(x=base[i] - 30 * max(0, math.sin(((t * 2.2) % 1) * math.pi * 2 - 0.6)) + 18 * wob(0), head_tilt=8, expr='surprised' if not push2 else 'laugh')
                    if push2: st.update(arm_f=80, elb_f=0, hand_f='open', expr='laugh')
                if w == 'ZAID' and push2:
                    st.update(expr='laugh', x=base[i] + 14 * wob(2), head_tilt=6 * math.sin(t * 9), bob=-5 * abs(math.sin(t * 9)))
                if giggle and w in ('ALI', 'BILAL'): st['bob'] = st.get('bob', 0) - 4 * abs(math.sin(t * 10 + i))
            lay = fn(st) + lay if False else lay + fn(st)
        if quiet and lt > D - 1.8: pass
        cam = (0, lerp(1.0, 1.08, lt / D))
        return 'hall', cam, lay, '', texts

    if n == 'after' or n.startswith('g_') or n == 'right_intro':
        # kids sitting on the carpet, Nana standing facing them; Maryam behind the lattice screen
        kx = (420, 620, 820)
        anyN = active(t, sh, 'sfx', 'nahin')
        gig = active(t, sh, 'sfx', 'kids_giggle', 0.3)
        nanaT = A(x=1380, y=GROUND - 10, s=0.95, face=-1, talk=m['NANA'], blink=bl(5), expr='playful' if n.startswith('g_') else 'warm')
        if nanaT['expr'] == 'playful': nanaT['expr'] = 'happy'
        lay = ''
        marT = A(x=160, y=GROUND, s=0.86, face=1, blink=bl(7), talk=m['MARYAM'], expr='happy', look=1)
        if anyN: marT.update(expr='excited', arm_f=150, elb_f=30, hand_f='open', bob=-10 * abs(math.sin(t * 10)))
        if active(t, sh, 'say', 'MARYAM'): marT.update(expr='laugh', bob=-6 * abs(math.sin(t * 9)))
        over_kids = ''
        sitting = not (n == 'g_run') and not (n == 'right_intro' and lt > 1.2)
        for i, (w, fn) in enumerate(KIDS):
            st = A(x=kx[i], y=GROUND, s=0.88, face=1, blink=bl(i), talk=m[w], look=1, expr='happy')
            st['pose'] = 'sit' if sitting else ('qiyam' if n == 'g_run' else 'stand')
            if n == 'after' and lt < 2.5: st['expr'] = 'surprised' if lt > 1.0 else 'neutral'
            if anyN:
                st.update(expr='excited', arm_f=150 + 10 * math.sin(t * 9 + i), elb_f=20, hand_f='open', arm_b=150, elb_b=20, hand_b='open', bob=-8 * abs(math.sin(t * 9 + i)))
            elif gig: st.update(expr='laugh', bob=-5 * abs(math.sin(t * 9 + i)))
            if active(t, sh, 'say', w):
                e = active(t, sh, 'say', w)['emo']; st['expr'] = {'excited': 'excited', 'sad': 'sad'}.get(e, 'happy')
                if e == 'excited': st.update(arm_f=120, elb_f=40, hand_f='open')
                if e == 'sad': st.update(head_tilt=10, look_y=0.8)
            if n == 'g_run' and not anyN and not gig and not active(t, sh, 'say'): st['expr'] = 'surprised' if 2 < lt < 7 else st['expr']
            over_kids += fn(st)
        # Nana's acts
        say0 = sh['beats'][0] if sh['beats'] else None
        acting = say0 is not None and say0['kind'] == 'say' and t >= say0['t']
        ask = active(t, sh, 'say', 'NANA') if acting else None
        asking = ask is not None and 'sahi tareeqa' in ask['text']
        doing = acting and not asking and not anyN and t < (say0['t'] + say0['d'] + 3.0)
        if n == 'g_push' and doing:
            ph = math.sin(t * 6)
            nanaT.update(arm_f=88, elb_f=8, hand_f='open', arm_b=60, elb_b=20, lean=8 + 6 * ph, x=1380 + 30 * ph, expr='laugh')
        elif n == 'g_giggle' and doing:
            nanaT.update(arm_f=122, elb_f=128, hand_f='relax', expr='laugh', bob=-6 * abs(math.sin(t * 11)), head_tilt=5 * math.sin(t * 8))
        elif n == 'g_yawn' and doing:
            k = t - say0['t']
            if k < say0['d'] * 0.55:
                fl = -1 if int(k / 0.7) % 2 == 0 else 1
                nanaT.update(face=fl, look=1, expr='neutral', head_tilt=6 * fl)
            else:
                nanaT.update(arm_f=170, elb_f=12, hand_f='open', arm_b=170, elb_b=12, hand_b='open', expr='laugh', talk=0.95, lean=-6)
        elif n == 'g_fidget' and doing:
            k = t - say0['t']
            if k < say0['d'] * 0.35: nanaT.update(arm_f=150 + 8 * math.sin(t * 16), elb_f=122, hand_f='relax', expr='neutral', head_tilt=8)
            elif k < say0['d'] * 0.7: nanaT.update(arm_f=30 + 14 * math.sin(t * 12), elb_f=40, hand_f='fist', arm_b=30 - 14 * math.sin(t * 12), elb_b=40, hand_b='fist', expr='happy')
            else: nanaT.update(arm_f=60, elb_f=70, hand_f='fist', arm_b=60, elb_b=70, hand_b='fist', expr='laugh', bob=-3 * abs(math.sin(t * 14)))
        elif n == 'g_run' and acting:
            rb = active(t, sh, 'sfx', 'run', 0.4)
            runb = next(b for b in sh['beats'] if b.get('name') == 'run')
            k = (t - runb['t'] + 0.4) / (runb['d'] + 1.0)
            if 0 <= k <= 1 and not asking:
                nanaT.update(x=lerp(1500, 120, k), walk=t * 3.2, face=-1, expr='laugh', arm_f=70, elb_f=70, hand_f='fist', y=GROUND + 40, s=1.0)
            elif k > 1:
                back = (t - (runb['t'] + runb['d'] + 0.6)) / 2.2
                nanaT.update(x=lerp(120, 1380, back), walk=(t * 1.6 if 0 < back < 1 else None), face=(1 if back < 1 else -1), expr='laugh',
                             y=lerp(GROUND + 40, GROUND - 10, back))
        if asking:
            nanaT.update(arm_f=100, elb_f=60, hand_f='open', expr='happy', head_tilt=-6)
        if n == 'right_intro' or (n == 'after' and t >= sh['beats'][1]['t']): nanaT.update(arm_f=95 + 8 * math.sin(t * 2.5) if m['NANA'] > 0.05 else 20, elb_f=40, hand_f='open')
        if n == 'after' and lt < sh['beats'][1]['t'] - sh['t0']:
            nanaT.update(x=lerp(1750, 1380, lt / 2.2), walk=lt * 1.4 if lt < 2.2 else None)
        # draw: Nana in front of kids when he runs past them
        front = n == 'g_run' and nanaT.get('walk') is not None
        lay += C.maryam(marT) + screen(30, 260)
        lay += (over_kids + C.nana(nanaT)) if front else (C.nana(nanaT) + over_kids)
        if anyN:
            kk = min(1, (t - anyN['t']) / 0.25); over += cross(1560, 260, kk)
        return 'hall', (0, 1), lay, over, texts

    if n.startswith('s_'):
        steps = ['s_saff', 's_nazar', 's_takbir', 's_qiyam', 's_ruku', 's_sajda', 's_jalsa']
        idx = steps.index(n)
        pose = {0: 'stand', 1: 'stand', 2: 'takbir', 3: 'qiyam', 4: 'ruku', 5: 'sajda', 6: 'sit'}[idx]
        trans = ease(lt / 0.7)
        xs = (230, 630, 1020, 1410)
        lay = ''
        nanaT = A(x=xs[0], y=GROUND, s=0.92, pose=pose, blink=bl(5), talk=m['NANA'], expr='warm', look_y=(0.8 if idx >= 1 else 0))
        if idx == 0: nanaT.update(arm_f=60 + 30 * math.sin(t * 2) if m['NANA'] > 0.05 else 10, elb_f=30, hand_f='open', face=1)
        lay += C.nana(nanaT)
        for i, (w, fn) in enumerate(KIDS):
            x = xs[i + 1]
            if idx == 0:   # shuffle into a straight row
                x = lerp(xs[i + 1] + (60, 160, 280)[i], xs[i + 1], (lt - 1.2) / 2.0)
            st = A(x=x, y=GROUND + (0 if idx else (24, -18, 30)[i] * (1 - ease((lt - 1.2) / 2.0))), s=0.88, pose=pose, blink=bl(i), talk=m[w],
                   expr='happy' if idx == 6 else 'neutral', look_y=(0.8 if idx >= 1 else 0), walk=(t * 1.6 if idx == 0 and 1.2 < lt < 3.2 else None))
            if pose == 'stand' and idx == 0: st['face'] = 1
            if active(t, sh, 'say', w): st['expr'] = 'excited' if w == 'ZAID' else 'happy'
            lay += fn(st)
        # step label card
        k = ease(lt / 0.5)
        over = f'<g opacity="{k}"><rect x="60" y="60" width="760" height="110" rx="30" fill="#fffbea" stroke="#3b2a20" stroke-width="7"/></g>' + tick(1780, 120, k)
        texts.append(('L:' + story.STEPS[idx], 440, 115, 56, '#2E8B57', k))
        return 'hall', (0, 1), lay, over, texts

    if n == 'proud':
        xs = (620, 860, 1100)
        lay = C.nana(A(x=1420, y=GROUND, s=0.95, face=-1, talk=m['NANA'], blink=bl(5), expr='proud', arm_f=100, elb_f=50, hand_f='open'))
        for i, (w, fn) in enumerate(KIDS):
            lay += fn(A(x=xs[i], y=GROUND, s=0.9, face=1, blink=bl(i), expr='laugh' if active(t, sh, 'sfx', 'kids_giggle', 0.3) else 'happy', look=1,
                        bob=-5 * abs(math.sin(t * 8 + i)) if active(t, sh, 'sfx', 'kids_giggle', 0.3) else 0))
        for i in range(3):
            kk = ((t * 0.7 + i / 3) % 1); lay += heart(700 + i * 300, GROUND - 520 - kk * 160, 0.8, 1 - kk)
        return 'hall', (0, 1), lay, '', texts
    return 'hall', (0, 1), '', '', texts

# ---------------------------------------------------------------- text
_f = {}
def ufont(sz, bold=True):
    k = ('u', sz, bold)
    if k not in _f: _f[k] = ImageFont.truetype(UFONT_B if bold else UFONT, sz, layout_engine=ImageFont.Layout.RAQM)
    return _f[k]
def lfont(sz, bold=False):
    k = ('l', sz, bold)
    if k not in _f: _f[k] = ImageFont.truetype(LFONT_B if bold else LFONT, sz)
    return _f[k]

COLORS = {'ALI': '#D52B31', 'BILAL': '#2f78bf', 'ZAID': '#2f9e5b', 'NANA': '#7b5a3c', 'MARYAM': '#c0396b', 'ALL': '#e08a1e'}

def draw_caption(im, cap):
    who, text = cap; d = ImageDraw.Draw(im); f = lfont(44); lh = 60
    words = text.split(); lines = []; cur = ''
    for w_ in words:
        tt = (cur + ' ' + w_).strip()
        if d.textlength(tt, font=f) > 1560 and cur: lines.append(cur); cur = w_
        else: cur = tt
    lines.append(cur)
    bh = lh * len(lines) + 34; y0 = H - bh - 18
    bw = max(d.textlength(l, font=f) for l in lines) + 90
    if who == 'ALL': bw = max(bw, 420)
    d.rounded_rectangle([W / 2 - bw / 2, y0, W / 2 + bw / 2, y0 + bh], 26, fill=(255, 255, 255, 238), outline=(59, 42, 32), width=5)
    if who in COLORS:
        nm = story.NAMES[who]; nf = lfont(32, True); nw = d.textlength(nm, font=nf) + 44
        xl = W / 2 - bw / 2 + 30
        d.rounded_rectangle([xl, y0 - 34, xl + nw, y0 + 16], 20, fill=COLORS[who], outline=(59, 42, 32), width=4)
        d.text((xl + nw / 2, y0 - 9), nm, font=nf, fill='white', anchor='mm')
    for i, l in enumerate(lines):
        d.text((W / 2, y0 + 17 + i * lh), l, font=f, fill=(40, 30, 24), anchor='ma')

def draw_texts(im, texts):
    if not texts: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); op = 1
    for s, x, y, sz, col, o in texts:
        if s.startswith('U:'): d.text((x, y), s[2:], font=ufont(sz), fill=col, anchor='mm', direction='rtl', language='ur')
        else: d.text((x, y), s[2:], font=lfont(sz, True), fill=col, anchor='mm')
        op = o
    if op < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * op)))
    im.alpha_composite(lay)

def name_of(t): return shot_at(t)['name']

def frame(t):
    name, (cx, zoom), lay, over, texts = scene(t)
    b = bg(name); bw = b.width; world = b.copy()
    if lay:
        png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{bw}" height="{H}">{C.DEFS}{lay}</svg>'.encode())
        o = Image.open(io.BytesIO(png)); world.paste(o, (0, 0), o)
    lift = 0 if name_of(t) in ('title', 'moral', 'end') else LIFT     # keep feet and sajda above the captions
    if lift:
        tall = Image.new('RGB', (bw, H + lift), (181, 56, 58)); tall.paste(world, (0, 0))
        world = tall.crop((0, lift, bw, H + lift))
    if zoom != 1:
        vw, vh = W / zoom, H / zoom; x0 = (bw - vw) / 2 + cx; y0 = (H - vh) * 0.75
        im = world.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh))).resize((W, H), Image.LANCZOS)
    else: im = world.crop((int(cx), 0, int(cx) + W, H))
    if over:
        png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{over}</svg>'.encode())
        o = Image.open(io.BytesIO(png)); im.paste(o, (0, 0), o)
    sh = shot_at(t); lt = t - sh['t0']; rt = sh['t1'] - t
    im = im.convert('RGBA'); draw_texts(im, texts)
    cap = caption(t)
    if cap: draw_caption(im, cap)
    fade = min(1, lt / 0.3, rt / 0.3) if sh['name'] != 'title' or lt > 0.3 else lt / 0.3
    if sh['name'].startswith('s_') and sh['name'] != 's_saff': fade = min(1, rt / 0.15 if sh['name'] == 's_jalsa' else 1, 1)
    if sh['name'].startswith('g_') and sh['name'] != 'g_push': fade = min(1, rt / 0.3) if sh['name'] == 'g_run' else 1
    if fade < 1: im = Image.blend(Image.new('RGBA', (W, H), (255, 255, 255, 255)), im, max(0, fade))
    return im.convert('RGB')

def chunk(args):
    i, a, b = args
    out = f'{BUILD}/chunks/c{i:03d}.mp4'
    if os.path.exists(out): return out
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', out + '.tmp.mp4'], stdin=subprocess.PIPE)
    for k in range(a, b): p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close(); p.wait(); os.rename(out + '.tmp.mp4', out)
    return out

def music_bed(path):
    import numpy as np, soundfile as sf
    sr = 48000; n = int(TOTAL * sr); x = np.zeros(n)
    notes = [293.7, 349.2, 440.0, 587.3, 440.0, 349.2, 261.6, 329.6, 392.0, 523.3, 392.0, 329.6]
    for s in SHOTS:
        if s['name'] not in ('title', 'moral', 'end'): continue
        tt = s['t0']; i = 0
        while tt < s['t1'] - 0.2:
            f0 = notes[i % len(notes)]; L = int(sr * 0.9); k = np.arange(L) / sr
            tone = (np.sin(2 * np.pi * f0 * k) + 0.3 * np.sin(4 * np.pi * f0 * k)) * np.exp(-k * 4.5)
            a = int(tt * sr); b = min(n, a + L); x[a:b] += 0.12 * tone[:b - a]; tt += 0.32; i += 1
    sf.write(path, np.stack([x, x], 1), sr)

def mix(out):
    inputs, filt = [], []; k = 0
    for s in SHOTS:
        for b in s['beats']:
            inputs += ['-i', b['file']]; ms = int(b['t'] * 1000)
            filt.append(f'[{k}:a]aresample=48000,volume={1.0 if b["kind"] == "say" else 0.85},adelay={ms}|{ms}[a{k}]'); k += 1
    bed = f'{BUILD}/bed.wav'; music_bed(bed); inputs += ['-i', bed]
    filt.append(f'[{k}:a]aresample=48000,volume=0.6,atrim=0:{TOTAL:.2f}[mus]')
    filt.append(''.join(f'[a{i}]' for i in range(k)) + f'[mus]amix=inputs={k+1}:normalize=0:dropout_transition=0,alimiter=limit=0.95[out]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '[out]', '-t', f'{TOTAL:.2f}', '-ac', '2', '-ar', '48000', out], check=True)

OUTFILE = f'{BUILD}/masjid_ke_adaab.mp4'

if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        ts = [float(x) for x in sys.argv[2].split(',')]
        ims = [frame(t).resize((640, 360)) for t in ts]
        cols = 3; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (640 * cols, 360 * rows), 'white')
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
        sheet.save(sys.argv[3] if len(sys.argv) > 3 else f'{BUILD}/sheet.png'); print('ok')
    elif sys.argv[1] == 'video':
        nw = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        os.makedirs(f'{BUILD}/chunks', exist_ok=True)
        N = int(TOTAL * FPS); step = 96
        jobs = [(i, a, min(a + step, N)) for i, a in enumerate(range(0, N, step))]
        with Pool(nw) as p: outs = p.map(chunk, jobs)
        open(f'{BUILD}/chunks/list.txt', 'w').write(''.join(f"file '{os.path.basename(o)}'\n" for o in outs))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{BUILD}/chunks/list.txt', '-c', 'copy', f'{BUILD}/video.mp4'], check=True)
        mix(f'{BUILD}/audio_mix.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{BUILD}/video.mp4', '-i', f'{BUILD}/audio_mix.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', OUTFILE], check=True)
        print('done', OUTFILE)
