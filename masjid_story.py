"""Episode 2: "Masjid ke Adaab" (مسجد کے آداب) — Masjid manners. For the Iqra-LetsLearn channel.
Kids push and giggle in jamaat; after salah Nana Jaan plays a game: he acts out distracting habits and asks
"Kya yeh sahi tareeqa hai?", the kids shout "Nahin!", then he teaches the right way, step by step.
Beat: ("say", who, roman_caption, devanagari_for_voice, emotion) | ("wait", s) | ("sfx", name).
Who: N (narrator), NANA, ALI, BILAL, ZAID, MARYAM, ALL (group sfx captions)."""

TITLE_UR = "مسجد کے آداب"
TITLE_RO = "Masjid ke Adaab"
MORAL_HEAD = "سبق"
MORAL = ("مسجد اللہ کا گھر ہے۔", "وہاں سکون اور ادب سے رہو۔")
THANKS = "دیکھنے کا شکریہ!"
SUBSCRIBE = "سبسکرائب کریں"
CHANNEL = "Iqra-LetsLearn"
NAMES = {'ALI': 'Ali', 'BILAL': 'Bilal', 'ZAID': 'Zaid', 'NANA': 'Nana Jaan', 'MARYAM': 'Maryam', 'ALL': 'Sab bachche'}
STEPS = ["1. Saff seedhi", "2. Nazar sajde ki jagah", "3. Takbeer", "4. Qiyaam", "5. Ruku", "6. Sajda", "7. Jalsa"]

ASK = ("say", "NANA", "Kya yeh sahi tareeqa hai?", "क्या ये सही तरीक़ा है?", "playful")
NAHIN = ("sfx", "nahin")


def game(roman, dev, extra=()):
    return [("say", "NANA", roman, dev, "playful"), *extra, ("wait", 0.3), ASK, NAHIN, ("wait", 0.2), ("sfx", "kids_giggle"), ("wait", 0.6)]


