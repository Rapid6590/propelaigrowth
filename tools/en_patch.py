# en_patch.py v0.3 (2026-11-19) — 英文站：主選單換成四步＋英文版「算算看」/en/calc/＋英文版 AI 頁 /en/ai/
#   v0.3：英文文案照「英文網站中英對照表」v0.2 校訂＋George 1119 裁示改（統一用詞：action you want to see easier to take／topic／we review it together／GPS, gas pedal／All programs are taught in Mandarin／compound）。
#   v0.2：George 看過預覽——算算看表頭（Now／Lift）沒對到輸入格 → 英文表頭改成置中；加英文版 AI 頁（內容對照 ai_page.py v0.2）。
# v0.4 (2026-11-24)：英文算算看表頭改用跟中文同一套 .cc-hf 排法，拿掉原本用 padding 湊的那兩條。
# 用法：python3 tools/en_patch.py <站台根目錄>   可重跑（冪等）。只動 /en/ 底下的頁（外加中文 /calc/ 的語言切換與 hreflang）。
# 順序：… → calc_page → … → wayfinding → en_patch（放最後；它拿 /en/about/ 當外框，也要讀 calc_page.py 的程式）。
# 規矩（George 1118–1119）：
#   - 英文站跟中文站同一套導覽：四步 ① What's stuck ② See why ③ Where to start ④ Talk to us（量過寬度：Find what's stuck／Choose where to start 在 1100 與 375 寬都會折成兩行，所以用短的）。
#     英文站頁數少：第 1、3 步連到英文首頁的段落（#pain、#courses），不展開；第 2、4 步才有下一層。
#   - 英文算算看跟中文版同一份算式與示範數字（CHAINS_EN 逐關對照 calc_page.py 的 CHAINS；改數字兩邊一起改）。
#   - 數字全是示意；免責句是中文統一句的英譯，英文頁要用照抄 DISCLAIMER_EN。
#   - 課程以中文授課，英文頁不放課程細節；CTA 導到 /en/contact/。
import sys, re, json, html, pathlib
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
HERE = pathlib.Path(__file__).parent
SITE = 'https://propelaigrowth.com'
def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')
def esc(s): return html.escape(s, quote=True)

# ---- 英文站唯一的一份選單：(名字, 入口, [(網址, 選單上的名字)]) ----
STEPS = [
    ("What's stuck", '/en/#pain', []),
    ('See why', '/en/how/', [('/en/how/', 'How we think'), ('/en/ai/', 'Where AI fits'), ('/en/calc/', 'Do the math')]),
    ('Where to start', '/en/#courses', []),
    ('Talk to us', '/en/contact/', [('/en/about/', 'About us'), ('/en/contact/', 'Contact')]),
]
ZH = {'/en/': '/', '/en/how/': '/how/', '/en/about/': '/about/', '/en/contact/': '/contact/', '/en/calc/': '/calc/', '/en/ai/': '/ai/'}

def header(url):
    cur = next((i for i, (_, _, items) in enumerate(STEPS, 1) if any(u == url for u, _ in items)), None)
    nav, sub = [], ''
    for i, (name, href, items) in enumerate(STEPS, 1):
        links = ''.join(f'<a href="{u}"' + (' aria-current="page"' if u == url else '') + f'>{esc(n)}</a>' for u, n in items)
        if i == cur:
            nav.append(f'<div class="wf-step cur"><a href="{href}" aria-current="step"><i>{i}</i>{esc(name)}</a></div>')
            sub = f'<div class="wf-sub t{i}" role="group" aria-label="{esc(name)}: pages in this step">{links}</div>'
        elif items:
            nav.append(f'<div class="wf-step"><a href="{href}"><i>{i}</i>{esc(name)}</a>'
                       f'<div class="wf-drop" role="group" aria-label="{esc(name)}: pages in this step"><div>{links}</div></div></div>')
        else:
            nav.append(f'<div class="wf-step nodrop"><a href="{href}"><i>{i}</i>{esc(name)}</a></div>')
    return ('<header class="sitehead">\n'
            '    <a class="wordmark" href="/en/">PROPEL AI<small>Behavioral economics × behavior design × AI</small></a>\n'
            f'    <a class="lang" href="{ZH[url]}" hreflang="zh-Hant" lang="zh-Hant">中文</a>\n'
            f'    <nav class="wf-nav" aria-label="Main menu">{"".join(nav)}{sub}</nav>\n'
            '  </header>')

