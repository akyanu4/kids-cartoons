"""Makes the Urdu voices for Nesting Stories episode 1 with Microsoft's free Urdu voices.
Double-click make_voices.bat (it runs this). Output: the voices folder and nesting_ep1_voices_v3.zip next to this file."""
import asyncio, json, os, sys, zipfile
import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices'); os.makedirs(OUT, exist_ok=True)

# who: (voice, rate in percent, pitch in Hz)
VOICE = {
    'N':      ('ur-PK-UzmaNeural',   +6,   0),   # narrator
    'CHACHA': ('ur-PK-AsadNeural',   +4, -10),   # Rasheed Chacha
    'IMRAN':  ('ur-IN-SalmanNeural', +6,   0),   # Imran
}
# emotion: (rate percent, pitch Hz, volume percent)
EMO = {
    'neutral': (0, 0, 0), 'warm': (-4, 0, 0), 'gentle': (-8, -2, -8), 'excited': (10, 8, 10),
    'surprised': (8, 12, 10), 'happy': (4, 5, 0), 'laugh': (6, 6, 5), 'proud': (-2, 2, 0),
    'sad': (-14, -6, -12), 'worried': (-10, -3, -10), 'tired': (-14, -5, -6), 'thoughtful': (-8, 0, -4),
    'playful': (3, 5, 5), 'naughty': (4, 8, 6), 'angry': (8, 4, 12),
}
LINES = json.loads(r'''[{"id": "ns1_52053621", "who": "N", "emo": "playful", "text": "چچا کا ایک پرانا طریقہ ہے۔ نئے گھر میں آؤ، کوئی جھگڑا کھڑا کرو، کرایہ مت دو... اور اگلے گھر چل دو!"}, {"id": "ns1_1590dbf8", "who": "CHACHA", "emo": "angry", "text": "کرایہ؟ کس بات کا کرایہ؟ نل میں گرم پانی ہی نہیں آتا! میں جا رہا ہوں!"}, {"id": "ns1_3630ad2d", "who": "CHACHA", "emo": "thoughtful", "text": "ہمممم..."}, {"id": "ns1_f5f66555", "who": "IMRAN", "emo": "surprised", "text": "چچا... آپ کی گاڑی کا بمپر؟"}, {"id": "ns1_ce98d395", "who": "CHACHA", "emo": "naughty", "text": "وہ؟ پچھلے مکان مالک کی دیوار سے دوستی ہو گئی تھی! ہی ہی!"}, {"id": "ns1_99745ae3", "who": "N", "emo": "surprised", "text": "رشید چچا کو مل گیا اپنا پندرہواں گھر۔ لیکن کیا چچا اس بار کرایہ دیں گے... یا پھر کوئی نیا جھگڑا؟ دیکھیے اگلے ایپیسوڈ میں... آمد!"}]''')


def sgn(v, unit): return ('+' if v >= 0 else '-') + str(abs(v)) + unit


async def one(l):
    f = os.path.join(OUT, l['id'] + '.mp3')
    if os.path.exists(f) and os.path.getsize(f) > 1000: return
    v, r, p = VOICE[l['who']]; er, ep, ev = EMO[l['emo']]
    for attempt in range(4):
        try:
            await edge_tts.Communicate(l['text'], v, rate=sgn(r + er, '%'), pitch=sgn(p + ep, 'Hz'), volume=sgn(ev, '%')).save(f)
            return
        except Exception as e:
            print('   retrying', l['id'], e); await asyncio.sleep(2 + attempt * 2)
    print('   FAILED', l['id'])


async def main():
    for i, l in enumerate(LINES, 1):
        print(f"[{i}/{len(LINES)}] {l['id']} {l['who']}")
        await one(l)
    z = os.path.join(HERE, 'nesting_ep1_voices_v3.zip')
    with zipfile.ZipFile(z, 'w') as zf:
        for fn in sorted(os.listdir(OUT)): zf.write(os.path.join(OUT, fn), fn)
    n = len([x for x in os.listdir(OUT) if x.endswith('.mp3')])
    print(f"\nDone: {n} of {len(LINES)} voice lines. File: {z}")

asyncio.run(main())
