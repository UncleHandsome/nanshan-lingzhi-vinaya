
# -*- coding: utf-8 -*-
import io, re, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
X = os.path.join(B, '_src', 'xml')

def plain(fn, strip_notes=True):
    t = io.open(os.path.join(X, fn), encoding='utf-8').read()
    if strip_notes:
        t = re.sub(r'<note[^>]*>.*?</note>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('&amp;', '&')
    return re.sub(r'\s+', '', t)

cs = plain('T40n1804.xml'); zj = plain('T40n1805.xml')
for k in (8, 12, 20):
    a = set(cs[i:i+k] for i in range(len(cs)-k))
    b = set(zj[i:i+k] for i in range(len(zj)-k))
    print('k=%d 行鈔 n-gram %d，見於資持記 %d (%.1f%%)' % (k, len(a), len(a & b), 100.0*len(a & b)/len(a)))

# 抽出資持記分卷
t = io.open(os.path.join(X, 'T40n1805.xml'), encoding='utf-8').read()
parts = re.split(r'<cb:juan[^>]*fun="open"[^>]*>\s*<cb:mulu[^>]*>([^<]*)</cb:mulu>', t)
print('段落數', len(parts))
names = parts[1::2]
texts = parts[2::2]
out = os.path.join(B, 'TXT', '資持記'); os.makedirs(out, exist_ok=True)
for i, (nm, body) in enumerate(zip(names, texts), 1):
    s = re.sub(r'<note[^>]*>.*?</note>', '', body, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s).replace('&amp;','&')
    s = re.sub(r'[ \t]+', ' ', s)
    io.open(os.path.join(out, '%02d_%s.txt' % (i, nm.strip() or ('卷%d' % i))), 'w', encoding='utf-8').write(s)
print('卷數', len(names), names)
