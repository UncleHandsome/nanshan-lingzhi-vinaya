import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

old = """    while len(parts) < len(src_parts):
        parts.append('')
    return parts"""
new = """    while len(parts) < len(src_parts):
        parts.append('')
    # 修正：若某片譯文最後一句是「下一科的導語」，移到下一片開頭
    for i in range(len(parts) - 1):
        ss = [x for x in _sents(parts[i]) if x.strip()]
        if len(ss) >= 2:
            last = ss[-1]
            body = last.strip()
            if han(body) < 22 and ('部分' in body or body.rstrip('。').endswith('中')
                                   or body.rstrip('。').endswith('科')):
                parts[i] = ''.join(ss[:-1])
                parts[i + 1] = last + parts[i + 1]
    return parts"""
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('split_tr tail-guard added')
