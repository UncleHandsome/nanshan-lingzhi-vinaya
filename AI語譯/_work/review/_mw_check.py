# -*- coding: utf-8 -*-
"""驗證 _mw_edits.py 的每一筆：段落定位、檔內唯一性、字串存在。"""
import io, os, re, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
spec = importlib.util.spec_from_file_location('mw', os.path.join(B, 'AI語譯', '_work', 'review', '_mw_edits.py'))
mw = importlib.util.module_from_spec(spec); spec.loader.exec_module(mw)
EDITS = mw.EDITS

def load(book, f):
    p = os.path.join(OUT, book, f)
    raw = open(p, 'rb').read()
    if raw[:3] == b'\xef\xbb\xbf':
        return p, raw, True
    return p, raw, False

def paras(text):
    t = text.replace('\r\n', '\n')
    return [p for p in t.split('\n\n') if p.strip()]

cache = {}
bad = []
seen = {}
for i, (book, f, pidx, old, new) in enumerate(EDITS, 1):
    key = (book, f)
    if key not in cache:
        p, raw, bom = load(book, f)
        cache[key] = (p, raw.decode('utf-8', 'strict'), bom, paras(raw.decode('utf-8', 'strict')))
    p, text, bom, ps = cache[key]
    if bom:
        bad.append((i, 'BOM', book + '/' + f, old))
    if old == new:
        bad.append((i, 'SAME', book + '/' + f, old))
    if pidx < 1 or pidx > len(ps):
        bad.append((i, 'PARA_RANGE', book + '/' + f, '%s (paras=%d)' % (pidx, len(ps))))
        continue
    if old not in ps[pidx - 1]:
        bad.append((i, 'NOT_IN_PARA', '%s/%s#%d' % (book, f, pidx), old))
    n = text.count(old)
    if n != 1:
        bad.append((i, 'FILE_COUNT=%d' % n, '%s/%s#%d' % (book, f, pidx), old))
    if new in text:
        bad.append((i, 'NEW_ALREADY_PRESENT', '%s/%s' % (book, f), new))
    seen.setdefault((book, f), []).append(i)

print('edits', len(EDITS), 'files', len(seen))
print('problems', len(bad))
for b in bad:
    print(b)
