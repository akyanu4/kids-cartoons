"""Sing-along video for 'Pyaara Ali'. python3 songs/chant/video.py frames 3,10 out.png | video
Needs build_song/{timeline.json,song.wav} from build.py."""
import os, sys, io, json, math, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import chars2 as C, soft, motion

W, H, FPS = 1920, 1080, 24
B = 'build_song'
TL = json.load(open(f'{B}/timeline.json')); PARTS = TL['parts']; BEAT = TL['beat']; TOTAL = TL['total']
GROUND = 870
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
_f = {}
def font(sz):
    if sz not in _f: _f[sz] = ImageFont.truetype(FB, sz)
    return _f[sz]
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)

S = 'stroke="#4a3628" stroke-width="5" stroke-linejoin="round"'


def bg_svg():
    s = f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fd3ff"/><stop offset="1" stop-color="#d8f1ff"/></linearGradient></defs>'
    s += f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    s += f'<circle cx="1700" cy="150" r="80" fill="#ffd54a"/>'
    for cx, cy, r in ((300, 140, 50), (360, 120, 60), (420, 145, 48), (1100, 110, 45), (1160, 92, 58), (1220, 115, 44)):
        s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" opacity=".95"/>'
    s += f'<path d="M0,560 Q300,430 640,540 Q980,440 1320,540 Q1640,450 1920,540 L1920,{H} L0,{H}Z" fill="#a8d982"/>'
    s += f'<rect y="640" width="{W}" height="{H-640}" fill="#8cc96a"/>'
    # small school building with an "Iqra" sign
    s += f'<rect x="760" y="330" width="400" height="300" fill="#f6e3c2" {S}/><path d="M730,340 L960,220 L1190,340Z" fill="#e2725b" {S}/>'
    s += f'<rect x="910" y="500" width="100" height="130" fill="#8a5a33" {S}/>'
    for x in (800, 1060): s += f'<rect x="{x}" y="400" width="70" height="70" fill="#bfe3f5" {S}/>'
    s += f'<rect x="845" y="268" width="230" height="56" rx="12" fill="#2f9e5b" {S}/><text x="960" y="307" font-family="Poppins" font-weight="700" font-size="34" fill="#fff" text-anchor="middle">Iqra School</text>'
    # bunting
    cols = ['#e74c3c', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6']
    s += f'<path d="M0,120 Q480,230 960,150 Q1440,230 1920,120" fill="none" stroke="#6b4a2a" stroke-width="4"/>'
    for k in range(24):
        x = 40 + k * 80; y = 120 + 90 * math.sin(math.pi * ((x % 960) / 960)) - 10
        s += f'<path d="M{x-22},{y} L{x+22},{y} L{x},{y+44}Z" fill="{cols[k % 5]}" {S}/>'
    for k in range(40):   # flowers
        x = (k * 173) % W; y = 700 + (k * 97) % 330
        s += f'<circle cx="{x}" cy="{y}" r="9" fill="{cols[k % 5]}"/><circle cx="{x}" cy="{y}" r="4" fill="#fff"/>'
    return s


_bg = None
def background():
    global _bg
    if _bg is None:
        f = f'{B}/bg.png'
        if not os.path.exists(f):
            cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{bg_svg()}</svg>'.encode(), write_to=f)
        _bg = soft.background(Image.open(f).convert('RGB'))
    return _bg


def part_at(t):
    for p in PARTS:
        if p['t'] <= t < p['t'] + p['slot']: return p
    return PARTS[-1]


def shot_at(t):
    p = part_at(t); return {'name': f"{p['kind']}{p['t']:.2f}"}


def env_at(p, t):
    if not p['env'] or t < p['t']: return 0
    i = int((t - p['t']) * FPS); return p['env'][i] if i < len(p['env']) else 0


POS = {'NANA': 300, 'MARYAM': 660, 'ALI': 960, 'BILAL': 1260, 'ZAID': 1560}
DRAW = {'ALI': lambda st: C.ali(st), 'BILAL': lambda st: C.bilal(st), 'ZAID': lambda st: C.zaid(st), 'MARYAM': lambda st: C.maryam(st), 'NANA': lambda st: C.nana(st)}


def scene(t):
    p = part_at(t); k = p['kind']; lt = t - p['t']
    beat_i = int(t / BEAT); ph = (t % BEAT) / BEAT
    bounce = -14 * math.sin(math.pi * ph) ** 2
    clap_now = beat_i % 2 == 1 and ph < 0.35
    lay = ''; over = ''; texts = []
    order = ['NANA', 'MARYAM', 'BILAL', 'ZAID', 'ALI']
    for who in order:
        st = dict(x=POS[who], y=GROUND, s=0.95 if who == 'NANA' else 1.0, face=1 if POS[who] < 960 else -1, blink=0,
                  expr='happy', bob=bounce, talk=0, arms_front=True, foot='front', lean=3 * math.sin(math.pi * t / BEAT / 2))
        if who == 'ALI': st['face'] = 1
        singing = who in p['singers'] and p['key'] is not None
        if singing: st['talk'] = min(1, env_at(p, t) * 1.1)
        # clapping on 2 and 4 when not singing a verse
        if not singing or k == 'chorus':
            if clap_now: st.update(arm_f=38, elb_f=105, hand_f='open', arm_b=38, elb_b=105, hand_b='open')
            else: st.update(arm_f=22, elb_f=70, hand_f='open', arm_b=22, elb_b=70, hand_b='open')
        if singing and k == 'verse':            # the verse singer steps forward and sings with an open arm
            st.update(y=GROUND + 25, s=1.06, arm_f=100 + 10 * math.sin(t * 4), elb_f=20, hand_f='open', arm_b=-12)
        if k == 'chorus' and who != 'ALI' and p['key'] == 'ch1':   # "Ali hai, Ali hai!" - everyone points at Ali
            st.update(arm_f=80, elb_f=5, hand_f='point', face=1 if POS[who] < 960 else -1)
        if who == 'ALI':
            if k == 'chorus': st.update(y=GROUND + 30, s=1.08, expr='laugh' if p['key'] == 'ch2' else 'happy')
            key = p['key']
            if key == 'v1': st.update(arm_f=165, elb_f=10, arm_b=165, elb_b=10, hand_f='open', hand_b='open', expr='happy')    # stretches: good morning!
            if key == 'v2': st.update(arm_f=150 + 15 * math.sin(t * 9), elb_f=25, hand_f='wave')                                 # waves: Assalam!
            if key == 'v3': st.update(walk=(t * 1.8) % 1, arm_f=None, arm_b=None)                                                # marching to school
            if key == 'v4': st.update(expr='laugh', bob=bounce - 8 * abs(math.sin(t * 10)))
            if key == 'v5': st.update(arm_f=70, elb_f=10, hand_f='open', face=-1)                                                # sharing toys
            if key == 'v6': st.update(arm_f=150 + 15 * math.sin(t * 9), elb_f=25, hand_f='wave', face=-1)
            if key == 'v7': st.update(arm_f=140, elb_f=40, hand_f='point', expr='neutral')                                       # finger up: always the truth
            if key == 'v8': st.update(expr='laugh', y=GROUND + 30, s=1.08)
            if st.get('arm_f') is None: st.pop('arm_f', None); st.pop('arm_b', None)
        if who == 'NANA': st.update(expr='happy', face=1)
        lay += DRAW[who](st)
    # confetti during the chorus
    if k == 'chorus':
        cols = ['#e74c3c', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6']
        for i in range(36):
            x = (i * 211 + 40 * math.sin(t * 2 + i)) % W; y = ((i * 97) + (t - p['t'] + 2) * (120 + i * 3)) % 900 - 40
            over += f'<rect x="{x:.0f}" y="{y:.0f}" width="14" height="22" rx="3" fill="{cols[i % 5]}" transform="rotate({(t * 200 + i * 40) % 360:.0f},{x:.0f},{y:.0f})"/>'
    if k == 'count' or (k == 'intro' and lt < 1.0):
        a = ease((t - 0.1) / 0.5) if k == 'count' else 1 - ease(lt / 1.0)
        over += f'<rect x="560" y="120" width="800" height="300" rx="50" fill="#fff" opacity="{0.92 * a:.2f}" stroke="#4a3628" stroke-width="8" stroke-opacity="{a:.2f}"/>'
        texts += [('Pyaara Ali', 960, 230, 150, (231, 76, 60), a), ("Iqra - Let's Learn", 960, 360, 60, (47, 120, 191), a)]
    if k == 'end':
        a = ease(lt / 0.5)
        over += f'<rect x="460" y="130" width="1000" height="280" rx="50" fill="#fff" opacity="{0.92 * a:.2f}" stroke="#4a3628" stroke-width="8" stroke-opacity="{a:.2f}"/>'
        texts += [('Shukriya!', 960, 230, 130, (231, 76, 60), a), ('Subscribe: Iqra - Let\'s Learn', 960, 350, 56, (47, 120, 191), a)]
    return 'song', (0, 1.0), lay, over, texts


if os.environ.get('MOTION', '1') == '1': motion.install(sys.modules[__name__])


def lyrics(im, t):
    p = part_at(t)
    if not p['roman'] or t < p['t'] - 0.15: return
    d = ImageDraw.Draw(im, 'RGBA'); f = font(58)
    words = p['roman'].split(); frac = (t - p['t']) / max(0.3, p['d']); n_lit = int(frac * len(words) + 0.999)
    tw = d.textlength(p['roman'], font=f); bw = tw + 100; x0 = (W - bw) / 2; y0 = H - 150
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + 110], 34, fill=(255, 255, 255, 240), outline=(74, 54, 40), width=6)
    x = (W - tw) / 2
    singers = p['singers']; col = {'MARYAM': (192, 57, 107), 'BILAL': (41, 98, 168), 'ZAID': (39, 132, 74)}.get(singers[0] if len(singers) == 1 else '', (231, 76, 60))
    for i, w in enumerate(words):
        s = w + ' '
        d.text((x, y0 + 22), s, font=f, fill=col if i < n_lit else (120, 110, 100))
        x += d.textlength(s, font=f)
    if len(singers) == 1:
        nm = {'MARYAM': 'Maryam', 'BILAL': 'Bilal', 'ZAID': 'Zaid'}[singers[0]]; nf = font(34); nw = d.textlength(nm, font=nf) + 44
        d.rounded_rectangle([x0 + 30, y0 - 36, x0 + 30 + nw, y0 + 14], 20, fill=col, outline=(74, 54, 40), width=4)
        d.text((x0 + 30 + nw / 2, y0 - 11), nm, font=nf, fill='white', anchor='mm')


