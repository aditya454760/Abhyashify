#!/usr/bin/env python3
"""Search, answer-engine and AI-engine pages for the Abhyashify site.

build.py calls this. It reads the exam catalogue (app/src/exams.js) and writes, into docs/:
  about/, exams/, exams/<id>/        English pages
  hi/about/, hi/exams/, hi/exams/<id>/   Hindi pages (with hreflang pairs)
  sitemap.xml, robots.txt, llms.txt, llms-full.txt, 404.html, pages.css
and gives build.py the head tags and <noscript> text for index.html.

Nothing here invents facts about an exam: subjects, typical months, study hours and mock lengths all come from
the catalogue, which the README already says is written from general knowledge and must be checked against the
exam body's own notice. Every page says so.
"""
import os, json, html, subprocess, datetime

BASE = 'https://aditya454760.github.io/Abhyashify/'
SITE = 'Abhyashify'
REPO = 'https://github.com/aditya454760/Abhyashify'
AUTHOR_URL = 'https://github.com/aditya454760'
here = os.path.dirname(os.path.abspath(__file__))
esc = lambda s: html.escape(str(s), quote=True)

TITLE = {'en': 'Abhyashify: exam study planner for GATE, JEE, NEET, UPSC',
         'hi': 'अभ्यासिफ़ाई: GATE, JEE, NEET, UPSC की पढ़ाई का प्लानर'}
DESC = {'en': 'Pick your exam and get a day-by-day timetable up to exam day, with alarms, study-time tracking, weekly reports and an assistant in English and Hindi.',
        'hi': 'अपनी परीक्षा चुनें और परीक्षा के दिन तक का रोज़ का टाइमटेबल पाएँ: अलार्म, पढ़ाई का समय, साप्ताहिक रिपोर्ट और हिन्दी-अंग्रेज़ी असिस्टेंट के साथ।'}

MONTHS = {'en': ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
          'hi': ['', 'जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर']}


