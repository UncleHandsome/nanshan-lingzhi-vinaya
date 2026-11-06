# -*- coding: utf-8 -*-
import json, io, os, re, difflib

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
src = os.path.join(base, 'AI語譯', '_work', 'align_fix2', '002.json')
data = json.load(io.open(src, encoding='utf-8'))
items = data['items']
cands = data['cand']

# full texts
def load_full(p):
    out = []
    for line in io.open(p, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^\[([zc])(\d+)\]\s*(.*)$', line)
        if m:
            out.append((m.group(1), int(m.group(2)), m.group(3)))
    return out

fullc = {i: t for _, i, t in load_full(os.path.join(base, 'AI語譯', '_work', 'align_fix', '_tmp029_cao_full.txt'))}
fullz = {i: t for _, i, t in load_full(os.path.join(base, 'AI語譯', '_work', 'align_fix', '_tmp029_ji_full.txt'))}

def norm(s):
    # keep CJK + ascii letters/digits
    return ''.join(ch for ch in s if ('\u3400' <= ch <= '\u9fff') or ch.isalnum())

def match_stats(z, c):
    a, b = norm(z), norm(c)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    blocks = [bl for bl in sm.get_matching_blocks() if bl.size >= 2]
    total = sum(bl.size for bl in blocks)
    # first significant block within z (size>=4)
    first = None
    for bl in blocks:
        if bl.size >= 4:
            first = (bl.a, bl.size)
            break
    return total, first, blocks

print('items', len(items), 'cands', len(cands))
rows = []
for it in items:
    z = it['z']
    zt = fullz.get(z, it['text'])
    scores = []
    for cd in cands:
        c = cd['c']
        ct = fullc.get(c, cd['text'])
        total, first, blocks = match_stats(zt, ct)
        scores.append((total, first, c, ct))
    scores.sort(key=lambda x: -x[0])
    rows.append((z, zt, scores))

out = []
for z, zt, scores in rows:
    out.append('#### z%d  %s' % (z, zt))
    for total, first, c, ct in scores[:4]:
        out.append('   c%-2d total=%-3d first=%s | %s' % (c, total, str(first), ct[:60]))
    out.append('')
io.open(os.path.join(os.path.dirname(__file__), '_w002_score.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('written')
