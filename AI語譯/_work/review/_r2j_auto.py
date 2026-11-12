# -*- coding: utf-8 -*-
"""auto.py：對指定檔，抽取回應中的「原文引語→現譯引語」，自動找出原譯兩邊的句子。
用法：python _r2j_auto.py 1223 1224 ..."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2j_lib as L
from _r2j_digest import digest, seg_refs, clean

MAP = L.load_map()
RESP2SEG = {}
for x in MAP:
    RESP2SEG[(x['resp'], int(x['uniq']))] = x


def sents(s):
    return [x for x in re.split(r'(?<=[。！？；])', s) if x.strip()]


def find_sent(text, q):
    for x in sents(text):
        if q and q in x:
            return x
    return None


def quotes(s):
    return re.findall(r'[「『]([^」』]{2,40})[」』]', s)


def show(n):
    items = digest(n)
    if not items:
        return
    print('\n===== %d =====' % n)
    for seg, text in items:
        if seg is None:
            refs = seg_refs(text)
            seg = refs[0] if refs else None
        if seg is None:
            # 以引語在全文各段中出現的次數定位
            qs0 = quotes(text)
            best = (0, None)
            for x in MAP:
                if x['resp'] != n:
                    continue
                cnt = sum(1 for q in qs0 if q in x['trans'] or q in x['orig'])
                if cnt > best[0]:
                    best = (cnt, int(x['uniq']))
            if best[1]:
                seg = best[1]
        if seg is None:
            print('  ??', text[:120])
            continue
        rec = RESP2SEG.get((n, seg))
        if not rec:
            print('  ?? no map', n, seg, text[:80])
            continue
        chunk, rseg = rec['chunk'], rec['seg']
        t = L.load_out(chunk)['segs'][rseg - 1]
        qs = quotes(text)
        ts = None
        for q in qs[1:] + qs[:1]:
            ts = find_sent(t, q)
            if ts:
                break
        os_ = None
        for q in qs:
            os_ = find_sent(rec['orig'], q)
            if os_:
                break
        print('  [%s#%d] %s' % (chunk.split('_')[0], rseg, re.sub(r'\s+', ' ', text)[:100]))
        if os_:
            print('    O:', os_[:180])
        if ts:
            print('    T:', ts[:220])
        elif qs:
            print('    T: (無對應句) 引語', qs[:3])


if __name__ == '__main__':
    for a in sys.argv[1:]:
        show(int(a))
