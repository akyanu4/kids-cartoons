"""Makes the Urdu voices for the Iqra - Let's Learn cartoons with Microsoft's free Urdu voices.
Double-click make_voices.bat (it runs this). Output: the voices folder and iqra_voices.zip next to this file."""
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
LINES = json.loads(r'''[{"id": "ep1_001", "who": "N", "emo": "warm", "text": "علی اور پیاسی بلی"}, {"id": "ep1_002", "who": "N", "emo": "neutral", "text": "گرمیوں کا ایک بہت گرم دن تھا۔ سورج خوب چمک رہا تھا، اور سب سائے کی تلاش میں تھے۔"}, {"id": "ep1_003", "who": "N", "emo": "neutral", "text": "علی اور اس کی چھوٹی بہن مریم اسکول سے گھر جا رہے تھے۔"}, {"id": "ep1_004", "who": "ALI", "emo": "tired", "text": "اُف! آج تو بہت گرمی ہے، مریم!"}, {"id": "ep1_005", "who": "MARYAM", "emo": "excited", "text": "میں تو گھر جا کر لیموں کا ٹھنڈا ٹھنڈا شربت پیوں گی!"}, {"id": "ep1_006", "who": "MARYAM", "emo": "surprised", "text": "علی، دیکھو! درخت کے نیچے ایک ننھی سی بلی!"}, {"id": "ep1_007", "who": "ALI", "emo": "sad", "text": "یہ تو بہت تھکی ہوئی لگ رہی ہے۔ شاید اسے بہت پیاس لگی ہے۔ بیچاری بلی!"}, {"id": "ep1_008", "who": "ALI", "emo": "worried", "text": "لیکن... میری بوتل میں تو بس آخری تھوڑا سا پانی ہے۔"}, {"id": "ep1_009", "who": "N", "emo": "thoughtful", "text": "علی کو بھی پیاس لگی تھی۔ پھر اسے یاد آیا کہ نانا ہمیشہ کیا کہتے ہیں۔"}, {"id": "ep1_010", "who": "NANA", "emo": "warm", "text": "سب کے ساتھ مہربانی کرو، جانوروں کے ساتھ بھی۔ اللہ مہربان ہے، اور وہ مہربانی کو پسند کرتا ہے۔"}, {"id": "ep1_011", "who": "ALI", "emo": "gentle", "text": "یہ لو ننھی بلی، پانی پی لو!"}, {"id": "ep1_012", "who": "N", "emo": "warm", "text": "ننھی بلی پانی پیتی رہی، پیتی رہی، یہاں تک کہ اس کی پیاس بجھ گئی۔"}, {"id": "ep1_013", "who": "MARYAM", "emo": "laugh", "text": "ہی ہی! یہ شکریہ کہہ رہی ہے، علی!"}, {"id": "ep1_014", "who": "N", "emo": "excited", "text": "اور پتا ہے کیا ہوا؟ ننھی بلی ان کے ساتھ ساتھ چل پڑی!"}, {"id": "ep1_015", "who": "ALI", "emo": "surprised", "text": "ارے! تم کہاں چلیں، بلی؟"}, {"id": "ep1_016", "who": "NANA", "emo": "warm", "text": "السلام علیکم، میرے بچو! اور یہ ننھا مہمان کون ہے؟"}, {"id": "ep1_017", "who": "ALI", "emo": "happy", "text": "وعلیکم السلام، نانا! اسے بہت پیاس لگی تھی، تو میں نے اسے اپنا پانی دے دیا۔"}, {"id": "ep1_018", "who": "NANA", "emo": "proud", "text": "ماشاءاللہ، علی! مجھے تم پر فخر ہے۔ ہمارے پیارے نبی ﷺ نے سکھایا کہ ہر جاندار پر مہربانی کرنے کا اجر ہے۔"}, {"id": "ep1_019", "who": "MARYAM", "emo": "excited", "text": "نانا، کیا ہم اسے رکھ لیں؟ اس کا نام لیمو رکھتے ہیں!"}, {"id": "ep1_020", "who": "NANA", "emo": "laugh", "text": "ہا ہا ہا! ٹھیک ہے، لیمو ہی سہی!"}, {"id": "ep1_021", "who": "N", "emo": "warm", "text": "ہر جاندار کے ساتھ مہربانی کرو۔ اللہ مہربان ہے، اور وہ مہربانی کو پسند کرتا ہے۔"}, {"id": "ep2_001", "who": "N", "emo": "warm", "text": "مسجد کے آداب"}, {"id": "ep2_002", "who": "N", "emo": "neutral", "text": "جمعہ کا دن تھا۔ مسجد میں جماعت کھڑی تھی۔"}, {"id": "ep2_003", "who": "N", "emo": "neutral", "text": "لیکن بلال کا دھیان نماز میں نہیں تھا۔ اس نے علی کو ہلکا سا دھکا دیا!"}, {"id": "ep2_004", "who": "N", "emo": "excited", "text": "علی نے بھی دھکا دیا، اور زید بھی کھی کھی کر کے ہنسنے لگا!"}, {"id": "ep2_005", "who": "N", "emo": "warm", "text": "نماز کے بعد، نانا جان مسکراتے ہوئے بچوں کے پاس آئے۔"}, {"id": "ep2_006", "who": "NANA", "emo": "warm", "text": "السلام علیکم، بچو! آؤ، ایک کھیل کھیلتے ہیں!"}, {"id": "ep2_007", "who": "BILAL", "emo": "excited", "text": "کھیل؟ واہ! کون سا کھیل، نانا جان؟"}, {"id": "ep2_008", "who": "NANA", "emo": "playful", "text": "میں دکھاتا ہوں کہ کچھ بچے نماز میں کیا کرتے ہیں۔ تم بتانا، صحیح ہے یا نہیں!"}, {"id": "ep2_009", "who": "NANA", "emo": "playful", "text": "دیکھو! میں اپنے ساتھ والے کو دھکا دیتا ہوں... دھکا!"}, {"id": "ep2_010", "who": "NANA", "emo": "playful", "text": "کیا یہ صحیح طریقہ ہے؟"}, {"id": "ep2_011", "who": "NANA", "emo": "playful", "text": "اب میں نماز میں کھی کھی کر کے ہنستا ہوں!"}, {"id": "ep2_012", "who": "NANA", "emo": "playful", "text": "اب میں اِدھر اُدھر دیکھتا ہوں... اور بڑی سی جمائی لیتا ہوں۔ آآآہ!"}, {"id": "ep2_013", "who": "NANA", "emo": "playful", "text": "اب میں سر کھجاتا ہوں، کپڑے کھینچتا ہوں، اور انگلیاں چٹخاتا ہوں!"}, {"id": "ep2_014", "who": "NANA", "emo": "playful", "text": "اور اب میں نماز پڑھنے والوں کے سامنے سے بھاگتا ہوں!"}, {"id": "ep2_015", "who": "MARYAM", "emo": "laugh", "text": "نانا جان، آپ تو بالکل بلال جیسے لگ رہے تھے!"}, {"id": "ep2_016", "who": "BILAL", "emo": "sad", "text": "جی، نانا جان... اب ہم ایسا نہیں کریں گے۔"}, {"id": "ep2_017", "who": "NANA", "emo": "warm", "text": "شاباش! اب دیکھو، نماز کا صحیح طریقہ۔"}, {"id": "ep2_018", "who": "NANA", "emo": "warm", "text": "صف سیدھی رکھو۔ کندھے سے کندھا، پاؤں سے پاؤں ملاؤ۔"}, {"id": "ep2_019", "who": "NANA", "emo": "warm", "text": "نظر سجدے کی جگہ پر رکھو۔"}, {"id": "ep2_020", "who": "NANA", "emo": "warm", "text": "اللہ اکبر کہو، اور ہاتھ کانوں تک اٹھاؤ۔"}, {"id": "ep2_021", "who": "NANA", "emo": "warm", "text": "ہاتھ باندھ کر، سکون سے کھڑے رہو۔"}, {"id": "ep2_022", "who": "NANA", "emo": "warm", "text": "رکوع میں جھکو، اور ہاتھ گھٹنوں پر رکھو۔"}, {"id": "ep2_023", "who": "NANA", "emo": "warm", "text": "سجدے میں ماتھا اور ناک زمین پر لگاؤ۔"}, {"id": "ep2_024", "who": "NANA", "emo": "warm", "text": "پھر آرام سے بیٹھو۔ نہ ہلنا، نہ ہنسنا۔"}, {"id": "ep2_025", "who": "ZAID", "emo": "excited", "text": "یہ تو بہت آسان ہے!"}, {"id": "ep2_026", "who": "ALI", "emo": "happy", "text": "اب ہم ہمیشہ ایسے ہی نماز پڑھیں گے، نانا جان!"}, {"id": "ep2_027", "who": "N", "emo": "warm", "text": "اگلی جماعت میں، تینوں بچے بالکل سیدھے اور سکون سے کھڑے تھے۔"}, {"id": "ep2_028", "who": "NANA", "emo": "proud", "text": "ماشاءاللہ! مجھے تم تینوں پر فخر ہے۔"}, {"id": "ep2_029", "who": "N", "emo": "warm", "text": "مسجد اللہ کا گھر ہے۔ وہاں سکون اور ادب سے رہو۔"}, {"id": "sfx_001", "who": "ALI", "emo": "excited", "text": "نہیں!"}, {"id": "sfx_002", "who": "ALI", "emo": "laugh", "text": "ہی ہی ہی ہی ہی!"}, {"id": "sfx_003", "who": "BILAL", "emo": "excited", "text": "نہیں!"}, {"id": "sfx_004", "who": "BILAL", "emo": "laugh", "text": "ہی ہی ہی ہی ہی!"}, {"id": "sfx_005", "who": "ZAID", "emo": "excited", "text": "نہیں!"}, {"id": "sfx_006", "who": "ZAID", "emo": "laugh", "text": "ہی ہی ہی ہی ہی!"}, {"id": "sfx_007", "who": "MARYAM", "emo": "excited", "text": "نہیں!"}, {"id": "sfx_008", "who": "MARYAM", "emo": "laugh", "text": "ہی ہی ہی ہی ہی!"}, {"id": "sfx_009", "who": "NANA", "emo": "laugh", "text": "ہا ہا ہا ہا!"}]''')


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
    z = os.path.join(HERE, 'iqra_voices.zip')
    with zipfile.ZipFile(z, 'w') as zf:
        for fn in sorted(os.listdir(OUT)): zf.write(os.path.join(OUT, fn), fn)
    n = len([x for x in os.listdir(OUT) if x.endswith('.mp3')])
    print(f"\nDone: {n} of {len(LINES)} voice lines. File: {z}")

asyncio.run(main())