def catalogue():
    t = open(os.path.join(here, 'src', 'exams.js'), encoding='utf-8').read()
    t = t[:t.index('/* the starting tools')]
    js = "const fs=require('fs');const f=new Function(fs.readFileSync(0,'utf8')+';return {EXAMS,WHEN_HI}');" \
         "process.stdout.write(JSON.stringify(f()))"
    # WHEN_HI is declared after the tools block, so give the evaluator the whole file up to the i18n helper
    full = open(os.path.join(here, 'src', 'exams.js'), encoding='utf-8').read()
    cut = full.index('const WHEN_HI')
    end = full.index('};', cut) + 2
    src = t + '\n' + full[cut:end]
    r = subprocess.run(['node', '-e', js], input=src, capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        raise SystemExit('seo.py: could not read the exam catalogue with node:\n' + r.stderr)
    d = json.loads(r.stdout)
    return d['EXAMS'], d['WHEN_HI']


EXAMS, WHEN_HI = catalogue()
TODAY = datetime.date.today().isoformat()
FAM = {f['id']: f for f in EXAMS}


def L(lang, en, hi):
    return hi if lang == 'hi' and hi else en


def fname(f, lang):
    return L(lang, f['name'], f['hi'])


def url_of(lang, kind, fid=None):
    p = ('hi/' if lang == 'hi' else '') + {'about': 'about/', 'exams': 'exams/', 'exam': 'exams/%s/' % fid}[kind]
    return BASE + p


def months(lang, wm):
    m = [MONTHS[lang][i] for i in wm]
    if len(m) == 1:
        return m[0]
    joiner = ' और ' if lang == 'hi' else ' and '
    return ', '.join(m[:-1]) + joiner + m[-1]


# ----------------------------------------------------------------------------------------------------------
# About-page content (answer-first, short, quotable)
# ----------------------------------------------------------------------------------------------------------
def fam_list(lang):
    return ', '.join(fname(f, lang) for f in EXAMS)


def about_faq(lang):
    n = len(EXAMS)
    if lang == 'hi':
        return [
            ('अभ्यासिफ़ाई क्या है?',
             'अभ्यासिफ़ाई (Abhyashify) प्रतियोगी परीक्षाओं की पढ़ाई का प्लानर है जो ब्राउज़र में चलता है और ऐप की तरह इंस्टॉल हो जाता है। आप अपनी परीक्षा चुनते हैं, यह परीक्षा की तारीख़ तक का रोज़ का टाइमटेबल बनाता है, हर पढ़ाई-ब्लॉक पर अलार्म बजाता है, आपने असल में कितना पढ़ा यह दर्ज करता है और साप्ताहिक रिपोर्ट में योजना से मिलाता है।'),
            ('कौन-कौन सी परीक्षाएँ शामिल हैं?',
             'अभी %d परीक्षा-परिवारों के विषय पहले से भरे हैं: %s। हर परिवार में उसके पेपर या ब्रांच हैं, जैसे GATE के CS, DA, ECE, EE, ME, CE वगैरह, या JEE Main और Advanced। जो परीक्षा सूची में नहीं है उसके लिए "अन्य" विकल्प हमेशा रहता है।' % (n, fam_list('hi'))),
            ('टाइमटेबल कैसे बनता है?',
             'यह आपकी परीक्षा, पेपर या ब्रांच और वैकल्पिक विषय पूछता है, फिर परीक्षा की तारीख़ (या महीना, या आपकी अपनी लक्ष्य-तारीख़) पक्की करवाता है। इसके बाद पूछता है कि दिन के कौन-से समय आपको सूट करते हैं, सप्ताह के दिनों और छुट्टी के दिनों में कितने घंटे दे सकते हैं और कौन-से दिन छुट्टी हैं। इन जवाबों से यह महत्त्व के हिसाब से विषयों को तारीख़ तक के दिनों में बाँटता है और अंत में रिवीज़न का बफ़र और मॉक टेस्ट रखता है। नतीजा आप जैसा है वैसा चला सकते हैं या कोई भी ब्लॉक बदल सकते हैं।'),
            ('क्या परीक्षा की तारीख़ें और सिलेबस आधिकारिक हैं?',
             'नहीं। विषय और आम तौर पर होने के महीने सामान्य जानकारी से लिखे गए हैं, आधिकारिक साइटों से लिए नहीं गए। अभ्यासिफ़ाई आपसे आपकी परीक्षा की तारीख़ पक्की करवाता है और अपने अनुमान को कभी असली तारीख़ नहीं मानता। सिलेबस और कार्यक्रम परीक्षा करवाने वाली संस्था की अपनी वेबसाइट पर देखें और विषय अलग हों तो बदल लें।'),
            ('क्या इसकी कोई कीमत है?',
             'अभ्यासिफ़ाई में कोई पेड प्लान नहीं है। बिल्ट-इन असिस्टेंट बिना अकाउंट और बिना खर्च के चलता है। वैकल्पिक चीज़ों का खर्च आपकी अपनी कुंजी से जुड़ा है: क्लोन की हुई आवाज़ के लिए ElevenLabs का पेड प्लान चाहिए और असिस्टेंट के स्मार्ट मोड में आपकी अपनी Gemini या Anthropic कुंजी लगती है।'),
            ('क्या यह फ़ोन पर और ऑफ़लाइन चलता है?',
             'हाँ। इसे Chrome, Edge या Safari में खोलकर ब्राउज़र मेन्यू से इंस्टॉल करें (iPhone पर "होम स्क्रीन पर जोड़ें")। उसके बाद यह अपनी विंडो में खुलता है और ऑफ़लाइन भी लोड होता है, और इंटरनेट लौटने पर डेटा अपडेट हो जाता है। अलार्म तभी बजते हैं जब पेज खुला हो, क्योंकि वेब पेज बंद फ़ोन को जगा नहीं सकता।'),
            ('क्या यह दूसरे ऐप और वेबसाइट पर पढ़ाई का समय गिन सकता है?',
             'कुछ हद तक। वेब पेज दूसरे ऐप या टैब नहीं देख सकता। अभ्यासिफ़ाई यह दर्ज करता है कि आप आज वाली स्क्रीन से किसी पढ़ाई के टूल पर कब गए और कब लौटे। Chrome/Edge एक्सटेंशन आपकी चुनी हुई पढ़ाई की साइटों पर बिताया समय गिनता है, और Android का साथी ऐप आपके चुने हुए पढ़ाई के ऐप का उपयोग-समय पढ़ता है। Android साथी ऐप अभी प्रायोगिक है।'),
            ('क्या यह हिन्दी में उपलब्ध है?',
             'हाँ। पूरा ऐप, असिस्टेंट के जवाब और वॉइस चैट सेटिंग्स से हिन्दी और अंग्रेज़ी के बीच बदले जा सकते हैं। हिन्दी बिल्ट-इन शब्दकोश से आती है, इसलिए कुछ वाक्यांश अब भी अंग्रेज़ी में दिख सकते हैं।'),
            ('सिंक कैसे होता है और मेरे डेटा का क्या होता है?',
             'Google से साइन इन करने पर आपका प्लान, सामग्री और पढ़ाई के लॉग Google Firestore के ज़रिए सिंक होते हैं, ताकि फ़ोन और लैपटॉप पर एक ही डेटा दिखे। अगर दो डिवाइस पर एक ही कोर्स का समय एक साथ दर्ज हो, तो वह ओवरलैप एक बार ही गिना जाता है। स्मार्ट मोड की आपकी कुंजी सिर्फ़ आपके डिवाइस पर रहती है और सिर्फ़ चुने हुए प्रदाता को भेजी जाती है।'),
            ('क्या मैं असिस्टेंट से बात कर सकता हूँ?',
             'हाँ। असिस्टेंट का नाम अनु है (पुरुष आवाज़ में आदि)। आप टाइप कर सकते हैं या बोल सकते हैं। वह अलार्म और रिमाइंडर लगाता है, टेस्ट शेड्यूल करता है और ऐप के बारे में सवालों के जवाब देता है। बोलने के लिए स्पीच सपोर्ट वाला ब्राउज़र चाहिए, जैसे Chrome, Edge या Safari।'),
        ]
    return [
        ('What is Abhyashify?',
         'Abhyashify is a study planner for competitive exams that runs in the browser and installs like an app. You choose an exam, it builds a day-by-day timetable up to your exam date, rings an alarm for each study block, logs the hours you actually study and compares them with the plan in a weekly report.'),
        ('Which exams does it cover?',
         'It has preloaded subjects for %d exam families: %s. Each one has its papers or branches, for example GATE CS, DA, ECE, EE, ME and CE, or JEE Main and Advanced. There is always an Other option for an exam that is not listed.' % (n, fam_list('en'))),
        ('How does it build the timetable?',
         'It asks for your exam, your paper or branch and any optional subjects, then confirms your exam date (or month, or your own target date). It then asks which parts of the day suit you, how many hours you can give on weekdays and on days off, and which days are off. From those answers it spreads the subjects across the days up to the date, weighted by importance, and keeps a revision buffer and mock tests at the end. You can follow the result as it is or edit any block.'),
        ('Are the exam dates and syllabus official?',
         'No. The subjects and the months an exam is usually held were written from general knowledge, not downloaded from official sites. Abhyashify asks you to confirm your own exam date and never treats its hint as the real date. Check the syllabus and schedule on the exam body\'s own website and edit the subjects if they differ.'),
        ('Does it cost anything?',
         'Abhyashify has no paid plan. The built-in assistant works with no account and no cost. Optional extras use your own keys: a cloned voice needs a paid plan with ElevenLabs, and the assistant\'s Smart mode uses a Gemini or Anthropic key that you supply.'),
        ('Does it work on a phone and offline?',
         'Yes. Open it in Chrome, Edge or Safari and install it from the browser menu (on iPhone, Add to Home Screen). It then opens in its own window and still loads offline, and your data catches up when you are back online. Alarms ring only while the page is open, because a web page cannot wake a closed phone.'),
        ('Can it track the apps and websites I study with?',
         'Partly. A web page cannot see other apps or tabs. Abhyashify notes when you leave the Today screen for a study tool and when you come back. A Chrome and Edge extension counts time on the study sites you choose, and an Android companion app reads usage time for the study apps you choose. The Android companion is still experimental.'),
        ('Is it available in Hindi?',
         'Yes. The whole app, the assistant\'s replies and the voice chat can switch between English and Hindi (हिन्दी) in Settings. The Hindi comes from a built-in dictionary, so a few phrases may still appear in English.'),
        ('How does syncing work, and what happens to my data?',
         'Sign in with Google and your plan, materials and study logs sync through Google Firestore, so a phone and a laptop show the same data. If two devices record the same course at the same time, the overlap is counted once. A Smart-mode key is stored only on your device and is sent only to the provider you chose.'),
        ('Can I talk to it?',
         'Yes. The assistant is called Anu (Adi in the male voice). You can type or speak. It sets alarms and reminders, schedules tests and answers questions about the app. Speaking needs a browser with speech support, such as Chrome, Edge or Safari.'),
    ]


def howto_steps(lang):
    if lang == 'hi':
        return [('परीक्षा और पेपर चुनें', 'सूची से अपनी परीक्षा और उसका पेपर या ब्रांच चुनें। उसके विषय अपने आप भर जाते हैं। वैकल्पिक विषय हों तो अपना वाला चुनें।'),
                ('तारीख़ पक्की करें', 'परीक्षा की तारीख़, महीना या अपनी लक्ष्य-तारीख़ डालें। यह तारीख़ आधिकारिक सूचना से मिला लें।'),
                ('अनुमतियाँ और पढ़ाई के टूल बताएँ', 'एक बार में सूचनाओं, माइक्रोफ़ोन और स्टोरेज की अनुमति दें और बताएँ कि आप किन ऐप, वेबसाइट या YouTube चैनल से पढ़ते हैं।'),
                ('अपना समय बताएँ', 'बताएँ कि कौन-से समय और कितने घंटे आपको सूट करते हैं और कौन-से दिन छुट्टी हैं।'),
                ('टाइमटेबल देखें और चलाएँ', 'परीक्षा की तारीख़ तक का बना टाइमटेबल जैसा है वैसा चलाएँ या कोई भी ब्लॉक बदलें। फिर अलार्म बजते हैं और आप अपनी पढ़ाई दर्ज करते हैं।')]
    return [('Pick your exam and paper', 'Choose your exam and its paper or branch from the list. Its subjects load by themselves. If there are optional subjects, pick yours.'),
            ('Confirm the date', 'Enter your exam date, the month, or your own target date. Check it against the official notice.'),
            ('Give permissions and name your study tools', 'Allow notifications, microphone and storage in one go, and say which apps, websites or YouTube channels you study with.'),
            ('Say when you can study', 'Tell it which parts of the day and how many hours suit you, and which days are off.'),
            ('Review the timetable and follow it', 'Follow the timetable up to the exam date as it is, or edit any block. Alarms then ring and you log what you actually studied.')]


UI = {
    'en': {'home': 'Home', 'about': 'About', 'exams': 'Exam planners', 'open': 'Open the planner', 'other': 'Hindi (हिन्दी)',
           'faq': 'Questions and answers', 'how': 'How it works', 'foot': 'Abhyashify is an open-source study planner. Subjects and typical timings on these pages were written from general knowledge, so always check the exam body\'s own notice.',
           'src': 'Source code', 'skip': 'Skip to content'},
    'hi': {'home': 'होम', 'about': 'परिचय', 'exams': 'परीक्षा प्लानर', 'open': 'प्लानर खोलें', 'other': 'English',
           'faq': 'सवाल और जवाब', 'how': 'यह कैसे काम करता है', 'foot': 'अभ्यासिफ़ाई एक ओपन-सोर्स पढ़ाई का प्लानर है। इन पन्नों के विषय और आम समय सामान्य जानकारी से लिखे गए हैं, इसलिए परीक्षा करवाने वाली संस्था की अपनी सूचना ज़रूर देखें।',
           'src': 'सोर्स कोड', 'skip': 'सामग्री पर जाएँ'},
}


# ----------------------------------------------------------------------------------------------------------
# Page shell
# ----------------------------------------------------------------------------------------------------------
def rel(depth):
    return '../' * depth


def alt_links(en_url, hi_url):
    return ('<link rel="alternate" hreflang="en" href="%s">\n<link rel="alternate" hreflang="hi" href="%s">\n'
            '<link rel="alternate" hreflang="x-default" href="%s">' % (en_url, hi_url, en_url))


def jsonld(*objs):
    out = ''
    for o in objs:
        out += '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>\n'
    return out


def faq_ld(faq):
    return {'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}


def crumbs_ld(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}


def page(lang, depth, path, title, desc, body, en_url, hi_url, ld='', kind='website'):
    r = rel(depth)
    ui = UI[lang]
    me = hi_url if lang == 'hi' else en_url
    other = en_url if lang == 'hi' else hi_url
    home = BASE + ('hi/' if False else '')
    nav = ('<a href="%s">%s</a><a href="%sabout/">%s</a><a href="%sexams/">%s</a>' % (
        r + ('' if lang == 'en' else ''), ui['home'], r + ('hi/' if lang == 'hi' else ''), ui['about'],
        r + ('hi/' if lang == 'hi' else ''), ui['exams']))
    return ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<title>%s</title>\n<meta name="description" content="%s">\n<link rel="canonical" href="%s">\n'
            '%s\n<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">\n'
            '<meta name="theme-color" content="#F1F2EE">\n'
            '<meta property="og:type" content="%s">\n<meta property="og:site_name" content="%s">\n<meta property="og:title" content="%s">\n'
            '<meta property="og:description" content="%s">\n<meta property="og:url" content="%s">\n<meta property="og:locale" content="%s">\n'
            '<meta property="og:image" content="%sog.png">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            '<meta property="og:image:alt" content="%s">\n'
            '<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="%s">\n<meta name="twitter:description" content="%s">\n'
            '<meta name="twitter:image" content="%sog.png">\n'
            '<link rel="icon" href="%sicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="%sapple-touch-icon.png">\n'
            '<link rel="preload" href="%sfonts/archivo-wdth.woff2" as="font" type="font/woff2" crossorigin>\n'
            '<link rel="stylesheet" href="%spages.css">\n%s</head>\n<body>\n<a class="skip" href="#main">%s</a>\n'
            '<header class="top"><a class="brand" href="%s">%s</a><nav aria-label="Site">%s</nav>'
            '<a class="lang" href="%s" hreflang="%s" lang="%s">%s</a></header>\n<main id="main">\n%s\n</main>\n'
            '<footer><p>%s</p><p><a href="%s">%s</a> · <a href="%s">%s</a></p></footer>\n</body>\n</html>\n') % (
        lang, esc(title), esc(desc), me, alt_links(en_url, hi_url), kind, SITE, esc(title), esc(desc), me,
        'hi_IN' if lang == 'hi' else 'en_IN', BASE, esc(TITLE[lang]), esc(title), esc(desc), BASE, r, r, r, r, ld, ui['skip'],
        r, SITE, nav, other, 'en' if lang == 'hi' else 'hi', 'en' if lang == 'hi' else 'hi', ui['other'], body,
        esc(ui['foot']), BASE, ui['open'], REPO, ui['src'])


def faq_html(lang, faq):
    return '<section class="faq"><h2>%s</h2>%s</section>' % (
        UI[lang]['faq'], ''.join('<details open><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in faq))


def cta(lang):
    return '<p class="cta"><a class="btn" href="%s">%s</a></p>' % (BASE, UI[lang]['open'])


# ----------------------------------------------------------------------------------------------------------
# About
# ----------------------------------------------------------------------------------------------------------
def about_page(lang):
    faq = about_faq(lang)
    steps = howto_steps(lang)
    en_u, hi_u = url_of('en', 'about'), url_of('hi', 'about')
    me = url_of(lang, 'about')
    h1 = 'अभ्यासिफ़ाई: प्रतियोगी परीक्षाओं का पढ़ाई-प्लानर' if lang == 'hi' else 'Abhyashify: a study planner for competitive exams'
    lead = ('यह ब्राउज़र में चलने वाला प्लानर है। परीक्षा चुनें, और यह तारीख़ तक का रोज़ का टाइमटेबल बनाता है, अलार्म बजाता है और आपकी असल पढ़ाई का हिसाब रखता है।'
            if lang == 'hi' else
            'A planner that runs in the browser. Choose your exam and it builds a day-by-day timetable up to the date, rings an alarm for each block and keeps count of what you actually studied.')
    feats = ([('परीक्षा के हिसाब से सेटअप', '%d परीक्षा-परिवार, हर एक के पेपर, ब्रांच और विषय पहले से भरे। "अन्य" विकल्प हमेशा।' % len(EXAMS)),
              ('रोज़ का टाइमटेबल', 'तारीख़ तक विषयों का बँटवारा, रिवीज़न बफ़र और मॉक टेस्ट के साथ। हर ब्लॉक बदला जा सकता है।'),
              ('अलार्म और सूचनाएँ', 'हर ब्लॉक से थोड़ा पहले अलार्म, जब तक पेज खुला हो।'),
              ('पढ़ाई का हिसाब', 'टाइमर, हाथ से दर्ज करना और साप्ताहिक रिपोर्ट। कई डिवाइस पर एक ही समय एक बार गिना जाता है।'),
              ('पढ़ाई के टूल', 'ऐप, वेबसाइट और YouTube चैनल जिनसे आप पढ़ते हैं, Chrome/Edge एक्सटेंशन के साथ।'),
              ('हिन्दी और अंग्रेज़ी', 'पूरा ऐप, असिस्टेंट अनु/आदि और वॉइस चैट दोनों भाषाओं में।')]
             if lang == 'hi' else
             [('Exam-first setup', '%d exam families with papers, branches and subjects preloaded, plus an Other option.' % len(EXAMS)),
              ('Day-by-day timetable', 'Subjects spread to the exam date with a revision buffer and mock tests. Every block can be edited.'),
              ('Alarms', 'An alarm shortly before each block while the page is open.'),
              ('Study log', 'A timer, manual entries and a weekly report. Time from several devices is merged so it is counted once.'),
              ('Study tools', 'The apps, websites and YouTube channels you study with, with a Chrome and Edge extension.'),
              ('Hindi and English', 'The whole app, the assistant Anu/Adi and the voice chat work in both.')])
    body = ('<nav class="crumbs" aria-label="Breadcrumb"><a href="%s">%s</a> › %s</nav>\n<h1>%s</h1>\n<p class="lead">%s</p>\n%s\n'
            '<section><h2>%s</h2><ul class="feat">%s</ul></section>\n<section><h2>%s</h2><ol class="steps">%s</ol></section>\n%s\n<section><h2>%s</h2><ul class="exlist">%s</ul></section>\n%s') % (
        BASE, UI[lang]['home'], UI[lang]['about'], esc(h1), esc(lead), cta(lang),
        'क्या-क्या है' if lang == 'hi' else 'What it does',
        ''.join('<li><b>%s</b> %s</li>' % (esc(a), esc(b)) for a, b in feats),
        UI[lang]['how'], ''.join('<li><b>%s</b> %s</li>' % (esc(a), esc(b)) for a, b in steps),
        faq_html(lang, faq), UI[lang]['exams'],
        ''.join('<li><a href="%s">%s</a></li>' % (url_of(lang, 'exam', f['id']), esc(fname(f, lang))) for f in EXAMS), cta(lang))
    ld = jsonld(
        {'@context': 'https://schema.org', '@type': 'AboutPage', 'url': me, 'name': h1, 'inLanguage': lang, 'description': lead,
         'isPartOf': {'@id': BASE + '#website'}, 'about': {'@id': BASE + '#app'}},
        faq_ld(faq),
        {'@context': 'https://schema.org', '@type': 'HowTo', 'name': 'अभ्यासिफ़ाई में अपना टाइमटेबल कैसे बनाएँ' if lang == 'hi' else 'How to build your exam timetable in Abhyashify',
         'inLanguage': lang, 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': a, 'text': b} for i, (a, b) in enumerate(steps)]},
        crumbs_ld([(UI[lang]['home'], BASE), (UI[lang]['about'], me)]))
    t = ('अभ्यासिफ़ाई क्या है? परिचय, सवाल-जवाब और कैसे काम करता है' if lang == 'hi' else 'What is Abhyashify? How it works, features and FAQ')
    return page(lang, 1 if lang == 'en' else 2, 'about', t, DESC[lang], body, en_u, hi_u, ld)


# ----------------------------------------------------------------------------------------------------------
# Exam pages
# ----------------------------------------------------------------------------------------------------------
def variant_html(lang, f, v):
    name = L(lang, v['name'], v['hi'])
    when = L(lang, v['when'], WHEN_HI.get(v['when']))
    subs = ', '.join(L(lang, s['name'], s['hi']) for s in v['s'])
    hrs = v['hrs']
    h = '<article class="var"><h3>%s</h3><dl>' % esc(name)
    h += '<dt>%s</dt><dd>%s</dd>' % ('आम तौर पर कब' if lang == 'hi' else 'Usually held', esc(when))
    h += '<dt>%s</dt><dd>%s</dd>' % ('पहले से भरे विषय' if lang == 'hi' else 'Subjects loaded', esc(subs))
    for g in v['o']:
        q = L(lang, g['q'], g.get('qh'))
        opts = ', '.join(L(lang, s['name'], s['hi']) for s in g['l'])
        h += '<dt>%s</dt><dd>%s</dd>' % (esc(q), esc(opts))
    h += '<dt>%s</dt><dd>%s</dd>' % ('सुझाए गए घंटे' if lang == 'hi' else 'Suggested study hours',
                                       ('रोज़ %d से %d घंटे' % (hrs[0], hrs[1])) if lang == 'hi' else ('%d to %d hours a day' % (hrs[0], hrs[1])))
    h += '<dt>%s</dt><dd>%s</dd>' % ('मॉक टेस्ट की लंबाई' if lang == 'hi' else 'Mock test length',
                                       ('%d मिनट, %d अंक' % tuple(v['mk'])) if lang == 'hi' else ('%d minutes, %d marks' % tuple(v['mk'])))
    return h + '</dl></article>'


def exam_faq(lang, f):
    name = fname(f, lang)
    vs = f['v']
    vnames = ', '.join(L(lang, v['name'], v['hi']) for v in vs)
    whens = []
    for v in vs:
        w = L(lang, v['when'], WHEN_HI.get(v['when']))
        if w not in whens:
            whens.append(w)
    whentxt = ' '.join(whens[:2]) if len(vs) > 1 and len(whens) > 1 else whens[0]
    if lang == 'hi':
        return [
            ('अभ्यासिफ़ाई में %s के कौन-से पेपर शामिल हैं?' % name, 'ये शामिल हैं: %s। हर एक के विषय पहले से भरे हैं और आप उन्हें बदल सकते हैं।' % vnames),
            ('%s कब होती है?' % name, '%s यह सिर्फ़ संकेत है। अभ्यासिफ़ाई इसे असली तारीख़ नहीं मानता और आपसे अपनी परीक्षा की तारीख़ पक्की करवाता है, जो आधिकारिक सूचना से मिला लें।' % whentxt),
            ('क्या मैं %s के विषय बदल सकता हूँ?' % name, 'हाँ। विषय जोड़े, हटाए या बदले जा सकते हैं, और "अन्य" विकल्प से अपनी पसंद की परीक्षा भी बनाई जा सकती है। वैकल्पिक विषय हों तो सेटअप में आपसे अपना वाला पूछा जाता है।'),
        ]
    return [
        ('Which %s papers does Abhyashify cover?' % name, 'It covers: %s. Each one has its subjects preloaded, and you can change them.' % vnames),
        ('When is %s held?' % name, '%s This is only a hint. Abhyashify never treats it as the real date and asks you to confirm your own exam date against the official notice.' % whentxt),
        ('Can I change the %s subjects?' % name, 'Yes. You can add, remove or rename subjects, and the Other option lets you build an exam that is not in the list. If a paper has optional subjects, the setup asks which one is yours.'),
    ]


def exam_page(lang, f):
    name = fname(f, lang)
    desc_f = L(lang, f['d'], f['dh'])
    faq = exam_faq(lang, f)
    en_u, hi_u = url_of('en', 'exam', f['id']), url_of('hi', 'exam', f['id'])
    me = url_of(lang, 'exam', f['id'])
    if lang == 'hi':
        h1 = '%s का स्टडी प्लानर और टाइमटेबल' % name
        lead = '%s। अभ्यासिफ़ाई %s के विषय भर देता है, पूछता है कि परीक्षा कब है और आप कब पढ़ना चाहते हैं, फिर परीक्षा के दिन तक का रोज़ का टाइमटेबल बना देता है।' % (desc_f, name)
        subs = '%s के पेपर और विषय' % name
        how = 'टाइमटेबल कैसे बनता है'
        how_t = 'विषयों को उनके महत्त्व के हिसाब से परीक्षा की तारीख़ तक के दिनों में बाँटा जाता है। आपके चुने हुए घंटे, समय और छुट्टी के दिन माने जाते हैं, अंत में रिवीज़न का बफ़र और मॉक टेस्ट रखे जाते हैं, और हर ब्लॉक बदला जा सकता है।'
        note = 'ध्यान दें: विषय और आम महीने सामान्य जानकारी से लिखे गए हैं, आधिकारिक साइटों से नहीं। सिलेबस और तारीख़ परीक्षा करवाने वाली संस्था की सूचना में देखें।'
        more = 'दूसरी परीक्षाएँ'
        t = '%s स्टडी प्लानर और टाइमटेबल | अभ्यासिफ़ाई' % name
    else:
        h1 = '%s study planner and timetable' % name
        lead = '%s. Abhyashify loads the %s subjects, asks when your exam is and when you like to study, then builds a day-by-day timetable up to exam day.' % (desc_f, name)
        subs = '%s papers and subjects' % name
        how = 'How the timetable is built'
        how_t = 'Subjects are spread across the days up to the exam date, weighted by importance. Your hours, times of day and days off are respected, a revision buffer and mock tests are kept at the end, and every block can be edited.'
        note = 'Note: the subjects and usual months here were written from general knowledge, not downloaded from official sites. Check the syllabus and dates in the exam body\'s own notice.'
        more = 'Other exams'
        t = '%s study planner and timetable | Abhyashify' % name
    body = ('<nav class="crumbs" aria-label="Breadcrumb"><a href="%s">%s</a> › <a href="%s">%s</a> › %s</nav>\n<h1>%s</h1>\n<p class="lead">%s</p>\n%s\n'
            '<section><h2>%s</h2>%s</section>\n<section><h2>%s</h2><p>%s</p></section>\n<p class="note">%s</p>\n%s\n<section><h2>%s</h2><ul class="exlist">%s</ul></section>\n%s') % (
        BASE, UI[lang]['home'], url_of(lang, 'exams'), UI[lang]['exams'], esc(name), esc(h1), esc(lead), cta(lang),
        esc(subs), ''.join(variant_html(lang, f, v) for v in f['v']), how, esc(how_t), esc(note), faq_html(lang, faq), more,
        ''.join('<li><a href="%s">%s</a></li>' % (url_of(lang, 'exam', g['id']), esc(fname(g, lang))) for g in EXAMS if g['id'] != f['id']),
        cta(lang))
    ld = jsonld(
        {'@context': 'https://schema.org', '@type': 'WebPage', 'url': me, 'name': h1, 'inLanguage': lang, 'description': lead,
         'isPartOf': {'@id': BASE + '#website'}, 'about': {'@id': BASE + '#app'}},
        faq_ld(faq),
        crumbs_ld([(UI[lang]['home'], BASE), (UI[lang]['exams'], url_of(lang, 'exams')), (name, me)]))
    d = ('%s स्टडी प्लानर: पहले से भरे विषय, परीक्षा की तारीख़ तक का रोज़ का टाइमटेबल, अलार्म और साप्ताहिक रिपोर्ट।' % name if lang == 'hi'
         else '%s study planner: preloaded subjects, a day-by-day timetable to your exam date, alarms and weekly reports.' % name)
    return page(lang, 2 if lang == 'en' else 3, 'exam', t, d, body, en_u, hi_u, ld)


def exams_index(lang):
    en_u, hi_u = url_of('en', 'exams'), url_of('hi', 'exams')
    me = url_of(lang, 'exams')
    h1 = 'परीक्षा के हिसाब से स्टडी प्लानर' if lang == 'hi' else 'Study planners by exam'
    lead = ('हर परीक्षा के पेपर, ब्रांच और विषय पहले से भरे हैं। अपनी परीक्षा चुनें और अभ्यासिफ़ाई में टाइमटेबल बनाएँ।' if lang == 'hi'
            else 'Papers, branches and subjects are preloaded for each exam. Pick yours and build a timetable in Abhyashify.')
    items = ''.join('<li><a href="%s"><b>%s</b></a> <span>%s</span></li>' % (
        url_of(lang, 'exam', f['id']), esc(fname(f, lang)), esc(L(lang, f['d'], f['dh']))) for f in EXAMS)
    body = ('<nav class="crumbs" aria-label="Breadcrumb"><a href="%s">%s</a> › %s</nav>\n<h1>%s</h1>\n<p class="lead">%s</p>\n%s\n<ul class="exlist big">%s</ul>\n%s') % (
        BASE, UI[lang]['home'], UI[lang]['exams'], esc(h1), esc(lead), cta(lang), items, cta(lang))
    ld = jsonld(
        {'@context': 'https://schema.org', '@type': 'CollectionPage', 'url': me, 'name': h1, 'inLanguage': lang, 'description': lead,
         'isPartOf': {'@id': BASE + '#website'},
         'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': url_of(lang, 'exam', f['id']), 'name': fname(f, lang)} for i, f in enumerate(EXAMS)]}},
        crumbs_ld([(UI[lang]['home'], BASE), (UI[lang]['exams'], me)]))
    t = ('परीक्षा के हिसाब से स्टडी प्लानर: JEE, NEET, GATE | अभ्यासिफ़ाई' if lang == 'hi'
         else 'Study planners by exam: JEE, NEET, GATE, UPSC and more | Abhyashify')
    return page(lang, 1 if lang == 'en' else 2, 'exams', t, lead, body, en_u, hi_u, ld)


# ----------------------------------------------------------------------------------------------------------
# index.html pieces
# ----------------------------------------------------------------------------------------------------------
def index_head():
    app = {'@context': 'https://schema.org', '@type': 'WebApplication', '@id': BASE + '#app', 'name': SITE, 'url': BASE,
           'description': DESC['en'], 'applicationCategory': 'EducationalApplication', 'operatingSystem': 'Any (web browser; installable as an app)',
           'browserRequirements': 'Requires JavaScript. Works in current Chrome, Edge and Safari.', 'inLanguage': ['en', 'hi'],
           'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'INR'},
           'image': BASE + 'og.png', 'screenshot': BASE + 'og.png', 'codeRepository': REPO, 'license': None,
           'audience': {'@type': 'EducationalAudience', 'educationalRole': 'student'},
           'featureList': ['Preloaded subjects for %d exam families' % len(EXAMS), 'Day-by-day timetable up to the exam date', 'Alarms before each study block',
                           'Study timer, manual log and weekly report', 'Time from several devices merged so it is counted once',
                           'Study-site tracking with a Chrome and Edge extension', 'English and Hindi assistant with voice chat'],
           'author': {'@type': 'Person', 'name': 'Aditya', 'url': AUTHOR_URL}, 'sameAs': [REPO]}
    app.pop('license')
    site = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '#website', 'name': SITE, 'url': BASE,
            'inLanguage': ['en', 'hi'], 'description': DESC['en'], 'publisher': {'@type': 'Person', 'name': 'Aditya', 'url': AUTHOR_URL}}
    return ('<meta name="description" content="%s">\n<link rel="canonical" href="%s">\n'
            '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">\n<meta name="author" content="Aditya">\n'
            '<meta property="og:type" content="website">\n<meta property="og:site_name" content="%s">\n<meta property="og:title" content="%s">\n'
            '<meta property="og:description" content="%s">\n<meta property="og:url" content="%s">\n<meta property="og:locale" content="en_IN">\n'
            '<meta property="og:locale:alternate" content="hi_IN">\n<meta property="og:image" content="%sog.png">\n'
            '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            '<meta property="og:image:alt" content="%s">\n<meta name="twitter:card" content="summary_large_image">\n'
            '<meta name="twitter:title" content="%s">\n<meta name="twitter:description" content="%s">\n<meta name="twitter:image" content="%sog.png">\n'
            '%s') % (esc(DESC['en']), BASE,
                     SITE, esc(TITLE['en']), esc(DESC['en']), BASE, BASE,
                     esc('Abhyashify: a two-colour print-style study planner with a day-by-day exam timetable'),
                     esc(TITLE['en']), esc(DESC['en']), BASE, jsonld(site, app))


