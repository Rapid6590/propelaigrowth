# calc_page.py（1119 15:24 George：官網是開放給不特定人，示範改法只標研究主題，不列作者年份；完整出處列在公司簡介與課堂講義，不寫來信索取） v0.2 (2026-11-18；v0.2 修表頭與欄位沒對齊：欄寬改用 px) — /calc/「算算看：每一關多一點，最後差多少？」（決策點的複利，三條示範鏈）
# v0.3 (2026-11-24)：表頭「原本通過」「多幾 %」兩格改成跟下面那一列同樣的排法（.cc-hf），字正對輸入格；之前靠右會偏到 % 上面（George 1124 22:45）。
# 用法：python3 tools/calc_page.py <站台根目錄>   可重跑。順序：… → articles → calc_page → wayfinding。
# 規矩（George 1117–1118）：
#   - 五關都在同一次交易／同一件申辦裡；回購、下次再來是下一條鏈，另算。
#   - 數字全是示意；免責句全站統一用 DISCLAIMER 這一句，別處要用照抄。
#   - 一次只動一兩關；每關都推過是幾輪下來的事（對齊工作坊手冊 R→O→P→E→L）。
#   - 不收任何資料：全部在瀏覽器裡算。
import sys, re, json, html, pathlib
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
SITE = 'https://propelaigrowth.com'
def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')
def esc(s): return html.escape(s, quote=True)

DISCLAIMER = '數字為示意，不是承諾；每一關實際多少，只能在你自己的流程裡量。'

# 每關：(關名, 原本 %, 推高 %, 示範改法, 這一輪先動?)
CHAINS = [
    {'id': 'b2c', 'tab': '賣給消費者', 'start': 10000, 'unit': '人', 'startLabel': '看到廣告的人', 'endLabel': '付款完成',
     'gates': [
        ('看到廣告 → 點進來', 3, 20, '「現省 300」改成「再兩天就少 300」', True),
        ('進站 → 看到商品頁', 60, 15, '第一屏跟廣告說同一句話，只放一個主推入口', False),
        ('商品頁 → 加入購物車', 30, 20, '放真實的購買數字，主推規格先選好', False),
        ('購物車 → 開始結帳', 40, 20, '運費在第一頁就講，欄位從十個減到四個', True),
        ('結帳 → 付款完成', 85, 5, '加一行保證，沒付完的一小時內提醒一次', False)],
     'src': '損失框架、選項數、描述性規範與預設、摩擦與揭露時點、提醒時點。完整出處列在公司簡介與課堂講義。'},
    {'id': 'b2b', 'tab': '賣給企業客戶', 'start': 100, 'unit': '家', 'startLabel': '名單上的客戶', 'endLabel': '續約',
     'gates': [
        ('約到做決定的人', 20, 15, '請求小而具體，加一句「不方便也沒關係」', True),
        ('同意下一步', 50, 20, '會議結束前寫下日期、誰做什麼', False),
        ('報價後選定方案', 40, 25, '方案給三個不給八個，標出多數客戶選的那個', True),
        ('內部簽核通過', 60, 15, '替他準備給老闆的一頁，第一行寫不做的代價', False),
        ('到期續約', 70, 10, '到期前 90 天提醒，附一頁這一年的成果', False)],
     'src': '小而具體的請求、執行意圖、選項數與錨定、損失框架、預設與提醒時點。完整出處列在公司簡介與課堂講義。'},
    {'id': 'gov', 'tab': '讓民眾辦得成', 'start': 10000, 'unit': '位', 'startLabel': '符合資格的民眾', 'endLabel': '辦成',
     'gates': [
        ('收到通知 → 決定要辦', 40, 15, '通知第一行寫要做什麼、哪一天前；屬實的話，加一句「多數人已經辦了」', False),
        ('決定要辦 → 找到申請入口', 50, 20, '連結直接到申請表，不先到機關首頁', True),
        ('找到入口 → 開始填', 60, 20, '機關查得到的資料，經同意後先帶入；12 欄減到 3 欄', True),
        ('開始填 → 送出', 70, 10, '表單最後留一格：「你打算哪一天送件？」', False),
        ('送出 → 辦成（含補件）', 80, 10, '補件通知寫明缺哪一件、哪一天前、從哪裡補', False)],
     'src': '通知信措辭與社會規範、少一步、預先帶入資料、寫下哪一天、具體指示。完整出處列在公司簡介與課堂講義。'},
]

