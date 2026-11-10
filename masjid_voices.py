"""Voices + sound effects for "Masjid ke Adaab". Writes build_masjid/timeline.json."""
import os, json, subprocess, hashlib
import numpy as np, soundfile as sf
import voices as V
import voices_ur as VU
import masjid_story as story

SR = 24000
OUT = 'build_masjid/audio'; os.makedirs(OUT, exist_ok=True)
V.OUT = 'build/audio'; os.makedirs(V.OUT, exist_ok=True)
VU.OUT = OUT
VU.VOICE.update({'BILAL': ('hm_psi', 1.30, 1.0), 'ZAID': ('hm_omega', 1.40, 1.02)})
VU.EMO['playful'] = (1.02, 1.03, 1.05)


def tts(who, dev, emo): return VU.tts(who, dev, emo)


def mixdown(parts, out, offsets, vols):
    xs = [sf.read(p)[0] for p in parts]
    n = max(int(o * SR) + len(x) for x, o in zip(xs, offsets))
    y = np.zeros(n)
    for x, o, v in zip(xs, offsets, vols):
        a = int(o * SR); y[a:a + len(x)] += x * v
    y /= max(1e-9, np.abs(y).max() / 0.9)
    sf.write(out, y, SR); return out


def sfx(name):
    f = f'{OUT}/sfx_{name}.wav'
    if os.path.exists(f): return f
    rng = np.random.default_rng(7)
    if name == 'nahin':     # all four children shout together
        p = [tts('ALI', 'नहीं!', 'excited'), tts('BILAL', 'नहीं!', 'excited'), tts('ZAID', 'नहीं!', 'excited'), tts('MARYAM', 'नहीं!', 'excited')]
        return mixdown(p, f, [0, 0.04, 0.09, 0.02], [1, 1, 1, 0.9])
    if name == 'kids_giggle':
        p = [tts('ALI', 'ही ही ही!', 'laugh'), tts('BILAL', 'ही ही!', 'laugh'), tts('ZAID', 'ही ही ही!', 'laugh')]
        out = mixdown(p, f + '.t.wav', [0, 0.15, 0.3], [0.8, 0.8, 0.8])
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-af', 'volume=0.55', f], check=True); os.remove(out); return f
    if name == 'nana_giggle':
        return tts('NANA', 'ही ही ही ही!', 'laugh')
    if name == 'crack':
        d = 1.4; x = np.zeros(int(SR * d))
        for i in range(5):
            t0 = int(SR * (0.1 + i * 0.25)); n = int(SR * 0.02)
            x[t0:t0 + n] += 0.6 * rng.normal(0, 1, n) * np.exp(-np.linspace(0, 6, n))
        sf.write(f, x, SR); return f
    if name == 'run':
        d = 1.6; x = np.zeros(int(SR * d))
        for i in range(10):
            t0 = int(SR * (0.05 + i * 0.15)); n = int(SR * 0.06)
            x[t0:t0 + n] += 0.4 * np.convolve(rng.normal(0, 1, n), np.ones(30) / 30, 'same') * np.exp(-np.linspace(0, 5, n)) * 8
        sf.write(f, x / (np.abs(x).max() + 1e-9) * 0.5, SR); return f
    return V.sfx(name)


SFX_WHO = {'nahin': 'ALL', 'kids_giggle': 'KIDS', 'nana_giggle': 'NANA'}


def build():
    t = 0.0; shots = []
    for name, beats in story.SHOTS:
        st = t; bl = []
        for b in beats:
            if b[0] == 'wait': t += b[1]; continue
            if b[0] == 'say':
                _, who, text, dev, emo = b
                f = tts(who, dev, emo); d = V.dur(f)
                bl.append({'kind': 'say', 'who': who, 'text': text, 'emo': emo, 'file': f, 't': t, 'd': d, 'env': V.envelope(f)})
                t += d + 0.25
            else:
                f = sfx(b[1]); d = V.dur(f)
                bl.append({'kind': 'sfx', 'name': b[1], 'who': SFX_WHO.get(b[1]), 'file': f, 't': t, 'd': d, 'env': V.envelope(f)})
                t += d + 0.15 if b[1] in ('nahin', 'run', 'crack', 'nana_giggle') else min(d, 1.0)
        shots.append({'name': name, 't0': st, 't1': t, 'beats': bl})
    os.makedirs('build_masjid', exist_ok=True)
    json.dump({'shots': shots, 'total': t}, open('build_masjid/timeline.json', 'w'), ensure_ascii=False)
    return shots, t


if __name__ == '__main__':
    shots, total = build()
    for s in shots: print(f"{s['name']:12s} {s['t0']:6.1f}-{s['t1']:6.1f}  {len(s['beats'])}")
    print('total', round(total, 1))