def index_noscript():
    """Plain HTML a crawler or a no-JavaScript visitor can read. Replaced by nothing: the app itself needs JavaScript."""
    faq = about_faq('en')[:4]
    return ('<noscript><div style="max-width:42rem;margin:0 auto;padding:24px 16px;font:16px/1.6 system-ui,sans-serif;color:#121646">'
            '<h1>Abhyashify: exam study planner</h1><p>%s</p><p>This app needs JavaScript. Without it you can still read about it:</p>'
            '<ul><li><a href="about/">About Abhyashify, how it works and FAQ</a></li><li><a href="exams/">Study planners by exam (JEE, NEET, GATE, UPSC and more)</a></li>'
            '<li><a href="hi/about/">हिन्दी में जानकारी</a></li></ul>%s</div></noscript>') % (
        esc(DESC['en']), ''.join('<h2>%s</h2><p>%s</p>' % (esc(q), esc(a)) for q, a in faq))


# ----------------------------------------------------------------------------------------------------------
# Text files
# ----------------------------------------------------------------------------------------------------------
def sitemap():
    urls = []

    def u(kind, fid=None):
        e, h = url_of('en', kind, fid), url_of('hi', kind, fid)
        for loc in (e, h):
            urls.append('<url><loc>%s</loc><lastmod>%s</lastmod><xhtml:link rel="alternate" hreflang="en" href="%s"/>'
                        '<xhtml:link rel="alternate" hreflang="hi" href="%s"/><xhtml:link rel="alternate" hreflang="x-default" href="%s"/></url>' % (loc, TODAY, e, h, e))
    urls.append('<url><loc>%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>' % (BASE, TODAY))
    u('about')
    u('exams')
    for f in EXAMS:
        u('exam', f['id'])
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(urls) + '\n</urlset>\n')


