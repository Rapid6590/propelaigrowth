# ai_page.py v0.2 (2026-11-19；v0.2 George 看過 v0.1 說「為什麼是現在：產出跟行為之間有一段距離」看不懂、跟主題接不上——
#   改成客戶會問的話「AI 都在用了，為什麼公司還沒感覺？」：一個例子 → 一個現象 → 一個原因 → 所以我們做什麼；台灣那一格拿掉；
#   「哪一步變貴了」三張卡不上頁（SHOW_WHY=False，要放回來改 True）。訊息要少、單刀直入。) — /ai/「AI 做得出東西；東西不會自己變成行為」（我們跟 AI 的關係；掛在第二步「看懂為什麼」底下）
# 用法：python3 tools/ai_page.py <站台根目錄>   可重跑。順序：… → calc_page → picker_order_patch → big_decisions_page → ai_page → wayfinding。
# 規矩（George 0921、1117–1119）：
#   - 講的是「產出跟行為之間的落差」，不講 AI 的能力。不寫「AI 做不出行為」（2026 已有反證）。
#   - 不寫導入失敗率（「○○% 專案失敗」「沒成功」）；MIT NANDA 的 95% 不用。
#   - 67% 對 32% 是 Microsoft 模型裡的相對重要性，不是因果；頁上要寫明。
#   - （v0.2 起頁上不放台灣 AIF 那一格；別處要用時）AIF 那兩個數字的分母都是「受訪企業」（228 家），不是員工人數：
#       61.8% 的企業＝員工自己用現成的生成式 AI 工具，公司沒禁止也沒提供；6.6% 的企業＝AI 完全整合進常規流程。
#   - 日本例用四年實證的結果（2017–2020 年度、五家、約 30 萬戶、平均約 2%），不用第一年的期中速報。
#   - 賓士例只寫機制（70 個參數、前 20 分鐘、咖啡杯與提示音），不引事故下降率。
#   - 數字都對過原始報告或原機構新聞稿（2026-11-19 重對）；要加新數字，先對原文再放。
#   - 客戶面用語：不寫「把人當設計對象」的句子；講師＝「帶著一起判斷」；提示詞印在講義上，不說提示卡。
#   - 選單與 /map/ 的項目在 wayfinding_patch.py 的 STEPS。
import sys, re, html, pathlib
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
SITE = 'https://propelaigrowth.com'
URL = '/ai/'
def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')
def esc(s): return html.escape(s, quote=True)

TITLE = 'AI 做得出東西；東西不會自己變成行為'
DESC = 'Propel AI 跟 AI 的關係：AI 是導航，不是油門。文案、簡報、報表 AI 都做得出來；客戶點頭、同仁照新流程做，要回頭看他做決定當下的環境。'

# (小標, 標題, [(%, 這個數字是誰、說了什麼, 用橘色?)], 這一組在比什麼)
SHOW_WHY = False   # 「有了 AI 之後，哪一步變貴了」三張卡；George 1119 要訊息簡單，先不上頁
# (小標, 標題, [(%, 這個數字是誰、說了什麼, 用橘色?)], 這一組在比什麼, 放大?)
STATS = [
    ('不只你這樣', '個人變快了，公司的數字沒跟上', [
        (80, '的受訪者說，AI 提升了自己的生產力', False),
        (37, '說，AI 對公司的獲利有正面貢獻', True)], '', False),
    ('原因', '差別在公司的環境，不在個人願不願意', [
        (67, '公司的環境：文化、主管支持、人才制度', True),
        (32, '個人的心態與做法', False)], '兩者對「AI 帶來多少幫助」的相對重要性', True),
]
SRC1 = ('外部調查，非 Propel AI 客戶實績｜出處：McKinsey《The state of AI in 2026》（1,719 人、97 國）｜'
        'Microsoft《2026 Work Trend Index》（20,000 位在工作上用 AI 的人、10 個市場；67% 與 32% 是模型裡的相對重要性，不是因果）')