def frame(t):
    _, cam, lay, over, texts = motion.scene(t) if motion._M else scene(t)
    world = background().copy()
    if lay: soft.draw(world, lay, C.DEFS, W, H, cairosvg.svg2png)
    im = world.convert('RGBA')
    if over:
        o = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{over}</svg>'.encode())))
        im.alpha_composite(o)
    for s, x, y, sz, col, a in texts:
        if a <= 0.01: continue
        lay_ = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay_)
        d.text((x, y), s, font=font(sz), fill=col, anchor='mm', stroke_width=max(4, sz // 14), stroke_fill=(255, 255, 255))
        lay_.putalpha(lay_.getchannel('A').point(lambda v: int(v * a))); im.alpha_composite(lay_)
    lyrics(im, t)
    return im.convert('RGB')


def chunk(args):
    i, a, b = args; out = f'{B}/chunks/c{i:03d}.mp4'
    if os.path.exists(out): return out
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', out + '.tmp.mp4'], stdin=subprocess.PIPE)
    for k in range(a, b): p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close(); p.wait(); os.rename(out + '.tmp.mp4', out); return out


if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        ts = [float(x) for x in sys.argv[2].split(',')]; ims = [frame(t).resize((640, 360)) for t in ts]
        sheet = Image.new('RGB', (640 * 3, 360 * ((len(ims) + 2) // 3)), 'white')
        for i, im in enumerate(ims): sheet.paste(im, ((i % 3) * 640, (i // 3) * 360))
        sheet.save(sys.argv[3]); print('ok')
    elif sys.argv[1] == 'video':
        os.makedirs(f'{B}/chunks', exist_ok=True); N = int(TOTAL * FPS); step = 96
        jobs = [(i, a, min(a + step, N)) for i, a in enumerate(range(0, N, step))]
        with Pool(2) as pool: outs = pool.map(chunk, jobs)
        open(f'{B}/chunks/list.txt', 'w').write(''.join(f"file '{os.path.basename(o)}'\n" for o in outs))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{B}/chunks/list.txt', '-i', f'{B}/song.wav',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5', '-shortest', f'{B}/pyaara_ali.mp4'], check=True)
        print('done', f'{B}/pyaara_ali.mp4')