CSS = '''
/* en:css */
.wf-step.nodrop>a::after{content:none!important}
@media (max-width:640px){.pg-en-calc .cc-after::before{content:"After"}}
.pg-en-ai .ai-flow li{font-size:13.5px}
/* 英文選單：四格等高（量過 1100／375 寬，Find what's stuck 與 Choose where to start 都會折行，所以用短字） */
[lang=en] .wf-step>a{height:100%;box-sizing:border-box}
/* /en:css */
'''
css = re.sub(r'\n/\* en:css \*/.*?/\* /en:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

# ---------- 英文算算看 ----------
DISCLAIMER_EN = 'These numbers are illustrations, not promises. Actual gains must be measured in your own process.'
# 每關：(名字, 原本 %, 多幾 %, 示範改法, 這一輪先動?)——數字與順序同 calc_page.py 的 CHAINS
CHAINS_EN = [
    {'id': 'b2c', 'tab': 'Selling to consumers', 'start': 10000, 'unit': 'people', 'startLabel': 'people who see the ad', 'endLabel': 'payment completed',
     'gates': [
        ('See the ad → click', 3, 20, 'Change “Save 300 today” to “In two days, you’ll miss out on the 300 discount.”', True),
        ('Land → view product page', 60, 15, 'Use the same message as the ad on the landing page, with one clear next step', False),
        ('Product page → add to cart', 30, 20, 'Show a real purchase count, and pre-select the most popular option', False),
        ('Cart → start checkout', 40, 20, 'Show shipping up front; cut the form from ten fields to four', True),
        ('Checkout → pay', 85, 5, 'Add a one-line guarantee; if payment isn’t finished, send one reminder within the hour', False)],
     'src': 'Loss framing, number of options, descriptive norms and defaults, friction and timing of disclosure, timing of reminders. Full references are listed in our company profile and course materials.'},
    {'id': 'b2b', 'tab': 'Selling to companies', 'start': 100, 'unit': 'accounts', 'startLabel': 'accounts on your target list', 'endLabel': 'renewed',
     'gates': [
        ('Get a meeting with the decision maker', 20, 15, 'Keep the ask small and specific, and add “No worries if now isn’t a good time.”', True),
        ('Agree on a next step', 50, 20, 'Before the meeting ends, record the next step, owner, and date', False),
        ('Choose a plan after the quote', 40, 25, 'Offer three plans, not eight, and mark the one most clients choose', True),
        ('Get internal approval', 60, 15, 'Write the one page they’ll show their boss, and open with the cost of doing nothing', False),
        ('Renew the agreement', 70, 10, 'Send a reminder 90 days before the agreement expires, with one page on what the year delivered', False)],
     'src': 'Small, specific requests; implementation intentions; number of options and anchoring; loss framing; defaults and timing of reminders. Full references are listed in our company profile and course materials.'},
    {'id': 'gov', 'tab': 'Public services', 'start': 10000, 'unit': 'people', 'startLabel': 'eligible residents', 'endLabel': 'completed',
     'gates': [
        ('Receive the notice → decide to apply', 40, 15, 'The first line says what to do and by which date; if it’s true, add “Most people have already applied.”', False),
        ('Decide → find the form', 50, 20, 'The link goes straight to the application form, not to the agency home page', True),
        ('Find it → start the application', 60, 20, 'With consent, pre-fill what the agency already has; 12 fields become 3', True),
        ('Start → submit', 70, 10, 'The last field on the form asks: “Which day do you plan to submit?”', False),
        ('Submit → done (incl. follow-up documents)', 80, 10, 'The follow-up notice says which document is missing, by which date, and where to send it', False)],
     'src': 'Wording of notices and social norms, one step fewer, pre-filled data, writing down a date, specific instructions. Full references are listed in our company profile and course materials.'},
]
# 跟中文版逐關核對數字（中文改了而英文沒跟上時，這裡會停下來）
ns = {}
src = (HERE / 'calc_page.py').read_text(encoding='utf-8')
exec(src[src.index('CHAINS = ['):src.index("CSS = '''")], ns)
for zc, ec in zip(ns['CHAINS'], CHAINS_EN):
    assert zc['id'] == ec['id'] and zc['start'] == ec['start'], ('英文算算看的起點跟中文版不一樣', zc['id'])
    assert [g[1:3] + g[4:] for g in zc['gates']] == [g[1:3] + g[4:] for g in ec['gates']], ('英文算算看的數字跟中文版不一樣', zc['id'])

JS = src[src.index("JS = r'''") + 9:]
JS = JS[:JS.index("'''")]
TR = [
    ("state.unit + '（' + state.startLabel + '）'", "state.startLabel"),
    ("aria-label=\"第 ' + (i + 1) + ' 關的名字\"", "aria-label=\"Name of step ' + (i + 1) + '\""),
    ("<label>原本通過</label>", "<label>Now</label>"),
    ("aria-label=\"第 ' + (i + 1) + ' 關原本通過幾 %\"", "aria-label=\"Step ' + (i + 1) + ': pass rate now, in %\""),
    ("<label>多幾 %</label>", "<label>Lift</label>"),
    ("aria-label=\"第 ' + (i + 1) + ' 關多幾 %\"", "aria-label=\"Step ' + (i + 1) + ': lift, in %\""),
    ("aria-label=\"這一輪先動第 ' + (i + 1) + ' 關\"", "aria-label=\"Change step ' + (i + 1) + ' first this round\""),
    ("<span hidden>這一輪先動</span>", "<span hidden>Change first</span>"),
    ("aria-label=\"拿掉第 ' + (i + 1) + ' 關\" title=\"拿掉這一關\"", "aria-label=\"Remove step ' + (i + 1) + '\" title=\"Remove this step\""),
    ("<b>示範改法</b>　", "<b>Example change</b>&nbsp; "),
    ("'走到這一關還剩：原本 ' + fmt(a) + ' ' + state.unit + '，每關都動過之後 ' + fmt(c) + ' ' + state.unit",
     "'Left after this step: ' + fmt(a) + ' now, ' + fmt(c) + ' with every step improved'"),
    ("'<em>' + (b / a).toFixed(1) + ' 倍</em>'", "'<em>' + (b / a).toFixed(1) + '×</em>'"),
    ("'<em>' + (c / a).toFixed(1) + ' 倍</em>'", "'<em>' + (c / a).toFixed(1) + '×</em>'"),
    ("picked ? '只動打勾的 ' + picked + ' 關' : '還沒勾要先動哪一關'", "picked ? 'only the ' + picked + (picked > 1 ? ' ticked steps' : ' ticked step') : 'no step ticked yet'"),
    ("n + ' 關都動過'", "'all ' + n + ' steps improved'"),
    ("(maxLift <= 30 ? '最多的一關也只多了 <b>' : '最多的一關多了 <b>') + maxLift + '%</b>；' + n + ' 關乘起來，是原本的 <b>' + (c / a).toFixed(1) + ' 倍</b>。'",
     "(maxLift <= 30 ? 'No step improved by more than <b>' : 'The biggest single step improved by <b>') + maxLift + '%</b>. Across ' + n + ' steps, the gains compound to <b>' + (c / a).toFixed(1) + '×</b> the starting result.'"),
    ("'這一輪只動 ' + picked + ' 關，就已經是 <b>' + (b / a).toFixed(1) + ' 倍</b>。'",
     "' Improving just ' + picked + (picked > 1 ? ' steps' : ' step') + ' this round gives <b>' + (b / a).toFixed(1) + '×</b> in this illustration.'"),
    ("'把每一關的數字填上去，下面就會算。'", "'Fill in a number for each step and the result appears below.'"),
    ("'有一關已經推到 100%：通過率最多就是全部的人，再往上沒有了。'", "' One step has reached 100%. A pass rate cannot go higher than everyone.'"),
    ("name:'再一關'", "name:'One more step'"),
    ('maxlength="24"', 'maxlength="40"'),
]
for a, b in TR:
    assert JS.count(a) == 1, ('calc_page.py 的 JS 改過了，英文對照要跟著改', a)
    JS = JS.replace(a, b)
assert not re.search(r'[一-鿿]', JS), '英文算算看的 JS 還有中文字'

tabs = ''.join(f'<button type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}">{esc(c["tab"])}</button>' for i, c in enumerate(CHAINS_EN))
calc_body = f'''<span class="pill">Do the math</span>
    <h1>Small gains at each step. See how they compound.</h1>
    <p class="lead">A customer, an employee or a resident may need to clear several steps in a row. Make each of ten steps 10% better and you get about 2.6×. Let each slip 10% and 0.35× is left. The three chains below are illustrations; change any number to your own.</p>
    <div class="cc">
      <div class="cc-tabs" role="tablist" aria-label="Choose an example chain">{tabs}</div>
      <div class="cc-start"><label for="cc-start">Start with</label><input id="cc-start" type="number" inputmode="numeric" min="0" step="1" value="10000"><span id="cc-startlabel"></span></div>
      <div class="cc-head" aria-hidden="true"><span>Step</span><span class="cc-hf"><b>Now</b><i>%</i></span><span class="cc-hf"><i>+</i><b>Lift</b><i>%</i></span><span class="cc-ha"><b>After</b><i>00%</i></span><span>First</span><span></span></div>
      <div id="cc-rows"></div>
      <button class="cc-add" id="cc-add" type="button">+ Add a step</button>
      <div class="cc-out" aria-live="polite">
        <h2>How many make it through every step</h2>
        <div class="cc-bar r0"><div class="t"><b>Now</b><small>nothing changed</small></div><div class="b"><i id="cc-b0"></i><span id="cc-v0"></span></div></div>
        <div class="cc-bar r1"><div class="t"><b>This round</b><small id="cc-t1"></small></div><div class="b"><i id="cc-b1"></i><span id="cc-v1"></span></div></div>
        <div class="cc-bar r2"><div class="t"><b>After several rounds</b><small id="cc-t2"></small></div><div class="b"><i id="cc-b2"></i><span id="cc-v2"></span></div></div>
        <p class="cc-say" id="cc-say"></p>
      </div>
      <p class="disc">{esc(DISCLAIMER_EN)} Everything on this page is calculated in your browser. Nothing is sent anywhere.</p>
      <details><summary>The research themes behind the example changes</summary><p id="cc-src" style="margin:6px 0 0"></p></details>
      <div class="cc-bridge">
        <h2>“My process doesn’t have these steps.”</h2>
        <p>Right. These are examples, not templates. At the second station of our full-day workshop, you map your own process in four to seven steps and circle the one or two that are most stuck.</p>
        <p>Change only those one or two at a time, and watch one number for two weeks. Improving every step takes several rounds.</p>
      </div>
      <div class="cta-row" style="margin-top:18px">
        <a class="btn primary" href="/en/contact/">Tell us one thing, and we’ll write back</a>
        <a class="btn secondary" href="/en/how/">See how we look at a problem</a>
      </div>
      <p class="note">All programs are taught in Mandarin.</p>
    </div>
<script>{JS.replace('__CHAINS__', json.dumps(CHAINS_EN, ensure_ascii=False, separators=(',', ':')))}</script>
      <div class="nav"><a href="/en/how/" class="prev">← How we think</a><a href="/en/">Home</a></div>'''

tpl = rd('en/about/index.html')
tpl = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', tpl)
HEAD, REST = tpl[:tpl.index('<main>') + 6], tpl[tpl.index('</main>'):]
title = 'Do the math: small gains at each step compound'
desc = 'To get anything done, people have to clear several steps in a row. Enter the pass rate for each step and see how small gains at every step compound. Three example chains. Nothing is collected.'
ALT = ('<link rel="alternate" hreflang="zh-Hant" href="{s}/calc/"><link rel="alternate" hreflang="en" href="{s}/en/calc/">'
       '<link rel="alternate" hreflang="x-default" href="{s}/calc/">').format(s=SITE)
h = HEAD
h = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}｜Propel AI</title>', h)
h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title) + '｜Propel AI', h)
h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
h = h.replace(f'{SITE}/en/about/', f'{SITE}/en/calc/')
h = re.sub(r'<body class="[^"]*">', '<body class="pg-en-calc">', h)
h = h.replace('</head>', ALT + '\n</head>', 1)
wr('en/calc/index.html', h + '\n    ' + calc_body + '\n' + REST)

