# -*- coding: utf-8 -*-
import os, io, re, difflib
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

def parse(path):
    t = io.open(path, encoding='utf-8').read()
    i = t.index('# 材料開始')
    head = t[:i]
    body = t[i + len('# 材料開始'):]
    bs = re.split(r'\n\n(?=【022-\d{4}】)', body.strip())
    out = []
    for b in bs:
        m = re.match(r'【(022-\d{4})】01_行事鈔/(\S+?)#(\d+)\n【原文】(.*?)\n【譯文】(.*)$', b.strip(), re.S)
        assert m, b[:60]
        out.append(m.groups())
    return head, out

old_head = None
old_all = []
for n in range(1, 6):
    h, bs = parse(os.path.join(B, '測試_022_五分之一', '校閱_022_%d.txt' % n))
    old_all += bs
    if old_head is None:
        old_head = h
new_head = None
new_all = []
for n in range(1, 6):
    h, bs = parse(os.path.join(B, '測試_022_修正版', '校閱_022_%d.txt' % n))
    new_all += bs
    print('file', n, 'segs', len(bs), 'lines', io.open(os.path.join(B, '測試_022_修正版', '校閱_022_%d.txt' % n), encoding='utf-8').read().count('\n'))
    if new_head is None:
        new_head = h
print('head identical:', old_head == new_head)
print('segs', len(old_all), len(new_all))
print('ids same:', [x[0] for x in old_all] == [x[0] for x in new_all])
diff = 0
for a, b in zip(old_all, new_all):
    assert a[0] == b[0] and a[1] == b[1] and a[2] == b[2]
    if a[3] != b[3]:
        print('!!! 原文 changed', a[0])
    if a[4] != b[4]:
        diff += 1
        print('譯文 changed', a[0], 'chars %d→%d' % (len(a[4]), len(b[4])))
print('changed trans segs:', diff)
