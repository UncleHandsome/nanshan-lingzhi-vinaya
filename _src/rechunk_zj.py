
# -*- coding: utf-8 -*-
import io, os, re, shutil
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'TXT', '資持記')
DST = os.path.join(B, 'TXT_分卷', '資持記_細分')
LIMIT = 24000

def b(s): return len(s.encode('utf-8'))

if not os.path.isdir(DST): os.makedirs(DST)
def paras_from(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    buf = ''
    out = []
    for ln in lines:
        buf += ln
        if len(buf) >= 120:
            # 在句末切
            m = list(re.finditer(r'[。！？；]', buf))
            if m and m[-1].end() >= 80:
                cut = m[-1].end()
                out.append(buf[:cut]); buf = buf[cut:]
            elif len(buf) >= 260:
                out.append(buf); buf = ''
    if buf.strip(): out.append(buf)
    return out

total = 0
for f in sorted(x for x in os.listdir(SRC) if x.endswith('.txt')):
    idx = f.split('_')[0]
    juan = f.split('_', 1)[1][:-4]
    text = io.open(os.path.join(SRC, f), encoding='utf-8').read()
    body = '\n'.join(text.split('\n')[3:])
    ps = paras_from(body)
    chunks, cur, cur_b = [], [], 0
    for p in ps:
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
        total += 1
print('chunks', total)