# ---------- 英文版 AI 頁（內容對照 ai_page.py；圖直接取那邊的 SVG，換掉圖上的中文字） ----------
asrc = (HERE / 'ai_page.py').read_text(encoding='utf-8')
ans = {'esc': esc}
exec(asrc[asrc.index('# 主圖：'):asrc.index('def stat_block')], ans)
SVG_TR = {
    'HERO': [('左邊是導航螢幕，上面畫出一條路線；右邊是一隻腳踩在油門上。導航算得出路，車要動還是要有人踩油門。', 'Left: a GPS screen with a route. Right: a foot on the gas pedal. The GPS plans the route; someone still has to step on the gas.'),
             ('AI：把路算出來', 'AI plans the route'), ('文案、簡報、報表、程式碼', 'Copy, decks, reports, code'),
             ('人：踩下油門', 'People step on the gas'), ('客戶點頭、同仁照做、民眾來辦', 'Customers reply. Teams follow through.')],
    'ONE': [('左邊：六個人看同一則訊息。右邊：六個人各自收到不同的訊息。', 'Left: six people see the same message. Right: each of six people gets a different message.'),
            ('以前：同一句話，同一個時間', 'Before: one message for all'), ('現在：各自的話，各自的那一秒', 'Now: one for each person')],
    'BILL': [('示意圖：一張用電通知，下面多了三條橫條，比較你家、相似的家庭、省電的家庭。', 'Illustration: an energy report with three bars comparing your home, similar homes and efficient homes.'),
             ('本月用電通知', 'Your energy report'), ('你家', 'You'), ('相似家庭', 'Similar'), ('省電家庭', 'Efficient')],
    'CUP': [('示意圖：儀表板中間亮起一個咖啡杯圖示，旁邊寫著該休息了嗎。', 'Illustration: a coffee cup icon lights up on the dashboard, with the words Time for a rest?'),
            ('font-size="10" font-weight="700" fill="#fff" text-anchor="middle">該休息了嗎？', 'font-size="8.5" font-weight="700" fill="#fff" text-anchor="middle">Time for a rest?')],
    'EG_L': [('一份提案，用 AI 一個小時就寫好。', 'A proposal, written with AI in one hour.'), ('提案寫好了', 'Proposal written'), ('用 AI，一個小時', 'With AI, in one hour'), ('做出來：變快了', 'Writing the proposal: faster')],
    'EG_R': [('客戶的訊息畫面：提案已讀，三天沒有回覆。', 'The customer’s message thread: proposal read, no reply for three days.'), ('提案在附件，請參考', 'Proposal attached'),
             ('>已讀<', '>Read<'), ('三天了，沒有回覆', 'Three days. No reply.'), ('對方照著做：沒有變容易', 'Getting a reply: no easier')],
}
G = {}
for k, pairs in SVG_TR.items():
    v = ans[k]
    for a_, b_ in pairs:
        assert v.count(a_) == 1, ('ai_page.py 的圖改過了，英文對照要跟著改', k, a_)
        v = v.replace(a_, b_)
    assert not re.search(r'[一-鿿]', v), ('英文 AI 頁的圖還有中文字', k)
    G[k] = v