CSS = '''
/* ai:css */
.pg-ai h1 .nb,.pg-ai h2 .nb,.pg-ai h3 .nb{display:inline-block}
.pg-ai main p{text-wrap:pretty}
.ai-fig{margin:6px 0 4px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 12px 6px}
.ai-fig svg{display:block;width:100%;height:auto}
.ai-fig .pane{fill:var(--sky)} .ai-fig .ink{fill:var(--navy)} .ai-fig .line{stroke:var(--navy);fill:none;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}
.ai-fig .route{stroke:var(--orange);fill:none;stroke-width:5;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1 11}
.ai-fig .dot{fill:var(--orange)} .ai-fig .soft{fill:var(--peach)} .ai-fig .paper{fill:var(--card);stroke:var(--line);stroke-width:2}
.ai-fig .lab{fill:var(--navy-text);font-size:19px;font-weight:700} .ai-fig .lab.o{fill:var(--accent-ink)} .ai-fig .lab.m{fill:var(--mute);font-size:15px;font-weight:500} .ai-fig .lab.sm{font-size:16px}
.ai-fig .mute{fill:var(--line)} .ai-fig .mline{stroke:var(--line);fill:none;stroke-width:2}
.ai-cap{color:var(--fg);font-size:17px;font-weight:700;margin:10px 2px 0;line-height:1.5}
.ai-cap small{display:block;color:var(--mute);font-size:14.5px;font-weight:400;margin-top:2px}
.ai-stats{display:grid;gap:12px;margin:14px 0 8px}
.ai-stat{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px 12px}
.ai-stat h3{margin:0 0 10px;font-size:16.5px;color:var(--navy-text);display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline}
.ai-stat h3 small{font-size:12px;font-weight:700;color:#fff;background:var(--navy);border-radius:999px;padding:1px 10px}
.ai-stat.ai-key{border:2px solid var(--orange)} .ai-stat.ai-key h3 small{background:var(--orange)}
.ai-eg{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:center;margin:12px 0 4px}
.ai-eg svg{display:block;width:100%;height:auto}
.ai-eg>i{font-style:normal;color:var(--orange);font-weight:900;font-size:20px}
.ai-eg>i::before{content:"→"}
.ai-eg .pane{fill:var(--sky)} .ai-eg .paper{fill:var(--card);stroke:var(--line);stroke-width:2}
.ai-eg .t1{font-size:19px;font-weight:700;fill:var(--navy-text)} .ai-eg .t2{font-size:14.5px;fill:var(--mute)} .ai-eg .t3{font-size:14px;fill:#fff} .ai-eg .t4{font-size:14.5px;font-weight:700;fill:var(--accent-ink)}
.ai-eg .k{font-size:16px;font-weight:700;fill:var(--navy-text)} .ai-eg .k.o{fill:var(--accent-ink)}
.ai-say{font-size:18px;line-height:1.6;font-weight:700;color:var(--navy-text);margin:12px 2px 2px}
.ai-say small{display:block;font-size:15.5px;font-weight:400;color:var(--fg);margin-top:2px}
.ai-so{margin:14px 0 10px;background:var(--navy);color:#fff;border-radius:14px;padding:16px 18px 15px}
.ai-so small{display:inline-block;font-size:12px;font-weight:700;background:var(--orange);border-radius:999px;padding:1px 10px;margin-bottom:6px}
.ai-so b{display:block;font-size:19px;line-height:1.55}
.ai-so b span,.ai-say span{display:inline-block}
.ai-so>span{display:block;font-size:15px;line-height:1.6;margin-top:6px;opacity:.92}
.ai-stat .cmp{color:var(--mute);font-size:13px;margin:-4px 0 8px}
.ai-row{display:grid;grid-template-columns:86px 1fr;gap:4px 12px;align-items:center;margin:0 0 9px}
.ai-row b{font-size:27px;font-weight:900;line-height:1;color:var(--navy-text);font-variant-numeric:tabular-nums;text-align:right}
.ai-row.o b{color:var(--accent-ink)}
.ai-row span{font-size:14.5px;line-height:1.45}
.ai-bar{grid-column:2;height:10px;border-radius:999px;background:var(--sky);overflow:hidden}
.ai-bar i{display:block;height:100%;border-radius:999px;background:var(--navy)}
.ai-row.o .ai-bar i{background:var(--orange)}
.ai-why{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0 6px}
.ai-why>div{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 14px 12px}
.ai-why svg{display:block;width:100%;max-width:150px;height:auto;margin:0 0 8px}
.ai-why h3{font-size:16px;line-height:1.45;color:var(--navy-text);margin:0 0 6px}
.ai-why p{font-size:14.5px;line-height:1.6;margin:0;color:var(--fg)}
.ai-ex{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0 6px}
.ai-ex>div{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px 12px;display:flex;flex-direction:column;gap:8px}
.ai-ex .tag2{align-self:flex-start;font-size:12px;font-weight:700;color:var(--accent-ink);border:1px solid var(--accent-ink);border-radius:999px;padding:0 9px}
.ai-ex h3{font-size:16.5px;line-height:1.45;color:var(--navy-text);margin:0}
.ai-ex p{font-size:14.5px;line-height:1.6;margin:0}
.ai-ex .src{color:var(--mute);font-size:12.5px;margin-top:auto;padding-top:6px;border-top:1px dashed var(--line)}
.ai-flow{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;list-style:none;padding:0;margin:14px 0 4px}
.ai-flow li{position:relative;background:var(--sky);border-radius:12px;padding:10px 10px 10px;font-size:14.5px;line-height:1.4;color:var(--navy-text);font-weight:700;text-align:center}
.ai-flow li small{display:block;font-size:12px;font-weight:700;color:var(--mute);margin-bottom:2px}
.ai-flow li.on{background:var(--peach);outline:2px solid var(--orange)}
.ai-flow li+li::before{content:"▶";position:absolute;left:-9px;top:50%;transform:translateY(-50%);font-size:10px;color:var(--orange)}
.ai-do{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:12px 0 10px}
.ai-do>div{border:1px solid var(--line);border-radius:14px;padding:12px 14px;background:var(--card)}
.ai-do h3{margin:0 0 4px;font-size:15.5px;color:var(--navy-text)} .ai-do p{margin:0;font-size:14.5px;line-height:1.6}
.ai-end{margin:26px 0 0;border-left:5px solid var(--orange);background:var(--sky);border-radius:0 14px 14px 0;padding:16px 18px 14px}
.ai-end b{display:block;font-size:19px;line-height:1.55;color:var(--navy-text)}
.ai-end ul{list-style:none;display:flex;flex-wrap:wrap;gap:6px 8px;padding:0;margin:12px 0 0}
.ai-end li{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:4px 13px;font-size:14.5px}
.ai-strip{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;margin:12px 0 0;padding:13px 18px;border:1px solid var(--line);border-left:4px solid var(--navy);border-radius:10px;background:var(--card);text-decoration:none;color:var(--navy-text)}
.ai-strip:hover{border-color:var(--orange);border-left-color:var(--orange)}
.ai-strip small{font-size:12.5px;font-weight:700;color:var(--mute)} .ai-strip b{font-size:16.5px} .ai-strip span{margin-left:auto;color:var(--orange);font-weight:700;font-size:13px}
@media (max-width:700px){.ai-eg{grid-template-columns:1fr;justify-items:center}.ai-eg>i::before{content:"↓"}.ai-why,.ai-ex,.ai-do{grid-template-columns:1fr}.ai-why>div{display:grid;grid-template-columns:92px 1fr;gap:4px 12px;align-items:start}.ai-why svg{grid-row:1/3;margin:0}.ai-why h3{margin:0}
.ai-flow{grid-template-columns:1fr 1fr}.ai-flow li:nth-child(3)::before{display:none}.ai-fig .lab{font-size:26px}.ai-fig .lab.m{font-size:21px}.ai-fig .lab.sm{font-size:21px}.ai-fig .lab.hide-m{display:none}.ai-row{grid-template-columns:74px 1fr}.ai-row b{font-size:23px}}
/* /ai:css */
'''
css = re.sub(r'\n/\* ai:css \*/.*?/\* /ai:css \*/\n', '', rd('assets/site.css'), flags=re.S)
wr('assets/site.css', css + CSS)

