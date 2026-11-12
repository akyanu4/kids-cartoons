"""Makes the Urdu voices for Nesting Stories episode 1 with Microsoft's free Urdu voices.
Double-click make_voices.bat (it runs this). Output: the voices folder and nesting_ep1_voices_v2.zip next to this file."""
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
    'playful': (3, 5, 5), 'naughty': (4, 8, 6),
}
LINES = json.loads(r'''[{"id": "ns1b_001", "who": "N", "emo": "playful", "text": "یہ ہیں رشید چچا۔ عمر بہتّر سال۔ شوق؟ گھر بدلنا... اور ہر گھر میں تھوڑی سی شرارت!"}, {"id": "ns1b_002", "who": "CHACHA", "emo": "naughty", "text": "یہ میرا چودہواں گھر ہے... صرف اس سال کا! ہی ہی!"}, {"id": "ns1b_003", "who": "CHACHA", "emo": "thoughtful", "text": "یہ گھر بھی ٹھیک نہیں۔ پڑوسی کا مرغا صبح پانچ بجے بولتا ہے!"}, {"id": "ns1b_004", "who": "N", "emo": "playful", "text": "اور مسجد؟ چچا نے کبھی اس کا راستہ بھی نہیں دیکھا۔"}, {"id": "ns1b_005", "who": "CHACHA", "emo": "naughty", "text": "نماز شماز بعد میں! پہلے اچھا سا گھر تو مل جائے!"}, {"id": "ns1b_006", "who": "N", "emo": "neutral", "text": "پھر ایک دن، چچا کے فون پر ایک اشتہار آیا۔"}, {"id": "ns1b_007", "who": "CHACHA", "emo": "excited", "text": "پورا ہال، تین مہینے کے لیے... بجلی، پانی، انٹرنیٹ سب شامل؟ بس! یہی میرا اگلا گھر ہے!"}, {"id": "ns1b_008", "who": "IMRAN", "emo": "warm", "text": "ہیلو، السلام علیکم۔ میں عمران بول رہا ہوں۔"}, {"id": "ns1b_009", "who": "CHACHA", "emo": "excited", "text": "ہاں ہاں، وہ ہال! میں لے رہا ہوں! کہاں ملیں؟"}, {"id": "ns1b_010", "who": "IMRAN", "emo": "surprised", "text": "ارے چچا... گھر کے سامنے فٹ پاتھ پر آ جائیے، میں وہیں ہوں۔"}, {"id": "ns1b_011", "who": "CHACHA", "emo": "excited", "text": "ابھی آیا!"}, {"id": "ns1b_012", "who": "IMRAN", "emo": "laugh", "text": "ہاؤ... یہ تو بڑے جلدی میں ہیں!"}, {"id": "ns1b_013", "who": "N", "emo": "warm", "text": "یہ ہیں عمران۔ حیدرآباد کے سافٹ ویئر انجینئر، دل کے بڑے نرم۔ ان کی فیملی کچھ مہینوں کے لیے انڈیا گئی ہوئی ہے۔"}, {"id": "ns1b_014", "who": "IMRAN", "emo": "warm", "text": "السلام علیکم، چچا! آئیے، آئیے۔"}, {"id": "ns1b_015", "who": "CHACHA", "emo": "naughty", "text": "وعلیکم السلام، بیٹا۔ پہلے ایک بات بتا دو۔ میں ہر اتوار پائے کا سوپ بناتا ہوں۔ پورے گھر میں خوشبو آئے گی۔ کوئی پرابلم تو نہیں ہوگی؟"}, {"id": "ns1b_016", "who": "IMRAN", "emo": "laugh", "text": "پرابلم؟ چچا، میں حیدرآبادی ہوں۔ پائے تو ہماری جان ہیں!"}, {"id": "ns1b_017", "who": "CHACHA", "emo": "naughty", "text": "پھر تو تمہیں بھی ملے گا... اگر کرایہ تھوڑا کم ہو جائے! ہی ہی!"}, {"id": "ns1b_018", "who": "CHACHA", "emo": "proud", "text": "اور سنو! میں بھی جوانی میں کمپیوٹر پر کام کرتا تھا۔ اتنا ڈیٹا ڈالا، اتنا ڈیٹا... کہ کمپیوٹر خود تھک گیا!"}, {"id": "ns1b_019", "who": "IMRAN", "emo": "surprised", "text": "واہ چچا! کون سا کمپیوٹر تھا؟"}, {"id": "ns1b_020", "who": "CHACHA", "emo": "naughty", "text": "بڑا والا! پورے کمرے جتنا! آج کل کے تمہارے لیپ ٹاپ تو بچے ہیں!"}, {"id": "ns1b_021", "who": "IMRAN", "emo": "warm", "text": "آئیے چچا، گھر دکھاتا ہوں۔ یہ پورا ہال آپ کا۔ بجلی، پانی، انٹرنیٹ، سب شامل۔"}, {"id": "ns1b_022", "who": "CHACHA", "emo": "naughty", "text": "ہمم... جہاں میں ابھی رہتا ہوں، وہاں کے انجینئر نے تو مجھے الگ کمرہ اور کلوزٹ بھی دیا ہے!"}, {"id": "ns1b_023", "who": "IMRAN", "emo": "warm", "text": "فکر مت کیجیے، کلوزٹ یہاں بھی ہے۔ بس ایک بات... یہ گھر صرف تین مہینے کے لیے ہے۔ میری فیملی انڈیا گئی ہوئی ہے۔"}, {"id": "ns1b_024", "who": "CHACHA", "emo": "naughty", "text": "تین مہینے؟ ارے، میرے لیے تو یہ لمبی مدت ہے! ہی ہی!"}, {"id": "ns1b_025", "who": "N", "emo": "gentle", "text": "چچا کو دیکھ کر، عمران کو اپنے ابّا یاد آ گئے... جو اب اس دنیا میں نہیں ہیں۔"}, {"id": "ns1b_026", "who": "IMRAN", "emo": "gentle", "text": "ابّا بھی ایسے ہی تھے... ہر بات میں جلدی۔ اگر میں ان کی خدمت کروں، تو ابّا کی روح بھی خوش ہوگی... اور اللہ بھی۔"}, {"id": "ns1b_027", "who": "CHACHA", "emo": "naughty", "text": "تو بیٹا... کرایہ کتنا؟"}, {"id": "ns1b_028", "who": "IMRAN", "emo": "warm", "text": "جتنا آپ دے سکیں، چچا۔ کائیکو فکر کرتے آپ؟"}, {"id": "ns1b_029", "who": "CHACHA", "emo": "happy", "text": "بیٹا، تم تو بالکل فرشتہ ہو!"}, {"id": "ns1b_030", "who": "CHACHA", "emo": "naughty", "text": "اچھا... وائی فائی کا پاس ورڈ کیا ہے؟"}, {"id": "ns1b_031", "who": "IMRAN", "emo": "laugh", "text": "ہا ہا ہا!"}, {"id": "ns1b_032", "who": "N", "emo": "surprised", "text": "رشید چچا کو مل گیا اپنا پندرہواں گھر۔ لیکن کیا وہ یہاں تین مہینے ٹک پائیں گے؟ دیکھیے اگلے ایپیسوڈ میں... آمد!"}]''')


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
    z = os.path.join(HERE, 'nesting_ep1_voices_v2.zip')
    with zipfile.ZipFile(z, 'w') as zf:
        for fn in sorted(os.listdir(OUT)): zf.write(os.path.join(OUT, fn), fn)
    n = len([x for x in os.listdir(OUT) if x.endswith('.mp3')])
    print(f"\nDone: {n} of {len(LINES)} voice lines. File: {z}")

asyncio.run(main())
