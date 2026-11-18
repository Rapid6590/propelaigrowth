# big_decisions_page.py v0.2 (2026-11-18；v0.2 George 定「先一小時一題」，拿掉三小時) — /big-decisions/「大決定之前，該問的都問了嗎？」（決策品質線 DQ：給董事、獨立董事與高階主管）
# 用法：python3 tools/big_decisions_page.py <站台根目錄>   可重跑。順序：… → calc_page → picker_order_patch → big_decisions_page → wayfinding。
# 規矩（George 1114–1118）：
#   - 名稱＝痛點句「大決定之前，該問的都問了嗎？」；副標「後照鏡照不到的地方，先回頭看一眼」（朋友的原話：怕不知道自己不知道什麼、後照鏡盲點）。
#   - 承諾範圍：不保證決定對；只說「研究上已知的盲點區逐一看過」。不寫「找出所有盲點」「避免錯誤決策」「可以免責」。
#   - 不教法律；不把偏誤貼在具名的人或公司身上；頁面上不放研究數字（DQ 線的研究卡還沒核完）。
#   - 同一個網站底下的一頁（不是第二個網站）；選單、/map/ 的項目在 wayfinding_patch.py 的 STEPS。
import sys, re, html, pathlib
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
SITE = 'https://propelaigrowth.com'
URL = '/big-decisions/'
def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')
def esc(s): return html.escape(s, quote=True)

TITLE = '大決定之前，該問的都問了嗎？'
SUB = '後照鏡照不到的地方，先回頭看一眼。'
DESC = '給董事、獨立董事與高階主管：併購、大額投資、進新市場這類大決定，表決前把研究上已知的三個盲點區各看過一遍，帶走一張會前檢核表。'

# (盲點區, 這一題, 會前多問這一句)
QUESTIONS = [
    ('太有把握', '這份財測，該打幾折？', '同類的案子，後來做到幾成？'),
    ('只看支持的證據', '大家都說好的案子，該多問什麼？', '誰負責講反方？講了嗎？'),
    ('已經投了這麼多', '走到一半的案子，怎麼開口說停？', '如果今天才第一次看到它，還會投嗎？'),
]
CHECKLIST = [
    '同類的案子，後來做到幾成？',
    '這份預測裡，最樂觀的假設是哪一個？',
    '誰負責講反方？講了嗎？',
    '如果一年後它失敗了，最可能的原因是什麼？',
    '如果今天才第一次看到它，還會投嗎？',
    '還沒開口的人，問過了嗎？',
]

