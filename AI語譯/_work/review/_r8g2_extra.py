# -*- coding: utf-8 -*-
"""Two report rows carry a stale/wrong segment label (orig from seg-1).
Their real defects live at the previous segment.  Emit those fixes separately."""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

def paras(book, chunk):
    p = os.path.join('AI語譯', 'out', book, chunk + '.txt')
    return [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]

rows = []

# 287-0034 : 「便私自前往織師的住處」 -> remove 私自  (real location: 15b#18)
book, chunk, seg = '02_戒疏', '15b_卷三下之三', 18
base = paras(book, chunk)[seg - 1]
assert base.count('便私自前往織師的住處') == 1
new = base.replace('便私自前往織師的住處', '便前往織師的住處')
rows.append((book, chunk, str(seg), base, new))

# 466-0021 : 佛牙段落未譯（目前誤植為前段婬女譯文）  (real location: 15b#63)
book, chunk, seg = '資持記', '15b_下三', 63
base = paras(book, chunk)[seg - 1]
pack = io.open('AI語譯/_work/review/pack/in/校閱_07.txt', encoding='utf-8').read()
i = pack.find('】資持記/15b_下三#63')
assert i > 0
j = pack.find('\n【譯文】', i)
k = pack.find('\n\n', j)
new = pack[j + len('\n【譯文】'):k].strip()
assert base != new and '佛牙' in new and '但下' not in new
rows.append((book, chunk, str(seg), base, new))

with io.open('AI語譯/_work/review/fix_r8_g2_extra.tsv', 'w', encoding='utf-8', newline='') as f:
    for book, chunk, seg, base, new in rows:
        assert '\t' not in new and '\n' not in new and '\r' not in new
        f.write('%s\t%s\t%s\t%s\n' % (book, chunk, seg, new))

for book, chunk, seg, base, new in rows:
    print('--- %s %s#%s  %d -> %d' % (book, chunk, seg, len(base), len(new)))
    print('OLD:', base)
    print('NEW:', new)
    print()
