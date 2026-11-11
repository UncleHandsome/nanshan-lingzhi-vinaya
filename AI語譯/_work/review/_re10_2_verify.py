# -*- coding: utf-8 -*-
"""re10_2 套用後獨立驗證：備份 vs 現檔、TSV vs out 段。"""
import io, os, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out', '01_行事鈔')
BK = os.path.join(B, '歸檔', 're10_2修正前', '01_行事鈔')
REV = os.path.join(B, 'AI語譯', '_work', 'review')

rows = [l.split('\t') for l in
        io.open(os.path.join(REV, 'fix_re10_2.tsv'), encoding='utf-8').read().splitlines()]
print('TSV 列數', len(rows), '欄位數', set(len(r) for r in rows))

for ch in ['00_卷首', '01a_卷上之一']:
    old = io.open(os.path.join(BK, ch + '.txt'), encoding='utf-8', newline='').read()
    new = io.open(os.path.join(OUT, ch + '.txt'), encoding='utf-8', newline='').read()
    po, pn = old.split('\r\n\r\n'), new.split('\r\n\r\n')
    assert len(po) == len(pn), (ch, len(po), len(pn))
    diff = [i + 1 for i in range(len(po)) if po[i] != pn[i]]
    print(f'{ch}: 段數 {len(po)-1}, 變動段 {diff}')
    print(f'   檔尾 \\r\\n\\r\\n: {new.endswith(chr(13)+chr(10)+chr(13)+chr(10))}, 長度 {len(old)}->{len(new)}')
    for i in diff:
        assert len(po[i - 1]) != len(pn[i - 1]) or po[i - 1] != pn[i - 1]
    # TSV 對照
    for r in rows:
        if r[1] != ch:
            continue
        seg = int(r[2])
        assert r[3] == pn[seg - 1], (ch, seg, 'TSV 與 out 段不一致')
print('TSV 與 out 段逐字相同：OK')

# 舊句 A 均已消失、新句 B 均在
log = __import__('json').load(io.open(
    os.path.join(REV, '_log_re10_2_apply.json'), encoding='utf-8'))
for rec in log:
    parts = io.open(os.path.join(OUT, rec['chunk'] + '.txt'), encoding='utf-8',
                    newline='').read().split('\r\n\r\n')
    txt = parts[rec['seg'] - 1]
    for op in rec['ops']:
        assert op['a'] not in txt, (rec['chunk'], rec['seg'], op['a'][:20])
        assert op['b'] in txt, (rec['chunk'], rec['seg'], op['b'][:20])
    assert txt == rec['new']
print('A 全消失 / B 全在 / 段全文與 log 相同：OK')
print('段落總數：00_卷首 82、01a_卷上之一 91（未變）')