CSS = '''
/* calc:css */
.cc-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 16px}
.cc-tabs button{font:inherit;font-size:14.5px;padding:8px 14px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--mute);cursor:pointer}
.cc-tabs button[aria-selected="true"]{border-color:var(--orange);background:var(--tint);color:var(--navy-text);font-weight:700}
.cc-start{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:15px;margin:0 0 12px}
.cc input[type=number],.cc input[type=text]{font:inherit;font-size:15px;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px 8px;min-width:0}
.cc input[type=number]{width:5.2em;text-align:right;font-variant-numeric:tabular-nums}
.cc input:focus,.cc-tabs button:focus-visible,.cc-add:focus-visible,.cc-del:focus-visible{outline:3px solid var(--orange);outline-offset:1px}
.cc-start input[type=number]{width:7.5em}
.cc-head,.cc-row{display:grid;grid-template-columns:minmax(0,1fr) 92px 104px 70px 44px 26px;gap:8px;align-items:center}
.cc-head{font-size:12px;color:var(--mute);letter-spacing:.04em;padding:0 13px 6px}
.cc-head>span:nth-child(n+2){text-align:right}.cc-head>span:nth-child(5){text-align:center}
/* 表頭這兩格照下面那一列的排法做（看不見的 +、% 佔同樣的位置），字就會正對著輸入格，換字型、換語言都不會跑掉 */
.cc-head .cc-hf{display:flex;align-items:center;gap:3px}
.cc-hf b{flex:1;min-width:0;text-align:center;font-weight:400;white-space:nowrap}
.cc-hf i{visibility:hidden;font-style:normal;font-size:14px;letter-spacing:0;line-height:1}
.cc-row{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin:0 0 8px}
.cc-row.on{border-color:var(--orange)}
.cc-name{display:flex;gap:8px;align-items:center;min-width:0}
.cc-name i{flex:0 0 22px;height:22px;border-radius:50%;background:var(--line);color:var(--fg);font-style:normal;font-weight:700;font-size:12px;display:inline-flex;align-items:center;justify-content:center}
.cc-row.on .cc-name i{background:var(--orange);color:#fff}
.cc-name input{flex:1;font-weight:700;border-color:transparent;background:transparent;padding-left:2px}
.cc-name input:hover{border-color:var(--line)}
.cc-f{display:flex;align-items:center;justify-content:flex-end;gap:3px;font-size:14px;color:var(--mute)}
.cc-f label{display:none}
.cc-f input{width:3.9em}
.cc-after{text-align:right;font-weight:700;font-variant-numeric:tabular-nums;color:var(--navy-text)}
.cc-pick{display:flex;justify-content:center}.cc-pick input{width:18px;height:18px;accent-color:var(--orange)}
.cc-del{font:inherit;border:0;background:transparent;color:var(--mute);cursor:pointer;font-size:18px;line-height:1;padding:2px}
.cc-how{grid-column:1/-1;font-size:13px;color:var(--mute);padding-left:30px;line-height:1.55}
.cc-how b{color:var(--accent-ink);font-weight:700}
.cc-cum{grid-column:1/-1;font-size:12.5px;color:var(--mute);padding-left:30px;font-variant-numeric:tabular-nums}
.cc-add{font:inherit;font-size:14px;border:1px dashed var(--line);background:transparent;color:var(--mute);border-radius:10px;padding:8px 14px;cursor:pointer;margin:2px 0 18px}
.cc-out{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin:0 0 10px}
.cc-out h2{margin:0 0 12px;font-size:17px}
.cc-bar{display:grid;grid-template-columns:8.6em minmax(0,1fr);gap:10px;align-items:center;margin:0 0 10px;font-size:14px}
.cc-bar .t b{display:block;color:var(--fg)}.cc-bar .t small{display:block;color:var(--mute);font-size:12px}
.cc-bar .b{display:flex;align-items:center;gap:8px;min-width:0}
.cc-bar .b i{display:block;height:26px;border-radius:6px;background:var(--line);min-width:3px;transition:width .25s}
.cc-bar.r1 .b i{background:#F3B48A}.cc-bar.r2 .b i{background:var(--orange)}
.cc-bar .b span{white-space:nowrap;font-weight:700;font-variant-numeric:tabular-nums;color:var(--navy-text)}
.cc-bar .b span em{font-style:normal;color:var(--accent-ink);margin-left:6px}
.cc-say{font-size:15px;margin:12px 0 0;padding-top:12px;border-top:1px dashed var(--line)}
.cc-say b{color:var(--accent-ink)}
.cc-bridge{background:var(--tint);border-radius:12px;padding:14px 16px;margin:22px 0 0}
.cc-bridge h2{margin:0 0 6px;font-size:18px}.cc-bridge p{margin:0 0 6px;font-size:15px}
.cc details{font-size:13px;color:var(--mute);margin:10px 0 0}.cc summary{cursor:pointer}
@media (max-width:640px){
  .cc-head{display:none}
  .cc-row{grid-template-columns:1fr 1fr 1fr;gap:8px 10px}
  .cc-name{grid-column:1/-1}
  .cc-f{flex-direction:column;align-items:flex-start;gap:2px}.cc-f label{display:block;font-size:11.5px}
  .cc-f .u{display:none}.cc-f input{width:100%}
  .cc-after{text-align:left}.cc-after::before{content:"之後";display:block;font-size:11.5px;font-weight:400;color:var(--mute)}
  .cc-pick{grid-column:1/3;justify-content:flex-start;font-size:13px;color:var(--mute)}.cc-pick label{display:flex;gap:6px;align-items:center}
  .cc-pick span{display:inline!important}
  .cc-del{justify-self:end}
  .cc-how,.cc-cum{padding-left:0}
  .cc-bar{grid-template-columns:1fr;gap:4px}
}
/* /calc:css */
'''
css = re.sub(r'\n/\* calc:css \*/.*?/\* /calc:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

JS = r'''
(function(){
  var CHAINS = __CHAINS__;
  var $ = function(id){ return document.getElementById(id); };
  var state = null, MAXG = 7, MING = 2;
  function clone(c){ return {id:c.id, start:c.start, unit:c.unit, startLabel:c.startLabel, endLabel:c.endLabel, src:c.src,
    gates:c.gates.map(function(g){ return {name:g[0], base:g[1], lift:g[2], how:g[3], pick:g[4]}; })}; }
  function num(v, lo, hi){ v = parseFloat(v); if (!isFinite(v)) v = 0; return Math.min(hi, Math.max(lo, v)); }
  function fmt(x){
    if (x >= 100) return Math.round(x).toLocaleString('en-US');
    if (x >= 10) return (Math.round(x * 10) / 10).toFixed(1);
    return (Math.round(x * 100) / 100).toFixed(x >= 1 ? 1 : 2);
  }
  function pct(x){ var r = Math.round(x * 10) / 10; return (r % 1 === 0 ? r.toFixed(0) : r.toFixed(1)) + '%'; }
  function after(g){ return Math.min(100, g.base * (1 + g.lift / 100)); }

  function load(i){
    state = clone(CHAINS[i]);
    var tabs = document.querySelectorAll('.cc-tabs button');
    for (var k = 0; k < tabs.length; k++) tabs[k].setAttribute('aria-selected', k === i ? 'true' : 'false');
    $('cc-start').value = state.start; $('cc-startlabel').textContent = state.unit + '（' + state.startLabel + '）';
    $('cc-src').textContent = state.src;
    rows(); calc();
  }
  function rows(){
    var box = $('cc-rows'); box.innerHTML = '';
    state.gates.forEach(function(g, i){
      var d = document.createElement('div'); d.className = 'cc-row' + (g.pick ? ' on' : '');
      d.innerHTML =
        '<div class="cc-name"><i>' + (i + 1) + '</i><input type="text" aria-label="第 ' + (i + 1) + ' 關的名字" maxlength="24"></div>' +
        '<div class="cc-f"><label>原本通過</label><input type="number" inputmode="decimal" min="0" max="100" step="1" aria-label="第 ' + (i + 1) + ' 關原本通過幾 %"><span class="u">%</span></div>' +
        '<div class="cc-f"><label>多幾 %</label><span class="u">+</span><input type="number" inputmode="decimal" min="0" max="200" step="5" aria-label="第 ' + (i + 1) + ' 關多幾 %"><span class="u">%</span></div>' +
        '<div class="cc-after"></div>' +
        '<div class="cc-pick"><label><input type="checkbox" aria-label="這一輪先動第 ' + (i + 1) + ' 關"><span hidden>這一輪先動</span></label></div>' +
        '<button class="cc-del" type="button" aria-label="拿掉第 ' + (i + 1) + ' 關" title="拿掉這一關">×</button>' +
        (g.how ? '<div class="cc-how"><b>示範改法</b>　' + g.how.replace(/</g, '&lt;') + '</div>' : '') +
        '<div class="cc-cum"></div>';
      var ins = d.querySelectorAll('input');
      ins[0].value = g.name; ins[1].value = g.base; ins[2].value = g.lift; ins[3].checked = !!g.pick;
      ins[0].addEventListener('input', function(){ g.name = this.value; if (g.how){ g.how = ''; var h = d.querySelector('.cc-how'); if (h) h.remove(); } });
      ins[1].addEventListener('input', function(){ g.base = num(this.value, 0, 100); calc(); });
      ins[2].addEventListener('input', function(){ g.lift = num(this.value, 0, 200); calc(); });
      ins[3].addEventListener('change', function(){ g.pick = this.checked; d.classList.toggle('on', g.pick); calc(); });
      d.querySelector('.cc-del').addEventListener('click', function(){ if (state.gates.length > MING){ state.gates.splice(i, 1); rows(); calc(); } });
      box.appendChild(d);
    });
    $('cc-add').hidden = state.gates.length >= MAXG;
    var dels = box.querySelectorAll('.cc-del');
    for (var k = 0; k < dels.length; k++) dels[k].style.visibility = state.gates.length > MING ? 'visible' : 'hidden';
  }
  function calc(){
    var s = num($('cc-start').value, 0, 1e9), a = s, b = s, c = s, picked = 0, maxLift = 0, capped = false;
    var els = $('cc-rows').children;
    state.gates.forEach(function(g, i){
      var af = after(g);
      if (g.base * (1 + g.lift / 100) > 100) capped = true;
      a *= g.base / 100; c *= af / 100; b *= (g.pick ? af : g.base) / 100;
      if (g.pick) picked++;
      if (g.lift > maxLift) maxLift = g.lift;
      els[i].querySelector('.cc-after').textContent = pct(af);
      els[i].querySelector('.cc-cum').textContent = '走到這一關還剩：原本 ' + fmt(a) + ' ' + state.unit + '，每關都動過之後 ' + fmt(c) + ' ' + state.unit;
    });
    var n = state.gates.length, top = Math.max(a, b, c, 1e-9);
    function bar(id, v){ $(id).style.width = Math.max(1, v / top * 100) + '%'; }
    bar('cc-b0', a); bar('cc-b1', b); bar('cc-b2', c);
    $('cc-v0').textContent = fmt(a) + ' ' + state.unit;
    $('cc-v1').innerHTML = fmt(b) + ' ' + state.unit + (a > 0 && picked ? '<em>' + (b / a).toFixed(1) + ' 倍</em>' : '');
    $('cc-v2').innerHTML = fmt(c) + ' ' + state.unit + (a > 0 ? '<em>' + (c / a).toFixed(1) + ' 倍</em>' : '');
    $('cc-t1').textContent = picked ? '只動打勾的 ' + picked + ' 關' : '還沒勾要先動哪一關';
    $('cc-t2').textContent = n + ' 關都動過';
    var say = '';
    if (a > 0 && maxLift > 0){
      say = (maxLift <= 30 ? '最多的一關也只多了 <b>' : '最多的一關多了 <b>') + maxLift + '%</b>；' + n + ' 關乘起來，是原本的 <b>' + (c / a).toFixed(1) + ' 倍</b>。';
      if (picked && picked < n) say += '這一輪只動 ' + picked + ' 關，就已經是 <b>' + (b / a).toFixed(1) + ' 倍</b>。';
    } else { say = '把每一關的數字填上去，下面就會算。'; }
    if (capped) say += '有一關已經推到 100%：通過率最多就是全部的人，再往上沒有了。';
    $('cc-say').innerHTML = say;
  }
  var tabs = document.querySelectorAll('.cc-tabs button');
  for (var k = 0; k < tabs.length; k++) (function(i){ tabs[i].addEventListener('click', function(){ load(i); }); })(k);
  $('cc-start').addEventListener('input', calc);
  $('cc-add').addEventListener('click', function(){ if (state.gates.length < MAXG){ state.gates.push({name:'再一關', base:50, lift:10, how:'', pick:false}); rows(); calc(); } });
  load(0);
})();
'''

tabs = ''.join(f'<button type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}">{esc(c["tab"])}</button>' for i, c in enumerate(CHAINS))
body = f'''<span class="pill">算算看</span>
    <h1>每一關多一點，最後差多少？</h1>
    <p class="lead">一件事要成，客人、員工或民眾得連過好幾關。十關各多 10%，乘起來是 2.6 倍；各少 10%，只剩 0.35。下面三條是示範，數字都可以改成你自己的。</p>
    <div class="cc">
      <div class="cc-tabs" role="tablist" aria-label="選一條示範流程">{tabs}</div>
      <div class="cc-start"><label for="cc-start">從</label><input id="cc-start" type="number" inputmode="numeric" min="0" step="1" value="10000"><span id="cc-startlabel"></span><span class="note">開始</span></div>
      <div class="cc-head" aria-hidden="true"><span>每一關</span><span class="cc-hf"><b>原本通過</b><i>%</i></span><span class="cc-hf"><i>+</i><b>多幾 %</b><i>%</i></span><span>之後</span><span>先動</span><span></span></div>
      <div id="cc-rows"></div>
      <button class="cc-add" id="cc-add" type="button">＋ 再加一關</button>
      <div class="cc-out" aria-live="polite">
        <h2>走完全部的關，還剩多少</h2>
        <div class="cc-bar r0"><div class="t"><b>原本</b><small>什麼都沒動</small></div><div class="b"><i id="cc-b0"></i><span id="cc-v0"></span></div></div>
        <div class="cc-bar r1"><div class="t"><b>這一輪</b><small id="cc-t1"></small></div><div class="b"><i id="cc-b1"></i><span id="cc-v1"></span></div></div>
        <div class="cc-bar r2"><div class="t"><b>幾輪之後</b><small id="cc-t2"></small></div><div class="b"><i id="cc-b2"></i><span id="cc-v2"></span></div></div>
        <p class="cc-say" id="cc-say"></p>
      </div>
      <p class="disc">{esc(DISCLAIMER)}這一頁的數字只在你的瀏覽器裡算，不會送出。</p>
      <details><summary>示範改法背後的研究主題</summary><p id="cc-src" style="margin:6px 0 0"></p></details>
      <div class="cc-bridge">
        <h2>「我的流程不是這幾關」</h2>
        <p>對，上面是示範，不是範本。全天工作坊的第二站，就是把你自己那件事拆成四到七步，圈出最卡的一兩步。</p>
        <p>一次只動圈出來的那一兩步，兩週看一個數字；每一關都動過，是幾輪下來的事。</p>
      </div>
      <div class="cta-row" style="margin-top:18px">
        <a class="btn primary" href="/workshop/">看全天工作坊怎麼拆 →</a>
        <a class="btn secondary" href="/quiz/">還不確定？先做兩分鐘小測驗</a>
      </div>
    </div>
<script>{JS.replace('__CHAINS__', json.dumps(CHAINS, ensure_ascii=False, separators=(',', ':')))}</script>'''

tpl = rd('about/index.html')
tpl = re.sub(r'<!-- aeo:ld -->.*?<!-- /aeo:ld -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<!-- wf:top -->.*?<!-- /wf:top -->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', tpl)
HEAD, REST = tpl[:tpl.index('<main>') + 6], tpl[tpl.index('</main>'):]
title = '算算看：每一關多一點，最後差多少？'
desc = '一件事要成，得連過好幾關。把每一關的通過率填進去，看每關多一點，乘起來差多少。三條示範：賣給消費者、賣給企業客戶、讓民眾辦得成。不用留資料。'
h = HEAD
h = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}｜Propel AI 啟進智能決策</title>', h)
h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title) + '｜Propel AI', h)
h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
h = h.replace(f'{SITE}/about/', SITE + '/calc/').replace('class="pg-about"', 'class="pg-calc"')
wr('calc/index.html', h + '\n    ' + body + '\n' + REST)

# 首頁第 02 段加一個入口（冪等）
home = rd('index.html')
HOOK = '<a class="more" href="/how/">四個例子：換預設、給選項、先開口、跟進信 →</a>'
if HOOK in home and 'calc:home' not in home:
    wr('index.html', home.replace(HOOK, '<div class="links">' + HOOK + '<!-- calc:home --><a class="more" href="/calc/">每一關多一點，最後差多少？算算看 →</a><!-- /calc:home --></div>', 1))
sm = rd('sitemap.xml')
if f'{SITE}/calc/' not in sm:
    wr('sitemap.xml', sm.replace('</urlset>', f'  <url><loc>{SITE}/calc/</loc></url>\n</urlset>'))
print('calc_page: /calc/ 已產生（三條示範鏈）；sitemap 已補')
