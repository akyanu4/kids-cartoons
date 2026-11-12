"""Nesting Stories, Episode 1: "Naya Kirayedaar" (The New Tenant) - Taaruf (Introduction).
Beats: ('say', who, emo, roman, urdu) | ('sfx', name) | ('wait', seconds). One shot = one scene layout."""
TITLE = 'Naya Kirayedaar'
TITLE_UR = 'نیا کرایہ دار'
EPISODE = 'Episode 1: Taaruf'
NAMES = {'N': None, 'CHACHA': 'Rasheed Chacha', 'IMRAN': 'Imran'}

SHOTS = [
    ('title', [('wait', 4.0)]),
    ('boxes', [
        ('say', 'N', 'playful', 'Yeh hain Rasheed Chacha. Umar bahattar saal. Aur shauq? Ghar badalna!',
         'یہ ہیں رشید چچا۔ عمر بہتّر سال۔ اور شوق؟ گھر بدلنا!'),
        ('say', 'CHACHA', 'happy', 'Yeh mera chaudahvaan ghar hai... sirf is saal ka!',
         'یہ میرا چودہواں گھر ہے... صرف اس سال کا!'),
        ('say', 'N', 'neutral', 'Har do hafte baad, Chacha ka saamaan phir se dabbon mein band ho jaata hai.',
         'ہر دو ہفتے بعد، چچا کا سامان پھر سے ڈبوں میں بند ہو جاتا ہے۔'),
        ('sfx', 'tape'),
        ('say', 'CHACHA', 'thoughtful', 'Yeh ghar bhi theek nahin. Khidki chhoti hai, aur padosi ka murgha subah paanch baje bolta hai!',
         'یہ گھر بھی ٹھیک نہیں۔ کھڑکی چھوٹی ہے، اور پڑوسی کا مرغا صبح پانچ بجے بولتا ہے!'),
        ('sfx', 'rooster'),
    ]),
    ('namaz', [
        ('say', 'N', 'playful', 'Aur masjid? Chacha ne kabhi uska raasta bhi nahin dekha.',
         'اور مسجد؟ چچا نے کبھی اس کا راستہ بھی نہیں دیکھا۔'),
        ('say', 'CHACHA', 'playful', 'Namaz-shamaz baad mein! Pehle achha sa ghar to mil jaaye!',
         'نماز شماز بعد میں! پہلے اچھا سا گھر تو مل جائے!'),
    ]),
    ('ad', [
        ('say', 'N', 'neutral', 'Aur phir, ek din, Chacha ke phone par ek ishtehaar aaya.',
         'اور پھر، ایک دن، چچا کے فون پر ایک اشتہار آیا۔'),
        ('sfx', 'ding'),
        ('wait', 1.2),
        ('say', 'CHACHA', 'excited', 'Poora hall... bijli, paani, internet sab shaamil? Bas! Yehi mera agla ghar hai!',
         'پورا ہال... بجلی، پانی، انٹرنیٹ سب شامل؟ بس! یہی میرا اگلا گھر ہے!'),
        ('sfx', 'ring'),
    ]),
    ('call', [
        ('say', 'IMRAN', 'warm', 'Hello, assalamu alaikum. Main Imran bol raha hoon.',
         'ہیلو، السلام علیکم۔ میں عمران بول رہا ہوں۔'),
        ('say', 'CHACHA', 'excited', 'Haan haan, woh hall! Main le raha hoon! Abhi aa raha hoon!',
         'ہاں ہاں، وہ ہال! میں لے رہا ہوں! ابھی آ رہا ہوں!'),
        ('say', 'IMRAN', 'surprised', 'Arre Chacha, pehle dekh to lijiye...',
         'ارے چچا، پہلے دیکھ تو لیجیے...'),
        ('say', 'CHACHA', 'excited', 'Dekhna kya hai beta? Internet hai na? Bas, main aa gaya!',
         'دیکھنا کیا ہے بیٹا؟ انٹرنیٹ ہے نا؟ بس، میں آ گیا!'),
        ('sfx', 'hangup'),
        ('say', 'IMRAN', 'laugh', 'Hau... yeh to bade jaldi mein hain!',
         'ہاؤ... یہ تو بڑے جلدی میں ہیں!'),
    ]),
    ('imran', [
        ('say', 'N', 'warm', 'Yeh hain Imran. Hyderabad ke software engineer. Dil ke bade naram, aur haath ke bade khule.',
         'یہ ہیں عمران۔ حیدرآباد کے سافٹ ویئر انجینئر۔ دل کے بڑے نرم، اور ہاتھ کے بڑے کھلے۔'),
    ]),
    ('arrive', [
        ('sfx', 'knock'),
        ('say', 'CHACHA', 'excited', 'Main aa gaya!', 'میں آ گیا!'),
        ('say', 'IMRAN', 'warm', 'Aaiye Chacha, aaiye! Andar aaiye na.', 'آئیے چچا، آئیے! اندر آئیے نا۔'),
    ]),
    ('memory', [
        ('say', 'N', 'gentle', 'Chacha ko dekh kar, Imran ko apne Abba yaad aa gaye... jo ab is duniya mein nahin hain.',
         'چچا کو دیکھ کر، عمران کو اپنے ابّا یاد آ گئے... جو اب اس دنیا میں نہیں ہیں۔'),
        ('say', 'IMRAN', 'gentle', 'Abba bhi aise hi the... har baat mein jaldi.',
         'ابّا بھی ایسے ہی تھے... ہر بات میں جلدی۔'),
        ('say', 'IMRAN', 'gentle', 'Agar main ek buzurg ki khidmat karoon, to Abba ki rooh bhi khush hogi... aur Allah bhi.',
         'اگر میں ایک بزرگ کی خدمت کروں، تو ابّا کی روح بھی خوش ہوگی... اور اللہ بھی۔'),
    ]),
    ('deal', [
        ('say', 'IMRAN', 'warm', 'Chacha, poora hall aapka. Bijli, paani, internet, sab shaamil hai.',
         'چچا، پورا ہال آپ کا۔ بجلی، پانی، انٹرنیٹ، سب شامل ہے۔'),
        ('say', 'CHACHA', 'surprised', 'Sab shaamil? Aur kiraya kitna?', 'سب شامل؟ اور کرایہ کتنا؟'),
        ('say', 'IMRAN', 'warm', 'Jitna aap de sakein, Chacha. Kaiku fikr karte aap?',
         'جتنا آپ دے سکیں، چچا۔ کائیکو فکر کرتے آپ؟'),
        ('say', 'CHACHA', 'happy', 'Beta, tum to bilkul farishta ho!', 'بیٹا، تم تو بالکل فرشتہ ہو!'),
        ('wait', 0.6),
        ('say', 'CHACHA', 'playful', 'Achha... wifi ka password kya hai?', 'اچھا... وائی فائی کا پاس ورڈ کیا ہے؟'),
        ('say', 'IMRAN', 'laugh', 'Ha ha ha!', 'ہا ہا ہا!'),
    ]),
    ('next', [
        ('say', 'N', 'playful', 'Aur is tarah, Rasheed Chacha ko mil gaya apna pandrahvaan ghar.',
         'اور اس طرح، رشید چچا کو مل گیا اپنا پندرہواں گھر۔'),
        ('say', 'N', 'surprised', 'Lekin kya Chacha yahan tik paayenge? Dekhiye agle episode mein... Aamad!',
         'لیکن کیا چچا یہاں ٹک پائیں گے؟ دیکھیے اگلے ایپیسوڈ میں... آمد!'),
    ]),
    ('end', [('wait', 5.0)]),
]

LINES = [b for _, beats in SHOTS for b in beats if b[0] == 'say']
