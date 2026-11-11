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
       'about':'/about/', 'contact':'/contact/', 'articles':'/articles/', 'clients':'/clients/',
       'en':'/en/', 'en-how':'/en/how/', 'en-about':'/en/about/', 'en-contact':'/en/contact/'}
TITLE = {'home':'Propel AI 啟進智能決策｜行為經濟學 × AI：讓你想要的行為更容易發生', 'trial':'59 分鐘試駕', 'half':'半天課・全天課', 'ws':'全天工作坊', 'surf':'SURF™ 原廠班',
         'how':'我們怎麼看問題', 'quiz':'兩分鐘小測驗', 'picker':'選題器', 'docs':'課程介紹下載',
         'trial-prep':'59 分鐘試駕 課前說明', 'half-prep':'半天課・全天課 課前說明', 'ws-prep':'全天工作坊 課前說明', 'surf-prep':'SURF™ 原廠班 課前說明',
         'about':'關於 Propel AI', 'contact':'聯絡我們', 'articles':'文章', 'clients':'客戶怎麼說',
         'en':'Propel AI｜Behavioral economics and AI for business teams', 'en-how':'How we think', 'en-about':'About Propel AI', 'en-contact':'Contact'}
DESC = {'home':'用行為經濟學和 AI，先不急著加預算，讓你想要的行為更容易發生。課程與工作坊：59 分鐘試駕、半天課・全天課、全天工作坊、SURF™ 原廠班。',
        'trial':'59 分鐘到你公司上：一個小實驗、一題半天課、寫下你最想先讓誰做什麼。NT$ 8,900（未稅），上限 30 人。',
        'half':'用你本來就在做的決定當題目：半天六題、全天十二題，每題一個規律、三個案例、一次判斷、一段 AI 提示詞。',
        'ws':'帶一個推不動的痛點來，走五站，當場拍板一個小規模、可以追蹤數字的試驗。每場上限 16 人。',
        'surf':'歐洲 MINDWORX 的方法，主題只有一個：怎麼讓客戶說 YES。台灣授權講師中文授課，發原廠結業證書。',
        'how':'數字是結果；可以動手的是行為。環境→行為→指標，每個指標背後都是一條行為鏈。',
        'quiz':'三題、用點的、不用留資料。看看那件推不動的事能不能用這個方法處理。',
        'picker':'三題答完，落到你的模組。十六個主題、四個現成組合。',
        'docs':'一頁介紹 PDF：59 分鐘試駕、半天課・全天課、全天工作坊、SURF™ 原廠班、PROPEL™ 六站。',
        'en':'Courses and workshops that bring behavioral economics and AI into everyday business decisions. Change the environment, not the person. Taipei, Taiwan.',
        'en-how':'Metrics are outcomes. Behavior is what you can work on. How Propel AI looks at a problem, with three examples of changing the environment.',
        'en-about':'Propel AI turns behavioral economics research into steps a business team can practice at work, then watches the effect in their own numbers.',
        'en-contact':'Tell us one thing you would like to make happen, and we will write back within two working days.'}

ALT = {'home':'en','how':'en-how','about':'en-about','contact':'en-contact'}
ALT.update({v:k for k,v in ALT.items()})

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
NAV_EN = [('/en/#pain','Sound familiar?'),('/en/how/','How we think'),('/en/#method','Method'),('/en/#courses','Programs'),('/en/about/','About'),('/en/contact/','Contact')]
NAV = [('/#pain','痛點'),('/how/','怎麼看問題'),('/#method','方法'),('/#courses','課程'),('/about/','為什麼是我們'),('/contact/','聯絡')]
SITE_CSS = '''
/* ---- site chrome ---- */
.sitehead{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:18px}
.sitenav{display:flex;gap:4px;flex-wrap:wrap}
.sitenav a{color:var(--mute);text-decoration:none;font-size:14px;padding:6px 10px;border-radius:999px}
.sitenav a:hover,.sitenav a[aria-current]{color:var(--navy);background:var(--sky)}
.sitenav a.lang{border:1px solid var(--line);margin-left:6px;font-weight:700;color:var(--navy)}
.pg-en .wordmark small,.pg-en-how .wordmark small,.pg-en-about .wordmark small,.pg-en-contact .wordmark small{letter-spacing:.02em}
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
/* ---- micro form ---- */
.mform{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:0 0 12px;display:grid;gap:10px}
.mform label{display:grid;grid-template-columns:6.5em 1fr;gap:10px;align-items:center;font-size:14px}
.mform label span{font-weight:700;color:var(--navy)}
.mform input:not([type=hidden]):not(.hp){width:100%;border:1px solid var(--line);border-radius:8px;padding:9px 10px;font:inherit;font-size:15px;background:#fff}
.mform input:focus{outline:2px solid var(--orange);border-color:var(--orange)}
.mform .hp{position:absolute;left:-9999px}
.mrow{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:4px}
.mnote{font-size:13px;color:var(--mute)}
.mdone{background:var(--navy);color:var(--navy-fg);border-radius:10px;padding:10px 12px;font-weight:700;margin:0}
@media (max-width:480px){.mform label{grid-template-columns:1fr;gap:4px}}
/* ---- home long page ---- */
img.av{width:56px;height:56px;border-radius:50%;object-fit:cover;flex:none}
.doors{margin:14px 0 4px}
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
/* ---- sample galleries ---- */
.demo{margin:26px 0 8px;padding:16px 16px 10px;border:1px solid var(--line);border-radius:14px;background:var(--sky)}
.demo h2{margin:0 0 4px;font-size:20px}
.demo .sub{color:var(--mute);font-size:14.5px;margin:0 0 12px}
.demo .k{display:inline-block;font-size:12px;color:var(--orange);font-weight:700;margin:10px 0 6px}
.gal{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0 0 6px}
.gal figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px;min-width:0}
.gal a{display:block}
.gal img{width:100%;height:auto;display:block;border-radius:6px;border:1px solid var(--line);background:#fff}
.gal figcaption{font-size:12.5px;line-height:1.45;margin:6px 2px 2px;color:var(--mute)}
.gal figcaption b{display:block;color:var(--navy);font-size:13px}
.gal.two{grid-template-columns:1fr 1fr}
.demo .note{font-size:12.5px;color:var(--mute);margin:8px 0 4px}
.walk{display:grid;gap:8px;margin:0 0 10px}
.walk .w{display:grid;grid-template-columns:7.5em 1fr;gap:10px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:14px}
.walk .w b{color:var(--orange)}
.walk .w b small{display:block;color:var(--mute);font-weight:400;font-size:12px}
.walk .w p{margin:0 0 4px}
.walk .w .ans{color:var(--navy);font-weight:700}
.walk .w .why{color:var(--mute);font-size:13px}
@media (max-width:600px){.gal{grid-template-columns:1fr 1fr}.walk .w{grid-template-columns:1fr;gap:4px}}
/* ---- home v0.3 chunking ---- */
.vs.three{grid-template-columns:1fr 1fr 1fr}
.vs.three .card p{font-size:14px;margin:0 0 4px}
.strip{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:14px 0 10px}
.strip div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 6px;text-align:center}
.strip b{display:block;font-size:22px;color:var(--orange);line-height:1.1}
.strip span{display:block;font-size:13.5px;color:var(--navy);font-weight:700;margin-top:2px}
.chips{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:0 0 12px;font-size:14px}
.chips span{background:var(--sky);border:1px solid var(--line);border-radius:999px;padding:4px 12px;color:var(--navy);font-weight:700}
.chips i{color:var(--orange);font-style:normal}
.links{display:flex;flex-wrap:wrap;gap:6px 22px;margin:4px 0}
.facts4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0}
.facts4 div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.facts4 b{display:block;color:var(--orange);font-size:14px;margin-bottom:4px}
.facts4 span{font-size:13.5px;color:var(--mute);line-height:1.45}
@media (max-width:700px){.vs.three{grid-template-columns:1fr}.strip{grid-template-columns:repeat(3,1fr)}.facts4{grid-template-columns:1fr 1fr}}
/* ---- v0.3b: OA layout review ---- */
.pg-home .wrap{max-width:820px}
.hero{display:grid;grid-template-columns:1.25fr 1fr;gap:18px;align-items:center;margin:4px 0 6px}
.hero-v{width:100%;height:auto;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px}
.strip b{font-size:30px}
.strip i{display:block;font-style:normal;font-size:10.5px;color:var(--mute);letter-spacing:.02em}
.strip div{border-color:#F3B48A;padding:12px 6px}
.strip div.later{border-color:var(--line);background:var(--sky)}
.strip div.later b{color:var(--mute)}
.strip-cap{margin:-2px 0 10px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;vertical-align:-1px;margin-right:4px}
.dot.o{background:var(--orange)}.dot.g{background:#B8C4CE;margin-left:6px}
.thumbs{display:grid;grid-template-columns:2fr 1fr;grid-template-rows:auto auto;gap:10px;margin:12px 0 10px}
.thumbs a{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px;text-decoration:none;color:var(--navy);font-size:13px;font-weight:700}
.thumbs a.main{grid-row:1/3}
.thumbs a.main span{font-size:14px}
.thumbs em{font-style:normal;font-weight:400;color:var(--mute);font-size:12px;margin-left:4px}
.thumbs img{width:100%;height:120px;object-fit:cover;object-position:top;display:block;border-radius:6px;border:1px solid var(--line);background:#fff;margin-bottom:6px}
.thumbs a.main img{height:auto;aspect-ratio:16/9}
@media (max-width:700px){.hero{grid-template-columns:1fr}.thumbs{grid-template-columns:1fr 1fr;gap:8px}.thumbs a.main{grid-row:auto;grid-column:1/3}.thumbs img{height:96px}.thumbs a{font-size:12px}}

/* ---- home v0.4: tiles, fewer words ---- */
.pg-home .sec{padding-top:44px}
.pg-home .eyebrow{letter-spacing:.12em}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0 14px}
.tiles.two{grid-template-columns:1fr 1fr}
.tile{display:flex;flex-direction:column;gap:8px;min-height:150px;padding:20px 20px 16px;border:1px solid var(--line);border-radius:14px;background:var(--card);text-decoration:none;color:var(--navy);transition:border-color .15s,transform .15s}
.tile:hover{border-color:var(--orange);transform:translateY(-2px)}
div.tile:hover{border-color:var(--line);transform:none}
[lang=en] .mform label{grid-template-columns:8.5em 1fr}
@media (max-width:480px){[lang=en] .mform label{grid-template-columns:1fr}}
div.tile.hot:hover{border-color:#F3B48A}
.tile.hot{border-color:#F3B48A;background:#FFF6EF}
.tile .k{font-size:12.5px;font-weight:700;color:var(--orange)}
.tile b{font-size:18px;line-height:1.4}
.tile .d{font-size:13.5px;color:var(--mute);line-height:1.5}
.tile .go{margin-top:auto;font-size:13px;font-weight:700;color:var(--orange)}
.chain.slim .c{font-size:13.5px}
.pg-home p.big{margin:10px 0 12px}
.facts4 b{font-size:20px}
@media (max-width:700px){.tiles,.tiles.two{grid-template-columns:1fr}.tile{min-height:0}}
'''

