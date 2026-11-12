# -*- coding: utf-8 -*-
"""r2 精簡摘要：只列強意見候選。用法: python _zx3_dg.py 1082 ..."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

RESP = os.path.join(L.ROOT, 'batch_qwen', 'r2')
QUOT = re.compile(r'「([^」]{2,60})」')
STRONG = re.compile(r'(❗|★|❌|⚠|P0|必須|應改|應作|錯|誤|相反|反了|顛倒|漏譯|漏掉|不成對|術語|專名|程序|增譯|衍文|脫文|存疑|待核)')
WEAK = re.compile(r'(可保留|無問題|正確無誤|譯得準確|已經正確|✔)')
SEQPATS = [
    re.compile(r'【\s*(?:\d{3,4}-)?(\d{1,4})\s*】'),
    re.compile(r'#{2,4}\s*(?:[\u4e00-\u9fff]+/[^\s#]*?#)?\s*(\d{1,4})\s*(?:｜|$)'),
    re.compile(r'(?<![\d])#(\d{1,2})(?![\d])'),
    re.compile(r'段\s*(\d{1,2})(?![\d])'),
]


def clean(s):
    return s.replace('**', '').replace('*', '').strip()


def quoted_pairs(item):
    return [clean(q) for q in QUOT.findall(item) if clean(q)]


def find_old(item, cur):
    best = None
    for q in quoted_pairs(item):
        if q in cur and len(q) >= 2:
            if best is None or len(q) > len(best):
                best = q
    return best


NEWPAT = re.compile(r'(?:建議(?:改為|作|改成)?|應作|應改為|應改|宜作|宜改為|宜改|改作|改為|改成|作)[：:，,、\s]*「([^」]+)」')


def find_new(item, old, cur, orig):
    m = NEWPAT.search(item)
    cands = []
    if m:
        cands.append(m.group(1))
    qs = quoted_pairs(item)
    if old in qs:
        i = qs.index(old)
        cands.extend(qs[i + 1:])
    cands.extend(qs)
    for c in cands:
        c = clean(c)
        if not c or c == old:
            continue
        if c in cur or c in (orig or ''):
            continue
        if '…' in c or len(c) > 40:
            continue
        return c
    return None


def main():
    hard = '--hard' in sys.argv
    for a in [x for x in sys.argv[1:] if not x.startswith('--')]:
        n = int(a)
        rp = os.path.join(RESP, 'resp_%d.txt' % n)
        print('##%d' % n)
        if not os.path.exists(rp):
            print('MISSING')
            continue
        txt = open(rp, encoding='utf-8').read()
        recs = L.parse_review(n)
        outs = {}
        for r in recs:
            k = (r['book'], r['chunk'])
            if k not in outs:
                outs[k] = L.Out(*k)
        seqs = [r['seq'] for r in recs]
        seq = None
        items = []
        cur = []
        for ln in txt.split('\n'):
            s = ln.rstrip('\r')
            found = None
            for p in SEQPATS:
                m = p.search(s)
                if m:
                    v = int(m.group(1))
                    if v in seqs or (1 <= v <= 99):
                        found = v
                        break
            isnew = bool(re.match(r'^\s*(?:\d{1,2}[\.、]|[*\-•]|❗|⚠|✏|✅|###|##\s*【)', s))
            if isnew and cur:
                items.append((seq, '\n'.join(cur)))
                cur = []
            if found is not None:
                seq = found if found in seqs else seq
            if s.strip():
                cur.append(s)
        if cur:
            items.append((seq, '\n'.join(cur)))
        for sq, it in items:
            if sq is None or sq not in seqs:
                continue
            if WEAK.search(it) and not re.search(r'(❗|★|❌|⚠|錯|誤|相反|顛倒|漏譯)', it):
                continue
            if not STRONG.search(it):
                continue
            if hard and not re.search(r'(❗|★|❌|相反|顛倒|術語|程序|主語|範圍|因果|漏譯|漏「)', it):
                continue
            r = [x for x in recs if x['seq'] == sq][0]
            cur_t = r['trans'] or '' 
            old = find_old(it, cur_t)
            if not old:
                continue
            new = find_new(it, old, cur_t, r['orig'])
            why = re.sub(r'\s+', ' ', it)[:40 if hard else 64]
            print('%d|%d|%d|%s||%s|%s' % (n, sq, r['seg'], old, new or '?', why))
        print()


if __name__ == '__main__':
    main()
