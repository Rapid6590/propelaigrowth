# propelaigrowth.com v0.1 — static site built from the 入口頁 sources
import re, pathlib, base64, json, shutil, html
H = pathlib.Path(__file__).parent.parent / 'hub'      # hub sources
S = pathlib.Path(__file__).parent.parent               # scratchpad
OUT = pathlib.Path(__file__).parent / 'out'
if OUT.exists(): shutil.rmtree(OUT)
(OUT/'assets/img').mkdir(parents=True); (OUT/'pdf').mkdir()

src = (H/'index.html').read_text(encoding='utf-8')
HUB_CSS = src[src.index('<style>')+7 : src.index('</style>')]
# drop hub-only navigation css bits that no longer apply
HUB_CSS = HUB_CSS.replace('[data-go],[data-prev],[data-scroll]{cursor:pointer}\n','').replace('a[data-go],a[data-prev],a[data-scroll]{color:inherit}\n','').replace('.choice[data-go]:hover{border-color:var(--orange)}','.choice:hover{border-color:var(--orange)}')

SITE = 'https://propelaigrowth.com'
PREVIEW = False  # True: 首頁放「準備中」，整站搬到 /preview/ 之下不被索引；False: 正式公開
OGIMG = {'quiz':'og_quiz.png'}
URL = {'home':'/preview/' if PREVIEW else '/', 'trial':'/trial/', 'half':'/half-day/', 'ws':'/workshop/', 'surf':'/surf/', 'how':'/how/',
       'quiz':'/quiz/', 'picker':'/picker/', 'docs':'/downloads/',
       'trial-prep':'/trial/prep/', 'half-prep':'/half-day/prep/', 'ws-prep':'/workshop/prep/', 'surf-prep':'/surf/prep/',
       'about':'/about/', 'contact':'/contact/', 'articles':'/articles/', 'clients':'/clients/'}
TITLE = {'home':'Propel AI 啟進智能決策｜講了三次，他還是沒做？', 'trial':'59 分鐘試駕', 'half':'半天課・全天課', 'ws':'全天工作坊', 'surf':'SURF™ 原廠班',
         'how':'我們怎麼看問題', 'quiz':'兩分鐘小測驗', 'picker':'選題器', 'docs':'課程介紹下載',
         'trial-prep':'59 分鐘試駕 課前說明', 'half-prep':'半天課・全天課 課前說明', 'ws-prep':'全天工作坊 課前說明', 'surf-prep':'SURF™ 原廠班 課前說明',
         'about':'關於 Propel AI', 'contact':'聯絡我們', 'articles':'文章', 'clients':'客戶怎麼說'}
DESC = {'home':'用行為經濟學和 AI，先不急著加預算，讓你想要的行為更容易發生。企業培訓與工作坊：59 分鐘試駕、半天課・全天課、全天工作坊、SURF™ 原廠班。',
        'trial':'59 分鐘到你公司上：一個小實驗、一題半天課、寫下你最想先讓誰做什麼。NT$ 8,900（未稅），上限 30 人。',
        'half':'用你本來就在做的決定當題目：半天六題、全天十二題，每題一個規律、三個案例、一次判斷、一段 AI 提示詞。',
        'ws':'帶一個推不動的痛點來，走五站，當場拍板一個兩週內看得到數字的小試驗。每場上限 16 人。',
        'surf':'歐洲 MINDWORX 的方法，主題只有一個：怎麼讓客戶說 YES。台灣授權講師中文授課，發原廠結業證書。',
        'how':'數字是結果；可以動手的是行為。環境→行為→指標，每個指標背後都是一條行為鏈。',
        'quiz':'三題、用點的、不用留資料。看看那件推不動的事能不能用這個方法處理。',
        'picker':'三題答完，落到你的模組。十六個主題、四個現成組合。',
        'docs':'一頁介紹 PDF：59 分鐘試駕、半天課・全天課、全天工作坊、SURF™ 原廠班、PROPEL 六站。'}

# ---------- views ----------
markers = [(m.start(), m.group(1)) for m in re.finditer(r'  <!-- ===== ([A-Z /:a-z]+) ===== -->', src)]
footer_pos = src.index('  <footer>Propel AI')
views = {}
keymap = {'HOME':'home','TRIAL':'trial','HALF / FULL DAY':'half','WORKSHOP':'ws','SURF':'surf','HOW':'how','QUIZ':'quiz','PICKER':'picker','DOCS':'docs',
          'PREP: trial':'trial-prep','PREP: half':'half-prep','PREP: ws':'ws-prep','PREP: surf':'surf-prep'}
for i,(pos,name) in enumerate(markers):
    end = markers[i+1][0] if i+1 < len(markers) else footer_pos
    views[keymap[name]] = src[pos:end]

def strip_section(v):
    v = re.sub(r'\s*<!-- ===== [^>]+ -->\n', '', v, count=1)
    v = re.sub(r'^\s*<section class="view[^"]*" id="v-[a-z-]+"( hidden)?>\n', '', v)
    v = re.sub(r'\n  </section>\s*$', '\n', v)
    return v

def links(v):
    v = re.sub(r'data-go="([a-z-]+)" role="link" tabindex="0"', lambda m: f'href="{URL[m.group(1)]}"', v)
    v = re.sub(r'data-prev="([a-z-]+)" role="link" tabindex="0"', lambda m: f'href="{URL[m.group(1)]}"', v)
    v = re.sub(r'data-scroll="([a-z-]+)" role="link" tabindex="0"', lambda m: f'href="#{m.group(1)}"', v)
    return v

