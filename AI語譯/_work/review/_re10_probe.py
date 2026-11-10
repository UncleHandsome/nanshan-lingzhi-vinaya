# -*- coding: utf-8 -*-
"""Probe: map re10.txt segment ids to out files via 校閱_80K and verify paragraph indices."""
import io, os, re, sys, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RE10 = os.path.join(B, '疑慮_10K', 're10.txt')

txt = io.open(RE10, encoding='utf-8-sig').read()
lines = txt.splitlines()
entries = []
i = 0
while i < len(lines):
    ln = lines[i].strip()
    if not ln:
        i += 1
        continue
    m = re.match(r'^(\d{3}-\d{4})(?:（[^）]*）)?｜(成立|不成立)｜(.*)$', ln)
    if m:
        e = {'seg': m.group(1), 'status': m.group(2), 'reason': m.group(3).strip(), 'fix': ''}
        if i + 1 < len(lines) and lines[i+1].strip().startswith('改法：'):
            e['fix'] = lines[i+1].strip()[3:].strip()
        entries.append(e)
        i += 1
        continue
    print('UNPARSED:', ln)
    i += 1

print('entries:', len(entries), 'chengli:', sum(1 for e in entries if e['status'] == '成立'))

# parse 校閱 files
review = {}
for p in sorted(glob.glob(os.path.join(B, '校閱_80K', '校閱_*.txt'))):
    data = io.open(p, encoding='utf-8-sig').read().splitlines()
    cur = None
    for ln in data:
        m = re.match(r'^【(\d{3}-\d{4})】(\S+?)/([^#]+)#(\d+)\s*$', ln)
        if m:
            cur = {'sid': m.group(1), 'book': m.group(2), 'chunk': m.group(3), 'idx': int(m.group(4)), 'file': p}
            continue
        if cur is not None and ln.startswith('【譯文】'):
            cur['tr'] = ln[4:]
            review[cur['sid']] = cur
            cur = None

def paras(path):
    text = io.open(path, encoding='utf-8').read()
    return [x.strip() for x in re.split(r'\r?\n\s*\r?\n', text.strip()) if x.strip()]

# check mapping for every review entry
bad = 0
cache = {}
for sid, r in review.items():
    op = os.path.join(B, 'AI語譯', 'out', r['book'], r['chunk'] + '.txt')
    if op not in cache:
        cache[op] = paras(op) if os.path.exists(op) else None
    ps = cache[op]
    if ps is None:
        print('NOFILE', sid, op)
        bad += 1
        continue
    idx = r['idx'] - 1
    if idx >= len(ps) or ps[idx] != r['tr'].strip():
        bad += 1
        print('MISMATCH', sid, r['book'], r['chunk'], r['idx'], 'npara=', len(ps))
        if idx < len(ps):
            print('  out:', ps[idx][:80])
            print('  rev:', r['tr'][:80])
print('review entries:', len(review), 'bad:', bad)

# report target A occurrence
for e in entries:
    if e['status'] != '成立':
        continue
    r = review.get(e['seg'])
    if not r:
        print('NOROW', e['seg'])
        continue
    ps = paras(os.path.join(B, 'AI語譯', 'out', r['book'], r['chunk'] + '.txt'))
    segtext = ps[r['idx']-1]
    m = re.search(r'「([^「」]*)」', e['fix'])
    if m:
        a = m.group(1)
        print('%s %s/%s#%d A-count=%d | %s' % (e['seg'], r['book'], r['chunk'], r['idx'], segtext.count(a), a[:40]))
    else:
        print('%s %s/%s#%d NOQUOTE  fix=%s' % (e['seg'], r['book'], r['chunk'], r['idx'], e['fix'][:60]))
