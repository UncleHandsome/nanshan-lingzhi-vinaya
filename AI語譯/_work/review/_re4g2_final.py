# -*- coding: utf-8 -*-
import io, json
raw = open(r'AI語譯/_work/review/fix_re4_g2.tsv', 'rb').read()
print('BOM', raw[:3] == b'\xef\xbb\xbf', 'CR', b'\r' in raw, 'ends_nl', raw.endswith(b'\n'))
txt = raw.decode('utf-8')
lines = txt.split('\n')[:-1]
print('lines', len(lines), 'first field', repr(lines[0].split('\t')[0]))
lens = [len(l.split('\t')[3]) for l in lines]
print('len min/max', min(lens), max(lens))
print('segs', [l.split('\t')[2] for l in lines[:5]])