img_n = [0]
def extract_images(v, prefix):
    def rep(m):
        mime, b64 = m.group(1), m.group(2)
        ext = {'image/png':'png','image/jpeg':'jpg','image/svg+xml':'svg'}[mime]
        img_n[0]+=1; name=f'{prefix}-{img_n[0]:02d}.{ext}'
        (OUT/'assets/img'/name).write_bytes(base64.b64decode(b64))
        return f'src="/assets/img/{name}"'
    return re.sub(r'src="data:([a-z/+]+);base64,([A-Za-z0-9+/=]+)"', rep, v)

# ---------- chrome ----------
NAV = [('/#pain','痛點'),('/how/','怎麼看問題'),('/#method','方法'),('/#courses','課程'),('/about/','為什麼是我們'),('/articles/','文章'),('/contact/','聯絡')]
SITE_CSS = '''
/* ---- site chrome ---- */
.sitehead{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:18px}
.sitenav{display:flex;gap:4px;flex-wrap:wrap}
.sitenav a{color:var(--mute);text-decoration:none;font-size:14px;padding:6px 10px;border-radius:999px}
.sitenav a:hover,.sitenav a[aria-current]{color:var(--navy);background:var(--sky)}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) .sitenav a:hover, :root:not([data-theme="light"]) .sitenav a[aria-current]{color:var(--fg)} }
.sitefoot{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);font-size:13px;color:var(--mute);line-height:1.7}
.sitefoot a{color:var(--mute)}
.sitefoot .disc{font-size:12px;margin-top:8px}
.cta-row{display:grid;gap:10px;margin:18px 0}
.disc{font-size:12.5px;color:var(--mute);border-top:1px dashed var(--line);padding-top:10px;margin-top:14px}
.prep .pdisc{margin-top:10px;font-size:12px;color:var(--mute);border-top:1px dashed var(--line);padding-top:10px}
.dl .acts a{display:inline-block;font:inherit;font-size:14px;font-weight:700;border-radius:8px;background:var(--orange);color:#fff;padding:8px 14px;text-decoration:none}
.dl .acts a.view{background:var(--card);color:var(--fg);border:1px solid var(--line)}
.empty{background:var(--sky);border-radius:12px;padding:16px;color:var(--mute);font-size:14px}
.btn[aria-disabled]{opacity:.55;pointer-events:none}
/* ---- home long page ---- */
.sec{margin:34px 0 0;padding-top:22px;border-top:1px solid var(--line)}
.sec .eyebrow{margin-bottom:4px}
.sec h2{margin:0 0 6px;font-size:22px}
.sec .sub{color:var(--mute);margin:0 0 14px;font-size:15px}
.pains{display:grid;gap:10px;margin:0 0 14px}
.pain{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.pain b{display:block;font-size:16px;margin-bottom:4px}
.pain span{color:var(--mute);font-size:14px}
.pain .k{display:inline-block;font-size:12px;color:var(--orange);font-weight:700;margin-bottom:4px}
.big{background:var(--navy);color:var(--navy-fg);border-radius:12px;padding:14px 16px;font-weight:700;font-size:16px;margin:14px 0}
.vs{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:0 0 14px}
.vs .card ul{margin:6px 0 0;padding-left:18px;color:var(--mute);font-size:14px}
.vs .card.us{border-color:var(--orange)}
.more{display:inline-block;margin:4px 0 0;color:var(--orange);font-weight:700;text-decoration:none}
.more:hover{text-decoration:underline}
.stations{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:0 0 14px}
.stations .st{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;min-width:0}
.stations .st b{display:block;color:var(--orange);font-size:18px;line-height:1.1}
.stations .st i{display:block;font-style:normal;font-weight:700;font-size:13px;margin:2px 0 4px}
.stations .st span{display:block;color:var(--mute);font-size:13px}
.mods{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:0 0 14px}
.mods .card ul{margin:6px 0 0;padding-left:18px;font-size:14px}
.mods .card .n2{font-size:12px;color:var(--mute)}
.creds{list-style:none;padding:0;margin:0 0 12px;display:grid;gap:6px;font-size:14px}
.creds li{display:grid;grid-template-columns:6.5em 1fr;gap:10px}
.creds b{color:var(--orange)}
@media (max-width:480px){.creds li{grid-template-columns:1fr}.stations{grid-template-columns:1fr 1fr}}
'''

def page(key, body, title=None, desc=None, extra_head='', wrap=True, nav_current=None, noindex=False):
    title = title or TITLE[key]; desc = desc or DESC.get(key, DESC['home'])
    full = title if key=='home' else f'{title}｜Propel AI 啟進智能決策'
    url = SITE + URL[key]
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if (nav_current or URL[key])==h else ""}>{t}</a>' for h,t in NAV)
    head = f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
{'<meta name="robots" content="noindex,nofollow">' if (noindex or PREVIEW) else ''}
<meta property="og:type" content="website"><meta property="og:site_name" content="Propel AI 啟進智能決策">
<meta property="og:title" content="{html.escape(full)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/assets/{OGIMG.get(key,"og.png")}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap">
<link rel="stylesheet" href="/assets/site.css">
{extra_head}
</head>
<body>
<div class="wrap">
  <header class="sitehead">
    <a class="wordmark" href="{URL['home']}">PROPEL AI<small>啟進智能決策｜行為經濟學 × 行為設計 × AI</small></a>
    <nav class="sitenav" aria-label="主選單">{nav}</nav>
  </header>
<main>
'''
    foot = '''
