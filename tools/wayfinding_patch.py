# wayfinding_patch.py v0.1 (2026-11-18) — 四步路徑條、麵包屑、/map/ 網站地圖、頁尾連結
# 用法：python3 tools/wayfinding_patch.py <站台根目錄>   可重跑（冪等）。只改中文頁，不碰 /en/。
# 四步：① 找到卡住的事（/q/、/quiz/）② 看懂為什麼（/how/）③ 選一個開始（/trial/ /half-day/ /workshop/ /surf/ /picker/）④ 聊一聊（/faq/ /about/ /contact/）
import sys, re, json, html, pathlib
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
SITE = 'https://propelaigrowth.com'
def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')
def esc(s): return html.escape(s, quote=True)
PAIN = json.loads((pathlib.Path(__file__).parent / 'data' / 'pain_pages.json').read_text(encoding='utf-8'))

STEPS = [('/q/', '找到卡住的事', '常見卡點、兩分鐘小測驗'),
         ('/how/', '看懂為什麼', '數字是結果，可以動手的是行為'),
         ('/trial/', '選一個開始', '試駕、半天課、工作坊、SURF'),
         ('/contact/', '聊一聊', '常見問題、為什麼是我們、聯絡')]
# url -> (麵包屑鏈 [(label,href)...不含首頁], 所在步 1–4 或 None)
PAGES = {
    '/how/': ([('怎麼看問題', None)], 2),
    '/q/': ([('常見卡點', None)], 1),
    '/quiz/': ([('兩分鐘小測驗', None)], 1),
    '/picker/': ([('課程', '/#courses'), ('選題器', None)], 3),
    '/trial/': ([('課程', '/#courses'), ('59 分鐘試駕', None)], 3),
    '/trial/prep/': ([('課程', '/#courses'), ('59 分鐘試駕', '/trial/'), ('課前說明', None)], 3),
    '/half-day/': ([('課程', '/#courses'), ('半天課・全天課', None)], 3),
    '/half-day/prep/': ([('課程', '/#courses'), ('半天課・全天課', '/half-day/'), ('課前說明', None)], 3),
    '/workshop/': ([('課程', '/#courses'), ('全天工作坊', None)], 3),
    '/workshop/prep/': ([('課程', '/#courses'), ('全天工作坊', '/workshop/'), ('課前說明', None)], 3),
    '/surf/': ([('課程', '/#courses'), ('SURF™ 原廠班', None)], 3),
    '/surf/prep/': ([('課程', '/#courses'), ('SURF™ 原廠班', '/surf/'), ('課前說明', None)], 3),
    '/faq/': ([('常見問題', None)], 4),
    '/about/': ([('為什麼是我們', None)], 4),
    '/contact/': ([('聯絡', None)], 4),
    '/downloads/': ([('一頁介紹下載', None)], None),
    '/articles/': ([('文章', None)], None),
}
for a in PAIN:
    PAGES[f"/q/{a['slug']}/"] = ([('常見卡點', '/q/'), (a['short'], None)], 1)

