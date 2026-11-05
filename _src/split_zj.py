
# -*- coding: utf-8 -*-
import io, os, re, shutil
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'TXT', '資持記')
DST = os.path.join(B, 'TXT_分卷', '資持記')
LIMIT = 29600

def b(s): return len(s.encode('utf-8'))

if os.path.isdir(DST): shutil.rmtree(DST)
os.makedirs(DST)
total = 0; sizes = []
files = sorted(f for f in os.listdir(SRC) if f.endswith('.txt'))
for f in files:
    idx = f.split('_')[0]
    juan = f.split('_', 1)[1][:-4]
    lines = io.open(os.path.join(SRC, f), encoding='utf-8').read().split('\n')
    # 去掉前三行抬頭
    body = lines[3:]
    # 併段：以空行分段
    paras, cur = [], []
    for ln in body:
        if ln.strip() == '':
            if cur: paras.append('\n'.join(cur)); cur = []
        else:
            cur.append(ln.rstrip())
    if cur: paras.append('\n'.join(cur))
    # 過長段落按句切開
    fixed = []
    for p in paras:
        if b(p) <= LIMIT - 200:
            fixed.append(p); continue
        sents = re.split(r'(?<=[。！？])', p)
        buf = ''
        for s2 in sents:
            if buf and b(buf) + b(s2) > LIMIT - 400:
                fixed.append(buf); buf = s2
            else:
                buf += s2
        if buf.strip(): fixed.append(buf)
    paras = fixed
    chunks, cur, cur_b = [], [], 0
    for p in paras:
        pb = b(p) + 2
        if cur and cur_b + pb > LIMIT:
            chunks.append(cur); cur, cur_b = [], 0
        cur.append(p); cur_b += pb
    if cur: chunks.append(cur)
    for i, ch in enumerate(chunks):
        letter = '' if len(chunks) == 1 else chr(96 + i + 1)
        fn = '%s%s_%s.txt' % (idx, letter, juan)
        head = '\n'.join([
            '四分律行事鈔資持記　%s%s' % (juan, ('（%d/%d）' % (i+1, len(chunks))) if len(chunks) > 1 else ''),
            '底本：CBETA 電子佛典（大正藏 T40 No.1805）',
            '（宋·元照撰）',
            '=' * 24, '', ''])
        io.open(os.path.join(DST, fn), 'w', encoding='utf-8').write(head + '\n\n'.join(ch) + '\n')
        sizes.append(b(head + '\n\n'.join(ch)))
        total += 1
print('chunks', total, 'max KB', round(max(sizes)/1024,1), 'min KB', round(min(sizes)/1024,1), 'total MB', round(sum(sizes)/1048576,2))
