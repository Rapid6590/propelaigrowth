# wayfinding_patch.py v0.4 (2026-11-18；v0.3 第二層瘦身 SUB_HIDE；v0.4 主層與下一層用線連起來) — 主選單＝四步；所在那步展開一排；麵包屑；/courses/ 入口；/map/ 網站地圖
# 用法：python3 tools/wayfinding_patch.py <站台根目錄>   可重跑（冪等）。只改中文頁，不碰 /en/。
# v0.2：George 裁示「主選單改成四步」——主選單、所在步驟展開列、/map/ 三處都從下面這一份 STEPS 產生，
#       不再有另一條路徑條。新增一頁只要加進 STEPS 對應那一步的 items。
#       /quiz/、/picker/ 是獨立工具頁（自己的版面），不放主選單。
# v0.4：George 說「主層次跟下一層之間有一條線做連結」（比照工作坊簡報的進度條）——
#       所在那一步往下拉一條線，接到一個有框的盒子，盒子裡是這一步的頁面（有框的小格，目前頁填色）。
#       首頁、網站地圖、404 沒有「所在那一步」→ 四步各自展開，一眼看到全部頁面。
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
.wf-nav{flex:1 0 100%;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px 6px}
.wf-nav>a{position:relative;display:flex;gap:8px;align-items:center;min-width:0;padding:9px 10px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--mute);text-decoration:none;font-size:14px;line-height:1.3}
.wf-nav>a i{flex:0 0 22px;height:22px;border-radius:50%;background:var(--line);color:var(--fg);font-style:normal;font-weight:700;font-size:12px;display:inline-flex;align-items:center;justify-content:center}
.wf-nav>a:hover{border-color:var(--navy);color:var(--navy-text)}
.wf-nav>a[aria-current]{border:2px solid var(--orange);padding:8px 9px;background:var(--tint);color:var(--navy-text);font-weight:700}
.wf-nav>a[aria-current] i{background:var(--orange);color:#fff}
.wf-nav a:focus-visible,.sitehead>.lang:focus-visible{outline:3px solid var(--orange);outline-offset:2px}
/* 連結線：所在那一步往下接到盒子 */
.wf-nav>a[aria-current]::after,.wf-all>a::after{content:"";position:absolute;left:50%;top:100%;width:2px;height:14px;margin-left:-1px;background:var(--orange)}
.wf-all>a::after{background:#9DB0BF;height:13px}
.wf-sub{grid-column:1/-1;justify-self:start;box-sizing:border-box;min-width:calc(25% - 5px);max-width:100%;display:flex;flex-wrap:wrap;gap:6px;padding:7px;border:2px solid var(--orange);border-radius:12px;background:var(--card)}
.wf-sub.t2{margin-left:calc(25% + 1.5px)}
.wf-sub.t3{justify-self:end;min-width:calc(50% - 3px)}
.wf-sub.t4{justify-self:end}
.wf-sub a{display:block;padding:5px 11px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--navy-text);text-decoration:none;font-size:13.5px;line-height:1.35;white-space:nowrap}
.wf-sub a:hover{border-color:var(--navy);background:var(--sky)}
.wf-sub a[aria-current]{background:var(--accent-ink);border-color:var(--accent-ink);color:#fff;font-weight:700}
/* 首頁等：四步各自展開 */
.wf-all .wf-sub{grid-column:auto;justify-self:stretch;align-self:start;min-width:0;margin-left:0;flex-direction:column;flex-wrap:nowrap;gap:5px;border:1.5px solid #9DB0BF}
.wf-all .wf-sub a{white-space:normal}
.wf-crumb{font-size:13px;color:var(--mute);margin:0 0 10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.wf-crumb a{color:var(--mute);text-decoration:none}.wf-crumb a:hover{color:var(--navy-text);text-decoration:underline}
.wf-crumb b{color:var(--fg);font-weight:600}
@media (max-width:640px){
.wf-nav{grid-template-columns:repeat(2,minmax(0,1fr))}.wf-nav>a{font-size:13.5px;padding:8px 9px;order:1}.wf-nav>a[aria-current]{padding:7px 8px}
.wf-nav>a:nth-of-type(n+3){order:3}.wf-sub{justify-self:stretch;min-width:0;order:2}.wf-sub.t2{margin-left:0}.wf-sub.t3,.wf-sub.t4{order:4;justify-self:stretch;min-width:0}
.wf-sub a{padding:5px 9px}
/* 首頁（手機）：一步一列，左邊是步驟、右邊是它的頁面，中間一條橫線 */
.wf-all{grid-template-columns:auto minmax(0,1fr);gap:8px 12px}
.wf-all>a:nth-of-type(1){order:1}.wf-all>a:nth-of-type(2){order:3}.wf-all>a:nth-of-type(3){order:5}.wf-all>a:nth-of-type(4){order:7}
.wf-all .wf-sub.t1{order:2}.wf-all .wf-sub.t2{order:4}.wf-all .wf-sub.t3{order:6}.wf-all .wf-sub.t4{order:8}
.wf-all>a{align-self:start}.wf-all>a::after{left:100%;top:50%;width:13px;height:2px;margin:-1px 0 0}
.wf-all .wf-sub{flex-direction:row;flex-wrap:wrap;padding:5px;gap:4px}.wf-all .wf-sub a{white-space:nowrap;padding:4px 8px;font-size:13px}
}
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

def sub_html(i, item):
    # 第二層瘦身（2026-11-18 George 同意）：SUB_HIDE 裡的頁不出現在盒子裡，除非人就在那一頁；網站地圖照列
    st = STEPS[i - 1]
    links = [f'<a href="{it[0]}"' + (' aria-current="page"' if it[0] == item else '') + f'>{esc(it[1])}</a>'
             for it in st['items'] if it[0] not in SUB_HIDE or it[0] == item]
    return f'<div class="wf-sub t{i}" role="group" aria-label="{esc(st["name"])}：這一步裡的頁面">' + ''.join(links) + '</div>'

def header_html(wordmark, step, item):
    nav = []
    for i, st in enumerate(STEPS, 1):
        cur = ' aria-current="step"' if i == step else ''
        nav.append(f'<a href="{st["href"]}"{cur}><i>{i}</i>{st["name"]}</a>')
    # 有所在那一步：只展開那一步（線接到盒子）。沒有（首頁、網站地圖、404）：四步都展開。
    subs = [sub_html(step, item)] if step else [sub_html(i, None) for i in range(1, len(STEPS) + 1)]
    cls = 'wf-nav' if step else 'wf-nav wf-all'
    out = ['<header class="sitehead">', '    ' + wordmark,
           '    <a class="lang" href="/en/" hreflang="en" lang="en">EN</a>',
           f'    <nav class="{cls}" aria-label="主選單">' + ''.join(nav) + ''.join(subs) + '</nav>',
           '  </header>']
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
        '<p class="lead">找到你卡住的事 → 看懂為什麼 → 選一個開始 → 聊一聊。上方選單就是這四步：你在哪一步，那一格會亮，往下一條線接到的盒子，就是這一步裡的頁面。</p>',
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
print(f'wayfinding v0.4: {n} 頁更新（主選單四步＋連結線展開盒＋麵包屑）；/courses/、/map/ 已產生')
