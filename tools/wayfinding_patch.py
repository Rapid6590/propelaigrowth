# wayfinding_patch.py v0.3 (2026-11-18；v0.3 第二層瘦身 SUB_HIDE) — 主選單＝四步；所在那步展開一排；麵包屑；/courses/ 入口；/map/ 網站地圖
# 用法：python3 tools/wayfinding_patch.py <站台根目錄>   可重跑（冪等）。只改中文頁，不碰 /en/。
# v0.2：George 裁示「主選單改成四步」——主選單、所在步驟展開列、/map/ 三處都從下面這一份 STEPS 產生，
#       不再有另一條路徑條。新增一頁只要加進 STEPS 對應那一步的 items。
#       /quiz/、/picker/ 是獨立工具頁（自己的版面），不放主選單。
import sys, re, json, html, pathlib
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
SITE = 'https://propelaigrowth.com'
HERE = pathlib.Path(__file__).parent
def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')
def esc(s): return html.escape(s, quote=True)
PAIN = json.loads((HERE / 'data' / 'pain_pages.json').read_text(encoding='utf-8'))
ARTS = {a['slug']: a for a in json.loads((HERE / 'data' / 'articles.json').read_text(encoding='utf-8'))}

# ---- 唯一的一份清單：(網址, 選單上的名字, 網站地圖上的一句說明[, 課前說明網址]) ----
# 展開列不列的頁：一頁介紹下載（各課程頁本來就有下載連結）、選題器（從 /courses/ 與首頁進）。頁面與網址都還在。
SUB_HIDE = {'/downloads/', '/picker/'}

STEPS = [
    {'name': '找到卡住的事', 'href': '/q/', 'items': [
        ('/q/', '常見卡點', '一句痛點、一頁直接回答，陸續補齊'),
        ('/quiz/', '兩分鐘小測驗', '三題，不用留資料，看你那件事能不能用這個方法')]},
    {'name': '看懂為什麼', 'href': '/how/', 'items': [
        ('/how/', '怎麼看問題', '數字是結果；可以動手的是行為。四個例子'),
        ('/articles/', '文章', '一個畫面、一個看法、一個問句'),
        ('/calc/', '算算看', '每一關多一點，最後差多少？換成你的數字'),
        ('/downloads/', '一頁介紹下載', '各課程一頁介紹，可以帶走')]},
    {'name': '選一個開始', 'href': '/courses/', 'items': [
        ('/trial/', '59 分鐘試駕', '到你公司，抽一題實際上一次', '/trial/prep/'),
        ('/half-day/', '半天課・全天課', '六題或十二題，每題練一個決定', '/half-day/prep/'),
        ('/workshop/', '全天工作坊', '帶自己的題目，PROPEL 六站走一遍', '/workshop/prep/'),
        ('/surf/', 'SURF™ 原廠班', 'MINDWORX 授權課程', '/surf/prep/'),
        ('/picker/', '選題器', '先挑你最想改的那個行為')]},
    {'name': '聊一聊', 'href': '/contact/', 'items': [
        ('/faq/', '常見問題', '費用、時間、怎麼上、適不適合'),
        ('/about/', '為什麼是我們', '我們相信的三件事、講師是誰'),
        ('/contact/', '聯絡', '留下一件你想推動的事，我們回信')]},
]
# 還沒產生的頁不列（例：/calc/ 尚未建）
for st in STEPS:
    st['items'] = [it for it in st['items'] if (ROOT / it[0].strip('/') / 'index.html').exists()]

def locate(url):
    """回傳 (第幾步 1–4 或 None, 所在項目的網址或 None)"""
    if url == '/courses/': return 3, None
    for i, st in enumerate(STEPS, 1):
        for it in st['items']:
            if url == it[0] or url.startswith(it[0]): return i, it[0]
    return None, None

def deep_label(url):
    """第二層頁面自己的名字（麵包屑最後一格）"""
    if url.endswith('/prep/'): return '課前說明'
    m = re.fullmatch(r'/q/([^/]+)/', url)
    if m:
        for a in PAIN:
            if a['slug'] == m.group(1): return a['short']
    m = re.fullmatch(r'/articles/([^/]+)/', url)
    if m and m.group(1) in ARTS: return ARTS[m.group(1)]['title']
    return None

