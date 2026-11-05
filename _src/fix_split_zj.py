
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\split_zj.py'
s = io.open(p, encoding='utf-8').read()
old = """    chunks, cur, cur_b = [], [], 0"""
new = """    # 過長段落按句切開
    fixed = []
    for p in paras:
        if b(p) <= LIMIT - 200:
            fixed.append(p); continue
        sents = re.split(r'(?<=[。！？])', p)
        buf = ''
        for s2 in sents:
            if buf and b(buf) + b(s2) > LIMIT - 400:
                fixed.append(buf); buf = s2
            else:
                buf += s2
        if buf.strip(): fixed.append(buf)
    paras = fixed
    chunks, cur, cur_b = [], [], 0"""
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
