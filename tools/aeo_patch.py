# aeo_patch.py v0.1 (2026-11-12) — AEO 第一層：/faq/ 頁、課程頁問答、結構化資料、robots、llms.txt
# 用法：python3 tools/aeo_patch.py <站台根目錄>   （build.py 結尾會自動對 tools/out 跑一次）
# 可重跑：所有插入都包在 <!-- aeo:* --> 標記裡，重跑先拆再裝。
# 問答原文的唯一來源是 /quiz/index.html「你可能想問」那七題；這裡只取用，不改寫。
import sys, re, json, html, pathlib

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
SITE = 'https://propelaigrowth.com'
ORG_ID = SITE + '/#org'

def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')

def strip_marked(s, tag):
    return re.sub(r'\n?[ \t]*<!-- aeo:%s -->.*?<!-- /aeo:%s -->\n?' % (tag, tag), '\n', s, flags=re.S)

def text(h):  # html → plain
    return html.unescape(re.sub(r'<[^>]+>', '', h)).strip()

# ---------- 1. 七題原文（從小測驗頁取） ----------
quiz = rd('quiz/index.html')
blk = quiz[quiz.index('你可能想問'):]
blk = blk[:blk.index('</div>')]
QA = re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', blk, flags=re.S)
assert len(QA) == 7, f'小測驗問答應為 7 題，讀到 {len(QA)} 題'
def pick(kw):
    hit = [qa for qa in QA if kw in qa[0]]
    assert len(hit) == 1, kw
    return hit[0]
Q_DIFF, Q_BUDGET, Q_TIME, Q_DESIGN, Q_BE, Q_AI, Q_HOW = (pick(k) for k in ['差別在哪', '預算', '多久', '被設計', '行為經濟學是什麼', '跟 AI', '課怎麼上'])

# 兩題新寫（文字取自關於頁導言與各課程頁的說明；v0.1 待 George 核）
Q_WHAT = ('Propel AI 是做什麼的？',
          'Propel AI（啟進智能決策）透過課程與工作坊，教團隊運用行為經濟學和 AI，找出客戶不往下談、同仁沒有行動的原因，再調整流程、訊息與做決定的環境。'
          '常見的題目有三種：提案做了，客戶卻遲遲沒有下一步；AI 工具買了，團隊卻沒有用起來；SOP 寫清楚了，現場還是照舊。')
Q_COURSES = ('有哪些課？從哪一個開始？',
             '四種。<a href="/trial/">59 分鐘試駕</a>：到你公司上，每場 NT$8,900（未稅），上限 30 人。'
             '<a href="/half-day/">半天課・全天課</a>：用你本來就在做的決定當題目，半天六題、全天十二題。'
             '<a href="/workshop/">全天工作坊</a>：帶一個推不動的痛點來，走五站，當場拍板一個小試驗，每場上限 16 人。'
             '<a href="/surf/">SURF™ 原廠班</a>：歐洲 MINDWORX 的方法，主題是怎麼讓客戶說 YES。'
             '還不確定的話，先做<a href="/quiz/">兩分鐘小測驗</a>，或從 59 分鐘試駕開始。')

GROUPS = [
    ('關於 Propel AI', [Q_WHAT, Q_BE, Q_AI]),
    ('這套做法', [Q_DIFF, Q_DESIGN]),
    ('費用與時間', [Q_BUDGET, Q_TIME]),
    ('上課', [Q_HOW, Q_COURSES]),
]

def ld(obj):
    return '<!-- aeo:ld --><script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script><!-- /aeo:ld -->'

def put_ld(s, obj):
    s = strip_marked(s, 'ld')
    return s.replace('</head>', ld(obj) + '\n</head>', 1)

# ---------- 2. /faq/ 頁（外框借關於頁） ----------
tpl = strip_marked(strip_marked(rd('about/index.html'), 'ld'), 'foot')
head, rest = tpl[:tpl.index('<main>') + 6], tpl[tpl.index('</main>'):]
T_FAQ = '常見問題｜Propel AI 啟進智能決策'
D_FAQ = 'Propel AI 是做什麼的、跟再講一遍和給獎勵差在哪、要花多少預算、多久看得到變化、課怎麼上：九個問題，直接回答。'
head = re.sub(r'<title>.*?</title>', f'<title>{T_FAQ}</title>', head)
head = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + D_FAQ, head)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + T_FAQ, head)
head = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + D_FAQ, head)
head = head.replace(f'{SITE}/about/', f'{SITE}/faq/')
head = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', head)   # 目前沒有英文版問答
head = head.replace('class="pg-about"', 'class="pg-faq"').replace(' aria-current="page"', '')
body = ['\n    <h1>常見問題</h1>',
        '    <p class="lead">你可能想問的幾件事，直接回答。找不到要的答案，<a href="/contact/">寫信給我們</a>。</p>']
for g, qs in GROUPS:
    body.append(f'    <h2>{g}</h2>\n    <div class="faqp">')
    for q, a in qs:
        body.append(f'      <section><h3>{q}</h3><p>{a}</p></section>')
    body.append('    </div>')
