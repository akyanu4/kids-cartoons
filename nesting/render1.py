"""Render Nesting Stories episode 1 "Naya Kirayedaar".
python3 nesting/ep1_voices.py; python3 nesting/render1.py frames 5,30 out.png | clip a b out.mp4 | video 2"""
import os, sys, json, math, io, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, ROOT); os.chdir(ROOT)
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import chars2 as C, people as P, ep1_story as story

W, H, FPS = 1920, 1080, 24
GROUND = 1000
LIFT = 120
BUILD = 'build_nesting1'
os.makedirs(f'{BUILD}/bg', exist_ok=True)
TL = json.load(open(f'{BUILD}/timeline.json'))
SHOTS, TOTAL = TL['shots'], TL['total']
_FD = os.path.expanduser('~/.fonts')
UFONT, UFONT_B = f'{_FD}/NotoNastaliqUrdu-Regular.ttf', f'{_FD}/NotoNastaliqUrdu-Bold.ttf'
LFONT_B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
LFONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
if not os.path.exists(LFONT): LFONT = LFONT_B
CARDS = ('title', 'end')
BODY = C.BODY['nana']


def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * ease(x)


# ---------------------------------------------------------------- props + backgrounds
S = 'stroke="#4a3628" stroke-width="6" stroke-linejoin="round"'


def box(x, y, w, h, label='', tilt=0):
    s = f'<g transform="translate({x},{y}) rotate({tilt})">'
    s += f'<rect x="0" y="{-h}" width="{w}" height="{h}" fill="#c99a5f" {S}/>'
    s += f'<path d="M0,{-h} L{w*0.5},{-h-18} L{w},{-h}" fill="#dcb47c" {S}/>'
    s += f'<rect x="{w/2-14}" y="{-h}" width="28" height="{h}" fill="#e8d3a3" opacity=".8"/>'
    if label: s += f'<text x="{w/2}" y="{-h/2+10}" font-family="Poppins" font-weight="700" font-size="{min(30, w/6)}" fill="#6b4a2a" text-anchor="middle">{label}</text>'
    s += f'<path d="M{w*0.12},{-h*0.25} l20,0 l-8,-8 M{w*0.12+20},{-h*0.25} l-8,8" stroke="#6b4a2a" stroke-width="4" fill="none"/>'
    return s + '</g>'


def window(x, y, w, h, view='sky', curtain='#d9534f'):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#bfe3f5" {S}/>'
    if view == 'masjid':
        m = x + w * 0.55; g = y + h * 0.82
        s += f'<path d="M{m-90},{g} L{m-90},{g-90} Q{m},{g-210} {m+90},{g-90} L{m+90},{g}Z" fill="#7fb59a" {S}/>'
        s += f'<path d="M{m-8},{g-200} L{m},{g-232} L{m+8},{g-200}Z" fill="#e2b64a"/>'
        s += f'<rect x="{x+30}" y="{g-250}" width="34" height="250" fill="#7fb59a" {S}/><path d="M{x+24},{g-250} Q{x+47},{g-300} {x+70},{g-250}Z" fill="#7fb59a" {S}/>'
        s += f'<rect x="{x}" y="{g}" width="{w}" height="{y+h-g}" fill="#a7c97f"/>'
    else:
        s += f'<ellipse cx="{x+w*0.3}" cy="{y+h*0.3}" rx="60" ry="24" fill="#fff" opacity=".9"/><ellipse cx="{x+w*0.7}" cy="{y+h*0.5}" rx="50" ry="18" fill="#fff" opacity=".8"/>'
        s += f'<rect x="{x}" y="{y+h*0.78}" width="{w}" height="{h*0.22}" fill="#a7c97f"/>'
    s += f'<path d="M{x+w/2},{y} L{x+w/2},{y+h} M{x},{y+h/2} L{x+w},{y+h/2}" stroke="#4a3628" stroke-width="8"/>'
    s += f'<rect x="{x-30}" y="{y-34}" width="{w+60}" height="20" rx="8" fill="#8a5a33" {S}/>'
    for sx, cx in ((1, x - 20), (-1, x + w + 20)):
        s += f'<path d="M{cx},{y-20} Q{cx+sx*70},{y+h*0.4} {cx+sx*30},{y+h+20} L{cx},{y+h+20}Z" fill="{curtain}" {S}/>'
    return s + f'<rect x="{x-14}" y="{y+h}" width="{w+28}" height="18" fill="#e9dcc2" {S}/>'


