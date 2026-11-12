# -*- coding: utf-8 -*-
"""r2 超精簡工作單：只抽 resp 中含段號的意見塊 + 被點段現行譯文。
用法: python _r2e_ws3.py 1664 [--full] [--max N]
"""
import os, sys, io, re, difflib
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

RESP = os.path.join(L.ROOT, 'batch_qwen', 'r2')
REF = re.compile(r'(?:#\s*\d{1,4}|【\s*\d{1,4}\s*】|(?<![0-9])\d{4}(?![0-9]))')


def norm(s):
    return ''.join(ch for ch in (s or '') if ch not in ' \t\r\n')


def clean(s):
    s = re.sub(r'\*\*|__|`|^>\s?', '', s)
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    full = '--full' in sys.argv
    cap = 340
    maxb = 24
    for a in args:
        n = int(a)
        rp = os.path.join(RESP, 'resp_%d.txt' % n)
        print('########## resp_%d ##########' % n)
        if not os.path.exists(rp):
            print('<<<RESP MISSING>>>')
            continue
        txt = open(rp, encoding='utf-8').read()
        blocks = [b for b in re.split(r'\n\s*\n', txt) if b.strip()]
        keep = []
        for b in blocks:
            if not REF.search(b):
                continue
            cb = clean(b)
            if not re.search(r'建議|→|應|宜|改|譯|錯|誤|疑|當作|可作', cb):
                continue
            if len(cb) > cap:
                cb = cb[:cap] + '…'
            keep.append(cb)
            if len(keep) >= maxb:
                break
        print('\n'.join('· ' + x for x in keep))
        recs = L.parse_review(n)
        cand = re.findall(r'#(\d{1,4})(?![0-9])', txt)
        cand += re.findall(r'【\s*#?(\d{1,4})\s*】', txt)
        cand += re.findall(r'(?<![0-9])(\d{4})(?![0-9])', txt)
        allseq = set(r['seq'] for r in recs)
        allseg = set(r['seg'] for r in recs)
        want = set(int(x) for x in cand if int(x) in allseq or int(x) in allseg)
        cache = {}
        print('----- 段 %d (%s) -----' % (len(recs), '%d-%d' % (recs[0]['seg'], recs[-1]['seg'])))
        for r in recs:
            if not full and r['seq'] not in want and r['seg'] not in want:
                continue
            k = (r['book'], r['chunk'])
            if k not in cache:
                cache[k] = L.Out(*k)
            cur = cache[k].segs[r['seg'] - 1]
            mt = r['trans'] or ''
            rt = difflib.SequenceMatcher(None, norm(mt), norm(cur)).ratio()
            same = (rt > 0.9999)
            print('=== #%d（seq%d）#%d%s' % (r['seq'], r['seq'], r['seg'],
                                            '' if same else '  [材異 %.4f]' % rt))
            print('原: ' + (r['orig'] or ''))
            if not same:
                print('材: ' + mt)
            print('譯: ' + cur)
        print()


if __name__ == '__main__':
    main()
