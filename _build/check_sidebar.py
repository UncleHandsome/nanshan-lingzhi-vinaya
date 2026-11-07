# -*- coding: utf-8 -*-
"""全面檢查側欄實作：nav.json 條目 vs 頁面錨點"""
import io, os, re, json, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')
nav = json.load(io.open(os.path.join(SITE, 'nav.json'), encoding='utf-8'))
problems = []
stats = []
for bk in nav['books']:
    out = bk['out']
    for v in bk['vols']:
        page = os.path.join(SITE, out, v['v'] + '.html')
        if not os.path.exists(page):
            problems.append((out, v['v'], '頁面不存在'))
            continue
        h = io.open(page, encoding='utf-8').read()
        ids = re.findall(r'id="(p\d+)"', h)
        idset = set(ids)
        dup = [x for x in idset if ids.count(x) > 1]
        missing = [s[0] for s in v.get('secs', []) if s[0] not in idset]
        orphan = sorted(idset - set(s[0] for s in v.get('secs', [])))
        stats.append((out, v['v'], len(v.get('secs', [])), len(idset)))
        if missing:
            problems.append((out, v['v'], '側欄連結無對應錨點: ' + ','.join(missing[:5])))
        if dup:
            problems.append((out, v['v'], '重複錨點: ' + ','.join(dup[:5])))
print('檢查卷數', len(stats))
print('問題', len(problems))
for p in problems[:20]:
    print('  ', p)
print('\n各書卷數／錨點數：')
for s in stats:
    if s[0] in ('yichao', 'jieshu', 'yeshu', 'nicao'):
        print('  %-10s %-6s 側欄 %2d 錨點 %2d' % s)