SHOTS = [
    ("title", [("wait", 1.0), ("say", "N", "Masjid ke Adaab", "मस्जिद के आदाब।", "warm"), ("wait", 1.6)]),

    ("jamaat", [
        ("wait", 0.6),
        ("say", "N", "Jumma ka din tha. Masjid mein jamaat khari thi.", "जुम्मा का दिन था। मस्जिद में जमात खड़ी थी।", "neutral"),
        ("wait", 1.2),
        ("say", "N", "Lekin Bilal ka dhyaan namaz mein nahin tha. Usne Ali ko halka sa dhakka diya!",
         "लेकिन बिलाल का ध्यान नमाज़ में नहीं था। उसने अली को हल्का सा धक्का दिया!", "neutral"),
        ("sfx", "kids_giggle"),
        ("wait", 0.8),
        ("say", "N", "Ali ne bhi dhakka diya, aur Zaid bhi khi khi karke hansne laga!",
         "अली ने भी धक्का दिया, और ज़ैद भी खी खी करके हंसने लगा!", "excited"),
        ("sfx", "kids_giggle"),
        ("wait", 1.6),
    ]),

    ("after", [
        ("say", "N", "Namaz ke baad, Nana Jaan muskuraate hue bachchon ke paas aaye.",
         "नमाज़ के बाद, नाना जान मुस्कुराते हुए बच्चों के पास आए।", "warm"),
        ("say", "NANA", "Assalamu alaikum, bachcho! Aao, ek khel khelte hain!",
         "अस्सलामु अलैकुम, बच्चो! आओ, एक खेल खेलते हैं!", "warm"),
        ("say", "BILAL", "Khel? Wah! Kaunsa khel, Nana Jaan?", "खेल? वाह! कौन सा खेल, नाना जान?", "excited"),
        ("say", "NANA", "Main dikhaata hoon ke kuch bachche namaz mein kya karte hain. Tum batana, sahi hai ya nahin!",
         "मैं दिखाता हूं कि कुछ बच्चे नमाज़ में क्या करते हैं। तुम बताना, सही है या नहीं!", "playful"),
        ("wait", 0.5),
    ]),

    ("g_push", game("Dekho! Main apne saath wale ko dhakka deta hoon... dhakka!",
                    "देखो! मैं अपने साथ वाले को धक्का देता हूं... धक्का!")),
    ("g_giggle", game("Ab main namaz mein khi khi karke hansta hoon!", "अब मैं नमाज़ में खी खी करके हंसता हूं!",
                      (("sfx", "nana_giggle"),))),
    ("g_yawn", game("Ab main idhar udhar dekhta hoon... aur badi si jamaai leta hoon. Aaaaah!",
                    "अब मैं इधर उधर देखता हूं... और बड़ी सी जमाई लेता हूं। आआआआह!")),
    ("g_fidget", game("Ab main sar khujaata hoon, kapde kheenchta hoon, aur ungliyan chatkaata hoon!",
                      "अब मैं सर खुजाता हूं, कपड़े खींचता हूं, और उंगलियां चटकाता हूं!", (("sfx", "crack"),))),
    ("g_run", game("Aur ab main namaz padhne walon ke saamne se bhaagta hoon!",
                   "और अब मैं नमाज़ पढ़ने वालों के सामने से भागता हूं!", (("sfx", "run"), ("wait", 1.2))) + [
        ("say", "MARYAM", "Nana Jaan, aap to bilkul Bilal jaise lag rahe the!", "नाना जान, आप तो बिल्कुल बिलाल जैसे लग रहे थे!", "laugh"),
        ("sfx", "kids_giggle"),
        ("say", "BILAL", "Ji, Nana Jaan... ab hum aisa nahin karenge.", "जी, नाना जान... अब हम ऐसा नहीं करेंगे।", "sad"),
        ("wait", 0.4),
    ]),

    ("right_intro", [
        ("say", "NANA", "Shabaash! Ab dekho, namaz ka sahi tareeqa.", "शाबाश! अब देखो, नमाज़ का सही तरीक़ा।", "warm"),
        ("wait", 0.4),
    ]),
    ("s_saff", [("say", "NANA", "Saff seedhi rakho. Kandhe se kandha, paon se paon milao.",
                 "सफ़ सीधी रखो। कंधे से कंधा, पांव से पांव मिलाओ।", "warm"), ("wait", 1.0)]),
    ("s_nazar", [("say", "NANA", "Nazar sajde ki jagah par rakho.", "नज़र सजदे की जगह पर रखो।", "warm"), ("wait", 1.0)]),
    ("s_takbir", [("say", "NANA", "Allahu Akbar kaho, aur haath kaanon tak uthao.", "अल्लाहु अकबर कहो, और हाथ कानों तक उठाओ।", "warm"), ("wait", 1.0)]),
    ("s_qiyam", [("say", "NANA", "Haath baandh kar, sukoon se khade raho.", "हाथ बांध कर, सुकून से खड़े रहो।", "warm"), ("wait", 1.0)]),
    ("s_ruku", [("say", "NANA", "Ruku mein jhuko, aur haath ghutnon par rakho.", "रुकू में झुको, और हाथ घुटनों पर रखो।", "warm"), ("wait", 1.2)]),
    ("s_sajda", [("say", "NANA", "Sajde mein maatha aur naak zameen par lagao.", "सजदे में माथा और नाक ज़मीन पर लगाओ।", "warm"), ("wait", 1.4)]),
    ("s_jalsa", [("say", "NANA", "Phir aaraam se baitho. Na hilna, na hansna.", "फिर आराम से बैठो। न हिलना, न हंसना।", "warm"), ("wait", 1.0),
                 ("say", "ZAID", "Yeh to bahut aasaan hai!", "ये तो बहुत आसान है!", "excited"),
                 ("say", "ALI", "Ab hum hamesha aise hi namaz padhenge, Nana Jaan!", "अब हम हमेशा ऐसे ही नमाज़ पढ़ेंगे, नाना जान!", "happy"),
                 ("wait", 0.5)]),

    ("jamaat2", [
        ("wait", 0.5),
        ("say", "N", "Agli jamaat mein, teeno bachche bilkul seedhe aur sukoon se khade the.",
         "अगली जमात में, तीनों बच्चे बिल्कुल सीधे और सुकून से खड़े थे।", "warm"),
        ("wait", 1.6),
    ]),
    ("proud", [
        ("say", "NANA", "MashaAllah! Mujhe tum teeno par fakhr hai.", "माशा अल्लाह! मुझे तुम तीनों पर फ़ख़्र है।", "proud"),
        ("sfx", "kids_giggle"),
        ("wait", 0.8),
    ]),
    ("moral", [("wait", 0.6), ("say", "N", "Masjid Allah ka ghar hai. Wahan sukoon aur adab se raho.",
                                "मस्जिद अल्लाह का घर है। वहां सुकून और अदब से रहो।", "warm"), ("wait", 1.8)]),
    ("end", [("wait", 5.0)]),
]