def robots():
    bots = ['Googlebot', 'Bingbot', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot',
            'Google-Extended', 'Applebot', 'Applebot-Extended', 'CCBot']
    return ('# Abhyashify welcomes search engines and AI answer engines. Nothing here is private: accounts and study data live behind sign-in.\n'
            'User-agent: *\nAllow: /\n\n' + ''.join('User-agent: %s\nAllow: /\n\n' % b for b in bots) + 'Sitemap: %ssitemap.xml\n' % BASE)


def llms():
    s = '# Abhyashify\n\n> %s\n\n' % DESC['en']
    s += ('Abhyashify is a free, open-source study planner for competitive exams (%s). It runs in the browser, installs like an app, and works in English and Hindi. '
          'Subjects and typical timings were written from general knowledge, not taken from official sites, so users must confirm exam dates and syllabus with the exam body.\n\n') % fam_list('en')
    s += '## Main pages\n\n- [Abhyashify app](%s): the planner itself (needs JavaScript)\n' % BASE
    s += '- [About, how it works and FAQ](%s): what it does, the setup steps and answers to common questions\n' % url_of('en', 'about')
    s += '- [Study planners by exam](%s): every exam family and paper with its preloaded subjects\n' % url_of('en', 'exams')
    s += '- [हिन्दी में जानकारी](%s): the same information in Hindi\n- [Source code and README](%s)\n\n## Exam pages\n\n' % (url_of('hi', 'about'), REPO)
    for f in EXAMS:
        s += '- [%s](%s): %s\n' % (f['name'], url_of('en', 'exam', f['id']), f['d'])
    s += '\n## Optional\n\n- [Full text of these pages](%sllms-full.txt)\n' % BASE
    return s


