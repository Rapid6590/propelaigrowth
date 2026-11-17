# articles.py v0.1 (2026-11-18) — 文章頁 /articles/<slug>/ ＋ 索引 /articles/（LinkedIn 貼文發出後留一份）
# 用法：python3 tools/articles.py <站台根目錄>   （資料在 tools/data/articles.json；可重跑）
# 每則：標題、日期、圖、正文（段落內 \n 為換行）、出處、相關卡點（連 /q/）、小測驗；draft:true 的不產頁也不列。
# 發文流程：LinkedIn 發出後，把 articles.json 該則 draft 改 false，重跑本腳本（或 build.py）即可。
import sys, re, json, html, pathlib

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
SITE = 'https://propelaigrowth.com'
ORG_ID = SITE + '/#org'
HERE = pathlib.Path(__file__).parent
DATA = json.loads((HERE / 'data' / 'articles.json').read_text(encoding='utf-8'))
PAIN = {a['slug']: a for a in json.loads((HERE / 'data' / 'pain_pages.json').read_text(encoding='utf-8'))}
LIVE = sorted([a for a in DATA if not a.get('draft')], key=lambda a: a['date'], reverse=True)

def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')
def esc(s): return html.escape(s, quote=True)
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'
def para(t): return '<p>' + esc(t).replace('\n', '<br>') + '</p>'
def zhdate(d): y, m, dd = d.split('-'); return f'{y} 年 {int(m)} 月 {int(dd)} 日'

tpl = rd('about/index.html')
tpl = re.sub(r'<!-- aeo:ld -->.*?<!-- /aeo:ld -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<!-- wf:top -->.*?<!-- /wf:top -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', tpl)
HEAD, REST = tpl[:tpl.index('<main>') + 6], tpl[tpl.index('</main>'):]

def shell(url, title, desc, body, extra_ld, og_image=None):
    h = HEAD
    h = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}｜Propel AI 啟進智能決策</title>', h)
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title) + '｜Propel AI', h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
    if og_image:
        h = h.replace(f'{SITE}/assets/og.png', SITE + og_image)
        h = re.sub(r'<meta property="og:image:(width|height)" content="\d+">', '', h)
    h = h.replace(f'{SITE}/about/', SITE + url).replace('class="pg-about"', 'class="pg-articles"').replace(' aria-current="page"', '')
    h = h.replace('</head>', extra_ld + '\n</head>', 1)
    return h + '\n' + body + REST