body.append('    <div class="cta">\n      <a class="btn primary" href="/quiz/">還不確定？先做兩分鐘小測驗</a>\n      <a class="btn secondary" href="/contact/">已經有題目：留下一件事</a>\n    </div>')
body.append('    <div class="nav"><a href="/" class="prev">← 回首頁</a><a href="/how/">我們怎麼看問題 →</a></div>\n')
faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': SITE + '/faq/#faq', 'inLanguage': 'zh-Hant',
          'mainEntity': [{'@type': 'Question', 'name': text(q), 'acceptedAnswer': {'@type': 'Answer', 'text': text(a)}} for _, qs in GROUPS for q, a in qs]}
wr('faq/index.html', put_ld(head + '\n'.join(body) + rest, faq_ld))

# ---------- 3. 課程頁與「怎麼看問題」頁：相關的兩三題 ----------
def block(qs):
    items = ''.join(f'\n      <details><summary>{q}</summary><p>{a}</p></details>' for q, a in qs)
    return ('    <!-- aeo:faq -->\n    <h2>你可能想問</h2>\n    <div class="faqb">' + items +
            '\n    </div>\n    <p><a class="more" href="/faq/">其他常見問題 →</a></p>\n    <!-- /aeo:faq -->\n')
PLACE = {  # 頁面：(題目, 插在哪個標記之前)
    'trial/index.html':    ([Q_BUDGET, Q_HOW],                 '      <div class="nav">'),
    'half-day/index.html': ([Q_BUDGET, Q_TIME],                '      <div class="nav">'),
    'workshop/index.html': ([Q_TIME, Q_HOW],                   '      <div class="nav">'),
    'how/index.html':      ([Q_DIFF, Q_DESIGN, Q_BE, Q_AI],    '    <div class="cta">'),
}
for p, (qs, anchor) in PLACE.items():
    s = strip_marked(rd(p), 'faq')
    assert s.count(anchor) == 1, (p, anchor, s.count(anchor))
    wr(p, s.replace(anchor, block(qs) + anchor, 1))

# ---------- 4. 結構化資料 ----------
ORG = {'@type': 'Organization', '@id': ORG_ID, 'name': 'Propel AI', 'legalName': '啟進智能決策有限公司',
       'alternateName': ['Propel AI 啟進智能決策', '啟進智能決策'], 'url': SITE + '/', 'logo': SITE + '/assets/og.png',
       'email': 'george.chen@propelaigrowth.com', 'taxID': '61933866', 'sameAs': ['https://www.linkedin.com/company/propelaigrowth/'],
       'description': 'Propel AI 啟進智能決策：把行為經濟學的研究發現，轉成企業團隊能在工作上練習的步驟，再用實際數字觀察效果。',
       'address': {'@type': 'PostalAddress', 'streetAddress': '忠孝東路五段 1-2 號 12 樓', 'addressLocality': '台北市', 'addressCountry': 'TW'},
       'areaServed': 'TW', 'knowsAbout': ['行為經濟學', '行為設計', '企業培訓', 'AI 導入'],
       'founder': {'@type': 'Person', 'name': 'George Chen', 'alternateName': '陳朝智', 'jobTitle': '創辦人・行為設計師',
                   'sameAs': 'https://www.linkedin.com/in/propelai'}}
for p, lang in [('index.html', 'zh-Hant'), ('en/index.html', 'en')]:
    site = {'@type': 'WebSite', '@id': SITE + '/#site', 'url': SITE + '/', 'name': 'Propel AI 啟進智能決策', 'inLanguage': ['zh-Hant', 'en'], 'publisher': {'@id': ORG_ID}}
    wr(p, put_ld(rd(p), {'@context': 'https://schema.org', '@graph': [ORG, site]}))
wr('about/index.html', put_ld(rd('about/index.html'), {'@context': 'https://schema.org', '@type': 'AboutPage', 'url': SITE + '/about/', 'inLanguage': 'zh-Hant', 'about': {'@id': ORG_ID}, 'mainEntity': ORG}))

def meta_desc(s): return html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
COURSES = {'trial/index.html': ('59 分鐘試駕', '/trial/', 'PT59M'), 'half-day/index.html': ('半天課・全天課', '/half-day/', None),
           'workshop/index.html': ('全天工作坊', '/workshop/', 'PT6H'), 'surf/index.html': ('SURF™ 原廠班', '/surf/', None)}
for p, (name, u, load) in COURSES.items():
    s = rd(p)
    inst = {'@type': 'CourseInstance', 'courseMode': 'Onsite', 'inLanguage': 'zh-Hant', 'instructor': {'@type': 'Person', 'name': 'George Chen'}}
    if load: inst['courseWorkload'] = load
    c = {'@context': 'https://schema.org', '@type': 'Course', '@id': SITE + u + '#course', 'name': name, 'description': meta_desc(s), 'url': SITE + u,
         'inLanguage': 'zh-Hant', 'provider': {'@type': 'Organization', '@id': ORG_ID, 'name': 'Propel AI 啟進智能決策', 'url': SITE + '/'},
         'audience': {'@type': 'Audience', 'audienceType': '企業團隊、主管與決策者'}, 'hasCourseInstance': inst}
    if p.startswith('trial'):   # 只有試駕價格是全公開的（價格方案 B）
        c['offers'] = {'@type': 'Offer', 'price': '8900', 'priceCurrency': 'TWD', 'category': '企業包班（每場，未稅）', 'url': SITE + u}
    wr(p, put_ld(s, c))

