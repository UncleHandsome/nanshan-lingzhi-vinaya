# -*- coding: utf-8 -*-
"""Targeted cleanup of duplication artifacts introduced by replacements."""
import json, re, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
FIX = [
    ('01_行事鈔/01b_卷上之一#50', '不足數的相狀如前面所述如前面所述。', '不足數的相狀如前面所述。'),
    ('01_行事鈔/05c_卷中之一#1', '「常住常住物。」是指', '「常住常住物」，是指'),
    ('01_行事鈔/05c_卷中之一#1', '「現前現前物。」若盜取', '「現前現前物」，若盜取'),
    ('01_行事鈔/11b_卷下之三#13', '乃至若乃至若想聽人稱說', '乃至若想聽人稱說'),
    ('01_行事鈔/01b_卷上之一#70', '有所乖違有所違背', '有所乖違'),
    ('02_戒疏/05b_卷二上之一#33', '首先指出首先指出', '首先指出'),
    ('02_戒疏/02b_卷一上之二#8', '這說的是這說的是', '這說的是'),
    ('02_戒疏/04a_卷一下之二#6', '而犯墮罪而犯墮罪', '而犯墮罪'),
    ('02_戒疏/05c_卷二上之一#12', '意思是意思是有情識', '意思是有情識'),
    ('02_戒疏/06b_卷二上之二#87', '而判為不犯而判為不犯', '而判為不犯'),
    ('02_戒疏/07b_卷二上之三#29', '就是現今就是現今', '就是現今'),
    ('02_戒疏/09d_卷二下之二#34', '那麼那麼佛', '那麼佛'),
    ('02_戒疏/05c_卷二上之一#96', '令對方獲益為要作為要歸', '令對方獲益為要，作為要歸'),
    ('02_戒疏/03c_卷一下之一#32', '所以說「乃至。」', '所以說「乃至」。'),
]

def main():
    byfile = collections.defaultdict(list)
    for lab, old, new in FIX:
        byfile[lab].append((old, new))
    changed = []
    for lab, fixes in byfile.items():
        m = re.match(r'(.+?)/([^/]+)#(\d+)$', lab)
        book, chunk, seg = m.group(1), m.group(2), int(m.group(3))
        p = os.path.join(ROOT, 'AI語譯', 'out', book, chunk + '.txt')
        raw = open(p, 'rb').read().decode('utf-8')
        eol = '\r\n' if '\r\n' in raw else '\n'
        blocks = re.split(re.escape(eol + eol), raw)
        t = blocks[seg - 1]
        for old, new in fixes:
            if t.count(old) == 1:
                t = t.replace(old, new, 1)
            else:
                print('SKIP', lab, repr(old), t.count(old))
        blocks[seg - 1] = t
        open(p, 'wb').write((eol + eol).join(blocks).encode('utf-8'))
        changed.append(lab)
    print('cleaned', len(changed), changed)

if __name__ == '__main__':
    main()