FOOT_EN = '''
</main>
  <footer class="sitefoot">
    <div><b>Propel AI Co., Ltd.</b>｜Tax ID 61933866｜12F, No. 1-2, Sec. 5, Zhongxiao E. Rd., Taipei, Taiwan｜<a href="mailto:george.chen@propelaigrowth.com">george.chen@propelaigrowth.com</a></div>
    <div>Licensed trainer and coach, MINDWORX SURF™ Method (Europe)｜We respect your decision; no follow-up marketing without your consent.</div>
    <div class="disc">Program descriptions are pre-course information; actual arrangements follow the quotation and pre-course confirmation. Propel AI reserves the right to adjust program content and format.</div>
  </footer>
</div>
<script>
(function(){
  document.querySelectorAll('form.mform').forEach(function(f){
    f.addEventListener('submit',function(e){
      e.preventDefault();
      if(!f.reportValidity())return;
      var d=new FormData(f);
      var body='I want: '+d.get('who')+'\\nat: '+d.get('when')+'\\nto: '+d.get('what')+'\\n\\n'+d.get('name')+'\\n'+d.get('email');
      var key=d.get('access_key');
      var done=function(){f.querySelector('.mdone').hidden=false;f.querySelectorAll('label,.mrow').forEach(function(x){x.hidden=true});};
      if(!key){location.href='mailto:george.chen@propelaigrowth.com?subject='+encodeURIComponent('Website (EN): one thing I want to make happen')+'&body='+encodeURIComponent(body);return;}
      var btn=f.querySelector('button');btn.disabled=true;btn.textContent='Sending…';
      d.append('message',body);
      fetch('https://api.web3forms.com/submit',{method:'POST',body:d,headers:{'Accept':'application/json'}}).then(function(r){return r.json()}).then(function(j){
        if(j.success){done();}else{throw 0;}
      }).catch(function(){btn.disabled=false;btn.textContent='Send — we\\'ll write back';location.href='mailto:george.chen@propelaigrowth.com?subject='+encodeURIComponent('Website (EN): one thing I want to make happen')+'&body='+encodeURIComponent(body);});
    });
  });
})();
</script>
</body>
</html>
'''

