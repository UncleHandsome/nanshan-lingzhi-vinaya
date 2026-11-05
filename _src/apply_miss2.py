import os, io, re, json, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'AI語譯', '_work', 'miss2')
T = os.path.join(B, 'AI語譯', 'out', '02_戒疏')
LEAD = re.compile(r'^(【[^】]{1,6}】)+')


def main(write=False):
    got = {}
    for p in sorted(glob.glob(os.path.join(SRC, 'out_*.json'))):
        arr = json.load(io.open(p, encoding='utf-8'))
        for it in arr:
            got.setdefault(it['key'], {})[int(it['seg'])] = it['text'].strip()
    total = 0
    for key, d in got.items():
        p = os.path.join(T, key + '.txt')
        ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
        bad = [s for s in d if not (1 <= s <= len(ps))]
        print('%-18s 得 %3d, 段數 %3d, 越界 %s' % (key, len(d), len(ps), bad[:5]))
        if bad or not write:
            continue
        for s, txt in d.items():
            body = LEAD.sub('', txt).strip()
            layer = LEAD.match(ps[s - 1])
            ps[s - 1] = (layer.group(0) + body) if layer else body
        io.open(p, 'w', encoding='utf-8').write('\n\n'.join(ps) + '\n')
        total += len(d)
    print('written', total)


if __name__ == '__main__':
    import sys
    main('--write' in sys.argv)