def floor(w, col='#b98a5a', line='#a0744a'):
    s = f'<rect y="700" width="{w}" height="{H-700}" fill="{col}"/>'
    for yy in (760, 840, 940, 1060): s += f'<rect y="{yy}" width="{w}" height="4" fill="{line}"/>'
    return s + f'<rect y="694" width="{w}" height="16" fill="#7a5232"/>'


def room(w, view='sky'):
    """Chacha's rented room, half packed"""
    s = f'<rect width="{w}" height="{H}" fill="#efe2c8"/>'
    for x in range(0, w, 90): s += f'<rect x="{x}" width="40" height="700" fill="#e8d8b8"/>'
    s += floor(w)
    s += window(1240, 230, 380, 320, view)
    # calendar with every day crossed out
    s += f'<rect x="880" y="220" width="190" height="220" fill="#fff" {S}/><rect x="880" y="220" width="190" height="50" fill="#d9534f" {S}/>'
    for r in range(4):
        for c in range(5):
            cx, cy = 900 + c * 34, 292 + r * 36
            s += f'<path d="M{cx},{cy} l18,18 M{cx+18},{cy} l-18,18" stroke="#d9534f" stroke-width="4"/>'
    # boxes stacked on the left
    s += box(80, 700, 220, 170, 'Saamaan') + box(320, 700, 200, 150, 'Bartan') + box(140, 530, 200, 150, 'Kapde', -3)
    s += box(560, 700, 170, 120, '') + box(360, 550, 140, 110, 'Misc', 4) + box(1680, 700, 200, 140, 'Kitaabein')
    s += f'<rect x="540" y="430" width="70" height="70" rx="6" fill="#7aa86a" {S}/><text x="575" y="478" font-family="Poppins" font-weight="700" font-size="28" fill="#fff" text-anchor="middle">14</text>'
    return s


def hall_bg(w, door=True):
    """Imran's house: big hall with sofa, window, father's photo, desk with laptop"""
    s = f'<rect width="{w}" height="{H}" fill="#e3ecef"/><rect width="{w}" height="120" fill="#d3e0e5"/>'
    s += floor(w, '#c69c6d', '#ad8456')
    if door:
        s += f'<rect x="120" y="250" width="270" height="450" fill="#9a6b3f" {S}/><rect x="150" y="280" width="210" height="180" rx="8" fill="#ac7a4a" {S}/>'
        s += f'<rect x="150" y="490" width="210" height="180" rx="8" fill="#ac7a4a" {S}/><circle cx="352" cy="480" r="12" fill="#e2b64a" {S}/>'
        s += f'<rect x="100" y="232" width="310" height="24" fill="#7a5232" {S}/>'
    s += window(640, 200, 420, 330, 'sky', '#6aa5a0')
    # sofa
    s += f'<rect x="1150" y="520" width="520" height="120" rx="40" fill="#3f8f8a" {S}/><rect x="1120" y="600" width="580" height="110" rx="30" fill="#4aa39d" {S}/>'
    s += f'<rect x="1100" y="560" width="70" height="150" rx="30" fill="#3f8f8a" {S}/><rect x="1650" y="560" width="70" height="150" rx="30" fill="#3f8f8a" {S}/>'
    s += f'<rect x="1250" y="560" width="90" height="70" rx="20" fill="#f2c45f" {S}/>'
    # plant + lamp
    s += f'<path d="M1780,700 L1760,600 L1860,600 L1840,700Z" fill="#c76b4a" {S}/>'
    for a in (-40, -15, 10, 35): s += f'<path d="M1810,600 Q{1810+a*2},{480} {1810+a*3},{440}" fill="none" stroke="#3c8a4a" stroke-width="16" stroke-linecap="round"/>'
    return s


