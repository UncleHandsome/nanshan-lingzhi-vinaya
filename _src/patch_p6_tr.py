import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
s = io.open(p, encoding='utf-8').read()

old_start = s.find('def split_tr(')
old_end = s.find('# 切好所有記段')
assert old_start > 0 and old_end > old_start
new_fn = '''def split_tr(tr, weights):
    """用句對句 DP 把白話切到與原文相同的段落數"""
    def sents(x):
        out = re.findall(r'[^。！？；]*[。！？；]?', x)
        return [y for y in out if y.strip()]
    trs = sents(tr)
    n_src = len(weights)
    if n_src <= 1 or len(trs) <= 1:
        return [tr] + [''] * (n_src - 1)
    # 每個原文段內的句數比例 → 目標切點（白話句索引）
    total_w = sum(weights) or 1
    targets = []
    acc = 0
    for w in weights[:-1]:
        acc += w
        targets.append(acc / total_w * len(trs))
    # 就近取句界
    cuts = []
    for tg in targets:
        cuts.append(min(max(1, int(round(tg))), len(trs) - (n_src - 1 - len(cuts))))
    cuts = sorted(cuts)
    parts, prev = [], 0
    for c in cuts:
        parts.append(''.join(trs[prev:c]))
        prev = c
    parts.append(''.join(trs[prev:]))
    while len(parts) < n_src:
        parts.append('')
    return parts


'''
s = s[:old_start] + new_fn + s[old_end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('split_tr DP-ish patched')
