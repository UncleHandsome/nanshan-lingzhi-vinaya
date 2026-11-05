
# -*- coding: utf-8 -*-
import io, re, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
X = os.path.join(B, '_src', 'xml')
t = io.open(os.path.join(X, 'T40n1805.xml'), encoding='utf-8').read()
parts = re.split(r'<cb:juan[^>]*fun="open"[^>]*>\s*<cb:mulu[^>]*>([^<]*)</cb:mulu>', t)
names = parts[1::2]; texts = parts[2::2]
out = os.path.join(B, 'TXT', '資持記'); os.makedirs(out, exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out, f))
digits = {1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二',13:'十三',14:'十四',15:'十五',16:'十六'}
tot = 0
for i, (nm, body) in enumerate(zip(names, texts), 1):
    body = re.sub(r'<note[^>]*>(.*?)</note>', r'〔\1〕', body, flags=re.S)
    s = re.sub(r'<[^>]+>', '', body).replace('&amp;','&')
    s = s.replace('\r', '')
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    nm = nm.strip() or ('卷%d' % i)
    fn = '%02d_%s.txt' % (i, nm)
    io.open(os.path.join(out, fn), 'w', encoding='utf-8').write('四分律行事鈔資持記　%s\n（大正藏 T40 No.1805　宋·元照撰）\n%s\n\n' % (nm, '='*20) + s)
    tot += len(s)
    print(fn, len(s))
print('total', tot)