CSS = '''
/* wf:css */
.sitehead>.lang{font-size:14px;font-weight:700;color:var(--navy-text);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:6px 12px}
.sitehead>.lang:hover{background:var(--sky)}
.wf-nav{flex:1 0 100%;display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.wf-nav a{display:flex;gap:8px;align-items:center;min-width:0;padding:9px 10px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--mute);text-decoration:none;font-size:14px;line-height:1.3}
.wf-nav a i{flex:0 0 22px;height:22px;border-radius:50%;background:var(--line);color:var(--fg);font-style:normal;font-weight:700;font-size:12px;display:inline-flex;align-items:center;justify-content:center}
.wf-nav a:hover{border-color:var(--navy);color:var(--navy-text)}
.wf-nav a[aria-current]{border-color:var(--orange);background:var(--tint);color:var(--navy-text);font-weight:700}
.wf-nav a[aria-current] i{background:var(--orange);color:#fff}
.wf-nav a:focus-visible,.wf-sub a:focus-visible,.sitehead>.lang:focus-visible{outline:3px solid var(--orange);outline-offset:2px}
.wf-sub{flex:1 0 100%;display:flex;flex-wrap:wrap;gap:2px 2px;align-items:center;font-size:13.5px;margin-top:-4px}
.wf-sub span{color:var(--mute);font-size:12.5px;margin-right:4px}
.wf-sub a{color:var(--mute);text-decoration:none;padding:4px 10px;border-radius:999px}
.wf-sub a:hover{color:var(--navy-text);background:var(--sky)}
.wf-sub a[aria-current]{color:var(--accent-ink);font-weight:700;background:var(--tint)}
.wf-crumb{font-size:13px;color:var(--mute);margin:0 0 10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.wf-crumb a{color:var(--mute);text-decoration:none}.wf-crumb a:hover{color:var(--navy-text);text-decoration:underline}
.wf-crumb b{color:var(--fg);font-weight:600}
@media (max-width:640px){.wf-nav{grid-template-columns:repeat(2,1fr)}.wf-nav a{font-size:13.5px;padding:8px 9px}.wf-sub span{display:none}.wf-sub a{padding:4px 8px}}
.map-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:8px 0 24px}
.map-col{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.map-col h2{font-size:16px;margin:0 0 8px;display:flex;gap:8px;align-items:center}
.map-col h2 i{flex:0 0 22px;height:22px;border-radius:50%;background:var(--orange);color:#fff;font-style:normal;font-weight:700;font-size:12px;display:inline-flex;align-items:center;justify-content:center}
.map-col ul{list-style:none;margin:0;padding:0}.map-col li{padding:6px 0;border-top:1px solid var(--line);font-size:14px}.map-col li:first-child{border-top:0}
.map-col li a{color:var(--navy-text);font-weight:600;text-decoration:none}.map-col li span{display:block;color:var(--mute);font-size:12.5px;margin-top:2px}
.map-col li.sub{padding-left:14px;font-size:13.5px}.map-col li.sub a{font-weight:500}
@media (max-width:640px){.map-cols{grid-template-columns:1fr}}
/* /wf:css */
'''
css = re.sub(r'\n/\* wf:css \*/.*?/\* /wf:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

def header_html(wordmark, step, item):
    nav = []
    for i, st in enumerate(STEPS, 1):
        cur = ' aria-current="step"' if i == step else ''
        nav.append(f'<a href="{st["href"]}"{cur}><i>{i}</i>{st["name"]}</a>')
    out = ['<header class="sitehead">', '    ' + wordmark,
           '    <a class="lang" href="/en/" hreflang="en" lang="en">EN</a>',
           '    <nav class="wf-nav" aria-label="主選單">' + ''.join(nav) + '</nav>']
    if step:
        # 第二層瘦身（2026-11-18 George 同意）：SUB_HIDE 裡的頁不出現在展開列，除非人就在那一頁；網站地圖照列
        sub = [f'<a href="{it[0]}"' + (' aria-current="page"' if it[0] == item else '') + f'>{esc(it[1])}</a>' for it in STEPS[step - 1]['items'] if it[0] not in SUB_HIDE or it[0] == item]
        out.append('    <nav class="wf-sub" aria-label="這一步裡的頁面"><span>這一步有</span>' + ''.join(sub) + '</nav>')
    out.append('  </header>')
    return '\n'.join(out)

def crumb_html(chain):
    parts = ['<a href="/">首頁</a>']
    for label, href in chain:
        parts.append('<span>›</span>')
        parts.append(f'<a href="{href}">{esc(label)}</a>' if href else f'<b>{esc(label)}</b>')
    return '<nav class="wf-crumb" aria-label="你在哪裡">' + ''.join(parts) + '</nav>'

HEADER_RE = re.compile(r'<header class="sitehead">.*?</header>', re.S)
WORDMARK_RE = re.compile(r'<a class="wordmark".*?</a>', re.S)
TOP_RE = re.compile(r'<main>\n<!-- wf:top -->.*?<!-- /wf:top -->\n', re.S)

def patch(s, url):
    step, item = locate(url)
    m = HEADER_RE.search(s)
    if m:
        wm = WORDMARK_RE.search(m.group(0))
        if wm: s = s[:m.start()] + header_html(wm.group(0), step, item) + s[m.end():]
    s = TOP_RE.sub('<main>', s)
    label = deep_label(url)
    if label and item and url != item:      # 只有第二層頁面放麵包屑；第一層看上面亮的那一格就知道
        parent = next(it for st in STEPS for it in st['items'] if it[0] == item)
        s = s.replace('<main>', '<main>\n<!-- wf:top -->' + crumb_html([(parent[1], parent[0]), (label, None)]) + '<!-- /wf:top -->\n', 1)
    return s

# ---- /courses/：第三步的入口頁（四張課程卡直接取自首頁「課程」那一段，改首頁這裡跟著變）----
tpl = rd('about/index.html')
tpl = re.sub(r'<!-- aeo:ld -->.*?<!-- /aeo:ld -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<!-- wf:top -->.*?<!-- /wf:top -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', tpl)
HEAD, REST = tpl[:tpl.index('<main>') + 6], tpl[tpl.index('</main>'):]
def shell(url, cls, title, desc, body, noindex=True):
    h = HEAD
    h = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}｜Propel AI 啟進智能決策</title>', h)
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title) + '｜Propel AI', h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
    h = h.replace(f'{SITE}/about/', SITE + url).replace('class="pg-about"', f'class="{cls}"')
    if noindex:
        h = h.replace('<meta name="robots" content="index,follow">', '')
        h = h.replace('</head>', '<meta name="robots" content="noindex,follow">\n</head>', 1)
    return h + '\n' + body + '\n' + REST