def office(w):
    """Imran's work corner, for the phone call"""
    s = f'<rect width="{w}" height="{H}" fill="#dfe9f2"/>' + floor(w, '#c69c6d', '#ad8456')
    s += f'<rect x="200" y="210" width="300" height="200" rx="8" fill="#fff" {S}/><text x="350" y="330" font-family="Poppins" font-weight="700" font-size="34" fill="#2f78bf" text-anchor="middle">&lt;/code&gt;</text>'
    s += f'<rect x="80" y="620" width="760" height="40" rx="8" fill="#8a5a33" {S}/><rect x="120" y="660" width="30" height="240" fill="#7a5232"/><rect x="770" y="660" width="30" height="240" fill="#7a5232"/>'
    s += f'<path d="M520,620 L560,470 L800,470 L770,620Z" fill="#2f3440" {S}/><rect x="580" y="490" width="200" height="110" fill="#7fd3ff" transform="skewX(-12) translate(115,0)"/>'
    s += f'<rect x="180" y="570" width="56" height="50" rx="8" fill="#f2f2f2" {S}/><path d="M236,580 q24,8 0,26" fill="none" stroke="#4a3628" stroke-width="6"/>'
    return s


def nested(src, x, w, view_x):
    return f'<svg x="{x}" y="0" width="{w}" height="{H}" viewBox="{view_x} 0 {w} {H}">{src}</svg>'


def title_bg():
    s = f'<rect width="{W}" height="{H}" fill="#fdf1dc"/>'
    for i in range(14): s += f'<circle cx="{(i*157)%W}" cy="{(i*263)%H}" r="{40+(i*13)%60}" fill="#f7dfb3" opacity=".6"/>'
    # logo: little house in a nest
    s += f'<g transform="translate(960,330)"><path d="M-200,40 Q0,170 200,40 Q140,120 0,130 Q-140,120 -200,40Z" fill="#a8743f" {S}/>'
    for k in range(-5, 6): s += f'<path d="M{k*34},{60+abs(k)*4} q20,30 40,4" fill="none" stroke="#7a5232" stroke-width="5"/>'
    s += f'<rect x="-90" y="-60" width="180" height="120" fill="#f2c45f" {S}/><path d="M-120,-56 L0,-150 L120,-56Z" fill="#d9534f" {S}/>'
    s += f'<rect x="-24" y="0" width="48" height="60" fill="#8a5a33" {S}/><rect x="40" y="-34" width="34" height="30" fill="#bfe3f5" {S}/></g>'
    return s


def bg_svg(name):
    if name in ('title', 'end'): return W, title_bg()
    if name == 'room': return W, room(W)
    if name == 'room_masjid': return W, room(W, 'masjid')
    if name == 'hall': return W, hall_bg(W)
    if name == 'split':
        return W, nested(room(W), 0, 955, 700) + nested(office(W), 965, 955, 0) + f'<rect x="952" y="0" width="16" height="{H}" fill="#3b2a20"/>'
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


BG_OF = {'title': 'title', 'boxes': 'room', 'namaz': 'room_masjid', 'ad': 'room', 'call': 'split', 'imran': 'hall',
         'arrive': 'hall', 'memory': 'hall', 'deal': 'hall', 'next': 'hall', 'end': 'end'}


# ---------------------------------------------------------------- timing helpers
def shot_at(t):
    for s in SHOTS:
        if s['t0'] <= t < s['t1']: return s
    return SHOTS[-1]


def mouth(t, who):
    for s in SHOTS:
        for b in s['beats']:
            if b['kind'] == 'say' and b['who'] == who and b['t'] <= t < b['t'] + b['d']:
                i = int((t - b['t']) * FPS); e = b['env']
                return e[i] if i < len(e) else 0
    return 0


def says(sh, t, who=None, n=None):
    """the line being spoken now in this shot (optionally by who / the n-th line of who)"""
    k = 0
    for b in sh['beats']:
        if b['kind'] != 'say': continue
        if who and b['who'] != who: continue
        if n is not None and k != n: k += 1; continue
        if b['t'] - 0.1 <= t < b['t'] + b['d'] + 0.2: return b
        k += 1
    return None


def line(sh, who, n):
    k = 0
    for b in sh['beats']:
        if b['kind'] == 'say' and b['who'] == who:
            if k == n: return b
            k += 1
    return None


def sfx_at(sh, name):
    return next((b for b in sh['beats'] if b['kind'] == 'sfx' and b['name'] == name), None)


def since(b, t): return -1 if b is None else t - b['t']


