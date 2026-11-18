#!/usr/bin/env python3
"""選題器：四個模組的題目順序改成「這條路」的順序（v0.1，2026-11-18）。

用法：python3 tools/picker_order_patch.py <根目錄>

為什麼有這支：選題器的來源檔（picker_standalone.html）不在 repo，build.py 只是把它包進外框。
講義題號 2026-11-18 起照模組路線圖的順序編；這支把 /picker/ 裡同樣那幾題排成同一個順序，
官網跟講義才對得上。只動順序，題目文字、模組代碼、網址都不動。可重跑：已經排好就不動。
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

def main(root):
    p = pathlib.Path(root) / 'picker' / 'index.html'
    s = p.read_text(encoding='utf-8')
    changed = []
    for key, order in ORDER.items():
        m = re.search(r'("%s":\{"t":"[^"]+".*?"q":)(\[.*?\])' % key, s, re.S)
        if not m:
            sys.exit(f'picker_order_patch: 找不到模組 {key}')
        qs = json.loads(m.group(2))
        if len(qs) != len(order):
            sys.exit(f'picker_order_patch: {key} 題數 {len(qs)} 不等於 {len(order)}')
        def rank(q):
            hits = [i for i, tag in enumerate(order) if tag in q]
            if len(hits) != 1:
                sys.exit(f'picker_order_patch: {key} 這一題對不到唯一位置：{q}')
            return hits[0]
        new = sorted(qs, key=rank)
        if new != qs:
            s = s[:m.start(2)] + json.dumps(new, ensure_ascii=False, separators=(',', ':')) + s[m.end(2):]
            changed.append(key)
    p.write_text(s, encoding='utf-8')
    print('picker_order_patch:', ('改了 ' + '、'.join(changed)) if changed else '已是路的順序，沒有變動')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
