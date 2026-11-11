# -*- coding: utf-8 -*-
"""Validate label->out mapping and build round-5 files."""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D4 = os.path.join(B, '測試_80K對照', '10K_第4輪')
D5 = os.path.join(B, '測試_80K對照', '10K_第5輪')
OUT = os.path.join(B, 'AI語譯', 'out')

LBL = re.compile(r'^【(001-\d{4})】(\S+?)#(\d+)$')
_cache = {}


def read(p):
    return io.open(p, encoding='utf-8').read()


def parse_material(text):
    lines = text.splitlines()
    i0 = next(i for i, l in enumerate(lines) if l.strip() == '# 材料開始')
    segs, cur = [], None
    for l in lines[i0 + 1:]:
        m = LBL.match(l.strip())
        if m:
            cur = dict(line=l.strip(), sid=m.group(1), src=m.group(2), seg=int(m.group(3)),
                       orig=None, trans=None)
            segs.append(cur)
            continue
        if cur is None:
            continue
        if l.startswith('【原文】'):
            cur['orig'] = l[4:]
        elif l.startswith('【譯文】'):
            cur['trans'] = l[4:]
    return segs


def out_segs(book, chunk):
    key = (book, chunk)
    if key not in _cache:
        p = os.path.join(OUT, book, chunk + '.txt')
        raw = read(p)
        _cache[key] = re.split(r'\r?\n\r?\n', raw)
        while _cache[key] and _cache[key][-1].strip() == '':
            _cache[key].pop()
    return _cache[key]


def main():
    files = sorted(f for f in os.listdir(D4) if f.endswith('.txt'))
    diffs = []
    all_segs = []
    for fn in files:
        segs = parse_material(read(os.path.join(D4, fn)))
        for s in segs:
            book, chunk = s['src'].split('/')
            o = out_segs(book, chunk)
            idx = s['seg'] - 1
            if idx >= len(o):
                print('!! index out of range', s['line'], idx, len(o))
                continue
            cur = o[idx].strip()
            s['current'] = cur
            if cur != s['trans']:
                diffs.append((s['line'], s['trans'], cur))
        all_segs += segs
    print('total segs', len(all_segs), 'diff vs round4 material', len(diffs))
    for d in diffs:
        print('--- DIFF', d[0])
        print('  R4 :', d[1][:120])
        print('  OUT:', d[2][:120])
    json.dump([[s['line'], s['orig'], s['trans'], s.get('current', '')] for s in all_segs],
              io.open(os.path.join(B, '_work_r5_all.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)


if __name__ == '__main__':
    main()