</main>
  <footer class="sitefoot">
    <div><b>Propel AI｜啟進智能決策有限公司</b>｜台北市忠孝東路五段 1-2 號 12 樓｜<a href="mailto:george.chen@propelaigrowth.com">george.chen@propelaigrowth.com</a>｜<a href="https://www.linkedin.com/in/digitalgeorge" rel="noopener" target="_blank">LinkedIn</a></div>
    <div>歐洲 MINDWORX SURF™ Method 授權講師與教練｜未經同意，不做後續推銷。</div>
    <div class="disc">課程頁與課前說明為課前說明，實際安排以報價單與開課前確認為準；本公司保留調整課程內容與進行方式之權利。</div>
  </footer>
</div>
</body>
</html>
'''
    return head + body + foot

def write(path, content):
    if PREVIEW:
        content = content.replace('href="/"', 'href="/preview/"').replace('href="/#courses"', 'href="/preview/#courses"')
    p = OUT / path.lstrip('/'); p.mkdir(parents=True, exist_ok=True)
    (p/'index.html').write_text(content, encoding='utf-8')

(OUT/'assets/site.css').write_text(HUB_CSS + SITE_CSS, encoding='utf-8')

# ---------- content pages from hub views ----------
bodies = {}
for key in ['trial','half','ws','surf','how','trial-prep','half-prep','ws-prep','surf-prep']:
    v = links(strip_section(views[key]))
    v = extract_images(v, key)
    bodies[key] = v
    if key.endswith('-prep'):
        v = f'<div class="prep">{v}</div>'
    write(URL[key], page(key, v))

# home: long page that follows the 公司簡介 storyline (v0.2)
how_body = bodies['how']
import re as _re
_ex1 = _re.search(r'<div class="exi">.*?</div></div></div>', how_body, _re.S).group(0)
_ex = '<div class="ex">'+_ex1+'</div><p class="note">外部研究，非 Propel AI 客戶實績｜出處：Ebeling &amp; Lotz (2015) Nature Climate Change</p>'
home = f"""
    <p class="eyebrow">講了三次，他還是沒做？</p>
    <h1>先不急著加預算，讓你想要的行為更容易發生</h1>
    <p class="lead">從客戶遲遲不做決定，到員工沒有採用新工具。我們帶你的團隊找出關鍵行為卡點，設計出可以測試的改善方案——改環境，不改人。</p>
    <div class="cta"><a class="btn primary" href="/quiz/">還不確定？兩分鐘小測驗</a><a class="btn secondary" href="/trial/">想先試一次：59 分鐘試駕</a></div>

    <section class="sec" id="pain">
      <p class="eyebrow">01　你的企業問題</p>
      <h2>你也卡在這裡嗎？</h2>
      <p class="sub">「今年不能再加人、加預算，業績還是要成長。」底下三句，是它最常見的樣子；有一句像的，就值得往下看。</p>
      <div class="pains">
        <div class="pain"><span class="k">不買、不回、不續</span><b>「提案做得再好，客戶還是說我再想想。」</b><span>卡在這一步：客戶收到提案後，沒有在約定時間確認下一步</span></div>
        <div class="pain"><span class="k">AI、數位轉型</span><b>「AI 工具買了，規矩訂了，就是沒人用。」</b><span>卡在這一步：員工開始日常工作時，沒有打開 AI 工具</span></div>
        <div class="pain"><span class="k">營運、品保、人資</span><b>「SOP 寫得很清楚，現場還是照舊。」</b><span>卡在這一步：現場交接時，沒有完成指定的檢核動作</span></div>
      </div>
      <div class="big">這幾句講的是同一件事：你想要的行為，沒有發生。</div>
      <p class="sub">你關心的每個指標背後，都是一條行為鏈——指標在最右邊，你撥不動；能動手的，永遠是中間那一格。</p>
      <table>
        <tr><th>在這個時刻</th><th>這個人做了這個動作</th><th>這個指標才會動</th></tr>
        <tr><td>客戶收到提案之後</td><td>在約定時間確認下一步</td><td>成交率</td></tr>
        <tr><td>業務準備開始日常工作時</td><td>打開 AI 做企畫</td><td>採用率</td></tr>
        <tr><td>現場每一次交接時</td><td>完成指定的檢核動作</td><td>SOP 執行率</td></tr>
      </table>
    </section>

    <section class="sec" id="how">
      <p class="eyebrow">02　我們怎麼看問題</p>
      <h2>數字是結果；可以動手的是行為</h2>
      <p class="sub">指標像速度表，指針撥不動；想讓車子快一點，要先找到油門。打開 AI、照 SOP 做，是油門；多一道登入、多一張表單，是煞車。油門踩不下去，常是煞車沒鬆。</p>
      <div class="chain">
        <div class="c"><b>環境</b>他看到什麼、要做幾步、預設是什麼<br><span class="note">我們多看的一步</span></div><div class="ar">▶</div>
        <div class="c"><b>行為</b>特定的人，在特定的時刻，做一個看得見的動作<br><span class="note">可以動手的地方</span></div><div class="ar">▶</div>
        <div class="c"><b>指標</b>業績、採用率、回購率<br><span class="note">行為動了，它才會動</span></div>
      </div>
      <div class="quote"><b>行為不只由人決定，很大一部分由環境決定——而環境，是你可以事先安排的。</b>我們不再多說服一次，而是改他做決定那一刻的環境。</div>
      <div class="vs">
        <div class="card"><h3>常見的做法</h3><ul><li>講道理：「這樣對你比較好」</li><li>下命令：「這是規定」</li><li>重複宣導：「再提醒一次」</li><li>獎勵與處罰</li></ul><p>都用得上，但力氣一停，數字常掉回來。</p></div>
        <div class="card us"><h3>我們的做法</h3><ul><li>把他第一眼看到的，換成你最想他選的</li><li>少一個欄位、少一步，他就走得完</li><li>預設先幫他選好；不要的人自己取消</li><li>在他正要做的那一刻提醒一次</li></ul><p>改一張表、一封信、一個流程——改一次，之後每個人經過的都是新流程。</p></div>
      </div>
      <h3>改環境，長什麼樣子？一個例子</h3>
      <p class="sub">同一個方案、同一個價格，只換了預設。同樣的東西換個擺法，數字差一截；我們把它做成你用得上的工件。</p>
      {_ex}
      <a class="more" href="/how/">還有兩個例子與完整說明：我們怎麼看問題 →</a>
    </section>

    <section class="sec" id="method">
      <p class="eyebrow">03　我們的方法</p>
      <h2>PROPEL：從模糊問題到可測試方案</h2>
      <p class="sub">像醫師問診：「業績不好」「員工不配合」是症狀，不是病因。先問診、逐步排除、找出病因，再開藥——六個字母，六站。是流程，不是軟體。</p>
      <div class="stations">
        <div class="st"><b>P</b><i>Pinpoint</i><span>把商業問題翻成特定的人、時刻、看得見的動作</span></div>
        <div class="st"><b>R</b><i>Reconstruct</i><span>還原他實際走的路，看斷在哪一步</span></div>
        <div class="st"><b>O</b><i>Obstacle</i><span>用六問找出待驗證的障礙，排優先序</span></div>
        <div class="st"><b>P</b><i>Prescribe</i><span>對準卡點，挑一個可以測試的介入</span></div>
        <div class="st"><b>E</b><i>Experiment</i><span>定比較方式、指標、看多久</span></div>
        <div class="st"><b>L</b><i>Loop</i><span>回公司看數字，修正判斷與下一步</span></div>
      </div>
      <div class="vs">
        <div class="card"><h3>先行為，後預算</h3><p>能靠改習慣解決的，就先不動手術。先試低成本的行為介入，小範圍看到數字，再談放大投資。</p></div>
        <div class="card"><h3>互補，不取代</h3><p>你原本的業務訓練、管理制度、獎勵辦法都有用，照用；我們補的是那一步沒發生時，怎麼改他旁邊的環境。</p></div>
      </div>
      <h3>每一題怎麼上：AI 是第二意見，決定權在人</h3>
      <ol class="steps">
        <li><div><b>先用現場經驗寫下自己的判斷</b><p>一個決定、一條規律、三個案例，再換你替一個情境做決定。</p></div></li>
        <li><div><b>AI 補盲點、提出其他可能假設</b><p>背後是整理好的 67 種常見卡點與 101 種改法。</p></div></li>
        <li><div><b>講師帶你對照研究與現場，一起篩掉不合用的</b><p>AI 提的，先當假設。</p></div></li>
        <li><div><b>你核對後自行拍板</b><p>帶一段 AI 提示詞回去，貼上自己的報價單、申請表或交辦，繼續練。</p></div></li>
      </ol>
    </section>

    <section class="sec" id="courses">
      <p class="eyebrow">04　合作方式</p>
      <h2>從培訓到實作，依你的需求選擇</h2>
      <p class="sub">不用先買最完整的方案；先從最輕的開始，之後往深走，路上的經驗直接帶過去。建議起點：59 分鐘試駕。已經有明確題目的，直接談模組課或工作坊。</p>
      <div class="menu">
        <a class="choice hot" href="/trial/"><span><span class="q">想先試一次、再決定 <span class="tag">建議起點</span></span><span class="a">59 分鐘試駕｜先看懂我們怎麼看問題，再從半天課抽一題實際上一次。到你公司上，最多 30 人</span></span><span class="go">→</span></a>
        <a class="choice" href="/half-day/"><span><span class="q">想把幾個具體決定做得更好</span><span class="a">半天課・全天課｜半天六題、全天十二題；每題練一個決定，含講義與 AI 提示詞</span></span><span class="go">→</span></a>
        <a class="choice" href="/workshop/"><span><span class="q">想把方法留在組織裡</span><span class="a">全天工作坊｜上半段看懂道理，下半段帶自己的痛點走 PROPEL；帶走一份最小試驗設計</span></span><span class="go">→</span></a>
        <a class="choice" href="/surf/"><span><span class="q">行銷業務團隊，要原廠方法與證書</span><span class="a">SURF™ 原廠班｜歐洲 MINDWORX 原廠課程，中文授課，含原廠結業證書</span></span><span class="go">→</span></a>
      </div>
      <h3 style="margin-top:18px">課程模組都用你的痛點命名</h3>
      <div class="mods">
        <div class="card"><h3>你想讓誰改變：客人</h3><div class="n2">不買、不回、不續</div><ul><li>價格怎麼開、怎麼談</li><li>加了購物車，沒結帳</li><li>客人說「我再想想」，然後就沒下文</li><li>產品賣出去了，客戶卻沒在用</li></ul></div>
        <div class="card"><h3>你想讓誰改變：員工</h3><div class="n2">不用、不照做、不帶</div><ul><li>工具買了、規矩訂了，沒人照做</li><li>新人來了，沒人帶</li><li>客訴來了，客服卻各回各的</li></ul></div>
        <div class="card"><h3>你想讓誰改變：民眾</h3><div class="n2">不來辦、不配合</div><ul><li>讓民眾辦得成</li></ul></div>
      </div>
      <p class="sub">不知道挑哪些？<a class="more" href="/picker/">用選題器，三題答完落到你的模組 →</a>　或 <a class="more" href="/downloads/">下載課程介紹（PDF）→</a></p>
    </section>

    <section class="sec" id="why">
      <p class="eyebrow">05　為什麼是 Propel AI</p>
      <h2>從行為經濟學研究到企業可執行的決策，中間那一步由我們完成</h2>
      <div class="who"><div class="av">G</div><div><h3>George Chen｜創辦人・行為經濟學與行為設計顧問</h3><p>在 Oracle 任職期間取得芝加哥大學 Booth 商學院 MBA，期間上了「行為經濟學之父」Richard Thaler 的課，從此投入這個領域。之後在 Oracle 多年，處理的是同一個問題：怎麼讓潛在客戶採取下一步。</p></div></div>
      <ul class="creds">
        <li><b>學位</b><span>芝加哥大學 Booth 商學院 MBA（With Honors，前 20% 畢業）；修過 2017 諾貝爾經濟學獎得主 Richard Thaler 的課</span></li>
        <li><b>經歷</b><span>Oracle 香港／台灣區行銷總監；Oracle 人力資源產品線亞太區行銷總監</span></li>
        <li><b>行為經濟學</b><span>Chicago Booth 高階主管教育「行為經濟學」；Irrational Labs 訓練營結業；歐洲 MINDWORX SURF™ Method 授權講師與教練</span></li>
      </ul>
      <div class="quote"><b>我們的夥伴：歐洲 MINDWORX</b>2015 年成立於歐洲的行為經濟學顧問公司，現於歐洲與北美設點；服務過 Allianz、Generali、UniCredit、Zurich 等集團旗下公司。SURF™ 是 MINDWORX 的方法，我們是授權講師與教練；Propel AI 的課與工作坊，用的是我們自己的 PROPEL 流程。<span class="note">上列為 MINDWORX 的客戶背景，不是 Propel AI 的客戶實績。</span></div>
      <a class="more" href="/about/">完整資歷（AI、設計與體驗、教學與引導）與我們的三不信條 →</a>
    </section>

    <section class="sec" id="next">
      <p class="eyebrow">06　下一步</p>
      <h2>從一個你想推動的行為開始</h2>
      <p class="sub">說一件你最想推動的事：誰？在什麼時候？希望完成什麼動作？一句話就夠。我們先看哪個行為值得處理，再談適合的合作方式；不適合，我們會直說。</p>
      <div class="cta"><a class="btn primary" href="mailto:george.chen@propelaigrowth.com?subject=%E6%88%91%E6%9C%80%E6%83%B3%E6%8E%A8%E5%8B%95%E7%9A%84%E4%B8%80%E4%BB%B6%E4%BA%8B">寫信說一件事</a><a class="btn secondary" href="/contact/">約 30 分鐘電話</a><a class="btn secondary" href="/quiz/">還不確定？兩分鐘小測驗</a></div>
      <div class="contact">
        <p><b>啟進智能決策有限公司 Propel AI</b>｜George Chen（創辦人）</p>
        <p>Email <code>george.chen@propelaigrowth.com</code>　台北市忠孝東路五段 1-2 號 12 樓</p>
        <p>未經同意，不做後續推銷。</p>
      </div>
    </section>
"""
write(URL['home'], page('home', home, nav_current='/'))

# ---------- downloads ----------
DOCS = [
 ('trial','59 分鐘試駕　一頁介紹','正面：59 分鐘你會經歷的三件事、帶走什麼、費用與折抵。背面：我們怎麼看問題——三個改環境的例子，和「每個指標背後都是一條行為鏈」。','Propel_AI_59分鐘試駕_一頁介紹.pdf'),
 ('half','半天課・全天課　一頁介紹','半天六題、全天十二題，用你本來就在做的決定當題目：每題一個規律、三個案例、一次判斷、一段 AI 提示詞。背面是模組一覽與四個現成組合。','Propel_AI_半天課全天課_一頁介紹.pdf'),
 ('workshop','全天工作坊　一頁介紹','上午看懂行為的規律，下午帶你們自己的題目走五站，當場拍板一個兩週內看得到數字的小試驗。每場上限 16 人。','Propel_AI_全天工作坊_一頁介紹.pdf'),
 ('surf','SURF™ 原廠班　一頁介紹','歐洲 MINDWORX 的方法，主題只有一個：怎麼讓客戶說 YES。台灣授權講師中文授課，半天、全天都發原廠結業證書。','Propel_AI_SURF原廠班_一頁介紹.pdf'),
 ('propel','我們怎麼做：PROPEL 六站（兩頁）','第 1 頁：像看診一樣，先找出症狀背後卡在哪一步，再開處方。第 2 頁：從找行為到看數字的六站流程，工作坊就是照這條路走。','Propel_AI_PROPEL架構兩頁.pdf'),
]
rows=[]
for key,title,desc,fname in DOCS:
    shutil.copy(S/'docs/pdf'/f'{key}.pdf', OUT/'pdf'/fname)
    shutil.copy(S/'docs/img'/f'th_{key}.jpg', OUT/'assets/img'/f'th_{key}.jpg')
    size=(S/'docs/pdf'/f'{key}.pdf').stat().st_size//1024
    pages='A4 一頁，正反面' if key!='propel' else 'A4 兩頁'
    rows.append(f'''      <div class="dl"><img src="/assets/img/th_{key}.jpg" alt="{title} 縮圖"><div><h3>{title}</h3><p>{desc}</p><p class="meta">{pages}・PDF {size} KB</p><div class="acts"><a class="view" href="/pdf/{fname}" target="_blank" rel="noopener">線上看</a><a href="/pdf/{fname}" download>下載 PDF</a></div></div></div>''')
docs = f'''
    <span class="pill">課程介紹下載</span>
    <h1>一頁介紹，可以下載帶走</h1>
    <p class="lead">每份都是 A4 一頁的介紹，方便印出來、或轉給同事。要看更完整的說明，回首頁點各課程的介紹頁。</p>
    <div class="dlist">
{chr(10).join(rows)}
    </div>
    <p class="note">想分享給同事，直接傳這一頁的連結就好。</p>
    <p class="disc">各份介紹為課前說明，實際安排以報價單與開課前確認為準；本公司保留調整課程內容與進行方式之權利。</p>
    <div class="nav"><a href="/" class="prev">← 回首頁</a><a href="/contact/">約 30 分鐘電話 →</a></div>
