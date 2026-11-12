# -*- coding: utf-8 -*-
"""批次 dump：resp 全文（壓縮）＋ 該檔各段錨點。用法：
python _r2i_dump.py 1181 1190 [--noanchor]
輸出 _r2i_batch_<a>_<b>.md
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RD = os.path.join(ROOT, 'batch_qwen', 'r2')
MAP = json.load(open(os.path.join(HERE, '_r2i_map.json'), encoding='utf-8'))
BY = {}
for r in MAP:
    BY.setdefault(r['resp'], []).append(r)


def clean(s):
    out = []
    for ln in s.split('\n'):
        t = ln.rstrip()
        if not t.strip():
            continue
        if re.fullmatch(r'\s*[-–—_=]{3,}\s*', t):
            continue
        if re.match(r'^\s*\|?[\s:|-]+\|?\s*$', t) and '-' in t:
            continue
        t = t.replace('**', '').replace('__', '')
        t = re.sub(r'^\s*#{1,6}\s*', '', t)
        t = re.sub(r'^[>\s]+', '', t)
        # 表格：| a | b | -> a｜b
        if t.startswith('|'):
            cells = [c.strip() for c in t.strip('|').split('|')]
            t = '｜'.join(cells)
        out.append(t)
    return '\n'.join(out)


def main():
    a, b = int(sys.argv[1]), int(sys.argv[2])
    noanchor = '--noanchor' in sys.argv
    buf = []
    raw = comp = 0
    for n in range(a, b + 1):
        p = os.path.join(RD, 'resp_%d.txt' % n)
        if not os.path.exists(p):
            buf.append('########## resp_%d （缺檔） ##########' % n)
            continue
        s = open(p, encoding='utf-8').read()
        raw += len(s)
        c = clean(s)
        comp += len(c)
        buf.append('########## resp_%d ##########' % n)
        if not noanchor:
            segs = BY.get(n, [])
            buf.append('[檔內段：' + '、'.join('%s(%s#%d)' % (r['uniq'][-4:], r['chunk'], r['seg']) for r in segs) + ']')
        buf.append(c)
        buf.append('')
    txt = '\n'.join(buf)
    out = os.path.join(HERE, '_r2i_batch_%d_%d.md' % (a, b))
    open(out, 'w', encoding='utf-8').write(txt)
    print('raw=%d comp=%d ratio=%.2f  -> %s' % (raw, comp, comp / max(1, raw), out))


main()
