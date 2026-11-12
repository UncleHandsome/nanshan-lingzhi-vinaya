# -*- coding: utf-8 -*-
"""r2 1649-1760 工作單：印 resp 全文 + 該檔材料各段（原文／材料譯文／out 現行）。
用法: python _r2e_ws.py 1649 [1650 ...] [--diff] [--orig]
  --diff  只印材料譯文與現行有差異的段（含上下文）
  --orig  一併印原文
"""
import os, sys, io, re, difflib
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

RESP = os.path.join(L.ROOT, 'batch_qwen', 'r2')


def norm(s):
    return ''.join(ch for ch in (s or '') if ch not in ' \t\r\n')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    only_diff = '--diff' in sys.argv
    show_orig = '--orig' in sys.argv
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
        cache = {}
        print('\n----- 段 (%d) -----' % len(recs))
        for r in recs:
            k = (r['book'], r['chunk'])
            if k not in cache:
                cache[k] = L.Out(*k)
            cur = cache[k].segs[r['seg'] - 1]
            mt = r['trans'] or ''
            rt = difflib.SequenceMatcher(None, norm(mt), norm(cur)).ratio()
            same = (rt > 0.9999)
            if only_diff and same:
                continue
            print('=== %d-%04d %s/%s#%d%s' % (r['batch'], r['seq'], r['book'], r['chunk'], r['seg'],
                                              '' if same else '  [mat!=out %.4f]' % rt))
            if show_orig:
                print('原: ' + (r['orig'] or ''))
            if not same:
                print('材: ' + mt)
            print('譯: ' + cur)
        print()


if __name__ == '__main__':
    main()