CSS = '''
/* bd:css */
.bd-fig{margin:6px 0 4px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:10px 10px 4px}
.bd-fig svg{display:block;width:100%;height:auto}
.bd-fig .road{fill:var(--sky)} .bd-fig .lane{stroke:var(--line);stroke-width:2;stroke-dasharray:14 12}
.bd-fig .see{fill:var(--blue)} .bd-fig .blind{fill:var(--peach)}
.bd-fig .me{fill:var(--navy)} .bd-fig .glass{fill:var(--sky)} .bd-fig .mirror{fill:var(--navy)}
.bd-fig .other{fill:var(--card);stroke:var(--orange);stroke-width:3}
.bd-fig .oglass{fill:none;stroke:var(--orange);stroke-width:2}
.bd-fig .q{fill:var(--orange);font-weight:900;font-size:30px}
.bd-fig .lab{fill:var(--navy-text);font-size:17px;font-weight:700}
.bd-fig .lab.o{fill:var(--accent-ink)} .bd-fig .lab.m{fill:var(--mute);font-weight:500;font-size:15px}
.bd-fig .turn{fill:none;stroke:var(--orange);stroke-width:3;stroke-linecap:round;stroke-dasharray:2 8}
.bd-fig .tip{fill:var(--orange)} .bd-fig .lead-line{stroke:var(--accent-ink);stroke-width:1.5;fill:none}
.pg-bd h1 .nb{display:inline-block}
.bd-cap{color:var(--mute);font-size:14.5px;margin:8px 2px 0}
.bd-qs{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0 10px}
.bd-q{display:flex;flex-direction:column;gap:8px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 16px 14px}
.bd-q .z{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:700;color:var(--accent-ink)}
.bd-q .z i{font-style:normal;width:24px;height:24px;border-radius:50%;background:var(--orange);color:#fff;display:grid;place-items:center;font-size:13px;flex:0 0 24px}
.bd-q b{font-size:17.5px;line-height:1.45;color:var(--navy-text)}
.bd-q .ask{margin-top:auto;border-top:1px dashed var(--line);padding-top:9px;font-size:14px;line-height:1.55;color:var(--fg)}
.bd-q .ask small{display:block;color:var(--mute);font-size:12px;letter-spacing:.04em;margin-bottom:2px}
.bd-flow{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;list-style:none;padding:0;margin:12px 0 6px;font-size:14.5px}
.bd-flow li{background:var(--sky);color:var(--navy-text);border-radius:999px;padding:5px 13px}
.bd-flow li+li::before{content:"→";color:var(--mute);margin:0 8px 0 -14px;position:relative;left:-7px}
.bd-two{display:grid;grid-template-columns:1.05fr .95fr;gap:22px;align-items:start;margin-top:12px}
.bd-sheet{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:18px 20px 14px;box-shadow:5px 6px 0 var(--sky);position:relative}
.bd-sheet::before{content:"示意";position:absolute;top:14px;right:16px;font-size:12px;color:var(--accent-ink);border:1px solid var(--accent-ink);border-radius:4px;padding:0 6px}
.bd-sheet h3{margin:0 0 10px;font-size:16px;color:var(--navy-text);border-bottom:2px solid var(--navy-text);padding-bottom:8px}
.bd-sheet ul{list-style:none;margin:0;padding:0}
.bd-sheet li{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px solid var(--line);font-size:14.5px;line-height:1.5}
.bd-sheet li:last-child{border-bottom:0}
.bd-sheet li::before{content:"";flex:0 0 15px;height:15px;margin-top:3px;border:1.5px solid var(--mute);border-radius:3px}
.bd-sheet li:nth-child(1)::before,.bd-sheet li:nth-child(3)::before{background:var(--orange);border-color:var(--orange);box-shadow:inset 0 0 0 2.5px var(--card)}
.bd-do{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.bd-do>div{border:1px solid var(--line);border-radius:14px;padding:14px 16px;background:var(--card)}
.bd-do h3{margin:0 0 6px;font-size:15px;color:var(--navy-text)}
.bd-do>div+div h3{color:var(--mute)}
.bd-do ul{margin:0;padding-left:1.1em;font-size:14.5px;line-height:1.7}
.bd-facts{margin:10px 0 0;padding-left:1.1em;line-height:1.8}
.bd-cta{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin:18px 0 0}
.bd-cta .btn{display:inline-block;background:var(--orange);color:#fff;font-weight:700;border-radius:999px;padding:12px 24px;text-decoration:none}
.bd-strip{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;margin:12px 0 0;padding:13px 18px;border:1px solid var(--line);border-left:4px solid var(--navy);border-radius:10px;background:var(--card);text-decoration:none;color:var(--navy-text)}
.bd-strip:hover{border-color:var(--orange);border-left-color:var(--orange)}
.bd-strip small{font-size:12.5px;font-weight:700;color:var(--accent-ink)}
.bd-strip b{font-size:16.5px} .bd-strip span{margin-left:auto;color:var(--orange);font-weight:700;font-size:13px}
@media (max-width:700px){.bd-qs,.bd-two,.bd-do{grid-template-columns:1fr}.bd-fig .lab{font-size:27px}.bd-fig .lab.m{font-size:23px}.bd-flow{flex-direction:column;align-items:flex-start}.bd-flow li+li::before{content:"↓";position:absolute;left:14px;top:-19px;margin:0}.bd-flow li{position:relative}.bd-flow{gap:20px}}
/* /bd:css */
'''
css = re.sub(r'\n/\* bd:css \*/.*?/\* /bd:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

# 主圖：俯視。我們的車朝右；後照鏡往後看到兩片（藍），緊貼車側後方那一塊照不到（橘），裡面有一台車。
SVG = '''<svg viewBox="0 0 720 300" role="img" aria-label="俯視圖：一台車的兩面後照鏡各照到後方一片區域；緊貼車身側後方有一塊照不到，那裡有另一台車。駕駛回頭看一眼才看得到。">
<rect class="road" x="0" y="14" width="720" height="272" rx="10"/>
<line class="lane" x1="0" y1="104" x2="720" y2="104"/><line class="lane" x1="0" y1="196" x2="720" y2="196"/>
<polygon class="see" points="470,121 20,100 20,14 108,14"/>
<polygon class="see" points="470,179 20,200 20,286 108,286"/>
<polygon class="blind" points="470,121 108,14 402,14"/>
<polygon class="blind" points="470,179 108,286 402,286"/>
<rect class="other" x="300" y="34" width="112" height="50" rx="12"/>
<rect class="oglass" x="382" y="42" width="16" height="34" rx="4"/><rect class="oglass" x="314" y="44" width="11" height="30" rx="3"/>
<text class="q" x="353" y="70" text-anchor="middle">?</text>
<rect class="me" x="380" y="122" width="128" height="56" rx="14"/>
<rect class="glass" x="462" y="130" width="20" height="40" rx="5"/><rect class="glass" x="398" y="132" width="14" height="36" rx="4"/>
<rect class="mirror" x="462" y="114" width="12" height="9" rx="2"/><rect class="mirror" x="462" y="177" width="12" height="9" rx="2"/>
<path class="turn" d="M446 140 C 440 112, 424 96, 404 90"/>
<polygon class="tip" points="398,88 411,84 408,97"/>
<text class="lab" x="34" y="72">後照鏡看得到</text>
<text class="lab" x="34" y="246">後照鏡看得到</text>
<text class="lab o" x="528" y="52">照不到的地方</text>
<path class="lead-line" d="M522 46 L 424 46"/>
<text class="lab o" x="528" y="100">回頭看一眼</text>
<path class="lead-line" d="M522 94 L 452 104"/>
<text class="lab m" x="528" y="246">你的車</text>
<path class="lead-line" d="M522 240 L 500 182" style="stroke:var(--mute)"/>
</svg>'''

qs = ''.join(f'<div class="bd-q"><span class="z"><i>{i}</i>{esc(z)}</span><b>{esc(t)}</b>'
             f'<span class="ask"><small>會前多問這一句</small>{esc(a)}</span></div>' for i, (z, t, a) in enumerate(QUESTIONS, 1))
sheet = ''.join(f'<li>{esc(x)}</li>' for x in CHECKLIST)
MAIL = 'mailto:george.chen@propelaigrowth.com?subject=' + '%E5%A4%A7%E6%B1%BA%E5%AE%9A%E4%B9%8B%E5%89%8D%EF%BC%9A%E6%83%B3%E6%8E%92%E4%B8%80%E5%A0%B4'

body = f'''<span class="pill">給董事、獨立董事與高階主管</span>
<h1><span class="nb">大決定之前，</span><span class="nb">該問的都問了嗎？</span></h1>
<p class="lead">{esc(SUB)}</p>
<figure class="bd-fig">{SVG}</figure>
<p class="bd-cap">開車的人都知道後照鏡有照不到的地方，所以變換車道前會回頭看一眼。大決定也有這樣的地方。</p>

<section class="sec">
<h2>最怕的，是不知道自己漏了什麼</h2>
<p>併購、大額投資、進新市場、收掉一條產品線——這種決定一年沒有幾次，後果卻要好幾年才看得清楚。</p>
<p>案子送上會議桌時，數字算過了，簡報做好了，大家也都說好。讓人不安的不是哪一題答錯，而是有沒有哪一題根本沒被問到。</p>
</section>

<section class="sec">
<h2>漏看，不是能力問題</h2>
<p>坐在駕駛座上，就是有一塊看不到，換誰來開都一樣。研究決策的人，已經把這種「人人都有、位置固定」的盲點整理出來。知道在哪裡，就能在表決前安排一個回頭看的動作。</p>
<p>我們平常幫企業做的，是把每天都在發生的小決定安排得更容易做對。這堂課用同一套科學，看很少發生、後果很大的決定。</p>
</section>

<section class="sec">
<h2>三個盲點區，各練一題</h2>
<div class="bd-qs">{qs}</div>
<p>每一題的走法都一樣：</p>
<ol class="bd-flow"><li>現場親自做一次小實驗</li><li>看研究怎麼說</li><li>勾一個你會先問的問題</li><li>放進你們的會前資料</li></ol>
<p>每一題最後還有一段：議案交給 AI 之前怎麼問，拿到 AI 的建議之後怎麼看。</p>
</section>

<section class="sec">
<h2>帶走一張會前檢核表</h2>
<div class="bd-two">
<div><p>課堂上勾出來的問題，最後收成一張表，放在議案資料的第一頁。下一次大決定表決前，照著問一遍。</p>
<p>表上的題目會依你們的議案格式調整；這裡看到的是示意。</p></div>
<div class="bd-sheet"><h3>大決定・會前檢核表</h3><ul>{sheet}</ul></div>
</div>
</section>

<section class="sec">
<h2>這堂課做什麼、不做什麼</h2>
<div class="bd-do">
<div><h3>做</h3><ul><li>把研究上已知的盲點區，逐一看過一遍</li><li>用公開資料上發生過的事當例子</li><li>讓你們帶一張表回去用</li></ul></div>
<div><h3>不做</h3><ul><li>不保證決定一定對</li><li>不教法律，不談董事責任怎麼認定</li><li>不評論個別公司或個人的對錯</li></ul></div>
</div>
</section>

<section class="sec">
<h2>怎麼排</h2>
<ul class="bd-facts">
<li>先從一小時開始：一個盲點區，完整走一遍。</li>
<li>三題完整版另談。</li>
<li>可以排成董事進修的一堂、經營團隊年度會議前的一堂，或高階主管場。</li>
<li>進修時數是否認列，以主辦機構審核為準。</li>
<li>費用與場次，來信談。</li>
</ul>
<div class="bd-cta"><a class="btn" href="{MAIL}">寫信談一場</a><a class="more" href="/how/">先看我們怎麼看問題 →</a></div>
</section>'''

tpl = rd('about/index.html')
tpl = re.sub(r'<!-- aeo:ld -->.*?<!-- /aeo:ld -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<!-- wf:top -->.*?<!-- /wf:top -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', tpl)
HEAD, REST = tpl[:tpl.index('<main>') + 6], tpl[tpl.index('</main>'):]
h = HEAD
h = re.sub(r'<title>.*?</title>', f'<title>{esc(TITLE)}｜Propel AI 啟進智能決策</title>', h)
h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(DESC), h)
h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(TITLE) + '｜Propel AI', h)
h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(DESC), h)
h = h.replace(f'{SITE}/about/', SITE + URL).replace('class="pg-about"', 'class="pg-bd"')
wr('big-decisions/index.html', h + '\n' + body + '\n' + REST)

# 首頁「課程」那段底下加一條入口（冪等）；/courses/ 由 wayfinding_patch 取同一條
STRIP = ('<!-- bd:home --><a class="bd-strip" href="/big-decisions/"><small>給董事、獨立董事與高階主管</small>'
         f'<b>{esc(TITLE)}</b><span>看這堂課 →</span></a><!-- /bd:home -->')
home = re.sub(r'\s*<!-- bd:home -->.*?<!-- /bd:home -->', '', rd('index.html'), flags=re.S)
m = re.search(r'(<section class="sec" id="courses">.*?<div class="links">.*?</div>)', home, re.S)
if m: wr('index.html', home[:m.end()] + '\n      ' + STRIP + home[m.end():])
sm = rd('sitemap.xml')
if URL not in sm: wr('sitemap.xml', sm.replace('</urlset>', f'  <url><loc>{SITE}{URL}</loc></url>\n</urlset>'))
print('big_decisions_page: /big-decisions/ 已產生；首頁課程段加入口；sitemap 已補')