home = rd('index.html')
m = re.search(r'<section class="sec" id="courses">.*?(<div class="tiles two">.*?</div>)\s*(<div class="links">.*?</div>)', home, re.S)
if m:
    body = ['<span class="pill">選一個開始</span>', '<h1>從你現在最想知道的那件事開始</h1>',
            '<p class="lead">四種開始的方式，各回答一個問題。還不確定的話，先看 59 分鐘試駕。</p>',
            m.group(1), m.group(2).replace('<a class="more" href="/downloads/">下載一頁介紹 →</a>', '<a class="more" href="/downloads/">下載一頁介紹 →</a><a class="more" href="/faq/">費用與常見問題 →</a>')]
    wr('courses/index.html', shell('/courses/', 'pg-courses', '選一個開始', '59 分鐘試駕、半天課、全天工作坊、SURF™ 原廠班：從你現在最想知道的那件事開始。', '\n'.join(body)))

# ---- /map/ 網站地圖：同一份 STEPS ----
body = ['<span class="pill">網站地圖</span><h1>整個網站，只有四步</h1>',
        '<p class="lead">找到你卡住的事 → 看懂為什麼 → 選一個開始 → 聊一聊。上方選單就是這四步：你在哪一步，那一格會亮，下面一排是這一步裡的頁面。</p>',
        '<div class="map-cols">']
for i, st in enumerate(STEPS, 1):
    body.append(f'<div class="map-col"><h2><i>{i}</i>{esc(st["name"])}</h2><ul>')
    for it in st['items']:
        prep = it[3] if len(it) > 3 else None
        extra = f'　<a href="{prep}" style="font-weight:400;font-size:12.5px">課前說明 →</a>' if prep else ''
        body.append(f'<li><a href="{it[0]}">{esc(it[1])}</a>{extra}<span>{esc(it[2])}</span></li>')
        if it[0] == '/q/':
            body += [f'<li class="sub"><a href="/q/{a["slug"]}/">{esc(a["pain"])}</a></li>' for a in PAIN]
    if i == 4: body.append('<li><a href="/en/">English</a><span>English pages</span></li>')
    body.append('</ul></div>')
body.append('</div>')
wr('map/index.html', shell('/map/', 'pg-map', '網站地圖', '整個網站只有四步：找到卡住的事、看懂為什麼、選一個開始、聊一聊。所有頁面都在這裡。', '\n'.join(body)))

# ---- 套到所有中文頁（含首頁與 404）----
n = 0
files = sorted(ROOT.glob('**/index.html')) + [ROOT / '404.html']
for f in files:
    if not f.exists(): continue
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith(('en/', 'tools/')): continue
    url = '/' if rel == 'index.html' else ('/404' if rel == '404.html' else '/' + rel[:-len('index.html')])
    s = f.read_text(encoding='utf-8'); o = s
    s = patch(s, url)
    # 頁尾加「網站地圖」；sitemap.xml 不加（noindex）
    if '<a href="/contact/">聯絡</a></div><!-- /aeo:foot -->' in s and '/map/">網站地圖' not in s:
        s = s.replace('<a href="/contact/">聯絡</a></div><!-- /aeo:foot -->', '<a href="/contact/">聯絡</a>｜<a href="/map/">網站地圖</a></div><!-- /aeo:foot -->')
    if s != o: f.write_text(s, encoding='utf-8'); n += 1
print(f'wayfinding v0.3: {n} 頁更新（主選單四步＋展開列＋麵包屑）；/courses/、/map/ 已產生')
