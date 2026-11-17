# nav_patch.py v0.1 (2026-11-17) — 主選單加「常見卡點」、首頁痛點卡連到 /q/、「講師把關」→「講師帶你一起判斷」
# 用法：python3 tools/nav_patch.py <站台根目錄>   可重跑（冪等）。只改中文頁，不碰 /en/。
import sys, re, pathlib
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
NEW_NAV = ('<nav class="sitenav" aria-label="主選單"><a href="/q/">常見卡點</a><a href="/how/">怎麼看問題</a>'
           '<a href="/#courses">課程</a><a href="/about/">為什麼是我們</a><a href="/contact/">聯絡</a>'
           '<a class="lang" href="/en/" hreflang="en" lang="en">EN</a></nav>')
CUR = {'/q/': 'q', '/how/': 'how', '/about/': 'about', '/contact/': 'contact'}
n = 0
for f in sorted(ROOT.glob('**/index.html')):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith('en/') or rel.startswith('tools/'): continue
    s = f.read_text(encoding='utf-8'); o = s
    # 主選單
    nav = NEW_NAV
    url = '/' + rel[:-len('index.html')]
    for k, v in CUR.items():
        if url == k or (k == '/q/' and url.startswith('/q/')):
            nav = nav.replace(f'<a href="{k}">', f'<a href="{k}" aria-current="page">', 1)
    s = re.sub(r'<nav class="sitenav" aria-label="主選單">.*?</nav>', nav, s, flags=re.S)
    # 把關 → 帶你一起判斷（全站用語規則 1112）
    s = s.replace('講師把關', '講師帶你一起判斷')
    if rel == 'index.html':
        s = s.replace('<a class="tile" href="/half-day/#sample"><span class="k">客人</span><b>「提案做得再好，客戶還是說我再想想。」</b><span class="go">看這一題怎麼上 →</span></a>',
                      '<a class="tile" href="/q/proposal-no-reply/"><span class="k">客人</span><b>「提案做得再好，客戶還是說我再想想。」</b><span class="go">看直接回答 →</span></a>')
        s = s.replace('<a class="tile" href="/workshop/#case"><span class="k">員工</span><b>「AI 工具買了，規矩訂了，就是沒人用。」</b><span class="go">看一個案例怎麼走 →</span></a>',
                      '<a class="tile" href="/q/ai-tool-not-used/"><span class="k">員工</span><b>「AI 工具買了，規矩訂了，就是沒人用。」</b><span class="go">看直接回答 →</span></a>')
        s = s.replace('<a class="tile" href="/how/"><span class="k">現場</span><b>「SOP 寫得很清楚，現場還是照舊。」</b><span class="go">看我們怎麼看 →</span></a>',
                      '<a class="tile" href="/q/sop-not-followed/"><span class="k">現場</span><b>「SOP 寫得很清楚，現場還是照舊。」</b><span class="go">看直接回答 →</span></a>')
        if 'nav:painmore' not in s:
            s = s.replace('<p class="big">三句講的是同一件事：你想要的行為，沒有發生。</p>',
                          '<p class="big">三句講的是同一件事：你想要的行為，沒有發生。</p>\n<!-- nav:painmore --><a class="more" href="/q/">八個常見卡點，每一題一頁直接回答 →</a><!-- /nav:painmore -->')
    if s != o:
        f.write_text(s, encoding='utf-8'); n += 1
print(f'nav_patch: {n} 頁更新')
