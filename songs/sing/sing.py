"""Make the kids' Microsoft voices *sing*: each syllable is moved onto the beat and tuned to a melody note
(WORLD vocoder: keep the voice, replace its pitch and timing), over an upbeat backing track made here.
python3 songs/sing/sing.py test   -> build_sing/chorus_test.wav (chorus only)"""
import os, sys, json, subprocess
import numpy as np, soundfile as sf, pyworld as pw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
VO = os.path.join(ROOT, 'songs/chant/voices'); B = os.path.join(ROOT, 'build_sing'); os.makedirs(B, exist_ok=True)
SR = 48000; BPM = 116; BEAT = 60 / BPM; E8 = BEAT / 2
NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}
def hz(n): return NOTE[n[:-1]] * 2 ** (int(n[-1]) - 4)

# melody per line: (note, length in eighths) - one entry per syllable
MEL = {
    'ch1': [('G4', 1), ('G4', 1), ('E4', 2), ('G4', 1), ('G4', 1), ('E4', 2), ('A4', 1), ('A4', 1), ('G4', 1), ('G4', 1), ('E4', 1), ('C5', 3)],   # A-li hai, A-li hai, pyaa-ra pyaa-ra A-li!
    'ch2': [('E4', 1), ('E4', 1), ('G4', 2), ('E4', 1), ('E4', 1), ('G4', 2), ('A4', 1), ('A4', 1), ('G4', 1), ('E4', 1), ('D4', 1), ('E4', 1), ('C4', 3)],  # Sab ka dost, sab ka yaar, ha-maa-ra ap-na A-li!
}


def load(i):
    x, sr = sf.read(f'{VO}/{i}.mp3') if os.path.exists(f'{VO}/{i}.mp3') else (None, None)
    if x is None: raise FileNotFoundError(i)
    x = x if x.ndim == 1 else x.mean(1)
    on = np.where(np.abs(x) > 0.03 * np.abs(x).max())[0]; x = x[on[0]:on[-1]]
    if sr != SR:
        n = int(len(x) * SR / sr); x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)
    return x.astype(np.float64)


def nuclei(x, want):
    """times (s) of the syllable centres: loudness peaks, picked to match the number of notes"""
    hop = int(0.01 * SR); e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    e = np.convolve(e, np.ones(5) / 5, 'same')
    pk = [i for i in range(2, len(e) - 2) if e[i] >= e[i - 1] and e[i] >= e[i + 1] and e[i] > 0.18 * e.max()]
    sel = []                                            # keep peaks at least 90 ms apart, strongest first
    for i in sorted(pk, key=lambda i: -e[i]):
        if all(abs(i - j) > 9 for j in sel): sel.append(i)
    sel = sorted(sel)
    if len(sel) != want:                                # fall back to even spacing over the voiced span
        sel = list(np.linspace(sel[0] if sel else 0, sel[-1] if sel else len(e) - 1, want))
    return np.array(sel) * 0.01


def sing(x, mel, start_pad=0.0):
    """retime syllables onto the note grid and tune them to the notes"""
    fp = 5.0
    f0, t = pw.harvest(x, SR, frame_period=fp); sp = pw.cheaptrick(x, f0, t, SR); ap = pw.d4c(x, f0, t, SR)
    n = len(mel); nuc = nuclei(x, n)
    onsets = np.cumsum([0] + [l * E8 for _, l in mel[:-1]])
    tgt = onsets + 0.06                                  # syllable centre lands just after the beat
    total = onsets[-1] + mel[-1][1] * E8
    # time map new->old: anchors at the syllable centres, plus the two ends
    new_a = np.concatenate([[0], tgt, [total]]); old_a = np.concatenate([[0], nuc, [len(x) / SR]])
    new_a, idx = np.unique(new_a, return_index=True); old_a = old_a[idx]
    T = np.arange(0, total, fp / 1000); old_t = np.interp(T, new_a, old_a)
    fi = np.clip(old_t / (fp / 1000), 0, len(f0) - 1)
    i0 = np.floor(fi).astype(int); i1 = np.minimum(i0 + 1, len(f0) - 1); w = (fi - i0)[:, None]
    sp2 = sp[i0] * (1 - w) + sp[i1] * w; ap2 = ap[i0] * (1 - w) + ap[i1] * w
    voiced = (f0[i0] > 0) | (f0[i1] > 0)
    # melody pitch curve with a short glide and vibrato on long notes
    p = np.zeros(len(T))
    for k, (nt, l) in enumerate(mel):
        a = onsets[k]; b = a + l * E8; m = (T >= a) & (T < b); f = hz(nt)
        vib = 1 + (0.012 * np.sin(2 * np.pi * 5.5 * (T[m] - a)) * np.clip((T[m] - a - 0.18) / 0.15, 0, 1) if l >= 2 else 0)
        p[m] = f * vib
    p = np.convolve(p, np.ones(7) / 7, 'same')                       # ~35 ms glides between notes
    f0n = np.where(voiced, p, 0.0)
    y = pw.synthesize(f0n, np.ascontiguousarray(sp2), np.ascontiguousarray(ap2), SR, fp)
    return y / (np.abs(y).max() + 1e-9)


