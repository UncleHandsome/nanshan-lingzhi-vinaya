# -*- coding: utf-8 -*-
import os, io, re, difflib
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for chunk in ('07b_卷中之三', '07c_卷中之三'):
    old = io.open(os.path.join(B, '歸檔', '022修正前', 'AI語譯', 'out', '01_行事鈔', chunk + '.txt'), encoding='utf-8', newline='').read()
    new = io.open(os.path.join(B, 'AI語譯', 'out', '01_行事鈔', chunk + '.txt'), encoding='utf-8', newline='').read()
    print('=' * 10, chunk)
    print('CRLF old/new', old.count('\r\n'), new.count('\r\n'), 'endswith', repr(old[-6:]), repr(new[-6:]))
    po = [x for x in re.split(r'\r?\n\r?\n', old) if x.strip()]
    pn = [x for x in re.split(r'\r?\n\r?\n', new) if x.strip()]
    print('paras', len(po), len(pn))
    assert len(po) == len(pn)
    for i, (a, b) in enumerate(zip(po, pn), 1):
        if a != b:
            sm = difflib.SequenceMatcher(None, a, b)
            print('  #%d chars %d→%d' % (i, len(a), len(b)))
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag != 'equal':
                    print('    %s: %r -> %r' % (tag, a[i1:i2], b[j1:j2]))
    # 非段落（頭尾空白）是否一致
    print('prefix same', old[:old.index(po[0])] == new[:new.index(pn[0])])