def caption(t):
    for s in SHOTS:
        for b in s['beats']:
            if b['kind'] == 'say' and b['t'] <= t < b['t'] + b['d'] + 0.15: return b['who'], b['text']
    return None


def talk(m): return min(1.0, m * 1.1)


EMO2EXPR = {'playful': 'happy', 'neutral': 'neutral'}


def person(who, t, sh, **kw):
    """state for CHACHA / IMRAN with talking mouth and the emotion of the current line"""
    st = dict(s=1.0, face=1, blink=0, talk=talk(mouth(t, who)), expr='neutral')
    b = says(sh, t, who)
    if b: st['expr'] = EMO2EXPR.get(b['emo'], b['emo'])
    st.update(kw)
    return st


def ear_arm(face=1):
    """front arm angles that bring a phone to the ear"""
    a, e = C._arm_to(BODY, 0, 0, BODY['sf'], (78, -500), up=False)
    return dict(arm_f=a, elb_f=e, hold_f='phone', hold_tilt_f=-15)


def phone_up():
    a, e = C._arm_to(BODY, 0, 0, BODY['sf'], (105, -380), up=False)
    return dict(arm_f=a, elb_f=e, hold_f='phone', hold_tilt_f=-8)


# ---------------------------------------------------------------- overlays
def rooster(x, y, s, op):
    return (f'<g transform="translate({x},{y}) scale({s})" opacity="{op}"><ellipse cx="0" cy="0" rx="60" ry="46" fill="#fff" {S}/>'
            f'<path d="M-50,-10 Q-110,-60 -90,10 Q-80,-40 -50,0Z" fill="#2f6b3f" {S}/><circle cx="46" cy="-44" r="30" fill="#fff" {S}/>'
            f'<path d="M34,-74 q8,-22 16,-2 q8,-22 16,0 q8,-14 8,6Z" fill="#e23b3b" {S}/><path d="M74,-46 L98,-38 L74,-30Z" fill="#f2b33d" {S}/>'
            f'<path d="M60,-22 q6,16 -4,18" fill="#e23b3b" {S}/><circle cx="54" cy="-48" r="5" fill="#222"/>'
            f'<path d="M100,-60 l40,-20 M104,-44 l46,0 M100,-28 l40,16" stroke="#3b2a20" stroke-width="6" stroke-linecap="round"/></g>')


def phone_ad(op, sc):
    """big phone with the rental ad"""
    return (f'<g opacity="{op:.2f}" transform="translate(960,520) scale({sc:.3f})"><rect x="-260" y="-420" width="520" height="840" rx="60" fill="#22252b" stroke="#3b2a20" stroke-width="10"/>'
            f'<rect x="-226" y="-370" width="452" height="740" rx="18" fill="#ffffff"/>'
            f'<rect x="-226" y="-370" width="452" height="120" rx="18" fill="#2f9e5b"/>'
            f'<rect x="-190" y="-220" width="380" height="230" rx="16" fill="#e3ecef" stroke="#3b2a20" stroke-width="5"/>'
            f'<rect x="-150" y="-110" width="300" height="80" rx="24" fill="#4aa39d" stroke="#3b2a20" stroke-width="4"/>'
            f'<rect x="-60" y="-200" width="120" height="70" fill="#bfe3f5" stroke="#3b2a20" stroke-width="4"/></g>')


def thought(x, y, op):
    s = f'<g opacity="{op:.2f}">'
    for i, (dx, dy, r) in enumerate(((0, 0, 14), (30, -40, 22))): s += f'<circle cx="{x+dx}" cy="{y+dy}" r="{r}" fill="#fff" stroke="#3b2a20" stroke-width="5"/>'
    return s + '</g>'


