# -*- coding: utf-8 -*-
"""r7k 上四b helpers: parse 校閱材料 / out chunks, diff, apply."""
import re, sys, json, io, os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..', '..', '..'))
MAT = os.path.join(ROOT, '校閱_7K')
OUT = os.path.join(ROOT, 'AI語譯', 'out', '資持記')

SEG_RE = re.compile(r'【(\d{4}-\d{4})】資持記/([^\s#]+)#(\d+)\s*\n【原文】(.*?)\n【譯文】(.*?)(?=\n\n【|\n\n\Z|\Z)', re.S)

def load_material(n):
    p = os.path.join(MAT, f'校閱_{n}.txt')
    t = open(p, encoding='utf-8').read()
    segs = []
    # split by segment headers
    parts = re.split(r'\n(?=【\d{4}-\d{4}】)', t)
    for pt in parts:
        m = re.match(r'【(\d{4}-\d{4})】資持記/([^\s#]+)#(\d+)\s*\n【原文】(.*?)\n【譯文】(.*)\Z', pt.strip('\n'), re.S)
        if m:
            segs.append({'sid': m.group(1), 'chunk': m.group(2), 'idx': int(m.group(3)),
                         'src': m.group(4).strip(), 'tr': m.group(5).strip()})
    return segs

def load_out(chunk):
    p = os.path.join(OUT, chunk + '.txt')
    raw = open(p, encoding='utf-8-sig', newline='').read()
    crlf = '\r\n' in raw
    txt = raw.replace('\r\n', '\n')
    paras = txt.split('\n\n')
    return raw, paras, crlf

def norm(s):
    return re.sub(r'\s+', '', s)

def diff_range(nums):
    for n in nums:
        segs = load_material(n)
        for s in segs:
            raw, paras, crlf = load_out(s['chunk'])
            cur = paras[s['idx']-1] if s['idx']-1 < len(paras) else '<MISSING>'
            same = norm(cur) == norm(s['tr'])
            print(f"{s['sid']}\t{s['chunk']}#{s['idx']}\t{'SAME' if same else 'DIFF'}\tmat={len(s['tr'])}\tcur={len(cur)}")

def apply_edits(edits, chunk):
    """edits: list of (idx, newtext)"""
    p = os.path.join(OUT, chunk + '.txt')
    raw = open(p, encoding='utf-8-sig', newline='').read()
    crlf = '\r\n' in raw
    paras = raw.replace('\r\n', '\n').split('\n\n')
    for idx, new in edits:
        old = paras[idx-1]
        assert old != new
        paras[idx-1] = new
    out = '\n\n'.join(paras)
    if crlf:
        out = out.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(out)
    print('WROTE', chunk, len(edits))

def show(nums, field='src'):
    for n in nums:
        for s in load_material(n):
            print(f"--- {s['sid']} {s['chunk']}#{s['idx']}")
            print(s[field])

def showcur(nums):
    for n in nums:
        for s in load_material(n):
            raw, paras, crlf = load_out(s['chunk'])
            print(f"--- {s['sid']} {s['chunk']}#{s['idx']}")
            print(paras[s['idx']-1])

def apply_subs(path):
    """path: json list of {sid, chunk, idx, old, new}
    Apply each old->new in paragraph idx of chunk, assert exactly one occurrence."""
    subs = json.load(open(path, encoding='utf-8'))
    bychunk = {}
    for e in subs:
        bychunk.setdefault(e['chunk'], []).append(e)
    for chunk, es in bychunk.items():
        p = os.path.join(OUT, chunk + '.txt')
        raw = open(p, encoding='utf-8-sig', newline='').read()
        crlf = '\r\n' in raw
        paras = raw.replace('\r\n', '\n').split('\n\n')
        n = 0
        for e in es:
            i = e['idx'] - 1
            txt = paras[i]
            c = txt.count(e['old'])
            assert c == 1, f"{e['sid']} count={c} for {e['old'][:30]!r}"
            paras[i] = txt.replace(e['old'], e['new'])
            n += 1
        out = '\n\n'.join(paras)
        if crlf:
            out = out.replace('\n', '\r\n')
        open(p, 'w', encoding='utf-8', newline='').write(out)
        print(f"WROTE {chunk}: {n} subs")

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'diff':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        diff_range(range(a, b+1))
    elif cmd == 'show':
        show([int(x) for x in sys.argv[2:]])
    elif cmd == 'cur':
        showcur([int(x) for x in sys.argv[2:]])
    elif cmd == 'subs':
        apply_subs(sys.argv[2])
