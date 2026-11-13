# -*- coding: utf-8 -*-
"""把 q1/q2/qq 的回覆依檔號切開，存成 回覆/檔NNN.txt。"""
import io, os, re, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, '待跑_審查擋掉7K')
OUT = os.path.join(D, '回覆')
os.makedirs(OUT, exist_ok=True)

SRC = ['q1.txt', 'q2.txt', 'qq.txt']
buckets = collections.defaultdict(list)
unassigned = []

for name in SRC:
    p = os.path.join(D, name)
    if not os.path.exists(p):
        print('缺', name)
        continue
    t = io.open(p, encoding='utf-8', errors='ignore').read()
    # 以 markdown 標題或編號項目為界切成塊
    blocks = re.split(r'\n(?=#{2,4}\s|\s*[-*]\s+\*\*|\d+[.、]\s)', t)
    for b in blocks:
        b = b.strip()
        if len(b) < 20:
            continue
        ids = re.findall(r'(\d{3,4})-\d{4}', b)
        if not ids:
            unassigned.append((name, b[:60]))
            continue
        # 取出現最多的檔號
        f = collections.Counter(ids).most_common(1)[0][0]
        buckets[int(f)].append(b)

rows = []
for n in sorted(buckets):
    txt = '# 檔%03d 校閱意見（來源：補跑）\n\n' % n + '\n\n---\n\n'.join(buckets[n])
    p = os.path.join(OUT, '檔%03d.txt' % n)
    io.open(p, 'w', encoding='utf-8').write(txt)
    segs = len(set(re.findall(r'(\d{3,4}-\d{4})', txt)))
    rows.append((n, len(txt), segs))

with io.open(os.path.join(OUT, 'index.tsv'), 'w', encoding='utf-8') as f:
    f.write('檔號\t字數\t段數\n')
    for n, ln, segs in rows:
        f.write('%d\t%d\t%d\n' % (n, ln, segs))

print('切成', len(rows), '份')
print('檔號：', ', '.join(str(r[0]) for r in rows))
print('未歸檔片段', len(unassigned))
for s in unassigned[:5]:
    print('  ', s)