'''
write('/downloads/', page('docs', docs))

# ---------- quiz & picker: standalone pages, re-wrapped ----------
def wrap_standalone(key, html_src, back_label):
    body = html_src.replace('https://claude.ai/artifact/3s8nnvSLSNKDmtqDSfrTQF', '/')
    body = body.replace('target="_blank" rel="noopener">Propel AI 入口頁', '>Propel AI 首頁')
    title_m = re.search(r'<title>(.*?)</title>', body); t = title_m.group(1) if title_m else TITLE[key]
    body = re.sub(r'<title>.*?</title>\n?', '', body)
    body = re.sub(r'<meta name="claude:[^>]+>\n?', '', body)
    body = body.replace('<div class="brand">', f'<div class="brand"><a href="/" style="color:var(--muted);text-decoration:none;font-size:13px;margin-right:8px">← 首頁</a>', 1)
    head = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(t)}｜Propel AI</title><meta name="description" content="{html.escape(DESC[key])}"><link rel="canonical" href="{SITE}{URL[key]}">
<meta property="og:title" content="{html.escape(t)}"><meta property="og:description" content="{html.escape(DESC[key])}"><meta property="og:image" content="{SITE}/assets/{OGIMG.get(key,"og.png")}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:url" content="{SITE}{URL[key]}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
</head><body>
'''
    return head + body + '\n</body></html>\n'
