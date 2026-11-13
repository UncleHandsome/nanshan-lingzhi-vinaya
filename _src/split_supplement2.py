# -*- coding: utf-8 -*-
"""用行序狀態機切分：遇到段號就切換檔別，其餘行歸入當前檔。"""
import io, os, re, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, '待跑_審查擋掉7K')
OUT = os.path.join(D, '回覆')
TMP = os.path.join(D, '_回覆_tmp')
if os.path.isdir(TMP):
    import shutil
    shutil.rmtree(TMP)
os.makedirs(TMP)

SRC = ['q1.txt', 'q2.txt', 'qq.txt']
buckets = collections.defaultdict(list)
cur = None
unassigned = 0

for name in SRC:
    p = os.path.join(D, name)
    if not os.path.exists(p):
        continue
    cur = None
    for line in io.open(p, encoding='utf-8', errors='ignore'):
        m = re.search(r'(\d{3,4})-\d{4}', line)
        if m:
            cur = int(m.group(1))
        if cur is None:
            if line.strip():
                unassigned += 1
            continue
        buckets[cur].append(line)

rows = []
for n in sorted(buckets):
    body = ''.join(buckets[n]).strip()
    if len(body) < 30:
        continue
    txt = '# 檔%03d 校閱意見（補跑）\n\n%s\n' % (n, body)
    io.open(os.path.join(TMP, '檔%03d.txt' % n), 'w', encoding='utf-8').write(txt)
    segs = len(set(re.findall(r'(\d{3,4}-\d{4})', txt)))
    rows.append((n, len(txt), segs))

# 併入既有 330
kept330 = os.path.join(OUT, '檔330.txt')
if os.path.exists(kept330):
    import shutil
    shutil.copy2(kept330, os.path.join(TMP, '檔330.txt'))
    segs = len(set(re.findall(r'(\d{3,4}-\d{4})', io.open(kept330, encoding='utf-8').read())))
    rows.append((330, os.path.getsize(kept330), segs))

rows.sort()
with io.open(os.path.join(TMP, 'index.tsv'), 'w', encoding='utf-8') as f:
    f.write('檔號\t字數\t段數\n')
    for n, ln, segs in rows:
        f.write('%d\t%d\t%d\n' % (n, ln, segs))

# 換掉舊目錄
import shutil
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
shutil.move(TMP, OUT)

print('切成', len(rows), '份')
print('檔號：', ', '.join(str(r[0]) for r in rows))
print('開頭未歸屬行數', unassigned)