# 主圖：左＝導航（AI 算路），右＝油門（人踩）
HERO = '''<svg viewBox="0 0 720 250" role="img" aria-label="左邊是導航螢幕，上面畫出一條路線；右邊是一隻腳踩在油門上。導航算得出路，車要動還是要有人踩油門。">
<rect class="pane" x="0" y="0" width="340" height="250" rx="12"/><rect class="pane" x="380" y="0" width="340" height="250" rx="12"/>
<rect class="paper" x="70" y="34" width="200" height="140" rx="14"/>
<path class="mline" d="M92 70 H150 M92 100 H128 M196 148 H250 M210 60 H252"/>
<path class="route" d="M104 150 C 120 112, 150 128, 170 104 S 214 96, 236 62"/>
<circle class="ink" cx="104" cy="150" r="8"/><path class="dot" d="M236 40 c -11 0 -18 8 -18 18 c 0 12 18 30 18 30 s 18 -18 18 -30 c 0 -10 -7 -18 -18 -18 z"/><circle cx="236" cy="58" r="6" fill="#fff"/>
<rect class="ink" x="150" y="174" width="40" height="12" rx="3"/>
<text class="lab" x="170" y="218" text-anchor="middle">AI：把路算出來</text>
<text class="lab m hide-m" x="170" y="240" text-anchor="middle">文案、簡報、報表、程式碼</text>
<path class="line" d="M352 110 h16 m-7 -7 l7 7 l-7 7" style="stroke:var(--orange)"/>
<g transform="translate(456,20)">
<rect class="mute" x="0" y="156" width="200" height="8" rx="4"/>
<path d="M150 158 L116 122" stroke="var(--navy)" stroke-width="7" stroke-linecap="round"/>
<path d="M88 136 L143 107" stroke="var(--navy)" stroke-width="12" stroke-linecap="round"/>
<g transform="translate(40,152) rotate(-28)">
<path class="dot" d="M6 0 H104 Q113 0 110 -10 Q104 -27 78 -31 L54 -37 V-80 H10 V-20 Q10 -8 6 0 Z"/>
<rect class="soft" x="10" y="-96" width="44" height="18" rx="3"/>
</g>
<path d="M160 92 l14 -8 M166 108 l16 -3 M150 78 l9 -12" stroke="var(--orange)" stroke-width="3" stroke-linecap="round"/>
</g><text class="lab o" x="550" y="218" text-anchor="middle">人：踩下油門</text>
<text class="lab m hide-m" x="550" y="240" text-anchor="middle">客戶點頭、同仁照做、民眾來辦</text>
</svg>'''