def llms_full():
    s = '# Abhyashify\n\n%s\n\nSource: %s\n\n## FAQ\n\n' % (DESC['en'], url_of('en', 'about'))
    for q, a in about_faq('en'):
        s += '### %s\n\n%s\n\n' % (q, a)
    s += '## How to build a timetable\n\n'
    for i, (a, b) in enumerate(howto_steps('en')):
        s += '%d. %s: %s\n' % (i + 1, a, b)
    s += '\n## Exams and preloaded subjects\n\nTimings are typical, not official. Always check the exam body\'s notice.\n\n'
    for f in EXAMS:
        s += '### %s (%s)\n\n%s\n\n' % (f['name'], url_of('en', 'exam', f['id']), f['d'])
        for v in f['v']:
            s += '- %s. Usually: %s Subjects: %s.\n' % (v['name'], v['when'], '; '.join(x['name'] for x in v['s']))
            for g in v['o']:
                s += '  - %s %s\n' % (g['q'], '; '.join(x['name'] for x in g['l']))
        s += '\n'
    return s


NOT_FOUND = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
             '<title>Page not found | Abhyashify</title><meta name="robots" content="noindex"><base href="%s">'
             '<link rel="stylesheet" href="pages.css"></head><body><header class="top"><a class="brand" href="./">Abhyashify</a></header>'
             '<main><h1>That page is not here</h1><p class="lead">Try the planner, or browse the exam pages.</p>'
             '<p class="cta"><a class="btn" href="./">Open the planner</a> <a class="btn ghost" href="exams/">Exam planners</a></p></main></body></html>') % BASE

