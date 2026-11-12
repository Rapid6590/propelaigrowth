# pain_pages.py v0.1 (2026-11-12) — AEO 第二層：痛點句問答頁 /q/<slug>/ ＋ 索引 /q/
# 用法：python3 tools/pain_pages.py <站台根目錄>   （資料在 tools/data/pain_pages.json；可重跑）
# 每頁：標題＝痛點句、開頭直接回答、三格原因、改法示意、一個有出處的研究、一件小事、問答、相關頁；Article＋FAQPage JSON-LD。
import sys, re, json, html, pathlib, datetime

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
SITE = 'https://propelaigrowth.com'
ORG_ID = SITE + '/#org'
DATA = json.loads((pathlib.Path(__file__).parent / 'data' / 'pain_pages.json').read_text(encoding='utf-8'))
PLANNED = ['SOP 寫清楚了，為什麼現場還是照舊？', '民眾為什麼不來辦、不配合？', '價格怎麼開、怎麼談，客戶才不會只比便宜？',
           '送樣了，然後為什麼就沒下文？', '新人來了，為什麼沒人帶？', '加了購物車，為什麼沒結帳？']

def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')
def esc(s): return html.escape(s, quote=True)
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'

# 外框借關於頁（去掉它的 JSON-LD 與 hreflang）
tpl = rd('about/index.html')
tpl = re.sub(r'<!-- aeo:ld -->.*?<!-- /aeo:ld -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', tpl)
HEAD, REST = tpl[:tpl.index('<main>') + 6], tpl[tpl.index('</main>'):]

def shell(url, title, desc, body, extra_ld):
    h = HEAD
    h = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}｜Propel AI 啟進智能決策</title>', h)
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title) + '｜Propel AI', h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
    h = h.replace(f'{SITE}/about/', SITE + url).replace('class="pg-about"', 'class="pg-q"').replace(' aria-current="page"', '')
    h = h.replace('</head>', extra_ld + '\n</head>', 1)
    return h + body + REST