AI_STATS = [
    ('Not just you', 'Individual tasks got faster. Company numbers haven’t caught up.', [
        (80, 'of respondents say AI has improved their own productivity', False),
        (37, 'say AI has contributed to their company’s earnings', True)], '', False),
    ('Why', 'The gap is more about the workplace than about individual willingness', [
        (67, 'Organizational factors: culture, manager support, talent practices', True),
        (32, 'Individual mindset and behavior', False)], 'Relative importance of workplace and individual factors in self-reported AI benefits', True),
]
def stat_block(tag, title, rows, cmp, key):
    r = ''.join(f'<div class="ai-row{" o" if o else ""}"><b>{v:g}%</b><span>{esc(t)}</span><div class="ai-bar"><i style="width:{v:g}%"></i></div></div>' for v, t, o in rows)
    c = f'<p class="cmp">{esc(cmp)}</p>' if cmp else ''
    return f'<div class="ai-stat{" ai-key" if key else ""}"><h3><small>{esc(tag)}</small>{esc(title)}</h3>{c}{r}</div>'
ai_stats = ''.join(stat_block(*x) for x in AI_STATS)
AI_SRC = ('External surveys, not Propel AI client results. Sources: McKinsey, The state of AI in 2026 (1,719 respondents, 97 countries). '
          'Microsoft, 2026 Work Trend Index (20,000 people who use AI at work, 10 markets; 67% and 32% are relative importance in a model, not causation).')