write('/quiz/', wrap_standalone('quiz', (H/'quiz_standalone.html').read_text(encoding='utf-8'), '首頁'))
write('/picker/', wrap_standalone('picker', (H/'picker_standalone.html').read_text(encoding='utf-8'), '首頁'))

# ---------- about ----------
about = '''
    <span class="pill">關於</span>
    <h1>我們做一件事：讓你想要的行為，更容易發生</h1>
    <p class="lead">提案做了，客戶卻遲遲沒有下一步；AI 工具買了，團隊卻沒有用起來；SOP 寫清楚了，現場還是照舊。Propel AI 透過企業培訓與工作坊，教團隊運用行為經濟學和 AI，找出客戶不往下談、同仁沒有行動的原因，再調整流程、訊息與做決定的環境。</p>
    <h2>為什麼是行為經濟學</h2>
    <p>企業很熟悉自己的銷售流程。但從客戶那一端看，他每一步要做什麼、擔心什麼、還需要誰點頭？這些客戶必須完成的事，不一定出現在我們的流程裡。行為經濟學講的就是這個：除了需求與意願，選項怎麼呈現、步驟有多麻煩、提醒怎麼出現，都會影響一個人的決定。</p>
    <p>過去，行為經濟學多由政府與大型企業聘顧問導入。一般企業也許聽過、也想試試看怎麼用在自己的生意上，但往往不知道從哪裡著手：學理讀起來需要時間，也缺一套可以直接拿來用的工具和工件，把研究發現接到工作上的步驟。我們這幾年做的，就是這一步——把行為經濟學的研究發現，轉成企業團隊能在工作上練習的步驟，再用實際數字觀察效果。</p>
    <h2>團隊在課堂上練習三件事</h2>
    <div class="cards">
      <div class="card"><div class="n">1</div><h3>拆成看得見的行動</h3><p>把「業績要成長」「工具要有人用」拆成誰、在什麼時候、做哪一個動作。</p></div>
      <div class="card"><div class="n">2</div><h3>找卡點，設計改法</h3><p>找出那個動作可能卡住的原因，設計一個先不急著加預算的改法。</p></div>
      <div class="card"><div class="n">3</div><h3>用自己的數字看效果</h3><p>小範圍試兩週，看數字，再決定留、改、或換一處。</p></div>
    </div>
    <p>過程中會用到我們自己開發的 AI 輔助工具，背後是整理好的 67 種常見卡點與 101 種改法。順序是固定的：團隊先想，AI 再補上可能漏看的地方，講師帶你看，最後由團隊決定。課程結束後，AI 還能繼續陪你練習——我們提供寫好的提示詞，回到公司，把自己的實際狀況貼進平常用的 AI 工具，就能照課堂上的原理和步驟再走一遍。</p>
    <h2>我們相信的三件事</h2>
    <div class="cards">
      <div class="card"><h3>不把結果當行為</h3><p>業績、採用率是結果；能動手的是誰在什麼時候做哪個動作。</p></div>
      <div class="card"><h3>不把人格當原因</h3><p>「他懶」「他不用心」不是卡點；先看那一步是不是太費力、太容易忘，或沒有人先做。</p></div>
      <div class="card"><h3>不把假設當結論</h3><p>改法先當假設，兩週小試驗看數字，再決定留、改、換。</p></div>
    </div>
    <h2>誰在做</h2>
    <div class="who"><div class="av">G</div><div><h3>George Chen 陳朝智｜創辦人</h3><p>「怎麼讓客戶願意往下走」，是他在 Oracle 多年一直面對的問題：負責過香港與台灣所有產品線的需求開發，也負責過大中華區的高科技產業，以及亞太區的人力資源產品線。有些產品是市場領導者，要讓客戶願意留下；有些是後進者，要讓客戶願意換掉原本的選擇。不同市場、不同競爭位置，都要先弄懂客戶為什麼願意、或不願意走下一步。</p></div></div>
    <p>在芝加哥大學 Booth 商學院取得 MBA 學位（With Honors，前 20% 畢業）時，他修了 Richard Thaler 的課——行為經濟學之父，後來獲得諾貝爾經濟學獎。那堂課讓他開始留意：除了需求與意願，選項怎麼呈現、步驟有多麻煩、提醒怎麼出現，都會影響一個人的決定。從那時起他就在想：讓事情發生的很大一部分是環境，而環境是可以事先安排的。</p>
    <h3 style="margin-top:18px">資歷與認證</h3>
    <ul class="facts">
      <li><b>學位</b><span>芝加哥大學 Booth 商學院 MBA（With Honors，前 20% 畢業）；修過 2017 諾貝爾經濟學獎得主 Richard Thaler 的課</span></li>
      <li><b>經歷</b><span>Oracle 香港／台灣區行銷總監；Oracle 人力資源產品線亞太區行銷總監</span></li>
      <li><b>行為經濟學</b><span>Chicago Booth 高階主管教育「行為經濟學」（2024）；Irrational Labs 訓練營結業；歐洲 MINDWORX SURF™ Method 授權講師與教練</span></li>
      <li><b>AI</b><span>密西根大學 Ross 商學院「生成式 AI 在企業」專項課程（Coursera，2025）；Google Cloud「生成式 AI 領導者」專業證書（Coursera，2025）</span></li>
      <li><b>創新與設計思考</b><span>Emeritus 創新與設計思考研究生文憑（Postgraduate Diploma）——與 MIT Sloan、哥倫比亞商學院、達特茅斯 Tuck 合辦</span></li>
      <li><b>UX 與顧客體驗</b><span>Parsons UX/UI、CX Academy 顧客體驗——所以解方做成你拿得到、能直接用的工件：一張表、一封信、一張提示詞</span></li>
      <li><b>教學與引導</b><span>ATD 微學習證書課程（2022）；Maven「The AI Bootcamp for L&amp;D」結業（授課者 Dr Philippa Hardman，劍橋大學學習科學家）；AD™ 加速式討論工作坊（引導，2026）</span></li>
    </ul>
    <p class="note">SURF™ 是 MINDWORX 的方法；Propel AI 的課程與工作坊是我們自己設計的架構。</p>
    <h2>公司</h2>
    <ul class="facts">
      <li><b>名稱</b><span>啟進智能決策有限公司（Propel AI）</span></li>
      <li><b>地址</b><span>台北市忠孝東路五段 1-2 號 12 樓</span></li>
      <li><b>聯絡</b><span>george.chen@propelaigrowth.com｜<a href="/contact/">約 30 分鐘電話</a></span></li>
    </ul>
    <div class="nav"><a href="/" class="prev">← 回首頁</a><a href="/how/">我們怎麼看問題 →</a></div>
'''
write('/about/', page('about', about, desc='Propel AI 啟進智能決策：把行為經濟學的研究發現，轉成企業團隊能在工作上練習的步驟，再用實際數字觀察效果。創辦人 George Chen。'))