# ---------------------------------------------------------------- scenes
def scene(t):
    sh = shot_at(t); n = sh['name']; lt = t - sh['t0']; dur = sh['t1'] - sh['t0']
    bl = lambda seed: 0
    lay, over, texts = '', '', []
    cam = (0, 1.0)

    if n == 'title':
        a = ease(lt / 0.8)
        texts = [('L:' + story.TITLE, 960, 600, 120, (217, 83, 79), a), ('U:' + story.TITLE_UR, 960, 760, 84, (74, 54, 40), a),
                 ('L:Nesting Stories  •  ' + story.EPISODE, 960, 900, 44, (122, 82, 50), a)]
        return n, cam, lay, over, texts

    if n == 'boxes':
        tape = sfx_at(sh, 'tape'); roo = sfx_at(sh, 'rooster')
        st = person('CHACHA', t, sh, x=1040, y=GROUND)
        l1 = line(sh, 'CHACHA', 0); l2 = line(sh, 'CHACHA', 1)
        if t < l1['t']:                                   # narrator: Chacha proudly surveys his boxes
            st.update(face=-1, expr='happy', arm_f=40, elb_f=60, hand_f='point', look=0.3)
        elif t < l1['t'] + l1['d'] + 0.3:                 # "14th house... this year!"
            st.update(face=1, arm_f=110 + 8 * math.sin(lt * 3), elb_f=20, hand_f='open')
        elif tape and tape['t'] - 1.2 <= t < tape['t'] + tape['d']:  # taping another box shut
            k = ease((t - tape['t'] + 1.2) / 0.6)
            st.update(face=-1, x=lerp(1040, 820, (t - tape['t'] + 1.2) / 0.8), lean=24 * k, arm_f=70 + 10 * math.sin(t * 14), elb_f=20,
                      arm_b=60, elb_b=20, expr='thoughtful', walk=None)
        elif t < l2['t'] + l2['d'] + 0.2:                  # complaining about the window and the rooster
            st.update(x=820, face=1, arm_f=95, elb_f=70, hand_f='point', expr=st['expr'] or 'thoughtful')
        else:
            st.update(x=820, face=1)
        if roo and t >= roo['t'] - 0.1:
            k = t - roo['t']
            st.update(expr='surprised', bob=-40 * max(0, math.sin(min(k, 0.5) * math.pi * 2)), arm_f=150, arm_b=150, elb_f=30, elb_b=30, hand_f='open', hand_b='open')
            over += rooster(1440, 470, 1.0, min(1, k / 0.15))
        lay = P.chacha(st)
        cam = (0, 1.08)
        return n, cam, lay, over, texts

    if n == 'namaz':
        st = person('CHACHA', t, sh, x=980, y=GROUND)
        l1 = line(sh, 'CHACHA', 0)
        if t < l1['t']:
            st.update(face=1, look=0.8, expr='neutral', head_tilt=-4)    # glances at the masjid through the window
        else:
            st.update(face=-1 if lt % 2 < 1.4 else 1, arm_f=100 + 25 * math.sin(lt * 7), elb_f=40, hand_f='open', expr='happy')
        lay = P.chacha(st)
        cam = (60, 1.05)
        return n, cam, lay, over, texts

    if n == 'ad':
        ding = sfx_at(sh, 'ding'); ring = sfx_at(sh, 'ring'); l1 = line(sh, 'CHACHA', 0)
        st = person('CHACHA', t, sh, x=960, y=GROUND, face=1)
        if t < l1['t']:
            st.update(phone_up()); st.update(expr='neutral', look=0.6, look_y=0.5)
        elif t < l1['t'] + l1['d'] + 0.1:
            st.update(phone_up()); st.update(bob=-14 * abs(math.sin(lt * 6)), arm_b=140, elb_b=30, hand_b='open')
        else:
            st.update(ear_arm()); st.update(expr='happy')
        lay = P.chacha(st)
        if ding and ding['t'] <= t < l1['t'] + l1['d'] * 0.75:
            k = t - ding['t']; sc = 0.6 + 0.4 * ease(k / 0.35); op = min(1, k / 0.25, (l1['t'] + l1['d'] * 0.75 - t) / 0.3)
            over += phone_ad(op, sc * 0.95)
            texts = [('L:KIRAYE KE LIYE', 960, 520 - 330 * sc * 0.95 + 20, int(46 * sc), (255, 255, 255), op),
                     ('L:Poora Hall', 960, 520 + 70 * sc * 0.95, int(54 * sc), (40, 30, 24), op),
                     ('L:Bijli • Paani • Internet', 960, 520 + 150 * sc * 0.95, int(36 * sc), (47, 158, 91), op),
                     ('L:sab shaamil!', 960, 520 + 205 * sc * 0.95, int(36 * sc), (47, 158, 91), op),
                     ('L:Contact: Imran', 960, 520 + 300 * sc * 0.95, int(36 * sc), (47, 120, 191), op)]
        cam = (0, 1.0)
        return n, cam, lay, over, texts

    if n == 'call':
        hang = sfx_at(sh, 'hangup')
        c = person('CHACHA', t, sh, x=480, y=GROUND, face=1); c.update(ear_arm())
        i = person('IMRAN', t, sh, x=1440, y=GROUND, face=-1); i.update(ear_arm())
        if says(sh, t, 'CHACHA'): c['bob'] = -10 * abs(math.sin(lt * 7))
        if hang and t >= hang['t']:
            c.update(phone_up()); c.update(expr='happy', arm_b=150, elb_b=20, hand_b='wave')
            i.update(phone_up()); i.update(expr='surprised' if t < hang['t'] + hang['d'] else i['expr'], look=0.7, look_y=0.4)
            if says(sh, t, 'IMRAN'): i.update(expr='laugh', bob=-6 * abs(math.sin(lt * 9)))
        lay = P.chacha(c) + P.imran(i)
        return n, cam, lay, over, texts

    if n == 'imran':
        i = person('IMRAN', t, sh, x=900, y=GROUND, face=1, expr='warm')
        i.update(arm_b=150 + 12 * math.sin(lt * 6), elb_b=20, hand_b='wave', expr='happy')
        lay = P.abba_photo(1500, 330, 0.75) + P.imran(i)
        a = ease((lt - 0.5) / 0.5)
        texts = [('L:Imran', 1380, 860 - LIFT, 64, (47, 120, 191), a), ('L:Software Engineer, Hyderabad', 1380, 930 - LIFT, 38, (60, 50, 40), a)]
        cam = (0, 1.0)
        return n, cam, lay, over, texts

    if n == 'arrive':
        knock = sfx_at(sh, 'knock'); l1 = line(sh, 'CHACHA', 0)
        i = person('IMRAN', t, sh, x=1250, y=GROUND, face=-1)
        k = (t - (l1['t'] - 0.3)) / 2.2 if l1 else 0
        cx = lerp(150, 700, k)
        c = person('CHACHA', t, sh, x=cx, y=GROUND, face=1, hold_f='suitcase', arm_f=6)
        if 0 < k < 1: c['walk'] = (t * 1.6) % 1
        if knock and t < knock['t'] + knock['d']: c = None; i.update(look=-0.8, expr='surprised')
        if says(sh, t, 'IMRAN'): i.update(arm_f=70, elb_f=10, hand_f='open', arm_b=70, elb_b=10, hand_b='open')
        door_open = c is not None
        lay = P.abba_photo(1500, 330, 0.75)
        if door_open: lay += f'<rect x="120" y="250" width="270" height="450" fill="#3b2a20"/><path d="M120,250 L60,230 L60,720 L120,700Z" fill="#9a6b3f" {S}/>'
        lay += (P.chacha(c) if c else '') + P.imran(i)
        return n, cam, lay, over, texts

    if n == 'memory':
        c = person('CHACHA', t, sh, x=600, y=GROUND, face=1, hold_f='suitcase', expr='happy')
        i = person('IMRAN', t, sh, x=1150, y=GROUND, face=1, expr='gentle')
        l1 = line(sh, 'IMRAN', 0); glow = ease(lt / 1.2)
        if t < l1['t']: i.update(face=1, look=0.6, look_y=-0.3, head_tilt=-4)     # looks up at Abba's photo
        else: i.update(face=-1, expr='gentle', head_tilt=3)                       # and back at Chacha
        lay = P.abba_photo(1500, 330, 0.75, glow * 0.9) + P.chacha(c) + P.imran(i)
        over = f'<rect width="{W}" height="{H}" fill="#ffd98a" opacity="{0.12 * glow:.2f}"/>'
        z = lerp(1.0, 1.18, lt / 2.5)
        cam = (lerp(0, 160, lt / 2.5), z)
        return n, cam, lay, over, texts

    if n == 'deal':
        c = person('CHACHA', t, sh, x=650, y=GROUND, face=1, expr='happy')
        i = person('IMRAN', t, sh, x=1150, y=GROUND, face=-1, expr='warm')
        L = [line(sh, 'IMRAN', 0), line(sh, 'CHACHA', 0), line(sh, 'IMRAN', 1), line(sh, 'CHACHA', 1), line(sh, 'CHACHA', 2), line(sh, 'IMRAN', 2)]
        if L[0]['t'] <= t < L[0]['t'] + L[0]['d']: i.update(arm_b=80, elb_b=10, hand_b='open', face=-1)       # "poora hall aapka"
        if t >= L[1]['t']: c.update(expr='surprised' if t < L[3]['t'] else c['expr'])
        if L[3]['t'] <= t < L[4]['t']: c.update(arm_f=150, elb_f=20, arm_b=150, elb_b=20, hand_f='open', hand_b='open', bob=-12 * abs(math.sin(lt * 6)))
        if t >= L[4]['t'] - 0.3: c.update(phone_up()); c.update(expr='happy', look=0.6)
        if t >= L[5]['t']: i.update(expr='laugh', bob=-8 * abs(math.sin(lt * 10)), arm_f=60, elb_f=90)
        lay = P.abba_photo(1500, 330, 0.75) + P.chacha(c) + P.imran(i)
        return n, cam, lay, over, texts

    if n == 'next':
        c = person('CHACHA', t, sh, x=1000, y=GROUND, face=1, expr='happy')
        c.update(phone_up()); c['look'] = 0.6
        l2 = line(sh, 'N', 1)
        lay = box(500, 1000 - LIFT + 120, 200, 140, 'Saamaan') + P.chacha(c)
        if l2 and t > l2['t'] + l2['d'] * 0.6:
            a = ease((t - l2['t'] - l2['d'] * 0.6) / 0.4)
            over = f'<rect x="610" y="110" width="700" height="240" rx="40" fill="#fff" stroke="#3b2a20" stroke-width="8" opacity="{a:.2f}"/>'
            texts = [('L:Agla Episode:', 960, 175, 54, (74, 54, 40), a), ('L:AAMAD', 960, 268, 110, (217, 83, 79), a)]
        cam = (0, 1.0)
        return n, cam, lay, over, texts

    if n == 'end':
        a = ease(lt / 0.6)
        texts = [('L:Shukriya!', 960, 600, 110, (217, 83, 79), a), ('L:Subscribe karein', 960, 740, 64, (74, 54, 40), a),
                 ('L:Nesting Stories', 960, 860, 52, (122, 82, 50), a)]
        return n, cam, lay, over, texts
    raise KeyError(n)