ai_body = f'''<span class="pill">Where AI fits</span>
    <h1><span class="nb">AI can produce the work.</span> <span class="nb">People still have to act on it.</span></h1>
    <p class="lead">AI can help create copy, slide decks, reports and code — often faster and at lower cost. But a customer saying yes, a team following a new process, or a resident completing an application still takes more than another document.</p>
    <figure class="ai-fig">{G["HERO"]}</figure>
    <p class="ai-cap">AI is the GPS, not the gas pedal.<small>It can plan the route. Someone still has to step on the gas.</small></p>

    <section class="sec">
    <h2><span class="nb">Using AI,</span> <span class="nb">but not seeing it in the numbers?</span></h2>
    <div class="ai-eg">{G["EG_L"]}<i></i>{G["EG_R"]}</div>
    <p class="ai-say"><span class="nb">AI made producing it faster.</span> <span class="nb">It didn’t make getting them to act any easier.</span><small>And revenue moves only when they act.</small></p>
    <div class="ai-stats">{ai_stats}</div>
    <div class="ai-so"><small>So</small><b>What we do is the step after AI has done its part: getting customers to reply and teams to follow through.</b><span>We change what people face at the moment they decide: what they see, how many steps it takes, when the reminder shows up.</span></div>
    <p class="note">{esc(AI_SRC)}</p>
    </section>

    <section class="sec">
    <h2><span class="nb">Before: one version for everyone.</span> <span class="nb">With AI: one for each person.</span></h2>
    <p>The same sign, the same letter, the same default: that was most of what could be done before. Now data records what each person actually did, and AI helps decide what to say to them and when. The principle stays the same: change the environment, not the person. AI can help tailor reminders to each situation.</p>
    <figure class="ai-fig">{G["ONE"]}</figure>
    <h3 style="margin-top:18px">Two examples already in use</h3>
    <div class="ai-ex">
    <div><span class="tag2">Government</span>{G["BILL"]}<h3>Japan’s Ministry of the Environment: a home energy report that shows how similar homes compare</h3>
    <p>Five electricity and gas utilities sent it to about 300,000 households over four years. Each household received a report written from its own usage. Energy use fell by about 2% on average.</p>
    <p>The Ministry calls this direction BI-Tech: behavioral science combined with data and AI, so that each household gets its own version.</p>
    <p class="src">Source: Ministry of the Environment, Japan, nudge program; Oracle Japan and Jyukankyo Research Institute (field trials, fiscal 2017–2020)</p></div>
    <div><span class="tag2">Business</span>{G["CUP"]}<h3>Mercedes-Benz ATTENTION ASSIST: it learns how you drive, then suggests a rest</h3>
    <p>In the first 20 minutes of a trip, the system records how you are driving, using 70 parameters. Later, when the steering shows the corrections typical of a tired driver, a coffee cup lights up on the dashboard and a tone sounds.</p>
    <p>There is no “Do not drive tired” sign. It reminds that one driver, at that moment.</p>
    <p class="src">Source: Mercedes-Benz press material (introduced in 2009)</p></div>
    </div>
    <p class="note">Both drawings are illustrations.</p>
    </section>

    <section class="sec">
    <h2>Where AI sits in our programs</h2>
    <p>The sequence stays the same:</p>
    <ol class="ai-flow"><li><small>1</small>Your team thinks it through</li><li class="on"><small>2</small>AI offers a second opinion</li><li><small>3</small>We review it together</li><li><small>4</small>Your team decides</li></ol>
    <div class="ai-do">
    <div><h3>Choosing</h3><p>AI helps the team pick which behavior to change first.</p></div>
    <div><h3>Checking</h3><p>It checks your analysis against 67 common sticking points and 101 fixes, to flag what you might have missed.</p></div>
    <div><h3>Taking it back</h3><p>One AI prompt per topic, printed in the handout, so you can run your own case again at work.</p></div>
    </div>
    <p>AI can draft the message. Deciding who needs it, when to send it, and what should change is your call — and that’s what the course helps teams practice.</p>
    </section>

    <div class="ai-end"><b>What people do depends not only on them, but also on the environment around them. That environment is something you can shape in advance.</b>
    <ul><li>Do they want to?</li><li>Is it easy to do?</li><li>Is there a reminder at the moment it matters?</li></ul></div>

    <div class="cta">
    <a class="btn primary" href="/en/contact/">Tell us one thing, and we’ll write back</a>
    <a class="btn secondary" href="/en/how/">See how we look at a problem</a>
    </div>
    <p><a class="more" href="/en/calc/">Small gains at every step can compound. Do the math →</a></p>
    <p class="note">All programs are taught in Mandarin.</p>
      <div class="nav"><a href="/en/how/" class="prev">← How we think</a><a href="/en/">Home</a></div>'''
