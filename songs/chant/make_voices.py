"""Makes the Urdu voices for the Iqra - Let's Learn cartoons with Microsoft's free Urdu voices.
Double-click make_voices.bat (it runs this). Output: the voices folder and pyaara_ali_song.zip next to this file."""
import asyncio, json, os, sys, zipfile
import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices'); os.makedirs(OUT, exist_ok=True)

# who: (voice, rate in percent, pitch in Hz)
VOICE = {
    'N':      ('ur-IN-GulNeural',   -4,   0),   # narrator
    'NANA':   ('ur-PK-AsadNeural',  -10, -8),   # Nana Jaan
    'ALI':    ('ur-PK-UzmaNeural',   +4, +22),  # Ali
    'MARYAM': ('ur-IN-GulNeural',    +6, +38),  # Maryam
    'BILAL':  ('ur-IN-SalmanNeural', +6, +50),  # Bilal
    'ZAID':   ('ur-PK-AsadNeural',   +8, +65),  # Zaid
}
# emotion: (rate percent, pitch Hz, volume percent)
EMO = {
    'neutral': (0, 0, 0), 'warm': (-4, 0, 0), 'gentle': (-8, -2, -8), 'excited': (10, 8, 10),
    'surprised': (8, 12, 10), 'happy': (4, 5, 0), 'laugh': (6, 6, 5), 'proud': (-2, 2, 0),
    'sad': (-14, -6, -12), 'worried': (-10, -3, -10), 'tired': (-14, -5, -6), 'thoughtful': (-8, 0, -4),
    'playful': (3, 5, 5),
}
LINES = json.loads(r'''[{"id": "song_intro_ALI", "who": "ALI", "emo": "excited", "text": "لا لا لا... اقرا! لیٹس لرن!"}, {"id": "song_ch1_ALI", "who": "ALI", "emo": "excited", "text": "علی ہے، علی ہے، پیارا پیارا علی!"}, {"id": "song_ch2_ALI", "who": "ALI", "emo": "excited", "text": "سب کا دوست، سب کا یار، ہمارا اپنا علی!"}, {"id": "song_intro_BILAL", "who": "BILAL", "emo": "excited", "text": "لا لا لا... اقرا! لیٹس لرن!"}, {"id": "song_ch1_BILAL", "who": "BILAL", "emo": "excited", "text": "علی ہے، علی ہے، پیارا پیارا علی!"}, {"id": "song_ch2_BILAL", "who": "BILAL", "emo": "excited", "text": "سب کا دوست، سب کا یار، ہمارا اپنا علی!"}, {"id": "song_intro_ZAID", "who": "ZAID", "emo": "excited", "text": "لا لا لا... اقرا! لیٹس لرن!"}, {"id": "song_ch1_ZAID", "who": "ZAID", "emo": "excited", "text": "علی ہے، علی ہے، پیارا پیارا علی!"}, {"id": "song_ch2_ZAID", "who": "ZAID", "emo": "excited", "text": "سب کا دوست، سب کا یار، ہمارا اپنا علی!"}, {"id": "song_intro_MARYAM", "who": "MARYAM", "emo": "excited", "text": "لا لا لا... اقرا! لیٹس لرن!"}, {"id": "song_ch1_MARYAM", "who": "MARYAM", "emo": "excited", "text": "علی ہے، علی ہے، پیارا پیارا علی!"}, {"id": "song_ch2_MARYAM", "who": "MARYAM", "emo": "excited", "text": "سب کا دوست، سب کا یار، ہمارا اپنا علی!"}, {"id": "song_v1", "who": "MARYAM", "emo": "excited", "text": "صبح اٹھے، بسم اللہ بولے"}, {"id": "song_v2", "who": "MARYAM", "emo": "excited", "text": "سب کو کہتا السلام!"}, {"id": "song_v3", "who": "MARYAM", "emo": "excited", "text": "بستہ اٹھائے، اسکول کو جائے"}, {"id": "song_v4", "who": "MARYAM", "emo": "excited", "text": "ہنستے ہنستے کرتا کام!"}, {"id": "song_v5", "who": "BILAL", "emo": "excited", "text": "کھیل کھلونے بانٹ کے کھیلے"}, {"id": "song_v6", "who": "BILAL", "emo": "excited", "text": "دوست بنائے ڈھیر سارے"}, {"id": "song_v7", "who": "ZAID", "emo": "excited", "text": "جھوٹ نہ بولے، سچ ہی بولے"}, {"id": "song_v8", "who": "ZAID", "emo": "excited", "text": "سب کہتے، واہ علی پیارے!"}]''')


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
    z = os.path.join(HERE, 'pyaara_ali_song.zip')
    with zipfile.ZipFile(z, 'w') as zf:
        for fn in sorted(os.listdir(OUT)): zf.write(os.path.join(OUT, fn), fn)
    n = len([x for x in os.listdir(OUT) if x.endswith('.mp3')])
    print(f"\nDone: {n} of {len(LINES)} voice lines. File: {z}")

asyncio.run(main())
