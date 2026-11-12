# -*- coding: utf-8 -*-
"""工作單（r2 1533-1648）：印 resp 全文 + 被引用的段（原文＋現行譯文）。
用法: python _r2d_ws.py 1533 [1534 ...] [--all]
"""
import os, sys, re, io
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

RESP = os.path.join(L.ROOT, 'batch_qwen', 'r2')


def cited(txt):
    segs, seqs = set(), set()
    for m in re.finditer(r'【\d{4}-(\d{4})】', txt):
        seqs.add(int(m.group(1)))
    for m in re.finditer(r'\d{4}-(\d{4})', txt):
        seqs.add(int(m.group(1)))
    for m in re.finditer(r'【#(\d{1,3})】', txt):
        segs.add(int(m.group(1)))
    for m in re.finditer(r'(?m)^#{2,4}\s*#?(\d{1,3})\s*(?:[（(]|\s|$)', txt):
        segs.add(int(m.group(1)))
    for m in re.finditer(r'#(\d{1,3})\b', txt):
        segs.add(int(m.group(1)))
    for m in re.finditer(r'段\s*(\d{1,3})\b', txt):
        segs.add(int(m.group(1)))
    return segs, seqs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    show_all = '--all' in sys.argv
    for a in args:
        n = int(a)
        rp = os.path.join(RESP, 'resp_%d.txt' % n)
        print('########## resp_%d ##########' % n)
        if not os.path.exists(rp):
            print('<<<RESP MISSING>>>')
            continue
        txt = open(rp, encoding='utf-8').read()
        print(txt.rstrip())
        recs = L.parse_review(n)
        wantseg, wantseq = cited(txt)
        if not wantseg and not wantseq:
            show_all = True
        cache = {}
        print('\n----- 段 -----')
        for r in recs:
            hit = show_all or (r['seg'] in wantseg) or (r['seq'] in wantseq)
            if not hit:
                continue
            key = (r['book'], r['chunk'])
            if key not in cache:
                cache[key] = L.Out(*key)
            cur = cache[key].segs[r['seg'] - 1]
            print('=== %d-%04d %s/%s#%d' % (r['batch'], r['seq'], r['book'], r['chunk'], r['seg']))
            print('原: ' + (r['orig'] or ''))
            print('譯: ' + cur)
        print()


if __name__ == '__main__':
    main()
