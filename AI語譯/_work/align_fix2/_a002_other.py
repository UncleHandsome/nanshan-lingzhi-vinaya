# -*- coding: utf-8 -*-
import json, io, os

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
W = os.path.join(base, 'AI語譯', '_work')
out = []

for rel in ['align_ys/029.json', 'align_ys/out_029.json', 'align_ai/029.json']:
    p = os.path.join(W, rel)
    if not os.path.exists(p):
        out.append('MISSING ' + rel); continue
    d = json.load(io.open(p, encoding='utf-8'))
    out.append('==== %s ==== type=%s' % (rel, type(d).__name__))
    if isinstance(d, dict):
        out.append('keys: ' + repr(list(d.keys())))
        for k, v in d.items():
            if isinstance(v, list):
                out.append('  %s: list len=%d' % (k, len(v)))
                for x in v[:3]:
                    out.append('    ' + json.dumps(x, ensure_ascii=False)[:200])
            else:
                out.append('  %s: %s' % (k, json.dumps(v, ensure_ascii=False)[:300]))
    elif isinstance(d, list):
        out.append('list len=%d' % len(d))
        for x in d[:3]:
            out.append('  ' + json.dumps(x, ensure_ascii=False)[:300])

io.open(os.path.join(os.path.dirname(__file__), '_a002_other.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