def page(key, body, title=None, desc=None, extra_head='', wrap=True, nav_current=None, noindex=False):
    en = key.startswith('en')
    title = title or TITLE[key]; desc = desc or DESC.get(key, DESC['home'])
    full = title if key in ('home','en') else (f'{title}｜Propel AI' if en else f'{title}｜Propel AI 啟進智能決策')
    url = SITE + URL[key]
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if (nav_current or URL[key])==h else ""}>{t}</a>' for h,t in (NAV_EN if en else NAV))
    alt = ALT.get(key)
    if en:   nav += f'<a class="lang" href="{URL[alt] if alt else "/"}" hreflang="zh-Hant" lang="zh-Hant">中文</a>'
    else:    nav += f'<a class="lang" href="{URL[alt] if alt else "/en/"}" hreflang="en" lang="en">EN</a>'
    if alt:
        zh_u, en_u = (URL[alt], url) if en else (url, URL[alt])
        if not zh_u.startswith('http'): zh_u = SITE + zh_u
        if not en_u.startswith('http'): en_u = SITE + en_u
        extra_head += f'<link rel="alternate" hreflang="zh-Hant" href="{zh_u}"><link rel="alternate" hreflang="en" href="{en_u}"><link rel="alternate" hreflang="x-default" href="{zh_u}">\n'
    head = f'''<!doctype html>
<html lang="{"en" if en else "zh-Hant"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
{'<meta name="robots" content="noindex,nofollow">' if (noindex or PREVIEW) else ''}
<meta property="og:type" content="website"><meta property="og:site_name" content="{"Propel AI" if en else "Propel AI 啟進智能決策"}">
<meta property="og:title" content="{html.escape(full)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/assets/{OGIMG.get(key,"og.png")}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap">
<link rel="stylesheet" href="/assets/site.css">
{extra_head}
</head>
<body class="pg-{key}">
<div class="wrap">
  <header class="sitehead">
    <a class="wordmark" href="{URL['en'] if en else URL['home']}">PROPEL AI<small>{'Behavioral economics × behavior design × AI' if en else '啟進智能決策｜行為經濟學 × 行為設計 × AI'}</small></a>
    <nav class="sitenav" aria-label="{'Main menu' if en else '主選單'}">{nav}</nav>
  </header>
<main>
'''
    foot = FOOT_EN if en else '''
</main>
  <footer class="sitefoot">
    <div><b>Propel AI｜啟進智能決策有限公司</b>｜統一編號 61933866｜台北市忠孝東路五段 1-2 號 12 樓｜<a href="mailto:george.chen@propelaigrowth.com">george.chen@propelaigrowth.com</a></div>
    <div>歐洲 MINDWORX SURF™ Method 授權講師與教練｜尊重您的決定；未經同意，不進行後續行銷聯繫。</div>
    <div class="disc">課程頁與課前說明為課前說明，實際安排以報價單與開課前確認為準；本公司保留調整課程內容與進行方式之權利。</div>
  </footer>
</div>
<script>
(function(){
  document.querySelectorAll('form.mform').forEach(function(f){
    f.addEventListener('submit',function(e){
      e.preventDefault();
      if(!f.reportValidity())return;
      var d=new FormData(f);
      var body='我想讓：'+d.get('who')+'\\n在：'+d.get('when')+'\\n完成：'+d.get('what')+'\\n\\n'+d.get('name')+'\\n'+d.get('email');
      var key=d.get('access_key');
      var done=function(){f.querySelector('.mdone').hidden=false;f.querySelectorAll('label,.mrow').forEach(function(x){x.hidden=true});};
      if(!key){location.href='mailto:george.chen@propelaigrowth.com?subject='+encodeURIComponent('官網：我最想推動的一件事')+'&body='+encodeURIComponent(body);return;}
      var btn=f.querySelector('button');btn.disabled=true;btn.textContent='送出中…';
      d.append('message',body);
      fetch('https://api.web3forms.com/submit',{method:'POST',body:d,headers:{'Accept':'application/json'}}).then(function(r){return r.json()}).then(function(j){
        if(j.success){done();}else{throw 0;}
      }).catch(function(){btn.disabled=false;btn.textContent='送出，我們回信';location.href='mailto:george.chen@propelaigrowth.com?subject='+encodeURIComponent('官網：我最想推動的一件事')+'&body='+encodeURIComponent(body);});
    });
  });
})();
</script>
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
cfg = json.loads((pathlib.Path(__file__).parent/'config.json').read_text(encoding='utf-8')) if (pathlib.Path(__file__).parent/'config.json').exists() else {}
FORM_KEY = cfg.get('form_key','')
# ---------- 實物示例（示意）與虛構示範案例 ----------
(OUT/'assets/demo').mkdir(parents=True, exist_ok=True)
for f in (pathlib.Path(__file__).parent/'demo').glob('*.jpg'):
    shutil.copy(f, OUT/'assets/demo'/f.name)

def fig(src, title, cap, w, h):
    return (f'<figure><a href="/assets/demo/{src}.jpg" target="_blank" rel="noopener">'
            f'<img src="/assets/demo/{src}_t.jpg" alt="{html.escape(title)}" width="{w}" height="{h}" loading="lazy"></a>'
            f'<figcaption><b>{title}</b>{cap}</figcaption></figure>')

_ys = [
 ('ys-1','① 決定頁','報價之後，第幾天、用什麼理由跟進？先選你現在是哪一種。'),
 ('ys-2','② 規律','跟進的兩個開關：時點讓他自己說，理由替他拆問號。'),
 ('ys-3','③ 案例之一','疫苗提醒信多一格「寫下你打算去的日期與時間」，接種 33%→37%。'),
 ('ys-4','④ 案例之二','紐約傳票重新設計＋開庭前簡訊，缺席率下降 36%。'),
 ('ys-5','⑤ 案例之三','「新的開始」效應：跟進日挑月初、連假後，不挑第 N 天。'),
 ('ys-6','⑥ 換你判斷','提案後兩週，採購已讀不回，四封跟進信你發哪一封？'),
 ('ys-7','⑦ AI 提示詞','回去把上一次沒下文的報價貼給 AI，讓它寫「拆一個問號」的跟進。'),
 ('ys-8','⑧ 延伸卡','課堂沒講到的，回去自己看：兩篇研究、各一句怎麼用。'),
 ('ys-9','⑨ 設計案','從概念推出來的解方，還沒量過：只寫預期方向與怎麼測。'),
]
HALF_DEMO = '''
    <section class="demo" id="sample">
      <h2>一題長什麼樣（示意）</h2>
      <p class="sub">取自模組「客人說『我再想想』，然後就沒下文」第六題〈報價之後：第幾天、用什麼理由跟進？〉。一題九頁、約 25 分鐘：前六頁課堂上走，後三頁帶回去用。點圖可放大。</p>
      <div class="k">課堂上：一個決定 → 一個規律、三個案例 → 一次判斷</div>
      <div class="gal">''' + ''.join(fig(s,t,c,640,360) for s,t,c in _ys[:6]) + '''</div>
      <div class="k">帶走：AI 提示詞、延伸卡、設計案</div>
      <div class="gal">''' + ''.join(fig(s,t,c,640,360) for s,t,c in _ys[6:]) + '''</div>
      <p class="note">示意頁面，非客戶實績；案例數字為公開研究（出處見各頁頁尾），台上只講方向與幅度。每題版面相同，內容依你挑的題目而定。</p>
    </section>
'''

WS_DEMO = '''
    <section class="demo" id="sample">
      <h2>帶走的那張最小試驗卡，長什麼樣（示意）</h2>
      <p class="sub">下半段第⑤站，每組只填一張：試什麼、找誰試、試多久、看哪個數字、誰負責、哪一天回來看。左邊是學員手冊裡的示範頁（虛構題目：業務拜訪完客戶，沒有當天把結果填進 CRM），右邊是空白卡。點圖可放大。</p>
      <div class="gal two">''' + fig('pm2-06','第⑤站｜小試驗（示範頁）','先小、短、看得到：一週、一個數字，回來看。',640,904) + fig('pm2-10','小試驗卡（空白）','回去填自己的題目，先試，再改。',640,904) + '''</div>
      <p class="note">示意，取自全天工作坊學員手冊；題目與數字皆為虛構教學情境。</p>
    </section>
'''

WS_CASE = '''
    <section class="demo" id="case">
      <h2>示範：如果是一家「AI 工具買了沒人用」的公司，六站會走成這樣（虛構案例）</h2>
      <p class="sub">一家 ERP 系統商（教學用虛構公司，數字為教學設計）三月導入 AI 提案工具，15 個席次、月費照繳；四個月後，後台只記到 31 次起草。總經理在月會上說：「大家就是懶得學新東西，我打算把使用次數放進考核。」</p>
      <div class="walk">
        <div class="w"><b>① 找行為<small>Pinpoint</small></b><div><p class="ans">業務同仁在每次提案前，先用 AI 草擬提案初稿。</p><p class="why">「提高 AI 使用率」是願望，不是行為。量尺也跟著定了：不是登入次數、不是草稿總數，是每次提案前有沒有先讓 AI 起草。</p></div></div>
        <div class="w"><b>② 拆解<small>Reconstruct</small></b><div><p class="ans">31 次拆開看：3 位新人用了 22 次，4 位資深加起來 3 次。訓練出席 11／12 人，課後測驗平均 82 分。</p><p class="why">「懶得學」先過測驗這一關——考最高分的那一群用得最少。總數會騙人，分布一拆，分水嶺就出來了：不是能力，是手上有沒有舊提案可抄。</p></div></div>
        <div class="w"><b>③ 找卡點<small>Obstacle</small></b><div><p class="ans">最值得先驗證的方向：公司裡最會寫提案的人從來不從白紙開始，工具卻被教成只能從白紙開始——動線接不上。</p><p class="why">AI 列出十個候選卡點，團隊逐條對證據：有原話或數字支持的命中 3 條（舊習慣的動線、系統和實際工作對不上、從沒見過對的用法），機制合理但沒證據的待確認 3 條，排除 4 條。資深那句「教它背景的時間，我自己都寫完了」是一筆算過的帳，不是態度。</p></div></div>
        <div class="w"><b>④ 找改法<small>Prescribe</small></b><div><p class="ans">不動考核、不加席次：已排定的 8/20 訓練改教「貼舊提案當範本」，請一位資深用自己的舊案現場跑一遍；每週在群組匿名公布一行「本週 AI 草稿 X 次、Y 位使用」。</p><p class="why">考核逼出來的是應付；看見同儕真的在用，觀望才鬆動。讓工具接上他們的起手式，優勢被放大；叫人改動線，抗拒被放大。</p></div></div>
        <div class="w"><b>⑤ 小試驗<small>Experiment</small></b><div><p class="ans">訓練前先花 30 分鐘：一位資深帶一份成交舊提案，貼進去跑一遍，量兩個數字——初稿可用段落比例、總修改時間。</p><p class="why">一個人、一份提案，只回答「這條路跑不跑得通」。跑得通，8/20 就照這個教；跑不通，先回頭看工具與流程，不急著全面推。</p></div></div>
        <div class="w"><b>⑥ 看數字<small>Loop</small></b><div><p class="ans">提案每週都在發生：看每人每週的起草次數，新人與資深分開看；待確認的三條，訓練現場各問一句就能定案。</p><p class="why">登入次數不能當指標（裡面混著系統自動連線）。老闆原本的考核沒被否決，只是排到後面——先用最便宜的一招驗證方向。</p></div></div>
      </div>
      <p class="note">虛構教學案例，公司、人物與數字均為教學設計；卡點判定為「有證據支持、待驗證的假設」，不是結論。你的題目會在課前收件表先談定，當天帶著自己的數字走這六站。</p>
    </section>
