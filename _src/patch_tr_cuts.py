import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 1) 新增 tr_cuts 切分函式
anchor = "def split_tr(tr, src_parts):"
add = '''def split_tr_cuts(tr, n_parts, cuts):
    """依指定句子（含該句）強制切出各片；cuts 長度 = n_parts-1。"""
    ss = [x for x in _sents(tr) if x.strip()]
    parts, cur, k = [], '', 0
    for x in ss:
        cur += x
        if k < len(cuts) and all(c in cur for c in [cuts[k]]):
            parts.append(cur)
            cur = ''
            k += 1
    if cur:
        parts.append(cur)
    while len(parts) < n_parts:
        parts.append('')
    return parts[:n_parts]


'''
assert anchor in s
s = s.replace(anchor, add + anchor, 1)

# 2) 在 split 套用處使用 tr_cuts
old = "        ts = split_tr(t, parts)"
new = """        if 'tr_cuts' in e:
            ts = split_tr_cuts(t, len(tg), list(e['tr_cuts']))
        else:
            ts = split_tr(t, parts)"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('tr_cuts 支援已加入')
