"""Makes the Urdu voices for Nesting Stories episode 1 with Microsoft's free Urdu voices.
Double-click make_voices.bat (it runs this). Output: the voices folder and nesting_ep1_voices.zip next to this file."""
import asyncio, json, os, sys, zipfile
import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices'); os.makedirs(OUT, exist_ok=True)

# who: (voice, rate in percent, pitch in Hz)
VOICE = {
    'N':      ('ur-PK-UzmaNeural',   -2,   0),   # narrator
    'CHACHA': ('ur-PK-AsadNeural',   -4, -10),   # Rasheed Chacha
    'IMRAN':  ('ur-IN-SalmanNeural',  0,   0),   # Imran
}
# emotion: (rate percent, pitch Hz, volume percent)
EMO = {
    'neutral': (0, 0, 0), 'warm': (-4, 0, 0), 'gentle': (-8, -2, -8), 'excited': (10, 8, 10),
    'surprised': (8, 12, 10), 'happy': (4, 5, 0), 'laugh': (6, 6, 5), 'proud': (-2, 2, 0),
    'sad': (-14, -6, -12), 'worried': (-10, -3, -10), 'tired': (-14, -5, -6), 'thoughtful': (-8, 0, -4),
    'playful': (3, 5, 5),
}
LINES = json.loads(r'''[{"id": "ns1_001", "who": "N", "emo": "playful", "text": "یہ ہیں رشید چچا۔ عمر بہتّر سال۔ اور شوق؟ گھر بدلنا!"}, {"id": "ns1_002", "who": "CHACHA", "emo": "happy", "text": "یہ میرا چودہواں گھر ہے... صرف اس سال کا!"}, {"id": "ns1_003", "who": "N", "emo": "neutral", "text": "ہر دو ہفتے بعد، چچا کا سامان پھر سے ڈبوں میں بند ہو جاتا ہے۔"}, {"id": "ns1_004", "who": "CHACHA", "emo": "thoughtful", "text": "یہ گھر بھی ٹھیک نہیں۔ کھڑکی چھوٹی ہے، اور پڑوسی کا مرغا صبح پانچ بجے بولتا ہے!"}, {"id": "ns1_005", "who": "N", "emo": "playful", "text": "اور مسجد؟ چچا نے کبھی اس کا راستہ بھی نہیں دیکھا۔"}, {"id": "ns1_006", "who": "CHACHA", "emo": "playful", "text": "نماز شماز بعد میں! پہلے اچھا سا گھر تو مل جائے!"}, {"id": "ns1_007", "who": "N", "emo": "neutral", "text": "اور پھر، ایک دن، چچا کے فون پر ایک اشتہار آیا۔"}, {"id": "ns1_008", "who": "CHACHA", "emo": "excited", "text": "پورا ہال... بجلی، پانی، انٹرنیٹ سب شامل؟ بس! یہی میرا اگلا گھر ہے!"}, {"id": "ns1_009", "who": "IMRAN", "emo": "warm", "text": "ہیلو، السلام علیکم۔ میں عمران بول رہا ہوں۔"}, {"id": "ns1_010", "who": "CHACHA", "emo": "excited", "text": "ہاں ہاں، وہ ہال! میں لے رہا ہوں! ابھی آ رہا ہوں!"}, {"id": "ns1_011", "who": "IMRAN", "emo": "surprised", "text": "ارے چچا، پہلے دیکھ تو لیجیے..."}, {"id": "ns1_012", "who": "CHACHA", "emo": "excited", "text": "دیکھنا کیا ہے بیٹا؟ انٹرنیٹ ہے نا؟ بس، میں آ گیا!"}, {"id": "ns1_013", "who": "IMRAN", "emo": "laugh", "text": "ہاؤ... یہ تو بڑے جلدی میں ہیں!"}, {"id": "ns1_014", "who": "N", "emo": "warm", "text": "یہ ہیں عمران۔ حیدرآباد کے سافٹ ویئر انجینئر۔ دل کے بڑے نرم، اور ہاتھ کے بڑے کھلے۔"}, {"id": "ns1_015", "who": "CHACHA", "emo": "excited", "text": "میں آ گیا!"}, {"id": "ns1_016", "who": "IMRAN", "emo": "warm", "text": "آئیے چچا، آئیے! اندر آئیے نا۔"}, {"id": "ns1_017", "who": "N", "emo": "gentle", "text": "چچا کو دیکھ کر، عمران کو اپنے ابّا یاد آ گئے... جو اب اس دنیا میں نہیں ہیں۔"}, {"id": "ns1_018", "who": "IMRAN", "emo": "gentle", "text": "ابّا بھی ایسے ہی تھے... ہر بات میں جلدی۔"}, {"id": "ns1_019", "who": "IMRAN", "emo": "gentle", "text": "اگر میں ایک بزرگ کی خدمت کروں، تو ابّا کی روح بھی خوش ہوگی... اور اللہ بھی۔"}, {"id": "ns1_020", "who": "IMRAN", "emo": "warm", "text": "چچا، پورا ہال آپ کا۔ بجلی، پانی، انٹرنیٹ، سب شامل ہے۔"}, {"id": "ns1_021", "who": "CHACHA", "emo": "surprised", "text": "سب شامل؟ اور کرایہ کتنا؟"}, {"id": "ns1_022", "who": "IMRAN", "emo": "warm", "text": "جتنا آپ دے سکیں، چچا۔ کائیکو فکر کرتے آپ؟"}, {"id": "ns1_023", "who": "CHACHA", "emo": "happy", "text": "بیٹا، تم تو بالکل فرشتہ ہو!"}, {"id": "ns1_024", "who": "CHACHA", "emo": "playful", "text": "اچھا... وائی فائی کا پاس ورڈ کیا ہے؟"}, {"id": "ns1_025", "who": "IMRAN", "emo": "laugh", "text": "ہا ہا ہا!"}, {"id": "ns1_026", "who": "N", "emo": "playful", "text": "اور اس طرح، رشید چچا کو مل گیا اپنا پندرہواں گھر۔"}, {"id": "ns1_027", "who": "N", "emo": "surprised", "text": "لیکن کیا چچا یہاں ٹک پائیں گے؟ دیکھیے اگلے ایپیسوڈ میں... آمد!"}]''')


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
    z = os.path.join(HERE, 'nesting_ep1_voices.zip')
    with zipfile.ZipFile(z, 'w') as zf:
        for fn in sorted(os.listdir(OUT)): zf.write(os.path.join(OUT, fn), fn)
    n = len([x for x in os.listdir(OUT) if x.endswith('.mp3')])
    print(f"\nDone: {n} of {len(LINES)} voice lines. File: {z}")

asyncio.run(main())