'''


bodies = {}
for key in ['trial','half','ws','surf','how','trial-prep','half-prep','ws-prep','surf-prep']:
    v = links(strip_section(views[key]))
    v = extract_images(v, key)
    if key == 'half':
        v = v.replace('<h2>模組一覽', HALF_DEMO + '    <h2>模組一覽', 1)
    if key == 'how':
        v = v.replace('<h2>跟常見的做法，哪裡不一樣</h2>', '''<h2>同一招，用在你公司：報價後的跟進信</h2>
    <div class="vs three">
      <div class="card"><h3>改前</h3><p>「附上報價，請參考，有問題再聯絡。」</p><p class="note">球在客戶手上</p></div>
      <div class="card"><h3>卡點</h3><p>他最容易做的，是什麼都不做。</p><p class="note">這封信沒替他定「下一步、什麼時候」</p></div>
      <div class="card us"><h3>改後</h3><p>「附上報價。我週四下午打給您，看有沒有要調的地方。」</p><p class="note">下一步先幫他定好，他只要不反對</p></div>
    </div>
    <p class="note">示意，非客戶實績。</p>
    '''+'<h2>跟常見的做法，哪裡不一樣</h2>', 1)
        v = v.rstrip() + '''
    <h2>這套看法，走的是一條固定的路</h2>
    <p>我們把它整理成 PROPEL™ 六站：找行為、拆解、找卡點、開處方、小試驗、看數字。全天工作坊就是照這條路走，每一站都有一張可以帶走的紙。</p>
    <p><a class="more" href="/workshop/#case">看六站走一遍（虛構案例）→</a>　<a class="more" href="/downloads/">PROPEL™ 架構兩頁 PDF →</a></p>
