# -*- coding: utf-8 -*-
"""把 r2 回應濃縮為候選清單：標記 ❌/★/❗ 優先；無標記則取箭頭建議與「誤／錯」句。"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2j_lib as L

MARK = re.compile(r'(❌|★|❗|\*\*★|\*\*❗)')


def clean(s):
    s = s.replace('**', '').replace('`', '')
    s = re.sub(r'^[\s>\-•]+', '', s)
    return s.strip()


def seg_refs(line):
    out = []
    for m in re.finditer(r'\d{4}-(\d{4})', line):
        out.append(int(m.group(1)))
    for m in re.finditer(r'(?<![\d-])(\d{4})(?![\d-])', line):
        n = int(m.group(1))
        if 1 <= n <= 20:
            out.append(n)
    return sorted(set(out))


def digest(n, cap=14):
    txt = L.resp_text(n)
    if txt is None:
        return None
    lines = [x.rstrip() for x in txt.split('\n')]
    cur = None
    items = []
    has_mark = any(MARK.search(x) for x in lines)
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith('#'):
            refs = seg_refs(ln)
            if refs:
                cur = refs[0]
        elif len(clean(ln)) < 24:
            refs = seg_refs(ln)
            if refs:
                cur = refs[0]
        hit = bool(MARK.search(ln))
        if not has_mark:
            hit = ('→' in ln and ('譯' in ln or '「' in ln)) or ('誤譯' in ln) or ('譯錯' in ln)
        if hit:
            block = [clean(ln)]
            j = i + 1
            while j < len(lines) and lines[j].strip() != '' and not MARK.search(lines[j]) and j < i + 3:
                block.append(clean(lines[j]))
                j += 1
            items.append((cur, ' / '.join(x for x in block if x)))
            i = j
            continue
        i += 1
    if len(items) > cap:
        items = items[:cap]
    return items


if __name__ == '__main__':
    a, b = int(sys.argv[1]), int(sys.argv[2])
    for n in range(a, b + 1):
        items = digest(n)
        if items is None:
            print('===== %d  (無回應) =====' % n)
            continue
        print('===== %d  (%d 條) =====' % (n, len(items)))
        for seg, text in items:
            print('  #%s %s' % (seg, text[:360]))