# 三個原因的小圖
ICON = [
 # 一疊資料 → 一個動作
 '''<svg viewBox="0 0 150 80" aria-hidden="true"><rect x="8" y="18" width="46" height="52" rx="4" fill="var(--line)"/><rect x="14" y="12" width="46" height="52" rx="4" fill="var(--sky)" stroke="var(--line)"/><rect x="20" y="6" width="46" height="52" rx="4" fill="var(--card)" stroke="var(--navy)" stroke-width="2"/><path d="M28 20h30M28 30h30M28 40h20" stroke="var(--line)" stroke-width="3" stroke-linecap="round"/><path d="M78 38h22m-8-8l8 8l-8 8" stroke="var(--mute)" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2 7"/><circle cx="126" cy="38" r="18" fill="var(--orange)"/><path d="M117 38l7 7l12-14" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
 # 十個訊息，一個進得去
 '''<svg viewBox="0 0 150 80" aria-hidden="true"><g fill="var(--line)"><rect x="6" y="6" width="22" height="14" rx="3"/><rect x="34" y="4" width="22" height="14" rx="3"/><rect x="62" y="8" width="22" height="14" rx="3"/><rect x="20" y="26" width="22" height="14" rx="3"/><rect x="76" y="28" width="22" height="14" rx="3"/><rect x="90" y="6" width="22" height="14" rx="3"/><rect x="118" y="10" width="22" height="14" rx="3"/><rect x="104" y="30" width="22" height="14" rx="3"/><rect x="2" y="40" width="14" height="12" rx="3"/></g><rect x="48" y="26" width="22" height="14" rx="3" fill="var(--orange)"/><path d="M30 50 L120 50 L84 66 L84 78 L66 78 L66 66 Z" fill="var(--sky)" stroke="var(--navy)" stroke-width="2" stroke-linejoin="round"/><path d="M59 42 L72 58" stroke="var(--orange)" stroke-width="3" stroke-linecap="round" stroke-dasharray="2 6"/></svg>''',
 # 想做 ≠ 會做 ≠ 做了
 '''<svg viewBox="0 0 150 80" aria-hidden="true"><rect x="2" y="22" width="38" height="36" rx="8" fill="var(--sky)" stroke="var(--navy)" stroke-width="2"/><rect x="56" y="22" width="38" height="36" rx="8" fill="var(--card)" stroke="var(--orange)" stroke-width="2" stroke-dasharray="4 4"/><rect x="110" y="22" width="38" height="36" rx="8" fill="var(--card)" stroke="var(--orange)" stroke-width="2" stroke-dasharray="4 4"/><text x="21" y="45" text-anchor="middle" font-size="13" font-weight="700" fill="var(--navy-text)">想做</text><text x="75" y="45" text-anchor="middle" font-size="13" font-weight="700" fill="var(--accent-ink)">會做</text><text x="129" y="45" text-anchor="middle" font-size="13" font-weight="700" fill="var(--accent-ink)">做了</text><text x="48" y="46" text-anchor="middle" font-size="15" font-weight="900" fill="var(--mute)">≠</text><text x="102" y="46" text-anchor="middle" font-size="15" font-weight="900" fill="var(--mute)">≠</text></svg>''',
]
WHY = [
    ('資訊越便宜，|讓人照著做越貴', '五十頁的簡報，一個下午就能改一版。對方看完會不會動，是另一回事。'),
    ('注意力，|是現在最貴的原料', '人人一天都能多發十封信，每一封都在搶同一個人的注意力。多講一次，不一定聽得進去。'),
    ('想做 ≠ 會做 ≠ 做了', '65% 用 AI 的人，怕不用就會落後，可見想做的人不少。卡住的常是後面兩步：做起來順不順手、該做的那一秒有沒有提醒。'),
]

# 一套對所有人 vs 一人一套
def people(x0, same):
    cols = ['var(--navy)', 'var(--orange)', 'var(--mute)', 'var(--navy)', 'var(--orange)', 'var(--mute)']
    out = []
    for i in range(6):
        x = x0 + 26 + i * 50
        c = 'var(--line)' if same else cols[i]
        out.append(f'<circle cx="{x}" cy="112" r="11" fill="{c}"/><path d="M{x-16} 150 c0 -18 8 -24 16 -24 s16 6 16 24 z" fill="{c}"/>')
        if not same:
            out.append(f'<rect x="{x-17}" y="64" width="34" height="22" rx="6" fill="var(--card)" stroke="{cols[i]}" stroke-width="2"/>'
                       f'<path d="M{x-5} 86 l5 7 l5 -7" fill="var(--card)" stroke="{cols[i]}" stroke-width="2" stroke-linejoin="round"/>'
                       f'<path d="M{x-10} 72 h{12 + (i * 5) % 9} M{x-10} 79 h{9 + (i * 7) % 11}" stroke="{cols[i]}" stroke-width="2" stroke-linecap="round"/>')
    if same:
        out.append(f'<rect x="{x0+70}" y="22" width="180" height="46" rx="10" fill="var(--card)" stroke="var(--mute)" stroke-width="2"/>'
                   f'<path d="M{x0+150} 68 l10 14 l10 -14" fill="var(--card)" stroke="var(--mute)" stroke-width="2" stroke-linejoin="round"/>'
                   f'<path d="M{x0+90} 38 h140 M{x0+90} 52 h96" stroke="var(--line)" stroke-width="4" stroke-linecap="round"/>')
    return ''.join(out)
ONE = ('<svg viewBox="0 0 720 200" role="img" aria-label="左邊：六個人看同一則訊息。右邊：六個人各自收到不同的訊息。">'
       '<rect class="pane" x="0" y="0" width="340" height="200" rx="12"/><rect class="pane" x="380" y="0" width="340" height="200" rx="12"/>'
       + people(8, True) + people(388, False) +
       '<text class="lab m" x="170" y="184" text-anchor="middle">以前：同一句話，同一個時間</text>'
       '<text class="lab o sm" x="550" y="184" text-anchor="middle">現在：各自的話，各自的那一秒</text>'
       '<path class="line" d="M352 100 h16 m-7 -7 l7 7 l-7 7" style="stroke:var(--orange)"/></svg>')

# 兩個例子的示意圖
BILL = '''<svg viewBox="0 0 300 150" role="img" aria-label="示意圖：一張用電通知，下面多了三條橫條，比較你家、相似的家庭、省電的家庭。"><rect x="40" y="6" width="220" height="138" rx="8" fill="var(--card)" stroke="var(--line)" stroke-width="2"/><rect x="40" y="6" width="220" height="24" rx="8" fill="var(--sky)"/><text x="54" y="23" font-size="12" font-weight="700" fill="var(--navy-text)">本月用電通知</text><path d="M54 44h90M54 56h60" stroke="var(--line)" stroke-width="4" stroke-linecap="round"/><text x="54" y="82" font-size="11" fill="var(--mute)">你家</text><rect x="108" y="73" width="136" height="11" rx="5" fill="var(--orange)"/><text x="54" y="104" font-size="11" fill="var(--mute)">相似家庭</text><rect x="108" y="95" width="104" height="11" rx="5" fill="var(--navy)"/><text x="54" y="126" font-size="11" fill="var(--mute)">省電家庭</text><rect x="108" y="117" width="66" height="11" rx="5" fill="var(--mute)"/><text x="262" y="142" font-size="10" fill="var(--mute)" text-anchor="end" dy="12"></text></svg>'''
CUP = '''<svg viewBox="0 0 300 150" role="img" aria-label="示意圖：儀表板中間亮起一個咖啡杯圖示，旁邊寫著該休息了嗎。"><rect x="20" y="14" width="260" height="122" rx="60" fill="var(--navy)"/><circle cx="76" cy="75" r="40" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="3"/><path d="M76 75 L98 52" stroke="#fff" stroke-width="3" stroke-linecap="round"/><circle cx="224" cy="75" r="40" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="3"/><path d="M224 75 L204 58" stroke="#fff" stroke-width="3" stroke-linecap="round"/><rect x="122" y="40" width="56" height="70" rx="8" fill="#fff" fill-opacity=".1"/><path d="M136 62 h22 v14 c0 7 -5 11 -11 11 s-11 -4 -11 -11 z" fill="var(--orange)"/><path d="M158 65 h4 c4 0 6 3 6 6 s-2 6 -6 6 h-4" fill="none" stroke="var(--orange)" stroke-width="3"/><path d="M142 56 c-2 -4 2 -5 0 -9 M150 56 c-2 -4 2 -5 0 -9" stroke="var(--orange)" stroke-width="2" fill="none" stroke-linecap="round"/><text x="150" y="102" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">該休息了嗎？</text></svg>'''

EG_L = '''<svg viewBox="0 0 340 176" role="img" aria-label="一份提案，用 AI 一個小時就寫好。"><rect class="pane" width="340" height="176" rx="12"/>
<rect class="paper" x="34" y="22" width="88" height="108" rx="8"/>
<path d="M48 44h60M48 59h60M48 74h40M48 89h60M48 104h32" stroke="var(--line)" stroke-width="4" stroke-linecap="round"/>
<circle cx="122" cy="26" r="16" fill="var(--orange)"/><path d="M114 26l6 6l10-12" stroke="#fff" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<text class="t1" x="150" y="70">提案寫好了</text><text class="t2" x="150" y="96">用 AI，一個小時</text>
<text class="k" x="170" y="160" text-anchor="middle">做出來：變快了</text></svg>'''
EG_R = '''<svg viewBox="0 0 340 176" role="img" aria-label="客戶的訊息畫面：提案已讀，三天沒有回覆。"><rect class="pane" width="340" height="176" rx="12"/>
<rect class="paper" x="34" y="18" width="272" height="116" rx="14"/>
<rect x="128" y="32" width="164" height="34" rx="12" fill="var(--navy)"/><text class="t3" x="210" y="54" text-anchor="middle">提案在附件，請參考</text>
<text class="t2" x="292" y="86" text-anchor="end">已讀</text>
<circle cx="56" cy="110" r="4.5" fill="var(--line)"/><circle cx="72" cy="110" r="4.5" fill="var(--line)"/><circle cx="88" cy="110" r="4.5" fill="var(--line)"/>
<text class="t4" x="106" y="115">三天了，沒有回覆</text>
<text class="k o" x="170" y="160" text-anchor="middle">對方照著做：沒有變容易</text></svg>'''

def stat_block(tag, title, rows, cmp, big=False):
    r = ''.join(f'<div class="ai-row{" o" if o else ""}"><b>{v:g}%</b><span>{esc(t)}</span><div class="ai-bar"><i style="width:{v:g}%"></i></div></div>' for v, t, o in rows)
    c = f'<p class="cmp">{esc(cmp)}</p>' if cmp else ''
    return f'<div class="ai-stat{" ai-key" if big else ""}"><h3><small>{esc(tag)}</small>{esc(title)}</h3>{c}{r}</div>'
stats = ''.join(stat_block(*s) for s in STATS)
def nb(t): return ''.join(f'<span class="nb">{esc(x)}</span>' for x in t.split('|'))
why = ''.join(f'<div>{ICON[i]}<h3>{nb(h)}</h3><p>{esc(p)}</p></div>' for i, (h, p) in enumerate(WHY))

WHY_SEC = (f'''<section class="sec">
<h2>有了 AI 之後，哪一步變貴了</h2>
<div class="ai-why">{why}</div>
<p class="note">出處：65% 見 Microsoft《2026 Work Trend Index》</p>
</section>''' if SHOW_WHY else '')

body = f'''<span class="pill">我們跟 AI 的關係</span>
<h1><span class="nb">AI 做得出東西；</span><span class="nb">東西不會自己變成行為</span></h1>
<p class="lead">文案、簡報、報表、程式碼，AI 都做得出來，而且越來越便宜。客戶點頭、同仁照新流程做、民眾來辦，不會因為多了一份文件就發生。</p>
<figure class="ai-fig">{HERO}</figure>
<p class="ai-cap">AI 是導航，不是油門。<small>路，它算得出來；車要動，油門還是要有人踩。</small></p>

<section class="sec">
<h2><span class="nb">AI 都在用了，</span><span class="nb">為什麼公司還沒感覺？</span></h2>
<div class="ai-eg">{EG_L}<i></i>{EG_R}</div>
<p class="ai-say"><span class="nb">AI 讓「做出來」變快了；</span><span class="nb">「對方照著做」，沒有變容易。</span><small>而業績，是對方做了才會動。</small></p>
<div class="ai-stats">{stats}</div>
<div class="ai-so"><small>所以</small><b>我們不教你用 AI。<br><span class="nb">我們處理 AI 做完之後的那一步：</span><span class="nb">讓客戶回覆、讓同仁照做。</span></b><span>做法是改他做事當下的環境：他看到什麼、要做幾步、提醒什麼時候出現。</span></div>
<p class="note">{esc(SRC1)}</p>
</section>
{WHY_SEC}
<section class="sec">
<h2><span class="nb">以前，一套對所有人；</span><span class="nb">有了 AI，可以一人一套</span></h2>
<p>同一張立牌、同一封信、同一個預設，過去能做的大多是這樣。現在，資料記得每個人實際做了什麼，AI 幫忙決定對他說什麼、什麼時候說。「改環境，不改人」沒有變；變的是提醒可以照每個人的情況給。</p>
<figure class="ai-fig">{ONE}</figure>
<h3 style="margin-top:18px">兩個已經在路上的例子</h3>
<div class="ai-ex">
<div><span class="tag2">政府</span>{BILL}<h3><span class="nb">日本環境省：</span><span class="nb">用電通知上，</span><span class="nb">多一段「相似的家庭用多少」</span></h3>
<p>五家電力與瓦斯公司，四年內寄給大約 30 萬戶。每一戶收到的，是照自己家用量寫的節能報告。平均省下約 2% 的能源。</p>
<p>環境省把這個方向取名 BI-Tech：行為科學加上資料與 AI，回給每一戶自己的版本。</p>
<p class="src">出處：日本環境省「ナッジ事業」；日本オラクル、住環境計画研究所（2017–2020 年度實證）</p></div>
<div><span class="tag2">企業</span>{CUP}<h3><span class="nb">賓士 ATTENTION ASSIST：</span><span class="nb">先學你怎麼開，</span><span class="nb">再提醒你休息</span></h3>
<p>上路的前 20 分鐘，系統用 70 個參數記下你這一趟的開法。之後方向盤出現疲勞時常見的修正，儀表板亮起一個咖啡杯，加一聲提示音。</p>
<p>它沒有貼「請勿疲勞駕駛」的標語。它在那一秒，提醒那一位駕駛。</p>
<p class="src">出處：Mercedes-Benz 新聞資料（2009 年推出）</p></div>
</div>
<p class="note">兩張圖為示意。</p>
</section>

<section class="sec">
<h2>在我們的課裡，AI 站在哪一格</h2>
<p>順序是固定的：</p>
<ol class="ai-flow"><li><small>1</small>團隊先判斷</li><li class="on"><small>2</small>AI 給第二意見</li><li><small>3</small>講師帶著一起判斷</li><li><small>4</small>團隊拍板</li></ol>
<div class="ai-do">
<div><h3>選題</h3><p>幫團隊挑出先改哪一個行為。</p></div>
<div><h3>對照</h3><p>把你們的分析，跟整理好的 67 種常見卡點、101 種改法比一次，看漏了哪一格。</p></div>
<div><h3>帶回去</h3><p>每題一段 AI 提示詞，印在講義上。回公司套自己的狀況，再練一次。</p></div>
</div>
<p>把那句話寫好，AI 做得到。對哪個人、在哪一秒、改哪一個地方，是你們的判斷，也是這門課在練的事。</p>
</section>

<div class="ai-end"><b>行為不只由人決定，很大一部分由環境決定。<br>而環境，是你可以事先安排的。</b>
<ul><li>他想不想？</li><li>做起來順不順手？</li><li>該做的那一秒，有沒有提醒？</li></ul></div>

<div class="cta">
<a class="btn primary" href="/quiz/">還不確定？先做兩分鐘小測驗</a>
<a class="btn secondary" href="/trial/">想先試一次：59 分鐘試駕</a>
</div>
<p><a class="more" href="/how/">看三個改環境的例子 →</a>　<a class="more" href="/calc/">每一關多一點，最後差多少？算算看 →</a></p>
<div class="nav"><a href="/how/" class="prev">← 怎麼看問題</a><a href="/">回首頁 ⌂</a></div>'''

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
h = h.replace(f'{SITE}/about/', SITE + URL).replace('class="pg-about"', 'class="pg-ai"')
wr('ai/index.html', h + '\n' + body + '\n' + REST)

# 首頁第 02 段（我們怎麼看問題）底下加一個入口（冪等）
home = re.sub(r'<!-- ai:home -->.*?<!-- /ai:home -->', '', rd('index.html'), flags=re.S)
LINK = '<!-- ai:home --><a class="more" href="/ai/">公司名字裡的 AI，是什麼意思？ →</a><!-- /ai:home -->'
if '<!-- /calc:home -->' in home:
    home = home.replace('<!-- /calc:home -->', '<!-- /calc:home -->' + LINK, 1)
wr('index.html', home)
sm = rd('sitemap.xml')
if SITE + URL not in sm: wr('sitemap.xml', sm.replace('</urlset>', f'  <url><loc>{SITE}{URL}</loc></url>\n</urlset>'))
print('ai_page: /ai/ 已產生；首頁第 02 段加入口；sitemap 已補')
