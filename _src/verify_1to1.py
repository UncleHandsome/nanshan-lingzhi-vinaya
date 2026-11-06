# -*- coding: utf-8 -*-
"""全 328 檔驗證：原文段數 vs 白話段數（允許段數變動，但必須 1:1）"""
import io, os, re, json, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PAIRS = [('01_行事鈔', '01_行事鈔'), ('02_戒疏', '02_戒疏'), ('03_業疏', '03_業疏'),
         ('資持記_細分', '資持記'), ('04_比丘尼鈔', '04_比丘尼鈔'), ('05_拾毗尼義鈔', '05_拾毗尼義鈔')]
SNAP = os.path.join(B, 'AI語譯', '_work', 'para_counts.json')

counts = {}
bad = []
files = 0
for sd, td in PAIRS:
    S = os.path.join(B, 'TXT_分卷', sd)
    T = os.path.join(B, 'AI語譯', 'out', td)
    if not os.path.isdir(S):
        continue
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        tp = os.path.join(T, k + '.txt')
        if not os.path.exists(tp):
            sp0 = [x for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
            if not sp0:
                continue
            bad.append((sd, k, '無譯文檔', len(sp0), 0))
            continue
        sp = [x for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        files += 1
        counts['%s/%s' % (sd, k)] = [len(sp), len(tt)]
        if len(sp) != len(tt):
            bad.append((sd, k, '段數不符', len(sp), len(tt)))
        if any(not x.strip() for x in sp) or any(not x.strip() for x in tt):
            bad.append((sd, k, '有空段', len(sp), len(tt)))

old = {}
if os.path.exists(SNAP):
    old = json.load(io.open(SNAP, encoding='utf-8'))
changed = []
for k, v in counts.items():
    if k in old and old[k] != v:
        changed.append((k, old[k], v))

print('檢查檔案數', files)
print('不符', len(bad))
for b in bad[:10]:
    print('  ', b)
print('段數變動檔數', len(changed))
for c in changed:
    print('  %-28s %s → %s' % (c[0], c[1], c[2]))
json.dump(counts, io.open(SNAP, 'w', encoding='utf-8'), ensure_ascii=False)
print('已更新快照', SNAP)
