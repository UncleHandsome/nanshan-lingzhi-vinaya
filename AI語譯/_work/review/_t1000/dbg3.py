# -*- coding: utf-8 -*-
import io, re, json, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
lines = io.open(os.path.join(B, '校閱_單段_前1000個校閱結果.md'), encoding='utf-8').read().split('\n')
re_head = re.compile(r'^(?:###\s*)?(.+?/[\w\u4e00-\u9fff]+#\d+)\s*(?:｜\s*(P\d)\s*｜\s*(.*))?$')
for n in (42, 49, 74, 81, 5602, 7179, 7244):
    m = re_head.match(lines[n-1])
    print(n, bool(m), m.groups() if m else '')
d = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'entries.json'), encoding='utf-8'))
print('all', len(d['all']))
for e in d['all']:
    print(e['gid'], e['level'], e['cat'], '|', (e['problem'] or e['doubt'])[:30])
