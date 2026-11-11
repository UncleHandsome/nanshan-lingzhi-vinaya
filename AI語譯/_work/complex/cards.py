# -*- coding: utf-8 -*-
"""Emit compact judgment cards for live findings."""
import re, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
QRE = re.compile(r'「([^」]{2,60})」')
Q2 = re.compile(r'『([^』]{2,60})』')

def norm(x):
    return re.sub(r'\s+', '', x or '')

def window(text, needle, back=80, fwd=140):
    if not needle:
        return ''
    i = text.find(needle)
    if i < 0:
        return ''
    a = max(0, i - back); b = min(len(text), i + len(needle) + fwd)
    return ('…' if a > 0 else '') + text[a:b] + ('…' if b < len(text) else '')

def card(r, idx):
    prob = re.sub(r'\s+', '', r['problem'])[:200]
    basis = re.sub(r'\s+', '', r['basis'])[:90]
    sugg = re.sub(r'\s+', '', r['sugg'])[:130]
    quotes = QRE.findall(r['problem']) + Q2.findall(r['problem'])
    cur = r['cur']; src = r['src']
    cw = ''; sw = ''
    for q in quotes + QRE.findall(r['sugg']):
        w = window(cur, q, 70, 130)
        if w:
            cw = w; break
    if basis:
        sw = window(src, norm(basis)[:14], 40, 60)
    if not cw:
        cw = cur[:200] + '…'
    lines = ['[%d] %s | %s | %s | 信%s' % (idx, r['label'], r['pl'], (r['ptype'] or '')[:24], r['conf'] or '?'),
             '  問題：' + prob]
    if basis:
        lines.append('  依據：' + basis)
    if sugg:
        lines.append('  建議：' + sugg)
    if sw:
        lines.append('  原近：' + sw)
    lines.append('  譯近：' + cw)
    return '\n'.join(lines)

def main():
    rows = json.load(open(os.path.join(OUT, 'rows.json'), encoding='utf-8'))
    which = sys.argv[1] if len(sys.argv) > 1 else 'live'
    if which == 'live':
        sel = [r for r in rows if 'OLD_IN_CUR' in r['flags']]
    elif which == 'other':
        sel = [r for r in rows if 'OLD_IN_CUR' not in r['flags']]
    elif which.startswith('label:'):
        key = which[6:]
        sel = [r for r in rows if r['label'].startswith(key)]
    else:
        sel = rows
    out = os.path.join(OUT, 'cards_%s.txt' % which.replace(':', '_').replace('/', '_'))
    with open(out, 'w', encoding='utf-8') as f:
        for i, r in enumerate(sel, 1):
            f.write(card(r, i) + '\n\n')
    print(out, len(sel))

if __name__ == '__main__':
    main()