# ---------- contact ----------
cfg = json.loads((pathlib.Path(__file__).parent/'config.json').read_text(encoding='utf-8')) if (pathlib.Path(__file__).parent/'config.json').exists() else {}
book = cfg.get('booking_url'); form = cfg.get('form_url')
contact = f'''
    <span class="pill">聯絡</span>
    <h1>先聊 30 分鐘，再決定要不要往下</h1>
    <p class="lead">說你那件推不動的事，我們告訴你可能卡在哪、從哪一個課程開始最省。不收費、不推銷；聊完覺得不適合，就到此為止。</p>
    <div class="cta-row">
      <a class="btn primary" href="{book or '#'}" {'target="_blank" rel="noopener"' if book else 'aria-disabled="true"'}>約 30 分鐘電話{'' if book else '（預約頁準備中）'}</a>
      <a class="btn secondary" href="{form or '#'}" {'target="_blank" rel="noopener"' if form else 'aria-disabled="true"'}>留言給我們{'' if form else '（表單準備中）'}</a>
      <a class="btn secondary" href="mailto:george.chen@propelaigrowth.com?subject=想聊聊：">Email george.chen@propelaigrowth.com</a>
    </div>
    <h2>還沒準備好聊？</h2>
    <div class="menu">
      <a class="choice" href="/quiz/"><span><span class="q">先做兩分鐘小測驗</span><span class="a">三題、用點的、不用留資料</span></span><span class="go">→</span></a>
      <a class="choice" href="/downloads/"><span><span class="q">下載一頁介紹</span><span class="a">轉給同事或老闆看</span></span><span class="go">→</span></a>
      <a class="choice" href="https://www.linkedin.com/in/digitalgeorge" target="_blank" rel="noopener"><span><span class="q">LinkedIn 私訊 George</span><span class="a">看他平常在寫什麼</span></span><span class="go">→</span></a>
    </div>
    <p class="note">啟進智能決策有限公司｜台北市忠孝東路五段 1-2 號 12 樓｜課程都到你公司上，雙北以外交通費另計。</p>
    <div class="nav"><a href="/" class="prev">← 回首頁</a></div>
'''
write('/contact/', page('contact', contact, desc='約 30 分鐘電話，說你那件推不動的事。不收費、不推銷。'))