# ---------- 5. 樣式 ----------
CSS = '''
/* aeo:css */
.faqb details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:0 14px;margin-top:8px}
.faqb summary{cursor:pointer;font-weight:700;color:var(--navy-text);padding:11px 0;list-style:none;display:flex;gap:10px;align-items:baseline}
.faqb summary::-webkit-details-marker{display:none}
.faqb summary::before{content:"＋";color:var(--orange);font-weight:900;flex:none}
.faqb details[open] summary::before{content:"－"}
.faqb details p{padding-bottom:12px;font-size:15px;margin:0}
.faqp section{padding:14px 0;border-bottom:1px solid var(--line)}
.faqp section:last-child{border-bottom:0}
.faqp h3{font-size:17px;line-height:1.5;color:var(--navy-text);margin:0 0 6px;text-wrap:balance}
.faqp p{margin:0;font-size:16px;line-height:1.8}
.sitefoot .flinks{margin-top:6px}
/* /aeo:css */
'''
css = re.sub(r'\n/\* aeo:css \*/.*?/\* /aeo:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

# ---------- 6. 頁尾連結（中文頁） ----------
FOOT_LINK = '<!-- aeo:foot --><div class="flinks"><a href="/faq/">常見問題</a>｜<a href="/quiz/">兩分鐘小測驗</a>｜<a href="/contact/">聯絡</a></div><!-- /aeo:foot -->'
for f in ROOT.rglob('index.html'):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith(('en/', 'tools/')): continue
    s = f.read_text(encoding='utf-8')
    if '<footer class="sitefoot">' not in s: continue
    s = strip_marked(s, 'foot')
    f.write_text(s.replace('    <div class="disc">', '    ' + FOOT_LINK + '\n    <div class="disc">', 1), encoding='utf-8')

# ---------- 7. robots、sitemap、llms.txt ----------
BOTS = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User',
        'Google-Extended', 'Applebot-Extended', 'Bingbot', 'CCBot']
wr('robots.txt', 'User-agent: *\nAllow: /\n\n# AI 搜尋與助理：歡迎讀取與引用\n' + ''.join(f'User-agent: {b}\n' for b in BOTS) + f'Allow: /\n\nSitemap: {SITE}/sitemap.xml\n')
sm = rd('sitemap.xml')
if f'{SITE}/faq/' not in sm:
    sm = sm.replace(f'  <url><loc>{SITE}/about/</loc></url>\n', f'  <url><loc>{SITE}/faq/</loc></url>\n  <url><loc>{SITE}/about/</loc></url>\n')
    wr('sitemap.xml', sm)
LL = ['# Propel AI 啟進智能決策', '',
      '> ' + text(Q_WHAT[1]), '',
      '公司：啟進智能決策有限公司（Propel AI），台北。創辦人 George Chen 親自授課；歐洲 MINDWORX SURF™ Method 授權講師與教練。',
      '核心想法：數字是結果，可以動手的是行為；先改做決定當下的環境，不急著加預算。', '',
      '## 常見問題（直接回答）', '']
for _, qs in GROUPS:
    for q, a in qs: LL += [f'### {text(q)}', text(a), '']
LL += ['## 主要頁面', '',
       f'- [常見問題]({SITE}/faq/)：九個問題的完整回答',
       f'- [我們怎麼看問題]({SITE}/how/)：環境→行為→指標，三個改環境的例子',
       f'- [59 分鐘試駕]({SITE}/trial/)：到你公司上，每場 NT$8,900（未稅），上限 30 人',
       f'- [半天課・全天課]({SITE}/half-day/)：半天六題、全天十二題，題目用痛點命名',
       f'- [全天工作坊]({SITE}/workshop/)：帶一個推不動的痛點來，走五站，拍板一個小試驗',
       f'- [SURF™ 原廠班]({SITE}/surf/)：怎麼讓客戶說 YES，MINDWORX 原廠課程',
       f'- [兩分鐘小測驗]({SITE}/quiz/)：三題，看那件推不動的事能不能用這個方法',
       f'- [關於 Propel AI]({SITE}/about/)',
       f'- [聯絡]({SITE}/contact/)：george.chen@propelaigrowth.com',
       f'- [English]({SITE}/en/)', '']
wr('llms.txt', '\n'.join(LL))
print('aeo_patch: /faq/ 9 題；課程頁問答', len(PLACE), '頁；結構化資料', 3 + len(COURSES) + 1, '頁；robots、sitemap、llms.txt 已更新')