CSS = '''
/* art:css */
.art-meta{font-size:13px;color:var(--mute);margin:0 0 18px}
.art-fig{margin:0 0 22px}.art-fig img{width:100%;height:auto;border-radius:12px;border:1px solid var(--line);display:block}
.art-fig figcaption{font-size:12.5px;color:var(--mute);margin-top:6px}
.art-body p{font-size:17px;line-height:1.9;margin:0 0 18px}
.art-src{font-size:13px;color:var(--mute);border-top:1px solid var(--line);padding-top:12px;margin:8px 0 22px}
.art-next{background:var(--tint);border-radius:12px;padding:14px 16px;margin:0 0 22px}
.art-next b{display:block;margin-bottom:6px}.art-next a{display:block;padding:6px 0;font-weight:700;text-decoration:none;color:var(--navy)}
.art-list{display:grid;gap:12px;margin:8px 0 24px}
.art-item{display:grid;grid-template-columns:120px 1fr;gap:14px;align-items:start;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;text-decoration:none;color:inherit}
.art-item img{width:120px;height:90px;object-fit:cover;border-radius:8px;display:block}
.art-item b{display:block;color:var(--navy);font-size:16px;line-height:1.4}.art-item span{display:block;font-size:13.5px;color:var(--mute);margin-top:4px}
.art-item small{display:block;font-size:12px;color:var(--mute);margin-top:6px}
.art-item:hover{border-color:var(--navy)}
@media (max-width:640px){.art-item{grid-template-columns:88px 1fr}.art-item img{width:88px;height:66px}}
/* /art:css */
'''
css = re.sub(r'\n/\* art:css \*/.*?/\* /art:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

LI = 'https://www.linkedin.com/in/propelai'

for i, a in enumerate(LIVE):
    url = f"/articles/{a['slug']}/"
    fig = lambda src, alt: f'<figure class="art-fig"><img src="{src}" alt="{esc(alt)}" loading="lazy"></figure>'
    figs = fig(*a['images'][0])
    # 第二張以後的圖插在正文段落之後：image_after = [段落序號(從 1 起)]
    after = {k: fig(*a['images'][j + 1]) for j, k in enumerate(a.get('image_after', []))}
    body_p = ''.join(para(t) + after.get(j + 1, '') for j, t in enumerate(a['body']))
    src = f'<p class="art-src">出處：{esc(a["source"])}</p>' if a.get('source') else ''
    nxt = ''
    links = [(f"/q/{q}/", PAIN[q]['pain']) for q in a.get('related_q', []) if q in PAIN]
    if a.get('quiz'): links.append(('/quiz/', '兩分鐘小測驗：你那件事卡在哪一格？'))
    if links:
        nxt = '<div class="art-next"><b>接著看</b>' + ''.join(f'<a href="{u}">{esc(t)} →</a>' for u, t in links) + '</div>'
    prev = LIVE[i + 1] if i + 1 < len(LIVE) else None
    newer = LIVE[i - 1] if i > 0 else None
    nav = '<div class="nav">' + (f'<a href="/articles/{prev["slug"]}/" class="prev">← 上一篇</a>' if prev else '<a href="/articles/" class="prev">← 全部文章</a>') + \
          (f'<a href="/articles/{newer["slug"]}/">下一篇 →</a>' if newer else '<a href="/articles/">全部文章 →</a>') + '</div>'
    body = f'''<!-- wf:top --><nav class="wf-crumb" aria-label="你在哪裡"><a href="/">首頁</a><span>›</span><a href="/articles/">文章</a><span>›</span><b>{esc(a['title'])}</b></nav><!-- /wf:top -->
    <span class="pill">文章 · 第 {a['no']} 篇</span>
    <h1>{esc(a['title'])}</h1>
    <p class="art-meta">George Chen 陳朝智・行為設計師｜{zhdate(a['date'])}｜先發在 <a href="{LI}" target="_blank" rel="noopener">LinkedIn</a>，這裡留一份</p>
    {figs}
    <div class="art-body">{body_p}</div>
    {src}
    {nxt}
    {nav}
'''
    obj = {'@context': 'https://schema.org', '@type': 'BlogPosting', '@id': SITE + url + '#post', 'headline': a['title'],
           'description': a['deck'], 'datePublished': a['date'], 'inLanguage': 'zh-Hant', 'url': SITE + url,
           'image': [SITE + s for s, _ in a['images']],
           'author': {'@type': 'Person', 'name': 'George Chen 陳朝智', 'jobTitle': '行為設計師', 'url': LI},
           'publisher': {'@id': ORG_ID}, 'mainEntityOfPage': SITE + url}
    wr(url.lstrip('/') + 'index.html', shell(url, a['title'], a['deck'], body, ld(obj), og_image=a['images'][0][0]))

# 索引頁
items = ''.join(f'<a class="art-item" href="/articles/{a["slug"]}/"><img src="{a["images"][0][0]}" alt="" loading="lazy"><div><b>{esc(a["title"])}</b><span>{esc(a["deck"])}</span><small>{zhdate(a["date"])}</small></div></a>' for a in LIVE)
empty = '' if LIVE else f'<div class="menu"><div class="empty">第一篇整理中。想先看的話，<a href="{LI}" target="_blank" rel="noopener">LinkedIn 上已經有幾篇</a>。</div></div>'
idx_body = f'''<!-- wf:top --><nav class="wf-crumb" aria-label="你在哪裡"><a href="/">首頁</a><span>›</span><b>文章</b></nav><!-- /wf:top -->
    <span class="pill">文章</span>
    <h1>一個畫面，一個看法，一個問句</h1>
    <p class="lead">每週幾篇，從一件日常的小事看「為什麼講了三次，他還是沒做」。先在 <a href="{LI}" target="_blank" rel="noopener">LinkedIn</a> 發，這裡留一份；每篇結尾接回對應的常見卡點。</p>
    <div class="art-list">{items}</div>{empty}
    <div class="nav"><a href="/q/" class="prev">← 常見卡點</a><a href="/contact/">留下一件事 →</a></div>
'''
idx_ld = ld({'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': '文章｜Propel AI', 'url': SITE + '/articles/',
             'hasPart': [{'@type': 'BlogPosting', 'headline': a['title'], 'url': f"{SITE}/articles/{a['slug']}/", 'datePublished': a['date']} for a in LIVE]})
wr('articles/index.html', shell('/articles/', '文章', '從一件日常的小事看「為什麼講了三次，他還是沒做」。LinkedIn 貼文留一份，每篇接回對應的常見卡點。', idx_body, idx_ld))

# sitemap：補文章頁（放在 /articles/ 之後）
sm = rd('sitemap.xml')
sm = re.sub(r'  <url><loc>https://propelaigrowth\.com/articles/[^<]+/</loc>(<lastmod>[^<]*</lastmod>)?</url>\n', '', sm)
add = ''.join(f'  <url><loc>{SITE}/articles/{a["slug"]}/</loc><lastmod>{a["date"]}</lastmod></url>\n' for a in LIVE)
anchor = re.search(r'  <url><loc>https://propelaigrowth\.com/articles/</loc>[^\n]*\n', sm)
if anchor: sm = sm[:anchor.end()] + add + sm[anchor.end():]
else: sm = sm.replace('</urlset>', add + '</urlset>')
wr('sitemap.xml', sm)
print(f'articles: {len(LIVE)} 篇上線（{len(DATA) - len(LIVE)} 篇 draft）')
