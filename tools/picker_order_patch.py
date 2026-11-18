#!/usr/bin/env python3
"""選題器：四個模組的題目順序改成「這條路」的順序（v0.3，2026-11-18）。

用法：python3 tools/picker_order_patch.py <根目錄>

為什麼有這支：選題器的來源檔（picker_standalone.html）不在 repo，build.py 只是把它包進外框。
講義題號 2026-11-18 起照模組路線圖的順序編；這支把 /picker/ 裡同樣那幾題排成同一個順序，
官網跟講義才對得上。只動順序，題目文字、模組代碼、網址都不動。可重跑：已經排好就不動。

注意：頁面裡的「推薦組合」（PLANS）和「單一主題推薦」（THEME_PLANS）是用「第幾題」指到題目的，
所以題目換位置時，這兩處的編號要一起換，不然推薦會指到別題。v0.1 漏了這件事，v0.2 補上；
同一個模組連續出現的幾題，換完之後照新題號由小到大排（＝路的順序）。
"""
import json, pathlib, re, sys

# 每個模組：照新順序列出每一題的辨識字（題目裡一定會出現的一段）
ORDER = {
    'RP':  ['自動開通', '幾套做法', '主管定', '哪天、幾點做', '跟自己比', '獎「做了」'],
    'AC':  ['一鍵帶入', '啟用邀請', '歡迎訊息', '第一次設定', '哪天開始', '進度條'],
    'PR':  ['以為這是什麼', '第一個數字', '襯它', '總價', '省下', '免費', '誰先出價', '折扣怎麼讓'],
    'FMC': ['分幾頁', '先問什麼', '自己填嗎', '勾好', '哪天做', '送出之後'],
    'FMG': ['分幾頁', '先問什麼', '自己填嗎', '勾好', '哪天辦', '送出之後'],
}

# 推薦理由裡把題目照順序念一遍的句子：（舊句, 新句）
WHY_FIX = [
    ('哪一欄能不能不要他填、哪一格能不能先勾好、先問什麼、要不要分頁、末尾要不要留一格讓他寫哪天辦、送出之後他看到什麼',
     '要不要分頁、先問什麼、哪一欄能不能不要他填、哪一格能不能先勾好、末尾要不要留一格讓他寫哪天辦、送出之後他看到什麼'),
]

def main(root):
    p = pathlib.Path(root) / 'picker' / 'index.html'
    s = p.read_text(encoding='utf-8')
    m = re.search(r'const\s+D\s*=\s*', s)
    if not m:
        sys.exit('picker_order_patch: 找不到資料區 const D=')
    D, end = json.JSONDecoder().raw_decode(s[m.end():])
    changed = []
    for key, order in ORDER.items():
        qs = D['TITLES'][key]['q']
        if len(qs) != len(order):
            sys.exit(f'picker_order_patch: {key} 題數 {len(qs)} 不等於 {len(order)}')
        def rank(q):
            hits = [i for i, tag in enumerate(order) if tag in q]
            if len(hits) != 1:
                sys.exit(f'picker_order_patch: {key} 這一題對不到唯一位置：{q}')
            return hits[0]
        perm = [rank(q) for q in qs]            # 舊位置 → 新位置
        if perm == list(range(len(qs))):
            continue
        D['TITLES'][key]['q'] = [q for _, q in sorted(zip(perm, qs))]
        for pl in D.get('PLANS', {}).values():
            for o in pl['options']:
                items = [[i, perm[q]] if i == key else [i, q] for i, q in o['items']]
                out, run = [], []
                for it in items + [[None, None]]:   # 同一模組連續的幾題，照新題號排
                    if run and it[0] != run[0][0]:
                        out += sorted(run, key=lambda x: x[1]) if run[0][0] == key else run
                        run = []
                    run.append(it)
                o['items'] = out
        tp = D.get('THEME_PLANS', {}).get(key)
        if tp:
            tp['items'] = sorted(perm[i] for i in tp['items'])
        changed.append(key)
    # 推薦理由裡照舊順序列題目的句子，跟著改（找得到舊句才換；換過就不動）
    for pl in D.get('PLANS', {}).values():
        for o in pl['options']:
            for old, new in WHY_FIX:
                if old in o.get('why', ''):
                    o['why'] = o['why'].replace(old, new)
                    if 'why' not in changed:
                        changed.append('why')
    if changed:
        s = s[:m.end()] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[m.end() + end:]
        p.write_text(s, encoding='utf-8')
    print('picker_order_patch:', ('改了 ' + '、'.join('推薦理由' if c == 'why' else c for c in changed)) if changed else '已是路的順序，沒有變動')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