CSS = """@font-face{font-family:Archivo;src:url(fonts/archivo-wdth.woff2) format('woff2');font-weight:100 900;font-stretch:62% 125%;font-display:swap}
@font-face{font-family:Atkinson;src:url(fonts/atkinson-400.woff2) format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:Atkinson;src:url(fonts/atkinson-600.woff2) format('woff2');font-weight:600;font-display:swap}
@font-face{font-family:Atkinson;src:url(fonts/atkinson-700.woff2) format('woff2');font-weight:700;font-display:swap}
@font-face{font-family:Deva;src:url(fonts/devanagari-wght.woff2) format('woff2');font-weight:100 900;font-display:swap;unicode-range:U+0900-097F,U+1CD0-1CF9,U+200C-200D,U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FF}
:root{--bg:#F1F2EE;--ink:#121646;--blue:#1F2A9C;--accent:#BE1263;--hl:#FFE53B;--rule:rgba(18,22,70,.22);--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#10143A;--ink:#F1F0FF;--blue:#A3B1FF;--accent:#FF63B0;--hl:#FFE53B;--rule:rgba(241,240,255,.25);--card:#171C4D}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:400 1.0625rem/1.65 Atkinson,Deva,system-ui,sans-serif}
a{color:var(--blue);text-underline-offset:3px}a:hover{color:var(--accent)}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:var(--hl);color:#121646;padding:8px 12px;z-index:9}
.top{display:flex;flex-wrap:wrap;align-items:center;gap:8px 20px;padding:14px max(16px,env(safe-area-inset-left));border-bottom:2px solid var(--ink)}
.brand{font:800 1.35rem/1 Archivo,Deva,sans-serif;font-stretch:112%;color:var(--ink);text-decoration:none;letter-spacing:-.01em}
.top nav{display:flex;gap:4px 18px;flex-wrap:wrap;margin-left:auto}.top nav a,.lang{color:var(--ink);font-weight:600;text-decoration:none;padding:10px 2px;min-height:44px;display:inline-flex;align-items:center}
.top a:hover{color:var(--accent)}.lang{border:2px solid var(--ink);padding:0 12px;border-radius:99px}
main{max-width:46rem;margin:0 auto;padding:28px 16px 56px}
h1{font:800 clamp(1.9rem,6.5vw,3rem)/1.08 Archivo,Deva,sans-serif;font-stretch:108%;letter-spacing:-.02em;margin:.4em 0 .3em;text-wrap:balance}
h2{font:800 1.45rem/1.2 Archivo,Deva,sans-serif;margin:2em 0 .6em;padding-top:.6em;border-top:2px solid var(--ink)}
h3{font:700 1.15rem/1.3 Atkinson,Deva,sans-serif;margin:0 0 .4em}
.lead{font-size:1.2rem;max-width:38rem}.crumbs{font-size:.95rem}.crumbs a{color:var(--ink)}
.btn{display:inline-flex;align-items:center;min-height:48px;padding:0 22px;border-radius:99px;background:var(--blue);color:#fff;font-weight:700;text-decoration:none;box-shadow:4px 4px 0 var(--accent)}
.btn:hover{color:#fff;transform:translate(-1px,-1px)}.btn.ghost{background:transparent;color:var(--ink);border:2px solid var(--ink);box-shadow:none}
@media (prefers-color-scheme:dark){.btn{background:#2A38D6}}
.cta{margin:1.4em 0}
.var{background:var(--card);border:2px solid var(--ink);border-radius:14px;padding:16px 18px;margin:0 0 14px}
dl{margin:0}dt{font-weight:700;margin-top:.7em;font-size:.95rem;text-transform:none}dd{margin:.1em 0 0}
details{border-bottom:1px solid var(--rule);padding:.2em 0}summary{cursor:pointer;font-weight:700;padding:12px 0;min-height:44px}details p{margin:0 0 1em}
ul.feat,ol.steps{padding-left:1.2em}ul.feat li,ol.steps li{margin:.5em 0}
ul.exlist{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px}ul.exlist li a{display:inline-block;padding:8px 14px;border:2px solid var(--ink);border-radius:99px;text-decoration:none;color:var(--ink);font-weight:600;min-height:44px}
ul.exlist li a:hover{background:var(--hl);color:#121646}
ul.exlist.big{display:grid;gap:10px}ul.exlist.big li{display:flex;flex-direction:column;border-bottom:1px solid var(--rule);padding:8px 0}ul.exlist.big li a{border:0;padding:0;font-size:1.2rem;border-radius:0;min-height:0}
.note{background:var(--hl);color:#121646;padding:12px 16px;border-radius:10px;font-weight:600}
@media (max-width:600px){.lang{margin-left:auto}.top nav{order:3;width:100%;margin:0}}
footer{max-width:46rem;margin:0 auto;padding:20px 16px 40px;border-top:2px solid var(--ink);font-size:.95rem}footer a{color:var(--ink)}
:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def write_site(out):
    def w(rel_path, text):
        p = os.path.join(out, rel_path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(text)
    for lang in ('en', 'hi'):
        pre = 'hi/' if lang == 'hi' else ''
        w(pre + 'about/index.html', about_page(lang))
        w(pre + 'exams/index.html', exams_index(lang))
        for f in EXAMS:
            w(pre + 'exams/%s/index.html' % f['id'], exam_page(lang, f))
    w('sitemap.xml', sitemap())
    w('robots.txt', robots())
    w('llms.txt', llms())
    w('llms-full.txt', llms_full())
    w('404.html', NOT_FOUND)
    w('pages.css', CSS)
    return 2 * (2 + len(EXAMS)) + 6


if __name__ == '__main__':
    print(write_site(os.path.join(here, '..', 'docs')), 'files')
