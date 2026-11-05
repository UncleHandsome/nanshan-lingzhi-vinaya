
# -*- coding: utf-8 -*-
import io, re, os, json
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
X = os.path.join(B, '_src', 'xml')

def plain(fn):
    t = io.open(os.path.join(X, fn), encoding='utf-8').read()
    t = re.sub(r'<note[^>]*>.*?</note>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return re.sub(r'\s+', '', t)

cs = plain('T40n1804.xml')
zj = plain('T40n1805.xml')
print('行事鈔 chars', len(cs), '資持記 chars', len(zj))

def shingles(s, k=25):
    return set(s[i:i+k] for i in range(0, len(s) - k, k))

a = shingles(cs); b = shingles(zj)
inter = a & b
print('行事鈔 shingles', len(a), '資持記 shingles', len(b), '交集', len(inter), '重疊率 %.1f%%' % (100.0*len(inter)/len(a)))
