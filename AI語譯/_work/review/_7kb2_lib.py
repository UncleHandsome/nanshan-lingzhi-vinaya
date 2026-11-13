# -*- coding: utf-8 -*-
"""7K 資持記 下一_b helpers (1883-1905)."""
import os, re, sys, json, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MAT = os.path.join(ROOT, '校閱_7K')
OUT = os.path.join(ROOT, 'AI語譯', 'out', '資持記')
SRC = os.path.join(ROOT, 'TXT_分卷', '資持記_細分')

def read(p):
    with open(p, 'r', encoding='utf-8', newline='') as f:
        return f.read()

def norm(t):
    return t.replace('\r\n', '\n').replace('\r', '\n')

def read_out(chunk):
    raw = read(os.path.join(OUT, chunk + '.txt'))
    eol = '\r\n' if '\r\n' in raw else ('\r' if '\r' in raw else '\n')
    lines = norm(raw).split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]
    return lines, eol

def mat_map(n):
    t = norm(read(os.path.join(MAT, '校閱_%d.txt' % n)))
    items = []
    pat = re.compile(r'【(\d{4}-\d{4})】資持記/(\S+?)#(\d+)\n【原文】(.*?)\n【譯文】(.*?)(?=\n\n【\d{4}-\d{4}】|\s*\Z)', re.S)
    for m in pat.finditer(t):
        items.append(dict(seg=m.group(1), chunk=m.group(2), idx=int(m.group(3)),
                          src=m.group(4).strip(), tr=m.group(5).strip()))
    return items

def para_index(lines):
    return [(i, l) for i, l in enumerate(lines) if l.strip()]

def show(n, src=True):
    items = mat_map(n)
    print('### 檔', n, 'segs', len(items))
    bychunk = {}
    for it in items:
        bychunk.setdefault(it['chunk'], []).append(it)
    for chunk, its in bychunk.items():
        lines = read_out(chunk)[0]
        ne = para_index(lines)
        print('--- chunk %s lines=%d nonempty=%d' % (chunk, len(lines), len(ne)))
        for it in its:
            cur = ne[it['idx'] - 1][1] if it['idx'] - 1 < len(ne) else '<MISSING>'
            same = (cur.strip() == it['tr'])
            print('[%s #%d] same=%s' % (it['seg'], it['idx'], same))
            if src:
                print('原文:', it['src'])
            print('材料譯:', it['tr'])
            print('現行譯:', cur)
            print()

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'show':
        for a in sys.argv[2:]:
            show(int(a))
    elif cmd == 'nosrc':
        for a in sys.argv[2:]:
            show(int(a), src=False)
    elif cmd == 'cur':
        chunk = sys.argv[2]
        for i, l in para_index(read_out(chunk)[0]):
            print(i, l)
