# -*- coding: utf-8 -*-
import json, re, difflib

np = json.load(open('AI語譯/_work/review/_g1_np.json', encoding='utf-8'))


def norm(s):
    return s.replace('『', '「').replace('』', '」').replace('“', '「').replace('”', '」')


def deq(t):
    # convert corner quotes to normal only if target has no normal quotes at all
    if '「' not in t and '」' not in t:
        return t.replace('『', '「').replace('』', '」')
    return t


def strip_alt(t):
    t = re.sub(r'（或[：:][^）]*）', '', t)
    t = re.sub(r'（或[^：:）][^）]*）', '', t)
    return t


def find_span(cur, src):
    nc = norm(cur)
    ns = norm(src)
    i = nc.find(ns)
    if i >= 0:
        return i, i + len(ns), 1.0
    # fuzzy: slide window
    L = len(ns)
    best = None
    for w in range(max(4, int(L * 0.6)), int(L * 1.4) + 2):
        for i in range(0, len(nc) - w + 1):
            r = difflib.SequenceMatcher(None, nc[i:i + w], ns).ratio()
            if best is None or r > best[2]:
                best = (i, i + w, r)
                if r > 0.95:
                    return best
    return best


out = open('AI語譯/_work/review/_g1_np_ctx2.txt', 'w', encoding='utf-8')
for x in np:
    if not x['np']:
        continue
    for a, b in x['np']:
        b2 = deq(strip_alt(b))
        sp = find_span(x['cur'], a)
        if not sp or sp[2] < 0.7:
            out.write(x['gid'] + '\tLOW(' + ('%.2f' % sp[2] if sp else 'NA') + ')\t' + a + ' => ' + b2 + '\n')
            continue
        i, j, r = sp
        old = x['cur'][i:j]
        new = b2
        s = max(0, i - 14)
        e = min(len(x['cur']), j + 14)
        out.write(x['gid'] + '\t' + x['cur'][s:i] + '【' + old + '→' + new + '】' + x['cur'][j:e] + '\n')
        x.setdefault('edits', []).append([old, new])
out.close()
json.dump(np, open('AI語譯/_work/review/_g1_np2.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('ok')
