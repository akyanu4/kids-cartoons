"""Nesting Stories, Episode 1: "Naya Kirayedaar" (The New Tenant) - Taaruf (Introduction).
Beats: ('say', who, emo, roman, urdu) | ('sfx', name) | ('wait', seconds). One shot = one scene layout."""
TITLE = 'Naya Kirayedaar'
TITLE_UR = 'نیا کرایہ دار'
EPISODE = 'Episode 1: Taaruf'
NAMES = {'N': None, 'CHACHA': 'Rasheed Chacha', 'IMRAN': 'Imran'}
GAP, SCENE_GAP = 0.12, 0.15          # pauses after a line / between scenes (kept short: brisk comedy pace)

SHOTS = [
    ('title', [('wait', 3.0)]),
    ('boxes', [
        ('say', 'N', 'playful', 'Yeh hain Rasheed Chacha. Umar bahattar saal. Shauq? Ghar badalna... aur har ghar mein thodi si shararat!',
         'یہ ہیں رشید چچا۔ عمر بہتّر سال۔ شوق؟ گھر بدلنا... اور ہر گھر میں تھوڑی سی شرارت!'),
        ('say', 'CHACHA', 'naughty', 'Yeh mera chaudahvaan ghar hai... sirf is saal ka! He he!',
         'یہ میرا چودہواں گھر ہے... صرف اس سال کا! ہی ہی!'),
        ('sfx', 'tape'),
        ('say', 'N', 'playful', 'Chacha ka ek purana tareeqa hai. Naye ghar mein aao, koi jhagda khada karo, kiraya mat do... aur agle ghar chal do!',
         'چچا کا ایک پرانا طریقہ ہے۔ نئے گھر میں آؤ، کوئی جھگڑا کھڑا کرو، کرایہ مت دو... اور اگلے گھر چل دو!'),
    ]),
    ('flashback', [
        ('say', 'CHACHA', 'angry', 'Kiraya? Kis baat ka kiraya? Nal mein garam paani hi nahin aata! Main ja raha hoon!',
         'کرایہ؟ کس بات کا کرایہ؟ نل میں گرم پانی ہی نہیں آتا! میں جا رہا ہوں!'),
        ('sfx', 'slam'),
    ]),
    ('namaz', [
        ('say', 'N', 'playful', 'Aur masjid? Chacha ne kabhi uska raasta bhi nahin dekha.',
         'اور مسجد؟ چچا نے کبھی اس کا راستہ بھی نہیں دیکھا۔'),
        ('say', 'CHACHA', 'naughty', 'Namaz-shamaz baad mein! Pehle achha sa ghar to mil jaaye!',
         'نماز شماز بعد میں! پہلے اچھا سا گھر تو مل جائے!'),
    ]),
    ('ad', [
        ('say', 'N', 'neutral', 'Phir ek din, Chacha ke phone par ek ishtehaar aaya.',
         'پھر ایک دن، چچا کے فون پر ایک اشتہار آیا۔'),
        ('sfx', 'ding'),
        ('wait', 0.6),
        ('say', 'CHACHA', 'excited', 'Poora hall, teen mahine ke liye... bijli, paani, internet sab shaamil? Bas! Yehi mera agla ghar hai!',
         'پورا ہال، تین مہینے کے لیے... بجلی، پانی، انٹرنیٹ سب شامل؟ بس! یہی میرا اگلا گھر ہے!'),
        ('sfx', 'ring'),
    ]),
    ('call', [
        ('say', 'IMRAN', 'warm', 'Hello, assalamu alaikum. Main Imran bol raha hoon.',
         'ہیلو، السلام علیکم۔ میں عمران بول رہا ہوں۔'),
        ('say', 'CHACHA', 'excited', 'Haan haan, woh hall! Main le raha hoon! Kahaan milein?',
         'ہاں ہاں، وہ ہال! میں لے رہا ہوں! کہاں ملیں؟'),
        ('say', 'IMRAN', 'surprised', 'Arre Chacha... ghar ke saamne footpath par aa jaaiye, main wahin hoon.',
         'ارے چچا... گھر کے سامنے فٹ پاتھ پر آ جائیے، میں وہیں ہوں۔'),
        ('say', 'CHACHA', 'excited', 'Abhi aaya!', 'ابھی آیا!'),
        ('sfx', 'hangup'),
        ('say', 'IMRAN', 'laugh', 'Hau... yeh to bade jaldi mein hain!',
         'ہاؤ... یہ تو بڑے جلدی میں ہیں!'),
    ]),
    ('imran', [
        ('say', 'N', 'warm', 'Yeh hain Imran. Hyderabad ke software engineer, dil ke bade naram. Unki family kuch mahinon ke liye India gayi hui hai.',
         'یہ ہیں عمران۔ حیدرآباد کے سافٹ ویئر انجینئر، دل کے بڑے نرم۔ ان کی فیملی کچھ مہینوں کے لیے انڈیا گئی ہوئی ہے۔'),
    ]),
    ('sidewalk', [
        ('sfx', 'car'),
        ('wait', 0.3),
        ('sfx', 'cardoor'),
        ('wait', 1.6),
        ('say', 'CHACHA', 'thoughtful', 'Hmmm...', 'ہمممم...'),
        ('wait', 0.8),
        ('say', 'IMRAN', 'warm', 'Assalamu alaikum, Chacha! Aaiye, aaiye.', 'السلام علیکم، چچا! آئیے، آئیے۔'),
        ('say', 'IMRAN', 'surprised', 'Chacha... aapki gaadi ka bumper?', 'چچا... آپ کی گاڑی کا بمپر؟'),
        ('say', 'CHACHA', 'naughty', 'Woh? Pichhle makaan-maalik ki deewar se dosti ho gayi thi! He he!',
         'وہ؟ پچھلے مکان مالک کی دیوار سے دوستی ہو گئی تھی! ہی ہی!'),
        ('say', 'CHACHA', 'naughty', 'Walaikum assalam, beta. Pehle ek baat bata do. Main har itwaar paaye ka soup banata hoon. Poore ghar mein khushboo aayegi. Koi problem to nahin hogi?',
         'وعلیکم السلام، بیٹا۔ پہلے ایک بات بتا دو۔ میں ہر اتوار پائے کا سوپ بناتا ہوں۔ پورے گھر میں خوشبو آئے گی۔ کوئی پرابلم تو نہیں ہوگی؟'),
        ('say', 'IMRAN', 'laugh', 'Problem? Chacha, main Hyderabadi hoon. Paaye to hamari jaan hain!',
         'پرابلم؟ چچا، میں حیدرآبادی ہوں۔ پائے تو ہماری جان ہیں!'),
        ('say', 'CHACHA', 'naughty', 'Phir to tumhe bhi milega... agar kiraya thoda kam ho jaaye! He he!',
         'پھر تو تمہیں بھی ملے گا... اگر کرایہ تھوڑا کم ہو جائے! ہی ہی!'),
        ('say', 'CHACHA', 'proud', 'Aur suno! Main bhi jawani mein computer par kaam karta tha. Itna data dala, itna data... ke computer khud thak gaya!',
         'اور سنو! میں بھی جوانی میں کمپیوٹر پر کام کرتا تھا۔ اتنا ڈیٹا ڈالا، اتنا ڈیٹا... کہ کمپیوٹر خود تھک گیا!'),
        ('say', 'IMRAN', 'surprised', 'Wah Chacha! Kaunsa computer tha?', 'واہ چچا! کون سا کمپیوٹر تھا؟'),
        ('say', 'CHACHA', 'naughty', 'Bada wala! Poore kamre jitna! Aaj kal ke tumhare laptop to bachche hain!',
         'بڑا والا! پورے کمرے جتنا! آج کل کے تمہارے لیپ ٹاپ تو بچے ہیں!'),
    ]),
    ('tour', [
        ('say', 'IMRAN', 'warm', 'Aaiye Chacha, ghar dikhata hoon. Yeh poora hall aapka. Bijli, paani, internet, sab shaamil.',
         'آئیے چچا، گھر دکھاتا ہوں۔ یہ پورا ہال آپ کا۔ بجلی، پانی، انٹرنیٹ، سب شامل۔'),
        ('say', 'CHACHA', 'naughty', 'Hmm... jahan main abhi rehta hoon, wahan ke engineer ne to mujhe alag kamra aur closet bhi diya hai!',
         'ہمم... جہاں میں ابھی رہتا ہوں، وہاں کے انجینئر نے تو مجھے الگ کمرہ اور کلوزٹ بھی دیا ہے!'),
        ('say', 'IMRAN', 'warm', 'Fikr mat kijiye, closet yahan bhi hai. Bas ek baat... yeh ghar sirf teen mahine ke liye hai. Meri family India gayi hui hai.',
         'فکر مت کیجیے، کلوزٹ یہاں بھی ہے۔ بس ایک بات... یہ گھر صرف تین مہینے کے لیے ہے۔ میری فیملی انڈیا گئی ہوئی ہے۔'),
        ('say', 'CHACHA', 'naughty', 'Teen mahine? Arre, mere liye to yeh lambi muddat hai! He he!',
         'تین مہینے؟ ارے، میرے لیے تو یہ لمبی مدت ہے! ہی ہی!'),
    ]),
    ('memory', [
        ('say', 'N', 'gentle', 'Chacha ko dekh kar, Imran ko apne Abba yaad aa gaye... jo ab is duniya mein nahin hain.',
         'چچا کو دیکھ کر، عمران کو اپنے ابّا یاد آ گئے... جو اب اس دنیا میں نہیں ہیں۔'),
        ('say', 'IMRAN', 'gentle', 'Abba bhi aise hi the... har baat mein jaldi. Agar main inki khidmat karoon, to Abba ki rooh bhi khush hogi... aur Allah bhi.',
         'ابّا بھی ایسے ہی تھے... ہر بات میں جلدی۔ اگر میں ان کی خدمت کروں، تو ابّا کی روح بھی خوش ہوگی... اور اللہ بھی۔'),
    ]),
    ('deal', [
        ('say', 'CHACHA', 'naughty', 'To beta... kiraya kitna?', 'تو بیٹا... کرایہ کتنا؟'),
        ('say', 'IMRAN', 'warm', 'Jitna aap de sakein, Chacha. Kaiku fikr karte aap?',
         'جتنا آپ دے سکیں، چچا۔ کائیکو فکر کرتے آپ؟'),
        ('say', 'CHACHA', 'happy', 'Beta, tum to bilkul farishta ho!', 'بیٹا، تم تو بالکل فرشتہ ہو!'),
        ('wait', 0.4),
        ('say', 'CHACHA', 'naughty', 'Achha... wifi ka password kya hai?', 'اچھا... وائی فائی کا پاس ورڈ کیا ہے؟'),
        ('say', 'IMRAN', 'laugh', 'Ha ha ha!', 'ہا ہا ہا!'),
    ]),
    ('next', [
        ('say', 'N', 'surprised', 'Rasheed Chacha ko mil gaya apna pandrahvaan ghar. Lekin kya Chacha is baar kiraya denge... ya phir koi naya jhagda? Dekhiye agle episode mein... Aamad!',
         'رشید چچا کو مل گیا اپنا پندرہواں گھر۔ لیکن کیا چچا اس بار کرایہ دیں گے... یا پھر کوئی نیا جھگڑا؟ دیکھیے اگلے ایپیسوڈ میں... آمد!'),
    ]),
    ('end', [('wait', 4.0)]),
]

LINES = [b for _, beats in SHOTS for b in beats if b[0] == 'say']
