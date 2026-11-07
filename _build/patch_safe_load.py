import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\hebian_safe.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("""SECS = ex.sections()
ZI = ex.build_zi(SECS, ex.zsecs())""",
"""ZI = ex.build_zi(ex.sections(), ex.zsecs())

# 自己載入鈔文（帶卷別）
def load(src, tr):
    S = os.path.join(B, 'TXT_分卷', src)
    T = os.path.join(B, 'AI語譯', 'out', tr)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        tp = os.path.join(T, k + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\\r?\\n\\r?\\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        out.append((k, sp, tt))
    return out


PATS = re.compile(r'^([\\u4e00-\\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
SECS = []
cur = None
for k, sp, tt in load('01_行事鈔', '01_行事鈔'):
    vol = k.split('_', 1)[1] if '_' in k else k
    if vol.startswith('卷首'):
        vol = '卷上之一'
    if k.startswith('00_'):
        continue
    for i, o in enumerate(sp):
        m = PATS.match(o.strip())
        if m:
            if any(x['name'] == m.group(1) for x in SECS):
                cur = next(x for x in SECS if x['name'] == m.group(1))
            else:
                cur = dict(name=m.group(1), items=[])
                SECS.append(cur)
            continue
        if cur is not None:
            cur['items'].append((o, tt[i] if i < len(tt) else '', vol))""")

s = s.replace("""            chao = []
            for it in sec['items']:
                o, t = it[0], it[1]
                v = it[2] if len(it) > 2 else '卷上之一'
                if v == vol and not SKIP.match(o.strip()):
                    chao.append((o, t))""",
"""            chao = [(it[0], it[1]) for it in sec['items'] if it[2] == vol and not SKIP.match(it[0].strip())]""")
io.open(p, 'w', encoding='utf-8').write(s)
print('hebian_safe loading rewritten')
