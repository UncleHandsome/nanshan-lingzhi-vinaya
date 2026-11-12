# -*- coding: utf-8 -*-
import os, re, sys
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.stdout.reconfigure(encoding='utf-8')
p = os.path.join(ROOT, '存疑材料', '補判', '末_補_01.md')
txt = open(p, encoding='utf-8').read()
parts = re.split(r'\n### ', txt)
head, entries = parts[0], parts[1:]
print('entries:', len(entries))
print('prompt has 是錯/不是錯/材料不足:', all(k in head for k in ['是錯', '不是錯', '材料不足']))

def blank_paras(path):
    with open(path, encoding='utf-8') as f:
        t = f.read().replace('\r\n', '\n')
    return [b.strip() for b in re.split(r'\n\s*\n', t.strip('\n')) if b.strip()]
def line_paras(path, skip=5):
    with open(path, encoding='utf-8') as f:
        ls = f.read().replace('\r\n', '\n').split('\n')
    return [l.strip() for l in ls[skip:] if l.strip()]

bad = 0
seen = []
for e in entries:
    code = e.split('\n', 1)[0].strip()
    seen.append(code)
    fields = {}
    for ln in e.split('\n'):
        m = re.match(r'- \*\*(.+?)\*\*：(.+)$', ln)
        if m:
            fields[m.group(1)] = m.group(2)
    need = ['段號', '書/chunk#段', '原文', '現行譯文', '疑點', '原檔']
    missing = [k for k in need if k not in fields]
    if missing:
        print('MISSING', code, missing); bad += 1; continue
    loc = fields['書/chunk#段']
    m = re.match(r'(.+?)／(.+?)＃(\d+)$', loc)
    book, chunk, para = m.group(1), m.group(2), int(m.group(3))
    if book == '03_業疏':
        ps = blank_paras(os.path.join(ROOT, 'TXT_分卷_標點', book, chunk + '.txt'))
    else:
        ps = line_paras(os.path.join(ROOT, 'TXT_分卷', book, chunk + '.txt'))
    yw = blank_paras(os.path.join(ROOT, 'AI語譯', 'out', book, chunk + '.txt'))
    ok1 = ps[para-1] == fields['原文']
    ok2 = yw[para-1] == fields['現行譯文']
    if not (ok1 and ok2):
        print('MISMATCH', code, 'txt=', ok1, 'yw=', ok2); bad += 1
print('bad:', bad)
print('order:', ' '.join(seen))