'''
    if key == 'ws':
        v = v.replace('<div class="price">', WS_DEMO + WS_CASE + '    <div class="price">', 1)
    bodies[key] = v
    if key.endswith('-prep'):
        v = f'<div class="prep">{v}</div>'
    write(URL[key], page(key, v))

def microform(ctx):
    return f'''
      <form class="mform" id="mform-{ctx}" novalidate>
        <input type="hidden" name="access_key" value="{FORM_KEY}">
        <input type="hidden" name="subject" value="官網：我最想推動的一件事">
        <input type="hidden" name="from_name" value="Propel AI 官網">
        <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
        <label><span>我想讓</span><input name="who" placeholder="例：業務團隊／收到報價的客戶" required></label>
        <label><span>在</span><input name="when" placeholder="例：每週一早會前／收到提案三天內" required></label>
        <label><span>完成</span><input name="what" placeholder="例：打開 AI 跑出第一版草稿／確認下一步會議時間" required></label>
        <label><span>公司與稱呼</span><input name="name" placeholder="例：○○公司 陳經理" required></label>
        <label><span>Email</span><input name="email" type="email" placeholder="回信用" required></label>
        <div class="mrow"><button class="btn primary" type="submit">送出，我們回信</button><span class="mnote">一句話就夠；不收費、不推銷。</span></div>
        <p class="mdone" hidden>收到了。我們會先看哪個行為值得處理，兩個工作天內回信。</p>
      </form>'''
# home: long page that follows the 公司簡介 storyline (v0.2)
how_body = bodies['how']
import re as _re
_ex1 = _re.search(r'<div class="exi">.*?</div></div></div>', how_body, _re.S).group(0)
_ex = '<div class="ex">'+_ex1+'</div><p class="note">外部研究，非 Propel AI 客戶實績｜出處：Ebeling &amp; Lotz (2015) Nature Climate Change</p>'
home = f"""
    <div class="hero">
      <div class="hero-t">
        <p class="eyebrow">講了三次，他還是沒做？</p>
        <h1>先不急著加預算，讓你想要的行為更容易發生</h1>
        <p class="lead">課程與工作坊：用行為經濟學和 AI，改環境，不改人。</p>
      </div>
      <svg class="hero-v" viewBox="0 0 320 200" role="img" aria-label="原本：每個人都要再說服一次；改環境之後：路徑清楚，少一步，適時提醒">
        <g font-family="Noto Sans TC,sans-serif" font-size="14" font-weight="700" fill="#003054">
          <text x="10" y="24">原本：每個人都要再說服一次</text>
          <text x="10" y="124">改環境：讓行為自己發生</text>
        </g>
        <g stroke="#C9D3DB" stroke-width="6" stroke-linecap="round"><line x1="20" y1="60" x2="300" y2="60"/></g>
        <g fill="#5C6B78"><circle cx="30" cy="60" r="8"/><circle cx="120" cy="60" r="8"/><circle cx="210" cy="60" r="8"/></g>
        <g fill="#DDE3E8"><rect x="66" y="44" width="30" height="32" rx="5"/><rect x="156" y="44" width="30" height="32" rx="5"/><rect x="246" y="44" width="30" height="32" rx="5"/></g>
        <g font-family="Noto Sans TC,sans-serif" font-size="11.5" fill="#5C6B78"><text x="56" y="94">資訊不清</text><text x="146" y="94">步驟繁瑣</text><text x="236" y="94">反覆提醒</text></g>
        <g stroke="#F06000" stroke-width="6" stroke-linecap="round"><line x1="20" y1="160" x2="290" y2="160"/></g>
        <polygon points="288,148 310,160 288,172" fill="#F06000"/>
        <g fill="#F06000"><circle cx="30" cy="160" r="8"/><circle cx="115" cy="160" r="8"/><circle cx="200" cy="160" r="8"/></g>
        <g font-family="Noto Sans TC,sans-serif" font-size="11.5" font-weight="700" fill="#003054"><text x="50" y="190">預設先選好</text><text x="138" y="190">少一個欄位</text><text x="222" y="190">那一刻提醒</text></g>
      </svg>
    </div>
    <div class="menu doors">
      <a class="choice hot" href="/contact/"><span><span class="q">已經有題目，想談怎麼上</span><span class="a">留下一件事，我們回信</span></span><span class="go">→</span></a>
      <a class="choice" href="/quiz/"><span><span class="q">還不確定，先看看自己卡在哪</span><span class="a">兩分鐘小測驗，不用留資料</span></span><span class="go">→</span></a>
    </div>

    <section class="sec" id="pain">
      <p class="eyebrow">01</p>
      <h2>你也卡在這裡嗎？</h2>
      <div class="tiles">
        <a class="tile" href="/half-day/#sample"><span class="k">客人</span><b>「提案做得再好，客戶還是說我再想想。」</b><span class="go">看這一題怎麼上 →</span></a>
        <a class="tile" href="/workshop/#case"><span class="k">員工</span><b>「AI 工具買了，規矩訂了，就是沒人用。」</b><span class="go">看一個案例怎麼走 →</span></a>
        <a class="tile" href="/how/"><span class="k">現場</span><b>「SOP 寫得很清楚，現場還是照舊。」</b><span class="go">看我們怎麼看 →</span></a>
      </div>
      <p class="big">三句講的是同一件事：你想要的行為，沒有發生。</p>
    </section>

    <section class="sec" id="how">
      <p class="eyebrow">02</p>
      <h2>數字是結果；可以動手的是行為</h2>
      <div class="chain slim">
        <div class="c"><b>環境</b>看到什麼、要做幾步、預設是什麼</div><div class="ar">▶</div>
        <div class="c"><b>行為</b>誰、在什麼時候、做哪個動作</div><div class="ar">▶</div>
        <div class="c"><b>指標</b>業績、採用率、回購率</div>
      </div>
      <p class="big">行為不只由人決定，很大一部分由環境決定——而環境，是你可以事先安排的。</p>
      <a class="more" href="/how/">四個例子：換預設、給選項、先開口、跟進信 →</a>
    </section>

    <section class="sec" id="method">
      <p class="eyebrow">03</p>
      <h2>PROPEL™ 六站：是流程，不是軟體</h2>
      <div class="strip">
        <div><b>P</b><i>Pinpoint</i><span>找行為</span></div><div><b>R</b><i>Reconstruct</i><span>拆解</span></div><div><b>O</b><i>Obstacle</i><span>找卡點</span></div><div><b>P</b><i>Prescribe</i><span>找改法</span></div><div><b>E</b><i>Experiment</i><span>小試驗</span></div><div class="later"><b>L</b><i>Loop</i><span>看數字</span></div>
      </div>
      <div class="chips"><span>團隊先想</span><i>→</i><span>AI 再補</span><i>→</i><span>講師把關</span><i>→</i><span>團隊決定</span></div>
      <a class="more" href="/workshop/#case">看六站走一遍（虛構案例）→</a>
    </section>

    <section class="sec" id="courses">
      <p class="eyebrow">04</p>
      <h2>從你現在最想知道的那件事開始</h2>
      <div class="tiles two">
        <a class="tile hot" href="/trial/"><span class="k">這個方法，對我們有沒有用？</span><b>59 分鐘試駕</b><span class="d">到你公司，抽一題實際上一次｜NT$ 8,900</span><span class="go">建議起點 →</span></a>
        <a class="tile" href="/half-day/"><span class="k">哪幾個決定，團隊可以做得更好？</span><b>半天課・全天課</b><span class="d">六題或十二題，每題練一個決定</span><span class="go">看課程 →</span></a>
        <a class="tile" href="/workshop/"><span class="k">我們這個題目，到底卡在哪？</span><b>全天工作坊</b><span class="d">帶自己的題目，帶走一張小試驗卡</span><span class="go">看工作坊 →</span></a>
        <a class="tile" href="/surf/"><span class="k">行銷業務要原廠方法與證書</span><b>歐洲 SURF™ 原廠班</b><span class="d">MINDWORX 原廠課程，中文授課</span><span class="go">看原廠班 →</span></a>
      </div>
      <div class="links"><a class="more" href="/picker/">用選題器挑模組 →</a><a class="more" href="/downloads/">下載一頁介紹 →</a></div>
    </section>

    <section class="sec" id="why">
      <p class="eyebrow">05</p>
      <h2>不是一份講義，是做好的教材和工具</h2>
      <div class="thumbs">
        <a class="main" href="/half-day/#sample"><img src="/assets/demo/ys-1.jpg" alt="模組課一題的決定頁" width="1024" height="576"><span>模組課一題的第一頁 <em>示意</em></span></a>
        <a href="/half-day/#sample"><img src="/assets/demo/ys-7_t.jpg" alt="每題帶走的 AI 提示詞頁" width="640" height="360"><span>每題帶走的 AI 提示詞</span></a>
        <a href="/workshop/#sample"><img src="/assets/demo/pm2-06_t.jpg" alt="工作坊的小試驗卡" width="453" height="640"><span>工作坊帶走的試驗卡</span></a>
      </div>
      <div class="facts4">
        <div><b>150</b><span>份做好的教材</span></div>
        <div><b>67／101</b><span>種卡點／改法，條條有出處</span></div>
        <div><b>AI</b><span>選題器、小測驗、每題提示詞</span></div>
        <div><b>MINDWORX</b><span>SURF™ 授權講師與教練</span></div>
      </div>
      <a class="more" href="/about/">George Chen 親自授課｜關於我們 →</a>
    </section>

    <section class="sec" id="next">
      <p class="eyebrow">06</p>
      <h2>說一件你想推動的事</h2>
      <p class="sub">我希望<b>誰</b>，在<b>什麼時候</b>，做<b>哪個動作</b>？拆成三格填就好。</p>
      {microform('home')}
    </section>
"""
write(URL['home'], page('home', home, nav_current='/'))

# ---------- downloads ----------
DOCS = [
 ('trial','59 分鐘試駕　一頁介紹','正面：59 分鐘你會經歷的三件事、帶走什麼、費用與折抵。背面：我們怎麼看問題——三個改環境的例子，和「每個指標背後都是一條行為鏈」。','Propel_AI_59分鐘試駕_一頁介紹.pdf'),
 ('half','半天課・全天課　一頁介紹','半天六題、全天十二題，用你本來就在做的決定當題目：每題一個規律、三個案例、一次判斷、一段 AI 提示詞。背面是模組一覽與四個現成組合。','Propel_AI_半天課全天課_一頁介紹.pdf'),
 ('workshop','全天工作坊　一頁介紹','上午看懂行為的規律，下午帶你們自己的題目走五站，當場拍板一個小規模、可以追蹤數字的試驗。每場上限 16 人。','Propel_AI_全天工作坊_一頁介紹.pdf'),
 ('surf','SURF™ 原廠班　一頁介紹','歐洲 MINDWORX 的方法，主題只有一個：怎麼讓客戶說 YES。台灣授權講師中文授課，半天、全天都發原廠結業證書。','Propel_AI_SURF原廠班_一頁介紹.pdf'),
 ('propel','我們怎麼做：PROPEL™ 六站（兩頁）','第 1 頁：像看診一樣，先找出症狀背後卡在哪一步，再開處方。第 2 頁：從找行為到看數字的六站流程，工作坊就是照這條路走。','Propel_AI_PROPEL架構兩頁.pdf'),
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
    <div class="nav"><a href="/" class="prev">← 回首頁</a><a href="/contact/">留下一件事 →</a></div>
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
    <p class="lead">提案做了，客戶卻遲遲沒有下一步；AI 工具買了，團隊卻沒有用起來；SOP 寫清楚了，現場還是照舊。Propel AI 透過課程與工作坊，教團隊運用行為經濟學和 AI，找出客戶不往下談、同仁沒有行動的原因，再調整流程、訊息與做決定的環境。</p>
    <h2>我們相信的三件事</h2>
    <div class="cards">
      <div class="card"><h3>不把結果當行為</h3><p>業績、採用率是結果；能動手的是誰在什麼時候做哪個動作。</p></div>
      <div class="card"><h3>不把人格當原因</h3><p>「他懶」「他不用心」不是卡點；先看那一步是不是太費力、太容易忘，或沒有人先做。</p></div>
      <div class="card"><h3>不把假設當結論</h3><p>改法先當假設，小試驗看數字，再決定留、改、換。觀察多久，看那個行為多常發生。</p></div>
    </div>
    <h2>為什麼是行為經濟學</h2>
    <p>企業很熟悉自己的銷售流程。但從客戶那一端看，他每一步要做什麼、擔心什麼、還需要誰點頭？這些客戶必須完成的事，不一定出現在我們的流程裡。行為經濟學講的就是這個：除了需求與意願，選項怎麼呈現、步驟有多麻煩、提醒怎麼出現，都會影響一個人的決定。</p>
    <p>過去，行為經濟學多由政府與大型企業聘顧問導入。一般企業也許聽過、也想試試看怎麼用在自己的生意上，但往往不知道從哪裡著手：學理讀起來需要時間，也缺一套可以直接拿來用的工具和工件，把研究發現接到工作上的步驟。我們這幾年做的，就是這一步——把行為經濟學的研究發現，轉成企業團隊能在工作上練習的步驟，再用實際數字觀察效果。</p>
    <h2>團隊在課堂上練習三件事</h2>
    <div class="cards">
      <div class="card"><div class="n">1</div><h3>拆成看得見的行動</h3><p>把「業績要成長」「工具要有人用」拆成誰、在什麼時候、做哪一個動作。</p></div>
      <div class="card"><div class="n">2</div><h3>找卡點，設計改法</h3><p>找出那個動作可能卡住的原因，設計一個先不急著加預算的改法。</p></div>
      <div class="card"><div class="n">3</div><h3>用自己的數字看效果</h3><p>小範圍試，看數字，再決定留、改、或換一處。觀察期依行為發生的頻率定；常發生的行為，一到兩週先看一次。</p></div>
    </div>
    <p>過程中會用到我們自己開發的 AI 輔助工具，背後是整理好的 67 種常見卡點與 101 種改法。順序是固定的：團隊先想，AI 再補上可能漏看的地方，講師帶你看，最後由團隊決定。課程結束後，AI 還能繼續陪你練習——我們提供寫好的提示詞，回到公司，把自己的實際狀況貼進平常用的 AI 工具，就能照課堂上的原理和步驟再走一遍。</p>
    <h2>方法、教材與夥伴</h2>
    <ul class="facts">
      <li><b>方法</b><span>PROPEL™ 六站流程：Pinpoint、Reconstruct、Obstacle、Prescribe、Experiment、Loop——從模糊問題走到可測試方案</span></li>
      <li><b>教材</b><span>八個痛點、150 份模組教材；半天六題、全天十二題，每題一個決定、一條規律、三個案例、一段 AI 提示詞</span></li>
      <li><b>資料庫</b><span>整理好的 67 種常見卡點與 101 種改法，是 AI 工具與講義背後的底</span></li>
      <li><b>夥伴</b><span>歐洲 MINDWORX：2015 年成立的行為經濟學顧問公司，現於歐洲與北美設點，服務過 Allianz、Generali、UniCredit、Zurich 等集團旗下公司；Propel AI 是其 SURF™ Method 台灣授權講師與教練</span></li>
    </ul>
    <h2>誰來上課</h2>
    <div class="who"><img class="av" src="/assets/george.jpg" alt="George Chen" width="56" height="56"><div><h3>George Chen 陳朝智｜創辦人，親自授課</h3><p>芝加哥大學 Booth 商學院 MBA（With Honors，前 20% 畢業），修過 2017 諾貝爾經濟學獎得主 Richard Thaler 的課；前 Oracle 香港／台灣區行銷總監、人力資源產品線亞太區行銷總監；歐洲 MINDWORX SURF™ Method 授權講師與教練。「怎麼讓客戶願意往下走」，是他在 Oracle 多年一直面對的問題。</p></div></div>
    <p class="note">完整講師資歷與認證，見公司簡介與各課程的課前說明。SURF™ 是 MINDWORX 的方法；Propel AI 的課程與工作坊是我們自己設計的架構。</p>
    <h2>公司</h2>
    <ul class="facts">
      <li><b>名稱</b><span>啟進智能決策有限公司（Propel AI）</span></li>
      <li><b>統一編號</b><span>61933866</span></li>
      <li><b>地址</b><span>台北市忠孝東路五段 1-2 號 12 樓</span></li>
      <li><b>聯絡</b><span>george.chen@propelaigrowth.com｜<a href="/contact/">留下一件事</a></span></li>
    </ul>
    <div class="nav"><a href="/" class="prev">← 回首頁</a><a href="/how/">我們怎麼看問題 →</a></div>
'''
write('/about/', page('about', about, desc='Propel AI 啟進智能決策：把行為經濟學的研究發現，轉成企業團隊能在工作上練習的步驟，再用實際數字觀察效果。'))

