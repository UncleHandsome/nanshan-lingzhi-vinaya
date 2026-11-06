import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = """    by_c = {}
    last = 0
    for k, c in enumerate(am[:len(zi)]):
        c = int(c)
        if c > 0:
            c = max(c, last)   # 強制單調
            last = c
            by_c.setdefault(c, []).append(k)"""
new = """    by_c = {}
    if p == 10:
        # 篇10 的 c 是區塊粗標，改用 AI 切點推導逐記鈔號
        smap = {}
        for e in splits:
            smap[int(e['n'])] = e
        FORCED = {35: 5, 51: 13, 52: 15}
        cur = 1
        for n in range(1, len(zi) + 1):
            if n in FORCED:
                cur = FORCED[n]
            if n in smap:
                tg = [int(x) for x in smap[n]['targets']]
                for c in tg:
                    by_c.setdefault(c, []).append(n - 1)
                cur = tg[-1]
            else:
                by_c.setdefault(cur, []).append(n - 1)
    else:
        last = 0
        for k, c in enumerate(am[:len(zi)]):
            c = int(c)
            if c > 0:
                c = max(c, last)   # 強制單調
                last = c
                by_c.setdefault(c, []).append(k)"""
if old in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('p10 cmap walk added')
else:
    print('missing')