ai_title = 'AI can produce the work. People still have to act on it.'
ai_desc = 'Where AI fits at Propel AI: AI is the GPS, not the gas pedal. AI can produce the copy, the deck and the report; getting customers to reply and teams to follow through depends on what they face at the moment they decide.'
AI_ALT = ('<link rel="alternate" hreflang="zh-Hant" href="{s}/ai/"><link rel="alternate" hreflang="en" href="{s}/en/ai/">'
          '<link rel="alternate" hreflang="x-default" href="{s}/ai/">').format(s=SITE)
h = HEAD
h = re.sub(r'<title>.*?</title>', f'<title>{esc(ai_title)}｜Propel AI</title>', h)
h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(ai_desc), h)
h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(ai_title) + '｜Propel AI', h)
h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(ai_desc), h)
h = h.replace(f'{SITE}/en/about/', f'{SITE}/en/ai/')
h = re.sub(r'<body class="[^"]*">', '<body class="pg-ai pg-en-ai">', h)
h = h.replace('</head>', AI_ALT + '\n</head>', 1)
wr('en/ai/index.html', h + '\n    ' + ai_body + '\n' + REST)
# 中文 /ai/：語言切換指到英文 AI 頁，補 hreflang
za = rd('ai/index.html')
za = za.replace('<a class="lang" href="/en/" hreflang="en" lang="en">EN</a>', '<a class="lang" href="/en/ai/" hreflang="en" lang="en">EN</a>')
if 'hreflang="en" href="' + SITE + '/en/ai/"' not in za: za = za.replace('</head>', AI_ALT + '\n</head>', 1)
wr('ai/index.html', za)