# ---------- contact ----------
book = cfg.get('booking_url'); form = cfg.get('form_url')
contact = f'''
    <span class="pill">聯絡</span>
    <h1>留下一件你想推動的事，我們回信</h1>
    <p class="lead">說你那件推不動的事，我們回信告訴你可能卡在哪、從哪一個課程開始最省。不適合，我們會直說。</p>
    {('<div class="cta-row"><a class="btn primary" href="'+book+'" target="_blank" rel="noopener">線上預約時間</a></div>') if book else ''}
    <p class="sub">例如：「我希望<b>業務同仁</b>，<b>每次拜訪客戶後</b>，<b>當天用 AI 整理會議紀錄</b>。」拆成三格填就好；不想填表的，寫信到 <a href="mailto:george.chen@propelaigrowth.com">george.chen@propelaigrowth.com</a> 也可以。</p>
    {microform('contact')}
    <h2>還沒準備好聊？</h2>
    <div class="menu">
      <a class="choice" href="/quiz/"><span><span class="q">先做兩分鐘小測驗</span><span class="a">三題、用點的、不用留資料</span></span><span class="go">→</span></a>
      <a class="choice" href="/downloads/"><span><span class="q">下載一頁介紹</span><span class="a">轉給同事或老闆看</span></span><span class="go">→</span></a>
      <a class="choice" href="https://www.linkedin.com/in/digitalgeorge" target="_blank" rel="noopener"><span><span class="q">LinkedIn 上的 George</span><span class="a">看他平常在寫什麼</span></span><span class="go">→</span></a>
    </div>
    <div class="nav"><a href="/" class="prev">← 回首頁</a></div>
'''
write('/contact/', page('contact', contact, desc='留下一件你想推動的事，我們回信告訴你可能卡在哪、從哪裡開始最省。'))


# ---------- English pages (/en/) v0.1 — texts from 英文官網四頁初稿 v0.2 + George's 1111 decisions ----------
def microform_en(ctx):
    return f"""
      <form class="mform" id="mform-{ctx}" novalidate>
        <input type="hidden" name="access_key" value="{FORM_KEY}">
        <input type="hidden" name="subject" value="Website (EN): one thing I want to make happen">
        <input type="hidden" name="from_name" value="Propel AI website (EN)">
        <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
        <label><span>I want</span><input name="who" placeholder="e.g. our sales team / clients who received a quote" required></label>
        <label><span>at</span><input name="when" placeholder="e.g. before the Monday meeting / within three days of the proposal" required></label>
        <label><span>to</span><input name="what" placeholder="e.g. open the AI tool and draft a first version / confirm the next meeting" required></label>
        <label><span>Company &amp; name</span><input name="name" placeholder="e.g. Acme Ltd., Mr. Chen" required></label>
        <label><span>Email</span><input name="email" type="email" placeholder="so we can write back" required></label>
        <div class="mrow"><button class="btn primary" type="submit">Send — we'll write back</button><span class="mnote">One sentence is enough. No fee, no sales call.</span></div>
        <p class="mdone" hidden>Got it. We'll look at which behavior is worth working on first and write back within two working days.</p>
      </form>"""

