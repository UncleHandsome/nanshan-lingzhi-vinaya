# -*- coding: utf-8 -*-
"""Verify whether each recheck item's fix content is present in the current paragraph,
stripping opinion wrapper words that make find_unapplied's fix[:8] test fail."""
import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
LEAD = re.compile(r'^【[^】]{1,6}】')

def norm(s):
    s = LEAD.sub('', s or '')
    return re.sub(r'[「」『』（）()：:，,。、；;！!？?\s]', '', s)

def paras(p):
    return [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]

ids = [l.strip() for l in io.open(os.path.join(B, 'AI語譯', '_work', 'recheckq', '01.txt'), encoding='utf-8') if l.strip()]
w = io.open(os.path.join(B, '_src', '_tmp_check.txt'), 'w', encoding='utf-8')
for cid in ids:
    book, key = cid.split('__', 1)
    ps = paras(os.path.join(B, 'AI語譯', 'out', book, key + '.txt'))
    items = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'recheck', cid + '.json'), encoding='utf-8'))
    w.write('\n### %s  paras=%d items=%d\n' % (cid, len(ps), len(items)))
    for it in items:
        seg = int(it['seg'])
        body = norm(ps[seg-1])
        # strip wrapper: take text inside last 「...」 of fix, plus whole fix
        cands = []
        for m in re.findall(r'「([^」]+)」', it['fix'] or ''):
            cands.append(m)
        cands.append(re.sub(r'^(應譯為|譯為|改為|可於.*?明譯為)', '', it['fix'] or ''))
        hit = []
        for c in cands:
            nc = norm(c)
            # test longest substring of nc (>=8 chars) present in body
            found = 0
            for L in range(min(len(nc), 24), 7, -1):
                ok = any(nc[i:i+L] in body for i in range(0, len(nc)-L+1))
                if ok:
                    found = L
                    break
            hit.append((c[:40], len(nc), found))
        w.write('seg %d kind=%s\n' % (seg, it.get('kind')))
        w.write('  quote: %s\n' % it.get('quote'))
        w.write('  fix  : %s\n' % it.get('fix'))
        w.write('  cur  : %s\n' % (it.get('cur') or '')[:120])
        for c, ln, found in hit:
            w.write('  cand "%s" (norm len %d) longest-present=%d %s\n' % (c, ln, found, 'HIT' if found >= 10 else 'MISS'))
        # does the classical quote still appear verbatim in body?
        w.write('  quote-in-body=%s\n' % (norm(it['quote']) in body))
w.close()
print('done')