CSS = '''
/* q:css */
.q-ans{background:var(--sky);border-left:4px solid var(--orange);border-radius:10px;padding:14px 16px;font-size:17px;line-height:1.8;margin:0 0 22px}
.q-cause{display:grid;gap:10px;margin:0 0 18px}
.q-cause .card b{display:block;color:var(--orange);font-size:13px;letter-spacing:.08em;margin-bottom:4px}
.q-cause .card p{margin:0;font-size:15px;line-height:1.7}
.q-step{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 18px}
.q-step b{display:block;margin-bottom:4px}
.q-rel a{display:block;padding:10px 0;border-bottom:1px solid var(--line);text-decoration:none;color:var(--navy-text);font-weight:700}
.q-rel a:last-child{border-bottom:0}
.q-byline{font-size:13px;color:var(--mute);margin:0 0 18px}
.q-list .choice.soon{opacity:.55}
/* /q:css */
'''
css = re.sub(r'\n/\* q:css \*/.*?/\* /q:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

for a in DATA:
    url = f"/q/{a['slug']}/"
    causes = ''.join(f'<div class="card"><b>{esc(k)}</b><p>{esc(v)}</p></div>' for k, v in a['causes'])
    ex = ''.join(f'<div class="card{" us" if i == 2 else ""}"><h3>{esc(t)}</h3><p>{esc(q)}</p><p class="note">{esc(n)}</p></div>' for i, (t, q, n) in enumerate(a['example']))
    faq = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>' for q, ans in a['faq'])
    rel = ''.join(f'<a href="{u}">{esc(t)} →</a>' for u, t in a['related'])
    body = f'''
    <span class="pill">常見卡點</span>
    <h1>{esc(a['pain'])}</h1>
    <p class="q-byline">George Chen 陳朝智・行為設計師｜{a['date']}</p>
    <p class="q-ans">{esc(a['answer'])}</p>
    <h2>常見的三個原因</h2>
    <p>{esc(a['causes_intro'])}</p>
    <div class="q-cause">{causes}</div>
    <h2>{esc(a['example_title'])}</h2>
    <div class="vs three">{ex}</div>
    <p class="note">示意，非客戶實績。</p>
    <h2>{esc(a['research_title'])}</h2>
    <p>{esc(a['research'])}</p>
    <p class="note">出處：{esc(a['research_src'])}｜{esc(a['research_note'])}</p>
    <h2>{esc(a['small_step_title'])}</h2>
    <div class="q-step"><p>{esc(a['small_step'])}</p></div>
    <h2>你可能想問</h2>
    <div class="faqb">{faq}</div>
    <p><a class="more" href="/faq/">其他常見問題 →</a></p>
    <h2>接下來可以看</h2>
    <div class="q-rel">{rel}</div>
    <div class="cta">
      <a class="btn primary" href="/quiz/">還不確定？先做兩分鐘小測驗</a>
      <a class="btn secondary" href="/contact/">已經有題目：留下一件事</a>
    </div>
    <div class="nav"><a href="/q/" class="prev">← 所有常見卡點</a><a href="/">回首頁 ⌂</a></div>
'''
    art = {'@type': 'Article', '@id': SITE + url + '#article', 'headline': a['pain'], 'description': a['desc'], 'inLanguage': 'zh-Hant',
           'datePublished': a['date'], 'dateModified': a['date'], 'url': SITE + url, 'mainEntityOfPage': SITE + url,
           'author': {'@type': 'Person', 'name': 'George Chen', 'alternateName': '陳朝智', 'jobTitle': '創辦人・行為設計師', 'url': SITE + '/about/'},
           'publisher': {'@id': ORG_ID}, 'about': a['short']}
    fq = {'@type': 'FAQPage', '@id': SITE + url + '#faq', 'inLanguage': 'zh-Hant',
          'mainEntity': [{'@type': 'Question', 'name': a['pain'], 'acceptedAnswer': {'@type': 'Answer', 'text': a['answer']}}] +
                        [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': ans}} for q, ans in a['faq']]}
    wr(url.lstrip('/') + 'index.html', shell(url, a['pain'], a['desc'], body, ld({'@context': 'https://schema.org', '@graph': [art, fq]})))

# 索引頁
items = ''.join(f'<a class="choice" href="/q/{a["slug"]}/"><span><span class="q">{esc(a["pain"])}</span><span class="a">{esc(a["answer"][:38])}…</span></span><span class="go">→</span></a>' for a in DATA)
items += ''.join(f'<span class="choice soon"><span><span class="q">{esc(t)}</span><span class="a">整理中</span></span></span>' for t in PLANNED)
idx = f'''
    <span class="pill">常見卡點</span>
    <h1>推了很久，卻還是沒發生的那幾件事</h1>
    <p class="lead">每一題先直接回答，再給一個改法示意、一個有出處的研究、一件這週就能做的小事。</p>
    <div class="menu q-list">{items}</div>
    <div class="nav"><a href="/" class="prev">← 回首頁</a><a href="/faq/">常見問題 →</a></div>
'''
wr('q/index.html', shell('/q/', '常見卡點', '客戶看完提案沒下文、AI 工具買了沒人用、SOP 沒人照做：每一題先直接回答，再給改法示意與有出處的研究。', idx,
                         ld({'@context': 'https://schema.org', '@type': 'CollectionPage', 'url': SITE + '/q/', 'name': '常見卡點', 'inLanguage': 'zh-Hant', 'publisher': {'@id': ORG_ID}})))

# sitemap、llms.txt、頁尾連結
sm = rd('sitemap.xml'); urls = ['/q/'] + [f"/q/{a['slug']}/" for a in DATA]
for u in urls:
    if f'{SITE}{u}' not in sm:
        sm = sm.replace(f'  <url><loc>{SITE}/faq/</loc></url>\n', f'  <url><loc>{SITE}/faq/</loc></url>\n  <url><loc>{SITE}{u}</loc></url>\n')
wr('sitemap.xml', sm)
ll = rd('llms.txt'); ll = re.sub(r'\n## 常見卡點（直接回答）\n.*?(?=\n## |\Z)', '', ll, flags=re.S)
block = '\n## 常見卡點（直接回答）\n\n' + ''.join(f"### {a['pain']}\n{a['answer']}\n完整頁面：{SITE}/q/{a['slug']}/\n\n" for a in DATA)
ll = ll.replace('\n## 主要頁面', block + '## 主要頁面', 1) if '\n## 主要頁面' in ll else ll + block
wr('llms.txt', ll)
for f in ROOT.rglob('index.html'):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith(('en/', 'tools/')): continue
    s = f.read_text(encoding='utf-8')
    if '<a href="/faq/">常見問題</a>｜<a href="/quiz/">' in s and '<a href="/q/">' not in s:
        f.write_text(s.replace('<a href="/faq/">常見問題</a>｜', '<a href="/q/">常見卡點</a>｜<a href="/faq/">常見問題</a>｜'), encoding='utf-8')
print('pain_pages:', len(DATA), '頁 + /q/ 索引；sitemap、llms.txt、頁尾已更新')
