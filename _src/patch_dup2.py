import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
start = s.find('def strip_dup_tail')
end = s.find('def build(p, splits):')
assert start > 0 and end > start
new = '''def strip_dup_tail(p):
    if p != 8:
        return
    import re as _re
    o169, t169 = ZI[7][168]
    o170, t170 = ZI[7][169]
    # 找 o169 後綴與 o170 前綴的最長重疊
    best = 0
    for L in range(min(120, len(o169), len(o170)), 20, -1):
        if o169[-L:] == o170[:L]:
            best = L
            break
    if best >= 20:
        rest = o170[best:].lstrip('。；，')
        # 白話按比例切掉
        ratio = best / max(1, len(o170))
        cut = int(round(len(t170) * ratio))
        # 對到句號
        j = t170.find('。', cut)
        rest_t = t170[j + 1:] if j > 0 else t170
        ZI[7][169] = (rest, rest_t)


'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('dup strip v2')
