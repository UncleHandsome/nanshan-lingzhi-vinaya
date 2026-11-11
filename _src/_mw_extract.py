# -*- coding: utf-8 -*-
"""抽出 01/02 現代詞命中處的句子上下文，供人工覆核。"""
import io, os, re, glob, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out'
BOOKS = ['01_行事鈔', '02_戒疏']
WORDS = ['立案', '管轄', '工資', '認領', '免職', '局處', '考評', '權限', '程序',
         '罪犯', '判決', '起訴', '偵查', '證據', '契約', '營業', '公司', '股東',
         '效率', '制度', '組織', '機構', '單位', '部門', '系統', '方案', '項目',
         '審核', '批准', '授權', '資格', '標準化', '現代化', '科學', '數據']

# 以句末標點切句
SENT = re.compile(r'[^。！？]*(?:[。！？]|$)')


def sentences(text):
    out = []
    pos = 0
    for m in SENT.finditer(text):
        s = m.group(0)
        if s:
            out.append((pos, s))
        pos = m.end()
        if m.end() == m.start():
            break
    return out


rows = []
occur = 0
for bk in BOOKS:
    for f in sorted(glob.glob(os.path.join(B, bk, '*.txt'))):
        raw = open(f, 'rb').read().decode('utf-8')
        paras = re.split(r'\r?\n', raw)
        for pi, p in enumerate(paras):
            if not p.strip():
                continue
            for s, sent in sentences(p):
                for w in WORDS:
                    n = sent.count(w)
                    if not n:
                        continue
                    occur += n
                    # 取詞左右各 14 字
                    i = sent.index(w)
                    l = sent[max(0, i - 16):i]
                    r = sent[i + len(w):i + len(w) + 16]
                    rows.append((bk, os.path.basename(f), pi + 1, w, n, l, r, sent.strip()))

with io.open(os.path.join(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src', '_mw_rows.txt'), 'w',
             encoding='utf-8', newline='\n') as fh:
    for r in rows:
        fh.write('\t'.join([r[0], r[1], str(r[2]), r[3], str(r[4]), r[5], r[6], r[7]]) + '\n')

print('句數', len(rows), '出現次數', occur)
c = collections.Counter(r[3] for r in rows)
for w, n in c.most_common():
    print('%-4s %3d 句' % (w, n))
