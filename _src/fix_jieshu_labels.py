import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, 'AI語譯', 'out', '02_戒疏')
FIRST = re.compile(r'^(【(?:律文|註文|疏文|記文|律|註|疏|記)】)(【[^】]{1,10}】)')
LEAD = re.compile(r'^(【[^】]{1,6}】)+')

n = 0
files = 0
for f in sorted(os.listdir(T)):
    if not f.endswith('.txt'):
        continue
    p = os.path.join(T, f)
    ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
    out = []
    changed = False
    for seg in ps:
        new = seg
        m = FIRST.match(seg)
        if m:
            new = m.group(1) + seg[m.end():].lstrip()
            changed = True
            n += 1
        out.append(new)
    if changed:
        io.open(p, 'w', encoding='utf-8').write('\n\n'.join(out) + '\n')
        files += 1
print('collapsed', n, 'paras in', files, 'files')

# 剩下的（無標準首標籤）只報告
rest = {}
for f in sorted(os.listdir(T)):
    if not f.endswith('.txt'):
        continue
    for i, seg in enumerate([x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, f), encoding='utf-8').read()) if x.strip()], 1):
        m = re.match(r'^【[^】]{1,8}】\s*【', seg)
        if m:
            rest.setdefault(seg[:16], 0)
            rest[seg[:16]] += 1
print('remaining double-label shapes:', len(rest))
for k, v in sorted(rest.items(), key=lambda x: -x[1])[:10]:
    print('   ', k, v)