CSS = '''
/* wf:css */
.wf-crumb{font-size:13px;color:var(--mute);margin:0 0 10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.wf-crumb a{color:var(--mute);text-decoration:none}.wf-crumb a:hover{color:var(--navy);text-decoration:underline}
.wf-crumb b{color:var(--fg);font-weight:600}
.wf-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:0 0 22px}
.wf-steps a{display:flex;gap:8px;align-items:center;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--mute);text-decoration:none;font-size:13px;line-height:1.3}
.wf-steps a i{flex:0 0 22px;height:22px;border-radius:50%;background:var(--line);color:var(--fg);font-style:normal;font-weight:700;font-size:12px;display:inline-flex;align-items:center;justify-content:center}
.wf-steps a span{display:block}.wf-steps a small{display:block;font-size:11px;color:var(--mute);margin-top:1px}
.wf-steps a.cur{border-color:var(--orange);background:var(--tint);color:var(--navy);font-weight:700}
.wf-steps a.cur i{background:var(--orange);color:#fff}
.wf-steps a:hover{border-color:var(--navy)}
@media (max-width:640px){.wf-steps{grid-template-columns:repeat(2,1fr)}.wf-steps a small{display:none}}
.map-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:8px 0 24px}
.map-col{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.map-col h2{font-size:16px;margin:0 0 8px;display:flex;gap:8px;align-items:center}
.map-col h2 i{flex:0 0 22px;height:22px;border-radius:50%;background:var(--orange);color:#fff;font-style:normal;font-weight:700;font-size:12px;display:inline-flex;align-items:center;justify-content:center}
.map-col ul{list-style:none;margin:0;padding:0}.map-col li{padding:6px 0;border-top:1px solid var(--line);font-size:14px}.map-col li:first-child{border-top:0}
.map-col li a{color:var(--navy);font-weight:600;text-decoration:none}.map-col li span{display:block;color:var(--mute);font-size:12.5px;margin-top:2px}
@media (max-width:640px){.map-cols{grid-template-columns:1fr}}
/* /wf:css */
'''
css = re.sub(r'\n/\* wf:css \*/.*?/\* /wf:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

def crumb_html(chain):
    parts = ['<a href="/">首頁</a>']
    for label, href in chain:
        parts.append('<span>›</span>')
        parts.append(f'<a href="{href}">{esc(label)}</a>' if href else f'<b>{esc(label)}</b>')
    return '<nav class="wf-crumb" aria-label="你在哪裡">' + ''.join(parts) + '</nav>'
def steps_html(cur):
    out = []
    for i, (href, name, sub) in enumerate(STEPS, 1):
        cls = ' class="cur"' if i == cur else ''
        out.append(f'<a{cls} href="{href}"><i>{i}</i><span>{name}<small>{sub}</small></span></a>')
    return '<nav class="wf-steps" aria-label="四步路徑">' + ''.join(out) + '</nav>'

n = 0
for f in sorted(ROOT.glob('**/index.html')):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith(('en/', 'tools/')) or rel == 'index.html': continue
    url = '/' + rel[:-len('index.html')]
    if url not in PAGES or url == '/map/': continue
    chain, cur = PAGES[url]
    s = f.read_text(encoding='utf-8'); o = s
    s = re.sub(r'<main>\n<!-- wf:top -->.*?<!-- /wf:top -->\n', '<main>', s, flags=re.S)
    block = '<!-- wf:top -->' + crumb_html(chain) + (steps_html(cur) if cur else '') + '<!-- /wf:top -->\n'
    s = s.replace('<main>', '<main>\n' + block, 1)
    if s != o: f.write_text(s, encoding='utf-8'); n += 1

# /map/ 網站地圖（借關於頁外框）
tpl = rd('about/index.html')
tpl = re.sub(r'<!-- aeo:ld -->.*?<!-- /aeo:ld -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<!-- wf:top -->.*?<!-- /wf:top -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', tpl)
HEAD, REST = tpl[:tpl.index('<main>') + 6], tpl[tpl.index('</main>'):]
h = HEAD
h = re.sub(r'<title>.*?</title>', '<title>網站地圖｜Propel AI 啟進智能決策</title>', h)
h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + '整個網站只有四步：找到卡住的事、看懂為什麼、選一個開始、聊一聊。所有頁面都在這裡。', h)
h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + '網站地圖｜Propel AI', h)
h = h.replace(f'{SITE}/about/', SITE + '/map/').replace('class="pg-about"', 'class="pg-map"').replace(' aria-current="page"', '')
h = h.replace('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex,follow">')
if '<meta name="robots"' not in h: h = h.replace('</head>', '<meta name="robots" content="noindex,follow">\n</head>', 1)
cols = [
  ('找到卡住的事', [('/q/', '常見卡點', '一句痛點、一頁直接回答，陸續補齊')] + [(f"/q/{a['slug']}/", a['pain'], '') for a in PAIN] + [('/quiz/', '兩分鐘小測驗', '三題，不用留資料，看你那件事能不能用這個方法')]),
  ('看懂為什麼', [('/how/', '怎麼看問題', '數字是結果；可以動手的是行為。四個例子'), ('/articles/', '文章', '一個畫面、一個看法、一個問句'), ('/downloads/', '一頁介紹下載', '各課程一頁介紹，可以帶走')]),
  ('選一個開始', [('/trial/', '59 分鐘試駕', '到你公司，抽一題實際上一次', '/trial/prep/'), ('/half-day/', '半天課・全天課', '六題或十二題，每題練一個決定', '/half-day/prep/'), ('/workshop/', '全天工作坊', '帶自己的題目，PROPEL 六站走一遍', '/workshop/prep/'), ('/surf/', 'SURF™ 原廠班', 'MINDWORX 授權課程', '/surf/prep/'), ('/picker/', '選題器', '先挑你最想改的那個行為')]),
  ('聊一聊', [('/faq/', '常見問題', '費用、時間、怎麼上、適不適合'), ('/about/', '為什麼是我們', '我們相信的三件事、講師是誰'), ('/contact/', '聯絡', '留下一件你想推動的事，我們回信'), ('/en/', 'English', 'English pages')]),
]
body = ['<nav class="wf-crumb" aria-label="你在哪裡"><a href="/">首頁</a><span>›</span><b>網站地圖</b></nav>',
        '<span class="pill">網站地圖</span><h1>整個網站，只有四步</h1>',
        '<p class="lead">找到你卡住的事 → 看懂為什麼 → 選一個開始 → 聊一聊。每一頁都在這四步裡；你在哪一步，頁面上方的路徑條會亮。</p>',
        '<div class="map-cols">']
for i, (name, items) in enumerate(cols, 1):
    body.append(f'<div class="map-col"><h2><i>{i}</i>{esc(name)}</h2><ul>')
    for it in items:
        href, label, sub = it[0], it[1], it[2]; prep = it[3] if len(it) > 3 else None
        extra = f'　<a href="{prep}" style="font-weight:400;font-size:12.5px">課前說明 →</a>' if prep else ''
        body.append(f'<li><a href="{href}">{esc(label)}</a>{extra}' + (f'<span>{esc(sub)}</span>' if sub else '') + '</li>')
    body.append('</ul></div>')
body.append('</div>')
wr('map/index.html', h + '\n' + '\n'.join(body) + '\n' + REST)

# 頁尾加「網站地圖」；sitemap 不加（noindex）
for f in ROOT.rglob('index.html'):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith(('en/', 'tools/')): continue
    s = f.read_text(encoding='utf-8')
    if '<a href="/contact/">聯絡</a></div><!-- /aeo:foot -->' in s and '/map/">網站地圖' not in s:
        f.write_text(s.replace('<a href="/contact/">聯絡</a></div><!-- /aeo:foot -->', '<a href="/contact/">聯絡</a>｜<a href="/map/">網站地圖</a></div><!-- /aeo:foot -->'), encoding='utf-8')
print(f'wayfinding: {n} 頁加路徑條／麵包屑；/map/ 已產生；頁尾已加網站地圖')