en_home = f"""
    <div class="hero">
      <div class="hero-t">
        <p class="eyebrow">You have explained it three times. They still haven't done it.</p>
        <h1>Before adding budget, make the behavior you want the easier choice</h1>
        <p class="lead">Courses and workshops that bring behavioral economics and AI into everyday business decisions. Our starting point is simple: change the environment, not the person.</p>
      </div>
      <svg class="hero-v" viewBox="0 0 320 200" role="img" aria-label="Before: everyone has to be persuaded again. After changing the environment: a clear path, one step fewer, a reminder at the right moment">
        <g font-family="Noto Sans TC,sans-serif" font-size="13" font-weight="700" fill="#003054">
          <text x="10" y="24">Before: persuade everyone, every time</text>
          <text x="10" y="124">After: let the behavior happen on its own</text>
        </g>
        <g stroke="#C9D3DB" stroke-width="6" stroke-linecap="round"><line x1="20" y1="60" x2="300" y2="60"/></g>
        <g fill="#5C6B78"><circle cx="30" cy="60" r="8"/><circle cx="120" cy="60" r="8"/><circle cx="210" cy="60" r="8"/></g>
        <g fill="#DDE3E8"><rect x="66" y="44" width="30" height="32" rx="5"/><rect x="156" y="44" width="30" height="32" rx="5"/><rect x="246" y="44" width="30" height="32" rx="5"/></g>
        <g font-family="Noto Sans TC,sans-serif" font-size="10.5" fill="#5C6B78"><text x="52" y="94">unclear info</text><text x="138" y="94">too many steps</text><text x="226" y="94">nagging</text></g>
        <g stroke="#F06000" stroke-width="6" stroke-linecap="round"><line x1="20" y1="160" x2="290" y2="160"/></g>
        <polygon points="288,148 310,160 288,172" fill="#F06000"/>
        <g fill="#F06000"><circle cx="30" cy="160" r="8"/><circle cx="115" cy="160" r="8"/><circle cx="200" cy="160" r="8"/></g>
        <g font-family="Noto Sans TC,sans-serif" font-size="10.5" font-weight="700" fill="#003054"><text x="40" y="190">default set</text><text x="118" y="190">one field fewer</text><text x="214" y="190">timely nudge</text></g>
      </svg>
    </div>
    <div class="menu doors">
      <a class="choice hot" href="/en/contact/"><span><span class="q">Have a specific problem in mind?</span><span class="a">Tell us about it in one sentence, and we'll write back</span></span><span class="go">→</span></a>
    </div>

    <section class="sec" id="pain">
      <p class="eyebrow">01</p>
      <h2>Does this sound familiar?</h2>
      <p class="sub">These are the three things we hear most often, almost word for word:</p>
      <div class="tiles">
        <div class="tile"><span class="k">Customers</span><b>"The proposal was solid, and the client still said, let me think about it."</b></div>
        <div class="tile"><span class="k">Employees</span><b>"We bought the AI tools and wrote the guidelines. Nobody uses them."</b></div>
        <div class="tile"><span class="k">The floor</span><b>"The SOP is crystal clear. People on the floor still do it the old way."</b></div>
      </div>
      <p class="big">Three different complaints, but they describe the same situation: the behavior you were counting on didn't happen.</p>
    </section>

    <section class="sec" id="how">
      <p class="eyebrow">02</p>
      <h2>Metrics are outcomes. Behavior is what you can actually work on.</h2>
      <p>Every number a company watches — revenue, adoption, repeat purchase — sits at the end of a chain. Somewhere in that chain, a specific person has to do a specific thing at a specific moment, and whether they do it depends a great deal on what they see in front of them, how many steps it takes, and what happens by default.</p>
      <div class="chain slim">
        <div class="c"><b>Environment</b>what they see, how many steps, what the default is</div><div class="ar">▶</div>
        <div class="c"><b>Behavior</b>who, at what moment, does which action</div><div class="ar">▶</div>
        <div class="c"><b>Metric</b>revenue, adoption rate, repeat purchase</div>
      </div>
      <p class="big">Behavior is not decided by the person alone. A large part of it is decided by the environment, and the environment is something you can arrange in advance.</p>
      <a class="more" href="/en/how/">Four examples: the default, the second option, who speaks first, and the follow-up email →</a>
    </section>

    <section class="sec" id="method">
      <p class="eyebrow">03</p>
      <h2>PROPEL™: six stations. It is a process, not a piece of software.</h2>
      <div class="strip">
        <div><b>P</b><i>Pinpoint</i><span>the behavior</span></div><div><b>R</b><i>Reconstruct</i><span>the chain</span></div><div><b>O</b><i>Obstacle</i><span>find it</span></div><div><b>P</b><i>Prescribe</i><span>a fix</span></div><div><b>E</b><i>Experiment</i><span>small scale</span></div><div class="later"><b>L</b><i>Loop</i><span>to the numbers</span></div>
      </div>
      <p>In every session the order is the same:</p>
      <div class="chips"><span>the team thinks first</span><i>→</i><span>AI fills in the gaps</span><i>→</i><span>the instructor guides the judgment</span><i>→</i><span>the team makes the call</span></div>
      <a class="more" href="/en/how/#propel">How this way of thinking becomes a path →</a>
    </section>

    <section class="sec" id="courses">
      <p class="eyebrow">04</p>
      <h2>Where would you like to start?</h2>
      <div class="tiles two">
        <div class="tile hot"><span class="k">Not sure whether this applies to you?</span><b>59-minute test drive</b><span class="d">We come to your office and work through one real question together. This is where most companies begin.</span></div>
        <div class="tile"><span class="k">Which decisions could your team be making better?</span><b>Half-day or full-day course</b><span class="d">Six or twelve questions, each one built around a single decision.</span></div>
        <div class="tile"><span class="k">Already know what's stuck?</span><b>Full-day workshop</b><span class="d">Bring your own problem and leave with an experiment you can run the following week.</span></div>
        <div class="tile"><span class="k">Sales and marketing teams looking for the original method and certificate?</span><b>SURF™ by MINDWORX</b><span class="d">The European program, delivered by a licensed trainer.</span></div>
      </div>
      <p class="note">Programs are delivered in Mandarin. Detailed program pages are in Mandarin; <a href="/en/contact/">write to us</a> and we'll tell you which one fits.</p>
    </section>

    <section class="sec" id="why">
      <p class="eyebrow">05</p>
      <h2>What you actually get</h2>
      <p class="sub">This is not a slide deck and a handout. Over the past two years we have built the materials a team needs to practice, not just listen:</p>
      <div class="facts4">
        <div><b>150</b><span>ready-made teaching modules</span></div>
        <div><b>67 / 101</b><span>common sticking points / fixes, each with its source</span></div>
        <div><b>AI</b><span>a question picker, a two-minute quiz, and a written prompt for every question</span></div>
        <div><b>MINDWORX</b><span>licensed SURF™ Method trainer and coach</span></div>
      </div>
      <a class="more" href="/en/about/">Every session is taught by George Chen in person｜About us →</a>
    </section>

    <section class="sec" id="next">
      <p class="eyebrow">06</p>
      <h2>Tell us one thing you would like to make happen</h2>
      <p class="sub">Think of it as a sentence with three blanks: I want <b>who</b>, at <b>when</b>, to <b>do what</b>. Fill in the three boxes and send — one sentence is enough. There is no fee and no sales call afterwards; we read it, think about which behavior is worth working on first, and write back within two working days.</p>
      {microform_en('en-home')}
    </section>
"""
write('/en/', page('en', en_home, nav_current='/en/'))

en_how = """
    <span class="pill">How we think</span>
    <h1>Metrics are outcomes. Behavior is what you can work on.</h1>
    <p class="lead">At Propel AI we use behavioral economics, with AI as a working tool, to make the behavior you want the easier choice — and we try to do it before anyone adds budget.</p>
    <h2>How we look at a problem</h2>
    <p>When a number is not moving, most companies look at the people and ask why they are not trying harder. We look one step earlier, at the environment those people are working in: what they see, how many steps the task takes, and what happens if they do nothing. That is the step most companies skip, and it is usually where the answer is.</p>
    <div class="chain">
      <div class="c"><b>Environment</b>what they see, how many steps, what the default is<br><span class="note">the step we add</span></div><div class="ar">▶</div>
      <div class="c"><b>Behavior</b>a specific person, at a specific moment, doing one visible action<br><span class="note">the part you can change</span></div><div class="ar">▶</div>
      <div class="c"><b>Metric</b>revenue, adoption rate, repeat purchase<br><span class="note">moves only when the behavior moves</span></div>
    </div>
    <h2>Behind every metric is a chain of behavior</h2>
    <table>
      <tr><th>At this moment</th><th>this person does this action</th><th>and only then does this metric move</th></tr>
      <tr><td>A shopper with items in the cart, just before leaving the site</td><td>clicks "Checkout"</td><td>checkout rate</td></tr>
      <tr><td>A salesperson, at the start of the working day</td><td>opens the AI tool to draft the plan</td><td>adoption rate</td></tr>
      <tr><td>A customer, in the week the product is about to run out</td><td>clicks "Buy again"</td><td>repeat purchase</td></tr>
    </table>
    <p>So we don't start with "how do we grow revenue." We start with a narrower question: who, at what moment, is not doing which action?</p>
    <h2>What does "changing the environment" look like? Three examples</h2>
    <div class="cards">
      <div class="card"><h3>Change the default</h3><p>A green electricity plan — same plan, same price. When customers had to tick a box to opt in, 7% took it. When they were enrolled by default and could untick to opt out, 69% stayed in.</p></div>
      <div class="card"><h3>Offer two options instead of one</h3><p>On a product page, showing a single option led 9% of visitors to buy. Showing two options side by side raised that to 66%.</p></div>
      <div class="card"><h3>Speak first</h3><p>When a customer asks "roughly how much," opening with "what's your budget?" and opening with a reasoned number lead to very different places. The side that names a number first tends to pull the final price its way.</p></div>
    </div>
    <p class="note">External studies, not Propel AI client results｜Sources: Ebeling &amp; Lotz (2015) Nature Climate Change｜Mochon (2013) J. Consumer Research｜Gunia et al. (2013) Personality and Social Psychology Bulletin</p>
    <h2>The same idea, applied in your company: the follow-up email after a quote</h2>
    <div class="vs three">
      <div class="card"><h3>Before</h3><p>"Please find the quote attached. Let me know if you have any questions."</p><p class="note">The ball is entirely in the client's court</p></div>
      <div class="card"><h3>Where it sticks</h3><p>The easiest thing for a busy client to do with that email is nothing.</p><p class="note">Nobody has set the next step, or a time for it</p></div>
      <div class="card us"><h3>After</h3><p>"Quote attached. I'll call you Thursday afternoon to see whether anything needs adjusting."</p><p class="note">The next step is already decided; the client only has to not object</p></div>
    </div>
    <p class="note">An illustration, not a client result.</p>
    <h2>How this differs from the usual approach</h2>
    <div class="cards">
      <div class="card"><h3>We aim at the environment, not the person</h3><p>Explaining again, issuing an instruction, repeating the message — these work for as long as someone keeps pushing, and the numbers tend to slide back the moment the effort stops.</p></div>
      <div class="card"><h3>We look before we spend</h3><p>Find the step where things are stuck first, and only then decide whether money is actually needed.</p></div>
      <div class="card"><h3>You judge, AI supplements, you decide</h3><p>What AI offers is a second opinion, and we treat it as a hypothesis until the numbers say otherwise.</p></div>
    </div>
    <h2 id="propel">This way of looking at a problem follows a fixed path</h2>
    <p>We call it PROPEL™ — six stations, from pinpointing the behavior to looping back to the numbers: <b>P</b>inpoint, <b>R</b>econstruct, <b>O</b>bstacle, <b>P</b>rescribe, <b>E</b>xperiment, <b>L</b>oop. The full-day workshop walks that path from beginning to end, and every station leaves the team with one sheet of paper they can use the following week.</p>
    <div class="cta">
      <a class="btn primary" href="/en/contact/">Tell us one thing, and we'll write back</a>
    </div>
    <div class="nav"><a href="/en/" class="prev">← Home</a><a href="/en/about/">About Propel AI →</a></div>
"""
write('/en/how/', page('en-how', en_how))

