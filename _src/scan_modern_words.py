# -*- coding: utf-8 -*-
"""掃描譯文中的現代法律／行政／商業用語，這類詞在律典語境多屬誤譯。"""
import io, os, re, glob, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')

WORDS = ['立案', '管轄', '工資', '認領', '免職', '局處', '考評', '權限', '程序',
         '罪犯', '判決', '起訴', '偵查', '證據', '契約', '營業', '公司', '股東',
         '效率', '制度', '組織', '機構', '單位', '部門', '系統', '方案', '項目',
         '審核', '批准', '授權', '資格', '標準化', '現代化', '科學', '數據']

hits = collections.defaultdict(list)
for f in glob.glob(os.path.join(OUT, '*', '*.txt')):
    book = os.path.basename(os.path.dirname(f))
    ch = os.path.splitext(os.path.basename(f))[0]
    for i, p in enumerate(re.split(r'\r?\n\r?\n', io.open(f, encoding='utf-8').read())):
        if not p.strip():
            continue
        for w in WORDS:
            if w in p:
                hits[w].append((book, ch, i + 1))

print('命中詞數', len(hits), '總處數', sum(len(v) for v in hits.values()))
for w, v in sorted(hits.items(), key=lambda x: -len(x[1])):
    books = collections.Counter(b for b, _, _ in v)
    print('%-6s %3d 處  %s' % (w, len(v), dict(books)))