# ---------------------------------------------------------------- drawing
_f = {}
def ufont(sz, bold=True):
    k = ('u', sz, bold)
    if k not in _f: _f[k] = ImageFont.truetype(UFONT_B if bold else UFONT, sz, layout_engine=ImageFont.Layout.RAQM)
    return _f[k]


def lfont(sz, bold=False):
    k = ('l', sz, bold)
    if k not in _f: _f[k] = ImageFont.truetype(LFONT_B if bold else LFONT, sz)
    return _f[k]


COLORS = {'CHACHA': '#7a5232', 'IMRAN': '#2f78bf'}


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
    d.rounded_rectangle([W / 2 - bw / 2, y0, W / 2 + bw / 2, y0 + bh], 26, fill=(255, 255, 255, 238), outline=(59, 42, 32), width=5)
    if who in COLORS:
        nm = story.NAMES[who]; nf = lfont(32, True); nw = d.textlength(nm, font=nf) + 44
        xl = W / 2 - bw / 2 + 30
        d.rounded_rectangle([xl, y0 - 34, xl + nw, y0 + 16], 20, fill=COLORS[who], outline=(59, 42, 32), width=4)
        d.text((xl + nw / 2, y0 - 9), nm, font=nf, fill='white', anchor='mm')
    for i, l in enumerate(lines):
        d.text((W / 2, y0 + 17 + i * lh), l, font=f, fill=(40, 30, 24), anchor='ma')


