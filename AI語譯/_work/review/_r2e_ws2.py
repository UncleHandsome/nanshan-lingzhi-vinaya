# -*- coding: utf-8 -*-
"""r2 精簡工作單：印 resp + 只印被點到的 seq 段（原/材/譯）。
用法: python _r2e_ws2.py 1664 [--all] [--noresp]
  --all     印全部段
  --noresp  不印 resp 全文（只看段）
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
    show_all = '--all' in sys.argv
    noresp = '--noresp' in sys.argv
    for a in args:
        n = int(a)
        rp = os.path.join(RESP, 'resp_%d.txt' % n)
        print('########## resp_%d ##########' % n)
        if not os.path.exists(rp):
            print('<<<RESP MISSING>>>')
            continue
        txt = open(rp, encoding='utf-8').read()
        if not noresp:
            print(txt.rstrip())
        recs = L.parse_review(n)
        cand = re.findall(r'#(\d{1,4})(?![0-9])', txt)
        cand += re.findall(r'【\s*#?(\d{1,4})\s*】', txt)
        cand += re.findall(r'(?<![0-9])(\d{4})(?![0-9])', txt)
        allseq = set(r['seq'] for r in recs)
        allseg = set(r['seg'] for r in recs)
        want = set(int(x) for x in cand if int(x) in allseq or int(x) in allseg)
        cache = {}
        print('\n----- 段 (%d) -----' % len(recs))
        for r in recs:
            if not show_all and r['seq'] not in want and r['seg'] not in want:
                continue
            k = (r['book'], r['chunk'])
            if k not in cache:
                cache[k] = L.Out(*k)
            cur = cache[k].segs[r['seg'] - 1]
            mt = r['trans'] or ''
            rt = difflib.SequenceMatcher(None, norm(mt), norm(cur)).ratio()
            same = (rt > 0.9999)
            print('=== %d-%04d %s/%s#%d%s' % (r['batch'], r['seq'], r['book'], r['chunk'], r['seg'],
                                              '' if same else '  [mat!=out %.4f]' % rt))
            print('原: ' + (r['orig'] or ''))
            if not same:
                print('材: ' + mt)
            print('譯: ' + cur)
        print()


if __name__ == '__main__':
    main()
