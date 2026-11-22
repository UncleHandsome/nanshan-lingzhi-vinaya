# -*- coding: utf-8 -*-
"""清除修訂回覆誤帶入的【前文背景】等提示詞區塊。"""
import io, json, re, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MARKERS = ('【後文背景', '【前文背景', '【本次待審', '【程式預警', '【所釋鈔文')
for book in ('yichao', 'nicao'):
    p = os.path.join(B, '定稿', book + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    n = 0; empty = []
    for r in rows:
        t = r.get('translation', '')
        pos = [t.find(m) for m in MARKERS if t.find(m) >= 0]
        if not pos:
            continue
        cut = min(pos)
        t = t[:cut].rstrip()
        t = re.sub(r'\n*-{3,}\s*$', '', t).rstrip()
        r['translation'] = t
        for s in r.get('segments') or []:
            st = s.get('translation', '')
            sp = [st.find(m) for m in MARKERS if st.find(m) >= 0]
            if sp:
                s['translation'] = st[:min(sp)].rstrip()
        if not t:
            empty.append(r['key'])
        n += 1
    io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    print(book, 'cleaned', n, 'empty', len(empty), empty[:10])
