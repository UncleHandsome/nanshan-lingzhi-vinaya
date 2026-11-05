
# -*- coding: utf-8 -*-
import io, re
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out\02_戒疏\19b_卷四下之一.txt'
raw = io.open(p, encoding='utf-8').read()
print('bytes', len(raw))
print('crlfcrlf', raw.count('\r\n\r\n'), 'lflf', raw.count('\n\n'))
a = [x for x in re.split(r'\r?\n\r?\n', raw) if x.strip()]
print('paras', len(a))
print('first', a[0][:30])