# ---------- articles (from data/articles.json) ----------
arts = json.loads((pathlib.Path(__file__).parent/'data/articles.json').read_text(encoding='utf-8')) if (pathlib.Path(__file__).parent/'data/articles.json').exists() else []
items=[]
for a in arts:
    slug=a['slug']; body=a['html']
    art = f'''
    <span class="pill">文章｜{a['date']}</span>
    <h1>{html.escape(a['title'])}</h1>
    {body}
    <p class="note">這篇也發在 <a href="{a.get('linkedin','https://www.linkedin.com/in/digitalgeorge')}" target="_blank" rel="noopener">LinkedIn</a>。想聊這一題，<a href="/contact/">約 30 分鐘電話</a>。</p>
    <div class="nav"><a href="/articles/" class="prev">← 所有文章</a><a href="/">回首頁 ⌂</a></div>
'''
    p = OUT/'articles'/slug; p.mkdir(parents=True, exist_ok=True)
    (p/'index.html').write_text(page('articles', art, title=a['title'], desc=a.get('summary',''), nav_current='/articles/').replace(f'{SITE}/articles/', f'{SITE}/articles/{slug}/'), encoding='utf-8')
    items.append(f'<a class="choice" href="/articles/{slug}/"><span><span class="q">{html.escape(a["title"])}</span><span class="a">{a["date"]}｜{html.escape(a.get("summary",""))}</span></span><span class="go">→</span></a>')
