# -*- coding: utf-8 -*-
"""r2 資持記 1263-1330 工作單：把回應切條，配對到 out 現行譯文句子。
用法：python _r2k_ws.py 1263 1270 [--full] [--cap 400]
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _r2j_lib as L

MAP = L.load_map()
IDX = {}
CHSEGS = {}
for x in MAP:
    IDX[(x['resp'], int(x['uniq']))] = x
    CHSEGS.setdefault(x['chunk'], set()).add(int(x['seg']))

_cache = {}


def out(chunk):
    if chunk not in _cache:
        _cache[chunk] = L.load_out(chunk)['segs']
    return _cache[chunk]


def sents(s):
    return [x for x in re.split(r'(?<=[。！？；])', s) if x.strip()]


def find(text, q):
    for x in sents(text):
        if q in x:
            return x
    return None


def clean(s):
    s = s.replace('**', '').replace('`', '')
    s = re.sub(r'^[>\s\-•*]+', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def quotes(s):
    return [q for q in re.findall(r'[「『]([^」』]{2,50})[」』]', s)]


REF_PATTERNS = [
    re.compile(r'【(\d{4})】'),
    re.compile(r'(\d{4})-(\d{4})'),
    re.compile(r'#(\d{1,2})(?!\d)'),
]


def refs_of(block, n):
    out = []
    for m in re.finditer(r'【(\d{4})】', block):
        out.append(int(m.group(1)))
    for m in re.finditer(r'(?<![\d-])%d-(\d{4})' % n, block):
        out.append(int(m.group(1)))
    for m in re.finditer(r'(?<![\d-])#(\d{1,2})(?!\d)', block):
        out.append(int(m.group(1)))
    return [x for x in dict.fromkeys(out) if x]


def blocks(txt):
    raw = re.split(r'\n\s*\n', txt)
    out = []
    for b in raw:
        lines = [clean(x) for x in b.split('\n')]
        lines = [x for x in lines if x and x != '---']
        if not lines:
            continue
        out.append(' '.join(lines))
    return out


def resolve(n, blk):
    """回傳 [(chunk, seg)]，以 map 為準。"""
    cands = []
    for u in refs_of(blk, n):
        rec = IDX.get((n, u))
        if rec:
            cands.append((rec['chunk'], int(rec['seg'])))
    if not cands:
        qs = quotes(blk)
        if qs:
            best = (0, None)
            for (r, u), rec in IDX.items():
                if r != n:
                    continue
                t = out(rec['chunk'])[int(rec['seg']) - 1]
                c = sum(1 for q in qs if q in t)
                if c > best[0]:
                    best = (c, (rec['chunk'], int(rec['seg'])))
            if best[1]:
                cands.append(best[1])
    return list(dict.fromkeys(cands))


def show_block(n, blk, cap, full):
    tg = resolve(n, blk)
    print(' C: ' + blk[:cap] + ('…' if len(blk) > cap else ''))
    if not tg:
        print(' ??: 未定位')
        return
    for chunk, seg in tg:
        t = out(chunk)[seg - 1]
        rec = None
        for (r, u), x in IDX.items():
            if r == n and x['chunk'] == chunk and int(x['seg']) == seg:
                rec = x
                break
        print(' @%s#%d' % (chunk.split('_')[0], seg))
        if full:
            print('  T: ' + t)
            if rec:
                print('  O: ' + rec['orig'])
            continue
        shown = False
        for q in quotes(blk):
            s = find(t, q)
            if s:
                print('  T: ' + s[:260])
                shown = True
                break
        if not shown:
            print('  T: ' + t[:240])
        if rec:
            for q in quotes(blk):
                s = find(rec['orig'], q)
                if s:
                    print('  O: ' + s[:200])
                    break


def main(argv):
    full = '--full' in argv
    cap = 400
    if '--cap' in argv:
        i = argv.index('--cap')
        cap = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    nums = [int(a) for a in argv if a.isdigit()]
    a, b = nums[0], nums[-1]
    for n in range(a, b + 1):
        txt = L.resp_text(n)
        print('\n===== %d =====' % n)
        if txt is None:
            print(' (無回應)')
            continue
        bs = blocks(txt)
        for blk in bs:
            show_block(n, blk, cap, full)


if __name__ == '__main__':
    main(sys.argv[1:])
