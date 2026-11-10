"""Voices for the 3D test clip. Writes build_3d/lines.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import voices as V, voices_ur as VU
VU.OUT = 'build_3d/audio'; os.makedirs(VU.OUT, exist_ok=True)
LINES = [
    ('ALI', 'Assalamu alaikum, Nana Jaan!', 'अस्सलामु अलैकुम, नाना जान!', 'happy'),
    ('NANA', 'Wa alaikum assalam, beta! Aao, saath mein namaz padhein.', 'व अलैकुम अस्सलाम, बेटा! आओ, साथ में नमाज़ पढ़ें।', 'warm'),
    ('NANA', 'Allahu Akbar.', 'अल्लाहु अकबर।', 'warm'),
]
out = []
for who, ro, dev, emo in LINES:
    f = VU.tts(who, dev, emo)
    out.append(dict(who=who, text=ro, file=f, d=V.dur(f), env=V.envelope(f, 24)))
json.dump(out, open('build_3d/lines.json', 'w'))
for o in out: print(o['who'], round(o['d'], 2))
