import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, '會本材料_11-30', '篇14_重出')
dec = json.JSONDecoder()
for i in range(1, 11):
    fp = os.path.join(D, '%d.txt' % i)
    s = io.open(fp, encoding='utf-8-sig').read()
    j = 0
    keys = []
    nb = ns = 0
    while j < len(s):
        while j < len(s) and s[j] in ' \r\n\t,，':
            j += 1
        if j >= len(s):
            break
        try:
            o, j = dec.raw_decode(s, j)
        except Exception as e:
            j += 1
            continue
        if isinstance(o, dict):
            if 'bounds' in o:
                nb += len(o['bounds'])
            if 'splits' in o:
                ns += len(o['splits'])
            keys += [k for k in o.keys() if k not in ('bounds', 'splits')]
    print(i, 'bounds', nb, 'splits', ns, 'keys', keys[:5])