# ---------------------------------------------------------------- backing track (all made here)
rng = np.random.default_rng(2)
def tone(f, d, kind='pluck', vol=1.0):
    n = int(SR * d); k = np.arange(n) / SR
    if kind == 'pluck':   y = (np.sin(2 * np.pi * f * k) + 0.4 * np.sin(4 * np.pi * f * k) + 0.15 * np.sin(6 * np.pi * f * k)) * np.exp(-k * 6)
    elif kind == 'bass':  y = (np.sin(2 * np.pi * f * k) + 0.3 * np.sin(4 * np.pi * f * k)) * np.exp(-k * 3.5)
    elif kind == 'pad':   y = sum(np.sin(2 * np.pi * f * (1 + dt) * k) for dt in (-0.004, 0, 0.004)) / 3 * np.minimum(1, k / 0.08) * np.exp(-k * 0.8)
    return y * vol * np.minimum(1, (d - k) / 0.03 + 0.001).clip(0, 1)
def kick():
    n = int(SR * 0.3); k = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(60 + 90 * np.exp(-k * 30)) / SR) * np.exp(-k * 9)
def snare():
    n = int(SR * 0.2); k = np.arange(n) / SR
    return (rng.normal(0, 1, n) * 0.7 + 0.5 * np.sin(2 * np.pi * 190 * k)) * np.exp(-k * 22) * 0.6
def hat():
    n = int(SR * 0.05); return rng.normal(0, 1, n) * np.exp(-np.arange(n) / (SR * 0.008)) * 0.18

CHORDS = {'C': ['C4', 'E4', 'G4'], 'G': ['B3', 'D4', 'G4'], 'Am': ['A3', 'C4', 'E4'], 'F': ['A3', 'C4', 'F4']}
def backing(bars, prog, mel_lines=()):
    n = int(SR * bars * 4 * BEAT + SR); y = np.zeros(n)
    K, Sn, Hh = kick(), snare(), hat()
    for b in range(bars):
        ch = prog[b % len(prog)]; root = CHORDS[ch][0]
        for q in range(8):                                   # eighths
            t = (b * 8 + q) * E8; a = int(t * SR)
            if q in (0, 3, 4): y[a:a + len(K)] += K * 0.9
            if q in (2, 6): y[a:a + len(Sn)] += Sn
            y[a:a + len(Hh)] += Hh * (1.0 if q % 2 else 0.6)
            bn = hz(root[:-1] + '2'); bs = tone(bn * (1.5 if q in (3, 7) else 1), E8 * 0.9, 'bass', 0.5)
            y[a:a + len(bs)] += bs
            if q % 2 == 1:                                    # off-beat ukulele-ish chord stabs
                for nt in CHORDS[ch]:
                    s = tone(hz(nt), E8 * 0.8, 'pluck', 0.16); y[a:a + len(s)] += s
        pd = sum(tone(hz(nt), 4 * BEAT, 'pad', 0.08) for nt in CHORDS[ch]); a = int(b * 4 * BEAT * SR); y[a:a + len(pd)] += pd
    return y


def test():
    kids = ['ALI', 'BILAL', 'ZAID', 'MARYAM']
    bars = 4; music = backing(bars + 1, ['C', 'G', 'Am', 'F'])
    out = music * 0.55
    for li, key in enumerate(['ch1', 'ch2']):
        line_start = 2 * BAR * li + BAR * 0 + 0.0 if False else li * 8 * E8 * 2  # each line = 2 bars
        for j, w in enumerate(kids):
            v = sing(load(f'song_{key}_{w}'), MEL[key])
            v = np.convolve(v, [0.6, 0.3, 0.1], 'same')     # soften a little
            a = int((line_start + 0.01 * j) * SR); out[a:a + len(v)] += v * 0.32
    # light room echo so the choir blends
    d = int(0.09 * SR); out[d:] += out[:-d] * 0.18
    out = out / (np.abs(out).max() + 1e-9) * 0.92
    sf.write(f'{B}/chorus_test.wav', np.stack([out, out], 1), SR)
    print('ok', f'{B}/chorus_test.wav', round(len(out) / SR, 1))


BAR = 4 * BEAT
if __name__ == '__main__':
    if sys.argv[1] == 'test': test()
