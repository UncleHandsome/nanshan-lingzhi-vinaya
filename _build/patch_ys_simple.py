import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
s = io.open(p, encoding='utf-8').read()

old = "    '03_業疏': dict(src='03_業疏', tr='03_業疏', mode='chunks', ju_dir='03_業疏'),"
new = "    '03_業疏': dict(src='03_業疏', tr='03_業疏', mode='simple'),"
if old in s and "mode='simple'" not in s:
    s = s.replace(old, new)

old2 = """def get(tag):
    cfg = BOOKS[tag]
    if cfg['mode'] == 'chunks':"""
new2 = """def pairs_simple(src_dir, tr_tag):
    \"\"\"直接以分卷原文配白話（段數已 1:1）。\"\"\"
    res = []
    cur = None
    entries = []
    for key, sp, tt in load_chunks(src_dir, tr_tag):
        vol = vol_of(key)
        if vol != cur:
            if entries:
                res.append((cur, entries))
            entries = []
            cur = vol
        n = min(len(sp), len(tt))
        for i in range(n):
            entries.append((sp[i], tt[i]))
        for i in range(n, len(sp)):
            entries.append((sp[i], ''))
    if entries:
        res.append((cur, entries))
    return res


def get(tag):
    cfg = BOOKS[tag]
    if cfg['mode'] == 'simple':
        return pairs_simple(cfg['src'], cfg['tr'])
    if cfg['mode'] == 'chunks':"""
if old2 in s and 'pairs_simple' not in s:
    s = s.replace(old2, new2)
io.open(p, 'w', encoding='utf-8').write(s)
print('yeshu simple mode added')
