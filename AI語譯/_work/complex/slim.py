# -*- coding: utf-8 -*-
"""Compose compact judgment slices (sorted by source order)."""
import re, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
QRE = re.compile(r'「([^」]{2,60})」')
Q2 = re.compile(r'『([^』]{2,60})』')

def norm(x):
    return re.sub(r'\s+', '', x or '')

def window(text, needle, back=60, fwd=110):
    if not needle:
        return ''
    i = text.find(needle)
    if i < 0:
        return ''
    a = max(0, i - back); b = min(len(text), i + len(needle) + fwd)
    return ('…' if a > 0 else '') + text[a:b] + ('…' if b < len(text) else '')

def book_key(label):
    m = re.match(r'(\d+_[^/]+)/(\S+)#(\d+)', label)
    if not m:
        return (9, label, 0)
    return (int(m.group(1)[:2]), m.group(2), int(m.group(3)))

def slim(r, i):
    prob = norm(r['problem'])[:150]
    basis = norm(r['basis'])[:48]
    sugg = norm(r['sugg'])[:85]
    quotes = QRE.findall(r['problem']) + Q2.findall(r['problem'])
    cw = ''
    for q in quotes + QRE.findall(r['sugg']):
        cw = window(r['cur'], q)
        if cw:
            break
    if not cw:
        cw = r['cur'][:190] + '…'
    s = '[%d]%s|%s|%s|%s\n問:%s\n' % (i, r['label'].replace('01_行事鈔/', ''), r['pl'], r['conf'] or '?', (r['ptype'] or '')[:14], prob)
    if basis:
        s += '依:%s\n' % basis
    if sugg:
        s += '建:%s\n' % sugg
    s += '近:%s' % cw
    return s

def main():
    rows = json.load(open(os.path.join(OUT, 'rows.json'), encoding='utf-8'))
    which = sys.argv[1]
    if which == 'live':
        sel = [(i + 1, r) for i, r in enumerate(rows) if 'OLD_IN_CUR' in r['flags']]
    else:
        sel = [(i + 1, r) for i, r in enumerate(rows) if 'OLD_IN_CUR' not in r['flags']]
    sel.sort(key=lambda x: book_key(x[1]['label']))
    base = os.path.join(OUT, 'slim_%s.txt' % which)
    with open(base, 'w', encoding='utf-8') as f:
        for i, r in sel:
            f.write(slim(r, i) + '\n\n')
    print(base, len(sel), os.path.getsize(base))

if __name__ == '__main__':
    main()
