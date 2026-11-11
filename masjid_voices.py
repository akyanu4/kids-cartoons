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


# Microsoft Urdu voices (made on the user's PC by voicekit/make_voices.bat, unzipped into voices_ms/).
# Set VOICES=kokoro to go back to the old offline voices.
USE_MS = os.environ.get('VOICES', 'ms') == 'ms' and os.path.isdir('voices_ms')
MS = {(l['ep'], l['who'], l['key'], l['emo']): l['id'] for l in json.load(open('voicekit/lines.json'))}


def ms_wav(i):
    """mp3 -> mono 24 kHz wav with the silence at both ends cut off (a short tail kept)"""
    out = f'{OUT}/ms_{i}.wav'
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'voices_ms/{i}.mp3', '-ac', '1', '-ar', str(SR), '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.06',
                        out], check=True)
    return out


def tts(who, dev, emo, text=None, ep='ep2'):
    if USE_MS and text is not None and (ep, who, text, emo) in MS: return ms_wav(MS[(ep, who, text, emo)])
    return VU.tts(who, dev, emo)


def kid_sfx(who, key, dev, emo):
    if USE_MS and ('sfx', who, key, emo) in MS: return ms_wav(MS[('sfx', who, key, emo)])
    return VU.tts(who, dev, emo)


def mixdown(parts, out, offsets, vols):
    xs = [sf.read(p)[0] for p in parts]
    n = max(int(o * SR) + len(x) for x, o in zip(xs, offsets))
    y = np.zeros(n)
    for x, o, v in zip(xs, offsets, vols):
        a = int(o * SR); y[a:a + len(x)] += x * v
    y /= max(1e-9, np.abs(y).max() / 0.9)
    sf.write(out, y, SR); return out


def _syll(who, txt):
    """one short laugh syllable from this character's voice, silence trimmed"""
    x, sr = sf.read(kid_sfx(who, 'giggle', txt, 'laugh'))
    if USE_MS:   # keep only the first 'hee' of the recorded giggle
        e = np.convolve(np.abs(x), np.ones(240) / 240, 'same'); on = e > 0.1 * e.max()
        a = int(np.argmax(on)); b = a + int(np.argmax(~on[a:])) if (~on[a:]).any() else len(x)
        x = x[a:max(b, a + int(0.08 * SR))]
    x = x if x.ndim == 1 else x.mean(1)
    on = np.where(np.abs(x) > 0.04 * np.abs(x).max())[0]
    x = x[on[0]:on[-1]] if len(on) else x
    return x / (np.abs(x).max() + 1e-9)


def _burst(x, pitch, length):
    n = int(len(x) / pitch); y = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)[:int(length * SR)]
    k = len(y); env = np.minimum(1, np.arange(k) / (0.012 * SR)) * np.exp(-np.linspace(0, 5.0, k))
    return y * env


def giggle(who, seed, n=6, pitch=1.0, gap=0.145, syl='ही'):
    """a natural giggle: quick uneven bursts, pitch going up then down, getting softer, a little breath in at the end"""
    rng = np.random.default_rng(seed)
    x = _syll(who, syl); out = np.zeros(int(SR * (n * gap * 1.4 + 0.8))); t = 0.02
    for i in range(n):
        shape = 1.06 + 0.06 * np.sin(i / max(1, n - 1) * np.pi) - 0.03 * i / n
        b = _burst(x, pitch * shape * rng.uniform(0.97, 1.03), rng.uniform(0.09, 0.13))
        a = int(t * SR); amp = (1 - 0.5 * i / n) * rng.uniform(0.85, 1.0)
        out[a:a + len(b)] += amp * b
        br = rng.normal(0, 1, int(0.05 * SR)); br = np.convolve(br, np.ones(25) / 25, 'same') * 0.012 * amp   # breath between bursts
        out[a + len(b):a + len(b) + len(br)] += br[:max(0, len(out) - a - len(b))]
        t += gap * rng.uniform(0.85, 1.15) * (1 + 0.06 * i)
    inh = rng.normal(0, 1, int(0.32 * SR)); inh = np.convolve(inh, np.ones(18) / 18, 'same') * np.linspace(0, 0.03, len(inh))
    a = int((t + 0.05) * SR); out[a:a + len(inh)] += inh[:max(0, len(out) - a)]
    out = out[:a + len(inh) + int(0.05 * SR)]
    return out / (np.abs(out).max() + 1e-9) * 0.9


def sfx(name):
    f = f'{OUT}/sfx_{name}.wav'
    if os.path.exists(f): return f
    rng = np.random.default_rng(7)
    if name == 'nahin':     # all four children shout together
        p = [kid_sfx(w, 'nahin', 'नहीं!', 'excited') for w in ('ALI', 'BILAL', 'ZAID', 'MARYAM')]
        return mixdown(p, f, [0, 0.04, 0.09, 0.02], [1, 1, 1, 0.9])
    if name == 'kids_giggle':
        parts = [(giggle('ALI', 1, 6, 1.0), 0.0, 0.9), (giggle('BILAL', 2, 5, 1.0, 0.16), 0.12, 0.8), (giggle('ZAID', 3, 7, 1.02, 0.13), 0.22, 0.75)]
        n = max(int(o * SR) + len(x) for x, o, _ in parts); y = np.zeros(n)
        for x, o, v in parts: a = int(o * SR); y[a:a + len(x)] += x * v
        sf.write(f, y / (np.abs(y).max() + 1e-9) * 0.55, SR); return f
    if name == 'nana_giggle':
        y = giggle('NANA', 4, 5, 1.0, 0.2, 'हा')
        sf.write(f, y * 0.9, SR); return f
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
                f = tts(who, dev, emo, text); d = V.dur(f)
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
