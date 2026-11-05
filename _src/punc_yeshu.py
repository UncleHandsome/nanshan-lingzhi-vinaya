
# -*- coding: utf-8 -*-
import os, io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'TXT_分卷', '03_業疏')
DST = os.path.join(B, 'TXT_句讀', '03_業疏')
os.makedirs(DST, exist_ok=True)
seq_file = os.path.join(DST, '01_序.txt')
seq = io.open(seq_file, encoding='utf-8').read().strip() if os.path.exists(seq_file) else ''

END = '。！？；：」'
def punctuate(p):
    p = p.strip()
    if not p: return p
    p = re.sub(r'[ \t]+', '', p)
    if p[-1] not in END:
        p += '。'
    return p

total = 0
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.txt'): continue
    key = f[:-4]
    lines = io.open(os.path.join(SRC, f), encoding='utf-8').read().split('\n')
    head, body = lines[:5], lines[5:]
    paras = [x.strip() for x in body if x.strip()]
    out = [punctuate(x) for x in paras]
    if key.startswith('01a') and seq:
        # 序：以人工句讀版本覆蓋對應段（序佔前若干段）
        seq_len = len(re.sub(r'[^\u4e00-\u9fff]', '', seq))
        acc = 0; cut = 0
        for i, p in enumerate(out):
            acc += len(re.sub(r'[^\u4e00-\u9fff]', '', p))
            cut = i + 1
            if acc >= seq_len: break
        out = [seq] + out[cut:]
    io.open(os.path.join(DST, key + '.txt'), 'w', encoding='utf-8').write('\n'.join(head) + '\n' + '\n'.join(out) + '\n')
    total += 1
print('wrote', total)