en_about = """
    <span class="pill">About</span>
    <h1>We do one thing: make the behavior you want the easier choice</h1>
    <p class="lead">The proposal went out, and the client never took the next step. The AI tools were bought, and the team never really picked them up. The SOP was written clearly, and the floor kept working the way it always had. These are the situations Propel AI was built for. Through courses and workshops, we teach teams to use behavioral economics and AI to find out why customers don't move forward and colleagues don't act, and then to adjust the process, the message, and the environment in which those decisions are made.</p>
    <h2>Three things we believe</h2>
    <div class="cards">
      <div class="card"><h3>An outcome is not a behavior</h3><p>Revenue and adoption are results. What a team can actually work on is who does which action, and when.</p></div>
      <div class="card"><h3>Personality is not the cause</h3><p>"He's lazy" or "she doesn't care" is where the conversation usually ends, and it is rarely where the problem is. More often the step takes too much effort, is too easy to forget, or nobody has gone first.</p></div>
      <div class="card"><h3>A hypothesis is not a conclusion</h3><p>Every fix is a guess until it has been tried on a small scale and the numbers have been read. Then the team keeps it, adjusts it, or replaces it.</p></div>
    </div>
    <h2>Why behavioral economics</h2>
    <p>Companies know their own sales process very well. What they see less clearly is the process from the customer's side: what he has to do at each step, what he is worried about, and who else has to sign off before he can say yes. Those things the customer must get done don't always appear anywhere in our process, and they are exactly what behavioral economics is about. Beyond need and willingness, how the options are laid out, how many steps it takes, and how the reminder arrives all shape a decision.</p>
    <p>For a long time, behavioral economics was something governments and large corporations brought in through consultants. Most companies have heard of it and would like to try it on their own business, but they rarely know where to begin: the research takes time to read, and there has been no set of tools that connects the findings to the steps of everyday work. That connection is what we have spent the last few years building — turning research findings into steps a business team can practice at work, and then watching the effect in their own numbers.</p>
    <h2>What teams practice in the room</h2>
    <div class="cards">
      <div class="card"><div class="n">1</div><h3>Break it into a visible action</h3><p>"Grow revenue" or "get people to use the tool" becomes who, at what moment, does which action.</p></div>
      <div class="card"><div class="n">2</div><h3>Find where it sticks and design a fix</h3><p>Work out why that action might stall, and design a change that doesn't begin by adding budget.</p></div>
      <div class="card"><div class="n">3</div><h3>Read your own numbers</h3><p>Try the change on a small scale, look at the numbers, and then decide whether to keep it, adjust it, or move to another spot. How long to watch depends on how often the behavior happens; for frequent behaviors, one to two weeks is enough for a first look.</p></div>
    </div>
    <p>Along the way the team works with an AI tool we built ourselves, backed by a library of 67 common sticking points and 101 fixes. The order never changes: the team thinks first, AI adds what might have been overlooked, the instructor guides the judgment, and the team decides. After the course, the AI stays with you — we provide written prompts, so that back at the office you can paste your real situation into whatever AI tool you normally use and walk through the same steps again.</p>
    <h2>Method, materials, partner</h2>
    <ul class="facts">
      <li><b>Method</b><span>PROPEL™, six stations: Pinpoint, Reconstruct, Obstacle, Prescribe, Experiment, Loop. From a fuzzy problem to a fix you can test.</span></li>
      <li><b>Materials</b><span>Eight pain points and 150 teaching modules. Six questions in a half day, twelve in a full day; each question is one decision, one principle, three cases, and one AI prompt.</span></li>
      <li><b>Library</b><span>67 common sticking points and 101 fixes. This is what sits underneath both the AI tool and the handouts.</span></li>
      <li><b>Partner</b><span>MINDWORX, a European behavioral economics consultancy founded in 2015 and now present in Europe and North America, with work for companies in the Allianz, Generali, UniCredit and Zurich groups. Propel AI is its licensed SURF™ Method trainer and coach for Taiwan.</span></li>
    </ul>
    <h2>Who teaches</h2>
    <div class="who"><img class="av" src="/assets/george.jpg" alt="George Chen" width="56" height="56"><div><h3>George Chen｜Founder. He teaches every session himself.</h3><p>George holds an MBA from the University of Chicago Booth School of Business (with Honors, top 20% of the class), where he took a course taught by Richard Thaler, the 2017 Nobel laureate in economics. He spent many years at Oracle, as Marketing Director for Oracle Hong Kong and Taiwan and as APAC Applications Campaign Lead, and he is a licensed trainer and coach for the MINDWORX SURF™ Method. "How do you get a customer to take the next step?" was the question his teams worked on at Oracle year after year.</p></div></div>
    <p class="note">Full credentials are in the company profile and in the pre-course notes for each program. SURF™ is MINDWORX's method; Propel AI's own courses and workshops are of our own design.</p>
    <h2>Company</h2>
    <ul class="facts">
      <li><b>Name</b><span>Propel AI Co., Ltd.（啟進智能決策有限公司）</span></li>
      <li><b>Tax ID</b><span>61933866</span></li>
      <li><b>Address</b><span>12F, No. 1-2, Sec. 5, Zhongxiao E. Rd., Taipei, Taiwan</span></li>
      <li><b>Contact</b><span>george.chen@propelaigrowth.com｜<a href="/en/contact/">Tell us one thing</a></span></li>
    </ul>
    <div class="nav"><a href="/en/" class="prev">← Home</a><a href="/en/how/">How we think →</a></div>
"""
write('/en/about/', page('en-about', en_about))

en_contact = f"""
    <span class="pill">Contact</span>
    <h1>Tell us one thing, and we'll write back</h1>
    <p class="lead">Describe the one thing you haven't been able to get moving. We'll reply with where it is probably stuck and where it would make sense to start. If we are not the right fit for it, we will tell you that too.</p>
    <p class="sub">An example of the kind of sentence we mean: "I want <b>our sales reps</b>, <b>after every client visit</b>, <b>to write up the meeting notes with AI on the same day</b>." Three boxes are all it takes. If you would rather not fill in a form, an email to <a href="mailto:george.chen@propelaigrowth.com">george.chen@propelaigrowth.com</a> works just as well.</p>
    {microform_en('en-contact')}
    <h2>Not ready to talk yet?</h2>
    <div class="menu">
      <a class="choice" href="/en/how/"><span><span class="q">Read how we look at a problem</span><span class="a">Three examples of changing the environment, and one follow-up email</span></span><span class="go">→</span></a>
      <a class="choice" href="https://www.linkedin.com/in/digitalgeorge" target="_blank" rel="noopener"><span><span class="q">George on LinkedIn</span><span class="a">See what he writes about each week</span></span><span class="go">→</span></a>
    </div>
    <p class="note">Programs are delivered in Mandarin.</p>
    <div class="nav"><a href="/en/" class="prev">← Home</a></div>
"""
write('/en/contact/', page('en-contact', en_contact))

# ---------- articles (from data/articles.json) ----------
arts = json.loads((pathlib.Path(__file__).parent/'data/articles.json').read_text(encoding='utf-8')) if (pathlib.Path(__file__).parent/'data/articles.json').exists() else []
items=[]
for a in arts:
    slug=a['slug']; body=a['html']
    art = f'''
    <span class="pill">文章｜{a['date']}</span>
    <h1>{html.escape(a['title'])}</h1>
    {body}
    <p class="note">這篇也發在 <a href="{a.get('linkedin','https://www.linkedin.com/in/digitalgeorge')}" target="_blank" rel="noopener">LinkedIn</a>。想聊這一題，<a href="/contact/">留下一件事</a>。</p>
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
    <div class="nav"><a href="/" class="prev">← 回首頁</a><a href="/contact/">留下一件事 →</a></div>
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
urls = [URL[k] for k in ['home','how','trial','half','ws','surf','trial-prep','half-prep','ws-prep','surf-prep','quiz','picker','docs','about','contact','articles','en','en-how','en-about','en-contact']] + [f'/articles/{a["slug"]}/' for a in arts]
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
shutil.copy(pathlib.Path(__file__).parent/'george.jpg', OUT/'assets/george.jpg')
print('built', sum(1 for _ in OUT.rglob('index.html')), 'pages;', len(list((OUT/'assets/img').iterdir())), 'images')
