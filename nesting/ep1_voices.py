"""Voices + sound effects + timeline for Nesting Stories episode 1.
Voice files come from make_voices.bat on the user's PC, unzipped into nesting/voices_ep1/ (ns1_001.mp3 ...).
Without them (FAKE=1, or files missing) silent placeholders with estimated lengths are used, to lay out the scenes.
Writes build_nesting1/timeline.json."""
import os, sys, json, subprocess
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
import ep1_story as story

SR = 24000
B = os.path.join(ROOT, 'build_nesting1'); A = f'{B}/audio'; os.makedirs(A, exist_ok=True)
VDIR = os.path.join(HERE, 'voices_ep1')
LINES = json.load(open(os.path.join(HERE, 'ep1_lines.json')))
ID = {(l['who'], l['emo'], l['roman']): l['id'] for l in LINES}
FPS = 24


def dur(f): return sf.info(f).duration


def envelope(f):
    x, sr = sf.read(f); x = x if x.ndim == 1 else x.mean(1)
    hop = sr // FPS; e = [float(np.sqrt(np.mean(x[i:i + hop] ** 2))) for i in range(0, len(x), hop)]
    m = max(e) if e and max(e) > 0 else 1
    return [round(min(1.0, v / m * 1.4), 3) for v in e]


def voice(who, emo, roman):
    i = ID[(who, emo, roman)]; src = f'{VDIR}/{i}.mp3'; out = f'{A}/{i}.wav'
    if os.path.exists(src) and os.environ.get('FAKE') != '1':
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', str(SR), '-af',
                            'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.06',
                            out], check=True)
        return out
    out = f'{A}/fake_{i}.wav'           # placeholder: a soft hum the length the line will roughly take
    d = 0.5 + len(roman.split()) / 2.6; n = int(SR * d); k = np.arange(n) / SR
    y = 0.05 * np.sin(2 * np.pi * 180 * k) * (0.5 + 0.5 * np.sin(2 * np.pi * 4 * k))
    sf.write(out, y, SR); return out


# ---------------------------------------------------------------- sound effects (made here, no downloads)
def _w(name, y):
    f = f'{A}/sfx_{name}.wav'; y = y / (np.abs(y).max() + 1e-9) * 0.8; sf.write(f, y, SR); return f


def sfx(name):
    f = f'{A}/sfx_{name}.wav'
    if os.path.exists(f): return f
    rng = np.random.default_rng(3)
    if name == 'tape':          # packing tape pulled off the roll: a rough rising rip
        d = 0.9; n = int(SR * d); k = np.arange(n) / SR
        noise = rng.normal(0, 1, n); grain = (np.sin(2 * np.pi * (60 + 140 * k / d) * k * 6) > 0.6).astype(float)
        y = noise * (0.4 + 0.6 * grain) * np.minimum(1, k / 0.05) * np.exp(-((k - 0.5) / 0.35) ** 2)
        return _w(name, np.convolve(y, np.ones(4) / 4, 'same'))
    if name == 'rooster':       # cartoon cock-a-doodle-doo: four nasal notes with a pitch sweep
        segs = [(0.18, 520, 600), (0.16, 640, 700), (0.2, 760, 820), (0.75, 860, 560)]
        out = []
        for L, f0, f1 in segs:
            n = int(SR * L); k = np.arange(n) / SR; fr = np.linspace(f0, f1, n) * (1 + 0.025 * np.sin(2 * np.pi * 9 * k))
            ph = 2 * np.pi * np.cumsum(fr) / SR
            tone = sum((0.9 ** h) * np.sin(h * ph) for h in range(1, 9))
            env = np.minimum(1, k / 0.02) * np.minimum(1, (L - k) / 0.05)
            out += [tone * env, np.zeros(int(SR * 0.03))]
        return _w(name, np.concatenate(out))
    if name == 'ding':          # phone notification
        n = int(SR * 0.9); k = np.arange(n) / SR
        y = (np.sin(2 * np.pi * 1318 * k) + 0.5 * np.sin(2 * np.pi * 2637 * k)) * np.exp(-k * 5)
        y2 = np.zeros(n); a = int(0.12 * SR); y2[a:] = (np.sin(2 * np.pi * 1760 * k[:n - a]) * np.exp(-k[:n - a] * 5))
        return _w(name, y + y2)
    if name == 'ring':          # phone ringing twice
        out = []
        for _ in range(2):
            n = int(SR * 0.9); k = np.arange(n) / SR
            out += [(np.sin(2 * np.pi * 440 * k) + np.sin(2 * np.pi * 480 * k)) * (np.sin(2 * np.pi * 20 * k) > 0) * 0.5, np.zeros(int(SR * 0.45))]
        return _w(name, np.concatenate(out))
    if name == 'hangup':        # click + short busy beeps
        y = np.zeros(int(SR * 1.0)); y[:200] = rng.normal(0, 1, 200) * np.exp(-np.arange(200) / 40)
        for i in range(3):
            a = int(SR * (0.25 + i * 0.25)); n = int(SR * 0.12); k = np.arange(n) / SR
            y[a:a + n] += 0.35 * np.sin(2 * np.pi * 480 * k)
        return _w(name, y)
    if name == 'knock':         # three knocks on a wooden door
        y = np.zeros(int(SR * 0.9))
        for i in range(3):
            a = int(SR * (0.05 + i * 0.22)); n = int(SR * 0.09); k = np.arange(n) / SR
            y[a:a + n] += (np.sin(2 * np.pi * 120 * k) + 0.6 * np.sin(2 * np.pi * 240 * k) + 0.3 * rng.normal(0, 1, n)) * np.exp(-k * 45)
        return _w(name, y)
    raise KeyError(name)


SFX_WHO = {}


def build():
    t = 0.0; shots = []
    for name, beats in story.SHOTS:
        st = t; bl = []
        for b in beats:
            if b[0] == 'wait': t += b[1]; continue
            if b[0] == 'say':
                _, who, emo, roman, ur = b
                f = voice(who, emo, roman); d = dur(f)
                bl.append({'kind': 'say', 'who': who, 'emo': emo, 'text': roman, 'file': f, 't': t, 'd': d, 'env': envelope(f)})
                t += d + story.GAP
            else:
                f = sfx(b[1]); d = dur(f)
                bl.append({'kind': 'sfx', 'name': b[1], 'who': SFX_WHO.get(b[1]), 'file': f, 't': t, 'd': d, 'env': envelope(f)})
                t += d + 0.08
        if name not in ('title', 'end'): t += story.SCENE_GAP   # a breath between scenes
        shots.append({'name': name, 't0': st, 't1': t, 'beats': bl})
    json.dump({'shots': shots, 'total': t}, open(f'{B}/timeline.json', 'w'), ensure_ascii=False)
    return shots, t


if __name__ == '__main__':
    shots, total = build()
    for s in shots: print(f"{s['name']:8s} {s['t0']:6.1f}-{s['t1']:6.1f}  {len(s['beats'])}")
    print('total', round(total, 1), '| real voices' if os.path.isdir(VDIR) and os.environ.get('FAKE') != '1' else '| placeholder voices')
