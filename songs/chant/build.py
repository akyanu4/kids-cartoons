"""'Pyaara Ali' chant: the kids' Microsoft voices placed on a 110 bpm grid over claps, snaps and stomps.
Voices: songs/chant/voices/<id>.mp3 (from make_voices.bat -> pyaara_ali_song.zip). Writes build_song/{song.wav,timeline.json}."""
import os, sys, json, subprocess
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
B = os.path.join(ROOT, 'build_song'); os.makedirs(f'{B}/v', exist_ok=True)
SR = 48000; BPM = 110; BEAT = 60 / BPM; BAR = 4 * BEAT
KIDS = ['ALI', 'BILAL', 'ZAID', 'MARYAM']
LINES = {l['id']: l for l in json.load(open(f'{HERE}/lines.json'))}

# (kind, line key, singers, bars)
SONG = [('count', None, [], 1),
        ('intro', 'intro', KIDS, 2),
        ('chorus', 'ch1', KIDS, 2), ('chorus', 'ch2', KIDS, 2),
        ('verse', 'v1', ['MARYAM'], 1), ('verse', 'v2', ['MARYAM'], 1), ('verse', 'v3', ['MARYAM'], 1), ('verse', 'v4', ['MARYAM'], 1),
        ('chorus', 'ch1', KIDS, 2), ('chorus', 'ch2', KIDS, 2),
        ('verse', 'v5', ['BILAL'], 1), ('verse', 'v6', ['BILAL'], 1), ('verse', 'v7', ['ZAID'], 1), ('verse', 'v8', ['ZAID'], 1),
        ('chorus', 'ch1', KIDS, 2), ('chorus', 'ch2', KIDS, 2),
        ('outro', 'intro', KIDS, 2),
        ('end', None, [], 1)]


def load(i):
    src = f"{os.environ.get('VOICES', HERE + '/voices')}/{i}.mp3"; out = f'{B}/v/{i}.wav'
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', str(SR), '-af',
                        'silenceremove=start_periods=1:start_threshold=-42dB,areverse,silenceremove=start_periods=1:start_threshold=-42dB,areverse', out], check=True)
    x, _ = sf.read(out); return x


def fit(x, slot):
    """speed a line up (never slow it down) so it fits its slot, keeping the pitch"""
    d = len(x) / SR
    if d <= slot: return x
    tmp_in, tmp_out = f'{B}/fit_in.wav', f'{B}/fit_out.wav'
    sf.write(tmp_in, x, SR)
    r = d / slot; chain = []
    while r > 2.0: chain.append('atempo=2.0'); r /= 2
    chain.append(f'atempo={r:.4f}')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp_in, '-af', ','.join(chain), tmp_out], check=True)
    return sf.read(tmp_out)[0]


def env(x, fps=24):
    hop = SR // fps; e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) if len(x[i:i + hop]) else 0 for i in range(0, len(x), hop)])
    return (np.clip(e / (e.max() + 1e-9) * 1.4, 0, 1)).round(3).tolist()


# ---------------------------------------------------------------- percussion (body percussion only, no instruments)
rng = np.random.default_rng(5)
def clap():
    n = int(SR * 0.12); k = np.arange(n) / SR; y = np.zeros(n)
    for o in (0, 0.008, 0.017):            # a clap is a few quick bursts
        a = int(o * SR); m = n - a; y[a:] += rng.normal(0, 1, m) * np.exp(-np.arange(m) / (SR * 0.018))
    return np.convolve(y, [1, -0.85], 'same') * 0.5
def snap():
    n = int(SR * 0.05); k = np.arange(n) / SR
    return (rng.normal(0, 1, n) * 0.6 + np.sin(2 * np.pi * 2200 * k)) * np.exp(-k * 120) * 0.35
def stomp():
    n = int(SR * 0.25); k = np.arange(n) / SR
    return (np.sin(2 * np.pi * (90 - 40 * k / 0.25) * k) * np.exp(-k * 14) + 0.15 * rng.normal(0, 1, n) * np.exp(-k * 60)) * 0.9


def build():
    total = sum(s[3] for s in SONG) * BAR
    out = np.zeros(int(SR * (total + 1))); tl = []; t = 0.0
    C, S, K = clap(), snap(), stomp()
    for kind, key, singers, bars in SONG:
        dur = bars * BAR
        for b in range(int(bars * 4)):                       # the groove
            bt = t + b * BEAT; a = int(bt * SR)
            if kind in ('end',) and b > 0: break
            if b % 2 == 0: out[a:a + len(K)] += K * (0.8 if kind != 'count' else 0.6)
            else: out[a:a + len(C)] += C
            if kind in ('verse', 'chorus'):
                a2 = int((bt + BEAT / 2) * SR); out[a2:a2 + len(S)] += S * (0.6 if kind == 'verse' else 0.35)
        if key:
            start = t + (BEAT * 0.0 if bars == 1 else 0.0)
            slot = dur - BEAT * 0.35
            parts = []
            for j, w in enumerate(singers):
                i = f'song_{key}_{w}' if key in ('intro', 'ch1', 'ch2') else f'song_{key}'
                x = fit(load(i), slot)
                off = int((start + 0.012 * j) * SR); out[off:off + len(x)] += x * (1.0 if len(singers) == 1 else 0.62)
                parts.append(len(x) / SR)
            first = f'song_{key}_ALI' if key in ('intro', 'ch1', 'ch2') else f'song_{key}'
            tl.append({'kind': kind, 'key': key, 'singers': singers, 't': start, 'd': max(parts), 'slot': dur,
                       'roman': LINES[first]['roman'], 'env': env(fit(load(first), slot))})
        else:
            tl.append({'kind': kind, 'key': None, 'singers': [], 't': t, 'd': dur, 'slot': dur, 'roman': '', 'env': []})
        t += dur
    out = out[:int(SR * (t + 0.6))]
    out = out / (np.abs(out).max() + 1e-9) * 0.92
    sf.write(f'{B}/song.wav', np.stack([out, out], 1), SR)
    json.dump({'bpm': BPM, 'beat': BEAT, 'bar': BAR, 'total': t + 0.6, 'parts': tl}, open(f'{B}/timeline.json', 'w'), ensure_ascii=False)
    print('song', round(t + 0.6, 1), 's,', len(tl), 'parts')


if __name__ == '__main__':
    build()