articles = f'''
    <span class="pill">文章</span>
    <h1>一個畫面，一個看法，一個問句</h1>
    <p class="lead">每週一篇，從一件日常的小事看「為什麼講了三次，他還是沒做」。先在 LinkedIn 發，這裡留一份。</p>
    <div class="menu">{''.join(items) if items else '<div class="empty">第一篇整理中。想先看的話，<a href="https://www.linkedin.com/in/digitalgeorge" target="_blank" rel="noopener">LinkedIn 上已經有幾篇</a>。</div>'}</div>
    <div class="nav"><a href="/" class="prev">← 回首頁</a><a href="/contact/">約 30 分鐘電話 →</a></div>
'''
write('/articles/', page('articles', articles, desc='Propel AI 文章：每週一篇，從日常小事看為什麼講了三次他還是沒做。'))

# ---------- clients (only when data exists) ----------
cl = json.loads((pathlib.Path(__file__).parent/'data/clients.json').read_text(encoding='utf-8')) if (pathlib.Path(__file__).parent/'data/clients.json').exists() else {'quotes':[],'cases':[]}
if cl['quotes'] or cl['cases']:
    q = ''.join(f'<div class="quote"><b>「{html.escape(x["text"])}」</b>{html.escape(x["who"])}{"（應客戶要求匿名）" if x.get("anon") else ""}</div>' for x in cl['quotes'])
    c = ''.join(f'<div class="exi"><h3>{html.escape(x["title"])}</h3><p><b>誰在什麼時候少做了哪個動作：</b>{html.escape(x["behavior"])}</p><p><b>改了哪一處：</b>{html.escape(x["change"])}</p><p><b>兩週後：</b>{html.escape(x["result"])}</p></div>' for x in cl['cases'])
    clients = f'<span class="pill">客戶怎麼說</span><h1>他們改了哪一處</h1>{"<h2>客戶的話</h2>"+q if q else ""}{"<h2>案例</h2><div class=\"ex\">"+c+"</div>" if c else ""}<div class="nav"><a href="/" class="prev">← 回首頁</a></div>'
    write('/clients/', page('clients', clients))

# ---------- static files ----------
(OUT/'CNAME').write_text('propelaigrowth.com\n')
(OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if PREVIEW else f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
urls = [URL[k] for k in ['home','how','trial','half','ws','surf','trial-prep','half-prep','ws-prep','surf-prep','quiz','picker','docs','about','contact','articles']] + [f'/articles/{a["slug"]}/' for a in arts]
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{SITE}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
(OUT/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#003054"/><text x="32" y="44" font-family="Arial,Helvetica,sans-serif" font-size="36" font-weight="900" fill="#F06000" text-anchor="middle">P</text></svg>')
(OUT/'404.html').write_text(page('home', '<span class="pill">404</span><h1>這一頁不在這裡</h1><p class="lead">可能是網址打錯，或這一頁搬家了。</p><div class="menu"><a class="choice" href="/"><span><span class="q">回首頁</span><span class="a">從「你現在是哪一種」開始</span></span><span class="go">→</span></a></div>', title='找不到這一頁', noindex=True), encoding='utf-8')
(OUT/'.nojekyll').write_text('')
if PREVIEW:
    hold = '''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Propel AI 啟進智能決策</title><meta name="robots" content="noindex,nofollow"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap">
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#003054;color:#fff;font-family:"Noto Sans TC",sans-serif;text-align:center;padding:24px}.w{max-width:520px}.wm{color:#F06000;letter-spacing:.32em;font-weight:900;font-size:14px}h1{font-size:clamp(26px,6vw,40px);line-height:1.3;margin:18px 0 10px}p{color:#DCE6EE;font-size:17px;line-height:1.7}a{color:#FFB880}</style></head>
<body><div class="w"><div class="wm">PROPEL AI</div><h1>講了三次，<br>他還是沒做？</h1><p>先不急著加預算，讓你想要的行為更容易發生。</p><p>網站整理中。想先聊聊：<a href="mailto:george.chen@propelaigrowth.com">george.chen@propelaigrowth.com</a></p><p style="font-size:13px;color:#A7B4BE">啟進智能決策有限公司｜行為經濟學 × 行為設計 × AI</p></div></body></html>'''
    (OUT/'index.html').write_text(hold, encoding='utf-8')
    (OUT/'sitemap.xml').unlink()
shutil.copy(pathlib.Path(__file__).parent/'og.png', OUT/'assets/og.png')
shutil.copy(pathlib.Path(__file__).parent/'og_quiz.png', OUT/'assets/og_quiz.png')
print('built', sum(1 for _ in OUT.rglob('index.html')), 'pages;', len(list((OUT/'assets/img').iterdir())), 'images')