# ---------- 五個英文頁的頁首換成四步 ----------
n = 0
for url in ZH:
    p = url.strip('/') + '/index.html'
    s = rd(p)
    s2 = re.sub(r'<header class="sitehead">.*?</header>', lambda m: header(url), s, count=1, flags=re.S)
    assert s2 != s or 'wf-nav' in s, p
    wr(p, s2); n += 1

# 英文首頁第 02 段加算算看入口（冪等）
home = re.sub(r'<!-- encalc:home -->.*?<!-- /encalc:home -->', '', rd('en/index.html'), flags=re.S)
m = re.search(r'<a class="more" href="/en/how/">Three examples from research[^<]*</a>', home)
if m:
    home = home[:m.end()] + '<!-- encalc:home --><br><a class="more" href="/en/calc/">Small gains at every step can compound. Do the math →</a><br><a class="more" href="/en/ai/">Why “AI” is in our name →</a><!-- /encalc:home -->' + home[m.end():]
    wr('en/index.html', home)

# 中文 /calc/：語言切換指到英文算算看，補 hreflang
zc = rd('calc/index.html')
zc = zc.replace('<a class="lang" href="/en/" hreflang="en" lang="en">EN</a>', '<a class="lang" href="/en/calc/" hreflang="en" lang="en">EN</a>')
if 'hreflang="en" href="' + SITE + '/en/calc/"' not in zc: zc = zc.replace('</head>', ALT + '\n</head>', 1)
wr('calc/index.html', zc)
sm = rd('sitemap.xml')
for u in ('/en/calc/', '/en/ai/'):
    if f'{SITE}{u}' not in sm: sm = sm.replace('</urlset>', f'  <url><loc>{SITE}{u}</loc></url>\n</urlset>')
wr('sitemap.xml', sm)
print(f'en_patch: 英文站 {n} 頁頁首換成四步；/en/calc/、/en/ai/ 已產生；中文 /calc/ 與 /ai/ 的 EN 指到對應英文頁')
