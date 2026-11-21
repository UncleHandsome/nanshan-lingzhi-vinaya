# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\對話回覆'
rows = []
for f in sorted(os.listdir(D)):
    if not f.endswith('.md') or f == '索引.md':
        continue
    t = io.open(os.path.join(D, f), encoding='utf-8').read()
    ev = re.search(r'- event: (\S+)', t)
    title = ''
    for line in t.splitlines():
        if line.startswith('# ') and not line.startswith('# 對話材料'):
            title = line[2:].strip()
            break
    rows.append((ev.group(1) if ev else '', title[:60], f, len(t)))
rows.sort(key=lambda x: (x[0], x[1], x[2]))
out = ['# 對話材料索引', '', '共 %d 份。' % len(rows), '', '| event | 標題 | 檔案 | 大小 |', '|:--|:--|:--|--:|']
for ev, title, f, n in rows:
    out.append('| %s | %s | [%s](%s) | %d |' % (ev, title, f, f, n))
io.open(os.path.join(D, '索引.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(len(rows))
