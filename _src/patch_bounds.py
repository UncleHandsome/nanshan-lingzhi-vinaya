import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 讀 bounds
s = s.replace("""SKIP = re.compile(r'^\\d+\\s*[\\u4e00-\\u9fff]{2,10}篇')""",
"""SKIP = re.compile(r'^\\d+\\s*[\\u4e00-\\u9fff]{2,10}篇')
BDIR = os.path.join(B, 'AI語譯', '_work', 'pian_bounds')


def load_bounds(pp):
    fp = os.path.join(BDIR, 'bounds_篇%02d.json' % pp)
    if not os.path.exists(fp):
        return None
    try:
        d = json.load(io.open(fp, encoding='utf-8-sig'))
        bs = [(int(x['c']), int(x['n'])) for x in d.get('bounds', [])]
    except Exception:
        return None
    bs = [b for b in bs if b[1] >= 1]
    if len(bs) < 2:
        return None
    return bs""")

# build 內：優先使用 bounds
s = s.replace("""    by_c = {}
    if p == 10:""",
"""    by_c = {}
    BS = load_bounds(p)
    if BS:
        cmap = {}
        for i2, (c2, n2) in enumerate(BS):
            end2 = BS[i2 + 1][1] - 1 if i2 + 1 < len(BS) else len(zi)
            for n3 in range(n2, max(n2, end2) + 1):
                cmap[n3] = c2
        for n3 in range(1, len(zi) + 1):
            if n3 in cmap:
                by_c.setdefault(cmap[n3], []).append(n3 - 1)
    elif p == 10:""")

# 驗證改用 cmap（若有）
s = s.replace("""        base = int(am[n - 1]) if n - 1 < len(am) else 0""",
"""        base = (cmap.get(n, 0) if BS else (int(am[n - 1]) if n - 1 < len(am) else 0))""")
io.open(p, 'w', encoding='utf-8').write(s)
print('bounds support added')