def draw_texts(im, texts):
    for s, x, y, sz, col, o in texts:
        if o <= 0.01: continue
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if s.startswith('U:'): d.text((x, y), s[2:], font=ufont(sz), fill=col, anchor='mm', direction='rtl', language='ur')
        else: d.text((x, y), s[2:], font=lfont(sz, True), fill=col, anchor='mm')
        if o < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * o)))
        im.alpha_composite(lay)


import motion
for _n in ('chacha', 'imran'): motion.register(P, _n, 'nana')
if os.environ.get('MOTION', '1') == '1': motion.install(sys.modules[__name__])


def frame(t):
    name, (cx, zoom), lay, over, texts = motion.scene(t) if motion._M else scene(t)
    b = bg(BG_OF[name]); bw = b.width; world = b.copy()
    if lay:
        png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{bw}" height="{H}">{C.DEFS}<defs>{P.HALO}</defs>{lay}</svg>'.encode())
        o = Image.open(io.BytesIO(png)); world.paste(o, (0, 0), o)
    lift = 0 if name in CARDS else LIFT
    if lift:
        tall = Image.new('RGB', (bw, H + lift), world.getpixel((10, H - 2))); tall.paste(world, (0, 0))
        world = tall.crop((0, lift, bw, H + lift))
    if zoom != 1:
        vw, vh = W / zoom, H / zoom; x0 = min(max(0, (bw - vw) / 2 + cx), bw - vw); y0 = (H - vh) * 0.6
        im = world.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh))).resize((W, H), Image.LANCZOS)
    else: im = world.crop((int(cx), 0, int(cx) + W, H))
    if over:
        png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{over}</svg>'.encode())
        o = Image.open(io.BytesIO(png)); im.paste(o, (0, 0), o)
    sh = shot_at(t); lt = t - sh['t0']; rt = sh['t1'] - t
    im = im.convert('RGBA'); draw_texts(im, texts)
    cap = caption(t)
    if cap: draw_caption(im, cap)
    fade = min(1, lt / 0.3, rt / 0.3)
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
    """a light bouncy tune under the title and end cards, very quiet under the story"""
    import numpy as np, soundfile as sf
    sr = 48000; n = int(TOTAL * sr); x = np.zeros(n)
    notes = [392.0, 440.0, 493.9, 587.3, 493.9, 440.0, 392.0, 329.6, 392.0, 440.0, 392.0, 293.7]
    tt = 0.0; i = 0
    while tt < TOTAL - 0.3:
        sh = shot_at(tt); vol = 0.13 if sh['name'] in CARDS else 0.025
        f0 = notes[i % len(notes)]; L = int(sr * 0.5); k = np.arange(L) / sr
        tone = (np.sin(2 * np.pi * f0 * k) + 0.25 * np.sin(4 * np.pi * f0 * k)) * np.exp(-k * 7)
        a = int(tt * sr); b = min(n, a + L); x[a:b] += vol * tone[:b - a]
        if i % 2 == 0:
            kb = np.arange(int(sr * 0.25)) / sr; bass = np.sin(2 * np.pi * f0 / 4 * kb) * np.exp(-kb * 10)
            b2 = min(n, a + len(bass)); x[a:b2] += vol * 0.8 * bass[:b2 - a]
        tt += 0.27; i += 1
    sf.write(path, np.stack([x, x], 1), sr)


def mix(out):
    inputs, filt = [], []; k = 0
    for s in SHOTS:
        for b in s['beats']:
            inputs += ['-i', b['file']]; ms = int(b['t'] * 1000)
            filt.append(f'[{k}:a]aresample=48000,volume={1.0 if b["kind"] == "say" else 0.7},adelay={ms}|{ms}[a{k}]'); k += 1
    bed = f'{BUILD}/bed.wav'; music_bed(bed); inputs += ['-i', bed]
    filt.append(f'[{k}:a]aresample=48000,atrim=0:{TOTAL:.2f}[mus]')
    filt.append(''.join(f'[a{i}]' for i in range(k)) + f'[mus]amix=inputs={k+1}:normalize=0:dropout_transition=0,alimiter=limit=0.95[out]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '[out]', '-t', f'{TOTAL:.2f}', '-ac', '2', '-ar', '48000', out], check=True)


OUTFILE = f'{BUILD}/naya_kirayedaar_ep1.mp4'

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
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{BUILD}/video.mp4', '-i', f'{BUILD}/audio_mix.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                        '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '48000', '-shortest', OUTFILE], check=True)
        print('done', OUTFILE)
