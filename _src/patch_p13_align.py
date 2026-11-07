import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

old = """    chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]"""
new = """    chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]
    if p == 13:
        # 卷中之一的譯文自「篇聚名報篇第十三」起整體前移一段，重新對齊
        k0 = None
        for i, (o, t) in enumerate(chao):
            if o.strip().startswith('篇聚名報篇第十三'):
                k0 = i
                break
        if k0 is not None:
            real = list(chao)
            for i in range(k0 + 1, len(chao)):
                real[i] = (chao[i][0], chao[i - 1][1])
            real[k0] = (chao[k0][0], '')
            chao = real"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('p13 realign added')
